import os
import platform
import sys
import threading
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon, setTheme, Theme, InfoBar, InfoBarPosition

from ..datasets import os_data
from .state import HardwareReportState, MacOSVersionState, SMBIOSState, BuildState
from .pages import (
    HomePage, SelectHardwareReportPage, CompatibilityPage, ConfigurationPage, 
    BuildPage, SettingsPage, ConfigEditorPage
)
from .custom_dialogs import (
    show_input_dialog, show_choice_dialog, show_question_dialog, show_info_dialog)
from .styles import COLORS
from .ui_utils import ConsoleRedirector
from Scripts.settings import Settings

scripts_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

WINDOW_MIN_SIZE = (1000, 700)
WINDOW_DEFAULT_SIZE = (1200, 800)


class OpCoreGUI(FluentWindow):
    gui_prompt_signal = pyqtSignal(str, str, object, object)
    update_status_signal = pyqtSignal(str, str)
    update_build_progress_signal = pyqtSignal(str, list, int, int, bool)
    update_gathering_progress_signal = pyqtSignal(dict)
    log_message_signal = pyqtSignal(str, str, bool)
    build_complete_signal = pyqtSignal(bool, object)
    open_result_folder_signal = pyqtSignal(str)
    
    PLATFORM_FONTS = {
        "Windows": "Segoe UI",
        "Darwin": "SF Pro Display",
        "Linux": "Ubuntu"
    }

    def __init__(self, ocpe_instance):
        super().__init__()
        self.ocpe = ocpe_instance
        self.settings = Settings()
        self.log_file_path = None
        self._setup_logging()

        self._init_state()
        self._setup_window()
        #self._apply_theme()
        self._connect_signals()
        self._setup_backend_handlers()
        self.init_navigation()

    def _setup_logging(self):
        if self.settings.get_enable_debug_logging():
            try:
                root_dir = os.path.dirname(scripts_path)
                log_dir = os.path.join(root_dir, "Logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now()
                self.log_file_path = os.path.join(log_dir, "ocs-{}.txt".format(timestamp.strftime("%Y-%m-%d-%H%M%S")))
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write("[{}] OpCore Simplify started\n".format(timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            except Exception as e:
                print("Failed to setup logging: {}".format(e))

    def _init_state(self):
        self.hardware_state = HardwareReportState()
        self.macos_state = MacOSVersionState()
        self.smbios_state = SMBIOSState()
        self.build_state = BuildState()
        
        self.build_btn = None
        self.progress_var = None
        self.progress_bar = None
        self.progress_label = None
        self.build_log = None
        self.open_result_btn = None
        self.stdout_redirector = None
        self.stderr_redirector = None

        self.console_redirected = False

    def _setup_window(self):
        self.setWindowTitle("OpCore Simplify")
        self.resize(*WINDOW_DEFAULT_SIZE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)

        font = QFont()
        system = platform.system()
        font_family = self.PLATFORM_FONTS.get(system, "Ubuntu")
        font.setFamily(font_family)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(font)

    def _apply_theme(self):
        theme_setting = self.settings.get_theme()
        theme = Theme.DARK if theme_setting == "Dark" else Theme.LIGHT
        setTheme(theme)

    def _connect_signals(self):
        self.gui_prompt_signal.connect(self._handle_gui_prompt_on_main_thread)
        self.update_status_signal.connect(self.update_status)
        self.update_build_progress_signal.connect(self._update_build_progress_on_main_thread)
        self.update_gathering_progress_signal.connect(self._update_gathering_progress_on_main_thread)
        self.log_message_signal.connect(self._log_message_on_main_thread)
        self.build_complete_signal.connect(self._handle_build_complete)
        self.open_result_folder_signal.connect(self._handle_open_result_folder)

    def _setup_backend_handlers(self):
        utils_instances = [
            self.ocpe.u,
            self.ocpe.h.utils,
            self.ocpe.k.utils,
            self.ocpe.c.utils,
            self.ocpe.co.utils,
            self.ocpe.o.utils,
            self.ocpe.ac.utils,
            self.ocpe.s.utils,
            self.ocpe.v.u,
        ]
        
        for utils in utils_instances:
            utils.gui_handler = self
            utils.gui_callback = self.handle_gui_prompt_threadsafe

        self.ocpe.u.gui_progress_callback = self.update_build_progress_threadsafe
        self.ocpe.u.gui_gathering_progress_callback = self.update_gathering_progress_threadsafe
        self.ocpe.o.utils.gui_gathering_progress_callback = self.update_gathering_progress_threadsafe

        for utils in utils_instances:
            if hasattr(utils, "gui_log_callback"):
                utils.gui_log_callback = self._dispatch_backend_log

    def init_navigation(self):
        self.homePage = HomePage(self)
        self.SelectHardwareReportPage = SelectHardwareReportPage(self)
        self.compatibilityPage = CompatibilityPage(self)
        self.configurationPage = ConfigurationPage(self)
        self.buildPage = BuildPage(self)
        self.configEditorPage = ConfigEditorPage(self)
        self.settingsPage = SettingsPage(self)

        self.addSubInterface(
            self.homePage,
            FluentIcon.HOME,
            "Home",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.SelectHardwareReportPage,
            FluentIcon.FOLDER_ADD,
            "1. Upload Report",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.compatibilityPage,
            FluentIcon.CHECKBOX,
            "2. Compatibility",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.configurationPage,
            FluentIcon.EDIT,
            "3. Configuration",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.buildPage,
            FluentIcon.DEVELOPER_TOOLS,
            "4. Build EFI",
            NavigationItemPosition.TOP
        )

        self.navigationInterface.addSeparator()
        self.addSubInterface(
            self.configEditorPage,
            FluentIcon.DOCUMENT,
            "Config Editor",
            NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingsPage,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM
        )

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

    def log_message(self, message, level="Info", *, to_build_log=True):
        if threading.current_thread() != threading.main_thread():
            self.log_message_signal.emit(message, level, to_build_log)
            return
            
        self._log_message_on_main_thread(message, level, to_build_log)

    def _log_message_on_main_thread(self, message, level, to_build_log):
        lines = message.splitlines()
        if not lines:
            lines = [""]

        if self.log_file_path:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    for line in lines:
                        f.write("[{}] [{}] {}\n".format(timestamp, level, line))
            except Exception:
                pass

        if to_build_log and self.build_log:
            for line in lines:
                self.build_log.append(line)

    def _handle_build_complete(self, success, bios_requirements):
        if hasattr(self, 'buildPage') and hasattr(self.buildPage, 'on_build_complete'):
            self.buildPage.on_build_complete(success, bios_requirements)

    def _handle_open_result_folder(self, folder_path):
        self.ocpe.u.open_folder(folder_path)

    def _dispatch_backend_log(self, message, level="Info", to_build_log=False):
        self.log_message(message, level, to_build_log=to_build_log)

    def update_status(self, message, status_type='info'):
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
        else:
            InfoBar.info(
                title='Info',
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    def handle_gui_prompt(self, prompt_type, prompt_text, options=None):
        self.log_message(f"User interaction required ({prompt_type}): {prompt_text}", level="Debug", to_build_log=False)
        if prompt_type == 'input':
            text, ok = show_input_dialog(self, "Input Required", prompt_text)
            if ok:
                return text
            return ""

        elif prompt_type == 'choice':
            if options:
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

            return "yes" if result else "no"

        elif prompt_type == 'info':
            if options:
                title = options.get('title', 'Information')
                message = options.get('message', prompt_text)
            else:
                title = 'Information'
                message = prompt_text

            return show_info_dialog(self, title, message)

        return None

    def handle_gui_prompt_threadsafe(self, prompt_type, prompt_text, options=None):
        if threading.current_thread() == threading.main_thread():
            return self.handle_gui_prompt(prompt_type, prompt_text, options)

        result_holder = {'result': None}
        event = threading.Event()

        self.gui_prompt_signal.emit(
            prompt_type, prompt_text, options, (result_holder, event))

        event.wait(timeout=None)

        return result_holder['result']

    def _handle_gui_prompt_on_main_thread(self, prompt_type, prompt_text, options, holder_tuple):
        result_holder, event = holder_tuple
        try:
            result = self.handle_gui_prompt(prompt_type, prompt_text, options)
            result_holder['result'] = result
        except Exception as e:
            print(f"Error in GUI prompt handler: {e}")
            result_holder['result'] = None
        finally:
            event.set()

    def suggest_macos_version(self):
        if not self.hardware_state.hardware_report or not self.macos_state.native_version:
            return None

        self.log_message("Analyzing hardware for suggested macOS version...", level="Info", to_build_log=False)

        hardware_report = self.hardware_state.hardware_report
        native_macos_version = self.macos_state.native_version

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

                        if self.ocpe.u.parse_darwin_version(suggested_macos_version) > self.ocpe.u.parse_darwin_version(device_props.get("Compatibility")[0]):
                            suggested_macos_version = device_props.get("Compatibility")[0]

        while True:
            if "Beta" in os_data.get_macos_name_by_darwin(suggested_macos_version):
                suggested_macos_version = "{}{}".format(
                    int(suggested_macos_version[:2]) - 1, suggested_macos_version[2:])
            else:
                break

        self.log_message(f"Suggested macOS version: {suggested_macos_version}", level="Info", to_build_log=False)
        return suggested_macos_version

    def apply_macos_version(self, version, defer_kext_selection=False):
        self.log_message(f"Applying macOS version: {version} ({os_data.get_macos_name_by_darwin(version)})", level="Info", to_build_log=False)
        self.macos_state.darwin_version = version
        self.macos_state.macos_version_name = os_data.get_macos_name_by_darwin(version)

        self.hardware_state.customized_hardware, self.hardware_state.disabled_devices, self.macos_state.needs_oclp = \
            self.ocpe.h.hardware_customization(self.hardware_state.hardware_report, version)
        
        self.log_message(f"Hardware customization complete. Disabled {len(self.hardware_state.disabled_devices)} incompatible devices.", level="Info", to_build_log=False)

        self.smbios_state.model_name = self.ocpe.s.select_smbios_model(
            self.hardware_state.customized_hardware, version)
        
        self.log_message(f"Selected SMBIOS model: {self.smbios_state.model_name}", level="Info", to_build_log=False)

        self.ocpe.ac.select_acpi_patches(
            self.hardware_state.customized_hardware, self.hardware_state.disabled_devices)
        
        self.log_message(f"Selected {len(self.ocpe.ac.patches)} ACPI patches.", level="Info", to_build_log=False)

        if not defer_kext_selection:
            self.macos_state.needs_oclp = self.ocpe.k.select_required_kexts(
                self.hardware_state.customized_hardware, version, self.macos_state.needs_oclp, self.ocpe.ac.patches
            )
            self.log_message(f"Kext selection complete. OCLP required: {self.macos_state.needs_oclp}", level="Info", to_build_log=False)

        self.ocpe.s.smbios_specific_options(
            self.hardware_state.customized_hardware, self.smbios_state.model_name, version,
            self.ocpe.ac.patches, self.ocpe.k
        )

        self.configurationPage.update_display()

    def build_efi(self):
        if not self.hardware_state.customized_hardware:
            self.update_status(
                "Please load a hardware report first", 'warning')
            return

        def build_thread():
            try:
                self.log_message(f"Starting EFI build process for Model: {self.smbios_state.model_name}, macOS: {self.macos_state.darwin_version}", level="Info", to_build_log=True)

                self.update_status_signal.emit(
                    "Phase 1/2: Gathering required files...", 'info')
                self.log_message("\nPhase 1: Gathering Files", to_build_log=True)
                self.log_message("-" * 60, to_build_log=True)
                
                self.ocpe.o.gather_bootloader_kexts(
                    self.ocpe.k.kexts, self.macos_state.darwin_version)

                self.update_status_signal.emit(
                    "Phase 2/2: Building OpenCore EFI structure...", 'info')
                self.log_message("\nPhase 2: Building EFI", to_build_log=True)
                self.log_message("-" * 60, to_build_log=True)
                
                self.ocpe.build_opencore_efi(
                    self.hardware_state.customized_hardware,
                    self.hardware_state.disabled_devices,
                    self.smbios_state.model_name,
                    self.macos_state.darwin_version,
                    self.macos_state.needs_oclp
                )

                self.update_status_signal.emit(
                    "✓ Build completed successfully!", 'success')
                
                self.log_message("\nBuild process finished successfully.", level="Info", to_build_log=True)

                bios_requirements = self.ocpe.check_bios_requirements(
                    self.hardware_state.data, self.hardware_state.customized_hardware)

                self.build_complete_signal.emit(True, bios_requirements)

                from Scripts.settings import Settings
                settings = Settings()
                if settings.get_open_folder_after_build():
                    self.open_result_folder_signal.emit(self.ocpe.result_dir)

            except Exception as e:
                self.update_status_signal.emit(
                    f"Build failed: {str(e)}", 'error')
                import traceback
                error_trace = traceback.format_exc()
                print(error_trace)
                
                self.log_message("\n" + "="*60, to_build_log=True)
                self.log_message("❌ Build Failed", to_build_log=True)
                self.log_message("="*60, to_build_log=True)
                self.log_message(f"\nError: {str(e)}", to_build_log=True)
                self.log_message("\nDetails:", to_build_log=True)
                self.log_message(error_trace, to_build_log=True)
                
                self.build_complete_signal.emit(False, None)

        thread = threading.Thread(target=build_thread, daemon=True)
        thread.start()

    def update_gathering_progress_threadsafe(self, progress_info):
        if threading.current_thread() == threading.main_thread():
            self.update_gathering_progress(progress_info)
        else:
            self.update_gathering_progress_signal.emit(progress_info)

    def _update_gathering_progress_on_main_thread(self, progress_info):
        self.update_gathering_progress(progress_info)

    def update_gathering_progress(self, progress_info):
        current = progress_info.get('current', 0)
        total = progress_info.get('total', 1)
        product_name = progress_info.get('product_name', '')
        status = progress_info.get('status', 'downloading')

        if self.progress_bar:
            if status == 'complete':
                self.progress_bar.setValue(40)
            else:
                progress_percent = int((current / total) * 40) if total > 0 else 0
                self.progress_bar.setValue(progress_percent)

        if self.progress_label:
            if status == 'complete':
                self.progress_label.setText(
                    "✓ All files gathered successfully! Starting build...")
                self.progress_label.setStyleSheet(f"color: {COLORS['success']};") if hasattr(self, 'COLORS') else None
            elif status == 'downloading':
                self.progress_label.setText(
                    f"⬇ Downloading ({current}/{total}): {product_name}")
            elif status == 'processing':
                self.progress_label.setText(
                    f"✓ Processing ({current}/{total}): {product_name}")

        if status == 'complete':
            self.log_message("\n" + "="*60, to_build_log=True)
            self.log_message("✓ File Gathering Phase Complete!", to_build_log=True)
            self.log_message("="*60, to_build_log=True)
            self.log_message(f"  Total files processed: {total}\n", to_build_log=True)
        elif status == 'downloading':
            self.log_message(
                f"  [{current}/{total}] ⬇ Downloading: {product_name}", 
                to_build_log=True)
        elif status == 'processing':
            self.log_message(
                f"  [{current}/{total}] ✓ Extracted: {product_name}", 
                to_build_log=True)

    def update_build_progress_threadsafe(self, title, steps, current_step_index, progress, done):
        if threading.current_thread() == threading.main_thread():
            self.update_build_progress(
                title, steps, current_step_index, progress, done)
        else:
            self.update_build_progress_signal.emit(
                title, steps, current_step_index, progress, done)

    def _update_build_progress_on_main_thread(self, title, steps, current_step_index, progress, done):
        self.update_build_progress(
            title, steps, current_step_index, progress, done)

    def update_build_progress(self, title, steps, current_step_index, progress, done):
        if self.progress_bar:
            if "Building" in title:
                adjusted_progress = 40 + int(progress * 0.6)
                self.progress_bar.setValue(adjusted_progress)
            else:
                self.progress_bar.setValue(progress)

        if self.progress_label:
            if done:
                self.progress_label.setText(f"✓ {title} complete!")
                self.progress_label.setStyleSheet(f"color: {COLORS['success']};") if hasattr(self, 'COLORS') else None
            else:
                step_text = steps[current_step_index] if current_step_index < len(
                    steps) else "Processing"
                step_counter = f"Step {current_step_index + 1}/{len(steps)}"
                self.progress_label.setText(f"⚙ {step_counter}: {step_text}...")
                
        if done:
            self.log_message("\n" + "="*60, to_build_log=True)
            self.log_message(f"✓ {title} Complete!", to_build_log=True)
            self.log_message("="*60 + "\n", to_build_log=True)
            for idx, step in enumerate(steps, 1):
                self.log_message(
                    f"  {idx}. ✓ {step}", to_build_log=True)
            self.log_message("", to_build_log=True)
        else:
            step_text = steps[current_step_index] if current_step_index < len(
                steps) else "Processing"
            self.log_message(
                f"\n[Step {current_step_index + 1}/{len(steps)}] {step_text}...", 
                to_build_log=True)

    def run(self):
        self.show()
