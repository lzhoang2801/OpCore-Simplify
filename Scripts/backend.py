import os
import sys
import shutil
import logging
import threading
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

from Scripts.datasets import chipset_data
from Scripts import acpi_guru
from Scripts import compatibility_checker
from Scripts import config_prodigy
from Scripts import gathering_files
from Scripts import hardware_customizer
from Scripts import kext_maestro
from Scripts import report_validator
from Scripts import run
from Scripts import smbios
from Scripts import settings
from Scripts import utils
from Scripts import integrity_checker
from Scripts import resource_fetcher
from Scripts import github
from Scripts import wifi_profile_extractor
from Scripts import dsdt

class LogSignalHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        to_build_log = getattr(record, 'to_build_log', False)
        self.signal.emit(msg, record.levelname, to_build_log)

class Backend(QObject):
    log_message_signal = pyqtSignal(str, str, bool)
    build_progress_signal = pyqtSignal(str, list, int, int, bool)
    update_status_signal = pyqtSignal(str, str)
    build_complete_signal = pyqtSignal(bool, object)
    
    def __init__(self):
        super().__init__()
        
        self.u = utils.Utils()
        self.settings = settings.Settings(utils_instance=self.u)
        self.log_file_path = None
        
        self._setup_logging()
        self.u.clean_temporary_dir()
        
        self.integrity_checker = integrity_checker.IntegrityChecker(utils_instance=self.u)
        
        self.resource_fetcher = resource_fetcher.ResourceFetcher(
            utils_instance=self.u,
            integrity_checker_instance=self.integrity_checker
        )
        self.github = github.Github(
            utils_instance=self.u,
            resource_fetcher_instance=self.resource_fetcher
        )
        
        self.r = run.Run()
        self.wifi_extractor = wifi_profile_extractor.WifiProfileExtractor(
            run_instance=self.r,
            utils_instance=self.u
        )
        self.k = kext_maestro.KextMaestro(utils_instance=self.u)
        self.c = compatibility_checker.CompatibilityChecker(
            utils_instance=self.u,
            settings_instance=self.settings
        )
        self.h = hardware_customizer.HardwareCustomizer(utils_instance=self.u)
        self.v = report_validator.ReportValidator(utils_instance=self.u)
        self.dsdt = dsdt.DSDT(
            utils_instance=self.u,
            github_instance=self.github,
            resource_fetcher_instance=self.resource_fetcher,
            run_instance=self.r
        )
        
        self.o = gathering_files.gatheringFiles(
            utils_instance=self.u,
            github_instance=self.github,
            kext_maestro_instance=self.k,
            integrity_checker_instance=self.integrity_checker,
            resource_fetcher_instance=self.resource_fetcher
        )
        
        self.s = smbios.SMBIOS(
            gathering_files_instance=self.o,
            run_instance=self.r,
            utils_instance=self.u,
            settings_instance=self.settings
        )
        
        self.ac = acpi_guru.ACPIGuru(
            dsdt_instance=self.dsdt,
            smbios_instance=self.s,
            run_instance=self.r,
            utils_instance=self.u
        )
        
        self.co = config_prodigy.ConfigProdigy(
            gathering_files_instance=self.o,
            settings_instance=self.settings,
            smbios_instance=self.s,
            utils_instance=self.u
        )
        
        custom_output_dir = self.settings.get_build_output_directory()
        if custom_output_dir:
            self.result_dir = self.u.create_folder(custom_output_dir, remove_content=True)
        else:
            self.result_dir = self.u.get_temporary_dir()

    def _setup_logging(self):
        logger = logging.getLogger("OpCoreSimplify")
        logger.setLevel(logging.DEBUG)
        
        logger.handlers = []

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(stream_handler)

        signal_handler = LogSignalHandler(self.log_message_signal)
        signal_handler.setLevel(logging.DEBUG)
        signal_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(signal_handler)

        if self.settings.get_enable_debug_logging():
            try:
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                self.log_file_path = os.path.join(log_dir, f"ocs-{timestamp}.txt")
                file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to setup file logging: {e}")

    def progress_bar(self, title, steps, current_step_index, done=False):
        if done:
            progress = 100
        else:
            progress = int((current_step_index / len(steps)) * 100)
        
        self.build_progress_signal.emit(title, steps, current_step_index, progress, done)

    def start_build_process(self, hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp):
        def build_thread():
            try:
                self.update_status_signal.emit("Phase 1/2: Gathering required files...", 'info')
                self.o.gather_bootloader_kexts(self.k.kexts, macos_version)

                self.update_status_signal.emit("Phase 2/2: Building OpenCore EFI...", 'info')
                self.build_opencore_efi(
                    hardware_report,
                    disabled_devices,
                    smbios_model,
                    macos_version,
                    needs_oclp
                )
                
                bios_requirements = self.check_bios_requirements(hardware_report, hardware_report)
                
                self.build_complete_signal.emit(True, bios_requirements)
            except Exception as e:
                self.build_complete_signal.emit(False, None)

        thread = threading.Thread(target=build_thread, daemon=True)
        thread.start()

    def build_opencore_efi(self, hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp):
        # Check which kexts are enabled to determine which steps to show
        itlwm_idx = kext_maestro.kext_data.kext_index_by_name.get("itlwm")
        applealc_idx = kext_maestro.kext_data.kext_index_by_name.get("AppleALC")
        itlwm_enabled = self.k.kexts[itlwm_idx].checked if itlwm_idx is not None else False
        applealc_enabled = self.k.kexts[applealc_idx].checked if applealc_idx is not None else False
        
        # Build dynamic steps list based on enabled kexts
        steps = [
            "Copying EFI base to results folder",
            "Applying ACPI patches",
            "Installing kernel extensions"
        ]
        
        # Make the kext configuration step more descriptive based on what's enabled
        kext_config_step = "Configuring kernel extensions"
        if itlwm_enabled and applealc_enabled:
            kext_config_step += " (WiFi profiles, audio codec)"
        elif itlwm_enabled:
            kext_config_step += " (WiFi profiles)"
        elif applealc_enabled:
            kext_config_step += " (audio codec)"
        steps.append(kext_config_step)
        
        steps.extend([
            "Generating config.plist",
            "Cleaning up unused drivers, resources, and tools"
        ])
        
        title = "Building OpenCore EFI"
        current_step = 0

        self.progress_bar(title, steps, current_step)
        current_step += 1
        self.u.create_folder(self.result_dir, remove_content=True)

        if not os.path.exists(self.k.ock_files_dir):
            raise Exception("Directory '{}' does not exist.".format(self.k.ock_files_dir))
        
        source_efi_dir = os.path.join(self.k.ock_files_dir, "OpenCorePkg")
        shutil.copytree(source_efi_dir, self.result_dir, dirs_exist_ok=True)

        config_file = os.path.join(self.result_dir, "EFI", "OC", "config.plist")
        config_data = self.u.read_file(config_file)
        
        if not config_data:
            raise Exception("Error: The file {} does not exist.".format(config_file))
        
        self.progress_bar(title, steps, current_step)
        current_step += 1
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

        self.progress_bar(title, steps, current_step)
        current_step += 1
        kexts_directory = os.path.join(self.result_dir, "EFI", "OC", "Kexts")
        self.k.install_kexts_to_efi(macos_version, kexts_directory)
        
        # Progress to kext configuration step (WiFi extraction and codec selection happen here)
        self.progress_bar(title, steps, current_step)
        current_step += 1
        
        # Load kexts - this internally handles WiFi profile extraction and codec layout selection
        config_data["Kernel"]["Add"] = self.k.load_kexts(hardware_report, macos_version, kexts_directory)

        self.progress_bar(title, steps, current_step)
        current_step += 1
        self.co.genarate(hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp, self.k.kexts, config_data)
        self.u.write_file(config_file, config_data)

        self.progress_bar(title, steps, current_step)
        current_step += 1
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
        # Use settings if available
        if hasattr(self, 'settings'):
            settings_variant = self.settings.get_picker_variant()
            if settings_variant and settings_variant != "Auto":
                picker_variant = settings_variant
        
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
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                self.u.log_gui(f"⚠ Failed to remove file {os.path.basename(file_path)}: {e}", level="Warning", to_build_log=True)
        
        self.progress_bar(title, steps, len(steps), done=True)

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
                
        return requirements
