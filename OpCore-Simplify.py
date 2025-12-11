import os
import sys
import platform
import traceback

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon, InfoBar, InfoBarPosition

from Scripts.datasets import os_data
from Scripts.state import HardwareReportState, MacOSVersionState, SMBIOSState, BuildState
from Scripts.pages import HomePage, SelectHardwareReportPage, CompatibilityPage, ConfigurationPage, BuildPage, SettingsPage
from Scripts.styles import COLORS
from Scripts.backend import Backend
from Scripts import ui_utils
import updater

WINDOW_MIN_SIZE = (1000, 700)
WINDOW_DEFAULT_SIZE = (1200, 800)


class OCS(FluentWindow):
    open_result_folder_signal = pyqtSignal(str)
    
    PLATFORM_FONTS = {
        "Windows": "Segoe UI",
        "Darwin": "SF Pro Display",
        "Linux": "Ubuntu"
    }

    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.settings = self.backend.settings
        self.ui_utils = ui_utils.UIUtils()
        
        self._init_state()
        self._setup_window()
        self._connect_signals()
        self._setup_backend_handlers()
        self.init_navigation()

    def _init_state(self):
        self.hardware_state = HardwareReportState()
        self.macos_state = MacOSVersionState()
        self.smbios_state = SMBIOSState()
        self.build_state = BuildState()
        
        self.build_btn = None
        self.progress_bar = None
        self.progress_label = None
        self.build_log = None
        self.open_result_btn = None

    def _setup_window(self):
        self.setWindowTitle("OpCore Simplify")
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        
        self._restore_window_geometry()

        font = QFont()
        system = platform.system()
        font_family = self.PLATFORM_FONTS.get(system, "Ubuntu")
        font.setFamily(font_family)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(font)
    
    def _restore_window_geometry(self):
        saved_geometry = self.settings.get("window_geometry")
        
        if saved_geometry and isinstance(saved_geometry, dict):
            x = saved_geometry.get("x")
            y = saved_geometry.get("y")
            width = saved_geometry.get("width", WINDOW_DEFAULT_SIZE[0])
            height = saved_geometry.get("height", WINDOW_DEFAULT_SIZE[1])
            
            if x is not None and y is not None:
                screen = QApplication.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    if (screen_geometry.left() <= x <= screen_geometry.right() and
                        screen_geometry.top() <= y <= screen_geometry.bottom()):
                        self.setGeometry(x, y, width, height)
                        return
        
        self._center_window()
    
    def _center_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_width = WINDOW_DEFAULT_SIZE[0]
            window_height = WINDOW_DEFAULT_SIZE[1]
            
            x = screen_geometry.left() + (screen_geometry.width() - window_width) // 2
            y = screen_geometry.top() + (screen_geometry.height() - window_height) // 2
            
            self.setGeometry(x, y, window_width, window_height)
        else:
            self.resize(*WINDOW_DEFAULT_SIZE)
    
    def _save_window_geometry(self):
        geometry = self.geometry()
        window_geometry = {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        }
        self.settings.set("window_geometry", window_geometry)
    
    def closeEvent(self, event):
        self._save_window_geometry()
        super().closeEvent(event)

    def _connect_signals(self):
        self.backend.log_message_signal.connect(
            lambda message, level, to_build_log: (
                [
                    self.build_log.append(line)
                    for line in (message.splitlines() or [""])
                ]
                if to_build_log and getattr(self, "build_log", None) else None
            )
        )
        self.backend.build_progress_signal.connect(self.update_build_progress)
        self.backend.update_status_signal.connect(self.update_status)
        self.backend.build_complete_signal.connect(self._handle_build_complete)
        
        self.open_result_folder_signal.connect(self._handle_open_result_folder)

    def _setup_backend_handlers(self):
        self.backend.u.gui_handler = self

    def init_navigation(self):
        self.homePage = HomePage(self)
        self.SelectHardwareReportPage = SelectHardwareReportPage(self)
        self.compatibilityPage = CompatibilityPage(self)
        self.configurationPage = ConfigurationPage(self)
        self.buildPage = BuildPage(self)
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
            self.settingsPage,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM
        )

    def _handle_build_complete(self, success, bios_requirements):
        if hasattr(self, 'buildPage') and hasattr(self.buildPage, 'on_build_complete'):
            self.buildPage.on_build_complete(success, bios_requirements)
            
        if success:
            if self.settings.get_open_folder_after_build():
                self.open_result_folder_signal.emit(self.backend.result_dir)

    def _handle_open_result_folder(self, folder_path):
        self.backend.u.open_folder(folder_path)

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

    def suggest_macos_version(self):
        if not self.hardware_state.hardware_report or not self.macos_state.native_version:
            return None

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

                        if self.backend.u.parse_darwin_version(suggested_macos_version) > self.backend.u.parse_darwin_version(device_props.get("Compatibility")[0]):
                            suggested_macos_version = device_props.get("Compatibility")[0]

        while True:
            if "Beta" in os_data.get_macos_name_by_darwin(suggested_macos_version):
                suggested_macos_version = "{}{}".format(
                    int(suggested_macos_version[:2]) - 1, suggested_macos_version[2:])
            else:
                break

        return suggested_macos_version

    def apply_macos_version(self, version, defer_kext_selection=False):
        self.backend.u.log_gui(f"Applying macOS version: {version} ({os_data.get_macos_name_by_darwin(version)})", level="Info", to_build_log=False)
        self.macos_state.darwin_version = version
        self.macos_state.macos_version_name = os_data.get_macos_name_by_darwin(version)

        self.hardware_state.customized_hardware, self.hardware_state.disabled_devices, self.macos_state.needs_oclp = \
            self.backend.h.hardware_customization(self.hardware_state.hardware_report, version)
        
        self.backend.u.log_gui(f"Hardware customization complete. Disabled {len(self.hardware_state.disabled_devices)} incompatible devices.", level="Info", to_build_log=False)

        self.smbios_state.model_name = self.backend.s.select_smbios_model(
            self.hardware_state.customized_hardware, version)
        
        self.backend.u.log_gui(f"Selected SMBIOS model: {self.smbios_state.model_name}", level="Info", to_build_log=False)

        self.backend.ac.select_acpi_patches(
            self.hardware_state.customized_hardware, self.hardware_state.disabled_devices)
        
        if not defer_kext_selection:
            self.macos_state.needs_oclp = self.backend.k.select_required_kexts(
                self.hardware_state.customized_hardware, version, self.macos_state.needs_oclp, self.backend.ac.patches
            )
            self.backend.u.log_gui(f"Kext selection complete. OCLP required: {self.macos_state.needs_oclp}", level="Info", to_build_log=False)

        self.backend.s.smbios_specific_options(
            self.hardware_state.customized_hardware, self.smbios_state.model_name, version,
            self.backend.ac.patches, self.backend.k
        )

        self.configurationPage.update_display()

    def build_efi(self):
        if not self.hardware_state.customized_hardware:
            self.update_status("Please load hardware report first", 'warning')
            return

        self.backend.start_build_process(
            self.hardware_state.customized_hardware,
            self.hardware_state.disabled_devices,
            self.smbios_state.model_name,
            self.macos_state.darwin_version,
            self.macos_state.needs_oclp
        )

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
                step_text = steps[current_step_index] if current_step_index < len(steps) else "Processing"
                step_counter = f"Step {current_step_index + 1}/{len(steps)}"
                self.progress_label.setText(f"⚙ {step_counter}: {step_text}...")
                
        if done:
            self.backend.u.log_gui(f"[BUILD] {title} complete!", 'success', to_build_log=True)
        else:
            step_text = steps[current_step_index] if current_step_index < len(steps) else "Processing"
            self.backend.u.log_gui(f"[BUILD] Step {current_step_index + 1}/{len(steps)}: {step_text}...", 'info', to_build_log=True)

    def run(self):
        self.show()

    def setup_exception_hook(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            error_message = f"Uncaught exception detected:\n{error_details}"
            
            self.backend.u.log_gui(error_message, level="Error")
            
            try:
                sys.__stderr__.write(f"\n[CRITICAL ERROR] {error_message}\n")
            except:
                pass

        sys.excepthook = handle_exception


if __name__ == '__main__':
    backend = Backend()

    if backend.settings.get_auto_update_check():
        update_flag = updater.Updater(
            utils_instance=backend.u,
            github_instance=backend.github,
            resource_fetcher_instance=backend.resource_fetcher,
            run_instance=backend.r
        ).run_update()
        if update_flag:
            os.execv(sys.executable, ['python3'] + sys.argv)
            
    app = QApplication(sys.argv)
    
    window = OCS(backend)
    window.setup_exception_hook()
    window.show()
    
    sys.exit(app.exec())
