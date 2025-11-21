from Scripts.datasets import os_data
from Scripts.datasets import chipset_data
from Scripts import acpi_guru
from Scripts import compatibility_checker
from Scripts import config_prodigy
from Scripts import gathering_files
from Scripts import hardware_customizer
from Scripts import kext_maestro
from Scripts import run
from Scripts import smbios
from Scripts import utils
import updater
import os
import sys
import re
import shutil
import traceback
import time
import json
from Scripts.utils_re import is_trusted_repo, RepoError
hardware_schema = {
    "type": "object",
    "properties": {
        "CPU": {
            "type": "object",
            "properties": {
                "Vendor": {"type": "string"},
                "Model": {"type": "string"},
                "Cores": {"type": "integer"},
                "Threads": {"type": "integer"},
                "FrequencyGHz": {"type": "number"}
            },
            "required": ["Vendor", "Model", "Cores"]
        },
        "GPU": {
            "type": "object",
            "properties": {
                "Vendor": {"type": "string"},
                "DeviceID": {"type": "string"}
            },
            "required": ["Vendor", "DeviceID"]
        },
        "RAM": {
            "type": "object",
            "properties": {
                "SizeGB": {"type": "integer"},
                "Type": {"type": "string"},
                "SpeedMHz": {"type": "integer"}
            },
            "required": ["SizeGB", "Type"]
        },
        "Storage": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Type": {"type": "string"},
                    "CapacityGB": {"type": "integer"},
                    "Vendor": {"type": "string"}
                },
                "required": ["Type", "CapacityGB"]
            }
        },
        "BIOS": {
            "type": "object",
            "properties": {
                "Version": {"type": "string"},
                "Date": {"type": "string"}
            },
            "required": ["Version"]
        },
        "Motherboard": {"type": "object"},
        "ACPI": {"type": "object"},
        "Network": {"type": "object"},
        "Bluetooth": {"type": "object"},
        "Audio": {"type": "object"}
    },
    "required": ["CPU", "GPU", "RAM", "Storage", "BIOS", "Motherboard"]
}


class OCPE:
    def __init__(self):
        self.u = utils.Utils("OpCore Simplify")
        self.u.clean_temporary_dir()
        self.ac = acpi_guru.ACPIGuru()
        self.c = compatibility_checker.CompatibilityChecker()
        self.co = config_prodigy.ConfigProdigy()
        self.o = gathering_files.gatheringFiles()
        self.h = hardware_customizer.HardwareCustomizer()
        self.k = kext_maestro.KextMaestro()
        self.s = smbios.SMBIOS()
        self.r = run.Run()
        self.result_dir = self.u.get_temporary_dir()

    def select_hardware_report(self):
        self.ac.dsdt = self.ac.acpi.acpi_tables = None

        while True:
            self.u.head("Select hardware report")
            print("")
            if os.name == "nt":
                print("\033[1;93mNote:\033[0m")
                print("- Ensure you are using the latest version of Hardware Sniffer before generating the hardware report.")
                print("- Hardware Sniffer will not collect information related to Resizable BAR option of GPU (disabled by default) and monitor connections in Windows PE.")
                print("")
                print("E. Export hardware report (Recommended) - on Linux or macOS, you can only export via a hardware sniffer manually.")
                print("")
                print("It'll export the hardware report automatically only on Windows.")
                print("")
            print("Q. Quit")
            print("")
        
            user_input = self.u.request_input("Drag and drop your hardware report here (.JSON) or type \"E\" to export: ")
            if user_input.lower() == "q":
                self.u.exit_program()
            if user_input.lower() == "e":
                hardware_sniffer = self.o.gather_hardware_sniffer()

                report_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "SysReport")

                self.u.head("Exporting Hardware Report")
                print("")
                print("Exporting hardware report to {}...".format(report_dir))
                
                output = self.r.run({
                    "args":[hardware_sniffer, "-e", "-o", report_dir]
                })

                if output[-1] != 0:
                    error_code = output[-1]
                    if error_code == 3:
                        error_message = "Error collecting hardware."
                    elif error_code == 4:
                        error_message = "Error generating hardware report."
                    elif error_code == 5:
                        error_message = "Error dumping ACPI tables."
                    else:
                        error_message = "Unknown error."

                    print("")
                    print("Could not export the hardware report. {}".format(error_message))
                    print("Please try again or using Hardware Sniffer manually.")
                    print("")
                    self.u.request_input()
                    continue
                else:
                    report_path = os.path.join(report_dir, "Report.json")
                    acpitables_dir = os.path.join(report_dir, "ACPI")

                    report_data = self.u.read_file(report_path)
                    self.ac.read_acpi_tables(acpitables_dir)
                    
                    return report_path, report_data
                
            path = self.u.normalize_path(user_input)
            path = os.path.normpath(path)
            if not path.endswith("Report.json"):
                raise ValueError("Only Report.json files are allowed")
            max_size_bytes = 100 * 1024 * 1024  # 100 MB limit
            if os.path.getsize(path) > max_size_bytes:
                print("")
                print("Hardware report exceeds 100 MB limit.")
                print("")
                self.u.request_input()
                continue
            report_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "SysReport")
            if not os.path.commonpath([path, report_dir]) == report_dir:
                print("")
                print("Invalid location. Hardware report must be inside SysReport directory.")
                print("")
                self.u.request_input()
                continue
            try:
                data = self.u.read_file(path)
            except Exception as e:  
                print(f"Error reading hardware report: {e}. This malformed report could contain malicious software.")
            try:
                validate(instance=data, schema=hardware_schema)
            except ValidationError as e:
                print("")
                print(f"Invalid hardware report: {e.message}")
                print("")
                self.u.request_input()
                continue
            if not path or os.path.splitext(path)[1].lower() != ".json" or not isinstance(data, dict):
                print("")
                print("Invalid file. Please ensure it is a valid 'Report.json' file.")
                print("")
                self.u.request_input()
                continue
            elif not path or os.path.splitext(path)[1].lower() != ".json" or not isinstance(data, dict):
                print("")
                print("Invalid file. Please ensure it is a valid \"Report.json\" file.")
                print("")
                self.u.request_input()
                continue
            
            return path, data
        
    def show_oclp_warning(self):
        while True:
            self.u.head("OpenCore Legacy Patcher Warning")
            print("")
            print("1. OpenCore Legacy Patcher is the only solution to enable dropped GPU and Broadcom WiFi")
            print("   support in newer macOS versions, as well as to bring back AppleHDA for macOS Tahoe 26.")
            print("")
            print("2. OpenCore Legacy Patcher may disable macOS security features including SIP and AMFI if needed, which may")
            print("   lead to issues such as requiring full installers for updates, application crashes, and")
            print("   system instability.")
            print("")
            print("3. OpenCore Legacy Patcher is not officially supported for Hackintosh community.")
            print("")
            print("SIP, the shortened version of System Integrity Protection, is a security feature introduced")
            print("in OS X 10.11 El Capitan that allows macOS to protect system files from being modified.")
            print(" ")
            print("Like this, Apple makes it difficult attackers to mess with critical system files and inject malware there.")
            print("\033[91mImportant:\033[0m")
            print("Please consider these risks carefully before proceeding.")
            print("")
            print("If your GPU is supported only up until let's say OS X 10.11 El Capitan.")
            print("Then, it's a less severe vulnerability to run macOS 15 Sequoia and disable SIP than")
            print("running outdated version of macOS like OS X 10.11 El Capitan or macOS 10.13 High Sierra by far.")
            print(" ")
            print("\033[1;93mNote:\033[0m")
            print("If you experience black screen after login with OpenCore Legacy Patcher v2.2.0 or newer")
            print("after applying root patches, please revert to version v2.1.2.")
            print("")
            option = self.u.request_input("Do you want to continue with OpenCore Legacy Patcher? (yes/No): ").strip().lower()
            if option == "yes":
                return True
            elif option == "no":
                return False

    def select_macos_version(self, hardware_report, native_macos_version, ocl_patched_macos_version):
        suggested_macos_version = native_macos_version[1]
        version_pattern = re.compile(r'^(\d+)(?:\.(\d+)(?:\.(\d+))?)?$')

        for device_type in ("GPU", "Network", "Bluetooth", "SD Controller"):
            if device_type in hardware_report:
                for device_name, device_props in hardware_report[device_type].items():
                    if device_props.get("Compatibility", (None, None)) != (None, None):
                        if device_type == "GPU" and device_props.get("Device Type") == "Integrated GPU":
                            device_id = device_props.get("Device ID", ""*8)[5:]

                            if device_props.get("Manufacturer") == "AMD" or device_id.startswith(("59", "87C0")):
                                suggested_macos_version = "22.99.99"
                            elif device_id.startswith(("09", "19")):
                                suggested_macos_version = "21.99.99"

                        if self.u.parse_darwin_version(suggested_macos_version) > self.u.parse_darwin_version(device_props.get("Compatibility")[0]):
                            suggested_macos_version = device_props.get("Compatibility")[0]

        while True:
            if "Beta" in os_data.get_macos_name_by_darwin(suggested_macos_version):
                suggested_macos_version = "{}{}".format(int(suggested_macos_version[:2]) - 1, suggested_macos_version[2:])
            else:
                break

        while True:
            self.u.head("Select macOS Version")
            if native_macos_version[1][:2] != suggested_macos_version[:2]:
                print("")
                print("\033[1;36mSuggested macOS version:\033[0m")
                print("- For better compatibility and stability, we suggest you to use only {} or older.".format(os_data.get_macos_name_by_darwin(suggested_macos_version)))
            print("")
            print("Available macOS versions:")
            print("")

            oclp_min = int(ocl_patched_macos_version[-1][:2]) if ocl_patched_macos_version else 99
            oclp_max = int(ocl_patched_macos_version[0][:2]) if ocl_patched_macos_version else 0
            min_version = min(int(native_macos_version[0][:2]), oclp_min)
            max_version = max(int(native_macos_version[-1][:2]), oclp_max)

            for darwin_version in range(min_version, max_version + 1):
                name = os_data.get_macos_name_by_darwin(str(darwin_version))
                label = " (\033[1;93mRequires OpenCore Legacy Patcher\033[0m)" if oclp_min <= darwin_version <= oclp_max else ""
                print("   {}. {}{}".format(darwin_version, name, label))

            print("")
            print("\033[1;93mNote:\033[0m")
            print("- To select a major version, enter the number (e.g., 19).")
            print("- To specify a full version, use the Darwin version format (e.g., 22.4.6).")
            print("")
            print("Q. Quit")
            print("")
            option = self.u.request_input("Please enter the macOS version you want to use (default: {}): ".format(os_data.get_macos_name_by_darwin(suggested_macos_version))) or suggested_macos_version
            if option.lower() == "q":
                self.u.exit_program()

            match = version_pattern.match(option)
            if match:
                target_version = "{}.{}.{}".format(match.group(1), match.group(2) if match.group(2) else 99, match.group(3) if match.group(3) else 99)
                
                if ocl_patched_macos_version and self.u.parse_darwin_version(ocl_patched_macos_version[-1]) <= self.u.parse_darwin_version(target_version) <= self.u.parse_darwin_version(ocl_patched_macos_version[0]):
                    return target_version
                elif self.u.parse_darwin_version(native_macos_version[0]) <= self.u.parse_darwin_version(target_version) <= self.u.parse_darwin_version(native_macos_version[-1]):
                    return target_version

    def build_opencore_efi(self, hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp):
        steps = [
            "Copying EFI base to results folder",
            "Applying ACPI patches",
            "Copying kexts and snapshotting to config.plist",
            "Generating config.plist",
            "Cleaning up unused drivers, resources, and tools"
        ]
        
        title = "Building OpenCore EFI"

        self.u.progress_bar(title, steps, 0)
        self.u.create_folder(self.result_dir, remove_content=True)

        if not os.path.exists(self.k.ock_files_dir):
            raise Exception("Directory '{}' does not exist.".format(self.k.ock_files_dir))
        
        source_efi_dir = os.path.join(self.k.ock_files_dir, "OpenCorePkg")
        shutil.copytree(source_efi_dir, self.result_dir, dirs_exist_ok=True)

        config_file = os.path.join(self.result_dir, "EFI", "OC", "config.plist")
        config_data = self.u.read_file(config_file)
        
        if not config_data:
            raise Exception("Error: The file {} does not exist.".format(config_file))
        
        self.u.progress_bar(title, steps, 1)
        config_data["ACPI"]["Add"] = []
        config_data["ACPI"]["Delete"] = []
        config_data["ACPI"]["Patch"] = []
        if self.ac.ensure_dsdt():
            self.ac.hardware_report = hardware_report
            self.ac.disabled_devices = disabled_devices
            self.ac.acpi_directory = os.path.join(self.result_dir, "EFI", "OC", "ACPI")
            self.ac.smbios_model = smbios_model
            self.ac.lpc_bus_device = self.ac.get_lpc_name()

            for patch in self.ac.patches:
                if patch.checked:
                    if patch.name == "BATP":
                        patch.checked = getattr(self.ac, patch.function_name)()
                        self.k.kexts[kext_maestro.kext_data.kext_index_by_name.get("ECEnabler")].checked = patch.checked
                        continue

                    acpi_load = getattr(self.ac, patch.function_name)()

                    if not isinstance(acpi_load, dict):
                        continue

                    config_data["ACPI"]["Add"].extend(acpi_load.get("Add", []))
                    config_data["ACPI"]["Delete"].extend(acpi_load.get("Delete", []))
                    config_data["ACPI"]["Patch"].extend(acpi_load.get("Patch", []))
        
        config_data["ACPI"]["Patch"].extend(self.ac.dsdt_patches)
        config_data["ACPI"]["Patch"] = self.ac.apply_acpi_patches(config_data["ACPI"]["Patch"])

        self.u.progress_bar(title, steps, 2)
        kexts_directory = os.path.join(self.result_dir, "EFI", "OC", "Kexts")
        self.k.install_kexts_to_efi(macos_version, kexts_directory)
        config_data["Kernel"]["Add"] = self.k.load_kexts(hardware_report, macos_version, kexts_directory)

        self.u.progress_bar(title, steps, 3)
        self.co.genarate(hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp, self.k.kexts, config_data)
        self.u.write_file(config_file, config_data)

        self.u.progress_bar(title, steps, 4)
        files_to_remove = []

        drivers_directory = os.path.join(self.result_dir, "EFI", "OC", "Drivers")
        driver_list = self.u.find_matching_paths(drivers_directory, extension_filter=".efi")
        driver_loaded = [kext.get("Path") for kext in config_data.get("UEFI").get("Drivers")]
        for driver_path, type in driver_list:
            if not driver_path in driver_loaded:
                files_to_remove.append(os.path.join(drivers_directory, driver_path))

        resources_audio_dir = os.path.join(self.result_dir, "EFI", "OC", "Resources", "Audio")
        if os.path.exists(resources_audio_dir):
            files_to_remove.append(resources_audio_dir)

        picker_variant = config_data.get("Misc", {}).get("Boot", {}).get("PickerVariant")
        if picker_variant in (None, "Auto"):
            picker_variant = "Acidanthera/GoldenGate" 
        if os.name == "nt":
            picker_variant = picker_variant.replace("/", "\\")

        resources_image_dir = os.path.join(self.result_dir, "EFI", "OC", "Resources", "Image")
        available_picker_variants = self.u.find_matching_paths(resources_image_dir, type_filter="dir")

        for variant_name, variant_type in available_picker_variants:
            variant_path = os.path.join(resources_image_dir, variant_name)
            if ".icns" in ", ".join(os.listdir(variant_path)):
                if picker_variant not in variant_name:
                    files_to_remove.append(variant_path)

        tools_directory = os.path.join(self.result_dir, "EFI", "OC", "Tools")
        tool_list = self.u.find_matching_paths(tools_directory, extension_filter=".efi")
        tool_loaded = [tool.get("Path") for tool in config_data.get("Misc").get("Tools")]
        for tool_path, type in tool_list:
            if not tool_path in tool_loaded:
                files_to_remove.append(os.path.join(tools_directory, tool_path))

        if "manifest.json" in os.listdir(self.result_dir):
            files_to_remove.append(os.path.join(self.result_dir, "manifest.json"))

        for file_path in files_to_remove:
            try:
                if os.path.isdir(file_path):
                    if not os.path.commonpath([file_path, self.result_dir]) == self.result_dir:
                        raise ValueError("Unsafe deletion attempt outside result directory has been prevented.")
                        sys.exit(3)
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                    sys.exit(3)
            except Exception as e:
                print("Failed to remove file: {}".format(e))
                sys.exit(3)
        
        self.u.progress_bar(title, steps, len(steps), done=True)
        
        print("OpenCore EFI build complete.")
        time.sleep(2)
        
    def check_bios_requirements(self, org_hardware_report, hardware_report):
        requirements = []
        
        org_firmware_type = org_hardware_report.get("BIOS", {}).get("Firmware Type", "Unknown")
        firmware_type = hardware_report.get("BIOS", {}).get("Firmware Type", "Unknown")
        if org_firmware_type == "Legacy" and firmware_type == "UEFI":
            requirements.append("Enable UEFI mode (disable Legacy/CSM (Compatibility Support Module))")

        secure_boot = hardware_report.get("BIOS", {}).get("Secure Boot", "Unknown")
        if secure_boot != "Disabled":
            requirements.append("Disable Secure Boot")
        
        if hardware_report.get("Motherboard", {}).get("Platform") == "Desktop" and hardware_report.get("Motherboard", {}).get("Chipset") in chipset_data.IntelChipsets[112:]:
            resizable_bar_enabled = any(gpu_props.get("Resizable BAR", "Disabled") == "Enabled" for gpu_props in hardware_report.get("GPU", {}).values())
            if not resizable_bar_enabled:
                requirements.append("Enable Above 4G Decoding")
                requirements.append("Disable Resizable BAR/Smart Access Memory")
        if firmware_type == "Legacy":
            cpu_model = hardware_report.get("CPU", {}).get("Model", "").lower()
            first_gen_keywords = [
                "i3-3", "i3-5", "i5-7", "i7-9",   # Bloomfield/Lynnfield ranges
                "i7-8", "i7-7",                   # Lynnfield/Clarksfield
                "i3-5", "i5-6",                   # Clarkdale
                "i3-3", "i5-4", "i7-6",           # Arrandale mobile
                "xeon 55", "xeon 56", "xeon 75"   # Nehalem/Westmere Xeons
            ]
            if any(keyword in cpu_model for keyword in first_gen_keywords):
                print("")
                print("⚠️ Unsupported Legacy BIOS + First Gen Intel CPU detected.")
                print(" ")
                print("OpenCore is unreliable on Nehalem/Westmere systems or earlier unless a third-party BIOS is flashed.")
                print("Recommendation: Use Clover bootloader instead.")
                print ("")
                print("To make it a little bit easier, you can use Unibeast for macOS Catalina and older.")
                print(" Note that for Unibeast you need to create an account for tonymacx if you don't have such yet.")
                print("Configuring with Clover can be extremely difficult if you never Hackintoshed ever.")
                print(" ")
                print("This is an OpenCore issue that it has nothing to do with OpCore-Simplify.")
                print("Please don't report this issue in this repo.")
                print("If you want to report this issue, you need to report it in this repo: https://github.com/acidanthera/OpenCorePkg")
                choice = input("Do you want to experiment with OpenCore anyway? If you use non-OEM BIOS like TinyCore, answer with y. Otherwise, it's recommended to answer with n and continue with Clover.(y/n): ")
                if choice.lower() != "n":
                    print("Thank you for using OpCore-Simplify. Now, you need to reconfigure with Clover instead.")
                    print(" ")
                    print("Reminder: This is an OpenCore issue that it has nothing to do with OpCore-Simplify. Please don't report in this repo that issue.")
                    print("Instead, report it in the following repo if you want: https://github.com/acidanthera/OpenCorePkg")
                    input("\nPress E to exit...")
                    if choice.lower() != "E":
                        sys.exit(1)
                else:
                    print("Proceeding with OpenCore experiment... ⚠️ Expect instability or impossibility to boot if using OEM BIOS.")
        return requirements

    def before_using_efi(self, org_hardware_report, hardware_report):
        while True:
            self.u.head("Before Using EFI")
            print("")                 
            print("\033[93mPlease complete the following steps:\033[0m")
            print("")
            
            bios_requirements = self.check_bios_requirements(org_hardware_report, hardware_report)
            if bios_requirements:
                print("* BIOS/UEFI Settings Required:")
                for requirement in bios_requirements:
                    print("    - {}".format(requirement))
                print("")
            
            print("* USB Mapping:")
            print("If you are unfamiliar what USB port mapping is, it means this: since macOS has a 15 port limit, you need to tell it which ports need to be activated.")
            print("Otherwise, macOS doesn't know which ports need to be activated and might not work properly unless you tell the bootloader to enable all of them.")
            print("To this 15 ports limit, it counts here many internal devices like camera, WiFi/Bluetooth, trackpad, keyboard etc.")
            print("This is done by running the tool USBToolBox which then generates a kernel extension (or in this case: a driver) to tell exactly this.")
            print("But you don't want to enable fingerprinting devices since they are not supported by macOS.")
            print("    - Use USBToolBox tool to map USB ports.")
            print("    - Add created UTBMap.kext into the {} folder.".format("EFI\\OC\\Kexts" if os.name == "nt" else "EFI/OC/Kexts"))
            print("    - Remove UTBDefault.kext in the {} folder.".format("EFI\\OC\\Kexts" if os.name == "nt" else "EFI/OC/Kexts"))
            print("    - Edit config.plist:")
            print("        - Use OpenCore Configurator to open your config.plist.")
            print("        - If you have more than 15 ports on a single controller, enable the XhciPortLimit patch in the OpenCore Configurator app.")
            print("        - Save the file when finished.")
            print("")
            print("Type \"AGREE\" to open the built EFI for you\n")
            response = self.u.request_input("")
            if response.lower() == "agree":
                self.u.open_folder(self.result_dir)
                break
            else:
                print("\033[91mInvalid input. Please try again.\033[0m")

    def main(self):
        hardware_report_path = None
        native_macos_version = None
        disabled_devices = None
        macos_version = None
        ocl_patched_macos_version = None
        needs_oclp = False
        smbios_model = None

        while True:
            self.u.head()
            print("")
            print("  Hardware Report: {}".format(hardware_report_path or 'Not selected'))
            if hardware_report_path:
                print("")
                print("  macOS Version:   {}".format(os_data.get_macos_name_by_darwin(macos_version) if macos_version else 'Not selected') + (' (' + macos_version + ')' if macos_version else '') + ('. \033[1;93mRequires OpenCore Legacy Patcher\033[0m' if needs_oclp else ''))
                print("  SMBIOS:          {}".format(smbios_model or 'Not selected'))
                if disabled_devices:
                    print("  Disabled Devices:")
                    for device, _ in disabled_devices.items():
                        print("    - {}".format(device))
            print("")

            print("1. Select Hardware Report")
            print("2. Select macOS Version")
            print("3. Customize ACPI Patch")
            print("4. Customize Kexts")
            print("5. Customize SMBIOS Model")
            print("6. Build OpenCore EFI")
            print("")
            print("Q. Quit")
            print("")

            option = self.u.request_input("Select an option: ")
            if option.lower() == "q":
                self.u.exit_program()
           
            if option == "1":
                hardware_report_path, hardware_report = self.select_hardware_report()
                hardware_report, native_macos_version, ocl_patched_macos_version = self.c.check_compatibility(hardware_report)
                macos_version = self.select_macos_version(hardware_report, native_macos_version, ocl_patched_macos_version)
                customized_hardware, disabled_devices, needs_oclp = self.h.hardware_customization(hardware_report, macos_version)
                smbios_model = self.s.select_smbios_model(customized_hardware, macos_version)
                if not self.ac.ensure_dsdt():
                    self.ac.select_acpi_tables()
                self.ac.select_acpi_patches(customized_hardware, disabled_devices)
                needs_oclp = self.k.select_required_kexts(customized_hardware, macos_version, needs_oclp, self.ac.patches)
                self.s.smbios_specific_options(customized_hardware, smbios_model, macos_version, self.ac.patches, self.k)

            if not hardware_report_path:
                self.u.head()
                print("\n\n")
                print("\033[1;93mPlease select a hardware report first.\033[0m")
                print("\n\n")
                self.u.request_input("Press Enter to go back...")
                continue

            if option == "2":
                macos_version = self.select_macos_version(hardware_report, native_macos_version, ocl_patched_macos_version)
                customized_hardware, disabled_devices, needs_oclp = self.h.hardware_customization(hardware_report, macos_version)
                smbios_model = self.s.select_smbios_model(customized_hardware, macos_version)
                needs_oclp = self.k.select_required_kexts(customized_hardware, macos_version, needs_oclp, self.ac.patches)
                self.s.smbios_specific_options(customized_hardware, smbios_model, macos_version, self.ac.patches, self.k)
            elif option == "3":
                self.ac.customize_patch_selection()
            elif option == "4":
                self.k.kext_configuration_menu(macos_version)
            elif option == "5":
                smbios_model = self.s.customize_smbios_model(customized_hardware, smbios_model, macos_version)
                self.s.smbios_specific_options(customized_hardware, smbios_model, macos_version, self.ac.patches, self.k)
            elif option == "6":
                if needs_oclp and not self.show_oclp_warning():
                    macos_version = self.select_macos_version(hardware_report, native_macos_version, ocl_patched_macos_version)
                    customized_hardware, disabled_devices, needs_oclp = self.h.hardware_customization(hardware_report, macos_version)
                    smbios_model = self.s.select_smbios_model(customized_hardware, macos_version)
                    needs_oclp = self.k.select_required_kexts(customized_hardware, macos_version, needs_oclp, self.ac.patches)
                    self.s.smbios_specific_options(customized_hardware, smbios_model, macos_version, self.ac.patches, self.k)
                    continue
                trusted_kexts = [kext.download_info["https://github.com/acidanthera/Lilu, https://github.com/acidanthera/VirtualSMC, https://github.com/acidanthera/WhateverGreen, https://github.com/acidanthera/AppleALC, https://nightly.link/ChefKissInc/SMCRadeonSensors/workflows/main/master/Artifacts.zip, https://nightly.link/ChefKissInc/NootRX/workflows/main/master/Artifacts.zip, https://nightly.link/ChefKissInc/NootedRed/workflows/main/master/Artifacts.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Wifi/corecaptureElCap-v1.0.2.zip, https://github.com/dortania/OpenCore-Legacy-Patcher, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Wifi/IO80211ElCap-v2.0.1.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Wifi/IO80211FamilyLegacy-v1.0.0.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Wifi/IOSkywalkFamily-v1.2.0.zip, https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/AppleIGB-v5.11.4.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Ethernet/CatalinaBCM5701Ethernet-v1.0.2.zip, https://github.com/TomHeaven/HoRNDIS/releases/download/rel9.3_2/Release.zip, https://bitbucket.org/RehabMan/os-x-null-ethernet/downloads/RehabMan-NullEthernet-2016-1220.zip, https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/RealtekRTL8100-v2.0.1.zip, https://github.com/Mieze/RTL8111_driver_for_OS_X/releases/download/2.4.2/RealtekRTL8111-V2.4.2.zip, https://github.com/daliansky/OS-X-USB-Inject-All/releases/download/v0.8.0/XHCI-unsupported.kext.zip, https://raw.githubusercontent.com/lzhoang2801/lzhoang2801.github.io/refs/heads/main/public/extra-files/CtlnaAHCIPort-v3.4.1.zip, https://raw.githubusercontent.com/lzhoang2801/lzhoang2801.github.io/refs/heads/main/public/extra-files/SATA-unsupported-v0.9.2.zip, https://github.com/lzhoang2801/lzhoang2801.github.io/raw/refs/heads/main/public/extra-files/VoodooTSCSync-v1.1.zip, https://nightly.link/ChefKissInc/ForgedInvariant/workflows/main/master/Artifacts.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Acidanthera/AMFIPass-v1.4.1-RELEASE.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Misc/ASPP-Override-v1.0.1.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Misc/AppleIntelCPUPowerManagement-v1.0.0.zip, https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Misc/AppleIntelCPUPowerManagementClient-v1.0.0.zip, https://github.com/acidanthera/bugtracker/files/3703498/AppleMCEReporterDisabler.kext.zip"]]
                for kext in self.k.kexts:
                    try:
                        is_trusted_repo(kext["download_info"]["url"])
                        print(f"{kext['name']} repo OK")
                        trusted_kexts.append(kext)
                    except RepoError as e:
                        print(f"{kext['name']} blocked: {e}")
                try:
                    self.o.gather_bootloader_kexts(trusted_kexts, macos_version)
                except Exception as e:
                    print("\033[91mError: {}\033[0m".format(e))
                    print("")
                    self.u.request_input("Press Enter to continue...")
                    continue
                
                self.build_opencore_efi(customized_hardware, disabled_devices, smbios_model, macos_version, needs_oclp)
                self.before_using_efi(hardware_report, customized_hardware)

                self.u.head("Result")
                print("")
                print("Your OpenCore EFI for {} has been built at:".format(customized_hardware.get("Motherboard").get("Name")))
                print("\t{}".format(self.result_dir))
                print("")
                self.u.request_input("Press Enter to main menu...")

if __name__ == '__main__':
    update_flag = updater.Updater().run_update()
    if update_flag:
        os.execv(sys.executable, ['python3'] + sys.argv)

    o = OCPE()
    while True:
        try:
            o.main()
        except Exception as e:
            o.u.head("An Error Occurred")
            print("")
            print(traceback.format_exc())
            o.u.request_input()
