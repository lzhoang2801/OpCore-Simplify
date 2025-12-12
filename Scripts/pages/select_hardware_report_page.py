from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, FluentIcon, 
    StrongBodyLabel, PrimaryPushButton, ProgressBar,
    IconWidget, ExpandGroupSettingCard
)

from Scripts.styles import SPACING, COLORS
from Scripts import ui_utils
from Scripts.custom_dialogs import show_info, show_confirmation
from Scripts.state import HardwareReportState, MacOSVersionState, SMBIOSState

import os
import threading

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
        
        self.reportCard.contentLabel.setStyleSheet("color: {};".format(COLORS['text_secondary']))
        self.acpiCard.contentLabel.setStyleSheet("color: {};".format(COLORS['text_secondary']))

    def update_status(self, section, path, status_type, message):
        card = self.reportCard if section == 'report' else self.acpiCard
        icon_widget = self.reportIcon if section == 'report' else self.acpiIcon
        
        if path and path != "Not selected":
            path = os.path.normpath(path)
        
        card.setContent(path)
        card.setToolTip(message if message else path)

        icon = FluentIcon.INFO
        color = COLORS['text_secondary']
        
        if status_type == 'success': 
            color = COLORS['text_primary']
            icon = FluentIcon.ACCEPT
        elif status_type == 'error': 
            color = COLORS['error']
            icon = FluentIcon.CANCEL
        elif status_type == 'warning': 
            color = COLORS['warning']
            icon = FluentIcon.INFO
        
        if status_type in ['error', 'warning'] and message:
             card.setContent(f"{path}\n\n{message}")
             card.contentLabel.setStyleSheet("color: {};".format(color))
        elif status_type == 'success':
             card.contentLabel.setStyleSheet("color: {};".format(COLORS['text_primary']))
        else:
             card.contentLabel.setStyleSheet("color: {};".format(COLORS['text_secondary']))

        icon_widget.setIcon(icon)
        icon_widget.setVisible(True)

class SelectHardwareReportPage(QWidget):
    load_hardware_report_signal = pyqtSignal(str, str)
    export_finished_signal = pyqtSignal(bool, str, str, str)

    def __init__(self, parent, ui_utils_instance=None):
        super().__init__(parent)
        self.setObjectName("SelectHardwareReport")
        self.controller = parent
        self.ui_utils = ui_utils_instance if ui_utils_instance else ui_utils.UIUtils()
        self._connect_signals()
        self._init_ui()

    def _connect_signals(self):
        self.load_hardware_report_signal.connect(self._handle_load_hardware_report_signal)
        self.export_finished_signal.connect(self._handle_export_finished)

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])
        self.main_layout.setSpacing(SPACING['large'])

        self.main_layout.addWidget(self.ui_utils.create_step_indicator(1))
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(SPACING['small'])
        title = SubtitleLabel("Select Hardware Report")
        subtitle = BodyLabel("Select hardware report of target system you want to build EFI for")
        subtitle.setStyleSheet("color: {};".format(COLORS['text_secondary']))
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)

        self.main_layout.addSpacing(SPACING['medium'])

        self.create_instructions_card()

        self.create_action_card()
        
        self.create_report_details_group()

        self.main_layout.addStretch()

    def create_instructions_card(self):
        card = self.ui_utils.custom_card(
            card_type='note',
            title="Quick Guide",
            body=(
                "<b>Windows Users:</b> Click <span style='color:#0078D4; font-weight:600;'>Export Hardware Report</span> button to generate hardware report for current system. Alternatively, you can manually generate hardware report using Hardware Sniffer tool.<br>"
                "<b>Linux/macOS Users:</b> Please transfer a report generated on Windows. Native generation is not supported."
            )
        )
        self.main_layout.addWidget(card)

    def create_action_card(self):
        self.action_card = CardWidget()
        layout = QVBoxLayout(self.action_card)
        layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        layout.setSpacing(SPACING['medium'])

        title = StrongBodyLabel("Select Methods")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING['medium'])

        self.select_btn = PrimaryPushButton(FluentIcon.FOLDER_ADD, "Select Hardware Report")
        self.select_btn.clicked.connect(self.select_hardware_report)
        btn_layout.addWidget(self.select_btn)

        if os.name == 'nt':
            self.export_btn = PushButton(FluentIcon.DOWNLOAD, "Export Hardware Report")
            self.export_btn.clicked.connect(self.export_hardware_report)
            btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)
        
        self.export_progress_container = QWidget()
        self.export_progress_container.setVisible(False)
        progress_layout = QVBoxLayout(self.export_progress_container)
        progress_layout.setContentsMargins(0, SPACING['small'], 0, 0)
        
        self.export_label = BodyLabel("Exporting hardware report...")
        progress_layout.addWidget(self.export_label)
        
        self.export_bar = ProgressBar()
        self.export_bar.setRange(0, 0)
        progress_layout.addWidget(self.export_bar)
        
        layout.addWidget(self.export_progress_container)

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

    def update_section_status(self, section, path, status_type, message):
        self.report_group.update_status(section, path, status_type, message)

    def load_hardware_report(self, report_path, acpi_dir):
        self.controller.hardware_state = HardwareReportState(report_path=report_path, acpi_dir=acpi_dir)
        self.controller.macos_state = MacOSVersionState()
        self.controller.smbios_state = SMBIOSState()

        self.update_section_status('report', report_path, 'info', "Validating report...")
        self.update_section_status('acpi', acpi_dir, 'info', "Waiting...")
        
        self.report_group.setExpand(True)
        
        is_valid, errors, warnings, validated_data = self.controller.backend.v.validate_report(report_path)
        
        if not is_valid or errors:
            msg = "Report Errors:\n" + "\n".join(errors)
            self.update_section_status('report', report_path, 'error', msg)
            show_info("Report Validation Failed", "The hardware report has errors:\n{}\n\nPlease select a valid report file.".format("\n".join(errors)), self)
            return
            
        elif warnings:
            msg = "Report Warnings:\n" + "\n".join(warnings)
            self.update_section_status('report', report_path, 'warning', msg)
        else:
            self.update_section_status('report', report_path, 'success', "Hardware Report is valid.")

        self.controller.hardware_state.hardware_report = validated_data

        self.controller.hardware_state.hardware_report, self.controller.macos_state.native_version, self.controller.macos_state.ocl_patched_version, self.controller.hardware_state.compatibility_error = self.controller.backend.c.check_compatibility(validated_data)
        
        self.controller.compatibilityPage.update_display()

        if self.controller.hardware_state.compatibility_error:
            error_msg = self.controller.hardware_state.compatibility_error
            if isinstance(error_msg, list):
                error_msg = "\n".join(error_msg)
            
            compat_text = f"\nCompatibility Error:\n{error_msg}"
            current_text = self.report_group.reportCard.contentLabel.text()
            if "Compatibility Error" not in current_text:
                self.update_section_status('report', report_path, 'error', current_text + compat_text)
            
            show_info("Incompatible Hardware", "Your hardware is not compatible with macOS:\n\n" + error_msg, self)
            return

        self.controller.backend.ac.read_acpi_tables(acpi_dir)
        
        if not self.controller.backend.ac._ensure_dsdt():
            self.update_section_status('acpi', acpi_dir, 'error', "No ACPI tables found in selected folder.")
            show_info("No ACPI tables", "No ACPI tables found in ACPI folder.", self)
            return
        else:
            count = len(self.controller.backend.ac.acpi.acpi_tables)
            self.update_section_status('acpi', acpi_dir, 'success', f"ACPI Tables loaded: {count} tables found.")

        self.controller.update_status("Hardware report loaded successfully", 'success')
        self.controller.configurationPage.update_display()

    def export_hardware_report(self):
        hardware_sniffer = self.controller.backend.o.gather_hardware_sniffer()
        if not hardware_sniffer:
            self.controller.update_status("Hardware Sniffer not found", 'error')
            return

        current_dir = os.path.dirname(os.path.realpath(__file__))
        gui_dir = os.path.dirname(current_dir)
        report_dir = os.path.join(gui_dir, "SysReport")

        self.export_progress_container.setVisible(True)
        self.select_btn.setEnabled(False)
        if hasattr(self, 'export_btn'):
            self.export_btn.setEnabled(False)

        def export_thread():
            output = self.controller.backend.r.run({
                "args": [hardware_sniffer, "-e", "-o", report_dir]
            })
            
            success = output[-1] == 0
            message = ""
            report_path = ""
            acpi_dir = ""

            if success:
                report_path = os.path.join(report_dir, "Report.json")
                acpi_dir = os.path.join(report_dir, "ACPI")
                message = "Export successful"
            else:
                error_code = output[-1]
                if error_code == 3: message = "Error collecting hardware."
                elif error_code == 4: message = "Error generating hardware report."
                elif error_code == 5: message = "Error dumping ACPI tables."
                else: message = "Unknown error."

            self.export_finished_signal.emit(success, message, report_path, acpi_dir)

        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def _handle_export_finished(self, success, message, report_path, acpi_dir):
        self.export_progress_container.setVisible(False)
        self.select_btn.setEnabled(True)
        if hasattr(self, 'export_btn'):
            self.export_btn.setEnabled(True)

        if success:
            self.controller.update_status("Export complete!", 'success')
            self.load_hardware_report(report_path, acpi_dir)
        else:
            self.controller.update_status(f"Export failed: {message}", 'error')

    def _handle_load_hardware_report_signal(self, report_path, acpi_dir):
        self.load_hardware_report(report_path, acpi_dir)

    def refresh(self):
        if self.controller.hardware_state.report_path != "Not selected":
             self.report_group.reportCard.setContent(self.controller.hardware_state.report_path)
             self.report_group.reportCard.contentLabel.setStyleSheet("color: {};".format(COLORS['text_primary']))
        if self.controller.hardware_state.acpi_dir != "Not selected":
             self.report_group.acpiCard.setContent(self.controller.hardware_state.acpi_dir)
             self.report_group.acpiCard.contentLabel.setStyleSheet("color: {};".format(COLORS['text_primary']))
