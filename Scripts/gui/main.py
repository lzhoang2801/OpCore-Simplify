"""Main GUI application with sidebar navigation using qfluentwidgets"""

from ..datasets import os_data, mac_model_data
import sys
import os
import threading
import time
import platform
import re

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
from .pages import HomePage, UploadPage, CompatibilityPage, ConfigurationPage, BuildPage, ConsolePage, SettingsPage
from .custom_dialogs import (
    show_input_dialog, show_choice_dialog, show_question_dialog, show_info_dialog,
    show_before_using_efi_dialog, show_wifi_network_count_dialog, show_codec_layout_dialog
)

# Import from Scripts package
scripts_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


class ConsoleRedirector(QObject):
    """Thread-safe stream redirector that feeds ConsolePage metrics and keeps stdout/stderr mirrored."""

    append_text_signal = pyqtSignal(str, str)
    LEVEL_PATTERN = re.compile(r"\[(info|warning|error|debug)\]", re.IGNORECASE)

    def __init__(self, controller, original_stdout=None, default_level="Info"):
        super().__init__()
        self.controller = controller
        self.original_stdout = original_stdout or sys.__stdout__
        self.default_level = default_level
        self._buffer = ""

        self.append_text_signal.connect(self._append_text_on_main_thread)

    def write(self, text):
        if not text:
            return

        normalized = text.replace('\r', '\n')
        self._buffer += normalized

        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            self._emit_line(line)

        if self.original_stdout:
            self.original_stdout.write(text)

    def _emit_line(self, line):
        message = line.rstrip('\r')
        level = self._detect_level(message)

        if threading.current_thread() == threading.main_thread():
            self.controller.log_message(message, level, to_build_log=False)
        else:
            self.append_text_signal.emit(message, level)

    def _append_text_on_main_thread(self, text, level):
        """Slot that appends text on the main thread"""
        self.controller.log_message(text, level, to_build_log=False)

    def _detect_level(self, text):
        match = self.LEVEL_PATTERN.search(text)
        if match:
            return match.group(1).capitalize()

        lowered = text.lower()
        if lowered.startswith("error") or "traceback" in lowered:
            return "Error"
        if lowered.startswith("warning") or lowered.startswith("warn"):
            return "Warning"
        if lowered.startswith("debug"):
            return "Debug"
        if "failed" in lowered:
            return "Error"
        return self.default_level

    def flush(self):
        if self._buffer:
            self._emit_line(self._buffer)
            self._buffer = ""
        if self.original_stdout:
            self.original_stdout.flush()


class OpCoreGUI(FluentWindow):
    """Main GUI application with modern sidebar layout using qfluentwidgets"""
    
    # Signals for thread-safe GUI operations
    gui_prompt_signal = pyqtSignal(str, str, object, object)  # prompt_type, prompt_text, options, result_holder
    update_status_signal = pyqtSignal(str, str)  # message, status_type
    update_build_progress_signal = pyqtSignal(str, list, int, int, bool)  # title, steps, current_step_index, progress, done
    update_gathering_progress_signal = pyqtSignal(dict)  # progress_info dict
    log_message_signal = pyqtSignal(str, str, bool, bool)  # message, level, to_console, to_build_log

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

        # Apply theme from settings
        from Scripts.settings import Settings
        settings = Settings()
        theme_setting = settings.get_theme()
        if theme_setting == "dark":
            setTheme(Theme.DARK)
        else:
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
        self.progress_label = None
        self.build_log = None
        self.open_result_btn = None
        self.console_log = None
        self.stdout_redirector = None
        self.stderr_redirector = None

        # Console redirection
        self.console_redirected = False
        
        # Connect signals to slots for thread-safe GUI operations
        self.gui_prompt_signal.connect(self._handle_gui_prompt_on_main_thread)
        self.update_status_signal.connect(self.update_status)
        self.update_build_progress_signal.connect(self._update_build_progress_on_main_thread)
        self.update_gathering_progress_signal.connect(self._update_gathering_progress_on_main_thread)
        self.log_message_signal.connect(self._log_message_on_main_thread)

        # Set up GUI handlers - using new direct handler approach
        self.ocpe.ac.gui_folder_callback = self.select_acpi_folder_gui
        
        # Set gui_handler to self for all utils instances (new direct dialog approach)
        self.ocpe.u.gui_handler = self
        self.ocpe.u.gui_progress_callback = self.update_build_progress_threadsafe
        self.ocpe.u.gui_gathering_progress_callback = self.update_gathering_progress_threadsafe
        
        self.ocpe.h.utils.gui_handler = self
        self.ocpe.k.utils.gui_handler = self
        self.ocpe.c.utils.gui_handler = self
        self.ocpe.co.utils.gui_handler = self
        self.ocpe.o.utils.gui_handler = self
        self.ocpe.o.utils.gui_gathering_progress_callback = self.update_gathering_progress_threadsafe
        self.ocpe.ac.utils.gui_handler = self
        
        # Keep old gui_callback for backward compatibility during migration
        self.ocpe.u.gui_callback = self.handle_gui_prompt_threadsafe
        self.ocpe.h.utils.gui_callback = self.handle_gui_prompt_threadsafe
        self.ocpe.k.utils.gui_callback = self.handle_gui_prompt_threadsafe
        self.ocpe.c.utils.gui_callback = self.handle_gui_prompt_threadsafe
        self.ocpe.co.utils.gui_callback = self.handle_gui_prompt_threadsafe
        self.ocpe.o.utils.gui_callback = self.handle_gui_prompt_threadsafe

        utils_with_logging = {
            self.ocpe.u,
            self.ocpe.h.utils,
            self.ocpe.k.utils,
            self.ocpe.c.utils,
            self.ocpe.co.utils,
            self.ocpe.o.utils,
            self.ocpe.ac.utils,
        }
        for utils_instance in utils_with_logging:
            if hasattr(utils_instance, "gui_log_callback"):
                utils_instance.gui_log_callback = self._dispatch_backend_log

        self.init_navigation()

    def init_navigation(self):
        """Initialize navigation sidebar and pages"""
        # Create pages
        self.homePage = HomePage(self)
        self.uploadPage = UploadPage(self)
        self.compatibilityPage = CompatibilityPage(self)
        self.configurationPage = ConfigurationPage(self)
        self.buildPage = BuildPage(self)
        self.consolePage = ConsolePage(self)
        self.settingsPage = SettingsPage(self)

        # Add pages to navigation
        self.addSubInterface(self.homePage, FluentIcon.HOME,
                             "Home", NavigationItemPosition.TOP)
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
        self.addSubInterface(self.settingsPage, FluentIcon.SETTING,
                             "Settings", NavigationItemPosition.BOTTOM)

        # Set console log widget for redirection/state sharing
        self.console_log = self.consolePage.console_text

        # Redirect console output
        if not self.console_redirected:
            self.stdout_redirector = ConsoleRedirector(
                controller=self,
                original_stdout=sys.__stdout__,
                default_level="Info",
            )
            self.stderr_redirector = ConsoleRedirector(
                controller=self,
                original_stdout=sys.__stderr__,
                default_level="Error",
            )
            sys.stdout = self.stdout_redirector
            sys.stderr = self.stderr_redirector
            self.console_redirected = True

    def log_message(self, message, level="Info", *, to_console=True, to_build_log=True):
        """Log a message to console dashboard and/or build log in a thread-safe way."""
        if threading.current_thread() != threading.main_thread():
            self.log_message_signal.emit(message, level, to_console, to_build_log)
            return
        self._log_message_on_main_thread(message, level, to_console, to_build_log)

    def _log_message_on_main_thread(self, message, level, to_console, to_build_log):
        lines = message.splitlines()
        if not lines:
            lines = [""]

        if to_console and hasattr(self, "consolePage") and self.consolePage:
            for line in lines:
                self.consolePage.append_log(line, level)

        if to_build_log and self.build_log:
            for line in lines:
                self.build_log.append(line)

    def _dispatch_backend_log(self, message, level="Info", to_build_log=False):
        """Callback passed to backend utils to surface logs in the GUI."""
        self.log_message(message, level, to_console=True, to_build_log=to_build_log)

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

        elif prompt_type == 'wifi_network_count':
            # WiFi network count selection dialog - the only WiFi dialog we actually need
            if options:
                total_networks = options.get('total_networks', 5)
                count, ok = show_wifi_network_count_dialog(self, total_networks)
                return (count, ok)
            return (None, False)

        elif prompt_type == 'codec_layout':
            # Codec layout selection dialog
            if options:
                codec_id = options.get('codec_id')
                available_layouts = options.get('available_layouts', [])
                default_layout = options.get('default_layout')
                recommended_layouts = options.get('recommended_layouts', [])
                
                layout_id, ok = show_codec_layout_dialog(
                    self, codec_id, available_layouts, default_layout, recommended_layouts)
                return (layout_id, ok)
            return (None, False)

        return None

    def handle_gui_prompt_threadsafe(self, prompt_type, prompt_text, options=None):
        """Thread-safe wrapper for handle_gui_prompt that can be called from any thread"""
        # Check if we're on the main thread
        if threading.current_thread() == threading.main_thread():
            # We're on the main thread, call directly
            return self.handle_gui_prompt(prompt_type, prompt_text, options)
        
        # We're on a background thread, use signal to invoke on main thread
        # Use threading.Event for proper synchronization
        result_holder = {'result': None}
        event = threading.Event()
        
        # Emit signal to main thread
        self.gui_prompt_signal.emit(prompt_type, prompt_text, options, (result_holder, event))
        
        # Wait for result from main thread without timeout - dialogs should wait for user interaction
        event.wait(timeout=None)
        
        return result_holder['result']
    
    def _handle_gui_prompt_on_main_thread(self, prompt_type, prompt_text, options, holder_tuple):
        """Slot that handles GUI prompts on the main thread"""
        result_holder, event = holder_tuple
        try:
            result = self.handle_gui_prompt(prompt_type, prompt_text, options)
            result_holder['result'] = result
        except Exception as e:
            # Log error but ensure event is set to prevent deadlock
            print(f"Error in GUI prompt handler: {e}")
            result_holder['result'] = None
        finally:
            # Always signal completion to prevent deadlock
            event.set()

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

                self.update_status_signal.emit(f"Export failed: {error_message}", 'error')
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
                self.update_status_signal.emit("Gathering bootloader and kexts...", 'info')
                self.ocpe.o.gather_bootloader_kexts(
                    self.ocpe.k.kexts, self.macos_version)

                # Build EFI (uses Darwin version)
                self.update_status_signal.emit("Building OpenCore EFI...", 'info')
                self.ocpe.build_opencore_efi(
                    self.customized_hardware,
                    self.disabled_devices,
                    self.smbios_model_text,
                    self.macos_version,
                    self.needs_oclp
                )

                self.update_status_signal.emit(
                    "OpenCore EFI built successfully!", 'success')

                # Show "Before Using EFI" dialog on main thread
                QTimer.singleShot(0, self.show_before_using_efi_dialog)

            except Exception as e:
                self.update_status_signal.emit(f"Build failed: {str(e)}", 'error')
                import traceback
                print(traceback.format_exc())
                # Re-enable build button on error
                if self.build_btn:
                    QTimer.singleShot(0, lambda: self.build_btn.setEnabled(True))

        thread = threading.Thread(target=build_thread, daemon=True)
        thread.start()

    def update_gathering_progress_threadsafe(self, progress_info):
        """Thread-safe wrapper for update_gathering_progress that can be called from any thread"""
        # Check if we're on the main thread
        if threading.current_thread() == threading.main_thread():
            # We're on the main thread, call directly
            self.update_gathering_progress(progress_info)
        else:
            # We're on a background thread, use signal to invoke on main thread
            self.update_gathering_progress_signal.emit(progress_info)
    
    def _update_gathering_progress_on_main_thread(self, progress_info):
        """Slot that handles gathering progress updates on the main thread"""
        self.update_gathering_progress(progress_info)
    
    def update_gathering_progress(self, progress_info):
        """Update gathering files progress in GUI"""
        current = progress_info.get('current', 0)
        total = progress_info.get('total', 1)
        product_name = progress_info.get('product_name', '')
        status = progress_info.get('status', 'downloading')
        
        # Update progress bar
        if self.progress_bar:
            progress_percent = int((current / total) * 100) if total > 0 else 0
            self.progress_bar.setValue(progress_percent)
        
        # Update progress label
        if self.progress_label:
            if status == 'complete':
                self.progress_label.setText("✓ All files gathered successfully!")
            elif status == 'downloading':
                self.progress_label.setText(f"⬇ Downloading {current}/{total}: {product_name}")
            elif status == 'processing':
                self.progress_label.setText(f"✓ Processing {current}/{total}: {product_name}")
        
        if status == 'complete':
            self.log_message("\n✓ All files gathered successfully!", to_build_log=True)
        elif status == 'downloading':
            self.log_message(f"⬇ {current}/{total}: {product_name}", to_build_log=True)
    
    def update_build_progress_threadsafe(self, title, steps, current_step_index, progress, done):
        """Thread-safe wrapper for update_build_progress that can be called from any thread"""
        # Check if we're on the main thread
        if threading.current_thread() == threading.main_thread():
            # We're on the main thread, call directly
            self.update_build_progress(title, steps, current_step_index, progress, done)
        else:
            # We're on a background thread, use signal to invoke on main thread
            self.update_build_progress_signal.emit(title, steps, current_step_index, progress, done)
    
    def _update_build_progress_on_main_thread(self, title, steps, current_step_index, progress, done):
        """Slot that handles build progress updates on the main thread"""
        self.update_build_progress(title, steps, current_step_index, progress, done)

    def update_build_progress(self, title, steps, current_step_index, progress, done):
        """Update build progress in GUI"""
        # Update progress bar
        if self.progress_bar:
            self.progress_bar.setValue(progress)
        
        # Update progress label
        if self.progress_label:
            if done:
                self.progress_label.setText(f"✓ {title} - Complete!")
            else:
                step_text = steps[current_step_index] if current_step_index < len(steps) else "Processing"
                self.progress_label.setText(f"⚙ {step_text}...")
        
        if done:
            self.log_message(f"\n✓ {title} - Complete!", to_build_log=True)
            for step in steps:
                self.log_message(f"  ✓ {step}", to_console=False, to_build_log=True)
        else:
            step_text = steps[current_step_index] if current_step_index < len(steps) else "Processing"
            self.log_message(f"\n> {step_text}...", to_build_log=True)

    def show_before_using_efi_dialog(self):
        """Show Before Using EFI dialog after successful build"""
        # Calculate BIOS requirements
        bios_requirements = self.ocpe.check_bios_requirements(
            self.hardware_report_data, self.customized_hardware)
        
        # Show the dialog
        result = show_before_using_efi_dialog(
            self, bios_requirements, self.ocpe.result_dir)
        
        if result:
            # User agreed - open the result folder if setting is enabled
            from Scripts.settings import Settings
            settings = Settings()
            if settings.get_open_folder_after_build():
                self.ocpe.u.open_folder(self.ocpe.result_dir)
            
            # Enable the open result button
            if self.open_result_btn:
                self.open_result_btn.setEnabled(True)
        
        # Re-enable the build button for next build
        if self.build_btn:
            self.build_btn.setEnabled(True)

    def run(self):
        """Run the application"""
        self.show()
