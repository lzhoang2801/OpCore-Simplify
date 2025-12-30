import os
import tempfile
import shutil
import sys

from PyQt6.QtCore import QThread, pyqtSignal

from Scripts import resource_fetcher
from Scripts import github
from Scripts import run
from Scripts import utils
from Scripts import integrity_checker
from Scripts.custom_dialogs import show_update_dialog, show_info, show_confirmation

class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(dict)
    check_failed = pyqtSignal(str)
    no_update = pyqtSignal()
    
    def __init__(self, updater_instance):
        super().__init__()
        self.updater = updater_instance
    
    def run(self):
        try:
            remote_manifest = self.updater.get_remote_manifest()
            if not remote_manifest:
                self.check_failed.emit("Could not fetch update information from GitHub.\n\nPlease check your internet connection and try again later.")
                return
            
            local_manifest = self.updater.get_local_manifest()
            if not local_manifest:
                self.check_failed.emit("Could not generate local manifest.\n\nPlease try again later.")
                return
                        
            files_to_update = self.updater.compare_manifests(local_manifest, remote_manifest)
            if not files_to_update:
                self.no_update.emit()
            else:
                self.update_available.emit(files_to_update)
        except Exception as e:
            self.check_failed.emit("An error occurred during update check:\n\n{}".format(str(e)))

class Updater:
    def __init__(self, utils_instance=None, github_instance=None, resource_fetcher_instance=None, run_instance=None, integrity_checker_instance=None):
        self.utils = utils_instance if utils_instance else utils.Utils()
        self.github = github_instance if github_instance else github.Github(utils_instance=self.utils)
        self.fetcher = resource_fetcher_instance if resource_fetcher_instance else resource_fetcher.ResourceFetcher(utils_instance=self.utils)
        self.run = run_instance.run if run_instance else run.Run().run
        self.integrity_checker = integrity_checker_instance if integrity_checker_instance else integrity_checker.IntegrityChecker(utils_instance=self.utils)
        self.remote_manifest_url = "https://nightly.link/lzhoang2801/OpCore-Simplify/workflows/generate-manifest/main/manifest.json.zip"
        self.download_repo_url = "https://github.com/lzhoang2801/OpCore-Simplify/archive/refs/heads/main.zip"
        self.temporary_dir = tempfile.mkdtemp()
        self.root_dir = os.path.dirname(os.path.realpath(__file__))

    def get_remote_manifest(self, dialog=None):
        if dialog:
            dialog.update_progress(10, "Fetching remote manifest...")
        
        try:
            temp_manifest_zip_path = os.path.join(self.temporary_dir, "remote_manifest.json.zip")
            success = self.fetcher.download_and_save_file(self.remote_manifest_url, temp_manifest_zip_path)
            
            if not success or not os.path.exists(temp_manifest_zip_path):
                return None

            self.utils.extract_zip_file(temp_manifest_zip_path, self.temporary_dir)
            
            remote_manifest_path = os.path.join(self.temporary_dir, "manifest.json")
            manifest_data = self.utils.read_file(remote_manifest_path)
            
            if dialog:
                dialog.update_progress(20, "Manifest downloaded successfully")
            
            return manifest_data
        except Exception as e:
            self.utils.log_message("[UPDATER] Error fetching remote manifest: {}".format(str(e)), level="ERROR")
            return None
    
    def get_local_manifest(self, dialog=None):
        if dialog:
            dialog.update_progress(40, "Generating local manifest...")
        
        try:
            manifest_data = self.integrity_checker.generate_folder_manifest(self.root_dir, save_manifest=False)
            
            if dialog:
                dialog.update_progress(50, "Local manifest generated")
            
            return manifest_data
        except Exception as e:
            self.utils.log_message("[UPDATER] Error generating local manifest: {}".format(str(e)), level="ERROR")
            return None
    
    def compare_manifests(self, local_manifest, remote_manifest):
        if not local_manifest or not remote_manifest:
            return None
        
        files_to_update = {
            "modified": [],
            "missing": [],
            "new": []
        }
        
        local_files = set(local_manifest.keys())
        remote_files = set(remote_manifest.keys())
        
        for file_path in local_files & remote_files:
            if local_manifest[file_path] != remote_manifest[file_path]:
                files_to_update["modified"].append(file_path)
        
        files_to_update["missing"] = list(remote_files - local_files)
        
        files_to_update["new"] = list(local_files - remote_files)
        
        total_changes = len(files_to_update["modified"]) + len(files_to_update["missing"])
        
        return files_to_update if total_changes > 0 else None
    
    def download_update(self, dialog=None):
        if dialog:
            dialog.update_progress(60, "Creating temporary directory...")
        
        try:
            self.utils.create_folder(self.temporary_dir)
            
            if dialog:
                dialog.update_progress(65, "Downloading update package...")
            
            file_path = os.path.join(self.temporary_dir, "update.zip")
            success = self.fetcher.download_and_save_file(self.download_repo_url, file_path)
            
            if not success or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                return False
            
            if dialog:
                dialog.update_progress(75, "Extracting files...")
            
            self.utils.extract_zip_file(file_path, self.temporary_dir)
            
            if dialog:
                dialog.update_progress(80, "Files extracted successfully")
            
            return True
        except Exception as e:
            self.utils.log_message("[UPDATER] Error during download/extraction: {}".format(str(e)), level="ERROR")
            return False
    
    def update_files(self, files_to_update, dialog=None):
        if not files_to_update:
            return True
        
        try:
            target_dir = os.path.join(self.temporary_dir, "OpCore-Simplify-main")

            if not os.path.exists(target_dir):
                self.utils.log_message("[UPDATER] Target directory not found: {}".format(target_dir), level="ERROR")
                return False
            
            all_files = files_to_update["modified"] + files_to_update["missing"]
            total_files = len(all_files)
            
            if dialog:
                dialog.update_progress(85, "Updating {} files...".format(total_files))
            
            updated_count = 0
            for index, relative_path in enumerate(all_files, start=1):
                source = os.path.join(target_dir, relative_path)
                
                if not os.path.exists(source):
                    self.utils.log_message("[UPDATER] Source file not found: {}".format(source), level="ERROR")
                    continue
                
                destination = os.path.join(self.root_dir, relative_path)
                
                self.utils.create_folder(os.path.dirname(destination))
                
                self.utils.log_message("[UPDATER] Updating [{}/{}]: {}".format(index, total_files, os.path.basename(relative_path)), level="INFO")
                if dialog:
                    progress = 85 + int((index / total_files) * 10)
                    dialog.update_progress(progress, "Updating [{}/{}]: {}".format(index, total_files, os.path.basename(relative_path)))
                
                try:
                    shutil.move(source, destination)
                    updated_count += 1
                    
                    if ".command" in os.path.splitext(relative_path)[-1] and os.name != "nt":
                        self.run({
                            "args": ["chmod", "+x", destination]
                        })
                except Exception as e:
                    self.utils.log_message("[UPDATER] Failed to update {}: {}".format(relative_path, str(e)), level="ERROR")
            
            if dialog:
                dialog.update_progress(95, "Successfully updated {}/{} files".format(updated_count, total_files))
            
            if os.path.exists(self.temporary_dir):
                shutil.rmtree(self.temporary_dir)
            
            if dialog:
                dialog.update_progress(100, "Update completed!")
            
            return True
        except Exception as e:
            self.utils.log_message("[UPDATER] Error during file update: {}".format(str(e)), level="ERROR")
            return False
    
    def run_update(self):    
        checker_thread = UpdateCheckerThread(self)
        
        def on_update_available(files_to_update):
            checker_thread.quit()
            checker_thread.wait()
            
            if not show_confirmation("An update is available!", "Would you like to update now?", yes_text="Update", no_text="Later"):
                return False
            
            dialog = show_update_dialog("Updating", "Starting update process...")
            dialog.show()
            
            try:
                if not self.download_update(dialog):
                    dialog.close()
                    show_info("Update Failed", "Could not download or extract update package.\n\nPlease check your internet connection and try again.")
                    return
                
                if not self.update_files(files_to_update, dialog):
                    dialog.close()
                    show_info("Update Failed", "Could not update files.\n\nPlease try again later.")
                    return
                
                dialog.close()
                show_info("Update Complete", "Update completed successfully!\n\nThe program needs to restart to complete the update process.")
                
                os.execv(sys.executable, ["python3"] + sys.argv)
            except Exception as e:
                dialog.close()
                self.utils.log_message("[UPDATER] Error during update: {}".format(str(e)), level="ERROR")
                show_info("Update Error", "An error occurred during the update process:\n\n{}".format(str(e)))
            finally:
                if os.path.exists(self.temporary_dir):
                    try:
                        shutil.rmtree(self.temporary_dir)
                    except:
                        pass
        
        def on_check_failed(error_message):
            checker_thread.quit()
            checker_thread.wait()
            show_info("Update Check Failed", error_message)
        
        def on_no_update():
            checker_thread.quit()
            checker_thread.wait()
        
        checker_thread.update_available.connect(on_update_available)
        checker_thread.check_failed.connect(on_check_failed)
        checker_thread.no_update.connect(on_no_update)
        
        checker_thread.start()