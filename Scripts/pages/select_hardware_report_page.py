import os
import threading

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, FluentIcon, 
    StrongBodyLabel, PrimaryPushButton, ProgressBar,
    IconWidget, ExpandGroupSettingCard
)

from Scripts.datasets import os_data
from Scripts.custom_dialogs import show_info, show_confirmation
from Scripts.state import HardwareReportState, macOSVersionState, SMBIOSState
from Scripts.styles import SPACING, COLORS
from Scripts import ui_utils

class ReportDetailsGroup(ExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(
            FluentIcon.INFO,
            "Hardware Report Details",
            "View selected report paths and validation status",
            parent
        )
        
        self.reportIcon = IconWidget(FluentIcon.INFO)
        self.reportIcon.setFixedSize(16, 16)
        self.reportIcon.setVisible(False)
        
        self.acpiIcon = IconWidget(FluentIcon.INFO)
        self.acpiIcon.setFixedSize(16, 16)
        self.acpiIcon.setVisible(False)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.reportCard = self.addGroup(
            FluentIcon.DOCUMENT,
            "Report Path",
            "Not selected",
            self.reportIcon
        )
        
        self.acpiCard = self.addGroup(
            FluentIcon.FOLDER,
            "ACPI Directory",
            "Not selected",
            self.acpiIcon
        )
        
        self.reportCard.contentLabel.setStyleSheet("color: {};".format(COLORS["text_secondary"]))
        self.acpiCard.contentLabel.setStyleSheet("color: {};".format(COLORS["text_secondary"]))

    def update_status(self, section, path, status_type, message):
        card = self.reportCard if section == "report" else self.acpiCard
        icon_widget = self.reportIcon if section == "report" else self.acpiIcon
        
        if path and path != "Not selected":
            path = os.path.normpath(path)
        
        card.setContent(path)
        card.setToolTip(message if message else path)

        icon = FluentIcon.INFO
        color = COLORS["text_secondary"]
        
        if status_type == "success": 
            color = COLORS["text_primary"]
            icon = FluentIcon.ACCEPT
        elif status_type == "error": 
            color = COLORS["error"]
            icon = FluentIcon.CANCEL
        elif status_type == "warning": 
            color = COLORS["warning"]
            icon = FluentIcon.INFO
        
        card.contentLabel.setStyleSheet("color: {};".format(color))
        icon_widget.setIcon(icon)
        icon_widget.setVisible(True)

class SelectHardwareReportPage(QWidget):
    export_finished_signal = pyqtSignal(bool, str, str, str)
    load_report_progress_signal = pyqtSignal(str, str, int)
    load_report_finished_signal = pyqtSignal(bool, str, str, str)
    report_validated_signal = pyqtSignal(str, str)
    compatibility_checked_signal = pyqtSignal()

    def __init__(self, parent, ui_utils_instance=None):
        super().__init__(parent)
        self.setObjectName("SelectHardwareReport")
        self.controller = parent
        self.ui_utils = ui_utils_instance if ui_utils_instance else ui_utils.UIUtils()
        self._connect_signals()
        self._init_ui()

    def _connect_signals(self):
        self.export_finished_signal.connect(self._handle_export_finished)
        self.load_report_progress_signal.connect(self._handle_load_report_progress)
        self.load_report_finished_signal.connect(self._handle_load_report_finished)
        self.report_validated_signal.connect(self._handle_report_validated)
        self.compatibility_checked_signal.connect(self._handle_compatibility_checked)

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(SPACING["xxlarge"], SPACING["xlarge"], SPACING["xxlarge"], SPACING["xlarge"])
        self.main_layout.setSpacing(SPACING["large"])

        self.main_layout.addWidget(self.ui_utils.create_step_indicator(1))
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(SPACING["small"])
        title = SubtitleLabel("Select Hardware Report")
        subtitle = BodyLabel("Select hardware report of target system you want to build EFI for")
        subtitle.setStyleSheet("color: {};".format(COLORS["text_secondary"]))
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)

        self.main_layout.addSpacing(SPACING["medium"])

        self.create_instructions_card()

        self.create_action_card()
        
        self.create_report_details_group()

        self.main_layout.addStretch()

    def create_instructions_card(self):
        card = self.ui_utils.custom_card(
            card_type="note",
            title="Quick Guide",
            body=(
                "<b>Windows Users:</b> Click <span style=\"color:#0078D4; font-weight:600;\">Export Hardware Report</span> button to generate hardware report for current system. Alternatively, you can manually generate hardware report using Hardware Sniffer tool.<br>"
                "<b>Linux/macOS Users:</b> Please transfer a report generated on Windows. Native generation is not supported."
            )
        )
        self.main_layout.addWidget(card)

    def create_action_card(self):
        self.action_card = CardWidget()
        layout = QVBoxLayout(self.action_card)
        layout.setContentsMargins(SPACING["large"], SPACING["large"], SPACING["large"], SPACING["large"])
        layout.setSpacing(SPACING["medium"])

        title = StrongBodyLabel("Select Methods")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING["medium"])

        self.select_btn = PrimaryPushButton(FluentIcon.FOLDER_ADD, "Select Hardware Report")
        self.select_btn.clicked.connect(self.select_hardware_report)
        btn_layout.addWidget(self.select_btn)

        if os.name == "nt":
            self.export_btn = PushButton(FluentIcon.DOWNLOAD, "Export Hardware Report")
            self.export_btn.clicked.connect(self.export_hardware_report)
            btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)
        
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, SPACING["small"], 0, 0)
        progress_layout.setSpacing(SPACING["medium"])
        
        status_row = QHBoxLayout()
        status_row.setSpacing(SPACING["medium"])
        
        self.status_icon_label = QLabel()
        self.status_icon_label.setFixedSize(28, 28)
        status_row.addWidget(self.status_icon_label)
        
        self.progress_label = StrongBodyLabel("Ready")
        self.progress_label.setStyleSheet("color: {}; font-size: 15px; font-weight: 600;".format(COLORS["text_secondary"]))
        status_row.addWidget(self.progress_label)
        status_row.addStretch()
        
        progress_layout.addLayout(status_row)
        
        self.progress_bar = ProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_container.setVisible(False)
        layout.addWidget(self.progress_container)

        self.progress_helper = ui_utils.ProgressStatusHelper(
            self.status_icon_label,
            self.progress_label,
            self.progress_bar,
            self.progress_container
        )

        self.main_layout.addWidget(self.action_card)

    def create_report_details_group(self):
        self.report_group = ReportDetailsGroup(self)
        self.main_layout.addWidget(self.report_group)

    def select_report_file(self):
        report_path, _ = QFileDialog.getOpenFileName(
            self, "Select Hardware Report", "", "JSON Files (*.json)"
        )
        return report_path if report_path else None

    def select_acpi_folder(self):
        acpi_dir = QFileDialog.getExistingDirectory(self, "Select ACPI Folder", "")
        return acpi_dir if acpi_dir else None
    
    def select_hardware_report(self):
        report_path = self.select_report_file()
        if not report_path:
            return

        report_dir = os.path.dirname(report_path)
        potential_acpi = os.path.join(report_dir, "ACPI")
        
        acpi_dir = None
        if os.path.isdir(potential_acpi):
            if show_confirmation("ACPI Folder Detected", "Found an ACPI folder at: {}\n\nDo you want to use this ACPI folder?".format(potential_acpi), self):
                acpi_dir = potential_acpi

        if not acpi_dir:
            acpi_dir = self.select_acpi_folder()

        if not acpi_dir:
            return
        
        self.load_hardware_report(report_path, acpi_dir)

    def set_detail_status(self, section, path, status_type, message):
        self.report_group.update_status(section, path, status_type, message)

    def suggest_macos_version(self):
        if not self.controller.hardware_state.hardware_report or not self.controller.macos_state.native_version:
            return None

        hardware_report = self.controller.hardware_state.hardware_report
        native_macos_version = self.controller.macos_state.native_version

        suggested_macos_version = native_macos_version[1]

        for device_type in ("GPU", "Network", "Bluetooth", "SD Controller"):
            if device_type in hardware_report:
                for device_name, device_props in hardware_report[device_type].items():
                    if device_props.get("Compatibility", (None, None)) != (None, None):
                        if device_type == "GPU" and device_props.get("Device Type") == "Integrated GPU":
                            device_id = device_props.get("Device ID", " " * 8)[5:]

                            if device_props.get("Manufacturer") == "AMD" or device_id.startswith(("59", "87C0")):
                                suggested_macos_version = "22.99.99"
                            elif device_id.startswith(("09", "19")):
                                suggested_macos_version = "21.99.99"

                        if self.controller.backend.u.parse_darwin_version(suggested_macos_version) > self.controller.backend.u.parse_darwin_version(device_props.get("Compatibility")[0]):
                            suggested_macos_version = device_props.get("Compatibility")[0]

        while True:
            if "Beta" in os_data.get_macos_name_by_darwin(suggested_macos_version):
                suggested_macos_version = "{}{}".format(
                    int(suggested_macos_version[:2]) - 1, suggested_macos_version[2:])
            else:
                break

        self.controller.macos_state.suggested_version = suggested_macos_version

    def load_hardware_report(self, report_path, acpi_dir, from_export=False):
        self.controller.hardware_state = HardwareReportState(report_path=report_path, acpi_dir=acpi_dir)
        self.controller.macos_state = macOSVersionState()
        self.controller.smbios_state = SMBIOSState()
        self.controller.backend.ac.acpi.acpi_tables = {}
        self.controller.backend.ac.acpi.dsdt = None
        
        self.controller.compatibilityPage.update_display()
        self.controller.configurationPage.update_display()
        
        if not from_export:
            self.progress_container.setVisible(True)
            self.select_btn.setEnabled(False)
            if hasattr(self, "export_btn"):
                self.export_btn.setEnabled(False)
        
        progress_offset = 40 if from_export else 0
        self.progress_helper.update("loading", "Validating report...", progress_offset)
        self.report_group.setExpand(True)
        
        def load_thread():
            try:
                progress_scale = 0.5 if from_export else 1.0
                
                def get_progress(base_progress):
                    return progress_offset + int(base_progress * progress_scale)
                
                self.load_report_progress_signal.emit("loading", "Validating report...", get_progress(10))
                
                is_valid, errors, warnings, validated_data = self.controller.backend.v.validate_report(report_path)
                
                if not is_valid or errors:
                    error_msg = "Report Errors:\n" + "\n".join(errors)
                    self.load_report_finished_signal.emit(False, "validation_error", report_path, acpi_dir)
                    return
                
                self.load_report_progress_signal.emit("loading", "Validating report...", get_progress(30))
                
                self.report_validated_signal.emit(report_path, "Hardware report validated successfully.")
                
                self.load_report_progress_signal.emit("loading", "Checking compatibility...", get_progress(35))
                
                self.controller.hardware_state.hardware_report = validated_data
                
                self.controller.hardware_state.hardware_report, self.controller.macos_state.native_version, self.controller.macos_state.ocl_patched_version, self.controller.hardware_state.compatibility_error = self.controller.backend.c.check_compatibility(validated_data)
                
                self.load_report_progress_signal.emit("loading", "Checking compatibility...", get_progress(55))

                self.compatibility_checked_signal.emit()

                if self.controller.hardware_state.compatibility_error:
                    error_msg = self.controller.hardware_state.compatibility_error
                    if isinstance(error_msg, list):
                        error_msg = "\n".join(error_msg)
                    self.load_report_finished_signal.emit(False, "compatibility_error", report_path, acpi_dir)
                    return
                
                self.load_report_progress_signal.emit("loading", "Loading ACPI tables...", get_progress(60))
                
                self.controller.backend.ac.read_acpi_tables(acpi_dir)
                
                self.load_report_progress_signal.emit("loading", "Loading ACPI tables...", get_progress(90))
                
                if not self.controller.backend.ac._ensure_dsdt():
                    self.load_report_finished_signal.emit(False, "acpi_error", report_path, acpi_dir)
                    return
                
                self.load_report_finished_signal.emit(True, "success", report_path, acpi_dir)
                
            except Exception as e:
                self.load_report_finished_signal.emit(False, "Exception: {}".format(e), report_path, acpi_dir)
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def _handle_load_report_progress(self, status, message, progress):
        self.progress_helper.update(status, message, progress)

    def _handle_report_validated(self, report_path, message):
        self.set_detail_status("report", report_path, "success", message)

    def _handle_compatibility_checked(self):
        self.controller.compatibilityPage.update_display()

    def _handle_load_report_finished(self, success, error_type, report_path, acpi_dir):
        self.select_btn.setEnabled(True)
        if hasattr(self, "export_btn"):
            self.export_btn.setEnabled(True)
        
        if success:
            count = len(self.controller.backend.ac.acpi.acpi_tables)
            self.set_detail_status("acpi", acpi_dir, "success", "ACPI Tables loaded: {} tables found.".format(count))
            
            self.progress_helper.update("success", "Hardware report loaded successfully", 100)
            
            self.controller.update_status("Hardware report loaded successfully", "success")
            self.suggest_macos_version()
            self.controller.configurationPage.update_display()
        else:
            if error_type == "validation_error":
                is_valid, errors, warnings, validated_data = self.controller.backend.v.validate_report(report_path)
                msg = "Report Errors:\n" + "\n".join(errors)
                self.set_detail_status("report", report_path, "error", msg)
                self.progress_helper.update("error", "Report validation failed", None)
                show_info("Report Validation Failed", "The hardware report has errors:\n{}\n\nPlease select a valid report file.".format("\n".join(errors)), self)
            elif error_type == "compatibility_error":
                error_msg = self.controller.hardware_state.compatibility_error
                if isinstance(error_msg, list):
                    error_msg = "\n".join(error_msg)
                compat_text = "\nCompatibility Error:\n{}".format(error_msg)
                self.set_detail_status("report", report_path, "error", compat_text)
                show_info("Incompatible Hardware", "Your hardware is not compatible with macOS:\n\n" + error_msg, self)
            elif error_type == "acpi_error":
                self.set_detail_status("acpi", acpi_dir, "error", "No ACPI tables found in selected folder.")
                self.progress_helper.update("error", "No ACPI tables found", None)
                show_info("No ACPI tables", "No ACPI tables found in ACPI folder.", self)
            else:
                self.progress_helper.update("error", "Error: {}".format(error_type), None)
                self.controller.update_status("Failed to load hardware report: {}".format(error_type), "error")

    def export_hardware_report(self):
        self.progress_container.setVisible(True)
        self.select_btn.setEnabled(False)
        if hasattr(self, "export_btn"):
            self.export_btn.setEnabled(False)
        
        self.progress_helper.update("loading", "Gathering Hardware Sniffer...", 10)
        
        current_dir = os.path.dirname(os.path.realpath(__file__))
        main_dir = os.path.dirname(os.path.dirname(current_dir))
        report_dir = os.path.join(main_dir, "SysReport")

        def export_thread():
            try:
                hardware_sniffer = self.controller.backend.o.gather_hardware_sniffer()
                
                if not hardware_sniffer:
                    self.export_finished_signal.emit(False, "Hardware Sniffer not found", "", "")
                    return
                
                self.export_finished_signal.emit(True, "gathering_complete", hardware_sniffer, report_dir)
            except Exception as e:
                self.export_finished_signal.emit(False, "Exception gathering sniffer: {}".format(e), "", "")
        
        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def _handle_export_finished(self, success, message, hardware_sniffer_or_error, report_dir):
        if not success:
            self.progress_container.setVisible(False)
            self.select_btn.setEnabled(True)
            if hasattr(self, "export_btn"):
                self.export_btn.setEnabled(True)
            self.progress_helper.update("error", "Export failed", 0)
            self.controller.update_status(hardware_sniffer_or_error, "error")
            return
        
        if message == "gathering_complete":
            self.progress_helper.update("loading", "Exporting hardware report...", 50)
            
            def run_export_thread():
                try:
                    output = self.controller.backend.r.run({
                        "args": [hardware_sniffer_or_error, "-e", "-o", report_dir]
                    })
                    
                    success = output[-1] == 0
                    error_message = ""
                    report_path = ""
                    acpi_dir = ""

                    if success:
                        report_path = os.path.join(report_dir, "Report.json")
                        acpi_dir = os.path.join(report_dir, "ACPI")
                        error_message = "Export successful"
                    else:
                        error_code = output[-1]
                        if error_code == 3: error_message = "Error collecting hardware."
                        elif error_code == 4: error_message = "Error generating hardware report."
                        elif error_code == 5: error_message = "Error dumping ACPI tables."
                        else: error_message = "Unknown error."

                    paths = "{}|||{}".format(report_path, acpi_dir) if report_path and acpi_dir else ""
                    self.export_finished_signal.emit(success, "export_complete", error_message, paths)
                except Exception as e:
                    self.export_finished_signal.emit(False, "export_complete", "Exception: {}".format(e), "")
            
            thread = threading.Thread(target=run_export_thread, daemon=True)
            thread.start()
            return
        
        if message == "export_complete":
            self.progress_container.setVisible(False)
            self.select_btn.setEnabled(True)
            if hasattr(self, "export_btn"):
                self.export_btn.setEnabled(True)

            self.controller.backend.u.log_message("[EXPORT] Export at: {}".format(report_dir), level="INFO")
            
            if success:
                if report_dir and "|||" in report_dir:
                    report_path, acpi_dir = report_dir.split("|||", 1)
                else:
                    report_path = ""
                    acpi_dir = ""
                
                if report_path and acpi_dir:
                    self.load_hardware_report(report_path, acpi_dir, from_export=True)
                else:
                    self.progress_helper.update("error", "Export completed but paths are invalid", None)
                    self.controller.update_status("Export completed but paths are invalid", "error")
            else:
                self.progress_helper.update("error", "Export failed: {}".format(hardware_sniffer_or_error), None)
                self.controller.update_status("Export failed: {}".format(hardware_sniffer_or_error), "error")