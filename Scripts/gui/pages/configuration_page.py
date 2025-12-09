from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ScrollArea, SubtitleLabel, BodyLabel, FluentIcon, 
    GroupHeaderCardWidget, SettingCardGroup, SwitchSettingCard, 
    ComboBoxSettingCard, PushSettingCard, ExpandSettingCard, 
    SpinBox, LineEdit, OptionsConfigItem, OptionsValidator
)

from ..styles import SPACING, COLORS
from ..ui_utils import add_group_with_indent, create_step_indicator
from ...settings import Settings


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

        self.boot_picker_card = ExpandSettingCard(
            FluentIcon.MENU,
            "Boot Picker",
            "Configure OpenCore picker settings",
            self.custom_card
        )
        self._picker_group(self.boot_picker_card)
        self.custom_card.addSettingCard(self.boot_picker_card)

        self.security_config_card = ExpandSettingCard(
            FluentIcon.DEVELOPER_TOOLS,
            "Security Configuration",
            "System Integrity Protection and Secure Boot",
            self.custom_card
        )
        self._security_group(self.security_config_card)
        self.custom_card.addSettingCard(self.security_config_card)

        self.boot_args_card = ExpandSettingCard(
            FluentIcon.COMMAND_PROMPT,
            "Boot Arguments",
            "Configure verbose mode and custom boot arguments",
            self.custom_card
        )
        self._bootargs_group(self.boot_args_card)
        self.custom_card.addSettingCard(self.boot_args_card)

        self.smbios_card = ExpandSettingCard(
            FluentIcon.PEOPLE,
            "SMBIOS Configuration",
            "SMBIOS generation and preservation options",
            self.custom_card
        )
        self._smbios_group(self.smbios_card)
        self.custom_card.addSettingCard(self.smbios_card)

        self.main_layout.addWidget(self.custom_card)
        self.main_layout.addStretch()

    def _picker_group(self, parent_card):
        show_picker_card = SwitchSettingCard(
            FluentIcon.MENU,
            "Show Picker",
            "Show the OpenCore Picker at startup, allowing you to choose between different boot entries.",
            configItem=None,
            parent=parent_card
        )
        show_picker_card.setObjectName("show_picker")
        show_picker_card.switchButton.setChecked(self.settings.get("show_picker", True))
        show_picker_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("show_picker", checked))
        parent_card.viewLayout.addWidget(show_picker_card)

        picker_mode_values = ["Builtin", "External"]
        picker_mode_value = self.settings.get("picker_mode", "External")
        if picker_mode_value not in picker_mode_values:
            picker_mode_value = "External"

        picker_mode_config = OptionsConfigItem(
            "BootPicker",
            "Mode",
            picker_mode_value,
            OptionsValidator(picker_mode_values)
        )
        picker_mode_config.valueChanged.connect(lambda value: self.settings.set("picker_mode", value))

        picker_mode_card = ComboBoxSettingCard(
            picker_mode_config,
            FluentIcon.APPLICATION,
            "Picker Mode",
            "Picker used for boot management: Builtin (text mode) or External (OpenCanopy GUI)",
            picker_mode_values,
            parent_card
        )
        picker_mode_card.setObjectName("picker_mode")
        parent_card.viewLayout.addWidget(picker_mode_card)

        hide_aux_card = SwitchSettingCard(
            FluentIcon.HIDE,
            "Hide auxiliary entries",
            "Hides auxiliary boot entries (Recovery, Reset NVRAM, Tools) from the boot picker for a cleaner interface",
            configItem=None,
            parent=parent_card
        )
        hide_aux_card.setObjectName("hide_auxiliary")
        hide_aux_card.switchButton.setChecked(self.settings.get("hide_auxiliary", False))
        hide_aux_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("hide_auxiliary", checked))
        parent_card.viewLayout.addWidget(hide_aux_card)

        picker_variant_values = [
            "Auto",
            "Acidanthera/GoldenGate",
            "Acidanthera/Syrah",
            "Acidanthera/Chardonnay"
        ]
        picker_variant_value = self.settings.get("picker_variant", "Auto")
        if picker_variant_value not in picker_variant_values:
            picker_variant_value = "Auto"

        picker_variant_config = OptionsConfigItem(
            "BootPicker",
            "Variant",
            picker_variant_value,
            OptionsValidator(picker_variant_values)
        )
        picker_variant_config.valueChanged.connect(lambda value: self.settings.set("picker_variant", value))

        picker_variant_card = ComboBoxSettingCard(
            picker_variant_config,
            FluentIcon.PALETTE,
            "Picker Variant",
            "Choose specific icon set to be used for boot management. Requires External Picker mode.",
            picker_variant_values,
            parent_card
        )
        picker_variant_card.setObjectName("picker_variant")
        parent_card.viewLayout.addWidget(picker_variant_card)

        timeout_card = ExpandSettingCard(
            FluentIcon.HISTORY,
            "Timeout",
            "Timeout in seconds in the OpenCore picker before automatic booting of the default boot entry. Set to 0 to disable.",
            parent_card
        )
        timeout_spin = SpinBox(timeout_card)
        timeout_spin.setObjectName("picker_timeout")
        timeout_spin.setRange(0, 60)
        timeout_spin.setValue(self.settings.get("picker_timeout", 5))
        timeout_spin.valueChanged.connect(lambda value: self.settings.set("picker_timeout", value))
        timeout_card.viewLayout.addWidget(timeout_spin)
        parent_card.viewLayout.addWidget(timeout_card)

    def _security_group(self, parent_card):
        disable_sip_card = SwitchSettingCard(
            FluentIcon.SETTING,
            "Disable System Integrity Protection (SIP)",
            "Allowing unrestricted modifications and installation of software, kexts, and kernel patches. Required for OpenCore Legacy Patcher and other tools.",
            configItem=None,
            parent=parent_card
        )
        disable_sip_card.setObjectName("disable_sip")
        disable_sip_card.switchButton.setChecked(self.settings.get("disable_sip", True))
        disable_sip_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("disable_sip", checked))
        parent_card.viewLayout.addWidget(disable_sip_card)

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
        secure_boot_value = self.settings.get("secure_boot_model", "Disabled")
        if secure_boot_value not in secure_boot_values:
            secure_boot_value = "Disabled"

        secure_boot_config = OptionsConfigItem(
            "Security",
            "SecureBootModel",
            secure_boot_value,
            OptionsValidator(secure_boot_values)
        )
        secure_boot_config.valueChanged.connect(lambda value: self.settings.set("secure_boot_model", value))

        secure_boot_card = ComboBoxSettingCard(
            secure_boot_config,
            FluentIcon.CERTIFICATE,
            "Secure Boot Model",
            "Sets Apple Secure Boot hardware model for security level: Default (based on SMBIOS board identifier), Disabled (Medium security), or specific value for Full security (e.g. j137, j680, etc.)",
            secure_boot_values,
            parent_card
        )
        parent_card.viewLayout.addWidget(secure_boot_card)

    def _bootargs_group(self, parent_card):
        verbose_boot_card = SwitchSettingCard(
            FluentIcon.CODE,
            "Verbose boot (debug mode)",
            'Enables verbose boot with "-v debug=0x100 keepsyms=1" arguments for detailed boot logging and troubleshooting',
            configItem=None,
            parent=parent_card
        )
        verbose_boot_card.setObjectName("verbose_boot")
        verbose_boot_card.switchButton.setChecked(self.settings.get("verbose_boot", True))
        verbose_boot_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("verbose_boot", checked))
        parent_card.viewLayout.addWidget(verbose_boot_card)

        custom_boot_args_card = ExpandSettingCard(
            FluentIcon.COMMAND_PROMPT,
            "Additional Boot Arguments",
            "Add custom boot arguments (space-separated)",
            parent_card
        )
        custom_boot_args_input = LineEdit(custom_boot_args_card)
        custom_boot_args_input.setObjectName("custom_boot_args")
        custom_boot_args_input.setPlaceholderText("e.g., -radcodec -raddvi")
        custom_boot_args_input.setText(self.settings.get("custom_boot_args", ""))
        custom_boot_args_input.textChanged.connect(lambda text: self.settings.set("custom_boot_args", text))
        custom_boot_args_input.setClearButtonEnabled(True)
        custom_boot_args_card.viewLayout.addWidget(custom_boot_args_input)
        parent_card.viewLayout.addWidget(custom_boot_args_card)

    def _smbios_group(self, parent_card):
        smbios_model_card = PushSettingCard(
            "Select Model",
            FluentIcon.TAG,
            "SMBIOS Model",
            "Choose the Mac model your system will identify as",
            parent_card
        )
        smbios_model_card.clicked.connect(self.customize_smbios)
        parent_card.viewLayout.addWidget(smbios_model_card)

        random_smbios_card = SwitchSettingCard(
            FluentIcon.SYNC,
            "Generate random SMBIOS",
            "Automatically generates new random serial numbers for each build to ensure unique system identifiers",
            configItem=None,
            parent=parent_card
        )
        random_smbios_card.setObjectName("random_smbios")
        random_smbios_card.switchButton.setChecked(self.settings.get("random_smbios", True))
        random_smbios_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("random_smbios", checked))
        parent_card.viewLayout.addWidget(random_smbios_card)

        preserve_smbios_card = SwitchSettingCard(
            FluentIcon.SAVE,
            "Preserve SMBIOS between builds",
            "Maintains the same SMBIOS values across multiple builds for consistency with iCloud and other services",
            configItem=None,
            parent=parent_card
        )
        preserve_smbios_card.setObjectName("preserve_smbios")
        preserve_smbios_card.switchButton.setChecked(self.settings.get("preserve_smbios", False))
        preserve_smbios_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("preserve_smbios", checked))
        parent_card.viewLayout.addWidget(preserve_smbios_card)

    def _build_config_card(self):
        if self.config_card is not None:
            self.main_layout.removeWidget(self.config_card)
            self.config_card.deleteLater()

        self.config_card = GroupHeaderCardWidget("Current Configuration", self.scrollWidget)

        macos_widget = QWidget()
        macos_widget_layout = QHBoxLayout(macos_widget)
        macos_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.macos_value = BodyLabel(self.controller.macos_state.version_text)
        self.macos_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        macos_widget_layout.addWidget(self.macos_value)
        macos_widget_layout.addStretch()

        self.config_card.addGroup(
            FluentIcon.GLOBE,
            "macOS Version",
            "Target operating system version",
            macos_widget
        )

        smbios_widget = QWidget()
        smbios_widget_layout = QHBoxLayout(smbios_widget)
        smbios_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.smbios_value = BodyLabel(self.controller.smbios_state.model_text)
        self.smbios_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        smbios_widget_layout.addWidget(self.smbios_value)
        smbios_widget_layout.addStretch()

        self.config_card.addGroup(
            FluentIcon.TAG,
            "SMBIOS Model",
            "System identifier for macOS",
            smbios_widget
        )

        disabled_devices = self.controller.hardware_state.disabled_devices if self.controller.hardware_state.disabled_devices is not None else {}

        if disabled_devices:
            header_widget = QWidget()
            header_layout = QVBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_label = BodyLabel(
                "Hardware components excluded from configuration")
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
            none_widget = QWidget()
            none_layout = QVBoxLayout(none_widget)
            none_layout.setContentsMargins(0, 0, 0, 0)
            none_label = BodyLabel(
                "All hardware components are compatible and enabled")
            none_label.setStyleSheet(f"color: {COLORS['success']};")
            none_layout.addWidget(none_label)

            self.config_card.addGroup(
                FluentIcon.ACCEPT,
                "Disabled Devices",
                "",
                none_widget
            )

        self.main_layout.insertWidget(
            self.cards_start_index, self.config_card)

    def select_macos_version(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please load a hardware report first", 'warning')
            return

        from ..custom_dialogs import show_macos_version_dialog

        suggested_version = self.controller.suggest_macos_version()

        selected_version, ok = show_macos_version_dialog(
            self.controller,
            self.controller.macos_state.native_version,
            self.controller.macos_state.ocl_patched_version,
            suggested_version,
            self.controller.ocpe.u
        )

        if ok and selected_version:
            # Apply the selected macOS version
            self.controller.apply_macos_version(selected_version)
            self.controller.update_status(
                f"macOS version updated to {self.controller.macos_state.version_text}", 'success')

    def customize_acpi(self):
        """Customize ACPI patches"""
        # Check if hardware report is loaded
        if not self.controller.hardware_state.customized_hardware:
            self.controller.update_status(
                "Please select hardware report and target macOS version first", 'warning')
            return

        # Import the ACPI patches dialog
        from ..custom_dialogs import show_acpi_patches_dialog

        # Show the ACPI patches dialog
        ok = show_acpi_patches_dialog(
            self.controller,
            self.controller.ocpe.ac
        )

        if ok:
            self.controller.update_status(
                "ACPI patches configuration updated successfully", 'success')

    def customize_kexts(self):
        """Customize kexts"""
        # Check if hardware report is loaded
        if not self.controller.hardware_state.customized_hardware:
            self.controller.update_status(
                "Please select hardware report and target macOS version first", 'warning')
            return

        # Import the kexts dialog
        from ..custom_dialogs import show_kexts_dialog

        # Show the kexts dialog (macos_version is in Darwin kernel version format, e.g., "22.0.0")
        ok = show_kexts_dialog(
            self.controller,
            self.controller.ocpe.k,
            self.controller.macos_state.version_darwin
        )

        if ok:
            self.controller.update_status(
                "Kext configuration updated successfully", 'success')

    def customize_smbios(self):
        """Customize SMBIOS model"""
        # Check if hardware report is loaded
        if not self.controller.hardware_state.customized_hardware:
            self.controller.update_status(
                "Please select hardware report and target macOS version first", 'warning')
            return

        # Import required modules
        from ...datasets.mac_model_data import mac_devices
        from ..custom_dialogs import show_smbios_dialog

        # Get current state
        current_model = self.controller.smbios_state.model_text
        default_model = self.controller.ocpe.s.select_smbios_model(
            self.controller.hardware_state.customized_hardware,
            self.controller.macos_state.version_darwin  # Use Darwin version
        )
        is_laptop = "Laptop" == self.controller.hardware_state.customized_hardware.get(
            "Motherboard").get("Platform")

        # Show SMBIOS selection dialog
        selected_model, ok = show_smbios_dialog(
            self.controller,
            mac_devices,
            current_model,
            default_model,
            self.controller.macos_state.version_darwin,  # Use Darwin version
            is_laptop,
            self.controller.ocpe.u
        )

        if ok and selected_model != current_model:
            # Update the selected SMBIOS model
            self.controller.smbios_state.model_text = selected_model

            # Apply SMBIOS-specific options
            self.controller.ocpe.s.smbios_specific_options(
                self.controller.hardware_state.customized_hardware,
                selected_model,
                self.controller.macos_state.version_darwin,  # Use Darwin version
                self.controller.ocpe.ac.patches,
                self.controller.ocpe.k
            )

            # Update display
            self.update_display()
            self.controller.update_status(
                f"SMBIOS model updated to {selected_model}", 'success')

    def update_display(self):
        """Update configuration display by rebuilding the config card"""
        self._build_config_card()

    def refresh(self):
        """Refresh page content"""
        self.update_display()