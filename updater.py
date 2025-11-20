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
import socket
import requests

class Updater:
    def check_internet():
        try:
            # Basic connectivity test (Google DNS)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    def troubleshoot_connectivity(self):
        if not self.check_internet():
            print("❌ No internet connection detected.")
            print("Please check your Wi-Fi/Ethernet, restart your router, or verify cables.")
            return False
        try:
            r = requests.get("https://github.com", timeout=5)
            if r.status_code == 200:
                print("✅ Internet is working, but GitHub API may be blocked.")
                print("Please check firewall/proxy settings or try again later.")
                return True
        except requests.exceptions.SSLError:
            print("⚠️ SSL error detected. Please check your system clock and certificates.")
        except requests.exceptions.RequestException:
            print("⚠️ Could not reach GitHub. Please check firewall/proxy settings.")
        return False
    def checkwindows11requirements():
        print("\n--- Windows 11 Requirements Diagnostics ---")
        print("Checking Windows 11 requirements...\n")
        print("Checking for minimal requirements of Windows 11 is done only manually. So you have to answer the following questions:")
        print("If you don't know what a CPU is or what CPU is used in your computer, open Settings and search info for your CPU.")
        input("Does your PC use Intel Core 2 Quad or Intel Core 2 Duo processor? (y/n): ")
        if input == y:
            print("On these CPUs, it is recommended to use Clover.")
            sys.exit(3)
        if input == n:
            print("Well, we're coming to the next question: - up until now, the requirements for SSE4.2 have been passed")
            input("Does your PC have TPM2.0 enabled? (y/n): ")
            if input == y:
                print("Well, we're coming to the next question: - up until now, the requirements for SSE4.2 and TPM2.0 have been passed")
                input("Does your PC have Secure Boot enabled? (y/n): ")
                if input == y:
                    print("Well, we're coming to the next question: - up until now, the requirements for SSE4.2, TPM2.0 and Secure Boot have been passed")
            if input == n:
                print("Well, we're coming to the next question: - up until now, the requirements for SSE4.2 have been passed but the TPM2.0 requirements have been failed:")
                input("Does your PC have TPM1.2 enabled? (y/n): ")
                if input == n:
                    print("OK, our automated bypass tricks will fail then since you don't have any TPM chip at all. What you can do is to download Windows 11 image from https://www.microsoft.com/en-US/software-download/windows11 .")
                    print("Then mount the ISO, then run CMD as Admin and run D:\ (or your virtual drive's location) and then setup.exe /product server.")
                    print("")
                    print("But don't worry, we'll continue to check for updates for Windows 10...")
                    print("Downloading all available updates...")
                    subprocess.run(["cmd", "/c", "usoclient StartDownload"], check=True)
                    print("Installing all available updates...")
                    subprocess.run(["cmd", "/c", "usoclient StartInstall"], check=True)
                    print("Your device is restarting to finish install updates...")
                    usoclient RestartDevice
                if input == y:
                    print("Well, we're coming to the next question: - up until now, the requirements for SSE4.2 have been passed but the TPM2.0 requirements have been failed:")
                    input("Does your PC have Pro, Pro N, Education, Education N, Enterprise, Enterprise N installed? (y/n): ")
                    if input == n:
                        print("OK, our automated bypass tricks will fail then since you don't have any TPM chip at all. What you can do is to download Windows 11 image from https://www.microsoft.com/en-US/software-download/windows11 .")
                        print("Then mount the ISO, then run CMD as Admin and run D:\ (or your virtual drive's location) and then setup.exe /product server.")
                        print("")
                        print("But don't worry, we'll continue to check for updates for Windows 10...")\
                        print("Downloading all available updates...")
                        subprocess.run(["cmd", "/c", "usoclient StartDownload"], check=True)
                        print("Installing all available updates...")
                        subprocess.run(["cmd", "/c", "usoclient StartInstall"], check=True)
                        print("Your device is restarting to finish install updates...")
                        usoclient RestartDevice
                    if input == y:
                        print("✅ Applying upgrade bypass for Windows 11's requirements...")
                        print("Deleting the registry key GE25H2 in CompatMarkers"...")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\CompatMarkers\GE25H2" /f"], check=True)
                        print("Deleting the registry key GE24H2 in CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\CompatMarkers\GE24H2" /f"], check=True)
                        print("Deleting the registry key NI23H2 in CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\CompatMarkers\NI23H2" /f"], check=True)
                        print("Deleting the registry key NI22H2 in CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\CompatMarkers\NI22H2" /f"], check=True)
                        print("Deleting the registry key NI21H2 in CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\CompatMarkers\NI21H2" /f"], check=True)
                        print("Deleting the registry key GE25H2 in Shared > CompatMarkers"...")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\CompatMarkers\GE25H2" /f"], check=True)
                        print("Deleting the registry key GE24H2 in Shared > CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\CompatMarkers\GE24H2" /f"], check=True)
                        print("Deleting the registry key NI23H2 in Shared > CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\CompatMarkers\NI23H2" /f"], check=True)
                        print("Deleting the registry key NI22H2 in Shared > CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\CompatMarkers\NI22H2" /f"], check=True)
                        print("Deleting the registry key NI21H2 in Shared > CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\CompatMarkers\NI21H2" /f"], check=True)
                        print("Deleting the registry key GE25H2 in Shared > GeneralMarkers"...")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\GeneralMarkers\GE25H2" /f"], check=True)
                        print("Deleting the registry key GE24H2 in Shared > GeneralMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\GeneralMarkers\GE24H2" /f"], check=True)
                        print("Deleting the registry key NI23H2 in Shared > GeneralMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\GeneralMarkers\NI23H2" /f"], check=True)
                        print("Deleting the registry key NI22H2 in Shared > GeneralMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\GeneralMarkers\NI22H2" /f"], check=True)
                        print("Deleting the registry key NI21H2 in Shared > GeneralMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\GeneralMarkers\NI21H2" /f"], check=True)
                        print("Deleting the registry key GE25H2 in Shared > TargetVersionUpgradeExperienceIndicators"...")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\TargetVersionUpgradeExperienceIndicators\GE25H2" /f"], check=True)
                        print("Deleting the registry key GE24H2 in Shared > TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\TargetVersionUpgradeExperienceIndicators\GE24H2" /f"], check=True)
                        print("Deleting the registry key NI23H2 in Shared > TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\TargetVersionUpgradeExperienceIndicators\NI23H2" /f"], check=True)
                        print("Deleting the registry key NI22H2 in Shared > TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\TargetVersionUpgradeExperienceIndicators\NI22H2" /f"], check=True)
                        print("Deleting the registry key NI21H2 in Shared > TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\TargetVersionUpgradeExperienceIndicators\NI21H2" /f"], check=True)
                        print("Deleting the registry key UNV in Shared > CompatMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\CompatMarkers\UNV" /f"], check=True)
                        print("Deleting the registry key UNV in Shared > GeneralMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\GeneralMarkers\UNV" /f"], check=True)
                        print("Deleting the registry key UNV in Shared > TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Shared\TargetVersionUpgradeExperienceIndicators\UNV" /f"], check=True)
                        print("Deleting the registry key UNV in TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\TargetVersionUpgradeExperienceIndicators\UNV" /f"], check=True)
                        print("Deleting the registry key UNV in GeneralMarkers")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\GeneralMarkers\UNV" /f"], check=True)
                        print("Deleting the registry key GE25H2 in TargetVersionUpgradeExperienceIndicators"...")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\TargetVersionUpgradeExperienceIndicators\GE25H2" /f"], check=True)
                        print("Deleting the registry key GE24H2 in TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\TargetVersionUpgradeExperienceIndicators\GE24H2" /f"], check=True)
                        print("Deleting the registry key NI23H2 in TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\TargetVersionUpgradeExperienceIndicators\NI23H2" /f"], check=True)
                        print("Deleting the registry key NI22H2 in TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\TargetVersionUpgradeExperienceIndicators\NI22H2" /f"], check=True)
                        print("Deleting the registry key NI21H2 in TargetVersionUpgradeExperienceIndicators")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\TargetVersionUpgradeExperienceIndicators\NI21H2" /f"], check=True)
                        print("Enable upgrades with unsupported TPM or CPU")
                        subprocess.run(["cmd", "/c", "reg add "HKLM\SYSTEM\Setup\MoSetup" /v AllowUpgradesWithUnsupportedTPMOrCPU /t REG_DWORD /d 1 /f" /f"], check=True)
                        print("Add hardware requirement check bypass variables")
                        subprocess.run(["cmd", "/c", "reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\HwReqChk" /v HwReqChkVars /t REG_MULTI_SZ /d "SQ_SecureBootCapable=TRUE\0SQ_TpmVersion=2\0SQ_RamMB=4096" /f"], check=True)
                        print("Add a policy to upgrade to Windows 11 so Windows Update can upgrade to Windows 11 without hardware requirements...")
                        subprocess.run(["cmd", "/c", "reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v TargetReleaseVersion /t REG_DWORD /d 1 /f"], check=True)
                        subprocess.run(["cmd", "/c", "reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v TargetReleaseVersionInfo /t REG_SZ /d "25H2" /f"], check=True)
                        print("Now we'll apply those policies")
                        subprocess.run(["cmd", "/c", "gpupdate /force"], check=True)
                        subprocess.run(["cmd", "/c", "gpupdate /logoff"], check=True)
                        subprocess.run(["cmd", "/c", "gpupdate /boot"], check=True)
                        print("Now all bypass tricks are done, now we'll check for Windows 11 upgrades and install those...")
                        print("Downloading all available updates...")
                        subprocess.run(["cmd", "/c", "usoclient StartDownload"], check=True)
                        print("Installing all available updates...")
                        subprocess.run(["cmd", "/c", "usoclient StartInstall"], check=True)
                        print("Now reversing the policy changes")
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v TargetReleaseVersion /f"], check=True)
                        subprocess.run(["cmd", "/c", "reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v TargetReleaseVersionInfo /f"], check=True)
                        print("Your device is restarting to finish install updates...")
                        subprocess.run(["cmd", "/c", "usoclient RestartDevice"], check=True)

    def run_linux_updates():
        print("Checking for your Linux distro...")
        distro = ""
        try:
            # Try to detect distribution name
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].strip('"')
                        break
        except Exception:
            distro = platform.system().lower()

        # Map distro to update command
        if distro in ["ubuntu", "debian", "zorin", "kali", "raspberrypi", "raspbian", "mx"]:
            print("Checking and applying updates for your computer...")
            cmd = "sudo apt update && sudo apt upgrade -y"
        elif distro in ["fedora", "rhel", "centos"]:
            print("Checking and applying updates for your computer...")
            cmd = "sudo dnf upgrade -y"
        elif distro in ["arch", "manjaro"]:
            print("Checking and applying updates for your computer...")
            cmd = "sudo pacman -Syu"
        elif distro in ["opensuse", "sles"]:
            print("Checking and applying updates for your computer...")
            cmd = "sudo zypper update -y"
        elif distro in ["centos"]:
            print("Attempting to check for updates using older methods on Cent OS if it still runs Cent OS 7...")
            cmd = "sudo yum update -y"
        elif distro in ["gentoo"]:
            print("Checking and applying updates for Gentoo...")
            cmd = "sudo emerge --sync && sudo emerge -uD @world"
        else:
            print(f"Unsupported distro: {distro}. Automatic diagnostics failed to run. This project may be stuck at a vulnerable version.")
            return

        # Launch in terminal
        subprocess.run([
        "gnome-terminal", "--",
        "bash", "-c", f"{cmd}; exec bash"
        ])

    def run_macos_updates():
        print("Checking and applying updates for your computer...")
        subprocess.run([
        "osascript", "-e",
        'tell application "Terminal" to do script "softwareupdate -l; sudo softwareupdate -ia"'
        ]) 
    
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
        if system == "macOS":
            run_macos_updates()
        if system == "Linux":
            run_linux_updates()
        if system == "Windows":
            print("Running sfc /scannow...")
            subprocess.run(["cmd", "/c", "sfc /scannow"], check=True)
            print("Running checks for Windows version that this PC is running...")
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
                        print("⚠️ Your version of Windows 10 is extremely out of date.")
                        print("We'll update Windows - right now you're exposed to vulnerabilities that you haven't patched yet that were fixed long ago.")
                        print("That's why OpCore-Simplify doesn't work properly.")
               
                        try:
                            print("Checking for updates...")
                            subprocess.run(["cmd", "/c", "usoclient StartInteractiveScan"], check=True)

                            print("Downloading all available updates...")
                            subprocess.run(["cmd", "/c", "usoclient StartDownload"], check=True)

                            print("Installing all available updates...")
                            subprocess.run(["cmd", "/c", "usoclient StartInstall"], check=True)
                            
                            print("Your device is restarting to finish installing updates...")
                            usoclient RestartDevice
                    if build >= 19045.5073:
                        print("You're running a fairly up to date Windows 10. Since Windows 10 is out of support, we'll update your system to a supported version of Windows.")
                        checkwindows11requirements()                                              
    
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
            print("Running connectivity diagnostics...\n")
            print("")
            
            if not self.troubleshoot_connectivity():
                while True:
                    user_input = self.utils.request_input(
                        "Do you want to skip the update process? (yes/No): "
                    ).strip().lower()
                    if user_input == "yes":
                        print("\nUpdate process skipped.")
                        return False
                    elif user_input == "no":
                        print("\nContinuing with update using default version check...")
                        latest_sha_version = "update_forced_by_user"
                        break
                    else:
                        print("\033[91mInvalid selection, please try again.\033[0m\n\n"))
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
