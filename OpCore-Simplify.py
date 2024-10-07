from Scripts.datasets import os_data
from Scripts import acpi_guru
from Scripts import aida64
from Scripts import compatibility_checker
from Scripts import efi_builder
from Scripts import gathering_files
from Scripts import kext_maestro
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
        self.a = aida64.AIDA64()
        self.c = compatibility_checker.CompatibilityChecker()
        self.b = efi_builder.builder()
        self.k = kext_maestro.KextMaestro()
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
            return path, self.a.dump(path)

    def show_hardware_report(self, hardware_report):
        self.u.head("Review the hardware information")
        contents = []
        for index, device_type in enumerate(hardware_report, start=1):
            contents.append("{}. {}{}".format(index, device_type, "" if device_type == "Intel MEI" else ":"))

            if device_type == "SD Controller":
                contents.append("{}* {}".format(" "*4, hardware_report.get(device_type).get("Device Description")))
            elif device_type == "Intel MEI":
                pass
            else:
                for device_name, device_props in hardware_report.get(device_type).items():
                    contents.append("{}* {}{}".format(" "*4, device_name, ": {}".format(device_props) if isinstance(device_props, str) else ""))
        content = "\n".join(contents) + "\n"
        self.u.adjust_window_size(content)
        print(content)
        self.u.request_input()
        return
    
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
        
    def results(self, hardware_report, smbios_model):
        self.u.head("Results")
        print("")
        print("Your OpenCore EFI for {} has been built at:".format(hardware_report.get("Motherboard").get("Motherboard Name")))
        print("\t{}".format(self.result_dir))
        print("")
        print("Before using EFI, please complete the following steps:")
        print("")
        print("1. Use USBToolBox:")
        print("   - Mapping USB with the option 'Use Native Class' enabled.")
        print("   - Use the model identifier '{}'.".format(smbios_model))
        print("")
        print("2. Add USBMap.kext:")
        print("   - Place the created USBMap.kext file into the {} folder.".format("EFI\\OC\\Kexts" if os.name == "nt" else "EFI/OC/Kexts"))
        print("")
        print("3. Edit config.plist:")
        print("   - Use ProperTree to open your config.plist.")
        print("   - Run OC Snapshot by pressing Command/Ctrl + R.")
        print("   - Save the file when finished.")
        print("")
        self.u.open_folder(self.result_dir)
        self.u.request_input()

    def main(self):
        hardware_report_path = None
        supported_macos_version = None
        unsupported_devices = None
        macos_version = None
        smbios_model = None

        while True:
            self.u.head()
            print("")
            print("Hardware Report: {}".format("No report selected" if not hardware_report_path else hardware_report_path))
            print("")
            if hardware_report_path:
                print("* Hardware Compatibility:")
                if supported_macos_version:
                    print("   - Supported macOS Version: {} - {}".format(os_data.get_macos_name_by_darwin(supported_macos_version[-1]), os_data.get_macos_name_by_darwin(supported_macos_version[0])))
                if unsupported_devices:
                    print("   - Unsupported devices:")
                    for index, device_name in enumerate(unsupported_devices, start=1):
                        device_props = unsupported_devices.get(device_name)
                        print("{}{}. {}{}".format(" "*6, index, device_name, "" if not device_props.get("Audio Endpoints") else " ({})".format(", ".join(device_props.get("Audio Endpoints")))))
                print("* EFI Options:")
                print("   - macOS Version: {}{}".format("Unknown" if not macos_version else os_data.get_macos_name_by_darwin(macos_version), "" if not macos_version else " ({})".format(macos_version)))
                print("   - SMBIOS: {}".format("Unknown" if not smbios_model else smbios_model))
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

            try:
                option = int(option)
            except:
                continue

            if option == 1:
                hardware_report_path, hardware_report = self.select_hardware_report()
                self.show_hardware_report(hardware_report)
                supported_macos_version, unsupported_devices = self.c.check_compatibility(hardware_report)
                macos_version = supported_macos_version[-1]
                if int(macos_version[:2]) == os_data.macos_versions[-1].darwin_version and os_data.macos_versions[-1].release_status == "beta":
                    macos_version = str(int(macos_version[:2]) - 1) + macos_version[2:]
                smbios_model = self.s.select_smbios_model(hardware_report, macos_version)
                self.ac.select_acpi_tables()
                self.ac.select_acpi_patches(hardware_report, unsupported_devices, smbios_model)
                self.k.select_required_kexts(hardware_report, smbios_model, macos_version, self.ac.patches)
            elif option < 7:
                try:
                    hardware_report
                except:
                    self.u.request_input("\nPlease select a hardware report to proceed")
                    continue

                if option == 2:
                    macos_version = self.select_macos_version(supported_macos_version)
                    smbios_model = self.s.select_smbios_model(hardware_report, macos_version)
                    self.k.select_required_kexts(hardware_report, smbios_model, macos_version, self.ac.patches)
                elif option == 3:
                    self.ac.customize_patch_selection(hardware_report, unsupported_devices, smbios_model)
                elif option == 4:
                    self.k.kext_configuration_menu(hardware_report, smbios_model, macos_version, self.ac.patches)
                elif option == 5:
                    smbios_model = self.s.customize_smbios_model(hardware_report, smbios_model, macos_version)
                    self.k.kext_configuration_menu(hardware_report, smbios_model, macos_version, self.ac.patches)
                elif option == 6:
                    self.gathering_files()
                    self.b.build_efi(hardware_report, unsupported_devices, smbios_model, macos_version, self.ac, self.k)
                    self.results(hardware_report, smbios_model)

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