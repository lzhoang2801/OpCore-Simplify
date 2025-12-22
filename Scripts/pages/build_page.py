import platform
import os
import shutil
import threading

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ProgressBar, PrimaryPushButton, FluentIcon,
    ScrollArea, TitleLabel
)

from Scripts.datasets import chipset_data
from Scripts.datasets import kext_data
from Scripts.custom_dialogs import show_confirmation
from Scripts.styles import COLORS, SPACING, RADIUS
from Scripts import ui_utils

DEFAULT_LOG_TEXT = "Build log will appear here..."


class BuildPage(ScrollArea):
    build_progress_signal = pyqtSignal(str, list, int, int, bool)
    build_complete_signal = pyqtSignal(bool, object)
    
    def __init__(self, parent, ui_utils_instance=None):
        super().__init__(parent)
        self.setObjectName("buildPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.build_in_progress = False
        self.build_successful = False
        self.ui_utils = ui_utils_instance if ui_utils_instance else ui_utils.UIUtils()
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.expandLayout.setContentsMargins(SPACING["xxlarge"], SPACING["xlarge"], SPACING["xxlarge"], SPACING["xlarge"])
        self.expandLayout.setSpacing(SPACING["xlarge"])

        self.expandLayout.addWidget(self.ui_utils.create_step_indicator(4))

        title_label = TitleLabel("Build OpenCore EFI")
        self.expandLayout.addWidget(title_label)

        subtitle_label = BodyLabel("Build your customized OpenCore EFI ready for installation")
        subtitle_label.setStyleSheet("color: {};".format(COLORS["text_secondary"]))
        self.expandLayout.addWidget(subtitle_label)

        self.expandLayout.addSpacing(SPACING["medium"])

        self.instructions_after_content = QWidget()
        self.instructions_after_content_layout = QVBoxLayout(self.instructions_after_content)
        self.instructions_after_content_layout.setContentsMargins(0, 0, 0, 0)
        self.instructions_after_content_layout.setSpacing(SPACING["medium"])
        
        self.instructions_after_build_card = self.ui_utils.custom_card(
            card_type="warning",
            title="Before Using Your EFI",
            body="Please complete these important steps before using the built EFI:",
            custom_widget=self.instructions_after_content,
            parent=self.scrollWidget
        )
        
        self.instructions_after_build_card.setVisible(False)
        self.expandLayout.addWidget(self.instructions_after_build_card)

        build_control_card = CardWidget(self.scrollWidget)
        build_control_card.setBorderRadius(RADIUS["card"])
        build_control_layout = QVBoxLayout(build_control_card)
        build_control_layout.setContentsMargins(SPACING["large"], SPACING["large"], SPACING["large"], SPACING["large"])
        build_control_layout.setSpacing(SPACING["xlarge"])
        
        control_header_layout = QHBoxLayout()
        control_header_layout.setSpacing(SPACING["medium"])
        control_icon = self.ui_utils.build_icon_label(FluentIcon.DEVELOPER_TOOLS, COLORS["primary"], size=28)
        control_header_layout.addWidget(control_icon)
        
        control_title = SubtitleLabel("Build Control")
        control_title.setStyleSheet("color: {}; font-weight: 600;".format(COLORS["text_primary"]))
        control_header_layout.addWidget(control_title)
        control_header_layout.addStretch()
        build_control_layout.addLayout(control_header_layout)

        action_section = QWidget()
        action_layout = QVBoxLayout(action_section)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING["medium"])

        self.build_btn = PrimaryPushButton(FluentIcon.DEVELOPER_TOOLS, "Build OpenCore EFI")
        self.build_btn.clicked.connect(self.start_build)
        self.build_btn.setFixedHeight(48)
        self.controller.build_btn = self.build_btn
        action_layout.addWidget(self.build_btn)

        self.open_result_btn = PrimaryPushButton(FluentIcon.FOLDER, "Open Result Folder")
        self.open_result_btn.clicked.connect(self.open_result)
        self.open_result_btn.setFixedHeight(48)
        self.open_result_btn.setEnabled(False)
        self.controller.open_result_btn = self.open_result_btn
        action_layout.addWidget(self.open_result_btn)
        
        build_control_layout.addWidget(action_section)

        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(SPACING["medium"])

        status_row = QHBoxLayout()
        status_row.setSpacing(SPACING["medium"])
        
        self.status_icon_label = QLabel()
        self.status_icon_label.setFixedSize(28, 28)
        status_row.addWidget(self.status_icon_label)
        
        self.progress_label = StrongBodyLabel("Ready to build")
        self.progress_label.setStyleSheet("color: {}; font-size: 15px; font-weight: 600;".format(COLORS["text_secondary"]))
        status_row.addWidget(self.progress_label)
        status_row.addStretch()
        
        progress_layout.addLayout(status_row)

        self.progress_bar = ProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(True)
        self.controller.progress_bar = self.progress_bar
        progress_layout.addWidget(self.progress_bar)
        
        self.controller.progress_label = self.progress_label
        self.progress_container.setVisible(False)
        
        self.progress_helper = ui_utils.ProgressStatusHelper(
            self.status_icon_label,
            self.progress_label,
            self.progress_bar,
            self.progress_container
        )
        
        build_control_layout.addWidget(self.progress_container)
        self.expandLayout.addWidget(build_control_card)

        log_card = CardWidget(self.scrollWidget)
        log_card.setBorderRadius(RADIUS["card"])
        log_card_layout = QVBoxLayout(log_card)
        log_card_layout.setContentsMargins(SPACING["large"], SPACING["large"], SPACING["large"], SPACING["large"])
        log_card_layout.setSpacing(SPACING["medium"])
        
        log_header_layout = QHBoxLayout()
        log_header_layout.setSpacing(SPACING["medium"])
        log_icon = self.ui_utils.build_icon_label(FluentIcon.DOCUMENT, COLORS["primary"], size=28)
        log_header_layout.addWidget(log_icon)
        
        log_title = SubtitleLabel("Build Log")
        log_title.setStyleSheet("color: {}; font-weight: 600;".format(COLORS["text_primary"]))
        log_header_layout.addWidget(log_title)
        log_header_layout.addStretch()
        log_card_layout.addLayout(log_header_layout)
        
        log_description = BodyLabel("Detailed build process information and status updates")
        log_description.setStyleSheet("color: {}; font-size: 13px;".format(COLORS["text_secondary"]))
        log_card_layout.addWidget(log_description)

        self.build_log = TextEdit()
        self.build_log.setReadOnly(True)
        self.build_log.setPlainText(DEFAULT_LOG_TEXT)
        self.build_log.setMinimumHeight(400)
        self.build_log.setStyleSheet(f"""
            TextEdit {{
                background-color: rgba(0, 0, 0, 0.03);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: {RADIUS["small"]}px;
                padding: {SPACING["large"]}px;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 13px;
                line-height: 1.7;
            }}
        """)
        self.controller.build_log = self.build_log
        log_card_layout.addWidget(self.build_log)
        
        self.expandLayout.addWidget(log_card)

        self.expandLayout.addStretch()

    def _connect_signals(self):
        self.build_progress_signal.connect(self._handle_build_progress)
        self.build_complete_signal.connect(self._handle_build_complete)

    def _handle_build_progress(self, title, steps, current_step_index, progress, done):
        status = "success" if done else "loading"
        
        if done:
            message = "{} complete!".format(title)
        else:
            step_text = steps[current_step_index] if current_step_index < len(steps) else "Processing"
            step_counter = "Step {}/{}".format(current_step_index + 1, len(steps))
            message = "{}: {}...".format(step_counter, step_text)
        
        if done:
            final_progress = 100
        else:
            if "Building" in title:
                final_progress = 40 + int(progress * 0.6)
            else:
                final_progress = progress
        
        if hasattr(self, "progress_helper"):
            self.progress_helper.update(status, message, final_progress)
        
        if done:
            self.controller.backend.u.log_message("[BUILD] {} complete!".format(title), "SUCCESS", to_build_log=True)
        else:
            step_text = steps[current_step_index] if current_step_index < len(steps) else "Processing"
            self.controller.backend.u.log_message("[BUILD] Step {}/{}: {}...".format(current_step_index + 1, len(steps), step_text), "INFO", to_build_log=True)

    def start_build(self):
        if not self.controller.validate_prerequisites():
            return

        if self.controller.macos_state.needs_oclp:
            content = (
                "1. OpenCore Legacy Patcher allows restoring support for dropped GPUs and Broadcom WiFi on newer versions of macOS, and also enables AppleHDA on macOS Tahoe 26.<br>"
                "2. OpenCore Legacy Patcher needs SIP disabled for applying custom kernel patches, which can cause instability, security risks and update issues.<br>"
                "3. OpenCore Legacy Patcher does not officially support the Hackintosh community.<br><br>"
                "<b><font color=\"{info_color}\">Support for macOS Tahoe 26:</font></b><br>"
                "To patch macOS Tahoe 26, you must download OpenCore-Patcher 3.0.0 or newer from my repository: <a href=\"https://github.com/lzhoang2801/OpenCore-Legacy-Patcher/releases/tag/3.0.0\">lzhoang2801/OpenCore-Legacy-Patcher</a>.<br>"
                "Official Dortania releases or older patches will NOT work with macOS Tahoe 26."
            ).format(error_color=COLORS["error"], info_color="#00BCD4")
            if not show_confirmation("OpenCore Legacy Patcher Warning", content, parent=self.window()):
                return

        self.build_in_progress = True
        self.build_successful = False
        self.build_btn.setEnabled(False)
        self.build_btn.setText("Building...")
        self.open_result_btn.setEnabled(False)
        
        self.progress_helper.update("loading", "Preparing to build...", 0)
        
        self.instructions_after_build_card.setVisible(False)
        self.build_log.clear()
        
        thread = threading.Thread(target=self._start_build_thread, daemon=True)
        thread.start()

    def _start_build_thread(self):
        try:
            backend = self.controller.backend
            backend.o.gather_bootloader_kexts(backend.k.kexts, self.controller.macos_state.darwin_version)

            self._build_opencore_efi(
                self.controller.hardware_state.customized_hardware,
                self.controller.hardware_state.disabled_devices,
                self.controller.smbios_state.model_name,
                self.controller.macos_state.darwin_version,
                self.controller.macos_state.needs_oclp
            )
            
            bios_requirements = self._check_bios_requirements(
                self.controller.hardware_state.customized_hardware,
                self.controller.hardware_state.customized_hardware
            )
            
            self.build_complete_signal.emit(True, bios_requirements)
        except Exception as e:
            self.build_complete_signal.emit(False, None)

    def _check_bios_requirements(self, org_hardware_report, hardware_report):
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

    def _build_opencore_efi(self, hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp):
        steps = [
            "Copying EFI base to results folder",
            "Applying ACPI patches",
            "Copying kexts and snapshotting to config.plist",
            "Generating config.plist",
            "Cleaning up unused drivers, resources, and tools"
        ]
        
        title = "Building OpenCore EFI"
        current_step = 0

        progress = int((current_step / len(steps)) * 100)
        self.build_progress_signal.emit(title, steps, current_step, progress, False)
        current_step += 1
        
        backend = self.controller.backend
        backend.u.create_folder(backend.result_dir, remove_content=True)

        if not os.path.exists(backend.k.ock_files_dir):
            raise Exception("Directory \"{}\" does not exist.".format(backend.k.ock_files_dir))
        
        source_efi_dir = os.path.join(backend.k.ock_files_dir, "OpenCorePkg")
        shutil.copytree(source_efi_dir, backend.result_dir, dirs_exist_ok=True)

        config_file = os.path.join(backend.result_dir, "EFI", "OC", "config.plist")
        config_data = backend.u.read_file(config_file)
        
        if not config_data:
            raise Exception("Error: The file {} does not exist.".format(config_file))
        
        progress = int((current_step / len(steps)) * 100)
        self.build_progress_signal.emit(title, steps, current_step, progress, False)
        current_step += 1
        config_data["ACPI"]["Add"] = []
        config_data["ACPI"]["Delete"] = []
        config_data["ACPI"]["Patch"] = []
        if backend.ac.ensure_dsdt():
            backend.ac.hardware_report = hardware_report
            backend.ac.disabled_devices = disabled_devices
            backend.ac.acpi_directory = os.path.join(backend.result_dir, "EFI", "OC", "ACPI")
            backend.ac.smbios_model = smbios_model
            backend.ac.lpc_bus_device = backend.ac.get_lpc_name()

            for patch in backend.ac.patches:
                if patch.checked:
                    if patch.name == "BATP":
                        patch.checked = getattr(backend.ac, patch.function_name)()
                        backend.k.kexts[kext_data.kext_index_by_name.get("ECEnabler")].checked = patch.checked
                        continue

                    acpi_load = getattr(backend.ac, patch.function_name)()

                    if not isinstance(acpi_load, dict):
                        continue

                    config_data["ACPI"]["Add"].extend(acpi_load.get("Add", []))
                    config_data["ACPI"]["Delete"].extend(acpi_load.get("Delete", []))
                    config_data["ACPI"]["Patch"].extend(acpi_load.get("Patch", []))
        
        config_data["ACPI"]["Patch"].extend(backend.ac.dsdt_patches)
        config_data["ACPI"]["Patch"] = backend.ac.apply_acpi_patches(config_data["ACPI"]["Patch"])

        progress = int((current_step / len(steps)) * 100)
        self.build_progress_signal.emit(title, steps, current_step, progress, False)
        current_step += 1
        kexts_directory = os.path.join(backend.result_dir, "EFI", "OC", "Kexts")
        backend.k.install_kexts_to_efi(macos_version, kexts_directory)
        config_data["Kernel"]["Add"] = backend.k.load_kexts(hardware_report, macos_version, kexts_directory)

        progress = int((current_step / len(steps)) * 100)
        self.build_progress_signal.emit(title, steps, current_step, progress, False)
        current_step += 1
        backend.co.genarate(hardware_report, disabled_devices, smbios_model, macos_version, needs_oclp, backend.k.kexts, config_data)
        backend.u.write_file(config_file, config_data)

        progress = int((current_step / len(steps)) * 100)
        self.build_progress_signal.emit(title, steps, current_step, progress, False)
        current_step += 1
        files_to_remove = []

        drivers_directory = os.path.join(backend.result_dir, "EFI", "OC", "Drivers")
        driver_list = backend.u.find_matching_paths(drivers_directory, extension_filter=".efi")
        driver_loaded = [kext.get("Path") for kext in config_data.get("UEFI").get("Drivers")]
        for driver_path, type in driver_list:
            if not driver_path in driver_loaded:
                files_to_remove.append(os.path.join(drivers_directory, driver_path))

        resources_audio_dir = os.path.join(backend.result_dir, "EFI", "OC", "Resources", "Audio")
        if os.path.exists(resources_audio_dir):
            files_to_remove.append(resources_audio_dir)

        picker_variant = config_data.get("Misc", {}).get("Boot", {}).get("PickerVariant")
        if picker_variant in (None, "Auto"):
            picker_variant = "Acidanthera/GoldenGate" 
        if os.name == "nt":
            picker_variant = picker_variant.replace("/", "\\")

        resources_image_dir = os.path.join(backend.result_dir, "EFI", "OC", "Resources", "Image")
        available_picker_variants = backend.u.find_matching_paths(resources_image_dir, type_filter="dir")

        for variant_name, variant_type in available_picker_variants:
            variant_path = os.path.join(resources_image_dir, variant_name)
            if ".icns" in ", ".join(os.listdir(variant_path)):
                if picker_variant not in variant_name:
                    files_to_remove.append(variant_path)

        tools_directory = os.path.join(backend.result_dir, "EFI", "OC", "Tools")
        tool_list = backend.u.find_matching_paths(tools_directory, extension_filter=".efi")
        tool_loaded = [tool.get("Path") for tool in config_data.get("Misc").get("Tools")]
        for tool_path, type in tool_list:
            if not tool_path in tool_loaded:
                files_to_remove.append(os.path.join(tools_directory, tool_path))

        if "manifest.json" in os.listdir(backend.result_dir):
            files_to_remove.append(os.path.join(backend.result_dir, "manifest.json"))

        for file_path in files_to_remove:
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                backend.u.log_message("[BUILD] Failed to remove file {}: {}".format(os.path.basename(file_path), e), level="WARNING", to_build_log=True)
        
        self.build_progress_signal.emit(title, steps, len(steps), 100, True)

    def show_post_build_instructions(self, bios_requirements):
        while self.instructions_after_content_layout.count():
            item = self.instructions_after_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if bios_requirements:
            bios_header = StrongBodyLabel("1. BIOS/UEFI Settings Required:")
            bios_header.setStyleSheet("color: {}; font-size: 14px;".format(COLORS["warning_text"]))
            self.instructions_after_content_layout.addWidget(bios_header)
            
            bios_text = "\n".join(["  • {}".format(req) for req in bios_requirements])
            bios_label = BodyLabel(bios_text)
            bios_label.setWordWrap(True)
            bios_label.setStyleSheet("color: #424242; line-height: 1.6;")
            self.instructions_after_content_layout.addWidget(bios_label)
            
            self.instructions_after_content_layout.addSpacing(SPACING["medium"])
        
        usb_header = StrongBodyLabel("{}. USB Port Mapping:".format(2 if bios_requirements else 1))
        usb_header.setStyleSheet("color: {}; font-size: 14px;".format(COLORS["warning_text"]))
        self.instructions_after_content_layout.addWidget(usb_header)
        
        path_sep = "\\" if platform.system() == "Windows" else "/"
        
        usb_mapping_instructions = (
            "1. Use USBToolBox tool to map USB ports<br>"
            "2. Add created UTBMap.kext into the EFI{path_sep}OC{path_sep}Kexts folder<br>"
            "3. Remove UTBDefault.kext from the EFI{path_sep}OC{path_sep}Kexts folder<br>"
            "4. Edit config.plist using ProperTree:<br>"
            "   a. Run OC Snapshot (Command/Ctrl + R)<br>"
            "   b. Enable XhciPortLimit quirk if you have more than 15 ports per controller<br>"
            "   c. Save the file when finished."
        ).format(path_sep=path_sep)
        
        usb_label = BodyLabel(usb_mapping_instructions)
        usb_label.setWordWrap(True)
        usb_label.setStyleSheet("color: #424242; line-height: 1.6;")
        self.instructions_after_content_layout.addWidget(usb_label)
        
        self.instructions_after_build_card.setVisible(True)

    def _handle_build_complete(self, success, bios_requirements):
        self.build_in_progress = False
        self.build_successful = success
        
        if success:
            self.progress_helper.update("success", "Build completed successfully!", 100)
            
            self.show_post_build_instructions(bios_requirements)
            
            self.build_btn.setText("Build OpenCore EFI")
            self.build_btn.setEnabled(True)
            self.open_result_btn.setEnabled(True)
            
            success_message = "Your OpenCore EFI has been built successfully!"
            if bios_requirements is not None:
                success_message += " Review the important instructions below."
            
            self.controller.update_status(success_message, "success")

            if hasattr(self.controller, "settings") and self.controller.settings.get_open_folder_after_build():
                if hasattr(self.controller, "open_result_folder_signal"):
                    self.controller.open_result_folder_signal.emit(self.controller.backend.result_dir)
        else:
            self.progress_helper.update("error", "Build OpenCore EFI failed", None)
            
            self.build_btn.setText("Retry Build OpenCore EFI")
            self.build_btn.setEnabled(True)
            self.open_result_btn.setEnabled(False)
            
            self.controller.update_status("An error occurred during the build. Check the log for details.", "error")

    def open_result(self):
        result_dir = self.controller.backend.result_dir
        try:
            self.controller.backend.u.open_folder(result_dir)
        except Exception as e:
            self.controller.update_status("Failed to open result folder: {}".format(e), "warning")

    def refresh(self):
        if not self.build_in_progress:
            if self.build_successful:
                self.progress_container.setVisible(True)
                self.open_result_btn.setEnabled(True)
            else:
                log_text = self.build_log.toPlainText()
                if not log_text or log_text == DEFAULT_LOG_TEXT:
                    self.progress_container.setVisible(False)
                self.open_result_btn.setEnabled(False)