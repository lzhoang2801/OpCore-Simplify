from Scripts.datasets import os_data
from Scripts import acpi_guru
from Scripts import compatibility_checker
from Scripts import efi_builder
from Scripts import gathering_files
from Scripts import smbios
from Scripts import utils
import updater
import os
import sys
import re

class OCPE:
    def __init__(self):
        self.u = utils.Utils("OpCore Simplify")
        self.o = gathering_files.gatheringFiles()
        self.ac = acpi_guru.ACPIGuru()
        self.c = compatibility_checker.CompatibilityChecker()
        self.b = efi_builder.builder()
        self.s = smbios.SMBIOS()
        self.u = utils.Utils()
        self.result_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Results")

    def gathering_files(self):
        self.u.head("Gathering Files")
        print("")
        print("Please wait for download OpenCore NO ACPI, kexts and macserial...")
        print("")

        self.o.get_bootloader_kexts_data()
        self.o.gathering_bootloader_kexts()

    def select_hardware_report(self):
        while True:
            self.u.head("Select hardware report")
            print("")
            print("To ensure the best results, please follow these instructions before generating the hardware report:")
            print("")
            print("  1. Install all available drivers if possible (skip this step when using Windows PE)")
            print("  2. Use the latest version of Hardware Sniffer")
            print("")
            print("Q. Quit")
            print("")
            user_input = self.u.request_input("Please drag and drop your hardware report here: (.JSON) ")
            if user_input.lower() == "q":
                self.u.exit_program()
            path, data = self.u.normalize_path(user_input), self.u.read_file(path)
            if not path or os.path.splitext(path).lower() == ".json" or not isinstance(data, dict): 
                continue
            return path, data
        
    def compatibility_check(self, hardware_report):
        supported_macos_version, unsupported_devices = self.c.check_compatibility(hardware_report)

        self.u.head("Compatibility Checker")
        print("")
        if not supported_macos_version:
            self.u.request_input("Your hardware is not compatible with macOS!")
            self.u.exit_program()
        print("* Supported macOS Version:")
        print("{}Max Version: {}".format(" "*4, os_data.get_macos_name_by_darwin(supported_macos_version[-1])))
        print("{}Min Version: {}".format(" "*4, os_data.get_macos_name_by_darwin(supported_macos_version[0])))
        if unsupported_devices:
            print("* Unsupported devices:")
            for index, device_name in enumerate(unsupported_devices, start=1):
                device_props = unsupported_devices.get(device_name)
                print("{}{}. {}{}".format(" "*4, index, device_name, "" if not device_props.get("Audio Endpoints") else " ({})".format(", ".join(device_props.get("Audio Endpoints")))))
        print("")
        self.u.request_input()
        return supported_macos_version, unsupported_devices
    
    def select_macos_version(self, supported_macos_version):
        version_pattern = re.compile(r'^(\d+)(?:\.(\d+)(?:\.(\d+))?)?$')

        while True:
            self.u.head("Select macOS Version")
            print("")
            for darwin_version in range(int(supported_macos_version[0][:2]), int(supported_macos_version[-1][:2]) + 1):
                print("{}. {}".format(darwin_version, os_data.get_macos_name_by_darwin(str(darwin_version))))
            print("")
            print("Please enter the macOS version you want to select:")
            print("- To select a major version, enter the number (e.g., 19).")
            print("- To specify a full version, use the Darwin version format (e.g., 22.4.6).")
            print("- The version must be in the range from {} to {}.".format(supported_macos_version[0], supported_macos_version[-1]))
            print("")
            print("Q. Quit")
            print("")
            option = self.u.request_input("Select macOS version: ")
            if option.lower() == "q":
                self.u.exit_program()

            match = version_pattern.match(option)
            if match:
                target_version = "{}.{}.{}".format(match.group(1), match.group(2) if match.group(2) else 99, match.group(3) if match.group(3) else 99)
                
                if self.u.parse_darwin_version(supported_macos_version[0]) <= self.u.parse_darwin_version(target_version) <= self.u.parse_darwin_version(supported_macos_version[-1]):
                    return target_version
        
    def show_result(self, hardware_report):
        def generate_tree_content(dir_path, prefix=''):
            contents = sorted(os.listdir(dir_path))
            pointers = ['├── '] * (len(contents) - 1) + ['└── ']
            content = ""

            if not contents:
                content += prefix + '└── (empty)\n'
            elif ".kext" in ", ".join(contents):
                pointers = pointers[:-1] + ['├── '] + ['└── ']
                contents.append("USBMap.kext ({})".format(self.u.message("use USBToolBox with the 'Use Native Class' option enabled to create this kext", "reminder")))

            for pointer, path in zip(pointers, contents):
                if path.startswith("."):
                    continue

                if path.endswith(".dsl"):
                    path += " ({})".format(self.u.message("adjust the ACPI path accordingly before compiling and using it", "reminder"))
                elif path.startswith("itlwm"):
                    path += " ({})".format(self.u.message("use the HeliPort app to connect to WiFi", "reminder"))
                full_path = os.path.join(dir_path, path)
                content += prefix + pointer + path + "\n"
                if os.path.isdir(full_path) and not ".kext" in os.path.splitext(path)[1]:
                    extension = '│   ' if pointer == '├── ' else '    '
                    if "Resources" in path:
                        content += prefix + extension + '└── ...hidden\n'
                    else:
                        content += generate_tree_content(full_path, prefix + extension)

            return content

        efi_dir = os.path.join(self.result_dir, "EFI")
        content = "\nYour OpenCore EFI for {} has been built at:".format(hardware_report.get("Motherboard").get("Motherboard Name"))
        content += "\n\t{}\n".format(self.result_dir)
        content += "\nEFI\n{}\n".format(generate_tree_content(efi_dir))
        self.u.adjust_window_size(content)

        while True:
            self.u.head("Results", resize=False)
            print(content)
            option = self.u.request_input("Do you want to open the OpenCore EFI folder? (yes/no): ")
            if option.lower() == "yes":
                self.u.open_folder(self.result_dir)
                break
            elif option.lower() == "no":
                break
        return

    def main(self):
        hardware_report_path = None
        macos_version = None
        smbios_model = None

        while True:
            self.u.head()
            print("")
            print("Hardware Report: {}".format("No report selected" if not hardware_report_path else hardware_report_path))
            print("macOS Version: {}{}".format("Unknown" if not macos_version else os_data.get_macos_name_by_darwin(macos_version), "" if not macos_version else " ({})".format(macos_version)))
            print("SMBIOS: {}".format("Unknown" if not smbios_model else smbios_model))
            print("")
            print("1. Select Hardware Report")
            print("2. Select macOS Version")
            print("3. Customize ACPI Patch")
            print("4. Customize SMBIOS Model")
            print("5. Build OpenCore EFI")
            print("")
            print("Q. Quit")
            print("")
            option = self.u.request_input("Select an option: ")
            if option.lower() == "q":
                self.u.exit_program()

            try:
                option = int(option)
            except:
                continue

            if option == 1:
                hardware_report_path, hardware_report = self.select_hardware_report()
                supported_macos_version, unsupported_devices = self.compatibility_check(hardware_report)
                macos_version = supported_macos_version[-1]
                if int(macos_version[:2]) == os_data.macos_versions[-1].darwin_version and os_data.macos_versions[-1].release_status == "beta":
                    macos_version = str(int(macos_version[:2]) - 1) + macos_version[2:]
                smbios_model = self.s.select_smbios_model(hardware_report, macos_version)
                self.ac.select_acpi_tables()
                self.ac.select_acpi_patches(hardware_report, unsupported_devices, smbios_model)
            elif option < 6:
                try:
                    hardware_report
                except:
                    self.u.request_input("\nPlease select a hardware report to proceed")
                    continue

                if option == 2:
                    macos_version = self.select_macos_version(supported_macos_version)
                    smbios_model = self.s.select_smbios_model(hardware_report, macos_version)
                elif option == 3:
                    self.ac.customize_patch_selection(hardware_report, unsupported_devices, smbios_model)
                elif option == 4:
                    smbios_model = self.s.customize_smbios_model(hardware_report, smbios_model, macos_version)
                elif option == 5:
                    self.gathering_files()
                    self.b.build_efi(hardware_report, unsupported_devices, smbios_model, macos_version, self.ac)
                    self.show_result(hardware_report)

if __name__ == '__main__':
    o = OCPE()
    try:
        update_flag = updater.Updater().run_update()
        if update_flag:
            os.execv(sys.executable, ['python3'] + sys.argv)
        else:
            o.main()
    except Exception as e:
        o.u.exit_program(o.u.message("\nAn error occurred: {}\n".format(e)))
