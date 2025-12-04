"""
Main GUI application with sidebar navigation using qfluentwidgets
"""

from ..datasets import os_data, mac_model_data
import sys
import os
import threading
import time
import platform

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QIcon, QFont
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    setTheme, Theme, InfoBar, InfoBarPosition
)

from .styles import COLORS, SPACING
from .pages import UploadPage, CompatibilityPage, ConfigurationPage, BuildPage, ConsolePage
from .custom_dialogs import (
    show_input_dialog, show_choice_dialog, show_question_dialog, show_info_dialog,
    show_wifi_profile_extractor_dialog, show_before_using_efi_dialog
)

# Import from Scripts package
scripts_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


class ConsoleRedirector:
    """Redirect stdout to QTextEdit widget"""

    def __init__(self, text_widget, original_stdout=None):
        self.text_widget = text_widget
        self.original_stdout = original_stdout or sys.__stdout__

    def write(self, text):
        if text.strip():
            self.text_widget.append(text.rstrip())
        if self.original_stdout:
            self.original_stdout.write(text)

    def flush(self):
        if self.original_stdout:
            self.original_stdout.flush()


class OpCoreGUI(FluentWindow):
    """Main GUI application with modern sidebar layout using qfluentwidgets"""

    def __init__(self, ocpe_instance):
        """
        Initialize the GUI application

        Args:
            ocpe_instance: Instance of OCPE class from OpCore-Simplify.py
        """
        super().__init__()
        self.ocpe = ocpe_instance

        # Set window properties
        self.setWindowTitle("OpCore Simplify")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)

        # Set cross-platform font with fallbacks
        font = QFont()
        # Use platform-appropriate fonts with fallbacks
        if platform.system() == "Windows":
            font.setFamily("Segoe UI")
        elif platform.system() == "Darwin":  # macOS
            font.setFamily("SF Pro Display")
        else:  # Linux and others
            font.setFamily("Ubuntu")
        # Set fallback fonts
        font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(font)

        # Use light theme by default
        setTheme(Theme.LIGHT)

        # Variables for tracking state
        self.hardware_report_path = "Not selected"
        self.macos_version_text = "Not selected"
        self.macos_version = ""  # Darwin version format (e.g., "22.0.0")
        self.smbios_model_text = "Not selected"
        self.disabled_devices_text = "None"

        # Data storage
        self.hardware_report = None
        self.hardware_report_data = None
        self.customized_hardware = None
        self.disabled_devices = None
        self.native_macos_version = None
        self.ocl_patched_macos_version = None
        self.needs_oclp = False

        # Placeholder for widgets that will be created by pages
        self.build_btn = None
        self.progress_var = None
        self.progress_bar = None
        self.build_log = None
        self.open_result_btn = None
        self.console_log = None

        # Console redirection
        self.console_redirected = False

        # Set up GUI callbacks
        self.ocpe.ac.gui_folder_callback = self.select_acpi_folder_gui
        self.ocpe.u.gui_callback = self.handle_gui_prompt
        self.ocpe.u.gui_parent = self
        self.ocpe.u.gui_progress_callback = self.update_build_progress
        self.ocpe.h.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.h.utils.gui_parent = self
        self.ocpe.k.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.k.utils.gui_parent = self
        self.ocpe.c.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.c.utils.gui_parent = self
        self.ocpe.o.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.o.utils.gui_parent = self
        self.ocpe.ac.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.ac.utils.gui_parent = self

        self.init_navigation()

    def init_navigation(self):
        """Initialize navigation sidebar and pages"""
        # Create pages
        self.uploadPage = UploadPage(self)
        self.compatibilityPage = CompatibilityPage(self)
        self.configurationPage = ConfigurationPage(self)
        self.buildPage = BuildPage(self)
        self.consolePage = ConsolePage(self)

        # Add pages to navigation
        self.addSubInterface(self.uploadPage, FluentIcon.FOLDER_ADD,
                             "1. Upload Report", NavigationItemPosition.TOP)
        self.addSubInterface(self.compatibilityPage, FluentIcon.SEARCH,
                             "2. Compatibility", NavigationItemPosition.TOP)
        self.addSubInterface(self.configurationPage, FluentIcon.SETTING,
                             "3. Configuration", NavigationItemPosition.TOP)
        self.addSubInterface(self.buildPage, FluentIcon.DEVELOPER_TOOLS,
                             "4. Build EFI", NavigationItemPosition.TOP)

        # Add tools section
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.consolePage, FluentIcon.DOCUMENT,
                             "Console Log", NavigationItemPosition.BOTTOM)

        # Set console log widget for redirection
        self.console_log = self.consolePage.console_text

        # Redirect console output
        if not self.console_redirected:
            sys.stdout = ConsoleRedirector(self.console_log)
            self.console_redirected = True

    def log_message(self, message):
        """Log a message to both console and build log"""
        print(message)
        if self.build_log:
            self.build_log.append(message)

    def update_status(self, message, status_type='info'):
        """Update the status using InfoBar"""
        if status_type == 'success':
            InfoBar.success(
                title='Success',
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
        elif status_type == 'error':
            InfoBar.error(
                title='Error',
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
        elif status_type == 'warning':
            InfoBar.warning(
                title='Warning',
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=4000,
                parent=self
            )
        else:  # info
            InfoBar.info(
                title='Info',
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    def select_hardware_report_gui(self):
        """GUI version of hardware report selection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Hardware Report",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            return file_path
        return None

    def select_acpi_folder_gui(self):
        """GUI version of ACPI folder selection"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select ACPI Folder",
            ""
        )

        if folder_path:
            return folder_path
        return None

    def handle_gui_prompt(self, prompt_type, prompt_text, options=None):
        """Handle interactive prompts in GUI mode"""
        if prompt_type == 'input':
            # Simple text input dialog
            text, ok = show_input_dialog(self, "Input Required", prompt_text)
            if ok:
                return text
            return ""

        elif prompt_type == 'choice':
            # Choice dialog with structured options
            if options:
                # Extract title, message, and choices from options dict
                title = options.get('title', 'Select Option')
                message = options.get('message', prompt_text)
                choices = options.get('choices', [])
                default = options.get('default', None)
                warning = options.get('warning', None)
                note = options.get('note', None)

                value, ok = show_choice_dialog(
                    self, title, message, choices, default, warning, note)
                if ok:
                    return value
            return None

        elif prompt_type == 'confirm':
            # Yes/No confirmation dialog with structured options
            if options:
                title = options.get('title', 'Confirmation')
                message = options.get('message', prompt_text)
                default = options.get('default', 'no')
                warning = options.get('warning', None)

                result = show_question_dialog(
                    self, title, message, default, warning)
            else:
                result = show_question_dialog(
                    self, "Confirmation", prompt_text)

            # Convert boolean to "yes"/"no" string for consistency with CLI
            return "yes" if result else "no"

        elif prompt_type == 'info':
            # Informational dialog with OK button
            if options:
                title = options.get('title', 'Information')
                message = options.get('message', prompt_text)
            else:
                title = 'Information'
                message = prompt_text

            return show_info_dialog(self, title, message)

        return None

    def load_hardware_report(self, path, data=None):
        """Load hardware report and update UI"""
        self.hardware_report_path = path

        if data is None:
            data = self.ocpe.u.read_file(path)

        self.hardware_report_data = data

        # Run compatibility check
        self.hardware_report, self.native_macos_version, self.ocl_patched_macos_version = \
            self.ocpe.c.check_compatibility(data)

        # Auto select macOS version
        self.auto_select_macos_version()

        # Update UI
        self.uploadPage.update_status()
        self.compatibilityPage.update_display()

        self.update_status("Hardware report loaded successfully", 'success')

    def auto_select_macos_version(self):
        """Auto-select recommended macOS version"""
        if not self.native_macos_version:
            return

        # Use the suggested version logic from original
        suggested_macos_version = self.native_macos_version[1]
        self.macos_version_text = os_data.get_macos_name_by_darwin(
            suggested_macos_version)

        # Apply the version
        self.apply_macos_version(suggested_macos_version)

    def apply_macos_version(self, version, defer_kext_selection=False):
        """Apply selected macOS version and configure system"""
        self.macos_version = version  # Store Darwin version
        self.macos_version_text = os_data.get_macos_name_by_darwin(version)

        # Perform hardware customization
        self.customized_hardware, self.disabled_devices, self.needs_oclp = \
            self.ocpe.h.hardware_customization(self.hardware_report, version)

        # Select SMBIOS model
        self.smbios_model_text = self.ocpe.s.select_smbios_model(
            self.customized_hardware, version)

        # Select ACPI patches
        if not self.ocpe.ac.ensure_dsdt():
            self.ocpe.ac.select_acpi_tables()
        self.ocpe.ac.select_acpi_patches(
            self.customized_hardware, self.disabled_devices)

        # Select required kexts
        if not defer_kext_selection:
            self.needs_oclp = self.ocpe.k.select_required_kexts(
                self.customized_hardware, version, self.needs_oclp, self.ocpe.ac.patches
            )

        # SMBIOS specific options
        self.ocpe.s.smbios_specific_options(
            self.customized_hardware, self.smbios_model_text, version,
            self.ocpe.ac.patches, self.ocpe.k
        )

        # Update disabled devices display
        if self.disabled_devices:
            self.disabled_devices_text = ", ".join(
                self.disabled_devices.keys())
        else:
            self.disabled_devices_text = "None"

        # Update UI
        self.configurationPage.update_display()

    def export_hardware_report(self):
        """Export hardware report using Hardware Sniffer"""
        hardware_sniffer = self.ocpe.o.gather_hardware_sniffer()

        if not hardware_sniffer:
            self.update_status("Hardware Sniffer not found", 'error')
            return

        report_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "SysReport")

        self.update_status("Exporting hardware report...", 'info')

        # Run export in background thread
        def export_thread():
            output = self.ocpe.r.run({
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

                self.update_status(f"Export failed: {error_message}", 'error')
            else:
                report_path = os.path.join(report_dir, "Report.json")
                acpitables_dir = os.path.join(report_dir, "ACPI")

                report_data = self.ocpe.u.read_file(report_path)
                self.ocpe.ac.read_acpi_tables(acpitables_dir)

                # Load the report
                QTimer.singleShot(0, lambda: self.load_hardware_report(
                    report_path, report_data))

        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def build_efi(self):
        """Build OpenCore EFI"""
        if not self.customized_hardware:
            self.update_status(
                "Please load a hardware report first", 'warning')
            return

        # Check for OCLP warning if needed
        if self.needs_oclp:
            result = show_question_dialog(
                self,
                "OpenCore Legacy Patcher Warning",
                "OpenCore Legacy Patcher is required for your configuration.\n\n"
                "Important considerations:\n"
                "1. OCLP is the only solution for dropped GPU and WiFi support\n"
                "2. OCLP disables macOS security features (SIP, AMFI)\n"
                "3. OCLP is not officially supported for Hackintosh\n\n"
                "Do you want to continue?"
            )

            if not result:
                return

        # Run build in background thread
        def build_thread():
            try:
                # Gather bootloader and kexts (uses Darwin version)
                self.update_status("Gathering bootloader and kexts...", 'info')
                self.ocpe.o.gather_bootloader_kexts(
                    self.ocpe.k.kexts, self.macos_version)

                # Build EFI (uses Darwin version)
                self.update_status("Building OpenCore EFI...", 'info')
                self.ocpe.build_opencore_efi(
                    self.customized_hardware,
                    self.disabled_devices,
                    self.smbios_model_text,
                    self.macos_version,
                    self.needs_oclp
                )

                self.update_status(
                    "OpenCore EFI built successfully!", 'success')

                # Show "Before Using EFI" dialog on main thread
                QTimer.singleShot(0, self.show_before_using_efi_dialog)

            except Exception as e:
                self.update_status(f"Build failed: {str(e)}", 'error')
                import traceback
                print(traceback.format_exc())

        thread = threading.Thread(target=build_thread, daemon=True)
        thread.start()

    def update_build_progress(self, title, steps, current_step_index, progress, done):
        """Update build progress in GUI"""
        # Update progress bar
        if self.progress_bar:
            self.progress_bar.setValue(progress)
        
        # Update build log with step information
        if self.build_log:
            if done:
                self.build_log.append(f"\n✓ {title} - Complete!")
                for step in steps:
                    self.build_log.append(f"  ✓ {step}")
            else:
                step_text = steps[current_step_index]
                self.build_log.append(f"\n> {step_text}...")

    def show_before_using_efi_dialog(self):
        """Show Before Using EFI dialog after successful build"""
        # Calculate BIOS requirements
        bios_requirements = self.ocpe.check_bios_requirements(
            self.hardware_report_data, self.customized_hardware)
        
        # Show the dialog
        result = show_before_using_efi_dialog(
            self, bios_requirements, self.ocpe.result_dir)
        
        if result:
            # User agreed - open the result folder
            self.ocpe.u.open_folder(self.ocpe.result_dir)
            
            # Enable the open result button
            if self.open_result_btn:
                self.open_result_btn.setEnabled(True)

    def run(self):
        """Run the application"""
        self.show()
