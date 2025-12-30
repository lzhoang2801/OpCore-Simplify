import os
import sys
import platform
import traceback

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon, InfoBar, InfoBarPosition

from Scripts.datasets import os_data
from Scripts.state import HardwareReportState, macOSVersionState, SMBIOSState, BuildState
from Scripts.pages import HomePage, SelectHardwareReportPage, CompatibilityPage, ConfigurationPage, BuildPage, SettingsPage
from Scripts.backend import Backend
from Scripts import ui_utils
from Scripts.custom_dialogs import set_default_gui_handler
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
        self.macos_state = macOSVersionState()
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
        self.backend.update_status_signal.connect(self.update_status)
        
        self.open_result_folder_signal.connect(self._handle_open_result_folder)

    def _setup_backend_handlers(self):
        self.backend.u.gui_handler = self
        set_default_gui_handler(self)

    def init_navigation(self):
        self.homePage = HomePage(self, ui_utils_instance=self.ui_utils)
        self.SelectHardwareReportPage = SelectHardwareReportPage(self, ui_utils_instance=self.ui_utils)
        self.compatibilityPage = CompatibilityPage(self, ui_utils_instance=self.ui_utils)
        self.configurationPage = ConfigurationPage(self, ui_utils_instance=self.ui_utils)
        self.buildPage = BuildPage(self, ui_utils_instance=self.ui_utils)
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
            "1. Select Hardware Report",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.compatibilityPage,
            FluentIcon.CHECKBOX,
            "2. Check Compatibility",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.configurationPage,
            FluentIcon.EDIT,
            "3. Configure OpenCore EFI",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.buildPage,
            FluentIcon.DEVELOPER_TOOLS,
            "4. Build & Review",
            NavigationItemPosition.TOP
        )

        self.navigationInterface.addSeparator()
        self.addSubInterface(
            self.settingsPage,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM
        )

    def _handle_open_result_folder(self, folder_path):
        self.backend.u.open_folder(folder_path)

    def update_status(self, message, status_type="INFO"):
        if status_type == "success":
            InfoBar.success(
                title="Success",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
        elif status_type == "ERROR":
            InfoBar.error(
                title="ERROR",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
        elif status_type == "WARNING":
            InfoBar.warning(
                title="WARNING",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=4000,
                parent=self
            )
        else:
            InfoBar.info(
                title="INFO",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    def validate_prerequisites(self, require_hardware_report=True, require_dsdt=True, require_darwin_version=True, check_compatibility_error=True, require_customized_hardware=True, show_status=True):
        if require_hardware_report:
            if not self.hardware_state.hardware_report:
                if show_status:
                    self.update_status("Please select hardware report first", "WARNING")
                return False
            
        if require_dsdt:
            if not self.backend.ac._ensure_dsdt():
                if show_status:
                    self.update_status("Please load ACPI tables first", "WARNING")
                return False
        
        if check_compatibility_error:
            if self.hardware_state.compatibility_error:
                if show_status:
                    self.update_status("Incompatible hardware detected, please select different hardware report and try again", "WARNING")
                return False
        
        if require_darwin_version:
            if not self.macos_state.darwin_version:
                if show_status:
                    self.update_status("Please select target macOS version first", "WARNING")
                return False

        if require_customized_hardware:
            if not self.hardware_state.customized_hardware:
                if show_status:
                    self.update_status("Please reload hardware report and select target macOS version to continue", "WARNING")
                return False
        
        return True

    def apply_macos_version(self, version):
        self.macos_state.darwin_version = version
        self.macos_state.selected_version_name = os_data.get_macos_name_by_darwin(version)

        self.hardware_state.customized_hardware, self.hardware_state.disabled_devices, self.macos_state.needs_oclp = self.backend.h.hardware_customization(self.hardware_state.hardware_report, version)

        self.smbios_state.model_name = self.backend.s.select_smbios_model(self.hardware_state.customized_hardware, version)
        
        self.backend.ac.select_acpi_patches(self.hardware_state.customized_hardware, self.hardware_state.disabled_devices)
        
        self.macos_state.needs_oclp, audio_layout_id, audio_controller_properties = self.backend.k.select_required_kexts(self.hardware_state.customized_hardware, version, self.macos_state.needs_oclp, self.backend.ac.patches)
        
        if audio_layout_id is not None:
            self.hardware_state.audio_layout_id = audio_layout_id
            self.hardware_state.audio_controller_properties = audio_controller_properties

        self.backend.s.smbios_specific_options(self.hardware_state.customized_hardware, self.smbios_state.model_name, version, self.backend.ac.patches, self.backend.k)

        self.configurationPage.update_display()

    def setup_exception_hook(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            error_message = "Uncaught exception detected:\n{}".format(error_details)
            
            self.backend.u.log_message(error_message, level="ERROR")
            
            try:
                sys.__stderr__.write("\n[CRITICAL ERROR] {}\n".format(error_message))
            except:
                pass

        sys.excepthook = handle_exception


if __name__ == "__main__":
    backend = Backend()
    
    app = QApplication(sys.argv)
    set_default_gui_handler(app)
    
    window = OCS(backend)
    window.setup_exception_hook()
    window.show()
    
    if backend.settings.get_auto_update_check():
        updater.Updater(
            utils_instance=backend.u,
            github_instance=backend.github,
            resource_fetcher_instance=backend.resource_fetcher,
            run_instance=backend.r,
            integrity_checker_instance=backend.integrity_checker
        ).run_update()
    
    sys.exit(app.exec())