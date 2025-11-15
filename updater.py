from Scripts import resource_fetcher
from Scripts import github
from Scripts import run
from Scripts import utils
import os
import tempfile
import shutil
import platform
import struct
import subprocess
import sys
import webbrowser
import psutil
import wmi

system_requirements = {
    "TPM": None,
    "SecureBoot": None,
    "UEFI": None
}
class Updater:
   def tpm_check():
       try:
           c = wmi.WMI(namespace="root\\CIMV2\\Security\\MicrosoftTpm")
           for tpm in c.Win32_Tpm():
               print(f"TPM Version: {tpm.SpecVersion}")
               if "2.0" in tpm.SpecVersion:
                   system_requirements["TPM"] = True
                   print("✅ TPM 2.0 detected.")
                else:
                   system_requirements["TPM"] = False
                   print("❌ TPM 2.0 is missing. We'll help you to bypass the minimum requirements.")
    def secure_boot_check():
      try:
          c = wmi.WMI(namespace="root\\Microsoft\\Windows\\HardwareManagement")
          for sb in c.MSFT_SecureBoot():
              enabled = bool(sb.SecureBootEnabled)
              print(f"Secure Boot Enabled: {enabled}")
              system_requirements["SecureBoot"] = True
        except Exception as e:
          print(f"⚠️ Secure Boot check failed: {e}. We'll help you to bypass the minimum requirements.")
          return False
    def ssse42_check():
        import cpuinfo
        subprocess.run(["cmd", "/c", "pip install py-cpuinfo"], check=True)
        info = cpuinfo.get_cpu_info()
        flags = info.get("flags", [])
        if "sse4_2" in flags:
            print("✅ SSE4.2 supported.")
            return True
        else:
            print("❌ SSE4.2 not supported. For these CPUs, Clover is a must, OpenCore doesn't support those well.")
            print(" ")
            input("Press E to exit OpCore-Simplify and continue with Clover.") 
            if user_input == "e":
                sys.exit(3)
    def uefi_check():
        try:
            c = wmi.WMI()
            for cs in c.Win32_ComputerSystem():
                print(f"Bootup State: {cs.BootupState}")
            
    def check_windows11_requirements():
        print("\n--- Windows 11 Requirements Diagnostics ---")
        print("Checking Windows 11 requirements...\n")
        ssse42_check()
        tpm_check()
        secure_boot_check()


        arch = platform.architecture()[0]
        print(f"Architecture: {arch}")

     
    def diagnose_environment_to_updateandfix():
        system = platform.system()
        release = platform.release()
        version = platform.version()
        arch = struct.calcsize("P") * 8

        print("\n--- OpCore-Simplify Error Diagnostics ---")
        print(f"OS: {system} {release} ({version}), Architecture: {arch}-bit")

        if arch != 64:
            print("⚠️ 32-bit environment detected. OpenCore-Simplify requires 64-bit.")
            print("To upgrade from 32 bit to 64 bit operating system, you need to reinstall the operating system using your flash drive.")
            print("If your operating system doesn't have 64 bit CPU, it is unsupported by OpCore-Simplify.")
            print("")

            input("Press E to exit OpCore-Simplify")
            if user_input == "e":
                sys.exit(3)
        if system == "Windows":
            try:
                build_number = int(version.split('.')[-1])
                print(f"Windows build number: {build_number}")
                if release in ["8", "8.1"]:
                    print("Windows 8 or 8.1 detected.")
                    print("This script doesn't support Windows 8.1 or older since it requires Python 3.14 or newer which requires Windows 10 at absolute minimum.")
                    print("It requires some other libraries that either require the latest version of Windows 10 or Windows 11.")
                    print("")
                    print("You need to upgrade to Windows 11 in order to run this script. No automated troubleshooting possible for such an old version of Windows.")
                    url = "https://www.microsoft.com/en-US/software-download/windows11"
                    webbrowser.open(url)
                    input("Press E to exit OpCore-Simplify")
                    if user_input == "e":
                        sys.exit(3)
                elif int(release)<8:
                    print("Windows 7, Vista, XP or older versions of Windows are detected.")
                    print("This script doesn't support Windows 8.1 or older since it requires Python 3.14 or newer which requires Windows 10 at absolute minimum.")
                    print("It requires some other libraries that either require the latest version of Windows 10 or Windows 11.")
                    print("")
                    print("You need to upgrade to Windows 11 in order to run this script. No automated troubleshooting possible for such an old version of Windows.")
                    url = "https://www.microsoft.com/en-US/software-download/windows11"
                    webbrowser.open(url)
                    input("Press E to exit OpCore-Simplify") 
                    if user_input == "e":
                        sys.exit(3)
                elif release in ["10"]:
                    if build <= 19045.5073:
                        print("⚠️ You're version of Windows 10 is extremely out of date.")
                        print("We'll update Windows - right now you're exposed to vulnerabilities that you haven't patched yet that were fixed long ago.")

                        try:
                            print("Checking for updates...")
                            subprocess.run(["cmd", "/c", "usoclient StartInteractiveScan"], check=True)

                            print("Downloading all available updates...")
                            subprocess.run(["cmd", "/c", "usoclient StartDownload"], check=True)

                            print("Installing all available updates...")
                            subprocess.run(["cmd", "/c", "usoclient StartInstall"], check=True)
                            input("Confirm that your PC is ready to finish installing updates. Answer with y to restart and n to schedule restart in 12 hours.")
                            if user_input == "y":
                                print("OK, your PC will finish installing updates now.")
                                subprocess.run(["cmd", "/c", "shutdown /r /t 0"], check=True) 
                            else:
                                print("OK, your PC will restart automatically in 12 hours.")
                                subprocess.run(["cmd", "/c", "shutdown /r /t 43200"], check=True)
                                sys.exit(0)
                    if build >= 19045.5073:
                        print("You're running a fairly up to date Windows 10. Since Windows 10 is EOS, we'll update your system to a supported version of Windows 11.")
                        check_windows11_requirements()
                                              
    
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
            diagnose_environment_to_updateandfix()

    def get_latest_sha_version(self):
        print("Fetching latest version from GitHub...")
        try:
            commits = self.github.get_commits("lzhoang2801", "OpCore-Simplify")
            return commits["commitGroups"][0]["commits"][0]["oid"]
        except Exception as e:
            print("Error fetching latest SHA version: {}".format(str(e)))
            diagnose_environment_to_updateandfix()
        
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
            diagnose_environment_to_updateandfix()
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
                diagnose_environment_to_updateandfix()
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
            
            while True:
                user_input = self.utils.request_input("Do you want to skip the update process? (yes/No): ").strip().lower()
                if user_input == "yes":
                    print("")
                    print("Update process skipped.")
                    return False
                elif user_input == "no":
                    print("")
                    print("Continuing with update using default version check...")
                    latest_sha_version = "update_forced_by_user"
                    break
                else:
                    print("\033[91mInvalid selection, please try again.\033[0m\n\n")
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