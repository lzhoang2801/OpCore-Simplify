from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from qfluentwidgets import PushButton, SubtitleLabel, BodyLabel, CardWidget, FluentIcon, StrongBodyLabel

from ..styles import SPACING
from ..ui_utils import create_step_indicator
from ..custom_dialogs import show_info_dialog
from ..state import HardwareReportState, MacOSVersionState, SMBIOSState

import os
import threading

class SelectHardwareReportPage(QWidget):
    load_hardware_report_signal = pyqtSignal(str, str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("SelectHardwareReport")
        self.controller = parent
        self._connect_signals()
        self.page()

    def _connect_signals(self):
        self.load_hardware_report_signal.connect(self._handle_load_hardware_report_signal)

    def page(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])

        layout.addWidget(create_step_indicator(1))

        title_label = SubtitleLabel("Select Hardware Report")
        layout.addWidget(title_label)

        subtitle_label = BodyLabel("Select hardware report of target system you want to build EFI for")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(SPACING['large'])

        upload_card = CardWidget()
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])

        card_title = StrongBodyLabel("Select Methods")
        upload_layout.addWidget(card_title)

        self.select_btn = PushButton(FluentIcon.FOLDER_ADD, "Select Hardware Report")
        self.select_btn.clicked.connect(self.select_hardware_report)
        upload_layout.addWidget(self.select_btn)

        if os.name == 'nt':
            self.export_btn = PushButton(FluentIcon.DOWNLOAD, "Export Hardware Report")
            self.export_btn.clicked.connect(self.export_hardware_report)
            upload_layout.addWidget(self.export_btn)

        layout.addWidget(upload_card)

        status_card = CardWidget()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])

        status_title = StrongBodyLabel("Current Report")
        status_layout.addWidget(status_title)

        self.status_label = BodyLabel("No hardware report selected")
        self.status_label.setStyleSheet("color: #605E5C;")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_card)

        instructions_card = CardWidget()
        instructions_layout = QVBoxLayout(instructions_card)
        instructions_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])

        instructions_title = StrongBodyLabel("Instructions")
        instructions_layout.addWidget(instructions_title)

        instructions_text = BodyLabel(
            "- For Windows users: Click 'Export Hardware Report' button to generate hardware report for current system. Alternatively, you can manually generate hardware report using Hardware Sniffer tool.\n"
            "- For Linux and macOS users: You must obtain SysReport (hardware report) that was previously generated on a Windows system. Reports created directly from Linux or macOS are not supported.\n"
            "- Remember: Always include ACPI folder together with Report.json file."
        )
        instructions_text.setStyleSheet("color: #605E5C;")
        instructions_text.setWordWrap(True)
        instructions_layout.addWidget(instructions_text)

        layout.addWidget(instructions_card)

        layout.addStretch()

    def select_report_file(self):
        report_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Hardware Report",
            "",
            "JSON Files (*.json)"
        )

        if not report_path:
            return None
        
        return report_path

    def select_acpi_folder(self):
        acpi_dir = QFileDialog.getExistingDirectory(
            self,
            "Select ACPI Folder",
            ""
        )

        if not acpi_dir:
            return None
        
        return acpi_dir
    
    def select_hardware_report(self):
        report_path = self.select_report_file()
        if not report_path:
            return

        report_dir = os.path.dirname(report_path)
        potential_acpi = os.path.join(report_dir, "ACPI")
        
        acpi_dir = None
        if os.path.isdir(potential_acpi):
            acpi_dir = potential_acpi
        else:
            acpi_dir = self.select_acpi_folder()

        if not acpi_dir:
            return
        
        self.load_hardware_report(report_path, acpi_dir)

    def load_hardware_report(self, report_path, acpi_dir):
        self.controller.hardware_state = HardwareReportState(report_path=report_path, acpi_dir=acpi_dir)
        self.controller.macos_state = MacOSVersionState()
        self.controller.smbios_state = SMBIOSState()

        is_valid, errors, warnings, validated_data = self.controller.ocpe.v.validate_report(report_path)
        if not is_valid or errors:
            error_msg = "\n".join(errors)
            show_info_dialog(self, "Report Validation Failed", "The hardware report has errors:\n{}\n\nPlease select a valid report file.".format(error_msg))
            self.controller.hardware_state.report_path = "Not selected"
            self.update_status()
            return
        elif warnings:
            warning_msg = "\n".join(warnings)
            show_info_dialog(self, "Report Warnings", "The hardware report has warnings:\n{}\n\nYou can continue, but some features might be affected.".format(warning_msg))
        
        self.controller.hardware_state.hardware_report = validated_data

        self.controller.hardware_state.hardware_report, self.controller.macos_state.native_version, self.controller.macos_state.ocl_patched_version, self.controller.hardware_state.compatibility_error = self.controller.ocpe.c.check_compatibility(validated_data)
        self.controller.compatibilityPage.update_display()

        self.controller.ocpe.ac.read_acpi_tables(acpi_dir)
        
        if not self.controller.ocpe.ac.acpi.acpi_tables:
            self.controller.hardware_state.report_path = "Not selected"
            self.controller.hardware_state.acpi_dir = "Not selected"
            self.update_status()
            return

        self.controller.update_status("Hardware report loaded and verified successfully", 'success')
        
        if self.controller.hardware_state.compatibility_error:
            error_codes = self.controller.hardware_state.compatibility_error
            error_msg = str(error_codes)
            if isinstance(error_codes, list):
                error_msg = "\n".join(error_codes)
                
            show_info_dialog(self, "Incompatible Hardware", f"Your hardware is not compatible with macOS:\n{error_msg}\n\nCannot proceed with configuration.")
            
            self.controller.hardware_state.report_path = "Not selected"
            self.controller.hardware_state.acpi_dir = "Not selected"
            self.update_status()
            return

        self.update_status()
        self.controller.configurationPage.update_display()

    def export_hardware_report(self):
        hardware_sniffer = self.controller.ocpe.o.gather_hardware_sniffer()

        if not hardware_sniffer:
            self.controller.update_status("Hardware Sniffer not found", 'error')
            return

        current_dir = os.path.dirname(os.path.realpath(__file__))
        gui_dir = os.path.dirname(current_dir)
        report_dir = os.path.join(gui_dir, "SysReport")

        self.controller.update_status("Exporting hardware report...", 'info')

        def export_thread():
            output = self.controller.ocpe.r.run({
                "args": [hardware_sniffer, "-e", "-o", report_dir]
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

                self.controller.update_status_signal.emit("Export failed: {}".format(error_message), 'error')
            else:
                report_path = os.path.join(report_dir, "Report.json")
                acpi_dir = os.path.join(report_dir, "ACPI")

                self.load_hardware_report_signal.emit(report_path, acpi_dir)

        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def _handle_load_hardware_report_signal(self, report_path, acpi_dir):
        self.load_hardware_report(report_path, acpi_dir)

    def update_status(self):
        if self.controller.hardware_state.report_path != "Not selected" and self.controller.hardware_state.acpi_dir != "Not selected":
            self.status_label.setText("Loaded: {} and {}".format(self.controller.hardware_state.report_path, self.controller.hardware_state.acpi_dir))
        elif self.controller.hardware_state.report_path != "Not selected":
            self.status_label.setText("No ACPI folder selected")
        elif self.controller.hardware_state.acpi_dir != "Not selected":
            self.status_label.setText("No hardware report selected")
        else:
            self.status_label.setText("No hardware report and ACPI folder selected")

    def refresh(self):
        self.update_status()