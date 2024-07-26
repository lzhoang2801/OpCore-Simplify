from Scripts import aida64
from Scripts import compatibility_checker
from Scripts import efi_builder
from Scripts import gathering_files
from Scripts import utils
import os

class OCPE:
    def __init__(self):
        self.u = utils.Utils("OpCore Simplify")
        self.o = gathering_files.gatheringFiles()
        self.a = aida64.AIDA64()
        self.c = compatibility_checker.CompatibilityChecker()
        self.b = efi_builder.builder()
        self.u = utils.Utils()
        self.current_version = "0.0.1"
        self.hardware = None
        self.compatibility = None
        self.macos_version = None
        self.macos_version_data = {
            "24": "macOS Sequoia 15 (Beta)",
            "23": "macOS Sonoma 14 (14.4+)",
            "22": "macOS Ventura 13",
            "21": "macOS Monterey 12",
            "20": "macOS Big Sur 11",
            "19": "macOS Catalina 10.15",
            "18": "macOS Mojave 10.14",
            "17": "macOS High Sierra 10.13"
        }
        self.result_dir = os.path.join(os.getcwd(), "Results")

    def check_for_update(self):
        self.u.head("Check for update")
        print("")
        print(f"Current script version: {self.current_version}")
        latest_version = self.u.check_latest_version()
        print(f"Latest script version: {latest_version}")
        print("")
        if latest_version and latest_version > self.current_version:
            print(self.u.message("An update is available at \"https://github.com/lzhoang2801/OpCore-Simplify\"", "reminder"))
            print(self.u.message("Please download the latest version to ensure the best experience.", "reminder"))
            print("")
            self.u.request_input()
        else:
            return
        self.u.exit_program()

    def gathering_files(self):
        self.u.head("Gathering Files")
        print("")
        print("Please wait for download OpenCore NO ACPI, kexts and macserial...")
        print("")

        try:
            self.o.gathering_bootloader_kexts()
        except Exception as e:
            print("")
            print(self.u.message(e, "warning"))
            print("")
            self.u.request_input()
            if len(os.listdir(self.o.ock_files_dir)) < 54:
                os.remove(self.o.download_history_file)
                raise Exception("The download process was not completed. Please try again once the REST API request quota is reset in about an hour")
        return

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
        if not self.hardware:
            self.select_aida64_report()

        self.u.head("Review the hardware information")
        contents = ["\n"]
        for index, device_type in enumerate(self.hardware, start=1):
            contents.append("{}. {}{}".format(index, device_type, "" if device_type == "Intel MEI" else ":"))

            if device_type == "SD Controller":
                contents.append("{}* {}".format(" "*4, self.hardware.get(device_type).get("Device Description")))
            elif device_type == "Intel MEI":
                pass
            else:
                for device_name, device_props in self.hardware.get(device_type).items():
                    if "Controllers" in device_name or "Devices" in device_name or "Drives" in device_name:
                        contents.append("{}* {}:".format(" "*4, device_name))
                        for device_name_child, device_props_child in device_props.items():
                            contents.append("{}- {}".format(" "*8, device_name_child))
                    else:
                        contents.append("{}* {}{}".format(" "*4, device_name, f": {device_props}" if isinstance(device_props, str) else ""))
        content = "\n".join(contents) + "\n"
        print(content, end="")
        self.u.adjust_window_size(content)
        self.u.request_input()
        return
        
    def compatibility_check(self):
        if not self.hardware:
            self.select_aida64_report()

        self.hardware = self.c.check_compatibility(self.hardware)
        self.compatibility = self.hardware.get("Compatibility")
        supported_macOS_version = self.compatibility.get("macOS Version")
        min_verion = supported_macOS_version.get("Min Version")
        max_verion = supported_macOS_version.get("Max Version")

        self.u.head("Compatibility Checker")
        print("")
        if max_verion == -1:
            self.u.request_input("Your hardware is not compatible with macOS!")
            self.u.exit_program()
        print("* Supported macOS Version:")
        print("{}Max Version: {}".format(" "*4, self.macos_version_data[str(max_verion)]))
        print("{}Min Version: {}".format(" "*4, self.macos_version_data[str(min_verion)]))
        if self.compatibility.get("Unsupported Devices"):
            print("* Unsupported devices:")
            for index, device in enumerate(self.compatibility.get("Unsupported Devices"), start=1):
                print("{}{}. {}".format(" "*4, index, device))
        print("")
        self.u.request_input()
        return
    
    def select_macos_version(self):
        if not self.compatibility:
            self.compatibility_check()

        supported_macOS_version = self.compatibility.get("macOS Version")
        min_verion = supported_macOS_version.get("Min Version")
        max_verion = supported_macOS_version.get("Max Version")

        while True:
            self.u.head("Select macOS Version")
            print("")
            for index, macos_version in enumerate(range(max_verion, min_verion - 1, -1), start=1):
                print("{}. {}".format(index, self.macos_version_data[str(macos_version)]))
            print("")
            print("Q. Quit")
            print("")
            option = self.u.request_input("Please select the macOS version you wish to install: ")
            if option.lower() == "q":
                self.u.exit_program()
            if "1" <= option <= str(max_verion - min_verion + 1):
                self.macos_version = max_verion - int(option) + 1
                return
            else:
                continue
        
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
                content += f"{prefix + pointer + path}\n"
                if os.path.isdir(full_path) and not ".kext" in os.path.splitext(path)[1]:
                    extension = '│   ' if pointer == '├── ' else '    '
                    if "Resources" in path:
                        content += prefix + extension + '└── ...hidden\n'
                    else:
                        content += generate_tree_content(full_path, prefix + extension)

            return content

        efi_dir = os.path.join(self.result_dir, "EFI")
        content = "\nYour OpenCore EFI for {} has been built at:".format(self.hardware.get("Motherboard").get("Motherboard Name"))
        content += f"\n\t{self.result_dir}\n"
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
        self.check_for_update()
        self.gathering_files()
        self.select_aida64_report()
        self.hardware_report()
        self.compatibility_check()
        self.select_macos_version()
        self.b.build_efi(self.hardware, self.macos_version)
        self.show_result()
        reminder_message = "\n\nIMPORTANT REMINDER: Please make sure you add the USBMap.kext to /EFI/OC/Kext before using this\nOpenCore EFI.\n\n"
        self.u.exit_program(o.u.message(reminder_message, "reminder"))

if __name__ == '__main__':
    o = OCPE()
    try:
        o.main()
    except SystemExit:
        raise
    except BaseException as e:
        o.u.exit_program(o.u.message("\nAn error occurred: {}\n".format(e)))
