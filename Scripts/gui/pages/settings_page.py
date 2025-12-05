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
    LineEdit, FluentIcon, InfoBar, InfoBarPosition,
    SettingCardGroup, SwitchSettingCard, ComboBox,
    PushSettingCard, ExpandSettingCard, setTheme, Theme, SpinBox
)

from ..styles import COLORS, SPACING
from ...settings import Settings
from ...datasets import os_data


class SettingsPage(QWidget):
    """Comprehensive settings page for OpCore Simplify with all 27 settings"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setObjectName("settingsPage")
        self.settings = Settings()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with modern qfluentwidgets components"""
        # Main layout with proper margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])

        # Title
        title_label = TitleLabel("Settings")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = BodyLabel(
            "Configure OpCore Simplify preferences - 27 settings across 9 categories")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle_label)

        layout.addSpacing(SPACING['medium'])

        # Scroll area for settings
        scroll = ScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(SPACING['medium'])
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Build Settings Group
        self.build_group = self.create_build_settings_group()
        scroll_layout.addWidget(self.build_group)

        # Boot Arguments Group
        self.boot_group = self.create_boot_args_group()
        scroll_layout.addWidget(self.boot_group)

        # macOS Version Settings Group
        self.macos_group = self.create_macos_version_group()
        scroll_layout.addWidget(self.macos_group)

        # OpenCore Boot Picker Group
        self.picker_group = self.create_boot_picker_group()
        scroll_layout.addWidget(self.picker_group)

        # Security Settings Group
        self.security_group = self.create_security_group()
        scroll_layout.addWidget(self.security_group)

        # SMBIOS Settings Group
        self.smbios_group = self.create_smbios_group()
        scroll_layout.addWidget(self.smbios_group)

        # Appearance Group
        self.appearance_group = self.create_appearance_group()
        scroll_layout.addWidget(self.appearance_group)

        # Update & Download Settings Group
        self.update_group = self.create_update_settings_group()
        scroll_layout.addWidget(self.update_group)

        # Advanced Settings Group
        self.advanced_group = self.create_advanced_group()
        scroll_layout.addWidget(self.advanced_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Bottom section with version and reset button
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, SPACING['medium'], 0, 0)
        
        # Version information
        version_label = BodyLabel("Version:")
        version_label.setStyleSheet("font-weight: bold;")
        bottom_layout.addWidget(version_label)

        git_sha = self.get_git_version()
        version_value = BodyLabel(git_sha)
        version_value.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-family: 'Courier New', monospace;")
        bottom_layout.addWidget(version_value)

        bottom_layout.addStretch()

        # Reset button
        reset_btn = PushButton("Reset All to Defaults", self)
        reset_btn.setIcon(FluentIcon.CANCEL)
        reset_btn.clicked.connect(self.reset_to_defaults)
        bottom_layout.addWidget(reset_btn)
        
        layout.addLayout(bottom_layout)

    def create_build_settings_group(self):
        """Create build settings group using modern components"""
        group = SettingCardGroup("Build Settings", self)
        
        # Output directory setting
        self.output_dir_card = PushSettingCard(
            "Browse",
            FluentIcon.FOLDER,
            "Build Output Directory",
            self.settings.get("build_output_directory", "") or "Use temporary directory (default)",
            group
        )
        self.output_dir_card.clicked.connect(self.browse_output_directory)
        group.addSettingCard(self.output_dir_card)

        # Open folder after build setting
        self.open_folder_card = SwitchSettingCard(
            FluentIcon.FOLDER_ADD,
            "Open folder after build",
            "Automatically open the result folder after EFI build completes",
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
            "Remove temporary build files when closing the application",
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
        group = SettingCardGroup("Boot Arguments", self)

        # Verbose boot setting
        self.verbose_boot_card = SwitchSettingCard(
            FluentIcon.CODE,
            "Verbose boot (debug mode)",
            'Include "-v debug=0x100 keepsyms=1" in boot-args for detailed boot logging',
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
            "Add custom boot arguments (e.g., 'alcid=1 -wegnoegpu'). Space-separated, appended to defaults.",
            group
        )
        self.custom_boot_args_input = LineEdit(self)
        self.custom_boot_args_input.setPlaceholderText("e.g., alcid=1 -wegnoegpu")
        self.custom_boot_args_input.setText(self.settings.get("custom_boot_args", ""))
        self.custom_boot_args_input.textChanged.connect(
            lambda text: self.settings.set("custom_boot_args", text))
        self.custom_boot_args_card.viewLayout.addWidget(self.custom_boot_args_input)
        group.addSettingCard(self.custom_boot_args_card)

        return group

    def create_macos_version_group(self):
        """Create macOS version settings group using modern components"""
        group = SettingCardGroup("macOS Version Settings", self)

        # Include beta versions
        self.include_beta_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            "Include beta versions",
            "Show beta/unreleased macOS versions in version selection menu",
            configItem=None,
            parent=group
        )
        self.include_beta_card.switchButton.setChecked(
            self.settings.get("include_beta_versions", False))
        self.include_beta_card.switchButton.checkedChanged.connect(
            lambda checked: [self.settings.set("include_beta_versions", checked), self.update_version_dropdown()])
        group.addSettingCard(self.include_beta_card)

        # Preferred macOS version with dropdown
        self.preferred_version_card = ExpandSettingCard(
            FluentIcon.EMBED,
            "Preferred macOS Version",
            "Default macOS version to auto-select. Leave as 'Auto' for automatic detection based on hardware.",
            group
        )
        
        # Create ComboBox with available macOS versions
        self.preferred_version_combo = ComboBox(self)
        self.update_version_dropdown()
        
        # Connect to save the darwin version when changed
        self.preferred_version_combo.currentTextChanged.connect(self.on_preferred_version_changed)
        
        self.preferred_version_card.viewLayout.addWidget(self.preferred_version_combo)
        group.addSettingCard(self.preferred_version_card)

        return group
    
    def update_version_dropdown(self):
        """Update the version dropdown based on include_beta_versions setting"""
        # Save current selection
        current_text = self.preferred_version_combo.currentText() if hasattr(self, 'preferred_version_combo') else None
        
        # Clear and rebuild dropdown
        self.preferred_version_combo.clear()
        
        # Add "Auto" as first option
        version_options = ["Auto"]
        
        # Check if beta versions should be included
        include_beta = self.settings.get("include_beta_versions", False)
        
        # Add macOS versions from the dataset
        for macos_info in os_data.macos_versions:
            # Skip beta versions if not enabled
            if macos_info.release_status != "final" and not include_beta:
                continue
            
            # Format: "macOS Ventura (13)" for example
            display_name = f"macOS {macos_info.name} ({macos_info.macos_version})"
            if macos_info.release_status != "final":
                display_name += " (Beta)"
            version_options.append(display_name)
        
        self.preferred_version_combo.addItems(version_options)
        
        # Restore previous selection if it still exists
        if current_text and current_text in version_options:
            self.preferred_version_combo.setCurrentText(current_text)
        else:
            # Set current value from settings
            current_pref = self.settings.get("preferred_macos_version", "")
            if current_pref:
                # Try to find matching version by darwin version
                matched = False
                for macos_info in os_data.macos_versions:
                    if current_pref.startswith(str(macos_info.darwin_version)):
                        display_name = f"macOS {macos_info.name} ({macos_info.macos_version})"
                        if macos_info.release_status != "final":
                            display_name += " (Beta)"
                        if display_name in version_options:
                            self.preferred_version_combo.setCurrentText(display_name)
                            matched = True
                            break
                if not matched:
                    self.preferred_version_combo.setCurrentIndex(0)  # Auto
            else:
                self.preferred_version_combo.setCurrentIndex(0)  # Auto
    
    def on_preferred_version_changed(self, text):
        """Handle preferred macOS version change"""
        if text == "Auto":
            self.settings.set("preferred_macos_version", "")
        else:
            # Extract version info from display text
            # Format is "macOS Ventura (13)" or "macOS Tahoe (26) (Beta)"
            for macos_info in os_data.macos_versions:
                display_name = f"macOS {macos_info.name} ({macos_info.macos_version})"
                if macos_info.release_status != "final":
                    display_name += " (Beta)"
                
                if text == display_name:
                    # Save as darwin version format (e.g., "23.0.0")
                    darwin_version = f"{macos_info.darwin_version}.0.0"
                    self.settings.set("preferred_macos_version", darwin_version)
                    break

    def create_boot_picker_group(self):
        """Create OpenCore boot picker settings group using modern components"""
        group = SettingCardGroup("OpenCore Boot Picker", self)

        # Show picker
        self.show_picker_card = SwitchSettingCard(
            FluentIcon.MENU,
            "Show boot picker",
            "Display OpenCore boot menu at startup",
            configItem=None,
            parent=group
        )
        self.show_picker_card.switchButton.setChecked(
            self.settings.get("show_picker", True))
        self.show_picker_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("show_picker", checked))
        group.addSettingCard(self.show_picker_card)

        # Picker mode
        self.picker_mode_card = ExpandSettingCard(
            FluentIcon.APPLICATION,
            "Picker mode",
            "Auto: Determined by firmware type. Builtin: Text mode. External: GUI mode with OpenCanopy.",
            group
        )
        self.picker_mode_combo = ComboBox(self)
        self.picker_mode_combo.addItems(["Auto", "Builtin", "External"])
        self.picker_mode_combo.setCurrentText(self.settings.get("picker_mode", "Auto"))
        self.picker_mode_combo.currentTextChanged.connect(
            lambda text: self.settings.set("picker_mode", text))
        self.picker_mode_card.viewLayout.addWidget(self.picker_mode_combo)
        group.addSettingCard(self.picker_mode_card)

        # Hide auxiliary
        self.hide_aux_card = SwitchSettingCard(
            FluentIcon.HIDE,
            "Hide auxiliary entries",
            "Hide auxiliary entries (recovery, reset NVRAM, tools) in boot picker",
            configItem=None,
            parent=group
        )
        self.hide_aux_card.switchButton.setChecked(
            self.settings.get("hide_auxiliary", False))
        self.hide_aux_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("hide_auxiliary", checked))
        group.addSettingCard(self.hide_aux_card)

        # Picker timeout using ExpandSettingCard with SpinBox
        self.timeout_card = ExpandSettingCard(
            FluentIcon.HISTORY,
            "Boot timeout (seconds)",
            "Time to wait before auto-booting default entry. 0 = wait indefinitely.",
            group
        )
        self.timeout_spin = SpinBox(self)
        self.timeout_spin.setRange(0, 999)
        self.timeout_spin.setValue(self.settings.get("picker_timeout", 5))
        self.timeout_spin.valueChanged.connect(
            lambda value: self.settings.set("picker_timeout", value))
        self.timeout_card.viewLayout.addWidget(self.timeout_spin)
        group.addSettingCard(self.timeout_card)

        # Picker variant
        self.picker_variant_card = ExpandSettingCard(
            FluentIcon.PALETTE,
            "Picker visual theme",
            "Visual theme for OpenCore boot picker (External mode only)",
            group
        )
        self.picker_variant_combo = ComboBox(self)
        self.picker_variant_combo.addItems(
            ["Auto", "Acidanthera/GoldenGate", "Acidanthera/Syrah", "Acidanthera/Chardonnay"])
        self.picker_variant_combo.setCurrentText(self.settings.get("picker_variant", "Auto"))
        self.picker_variant_combo.currentTextChanged.connect(
            lambda text: self.settings.set("picker_variant", text))
        self.picker_variant_card.viewLayout.addWidget(self.picker_variant_combo)
        group.addSettingCard(self.picker_variant_card)

        return group

    def create_security_group(self):
        """Create security settings group using modern components"""
        group = SettingCardGroup("Security Settings ⚠️", self)

        # Disable SIP
        self.disable_sip_card = SwitchSettingCard(
            FluentIcon.SETTING,
            "Disable SIP",
            "Disable System Integrity Protection (csr-active-config). Required for many Hackintosh features.",
            configItem=None,
            parent=group
        )
        self.disable_sip_card.switchButton.setChecked(
            self.settings.get("disable_sip", True))
        self.disable_sip_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("disable_sip", checked))
        group.addSettingCard(self.disable_sip_card)

        # Secure boot model
        self.secure_boot_card = ExpandSettingCard(
            FluentIcon.CERTIFICATE,
            "Secure Boot Model",
            "Default: Auto-select based on macOS version. Disabled: No secure boot. Others: Specific Mac model identifiers.",
            group
        )
        self.secure_boot_combo = ComboBox(self)
        self.secure_boot_combo.addItems(
            ["Default", "Disabled", "j137", "j680", "j132", "j174", "j140k", "j152f"])
        self.secure_boot_combo.setCurrentText(self.settings.get("secure_boot_model", "Default"))
        self.secure_boot_combo.currentTextChanged.connect(
            lambda text: self.settings.set("secure_boot_model", text))
        self.secure_boot_card.viewLayout.addWidget(self.secure_boot_combo)
        group.addSettingCard(self.secure_boot_card)

        # Vault
        self.vault_card = ExpandSettingCard(
            FluentIcon.COMPLETED,
            "OpenCore Vault",
            "Optional: No vault protection. Basic/Secure: Vault signature verification (requires manual setup).",
            group
        )
        self.vault_combo = ComboBox(self)
        self.vault_combo.addItems(["Optional", "Basic", "Secure"])
        self.vault_combo.setCurrentText(self.settings.get("vault", "Optional"))
        self.vault_combo.currentTextChanged.connect(
            lambda text: self.settings.set("vault", text))
        self.vault_card.viewLayout.addWidget(self.vault_combo)
        group.addSettingCard(self.vault_card)

        return group

    def create_smbios_group(self):
        """Create SMBIOS settings group using modern components"""
        group = SettingCardGroup("SMBIOS Settings ⚠️", self)

        # Random SMBIOS
        self.random_smbios_card = SwitchSettingCard(
            FluentIcon.SYNC,
            "Generate random SMBIOS",
            "Generate new random serial numbers for each build",
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
            "Keep the same SMBIOS values across multiple builds",
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
            "Leave empty to auto-generate. Disabled when random SMBIOS is enabled.",
            group
        )
        self.custom_serial_input = LineEdit(self)
        self.custom_serial_input.setPlaceholderText("Leave empty to auto-generate")
        self.custom_serial_input.setText(self.settings.get("custom_serial_number", ""))
        self.custom_serial_input.textChanged.connect(
            lambda text: self.settings.set("custom_serial_number", text))
        self.custom_serial_input.setEnabled(not self.settings.get("random_smbios", True))
        self.custom_serial_card.viewLayout.addWidget(self.custom_serial_input)
        group.addSettingCard(self.custom_serial_card)

        # Custom MLB with expandable card
        self.custom_mlb_card = ExpandSettingCard(
            FluentIcon.DEVELOPER_TOOLS,
            "Custom MLB (Main Logic Board)",
            "Leave empty to auto-generate. Disabled when random SMBIOS is enabled.",
            group
        )
        self.custom_mlb_input = LineEdit(self)
        self.custom_mlb_input.setPlaceholderText("Leave empty to auto-generate")
        self.custom_mlb_input.setText(self.settings.get("custom_mlb", ""))
        self.custom_mlb_input.textChanged.connect(
            lambda text: self.settings.set("custom_mlb", text))
        self.custom_mlb_input.setEnabled(not self.settings.get("random_smbios", True))
        self.custom_mlb_card.viewLayout.addWidget(self.custom_mlb_input)
        group.addSettingCard(self.custom_mlb_card)

        # Custom ROM with expandable card
        self.custom_rom_card = ExpandSettingCard(
            FluentIcon.RINGER,
            "Custom ROM (MAC Address)",
            "Leave empty to auto-generate (e.g., 112233445566). Disabled when random SMBIOS is enabled.",
            group
        )
        self.custom_rom_input = LineEdit(self)
        self.custom_rom_input.setPlaceholderText("Leave empty to auto-generate (e.g., 112233445566)")
        self.custom_rom_input.setText(self.settings.get("custom_rom", ""))
        self.custom_rom_input.textChanged.connect(
            lambda text: self.settings.set("custom_rom", text))
        self.custom_rom_input.setEnabled(not self.settings.get("random_smbios", True))
        self.custom_rom_card.viewLayout.addWidget(self.custom_rom_input)
        group.addSettingCard(self.custom_rom_card)

        return group

    def create_appearance_group(self):
        """Create appearance settings group using modern components"""
        group = SettingCardGroup("Appearance", self)

        # Theme setting
        self.theme_card = ExpandSettingCard(
            FluentIcon.BRUSH,
            "Theme",
            "Choose the application theme. Changes apply immediately.",
            group
        )
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(["Light", "Dark"])
        current_theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentText("Light" if current_theme == "light" else "Dark")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.theme_card.viewLayout.addWidget(self.theme_combo)
        group.addSettingCard(self.theme_card)

        return group

    def create_update_settings_group(self):
        """Create update & download settings group using modern components"""
        group = SettingCardGroup("Updates & Downloads", self)

        # Auto-update check
        self.auto_update_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            "Check for updates on startup",
            "Automatically check for OpCore Simplify updates when the application starts",
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
            "Verify SHA256 checksums of downloaded OpenCore and kext files for security",
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
            "Always download fresh files even if they exist locally. Useful for debugging.",
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
        group = SettingCardGroup("Advanced Settings ⚠️", self)

        # Enable debug logging
        self.debug_logging_card = SwitchSettingCard(
            FluentIcon.DEVELOPER_TOOLS,
            "Enable debug logging",
            "Enable detailed debug logging throughout the application for troubleshooting",
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
            "Bypass ACPI table validation warnings. Use only if you know what you're doing.",
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
            "Force load kexts on unsupported macOS versions using '-lilubetaall'. May cause instability.",
            configItem=None,
            parent=group
        )
        self.force_kext_card.switchButton.setChecked(
            self.settings.get("force_load_incompatible_kexts", False))
        self.force_kext_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("force_load_incompatible_kexts", checked))
        group.addSettingCard(self.force_kext_card)

        return group

    def browse_output_directory(self):
        """Browse for output directory"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Build Output Directory",
            self.settings.get("build_output_directory", "") or os.path.expanduser("~")
        )

        if folder:
            self.settings.set("build_output_directory", folder)
            self.output_dir_card.setContent(folder)
            self.show_success("Output directory updated successfully")

    def on_theme_changed(self, text):
        """Handle theme change"""
        theme = "light" if text == "Light" else "dark"
        self.settings.set("theme", theme)

        # Apply theme immediately
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

            # Update all UI elements using the new card components
            self.output_dir_card.setContent("Use temporary directory (default)")
            self.open_folder_card.switchButton.setChecked(True)
            self.clean_temp_card.switchButton.setChecked(True)
            self.verbose_boot_card.switchButton.setChecked(True)
            self.custom_boot_args_input.setText("")
            self.include_beta_card.switchButton.setChecked(False)
            self.preferred_version_combo.setCurrentIndex(0)  # Set to "Auto"
            self.show_picker_card.switchButton.setChecked(True)
            self.picker_mode_combo.setCurrentText("Auto")
            self.hide_aux_card.switchButton.setChecked(False)
            self.timeout_spin.setValue(5)
            self.picker_variant_combo.setCurrentText("Auto")
            self.disable_sip_card.switchButton.setChecked(True)
            self.secure_boot_combo.setCurrentText("Default")
            self.vault_combo.setCurrentText("Optional")
            self.random_smbios_card.switchButton.setChecked(True)
            self.preserve_smbios_card.switchButton.setChecked(False)
            self.custom_serial_input.setText("")
            self.custom_mlb_input.setText("")
            self.custom_rom_input.setText("")
            self.theme_combo.setCurrentText("Light")
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
