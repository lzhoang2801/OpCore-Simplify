from Scripts.datasets import os_data
from Scripts import aida64
from Scripts import compatibility_checker
from Scripts import efi_builder
from Scripts import gathering_files
from Scripts import utils
import updater
import os
import sys
import re

class OCPE:
    def __init__(self):
        self.u = utils.Utils("OpCore Simplify")
        self.o = gathering_files.gatheringFiles()
        self.a = aida64.AIDA64()
        self.c = compatibility_checker.CompatibilityChecker()
        self.b = efi_builder.builder()
        self.u = utils.Utils()
        self.hardware = None
        self.compatibility = None
        self.result_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Results")

    def gathering_files(self):
        self.u.head("Gathering Files")
        print("")
        print("Please wait for download OpenCore NO ACPI, kexts and macserial...")
        print("")

        self.o.get_bootloader_kexts_data()
        self.o.gathering_bootloader_kexts()

    def select_aida64_report(self):
        while True:
            self.u.head("Select your AIDA64 report")
            print("")
            print("To ensure the best results, please follow these instructions before generating the AIDA64 report:")
            print("")
            print("  1. Install all available drivers if possible (skip this step when using Windows PE)")
            print("  2. Use the latest version of AIDA64 Extreme, available at \"https://aida64.com/downloads\"")
            print("  3. In the Report Wizard, ensure \"Hardware-related pages\" is selected on the Report Profiles\n     and choose the \"HTML\" format")
            print("")
            print("Q. Quit")
            print("")
            user_input = self.u.request_input("Please drag and drop your AIDA64 report here: (*HTML/.htm) ")
            if user_input.lower() == "q":
                self.u.exit_program()
            path = self.u.normalize_path(user_input)
            if not path: 
                continue
            self.hardware = self.a.dump(path)
            return

    def hardware_report(self):
        self.u.head("Review the hardware information")
        contents = []
        for index, device_type in enumerate(self.hardware, start=1):
            contents.append("{}. {}{}".format(index, device_type, "" if device_type == "Intel MEI" else ":"))

            if device_type == "SD Controller":
                contents.append("{}* {}".format(" "*4, self.hardware.get(device_type).get("Device Description")))
            elif device_type == "Intel MEI":
                pass
            else:
                for device_name, device_props in self.hardware.get(device_type).items():
                    contents.append("{}* {}{}".format(" "*4, device_name, ": {}".format(device_props) if isinstance(device_props, str) else ""))
        content = "\n".join(contents) + "\n"
        self.u.adjust_window_size(content)
        print(content)
        self.u.request_input()
        return
        
    def compatibility_check(self):
        self.hardware = self.c.check_compatibility(self.hardware)
        self.compatibility = self.hardware.get("Compatibility")
        supported_macOS_version = self.compatibility.get("macOS Version")

        self.u.head("Compatibility Checker")
        print("")
        if not supported_macOS_version:
            self.u.request_input("Your hardware is not compatible with macOS!")
            self.u.exit_program()
        print("* Supported macOS Version:")
        print("{}Max Version: {}".format(" "*4, os_data.get_macos_name_by_darwin(supported_macOS_version.get("Max Version"))))
        print("{}Min Version: {}".format(" "*4, os_data.get_macos_name_by_darwin(supported_macOS_version.get("Min Version"))))
        if self.compatibility.get("Unsupported Devices"):
            print("* Unsupported devices:")
            for index, device_name in enumerate(self.compatibility.get("Unsupported Devices"), start=1):
                device_props = self.compatibility.get("Unsupported Devices").get(device_name)
                print("{}{}. {}{}".format(" "*4, index, device_name, "" if not device_props.get("Audio Endpoints") else " ({})".format(", ".join(device_props.get("Audio Endpoints")))))
        print("")
        self.u.request_input()
        return
    
    def select_macos_version(self):
        supported_macOS_version = self.compatibility.get("macOS Version")
        min_version = supported_macOS_version.get("Min Version")
        max_version = supported_macOS_version.get("Max Version")

        version_pattern = re.compile(r'^(\d+)(?:\.(\d+)(?:\.(\d+))?)?$')

        while True:
            self.u.head("Select macOS Version")
            print("")
            for index, macos_version_name in enumerate(os_data.get_macos_names(min_version, max_version), start=min_version[0]):
                print("{}. {}".format(index, macos_version_name))
            print("")
            print("Please enter the macOS version you want to select:")
            print("- To select a major version, enter the number (e.g., 19).")
            print("- To specify a full version, use the Darwin version format (e.g., 22.4.6).")
            print("- The version must be in the range from {} to {}.".format(".".join(str(item) for item in min_version), ".".join(str(item) for item in max_version)))
            print("")
            print("Q. Quit")
            print("")
            option = self.u.request_input("Select macOS version: ")
            if option.lower() == "q":
                self.u.exit_program()

            match = version_pattern.match(option)
            if match:
                target_version = (int(match.group(1)), int(match.group(2)) if match.group(2) else 99, int(match.group(3)) if match.group(3) else 99)
                
                if min_version <= target_version <= max_version:
                    self.macos_version = target_version
                    return
        
    def show_result(self):
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
        content = "\nYour OpenCore EFI for {} has been built at:".format(self.hardware.get("Motherboard").get("Motherboard Name"))
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
        self.select_aida64_report()
        self.hardware_report()
        self.compatibility_check()
        self.select_macos_version()
        self.gathering_files()
        self.b.build_efi(self.hardware, self.macos_version)
        self.show_result()
        reminder_message = "\n\nIMPORTANT REMINDER: Please make sure you add the USBMap.kext to /EFI/OC/Kexts before using this\nOpenCore EFI.\n\n"
        self.u.exit_program(o.u.message(reminder_message, "reminder"))

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
