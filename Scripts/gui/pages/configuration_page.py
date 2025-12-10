from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ScrollArea, SubtitleLabel, BodyLabel, FluentIcon, 
    PushSettingCard, ExpandGroupSettingCard, SpinBox, 
    LineEdit, PushButton, SwitchButton, ComboBox, 
    IndicatorPosition, SettingCard
)

from ..custom_dialogs import show_macos_version_dialog
from ..styles import SPACING, COLORS
from ..ui_utils import add_group_with_indent, create_step_indicator
from ...settings import Settings


class PickerGroup(ExpandGroupSettingCard):
    def __init__(self, settings, parent=None):
        super().__init__(
            FluentIcon.MENU,
            "Boot Picker",
            "Configure OpenCore picker settings",
            parent
        )
        self.settings = settings
        
        self.showPickerSwitch = SwitchButton("Off", self, IndicatorPosition.RIGHT)
        self.showPickerSwitch.setOnText("On")
        self.showPickerSwitch.setChecked(self.settings.get("show_picker", True))
        self.showPickerSwitch.checkedChanged.connect(lambda c: self.settings.set("show_picker", c))
        
        self.pickerModeCombo = ComboBox()
        picker_mode_values = ["Builtin", "External"]
        self.pickerModeCombo.addItems(picker_mode_values)
        self.pickerModeCombo.setCurrentText(self.settings.get("picker_mode", "External"))
        self.pickerModeCombo.currentTextChanged.connect(lambda t: self.settings.set("picker_mode", t))
        self.pickerModeCombo.setFixedWidth(150)
        
        self.hideAuxSwitch = SwitchButton("Off", self, IndicatorPosition.RIGHT)
        self.hideAuxSwitch.setOnText("On")
        self.hideAuxSwitch.setChecked(self.settings.get("hide_auxiliary", False))
        self.hideAuxSwitch.checkedChanged.connect(lambda c: self.settings.set("hide_auxiliary", c))
        
        self.pickerVariantCombo = ComboBox()
        picker_variant_values = [
            "Auto",
            "Acidanthera/GoldenGate",
            "Acidanthera/Syrah",
            "Acidanthera/Chardonnay"
        ]
        self.pickerVariantCombo.addItems(picker_variant_values)
        self.pickerVariantCombo.setCurrentText(self.settings.get("picker_variant", "Auto"))
        self.pickerVariantCombo.currentTextChanged.connect(lambda t: self.settings.set("picker_variant", t))
        self.pickerVariantCombo.setFixedWidth(220)
        
        self.timeoutSpin = SpinBox()
        self.timeoutSpin.setRange(0, 60*10)
        self.timeoutSpin.setValue(self.settings.get("picker_timeout", 5))
        self.timeoutSpin.valueChanged.connect(lambda v: self.settings.set("picker_timeout", v))
        
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)
        
        self.addGroup(
            FluentIcon.MENU, 
            "Show Picker", 
            "Show the OpenCore Picker at startup, allowing you to choose between different boot entries.", 
            self.showPickerSwitch
        )
        self.addGroup(
            FluentIcon.APPLICATION, 
            "Picker Mode", 
            "Picker used for boot management: Builtin (text mode) or External (OpenCanopy GUI).", 
            self.pickerModeCombo
        )
        self.addGroup(
            FluentIcon.HIDE, 
            "Hide auxiliary entries", 
            "Hides auxiliary boot entries (Recovery, Reset NVRAM, Tools) from the boot picker for a cleaner interface.", 
            self.hideAuxSwitch
        )
        self.addGroup(
            FluentIcon.PALETTE, 
            "Picker Variant", 
            "Choose specific icon set to be used for boot management. Requires External Picker mode.", 
            self.pickerVariantCombo
        )
        self.addGroup(
            FluentIcon.HISTORY, 
            "Timeout", 
            "Timeout in seconds in the OpenCore picker before automatic booting of the default boot entry. Set to 0 to disable.", 
            self.timeoutSpin
        )


class SecurityConfigGroup(ExpandGroupSettingCard):
    def __init__(self, settings, parent=None):
        super().__init__(
            FluentIcon.DEVELOPER_TOOLS,
            "Security Configuration",
            "System Integrity Protection and Secure Boot Model",
            parent
        )
        self.settings = settings
        
        self.disableSipSwitch = SwitchButton("Off", self, IndicatorPosition.RIGHT)
        self.disableSipSwitch.setOnText("On")
        self.disableSipSwitch.setChecked(self.settings.get("disable_sip", True))
        self.disableSipSwitch.checkedChanged.connect(lambda c: self.settings.set("disable_sip", c))
        
        self.secureBootCombo = ComboBox()
        secure_boot_values = [
            "Default",
            "Disabled",
            "j137",
            "j680",
            "j132",
            "j174",
            "j140k",
            "j780",
            "j213",
            "j140a",
            "j152f",
            "j160",
            "j230k",
            "j214k",
            "j223",
            "j215",
            "j185",
            "j185f",
            "x86legacy"
        ]
        self.secureBootCombo.addItems(secure_boot_values)
        current_sb = self.settings.get("secure_boot_model", "Disabled")
        if current_sb not in secure_boot_values:
            current_sb = "Disabled"
        self.secureBootCombo.setCurrentText(current_sb)
        self.secureBootCombo.currentTextChanged.connect(lambda t: self.settings.set("secure_boot_model", t))
        self.secureBootCombo.setFixedWidth(150)
        
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)
        
        self.addGroup(
            FluentIcon.SETTING, 
            "Disable SIP", 
            "Allowing unrestricted modifications and installation of software, kexts, and kernel patches. Required for OpenCore Legacy Patcher and other tools.", 
            self.disableSipSwitch
        )
        self.addGroup(
            FluentIcon.CERTIFICATE, 
            "Secure Boot Model", 
            "Sets Apple Secure Boot hardware model for security level.", 
            self.secureBootCombo
        )


class BootArgsGroup(ExpandGroupSettingCard):
    def __init__(self, settings, parent=None):
        super().__init__(
            FluentIcon.COMMAND_PROMPT,
            "Boot Arguments",
            "Configure verbose mode and custom boot arguments",
            parent
        )
        self.settings = settings
        
        self.verboseSwitch = SwitchButton("Off", self, IndicatorPosition.RIGHT)
        self.verboseSwitch.setOnText("On")
        self.verboseSwitch.setChecked(self.settings.get("verbose_boot", True))
        self.verboseSwitch.checkedChanged.connect(lambda c: self.settings.set("verbose_boot", c))
        
        self.customArgsInput = LineEdit()
        self.customArgsInput.setPlaceholderText("e.g., -radcodec -raddvi")
        self.customArgsInput.setText(self.settings.get("custom_boot_args", ""))
        self.customArgsInput.textChanged.connect(lambda t: self.settings.set("custom_boot_args", t))
        self.customArgsInput.setClearButtonEnabled(True)
        self.customArgsInput.setFixedWidth(400)
        
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)
        
        self.addGroup(
            FluentIcon.CODE, 
            "Verbose boot", 
            "Enables verbose boot with \"-v debug=0x100 keepsyms=1\" arguments for detailed boot logging and troubleshooting.", 
            self.verboseSwitch
        )
        self.addGroup(
            FluentIcon.COMMAND_PROMPT, 
            "Additional Arguments", 
            "Add custom boot arguments (space-separated)", 
            self.customArgsInput
        )


class SMBIOSGroup(ExpandGroupSettingCard):
    def __init__(self, settings, controller, on_select_model, parent=None):
        super().__init__(
            FluentIcon.PEOPLE,
            "SMBIOS Configuration",
            "SMBIOS generation and preservation options",
            parent
        )
        self.settings = settings
        self.controller = controller
        
        self.modelLabel = BodyLabel(self.controller.smbios_state.model_name)
        self.modelLabel.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-right: 10px;")

        self.selectModelBtn = PushButton("Select Model")
        self.selectModelBtn.clicked.connect(on_select_model)
        self.selectModelBtn.setFixedWidth(150)
        
        model_widget = QWidget()
        model_layout = QHBoxLayout(model_widget)
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.addWidget(self.modelLabel)
        model_layout.addWidget(self.selectModelBtn)
        
        self.randomSwitch = SwitchButton("Off", self, IndicatorPosition.RIGHT)
        self.randomSwitch.setOnText("On")
        self.randomSwitch.setChecked(self.settings.get("random_smbios", True))
        self.randomSwitch.checkedChanged.connect(lambda c: self.settings.set("random_smbios", c))
        
        self.preserveSwitch = SwitchButton("Off", self, IndicatorPosition.RIGHT)
        self.preserveSwitch.setOnText("On")
        self.preserveSwitch.setChecked(self.settings.get("preserve_smbios", False))
        self.preserveSwitch.checkedChanged.connect(lambda c: self.settings.set("preserve_smbios", c))
        
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)
        
        self.addGroup(
            FluentIcon.TAG, 
            "SMBIOS Model", 
            "Choose the Mac model your system will identify as", 
            model_widget
        )
        self.addGroup(
            FluentIcon.SYNC, 
            "Generate random SMBIOS", 
            "Automatically generates new random serial numbers for each build to ensure unique system identifiers", 
            self.randomSwitch
        )
        self.addGroup(
            FluentIcon.SAVE, 
            "Preserve SMBIOS", 
            "Maintains the same SMBIOS values across multiple builds for consistency with iCloud and other services", 
            self.preserveSwitch
        )

    def update_model(self):
        self.modelLabel.setText(self.controller.smbios_state.model_name)


class macOSCard(SettingCard):
    def __init__(self, controller, on_select_version, parent=None):
        super().__init__(
            FluentIcon.GLOBE,
            "macOS Version",
            "Target operating system version",
            parent
        )
        self.controller = controller
        
        self.versionLabel = BodyLabel(self.controller.macos_state.macos_version_name)
        self.versionLabel.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-right: 10px;")
        
        self.selectVersionBtn = PushButton("Select Version")
        self.selectVersionBtn.clicked.connect(on_select_version)
        self.selectVersionBtn.setFixedWidth(150)
        
        self.hBoxLayout.addWidget(self.versionLabel)
        self.hBoxLayout.addWidget(self.selectVersionBtn)
        self.hBoxLayout.addSpacing(16)

    def update_version(self):
        self.versionLabel.setText(self.controller.macos_state.macos_version_name)


class ConfigurationPage(ScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.setObjectName("configurationPage")
        self.controller = parent
        self.settings = Settings()
        self.scrollWidget = QWidget()
        self.main_layout = QVBoxLayout(self.scrollWidget)
        
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.enableTransparentBackground()
        
        self.status_card = None
        
        self.page()

    def page(self):
        self.main_layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])
        self.main_layout.setSpacing(SPACING['large'])

        self.main_layout.addWidget(create_step_indicator(3))

        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Configuration")
        header_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Configure your OpenCore EFI settings")
        subtitle_label.setStyleSheet("color: #605E5C;")
        header_layout.addWidget(subtitle_label)

        self.main_layout.addWidget(header_container)
        self.main_layout.addSpacing(SPACING['large'])

        self.status_start_index = self.main_layout.count()
        self._update_status_card()

        self.macos_card = macOSCard(self.controller, self.select_macos_version, self.scrollWidget)
        self.main_layout.addWidget(self.macos_card)

        self.acpi_card = PushSettingCard(
            "Configure Patches",
            FluentIcon.DEVELOPER_TOOLS,
            "ACPI Patches",
            "Customize system ACPI table modifications for hardware compatibility",
            self.scrollWidget
        )
        self.acpi_card.clicked.connect(self.customize_acpi)
        self.main_layout.addWidget(self.acpi_card)

        self.kexts_card = PushSettingCard(
            "Manage Kexts",
            FluentIcon.CODE,
            "Kernel Extensions",
            "Configure kexts required for your hardware",
            self.scrollWidget
        )
        self.kexts_card.clicked.connect(self.customize_kexts)
        self.main_layout.addWidget(self.kexts_card)

        self.boot_picker_card = PickerGroup(self.settings, self.scrollWidget)
        self.main_layout.addWidget(self.boot_picker_card)

        self.security_config_card = SecurityConfigGroup(self.settings, self.scrollWidget)
        self.main_layout.addWidget(self.security_config_card)

        self.boot_args_card = BootArgsGroup(self.settings, self.scrollWidget)
        self.main_layout.addWidget(self.boot_args_card)

        self.smbios_card = SMBIOSGroup(self.settings, self.controller, self.customize_smbios, self.scrollWidget)
        self.main_layout.addWidget(self.smbios_card)
        self.main_layout.addStretch()

    def _update_status_card(self):
        if self.status_card is not None:
            self.main_layout.removeWidget(self.status_card)
            self.status_card.deleteLater()
            self.status_card = None

        disabled_devices = self.controller.hardware_state.disabled_devices or {}
        
        status_text = ""
        status_color = COLORS['text_secondary']
        icon = FluentIcon.INFO
        
        if disabled_devices:
            status_text = "Hardware components excluded from configuration"
            status_color = COLORS['text_secondary']
            icon = FluentIcon.WARNING
        elif not self.controller.hardware_state.hardware_report:
            status_text = "Please select hardware report first"
        elif not self.controller.macos_state.darwin_version:
            status_text = "Please select target macOS version first"
        else:
            status_text = "All hardware components are compatible and enabled"
            status_color = COLORS['success']
            icon = FluentIcon.ACCEPT

        self.status_card = ExpandGroupSettingCard(
            icon,
            "Compatibility Status",
            "",
            self.scrollWidget
        )
        
        status_label = BodyLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color};")
        
        self.status_card.setContent(status_text)
        
        if hasattr(self.status_card, 'contentLabel'):
            self.status_card.contentLabel.setStyleSheet(f"color: {status_color};")
            
        if disabled_devices:
            for device_name in disabled_devices.keys():
                self.status_card.addGroup(
                    FluentIcon.CLOSE,
                    device_name,
                    "Incompatible or disabled",
                    None
                )
        else:
             pass

        self.main_layout.insertWidget(self.status_start_index, self.status_card)

    def select_macos_version(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please select hardware report first", 'warning')
            return

        if self.controller.hardware_state.compatibility_error:
            self.controller.update_status("Incompatible hardware detected, please select different hardware report and try again", 'warning')
            return

        suggested_version = self.controller.suggest_macos_version()

        selected_version, ok = show_macos_version_dialog(
            self.controller,
            self.controller.macos_state.native_version,
            self.controller.macos_state.ocl_patched_version,
            suggested_version,
            self.controller.ocpe.u
        )

        if ok and selected_version:
            self.controller.apply_macos_version(selected_version)
            self.controller.update_status("macOS version updated to {}".format(self.controller.macos_state.macos_version_name), 'success')
            if hasattr(self, 'macos_card'):
                self.macos_card.update_version()

    def customize_acpi(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please select hardware report first", 'warning')
            return

        if not self.controller.macos_state.darwin_version:
            self.controller.update_status("Please select target macOS version first", 'warning')
            return

        from ..custom_dialogs import show_acpi_patches_dialog

        ok = show_acpi_patches_dialog(
            self.controller,
            self.controller.ocpe.ac
        )

        if ok:
            self.controller.update_status(
                "ACPI patches configuration updated successfully", 'success')

    def customize_kexts(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please select hardware report first", 'warning')
            return

        if not self.controller.macos_state.darwin_version:
            self.controller.update_status("Please select target macOS version first", 'warning')
            return

        from ..custom_dialogs import show_kexts_dialog

        ok = show_kexts_dialog(
            self.controller,
            self.controller.ocpe.k,
            self.controller.macos_state.darwin_version
        )

        if ok:
            self.controller.update_status(
                "Kext configuration updated successfully", 'success')

    def customize_smbios(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please select hardware report first", 'warning')
            return

        if not self.controller.macos_state.darwin_version:
            self.controller.update_status("Please select target macOS version first", 'warning')
            return

        from ...datasets.mac_model_data import mac_devices
        from ..custom_dialogs import show_smbios_dialog

        current_model = self.controller.smbios_state.model_name
        default_model = self.controller.ocpe.s.select_smbios_model(
            self.controller.hardware_state.customized_hardware,
            self.controller.macos_state.darwin_version
        )
        is_laptop = "Laptop" == self.controller.hardware_state.customized_hardware.get("Motherboard").get("Platform")

        selected_model, ok = show_smbios_dialog(
            self.controller,
            mac_devices,
            current_model,
            default_model,
            self.controller.macos_state.darwin_version,
            is_laptop,
            self.controller.ocpe.u
        )

        if ok and selected_model != current_model:
            self.controller.smbios_state.model_name = selected_model

            self.controller.ocpe.s.smbios_specific_options(
                self.controller.hardware_state.customized_hardware,
                selected_model,
                self.controller.macos_state.darwin_version,
                self.controller.ocpe.ac.patches,
                self.controller.ocpe.k
            )

            self.smbios_card.update_model()
            self.controller.update_status("SMBIOS model updated to {}".format(selected_model), 'success')

    def update_display(self):
        self._update_status_card()
        if hasattr(self, 'macos_card'):
            self.macos_card.update_version()
        if hasattr(self, 'smbios_card'):
            self.smbios_card.update_model()

    def refresh(self):
        self.update_display()