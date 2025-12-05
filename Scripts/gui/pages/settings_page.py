"""
Comprehensive Settings page for OpCore Simplify GUI
Contains all 27 configurable settings across 9 categories
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ScrollArea, TitleLabel, BodyLabel, PushButton, 
    SwitchButton, LineEdit, ComboBox, CardWidget,
    FluentIcon, InfoBar, InfoBarPosition, SpinBox,
    ExpandLayout, SettingCardGroup, OptionsSettingCard,
    SwitchSettingCard, RangeSettingCard, PushSettingCard,
    HyperlinkCard, PrimaryPushSettingCard
)

from ..styles import COLORS, SPACING
from ...settings import Settings


class SettingsPage(QWidget):
    """Comprehensive settings page for OpCore Simplify with all 27 settings"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.settings = Settings()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = TitleLabel("Settings")
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = BodyLabel("Configure OpCore Simplify preferences - 27 settings across 9 categories")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle_label)
        
        # Scroll area for settings
        scroll = ScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Build Settings Card
        build_card = self.create_build_settings_card()
        scroll_layout.addWidget(build_card)
        
        # Boot Arguments Card
        boot_card = self.create_boot_args_card()
        scroll_layout.addWidget(boot_card)
        
        # macOS Version Settings Card
        macos_card = self.create_macos_version_card()
        scroll_layout.addWidget(macos_card)
        
        # OpenCore Boot Picker Card
        picker_card = self.create_boot_picker_card()
        scroll_layout.addWidget(picker_card)
        
        # Security Settings Card
        security_card = self.create_security_card()
        scroll_layout.addWidget(security_card)
        
        # SMBIOS Settings Card
        smbios_card = self.create_smbios_card()
        scroll_layout.addWidget(smbios_card)
        
        # Appearance Card
        appearance_card = self.create_appearance_card()
        scroll_layout.addWidget(appearance_card)
        
        # Update & Download Settings Card
        update_card = self.create_update_settings_card()
        scroll_layout.addWidget(update_card)
        
        # Advanced Settings Card
        advanced_card = self.create_advanced_card()
        scroll_layout.addWidget(advanced_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Version information
        version_layout = QHBoxLayout()
        version_layout.setContentsMargins(10, 10, 10, 5)
        
        version_label = BodyLabel("Version:")
        version_label.setStyleSheet("font-weight: bold;")
        version_layout.addWidget(version_label)
        
        # Get git SHA version
        git_sha = self.get_git_version()
        version_value = BodyLabel(git_sha)
        version_value.setStyleSheet(f"color: {COLORS['text_secondary']}; font-family: 'Courier New', monospace;")
        version_layout.addWidget(version_value)
        
        version_layout.addStretch()
        layout.addLayout(version_layout)
        
        # Reset button at bottom
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_btn = PushButton("Reset All to Defaults", self)
        reset_btn.setIcon(FluentIcon.CANCEL)
        reset_btn.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(reset_btn)
        layout.addLayout(reset_layout)
    
    def create_build_settings_card(self):
        """Create build settings card (3 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title
        title = TitleLabel("Build Settings")
        card_layout.addWidget(title)
        
        # Output directory setting
        dir_label = BodyLabel("Build Output Directory:")
        dir_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(dir_label)
        
        dir_desc = BodyLabel("Choose where to save built EFI folders. Leave empty to use temporary directory.")
        dir_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(dir_desc)
        
        dir_layout = QHBoxLayout()
        self.output_dir_input = LineEdit(self)
        self.output_dir_input.setPlaceholderText("Use temporary directory (default)")
        current_dir = self.settings.get("build_output_directory", "")
        if current_dir:
            self.output_dir_input.setText(current_dir)
        self.output_dir_input.textChanged.connect(lambda text: self.settings.set("build_output_directory", text))
        dir_layout.addWidget(self.output_dir_input)
        
        browse_btn = PushButton("Browse", self)
        browse_btn.setIcon(FluentIcon.FOLDER)
        browse_btn.clicked.connect(self.browse_output_directory)
        dir_layout.addWidget(browse_btn)
        
        card_layout.addLayout(dir_layout)
        
        # Open folder after build setting
        open_layout = QHBoxLayout()
        open_label = BodyLabel("Open folder after build:")
        open_label.setStyleSheet("font-weight: bold;")
        open_layout.addWidget(open_label)
        open_layout.addStretch()
        
        self.open_folder_switch = SwitchButton(self)
        self.open_folder_switch.setChecked(self.settings.get("open_folder_after_build", True))
        self.open_folder_switch.checkedChanged.connect(lambda checked: self.settings.set("open_folder_after_build", checked))
        open_layout.addWidget(self.open_folder_switch)
        
        card_layout.addLayout(open_layout)
        
        open_desc = BodyLabel("Automatically open the result folder after EFI build completes.")
        open_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(open_desc)
        
        # Clean temp files setting
        clean_layout = QHBoxLayout()
        clean_label = BodyLabel("Clean temporary files on exit:")
        clean_label.setStyleSheet("font-weight: bold;")
        clean_layout.addWidget(clean_label)
        clean_layout.addStretch()
        
        self.clean_temp_switch = SwitchButton(self)
        self.clean_temp_switch.setChecked(self.settings.get("clean_temp_files_on_exit", True))
        self.clean_temp_switch.checkedChanged.connect(lambda checked: self.settings.set("clean_temp_files_on_exit", checked))
        clean_layout.addWidget(self.clean_temp_switch)
        
        card_layout.addLayout(clean_layout)
        
        clean_desc = BodyLabel("Remove temporary build files when closing the application.")
        clean_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(clean_desc)
        
        return card
    
    def create_boot_args_card(self):
        """Create boot arguments card (2 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title
        title = TitleLabel("Boot Arguments")
        card_layout.addWidget(title)
        
        # Verbose boot setting
        verbose_layout = QHBoxLayout()
        verbose_label = BodyLabel("Verbose boot (debug mode):")
        verbose_label.setStyleSheet("font-weight: bold;")
        verbose_layout.addWidget(verbose_label)
        verbose_layout.addStretch()
        
        self.verbose_boot_switch = SwitchButton(self)
        self.verbose_boot_switch.setChecked(self.settings.get("verbose_boot", True))
        self.verbose_boot_switch.checkedChanged.connect(lambda checked: self.settings.set("verbose_boot", checked))
        verbose_layout.addWidget(self.verbose_boot_switch)
        
        card_layout.addLayout(verbose_layout)
        
        verbose_desc = BodyLabel('Include "-v debug=0x100 keepsyms=1" in boot-args for detailed boot logging.')
        verbose_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(verbose_desc)
        
        # Custom boot arguments
        custom_label = BodyLabel("Additional Boot Arguments:")
        custom_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(custom_label)
        
        custom_desc = BodyLabel("Add custom boot arguments (e.g., 'alcid=1 -wegnoegpu'). Space-separated, appended to defaults.")
        custom_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(custom_desc)
        
        self.custom_boot_args_input = LineEdit(self)
        self.custom_boot_args_input.setPlaceholderText("e.g., alcid=1 -wegnoegpu")
        self.custom_boot_args_input.setText(self.settings.get("custom_boot_args", ""))
        self.custom_boot_args_input.textChanged.connect(lambda text: self.settings.set("custom_boot_args", text))
        card_layout.addWidget(self.custom_boot_args_input)
        
        return card
    
    def create_macos_version_card(self):
        """Create macOS version settings card (2 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title
        title = TitleLabel("macOS Version Settings")
        card_layout.addWidget(title)
        
        # Include beta versions
        beta_layout = QHBoxLayout()
        beta_label = BodyLabel("Include beta versions:")
        beta_label.setStyleSheet("font-weight: bold;")
        beta_layout.addWidget(beta_label)
        beta_layout.addStretch()
        
        self.include_beta_switch = SwitchButton(self)
        self.include_beta_switch.setChecked(self.settings.get("include_beta_versions", False))
        self.include_beta_switch.checkedChanged.connect(lambda checked: self.settings.set("include_beta_versions", checked))
        beta_layout.addWidget(self.include_beta_switch)
        
        card_layout.addLayout(beta_layout)
        
        beta_desc = BodyLabel("Show beta/unreleased macOS versions in version selection menu.")
        beta_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(beta_desc)
        
        # Preferred macOS version
        pref_label = BodyLabel("Preferred macOS Version:")
        pref_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(pref_label)
        
        pref_desc = BodyLabel("Default macOS version to auto-select (Darwin format, e.g., '23.0.0'). Leave empty for auto-detection.")
        pref_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(pref_desc)
        
        self.preferred_version_input = LineEdit(self)
        self.preferred_version_input.setPlaceholderText("e.g., 23.0.0 (Ventura) - leave empty for auto")
        self.preferred_version_input.setText(self.settings.get("preferred_macos_version", ""))
        self.preferred_version_input.textChanged.connect(lambda text: self.settings.set("preferred_macos_version", text))
        card_layout.addWidget(self.preferred_version_input)
        
        return card
    
    def create_boot_picker_card(self):
        """Create OpenCore boot picker settings card (5 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title
        title = TitleLabel("OpenCore Boot Picker")
        card_layout.addWidget(title)
        
        # Show picker
        show_layout = QHBoxLayout()
        show_label = BodyLabel("Show boot picker:")
        show_label.setStyleSheet("font-weight: bold;")
        show_layout.addWidget(show_label)
        show_layout.addStretch()
        
        self.show_picker_switch = SwitchButton(self)
        self.show_picker_switch.setChecked(self.settings.get("show_picker", True))
        self.show_picker_switch.checkedChanged.connect(lambda checked: self.settings.set("show_picker", checked))
        show_layout.addWidget(self.show_picker_switch)
        
        card_layout.addLayout(show_layout)
        
        show_desc = BodyLabel("Display OpenCore boot menu at startup.")
        show_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(show_desc)
        
        # Picker mode
        mode_label = BodyLabel("Picker mode:")
        mode_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(mode_label)
        
        mode_layout = QHBoxLayout()
        self.picker_mode_combo = ComboBox(self)
        self.picker_mode_combo.addItems(["Auto", "Builtin", "External"])
        current_mode = self.settings.get("picker_mode", "Auto")
        self.picker_mode_combo.setCurrentText(current_mode)
        self.picker_mode_combo.currentTextChanged.connect(lambda text: self.settings.set("picker_mode", text))
        mode_layout.addWidget(self.picker_mode_combo)
        mode_layout.addStretch()
        card_layout.addLayout(mode_layout)
        
        mode_desc = BodyLabel("Auto: Determined by firmware type. Builtin: Text mode. External: GUI mode with OpenCanopy.")
        mode_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(mode_desc)
        
        # Hide auxiliary
        aux_layout = QHBoxLayout()
        aux_label = BodyLabel("Hide auxiliary entries:")
        aux_label.setStyleSheet("font-weight: bold;")
        aux_layout.addWidget(aux_label)
        aux_layout.addStretch()
        
        self.hide_aux_switch = SwitchButton(self)
        self.hide_aux_switch.setChecked(self.settings.get("hide_auxiliary", False))
        self.hide_aux_switch.checkedChanged.connect(lambda checked: self.settings.set("hide_auxiliary", checked))
        aux_layout.addWidget(self.hide_aux_switch)
        
        card_layout.addLayout(aux_layout)
        
        aux_desc = BodyLabel("Hide auxiliary entries (recovery, reset NVRAM, tools) in boot picker.")
        aux_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(aux_desc)
        
        # Picker timeout
        timeout_label = BodyLabel("Boot timeout (seconds):")
        timeout_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(timeout_label)
        
        timeout_layout = QHBoxLayout()
        self.timeout_spin = SpinBox(self)
        self.timeout_spin.setRange(0, 999)
        self.timeout_spin.setValue(self.settings.get("picker_timeout", 5))
        self.timeout_spin.valueChanged.connect(lambda value: self.settings.set("picker_timeout", value))
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        card_layout.addLayout(timeout_layout)
        
        timeout_desc = BodyLabel("Time to wait before auto-booting default entry. 0 = wait indefinitely.")
        timeout_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(timeout_desc)
        
        # Picker variant
        variant_label = BodyLabel("Picker visual theme:")
        variant_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(variant_label)
        
        variant_layout = QHBoxLayout()
        self.picker_variant_combo = ComboBox(self)
        self.picker_variant_combo.addItems(["Auto", "Acidanthera/GoldenGate", "Acidanthera/Syrah", "Acidanthera/Chardonnay"])
        current_variant = self.settings.get("picker_variant", "Auto")
        self.picker_variant_combo.setCurrentText(current_variant)
        self.picker_variant_combo.currentTextChanged.connect(lambda text: self.settings.set("picker_variant", text))
        variant_layout.addWidget(self.picker_variant_combo)
        variant_layout.addStretch()
        card_layout.addLayout(variant_layout)
        
        variant_desc = BodyLabel("Visual theme for OpenCore boot picker (External mode only).")
        variant_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(variant_desc)
        
        return card
    
    def create_security_card(self):
        """Create security settings card (3 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title with warning
        title_layout = QHBoxLayout()
        title = TitleLabel("Security Settings")
        title_layout.addWidget(title)
        title_layout.addStretch()
        warning_label = BodyLabel("⚠️ Caution")
        warning_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        title_layout.addWidget(warning_label)
        card_layout.addLayout(title_layout)
        
        warning_desc = BodyLabel("Modifying these settings may affect system security and stability.")
        warning_desc.setStyleSheet("color: #FFA500; font-size: 12px; font-style: italic;")
        card_layout.addWidget(warning_desc)
        
        # Disable SIP
        sip_layout = QHBoxLayout()
        sip_label = BodyLabel("Disable SIP:")
        sip_label.setStyleSheet("font-weight: bold;")
        sip_layout.addWidget(sip_label)
        sip_layout.addStretch()
        
        self.disable_sip_switch = SwitchButton(self)
        self.disable_sip_switch.setChecked(self.settings.get("disable_sip", True))
        self.disable_sip_switch.checkedChanged.connect(lambda checked: self.settings.set("disable_sip", checked))
        sip_layout.addWidget(self.disable_sip_switch)
        
        card_layout.addLayout(sip_layout)
        
        sip_desc = BodyLabel("Disable System Integrity Protection (csr-active-config). Required for many Hackintosh features.")
        sip_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(sip_desc)
        
        # Secure boot model
        secure_label = BodyLabel("Secure Boot Model:")
        secure_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(secure_label)
        
        secure_layout = QHBoxLayout()
        self.secure_boot_combo = ComboBox(self)
        self.secure_boot_combo.addItems(["Default", "Disabled", "j137", "j680", "j132", "j174", "j140k", "j152f"])
        current_secure = self.settings.get("secure_boot_model", "Default")
        self.secure_boot_combo.setCurrentText(current_secure)
        self.secure_boot_combo.currentTextChanged.connect(lambda text: self.settings.set("secure_boot_model", text))
        secure_layout.addWidget(self.secure_boot_combo)
        secure_layout.addStretch()
        card_layout.addLayout(secure_layout)
        
        secure_desc = BodyLabel("Default: Auto-select based on macOS version. Disabled: No secure boot. Others: Specific Mac model identifiers.")
        secure_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(secure_desc)
        
        # Vault
        vault_label = BodyLabel("OpenCore Vault:")
        vault_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(vault_label)
        
        vault_layout = QHBoxLayout()
        self.vault_combo = ComboBox(self)
        self.vault_combo.addItems(["Optional", "Basic", "Secure"])
        current_vault = self.settings.get("vault", "Optional")
        self.vault_combo.setCurrentText(current_vault)
        self.vault_combo.currentTextChanged.connect(lambda text: self.settings.set("vault", text))
        vault_layout.addWidget(self.vault_combo)
        vault_layout.addStretch()
        card_layout.addLayout(vault_layout)
        
        vault_desc = BodyLabel("Optional: No vault protection. Basic/Secure: Vault signature verification (requires manual setup).")
        vault_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(vault_desc)
        
        return card
    
    def create_smbios_card(self):
        """Create SMBIOS settings card (5 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title with warning
        title_layout = QHBoxLayout()
        title = TitleLabel("SMBIOS Settings")
        title_layout.addWidget(title)
        title_layout.addStretch()
        warning_label = BodyLabel("⚠️ Advanced")
        warning_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        title_layout.addWidget(warning_label)
        card_layout.addLayout(title_layout)
        
        warning_desc = BodyLabel("Custom SMBIOS values may affect iServices functionality. Use with caution.")
        warning_desc.setStyleSheet("color: #FFA500; font-size: 12px; font-style: italic;")
        card_layout.addWidget(warning_desc)
        
        # Random SMBIOS
        random_layout = QHBoxLayout()
        random_label = BodyLabel("Generate random SMBIOS:")
        random_label.setStyleSheet("font-weight: bold;")
        random_layout.addWidget(random_label)
        random_layout.addStretch()
        
        self.random_smbios_switch = SwitchButton(self)
        self.random_smbios_switch.setChecked(self.settings.get("random_smbios", True))
        self.random_smbios_switch.checkedChanged.connect(self.on_random_smbios_changed)
        random_layout.addWidget(self.random_smbios_switch)
        
        card_layout.addLayout(random_layout)
        
        random_desc = BodyLabel("Generate new random serial numbers for each build.")
        random_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(random_desc)
        
        # Preserve SMBIOS
        preserve_layout = QHBoxLayout()
        preserve_label = BodyLabel("Preserve SMBIOS between builds:")
        preserve_label.setStyleSheet("font-weight: bold;")
        preserve_layout.addWidget(preserve_label)
        preserve_layout.addStretch()
        
        self.preserve_smbios_switch = SwitchButton(self)
        self.preserve_smbios_switch.setChecked(self.settings.get("preserve_smbios", False))
        self.preserve_smbios_switch.checkedChanged.connect(lambda checked: self.settings.set("preserve_smbios", checked))
        preserve_layout.addWidget(self.preserve_smbios_switch)
        
        card_layout.addLayout(preserve_layout)
        
        preserve_desc = BodyLabel("Keep the same SMBIOS values across multiple builds.")
        preserve_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(preserve_desc)
        
        # Custom serial number
        serial_label = BodyLabel("Custom Serial Number:")
        serial_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(serial_label)
        
        self.custom_serial_input = LineEdit(self)
        self.custom_serial_input.setPlaceholderText("Leave empty to auto-generate")
        self.custom_serial_input.setText(self.settings.get("custom_serial_number", ""))
        self.custom_serial_input.textChanged.connect(lambda text: self.settings.set("custom_serial_number", text))
        self.custom_serial_input.setEnabled(not self.settings.get("random_smbios", True))
        card_layout.addWidget(self.custom_serial_input)
        
        # Custom MLB
        mlb_label = BodyLabel("Custom MLB (Main Logic Board):")
        mlb_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(mlb_label)
        
        self.custom_mlb_input = LineEdit(self)
        self.custom_mlb_input.setPlaceholderText("Leave empty to auto-generate")
        self.custom_mlb_input.setText(self.settings.get("custom_mlb", ""))
        self.custom_mlb_input.textChanged.connect(lambda text: self.settings.set("custom_mlb", text))
        self.custom_mlb_input.setEnabled(not self.settings.get("random_smbios", True))
        card_layout.addWidget(self.custom_mlb_input)
        
        # Custom ROM
        rom_label = BodyLabel("Custom ROM (MAC Address):")
        rom_label.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(rom_label)
        
        self.custom_rom_input = LineEdit(self)
        self.custom_rom_input.setPlaceholderText("Leave empty to auto-generate (e.g., 112233445566)")
        self.custom_rom_input.setText(self.settings.get("custom_rom", ""))
        self.custom_rom_input.textChanged.connect(lambda text: self.settings.set("custom_rom", text))
        self.custom_rom_input.setEnabled(not self.settings.get("random_smbios", True))
        card_layout.addWidget(self.custom_rom_input)
        
        return card
    
    def create_appearance_card(self):
        """Create appearance settings card (1 setting)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title
        title = TitleLabel("Appearance")
        card_layout.addWidget(title)
        
        # Theme setting
        theme_layout = QHBoxLayout()
        theme_label = BodyLabel("Theme:")
        theme_label.setStyleSheet("font-weight: bold;")
        theme_layout.addWidget(theme_label)
        theme_layout.addStretch()
        
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(["Light", "Dark"])
        current_theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentText("Light" if current_theme == "light" else "Dark")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        card_layout.addLayout(theme_layout)
        
        theme_desc = BodyLabel("Choose the application theme. Changes apply immediately.")
        theme_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(theme_desc)
        
        return card
    
    def create_update_settings_card(self):
        """Create update & download settings card (3 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title
        title = TitleLabel("Updates & Downloads")
        card_layout.addWidget(title)
        
        # Auto-update check
        update_layout = QHBoxLayout()
        update_label = BodyLabel("Check for updates on startup:")
        update_label.setStyleSheet("font-weight: bold;")
        update_layout.addWidget(update_label)
        update_layout.addStretch()
        
        self.auto_update_switch = SwitchButton(self)
        self.auto_update_switch.setChecked(self.settings.get("auto_update_check", True))
        self.auto_update_switch.checkedChanged.connect(lambda checked: self.settings.set("auto_update_check", checked))
        update_layout.addWidget(self.auto_update_switch)
        
        card_layout.addLayout(update_layout)
        
        update_desc = BodyLabel("Automatically check for OpCore Simplify updates when the application starts.")
        update_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(update_desc)
        
        # Verify download integrity
        verify_layout = QHBoxLayout()
        verify_label = BodyLabel("Verify download integrity (SHA256):")
        verify_label.setStyleSheet("font-weight: bold;")
        verify_layout.addWidget(verify_label)
        verify_layout.addStretch()
        
        self.verify_integrity_switch = SwitchButton(self)
        self.verify_integrity_switch.setChecked(self.settings.get("verify_download_integrity", True))
        self.verify_integrity_switch.checkedChanged.connect(lambda checked: self.settings.set("verify_download_integrity", checked))
        verify_layout.addWidget(self.verify_integrity_switch)
        
        card_layout.addLayout(verify_layout)
        
        verify_desc = BodyLabel("Verify SHA256 checksums of downloaded OpenCore and kext files for security.")
        verify_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(verify_desc)
        
        # Force redownload
        force_layout = QHBoxLayout()
        force_label = BodyLabel("Force redownload files:")
        force_label.setStyleSheet("font-weight: bold;")
        force_layout.addWidget(force_label)
        force_layout.addStretch()
        
        self.force_redownload_switch = SwitchButton(self)
        self.force_redownload_switch.setChecked(self.settings.get("force_redownload", False))
        self.force_redownload_switch.checkedChanged.connect(lambda checked: self.settings.set("force_redownload", checked))
        force_layout.addWidget(self.force_redownload_switch)
        
        card_layout.addLayout(force_layout)
        
        force_desc = BodyLabel("Always download fresh files even if they exist locally. Useful for debugging.")
        force_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(force_desc)
        
        return card
    
    def create_advanced_card(self):
        """Create advanced settings card (3 settings)"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Card title with warning
        title_layout = QHBoxLayout()
        title = TitleLabel("Advanced Settings")
        title_layout.addWidget(title)
        title_layout.addStretch()
        warning_label = BodyLabel("⚠️ Experts Only")
        warning_label.setStyleSheet("color: #FF4444; font-weight: bold;")
        title_layout.addWidget(warning_label)
        card_layout.addLayout(title_layout)
        
        warning_desc = BodyLabel("These settings are for advanced users only. Incorrect values may cause boot failures.")
        warning_desc.setStyleSheet("color: #FF4444; font-size: 12px; font-style: italic;")
        card_layout.addWidget(warning_desc)
        
        # Enable debug logging
        debug_layout = QHBoxLayout()
        debug_label = BodyLabel("Enable debug logging:")
        debug_label.setStyleSheet("font-weight: bold;")
        debug_layout.addWidget(debug_label)
        debug_layout.addStretch()
        
        self.debug_logging_switch = SwitchButton(self)
        self.debug_logging_switch.setChecked(self.settings.get("enable_debug_logging", False))
        self.debug_logging_switch.checkedChanged.connect(lambda checked: self.settings.set("enable_debug_logging", checked))
        debug_layout.addWidget(self.debug_logging_switch)
        
        card_layout.addLayout(debug_layout)
        
        debug_desc = BodyLabel("Enable detailed debug logging throughout the application for troubleshooting.")
        debug_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(debug_desc)
        
        # Skip ACPI validation
        acpi_layout = QHBoxLayout()
        acpi_label = BodyLabel("Skip ACPI validation warnings:")
        acpi_label.setStyleSheet("font-weight: bold;")
        acpi_layout.addWidget(acpi_label)
        acpi_layout.addStretch()
        
        self.skip_acpi_switch = SwitchButton(self)
        self.skip_acpi_switch.setChecked(self.settings.get("skip_acpi_validation", False))
        self.skip_acpi_switch.checkedChanged.connect(lambda checked: self.settings.set("skip_acpi_validation", checked))
        acpi_layout.addWidget(self.skip_acpi_switch)
        
        card_layout.addLayout(acpi_layout)
        
        acpi_desc = BodyLabel("Bypass ACPI table validation warnings. Use only if you know what you're doing.")
        acpi_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(acpi_desc)
        
        # Force load incompatible kexts
        force_kext_layout = QHBoxLayout()
        force_kext_label = BodyLabel("Force load incompatible kexts:")
        force_kext_label.setStyleSheet("font-weight: bold;")
        force_kext_layout.addWidget(force_kext_label)
        force_kext_layout.addStretch()
        
        self.force_kext_switch = SwitchButton(self)
        self.force_kext_switch.setChecked(self.settings.get("force_load_incompatible_kexts", False))
        self.force_kext_switch.checkedChanged.connect(lambda checked: self.settings.set("force_load_incompatible_kexts", checked))
        force_kext_layout.addWidget(self.force_kext_switch)
        
        card_layout.addLayout(force_kext_layout)
        
        force_kext_desc = BodyLabel("Force load kexts on unsupported macOS versions using '-lilubetaall'. May cause instability.")
        force_kext_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        card_layout.addWidget(force_kext_desc)
        
        return card
    
    def browse_output_directory(self):
        """Browse for output directory"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Build Output Directory",
            self.output_dir_input.text() or os.path.expanduser("~")
        )
        
        if folder:
            self.output_dir_input.setText(folder)
            self.settings.set("build_output_directory", folder)
            self.show_success("Output directory updated successfully")
    
    def on_theme_changed(self, text):
        """Handle theme change"""
        theme = "light" if text == "Light" else "dark"
        self.settings.set("theme", theme)
        
        # Apply theme immediately
        from qfluentwidgets import setTheme, Theme
        if theme == "dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        
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
            
            # Update all UI elements
            self.output_dir_input.setText("")
            self.open_folder_switch.setChecked(True)
            self.clean_temp_switch.setChecked(True)
            self.verbose_boot_switch.setChecked(True)
            self.custom_boot_args_input.setText("")
            self.include_beta_switch.setChecked(False)
            self.preferred_version_input.setText("")
            self.show_picker_switch.setChecked(True)
            self.picker_mode_combo.setCurrentText("Auto")
            self.hide_aux_switch.setChecked(False)
            self.timeout_spin.setValue(5)
            self.picker_variant_combo.setCurrentText("Auto")
            self.disable_sip_switch.setChecked(True)
            self.secure_boot_combo.setCurrentText("Default")
            self.vault_combo.setCurrentText("Optional")
            self.random_smbios_switch.setChecked(True)
            self.preserve_smbios_switch.setChecked(False)
            self.custom_serial_input.setText("")
            self.custom_mlb_input.setText("")
            self.custom_rom_input.setText("")
            self.theme_combo.setCurrentText("Light")
            self.auto_update_switch.setChecked(True)
            self.verify_integrity_switch.setChecked(True)
            self.force_redownload_switch.setChecked(False)
            self.debug_logging_switch.setChecked(False)
            self.skip_acpi_switch.setChecked(False)
            self.force_kext_switch.setChecked(False)
            
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
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            
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
