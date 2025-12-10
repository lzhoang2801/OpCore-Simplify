from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ScrollArea, SubtitleLabel, BodyLabel, FluentIcon, 
    GroupHeaderCardWidget, SettingCardGroup, PushSettingCard, 
    ExpandGroupSettingCard, SpinBox, LineEdit, PushButton, 
    SwitchButton, ComboBox, IndicatorPosition
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

        self.config_card = None
        self.cards_start_index = self.main_layout.count()
        self._build_config_card()

        self.custom_card = SettingCardGroup("Customization Options", self.scrollWidget)
        
        self.macos_card = PushSettingCard(
            "Select Version",
            FluentIcon.GLOBE,
            "macOS Version",
            "Choose your target macOS version for optimal compatibility",
            self.custom_card
        )
        self.macos_card.clicked.connect(self.select_macos_version)
        self.custom_card.addSettingCard(self.macos_card)

        self.acpi_card = PushSettingCard(
            "Configure Patches",
            FluentIcon.DEVELOPER_TOOLS,
            "ACPI Patches",
            "Customize system ACPI table modifications for hardware compatibility",
            self.custom_card
        )
        self.acpi_card.clicked.connect(self.customize_acpi)
        self.custom_card.addSettingCard(self.acpi_card)

        self.kexts_card = PushSettingCard(
            "Manage Kexts",
            FluentIcon.CODE,
            "Kernel Extensions",
            "Configure kexts required for your hardware",
            self.custom_card
        )
        self.kexts_card.clicked.connect(self.customize_kexts)
        self.custom_card.addSettingCard(self.kexts_card)

        self.boot_picker_card = PickerGroup(self.settings, self.custom_card)
        self.custom_card.addSettingCard(self.boot_picker_card)

        self.security_config_card = SecurityConfigGroup(self.settings, self.custom_card)
        self.custom_card.addSettingCard(self.security_config_card)

        self.boot_args_card = BootArgsGroup(self.settings, self.custom_card)
        self.custom_card.addSettingCard(self.boot_args_card)

        self.smbios_card = SMBIOSGroup(self.settings, self.controller, self.customize_smbios, self.custom_card)
        self.custom_card.addSettingCard(self.smbios_card)

        self.main_layout.addWidget(self.custom_card)
        self.main_layout.addStretch()

    def _build_config_card(self):
        if self.config_card is not None:
            self.main_layout.removeWidget(self.config_card)
            self.config_card.deleteLater()

        self.config_card = GroupHeaderCardWidget("Current Configuration", self.scrollWidget)

        macos_widget = QWidget()
        macos_widget_layout = QHBoxLayout(macos_widget)
        macos_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.macos_value = BodyLabel(self.controller.macos_state.macos_version_name)
        self.macos_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        macos_widget_layout.addWidget(self.macos_value)
        macos_widget_layout.addStretch()

        self.config_card.addGroup(
            FluentIcon.GLOBE,
            "macOS Version",
            "Target operating system version",
            macos_widget
        )

        disabled_devices = self.controller.hardware_state.disabled_devices or {}

        if disabled_devices:
            header_widget = QWidget()
            header_layout = QVBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_label = BodyLabel("Hardware components excluded from configuration")
            header_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            header_layout.addWidget(header_label)

            self.config_card.addGroup(
                FluentIcon.CLOSE,
                "Disabled Devices",
                "",
                header_widget
            )

            for device_name in disabled_devices.keys():
                add_group_with_indent(
                    self.config_card,
                    FluentIcon.INFO,
                    device_name,
                    "",
                    None,
                    indent_level=1
                )
        else:
            status_widget = QWidget()
            status_layout = QVBoxLayout(status_widget)
            status_layout.setContentsMargins(0, 0, 0, 0)
            
            if not self.controller.hardware_state.hardware_report:
                status_text = "Please select hardware report first"
                status_color = COLORS['text_secondary']
                status_icon = FluentIcon.INFO
            elif not self.controller.macos_state.darwin_version:
                status_text = "Please select target macOS version first"
                status_color = COLORS['text_secondary']
                status_icon = FluentIcon.INFO
            else:
                status_text = "All hardware components are compatible and enabled"
                status_color = COLORS['success']
                status_icon = FluentIcon.ACCEPT
            
            status_label = BodyLabel(status_text)
            status_label.setStyleSheet(f"color: {status_color};")
            status_layout.addWidget(status_label)

            self.config_card.addGroup(
                status_icon,
                "Disabled Devices",
                "",
                status_widget
            )

        self.main_layout.insertWidget(self.cards_start_index, self.config_card)

    def select_macos_version(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please select hardware report first", 'warning')
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
        self._build_config_card()
        if hasattr(self, 'smbios_card'):
            self.smbios_card.update_model()

    def refresh(self):
        self.update_display()