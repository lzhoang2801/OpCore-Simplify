from Scripts import config_prodigy
from Scripts import kext_maestro
from Scripts import utils
import os
import shutil
import re

class builder:
    def __init__(self):
        self.config = config_prodigy.ConfigProdigy()
        self.kext = kext_maestro.KextMaestro()
        self.utils = utils.Utils()
        
    def clean_up(self, config, efi_directory):
        files_to_remove = []

        drivers_directory = os.path.join(efi_directory, "EFI", "OC", "Drivers")
        driver_list = self.utils.find_matching_paths(drivers_directory, extension_filter=".efi")
        driver_loaded = [kext.get("Path") for kext in config.get("UEFI").get("Drivers")]
        for driver_path, type in driver_list:
            if not driver_path in driver_loaded:
                files_to_remove.append(os.path.join(drivers_directory, driver_path))

        tools_directory = os.path.join(efi_directory, "EFI", "OC", "Tools")
        tool_list = self.utils.find_matching_paths(tools_directory, extension_filter=".efi")
        tool_loaded = [tool.get("Path") for tool in config.get("Misc").get("Tools")]
        for tool_path, type in tool_list:
            if not tool_path in tool_loaded:
                files_to_remove.append(os.path.join(tools_directory, tool_path))

        error = None
        for path in files_to_remove:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                error = True
                print("\nFailed to remove file: {}".format(e), end="")
                continue

        if error:
            print("")
            self.utils.request_input()

    def build_efi(self, hardware_report, unsupported_devices, smbios_model, macos_version, acpi_guru, kext_maestro):
        efi_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Results")
        
        self.utils.create_folder(efi_directory, remove_content=True)

        forbidden_chars = r'[<>:"/\\|?*]'
        self.utils.write_file(os.path.join(efi_directory, re.sub(forbidden_chars, '_', hardware_report.get("Motherboard").get("Motherboard Name")) + ".json"), hardware_report)
        
        if not os.path.exists(self.kext.ock_files_dir):
            raise Exception("Directory '{}' does not exist.".format(self.kext.ock_files_dir))
        
        source_efi_dir = os.path.join(self.kext.ock_files_dir, "OpenCore")
        shutil.copytree(source_efi_dir, efi_directory, dirs_exist_ok=True)
        
        config_file = os.path.join(efi_directory, "EFI", "OC", "config.plist")
        config_data = self.utils.read_file(config_file)
        
        if not config_data:
            raise Exception("Error: The file {} does not exist.".format(config_file))
        
        self.config.genarate(hardware_report, unsupported_devices, smbios_model, macos_version, kext_maestro.kexts, config_data)

        acpi_guru.hardware_report = hardware_report
        acpi_guru.unsupported_devices = unsupported_devices
        acpi_guru.acpi_directory = os.path.join(efi_directory, "EFI", "OC", "ACPI")
        acpi_guru.smbios_model = smbios_model
        acpi_guru.get_low_pin_count_bus_device()

        for patch in acpi_guru.patches:
            if patch.checked:
                if patch.name == "BATP":
                    patch.checked = getattr(acpi_guru, patch.function_name)()
                    continue

                acpi_load = getattr(acpi_guru, patch.function_name)()

                if not isinstance(acpi_load, dict):
                    continue

                config_data["ACPI"]["Add"].extend(acpi_load.get("Add", []))
                config_data["ACPI"]["Delete"].extend(acpi_load.get("Delete", []))
                config_data["ACPI"]["Patch"].extend(acpi_load.get("Patch", []))

        config_data["ACPI"]["Patch"] = acpi_guru.apply_acpi_patches(config_data["ACPI"]["Patch"])

        kexts_directory = os.path.join(efi_directory, "EFI", "OC", "Kexts")
        kext_maestro.install_kexts_to_efi(macos_version, kexts_directory)
        config_data["Kernel"]["Add"] = kext_maestro.load_kexts(macos_version, kexts_directory)

        self.utils.write_file(config_file, config_data)

        self.clean_up(config_data, efi_directory)