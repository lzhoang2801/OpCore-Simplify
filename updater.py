from Scripts import resource_fetcher
from Scripts import github
from Scripts import run
from Scripts import utils
import os
import tempfile
import shutil

class Updater:
    def __init__(self):
        self.github = github.Github()
        self.fetcher = resource_fetcher.ResourceFetcher()
        self.run = run.Run().run
        self.utils = utils.Utils()
        self.sha_version = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sha_version.txt")
        self.download_repo_url = "https://github.com/lzhoang2801/OpCore-Simplify/archive/refs/heads/main.zip"
        self.temporary_dir = tempfile.mkdtemp()
        self.current_step = 0

    def get_current_sha_version(self):
        print("Checking current version...")
        try:
            current_sha_version = self.utils.read_file(self.sha_version)

            if not current_sha_version:
                print("SHA version information is missing.")
                return "missing_sha_version"

            return current_sha_version.decode()
        except Exception as e:
            print("Error reading current SHA version: {}".format(str(e)))
            return "error_reading_sha_version"

    def get_latest_sha_version(self):
        print("Fetching latest version from GitHub...")
        try:
            latest_commit = self.github.get_latest_commit("lzhoang2801", "OpCore-Simplify")
            if latest_commit and latest_commit.get("sha"):
                return latest_commit.get("sha")
        except Exception as e:
            print("Error fetching latest SHA version: {}".format(str(e)))
            return None
        
        print("Could not fetch latest commit information from GitHub.")
        return None

    def download_update(self):
        self.current_step += 1
        print("")
        print("Step {}: Creating temporary directory...".format(self.current_step))
        try:
            self.utils.create_folder(self.temporary_dir)
            print("  Temporary directory created.")
            
            self.current_step += 1
            print("Step {}: Downloading update package...".format(self.current_step))
            print("  ", end="")
            file_path = os.path.join(self.temporary_dir, os.path.basename(self.download_repo_url))
            self.fetcher.download_and_save_file(self.download_repo_url, file_path)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print("  Update package downloaded ({:.1f} KB)".format(os.path.getsize(file_path)/1024))
                
                self.current_step += 1
                print("Step {}: Extracting files...".format(self.current_step))
                self.utils.extract_zip_file(file_path)
                print("  Files extracted successfully")
                return True
            else:
                print("  Download failed or file is empty")
                return False
        except Exception as e:
            print("  Error during download/extraction: {}".format(str(e)))
            return False

    def update_files(self):
        self.current_step += 1
        print("Step {}: Updating files...".format(self.current_step))
        try:
            target_dir = os.path.join(self.temporary_dir, "OpCore-Simplify-main")
            if not os.path.exists(target_dir):
                target_dir = os.path.join(self.temporary_dir, "main", "OpCore-Simplify-main")
                
            if not os.path.exists(target_dir):
                print("  Could not locate extracted files directory")
                return False
                
            file_paths = self.utils.find_matching_paths(target_dir, type_filter="file")
            
            total_files = len(file_paths)
            print("  Found {} files to update".format(total_files))
            
            updated_count = 0
            for index, (path, type) in enumerate(file_paths, start=1):
                source = os.path.join(target_dir, path)
                destination = source.replace(target_dir, os.path.dirname(os.path.realpath(__file__)))
                
                self.utils.create_folder(os.path.dirname(destination))
                
                print("    Updating [{}/{}]: {}".format(index, total_files, os.path.basename(path)), end="\r")
                
                try:
                    shutil.move(source, destination)
                    updated_count += 1
                    
                    if ".command"  in os.path.splitext(path)[-1] and os.name != "nt":
                        self.run({
                            "args": ["chmod", "+x", destination]
                        })
                except Exception as e:
                    print("      Failed to update {}: {}".format(path, str(e)))
            
            print("")
            print("  Successfully updated {}/{} files".format(updated_count, total_files))
            
            self.current_step += 1
            print("Step {}: Cleaning up temporary files...".format(self.current_step))
            shutil.rmtree(self.temporary_dir)
            print("  Cleanup complete")
            
            return True
        except Exception as e:
            print("  Error during file update: {}".format(str(e)))
            return False

    def save_latest_sha_version(self, latest_sha):
        try:
            self.utils.write_file(self.sha_version, latest_sha.encode())
            self.current_step += 1
            print("Step {}: Version information updated.".format(self.current_step))
            return True
        except Exception as e:
            print("Failed to save version information: {}".format(str(e)))
            return False

    def run_update(self):
        self.utils.head("Check for Updates")
        print("")
        
        current_sha_version = self.get_current_sha_version()
        latest_sha_version = self.get_latest_sha_version()
        
        print("")

        if latest_sha_version is None:
            print("Could not verify the latest version from GitHub.")
            print("Current script SHA version: {}".format(current_sha_version))
            print("Please check your internet connection and try again later.")
            print("")
            
            user_input = self.utils.request_input("Do you want to skip the update process? (Y/n): ").strip().lower() or "y"
            if user_input == 'y':
                print("")
                print("Update process skipped.")
                return False
            else:
                print("")
                print("Continuing with update using default version check...")
                latest_sha_version = "update_forced_by_user"
        else:
            print("Current script SHA version: {}".format(current_sha_version))
            print("Latest script SHA version: {}".format(latest_sha_version))
        
        print("")
        
        if latest_sha_version != current_sha_version:
            print("Update available!")
            print("Updating from version {} to {}".format(current_sha_version, latest_sha_version))
            print("")
            print("Starting update process...")
            
            if not self.download_update():
                print("")
                print("  Update failed: Could not download or extract update package")

                if os.path.exists(self.temporary_dir):
                    self.current_step += 1
                    print("Step {}: Cleaning up temporary files...".format(self.current_step))
                    shutil.rmtree(self.temporary_dir)
                    print("  Cleanup complete")

                return False
                
            if not self.update_files():
                print("")
                print("  Update failed: Could not update files")
                return False
                
            if not self.save_latest_sha_version(latest_sha_version):
                print("")
                print("  Update completed but version information could not be saved")
            
            print("")
            print("Update completed successfully!")
            print("")
            print("The program needs to restart to complete the update process.")
            return True
        else:
            print("You are already using the latest version")
            return False