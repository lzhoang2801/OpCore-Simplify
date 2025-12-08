"""
Comprehensive Settings page for OpCore Simplify GUI
Contains all 27 configurable settings across 9 categories
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    ScrollArea, TitleLabel, BodyLabel, PushButton,
    LineEdit, FluentIcon, InfoBar, InfoBarPosition,
    SettingCardGroup, SwitchSettingCard, ComboBoxSettingCard,
    PushSettingCard, ExpandSettingCard, setTheme, Theme, SpinBox,
    OptionsConfigItem, OptionsValidator, qconfig, HyperlinkCard,
    RangeSettingCard, StrongBodyLabel, CaptionLabel,
    setFont, SettingCard
)

from ..styles import COLORS, SPACING
from ...settings import Settings
from ...datasets import os_data


class SettingsPage(ScrollArea):
    """Comprehensive settings page for OpCore Simplify with all 27 settings"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setObjectName("settingsPage")
        self.settings = Settings()
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout()
        self.scrollWidget.setLayout(self.expandLayout)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with modern qfluentwidgets components"""
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # Enable transparent background for proper styling
        self.enableTransparentBackground()

        # Title labels - positioned absolutely outside the scroll area
        self.settingLabel = TitleLabel("Settings", self)
        setFont(self.settingLabel, 28, QFont.Weight.DemiBold)
        self.settingLabel.move(36, 30)

        # Subtitle with improved styling
        self.subtitle_label = StrongBodyLabel(
            "Configure OpCore Simplify preferences", self)
        self.subtitle_label.setStyleSheet(
            f"color: {COLORS['text_secondary']};")
        self.subtitle_label.move(36, 70)

        # Category count with helpful info
        self.category_info = CaptionLabel(
            "27 settings organized across 9 categories • Changes are saved automatically", self)
        self.category_info.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        self.category_info.move(36, 95)

        # Initialize layout for setting cards
        self._init_layout()

    def _init_layout(self):
        """Initialize the layout with all setting groups"""
        # Set layout spacing and margins
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])

        # Build Settings Group
        self.build_group = self.create_build_settings_group()
        self.expandLayout.addWidget(self.build_group)

        # Boot Arguments Group
        self.boot_group = self.create_boot_args_group()
        self.expandLayout.addWidget(self.boot_group)

        # macOS Version Settings Group
        self.macos_group = self.create_macos_version_group()
        self.expandLayout.addWidget(self.macos_group)

        # OpenCore Boot Picker Group
        self.picker_group = self.create_boot_picker_group()
        self.expandLayout.addWidget(self.picker_group)

        # Security Settings Group
        self.security_group = self.create_security_group()
        self.expandLayout.addWidget(self.security_group)

        # SMBIOS Settings Group
        self.smbios_group = self.create_smbios_group()
        self.expandLayout.addWidget(self.smbios_group)

        # Appearance Group
        self.appearance_group = self.create_appearance_group()
        self.expandLayout.addWidget(self.appearance_group)

        # Update & Download Settings Group
        self.update_group = self.create_update_settings_group()
        self.expandLayout.addWidget(self.update_group)

        # Advanced Settings Group
        self.advanced_group = self.create_advanced_group()
        self.expandLayout.addWidget(self.advanced_group)

        # Documentation and Help Group
        self.help_group = self.create_help_group()
        self.expandLayout.addWidget(self.help_group)

        # Bottom section with version and reset button
        self.bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(self.bottom_widget)
        bottom_layout.setContentsMargins(
            0, SPACING['large'], 0, SPACING['large'])
        bottom_layout.setSpacing(SPACING['medium'])

        # Version information with better styling
        version_container = QHBoxLayout()
        version_container.setSpacing(SPACING['small'])

        version_label = StrongBodyLabel("Version:")
        version_container.addWidget(version_label)

        git_sha = self.get_git_version()
        version_value = CaptionLabel(git_sha)
        version_value.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-family: 'Courier New', monospace;")
        version_container.addWidget(version_value)

        bottom_layout.addLayout(version_container)
        bottom_layout.addStretch()

        # Reset button
        reset_btn = PushButton("Reset All to Defaults", self.bottom_widget)
        reset_btn.setIcon(FluentIcon.CANCEL)
        reset_btn.clicked.connect(self.reset_to_defaults)
        bottom_layout.addWidget(reset_btn)

        self.expandLayout.addWidget(self.bottom_widget)

        # Adjust icon size for all setting cards (must be done after all cards are added)
        # ExpandSettingCard inherits from QScrollArea, not SettingCard, so it won't be affected
        for card in self.findChildren(SettingCard):
            card.setIconSize(18, 18)

    def create_build_settings_group(self):
        """Create build settings group using modern components"""
        group = SettingCardGroup("Build Settings", self.scrollWidget)

        # Output directory setting
        self.output_dir_card = PushSettingCard(
            "Browse",
            FluentIcon.FOLDER,
            "Build Output Directory",
            self.settings.get("build_output_directory",
                              "") or "Use temporary directory (default)",
            group
        )
        self.output_dir_card.clicked.connect(self.browse_output_directory)
        group.addSettingCard(self.output_dir_card)

        # Open folder after build setting
        self.open_folder_card = SwitchSettingCard(
            FluentIcon.FOLDER_ADD,
            "Open folder after build",
            "Automatically opens the EFI build result folder when the build process completes successfully",
            configItem=None,
            parent=group
        )
        self.open_folder_card.switchButton.setChecked(
            self.settings.get("open_folder_after_build", True))
        self.open_folder_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("open_folder_after_build", checked))
        group.addSettingCard(self.open_folder_card)

        # Clean temp files setting
        self.clean_temp_card = SwitchSettingCard(
            FluentIcon.DELETE,
            "Clean temporary files on exit",
            "Automatically removes temporary build files and cache when closing the application to save disk space",
            configItem=None,
            parent=group
        )
        self.clean_temp_card.switchButton.setChecked(
            self.settings.get("clean_temp_files_on_exit", True))
        self.clean_temp_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("clean_temp_files_on_exit", checked))
        group.addSettingCard(self.clean_temp_card)

        return group

    def create_boot_args_group(self):
        """Create boot arguments group using modern components"""
        group = SettingCardGroup("Boot Arguments", self.scrollWidget)

        # Verbose boot setting
        self.verbose_boot_card = SwitchSettingCard(
            FluentIcon.CODE,
            "Verbose boot (debug mode)",
            'Enables verbose boot with "-v debug=0x100 keepsyms=1" arguments for detailed boot logging and troubleshooting',
            configItem=None,
            parent=group
        )
        self.verbose_boot_card.switchButton.setChecked(
            self.settings.get("verbose_boot", True))
        self.verbose_boot_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("verbose_boot", checked))
        group.addSettingCard(self.verbose_boot_card)

        # Custom boot arguments with expandable card
        self.custom_boot_args_card = ExpandSettingCard(
            FluentIcon.COMMAND_PROMPT,
            "Additional Boot Arguments",
            "Add custom boot arguments (space-separated). Examples: alcid=1 (audio), -wegnoegpu (disable GPU)",
            group
        )
        self.custom_boot_args_input = LineEdit(self)
        self.custom_boot_args_input.setPlaceholderText(
            "e.g., alcid=1 -wegnoegpu agdpmod=pikera")
        self.custom_boot_args_input.setText(
            self.settings.get("custom_boot_args", ""))
        self.custom_boot_args_input.textChanged.connect(
            lambda text: self.settings.set("custom_boot_args", text))
        self.custom_boot_args_input.setClearButtonEnabled(True)
        self.custom_boot_args_card.viewLayout.addWidget(
            self.custom_boot_args_input)
        group.addSettingCard(self.custom_boot_args_card)

        return group

    def create_macos_version_group(self):
        """Create macOS version settings group using modern components"""
        group = SettingCardGroup("macOS Version Settings", self.scrollWidget)

        # Include beta versions
        self.include_beta_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            "Include beta versions",
            "Shows beta and unreleased macOS versions in version selection menus. Enable for testing new macOS releases.",
            configItem=None,
            parent=group
        )
        self.include_beta_card.switchButton.setChecked(
            self.settings.get("include_beta_versions", False))
        self.include_beta_card.switchButton.checkedChanged.connect(
            self.on_include_beta_toggled)
        group.addSettingCard(self.include_beta_card)

        # Preferred macOS version selection
        version_values, version_texts = self._get_macos_version_options()
        initial_value = self.settings.get("preferred_macos_version", "")
        if initial_value not in version_values:
            initial_value = ""

        self.macos_version_validator = OptionsValidator(version_values)
        self.macos_version_config = OptionsConfigItem(
            "macOSSettings",
            "PreferredVersion",
            initial_value,
            self.macos_version_validator
        )
        self.macos_version_config.valueChanged.connect(
            self.on_preferred_version_changed)

        self.preferred_version_card = ComboBoxSettingCard(
            self.macos_version_config,
            FluentIcon.EMBED,
            "Preferred macOS Version",
            "Sets the default macOS version to auto-select. Choose 'Auto' for automatic hardware-based detection.",
            version_texts,
            group
        )
        group.addSettingCard(self.preferred_version_card)

        return group

    def _get_macos_version_options(self):
        """Build the macOS version options (value/text pairs)."""
        include_beta = self.settings.get("include_beta_versions", False)
        values = [""]
        texts = ["Auto"]

        for macos_info in os_data.macos_versions:
            if macos_info.release_status != "final" and not include_beta:
                continue

            display_name = f"macOS {macos_info.name} ({macos_info.macos_version})"
            if macos_info.release_status != "final":
                display_name += " (Beta)"

            values.append(f"{macos_info.darwin_version}.0.0")
            texts.append(display_name)

        return values, texts

    def update_version_dropdown(self):
        """Refresh ComboBoxSettingCard options when include beta toggles."""
        if not hasattr(self, 'preferred_version_card') or not hasattr(self, 'macos_version_config'):
            return

        values, texts = self._get_macos_version_options()
        self.macos_version_validator.options = values

        card = self.preferred_version_card
        combo = card.comboBox

        combo.blockSignals(True)
        combo.clear()
        card.optionToText = {value: text for value, text in zip(values, texts)}

        for text, value in zip(texts, values):
            combo.addItem(text, userData=value)

        current_value = qconfig.get(self.macos_version_config)
        if current_value not in card.optionToText:
            current_value = values[0]
            qconfig.set(self.macos_version_config, current_value, save=False)

        combo.setCurrentText(card.optionToText[current_value])
        combo.blockSignals(False)

    def on_include_beta_toggled(self, checked):
        """Update settings and refresh options when beta visibility changes."""
        self.settings.set("include_beta_versions", checked)
        self.update_version_dropdown()

    def on_preferred_version_changed(self, value):
        """Store preferred macOS version whenever the config item changes."""
        self.settings.set("preferred_macos_version", value or "")

    def on_picker_mode_changed(self, value):
        """Persist picker mode selection."""
        self.settings.set("picker_mode", value)

    def on_picker_variant_changed(self, value):
        """Persist picker variant selection."""
        self.settings.set("picker_variant", value)

    def on_secure_boot_model_changed(self, value):
        """Persist secure boot model selection."""
        self.settings.set("secure_boot_model", value)

    def on_vault_changed(self, value):
        """Persist vault selection."""
        self.settings.set("vault", value)

    def create_boot_picker_group(self):
        """Create OpenCore boot picker settings group using modern components"""
        group = SettingCardGroup("OpenCore Boot Picker", self.scrollWidget)

        # Show picker
        self.show_picker_card = SwitchSettingCard(
            FluentIcon.MENU,
            "Show boot picker",
            "Displays the OpenCore boot menu at startup, allowing you to choose between different boot entries",
            configItem=None,
            parent=group
        )
        self.show_picker_card.switchButton.setChecked(
            self.settings.get("show_picker", True))
        self.show_picker_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("show_picker", checked))
        group.addSettingCard(self.show_picker_card)

        # Picker mode
        picker_mode_values = ["Auto", "Builtin", "External"]
        picker_mode_value = self.settings.get("picker_mode", "Auto")
        if picker_mode_value not in picker_mode_values:
            picker_mode_value = "Auto"

        self.picker_mode_config = OptionsConfigItem(
            "BootPicker",
            "Mode",
            picker_mode_value,
            OptionsValidator(picker_mode_values)
        )
        self.picker_mode_config.valueChanged.connect(
            self.on_picker_mode_changed)

        self.picker_mode_card = ComboBoxSettingCard(
            self.picker_mode_config,
            FluentIcon.APPLICATION,
            "Picker mode",
            "Boot picker interface: Auto (firmware-based), Builtin (text mode), or External (OpenCanopy GUI)",
            picker_mode_values,
            group
        )
        group.addSettingCard(self.picker_mode_card)

        # Hide auxiliary
        self.hide_aux_card = SwitchSettingCard(
            FluentIcon.HIDE,
            "Hide auxiliary entries",
            "Hides auxiliary boot entries (recovery, reset NVRAM, tools) from the boot picker for a cleaner interface",
            configItem=None,
            parent=group
        )
        self.hide_aux_card.switchButton.setChecked(
            self.settings.get("hide_auxiliary", False))
        self.hide_aux_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("hide_auxiliary", checked))
        group.addSettingCard(self.hide_aux_card)

        # Picker timeout using SpinBox for precise control
        self.timeout_card = ExpandSettingCard(
            FluentIcon.HISTORY,
            "Boot timeout",
            "Time in seconds to wait before auto-booting the default entry. Set to 0 to wait indefinitely.",
            group
        )
        self.timeout_spin = SpinBox(self)
        self.timeout_spin.setRange(0, 60)
        self.timeout_spin.setValue(self.settings.get("picker_timeout", 5))
        self.timeout_spin.valueChanged.connect(
            lambda value: self.settings.set("picker_timeout", value))
        self.timeout_card.viewLayout.addWidget(self.timeout_spin)
        group.addSettingCard(self.timeout_card)

        # Picker variant
        picker_variant_values = [
            "Auto",
            "Acidanthera/GoldenGate",
            "Acidanthera/Syrah",
            "Acidanthera/Chardonnay"
        ]
        picker_variant_value = self.settings.get("picker_variant", "Auto")
        if picker_variant_value not in picker_variant_values:
            picker_variant_value = "Auto"

        self.picker_variant_config = OptionsConfigItem(
            "BootPicker",
            "Variant",
            picker_variant_value,
            OptionsValidator(picker_variant_values)
        )
        self.picker_variant_config.valueChanged.connect(
            self.on_picker_variant_changed)

        self.picker_variant_card = ComboBoxSettingCard(
            self.picker_variant_config,
            FluentIcon.PALETTE,
            "Picker visual theme",
            "Selects the visual theme for the OpenCore boot picker (only applies when using External/OpenCanopy mode)",
            picker_variant_values,
            group
        )
        group.addSettingCard(self.picker_variant_card)

        return group

    def create_security_group(self):
        """Create security settings group using modern components"""
        group = SettingCardGroup("Security Settings ⚠️", self.scrollWidget)

        # Disable SIP
        self.disable_sip_card = SwitchSettingCard(
            FluentIcon.SETTING,
            "Disable SIP",
            "Disables System Integrity Protection (csr-active-config). Required for many Hackintosh features and kexts.",
            configItem=None,
            parent=group
        )
        self.disable_sip_card.switchButton.setChecked(
            self.settings.get("disable_sip", True))
        self.disable_sip_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("disable_sip", checked))
        group.addSettingCard(self.disable_sip_card)

        # Secure boot model
        secure_boot_values = ["Default", "Disabled",
                              "j137", "j680", "j132", "j174", "j140k", "j152f"]
        secure_boot_value = self.settings.get("secure_boot_model", "Default")
        if secure_boot_value not in secure_boot_values:
            secure_boot_value = "Default"

        self.secure_boot_config = OptionsConfigItem(
            "Security",
            "SecureBootModel",
            secure_boot_value,
            OptionsValidator(secure_boot_values)
        )
        self.secure_boot_config.valueChanged.connect(
            self.on_secure_boot_model_changed)

        self.secure_boot_card = ComboBoxSettingCard(
            self.secure_boot_config,
            FluentIcon.CERTIFICATE,
            "Secure Boot Model",
            "Secure boot configuration: Default (auto-detect), Disabled (no secure boot), or specific Mac model identifiers",
            secure_boot_values,
            group
        )
        group.addSettingCard(self.secure_boot_card)

        # Vault
        vault_values = ["Optional", "Basic", "Secure"]
        vault_value = self.settings.get("vault", "Optional")
        if vault_value not in vault_values:
            vault_value = "Optional"

        self.vault_config = OptionsConfigItem(
            "Security",
            "Vault",
            vault_value,
            OptionsValidator(vault_values)
        )
        self.vault_config.valueChanged.connect(self.on_vault_changed)

        self.vault_card = ComboBoxSettingCard(
            self.vault_config,
            FluentIcon.COMPLETED,
            "OpenCore Vault",
            "Vault protection level: Optional (none), Basic/Secure (requires vault signature setup for enhanced security)",
            vault_values,
            group
        )
        group.addSettingCard(self.vault_card)

        return group

    def create_smbios_group(self):
        """Create SMBIOS settings group using modern components"""
        group = SettingCardGroup("SMBIOS Settings ⚠️", self.scrollWidget)

        # Random SMBIOS
        self.random_smbios_card = SwitchSettingCard(
            FluentIcon.SYNC,
            "Generate random SMBIOS",
            "Automatically generates new random serial numbers for each build to ensure unique system identifiers",
            configItem=None,
            parent=group
        )
        self.random_smbios_card.switchButton.setChecked(
            self.settings.get("random_smbios", True))
        self.random_smbios_card.switchButton.checkedChanged.connect(
            self.on_random_smbios_changed)
        group.addSettingCard(self.random_smbios_card)

        # Preserve SMBIOS
        self.preserve_smbios_card = SwitchSettingCard(
            FluentIcon.SAVE,
            "Preserve SMBIOS between builds",
            "Maintains the same SMBIOS values across multiple builds for consistency with iCloud and other services",
            configItem=None,
            parent=group
        )
        self.preserve_smbios_card.switchButton.setChecked(
            self.settings.get("preserve_smbios", False))
        self.preserve_smbios_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("preserve_smbios", checked))
        group.addSettingCard(self.preserve_smbios_card)

        # Custom serial number with expandable card
        self.custom_serial_card = ExpandSettingCard(
            FluentIcon.TAG,
            "Custom Serial Number",
            "Override auto-generated serial. Leave empty for automatic generation. Disabled when random SMBIOS is enabled.",
            group
        )
        self.custom_serial_input = LineEdit(self)
        self.custom_serial_input.setPlaceholderText(
            "Leave empty to auto-generate")
        self.custom_serial_input.setText(
            self.settings.get("custom_serial_number", ""))
        self.custom_serial_input.textChanged.connect(
            lambda text: self.settings.set("custom_serial_number", text))
        self.custom_serial_input.setEnabled(
            not self.settings.get("random_smbios", True))
        self.custom_serial_input.setClearButtonEnabled(True)
        self.custom_serial_card.viewLayout.addWidget(self.custom_serial_input)
        group.addSettingCard(self.custom_serial_card)

        # Custom MLB with expandable card
        self.custom_mlb_card = ExpandSettingCard(
            FluentIcon.DEVELOPER_TOOLS,
            "Custom MLB (Main Logic Board)",
            "Override auto-generated MLB. Leave empty for automatic generation. Disabled when random SMBIOS is enabled.",
            group
        )
        self.custom_mlb_input = LineEdit(self)
        self.custom_mlb_input.setPlaceholderText(
            "Leave empty to auto-generate")
        self.custom_mlb_input.setText(self.settings.get("custom_mlb", ""))
        self.custom_mlb_input.textChanged.connect(
            lambda text: self.settings.set("custom_mlb", text))
        self.custom_mlb_input.setEnabled(
            not self.settings.get("random_smbios", True))
        self.custom_mlb_input.setClearButtonEnabled(True)
        self.custom_mlb_card.viewLayout.addWidget(self.custom_mlb_input)
        group.addSettingCard(self.custom_mlb_card)

        # Custom ROM with expandable card
        self.custom_rom_card = ExpandSettingCard(
            FluentIcon.RINGER,
            "Custom ROM (MAC Address)",
            "Override auto-generated ROM address. Format: 12 hex digits (e.g., 112233445566). Disabled when random SMBIOS is enabled.",
            group
        )
        self.custom_rom_input = LineEdit(self)
        self.custom_rom_input.setPlaceholderText(
            "e.g., 112233445566")
        self.custom_rom_input.setText(self.settings.get("custom_rom", ""))
        self.custom_rom_input.textChanged.connect(
            lambda text: self.settings.set("custom_rom", text))
        self.custom_rom_input.setEnabled(
            not self.settings.get("random_smbios", True))
        self.custom_rom_input.setClearButtonEnabled(True)
        self.custom_rom_card.viewLayout.addWidget(self.custom_rom_input)
        group.addSettingCard(self.custom_rom_card)

        return group

    def create_appearance_group(self):
        """Create appearance settings group using modern components"""
        group = SettingCardGroup("Appearance", self.scrollWidget)

        # Theme setting
        theme_values = ["light", "dark"]
        theme_texts = ["Light", "Dark"]
        theme_value = self.settings.get("theme", "light")
        if theme_value not in theme_values:
            theme_value = "light"

        self.theme_config = OptionsConfigItem(
            "Appearance",
            "Theme",
            theme_value,
            OptionsValidator(theme_values)
        )
        self.theme_config.valueChanged.connect(self.on_theme_changed)

        self.theme_card = ComboBoxSettingCard(
            self.theme_config,
            FluentIcon.BRUSH,
            "Theme",
            "Selects the application color theme. Changes take effect immediately throughout the interface.",
            theme_texts,
            group
        )
        group.addSettingCard(self.theme_card)

        return group

    def create_update_settings_group(self):
        """Create update & download settings group using modern components"""
        group = SettingCardGroup("Updates & Downloads", self.scrollWidget)

        # Auto-update check
        self.auto_update_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            "Check for updates on startup",
            "Automatically checks for new OpCore Simplify updates when the application launches to keep you up to date",
            configItem=None,
            parent=group
        )
        self.auto_update_card.switchButton.setChecked(
            self.settings.get("auto_update_check", True))
        self.auto_update_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("auto_update_check", checked))
        group.addSettingCard(self.auto_update_card)

        # Verify download integrity
        self.verify_integrity_card = SwitchSettingCard(
            FluentIcon.CERTIFICATE,
            "Verify download integrity (SHA256)",
            "Verifies SHA256 checksums of downloaded OpenCore and kext files to ensure authenticity and security",
            configItem=None,
            parent=group
        )
        self.verify_integrity_card.switchButton.setChecked(
            self.settings.get("verify_download_integrity", True))
        self.verify_integrity_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("verify_download_integrity", checked))
        group.addSettingCard(self.verify_integrity_card)

        # Force redownload
        self.force_redownload_card = SwitchSettingCard(
            FluentIcon.DOWNLOAD,
            "Force redownload files",
            "Forces fresh downloads of all files even if they exist locally. Useful for debugging or ensuring latest versions.",
            configItem=None,
            parent=group
        )
        self.force_redownload_card.switchButton.setChecked(
            self.settings.get("force_redownload", False))
        self.force_redownload_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("force_redownload", checked))
        group.addSettingCard(self.force_redownload_card)

        return group

    def create_advanced_group(self):
        """Create advanced settings group using modern components"""
        group = SettingCardGroup("Advanced Settings ⚠️", self.scrollWidget)

        # Enable debug logging
        self.debug_logging_card = SwitchSettingCard(
            FluentIcon.DEVELOPER_TOOLS,
            "Enable debug logging",
            "Enables detailed debug logging throughout the application for advanced troubleshooting and diagnostics",
            configItem=None,
            parent=group
        )
        self.debug_logging_card.switchButton.setChecked(
            self.settings.get("enable_debug_logging", False))
        self.debug_logging_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("enable_debug_logging", checked))
        group.addSettingCard(self.debug_logging_card)

        # Skip ACPI validation
        self.skip_acpi_card = SwitchSettingCard(
            FluentIcon.CANCEL,
            "Skip ACPI validation warnings",
            "Bypasses ACPI table validation warnings during build. Only enable if you understand the implications.",
            configItem=None,
            parent=group
        )
        self.skip_acpi_card.switchButton.setChecked(
            self.settings.get("skip_acpi_validation", False))
        self.skip_acpi_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("skip_acpi_validation", checked))
        group.addSettingCard(self.skip_acpi_card)

        # Force load incompatible kexts
        self.force_kext_card = SwitchSettingCard(
            FluentIcon.CARE_RIGHT_SOLID,
            "Force load incompatible kexts",
            "Forces loading of kexts on unsupported macOS versions using '-lilubetaall' boot argument. May cause system instability.",
            configItem=None,
            parent=group
        )
        self.force_kext_card.switchButton.setChecked(
            self.settings.get("force_load_incompatible_kexts", False))
        self.force_kext_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("force_load_incompatible_kexts", checked))
        group.addSettingCard(self.force_kext_card)

        return group

    def create_help_group(self):
        """Create help and documentation group with useful links"""
        group = SettingCardGroup("Help & Documentation", self.scrollWidget)

        # OpenCore Documentation
        self.opencore_docs_card = HyperlinkCard(
            "https://dortania.github.io/OpenCore-Install-Guide/",
            "OpenCore Install Guide",
            FluentIcon.BOOK_SHELF,
            "OpenCore Documentation",
            "Complete guide for installing macOS with OpenCore",
            group
        )
        group.addSettingCard(self.opencore_docs_card)

        # Troubleshooting Guide
        self.troubleshoot_card = HyperlinkCard(
            "https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/troubleshooting.html",
            "Troubleshooting",
            FluentIcon.HELP,
            "Troubleshooting Guide",
            "Solutions to common OpenCore installation issues",
            group
        )
        group.addSettingCard(self.troubleshoot_card)

        # GitHub Repository
        self.github_card = HyperlinkCard(
            "https://github.com/lzhoang2801/OpCore-Simplify",
            "View on GitHub",
            FluentIcon.GITHUB,
            "OpCore-Simplify Repository",
            "Report issues, contribute, or view the source code",
            group
        )
        group.addSettingCard(self.github_card)

        return group

    def browse_output_directory(self):
        """Browse for output directory"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Build Output Directory",
            self.settings.get("build_output_directory",
                              "") or os.path.expanduser("~")
        )

        if folder:
            self.settings.set("build_output_directory", folder)
            self.output_dir_card.setContent(folder)
            self.show_success("Output directory updated successfully")

    def on_theme_changed(self, value):
        """Handle theme change"""
        theme = value if value in ("light", "dark") else "light"
        self.settings.set("theme", theme)

        # Apply theme immediately
        setTheme(Theme.DARK if theme == "dark" else Theme.LIGHT)

        self.show_success("Theme updated successfully")

    def on_random_smbios_changed(self, checked):
        """Handle random SMBIOS toggle"""
        self.settings.set("random_smbios", checked)

        # Enable/disable custom SMBIOS inputs
        self.custom_serial_input.setEnabled(not checked)
        self.custom_mlb_input.setEnabled(not checked)
        self.custom_rom_input.setEnabled(not checked)

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        from ..custom_dialogs import show_question_dialog
        result = show_question_dialog(
            self.controller,
            "Reset Settings",
            "Are you sure you want to reset all 27 settings to their default values?"
        )

        if result:
            # Reset settings
            self.settings.settings = self.settings.defaults.copy()
            self.settings.save()

            # Update all UI elements using the new card components
            self.output_dir_card.setContent(
                "Use temporary directory (default)")
            self.open_folder_card.switchButton.setChecked(True)
            self.clean_temp_card.switchButton.setChecked(True)
            self.verbose_boot_card.switchButton.setChecked(True)
            self.custom_boot_args_input.setText("")
            self.include_beta_card.switchButton.setChecked(False)
            if hasattr(self, 'preferred_version_card'):
                self.preferred_version_card.setValue("")
            self.show_picker_card.switchButton.setChecked(True)
            if hasattr(self, 'picker_mode_card'):
                self.picker_mode_card.setValue("Auto")
            self.hide_aux_card.switchButton.setChecked(False)
            if hasattr(self, 'timeout_spin'):
                self.timeout_spin.setValue(5)
            if hasattr(self, 'picker_variant_card'):
                self.picker_variant_card.setValue("Auto")
            self.disable_sip_card.switchButton.setChecked(True)
            if hasattr(self, 'secure_boot_card'):
                self.secure_boot_card.setValue("Default")
            if hasattr(self, 'vault_card'):
                self.vault_card.setValue("Optional")
            self.random_smbios_card.switchButton.setChecked(True)
            self.preserve_smbios_card.switchButton.setChecked(False)
            self.custom_serial_input.setText("")
            self.custom_mlb_input.setText("")
            self.custom_rom_input.setText("")
            if hasattr(self, 'theme_card'):
                self.theme_card.setValue("light")
            self.auto_update_card.switchButton.setChecked(True)
            self.verify_integrity_card.switchButton.setChecked(True)
            self.force_redownload_card.switchButton.setChecked(False)
            self.debug_logging_card.switchButton.setChecked(False)
            self.skip_acpi_card.switchButton.setChecked(False)
            self.force_kext_card.switchButton.setChecked(False)

            self.show_success("All settings reset to defaults")

    def show_success(self, message):
        """Show success message"""
        InfoBar.success(
            title='Success',
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.controller
        )

    def get_git_version(self):
        """Get the SHA version from sha_version.txt file"""
        try:
            # Get the project root directory (3 levels up from this file)
            script_dir = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

            # Read from sha_version.txt file
            sha_version_file = os.path.join(script_dir, 'sha_version.txt')
            if os.path.exists(sha_version_file):
                with open(sha_version_file, 'r') as f:
                    version = f.read().strip()
                    if version:
                        return version

            # If file doesn't exist or is empty
            return "unknown"
        except Exception:
            return "unknown"
