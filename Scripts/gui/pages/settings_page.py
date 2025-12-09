import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ScrollArea, BodyLabel, PushButton, LineEdit, FluentIcon,
    SettingCardGroup, SwitchSettingCard, ComboBoxSettingCard,
    PushSettingCard, ExpandSettingCard, SpinBox,
    OptionsConfigItem, OptionsValidator, HyperlinkCard,
    StrongBodyLabel, CaptionLabel, SettingCard, SubtitleLabel,
    setTheme, Theme
)

from ..custom_dialogs import show_question_dialog
from ..styles import COLORS, SPACING
from ...settings import Settings


class SettingsPage(ScrollArea):
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
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        self.enableTransparentBackground()

        self._init_layout()

    def _init_layout(self):
        self.expandLayout.setSpacing(SPACING['large'])
        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])

        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Settings")
        header_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Configure OpCore Simplify preferences")
        subtitle_label.setStyleSheet("color: {};".format(COLORS['text_secondary']))
        header_layout.addWidget(subtitle_label)

        self.expandLayout.addWidget(header_container)
        self.expandLayout.addSpacing(SPACING['medium'])

        self.build_output_group = self.create_build_output_group()
        self.expandLayout.addWidget(self.build_output_group)

        self.macos_group = self.create_macos_version_group()
        self.expandLayout.addWidget(self.macos_group)

        self.bootargs_group = self.create_bootargs_group()
        self.expandLayout.addWidget(self.bootargs_group)

        self.picker_group = self.create_boot_picker_group()
        self.expandLayout.addWidget(self.picker_group)

        self.security_group = self.create_security_group()
        self.expandLayout.addWidget(self.security_group)

        self.smbios_group = self.create_smbios_group()
        self.expandLayout.addWidget(self.smbios_group)

        self.appearance_group = self.create_appearance_group()
        self.expandLayout.addWidget(self.appearance_group)

        self.update_group = self.create_update_settings_group()
        self.expandLayout.addWidget(self.update_group)

        self.advanced_group = self.create_advanced_group()
        self.expandLayout.addWidget(self.advanced_group)

        self.help_group = self.create_help_group()
        self.expandLayout.addWidget(self.help_group)
        
        self.bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(self.bottom_widget)
        bottom_layout.setContentsMargins(
            0, SPACING['large'], 0, SPACING['large'])
        bottom_layout.setSpacing(SPACING['medium'])

        version_container = QHBoxLayout()
        version_container.setSpacing(SPACING['small'])

        version_label = StrongBodyLabel("Version:")
        version_container.addWidget(version_label)

        git_sha = self.get_git_version()
        version_value = CaptionLabel(git_sha)
        version_value.setStyleSheet("color: {}; font-family: 'Courier New', monospace;".format(COLORS['text_secondary']))
        version_container.addWidget(version_value)

        bottom_layout.addLayout(version_container)
        bottom_layout.addStretch()

        reset_btn = PushButton("Reset All to Defaults", self.bottom_widget)
        reset_btn.setIcon(FluentIcon.CANCEL)
        reset_btn.clicked.connect(self.reset_to_defaults)
        bottom_layout.addWidget(reset_btn)

        self.expandLayout.addWidget(self.bottom_widget)

        for card in self.findChildren(SettingCard):
            card.setIconSize(18, 18)

    def _update_widget_value(self, widget, value):
        if widget is None:
            return
            
        if isinstance(widget, SwitchSettingCard):
            widget.switchButton.setChecked(value)
        elif isinstance(widget, (ComboBoxSettingCard, OptionsConfigItem)):
            widget.setValue(value)
        elif isinstance(widget, SpinBox):
            widget.setValue(value)
        elif isinstance(widget, LineEdit):
            widget.setText(value)
        elif isinstance(widget, PushSettingCard):
            widget.setContent(value or "Use temporary directory (default)")

    def create_build_output_group(self):
        group = SettingCardGroup("Build Output", self.scrollWidget)

        self.output_dir_card = PushSettingCard(
            "Browse",
            FluentIcon.FOLDER,
            "Output Directory",
            self.settings.get("build_output_directory", "") or "Use temporary directory (default)",
            group
        )
        self.output_dir_card.setObjectName("build_output_directory")
        self.output_dir_card.clicked.connect(self.browse_output_directory)
        group.addSettingCard(self.output_dir_card)

        self.open_folder_card = SwitchSettingCard(
            FluentIcon.FOLDER_ADD,
            "Open folder after build",
            "Automatically open the EFI build result folder when the build process completes successfully.",
            configItem=None,
            parent=group
        )
        self.open_folder_card.setObjectName("open_folder_after_build")
        self.open_folder_card.switchButton.setChecked(
            self.settings.get("open_folder_after_build", True))
        self.open_folder_card.switchButton.checkedChanged.connect(
            lambda checked: self.settings.set("open_folder_after_build", checked))
        group.addSettingCard(self.open_folder_card)

        return group

    def create_macos_version_group(self):
        group = SettingCardGroup("macOS Version", self.scrollWidget)

        self.include_beta_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            "Include beta version",
            "Show major beta macOS versions in version selection menus. Enable to test new macOS releases.",
            configItem=None,
            parent=group
        )
        self.include_beta_card.setObjectName("include_beta_versions")
        self.include_beta_card.switchButton.setChecked(self.settings.get("include_beta_versions", False))
        self.include_beta_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("include_beta_versions", checked))
        group.addSettingCard(self.include_beta_card)

        return group

    def create_bootargs_group(self):
        group = SettingCardGroup("Boot Arguments", self.scrollWidget)

        self.verbose_boot_card = SwitchSettingCard(
            FluentIcon.CODE,
            "Verbose boot (debug mode)",
            'Enables verbose boot with "-v debug=0x100 keepsyms=1" arguments for detailed boot logging and troubleshooting',
            configItem=None,
            parent=group
        )
        self.verbose_boot_card.setObjectName("verbose_boot")
        self.verbose_boot_card.switchButton.setChecked(self.settings.get("verbose_boot", True))
        self.verbose_boot_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("verbose_boot", checked))
        group.addSettingCard(self.verbose_boot_card)

        self.custom_boot_args_card = ExpandSettingCard(
            FluentIcon.COMMAND_PROMPT,
            "Additional Boot Arguments",
            "Add custom boot arguments (space-separated)",
            group
        )
        self.custom_boot_args_input = LineEdit(self)
        self.custom_boot_args_input.setObjectName("custom_boot_args")
        self.custom_boot_args_input.setPlaceholderText("e.g., -radcodec -raddvi")
        self.custom_boot_args_input.setText(self.settings.get("custom_boot_args", ""))
        self.custom_boot_args_input.textChanged.connect(lambda text: self.settings.set("custom_boot_args", text))
        self.custom_boot_args_input.setClearButtonEnabled(True)
        self.custom_boot_args_card.viewLayout.addWidget(self.custom_boot_args_input)
        group.addSettingCard(self.custom_boot_args_card)

        return group

    def create_boot_picker_group(self):
        group = SettingCardGroup("OpenCore Boot Picker", self.scrollWidget)

        self.show_picker_card = SwitchSettingCard(
            FluentIcon.MENU,
            "Show Picker",
            "Show the OpenCore Picker at startup, allowing you to choose between different boot entries.",
            configItem=None,
            parent=group
        )
        self.show_picker_card.setObjectName("show_picker")
        self.show_picker_card.switchButton.setChecked(self.settings.get("show_picker", True))
        self.show_picker_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("show_picker", checked))
        group.addSettingCard(self.show_picker_card)

        picker_mode_values = ["Builtin", "External"]
        picker_mode_value = self.settings.get("picker_mode", "External")
        if picker_mode_value not in picker_mode_values:
            picker_mode_value = "External"

        self.picker_mode_config = OptionsConfigItem(
            "BootPicker",
            "Mode",
            picker_mode_value,
            OptionsValidator(picker_mode_values)
        )
        self.picker_mode_config.valueChanged.connect(lambda value: self.settings.set("picker_mode", value))

        self.picker_mode_card = ComboBoxSettingCard(
            self.picker_mode_config,
            FluentIcon.APPLICATION,
            "Picker Mode",
            "Picker used for boot management: Builtin (text mode) or External (OpenCanopy GUI)",
            picker_mode_values,
            group
        )
        self.picker_mode_card.setObjectName("picker_mode")
        group.addSettingCard(self.picker_mode_card)

        self.hide_aux_card = SwitchSettingCard(
            FluentIcon.HIDE,
            "Hide auxiliary entries",
            "Hides auxiliary boot entries (Recovery, Reset NVRAM, Tools) from the boot picker for a cleaner interface",
            configItem=None,
            parent=group
        )
        self.hide_aux_card.setObjectName("hide_auxiliary")
        self.hide_aux_card.switchButton.setChecked(self.settings.get("hide_auxiliary", False))
        self.hide_aux_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("hide_auxiliary", checked))
        group.addSettingCard(self.hide_aux_card)

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
        self.picker_variant_config.valueChanged.connect(lambda value: self.settings.set("picker_variant", value))

        self.picker_variant_card = ComboBoxSettingCard(
            self.picker_variant_config,
            FluentIcon.PALETTE,
            "Picker Variant",
            "Choose specific icon set to be used for boot management. Requires External Picker mode.",
            picker_variant_values,
            group
        )
        self.picker_variant_card.setObjectName("picker_variant")
        group.addSettingCard(self.picker_variant_card)

        self.timeout_card = ExpandSettingCard(
            FluentIcon.HISTORY,
            "Timeout",
            "Timeout in seconds in the OpenCore picker before automatic booting of the default boot entry. Set to 0 to disable.",
            group
        )
        self.timeout_spin = SpinBox(self)
        self.timeout_spin.setObjectName("picker_timeout")
        self.timeout_spin.setRange(0, 60)
        self.timeout_spin.setValue(self.settings.get("picker_timeout", 5))
        self.timeout_spin.valueChanged.connect(lambda value: self.settings.set("picker_timeout", value))
        self.timeout_card.viewLayout.addWidget(self.timeout_spin)
        group.addSettingCard(self.timeout_card)

        return group

    def create_security_group(self):
        group = SettingCardGroup("Security Settings", self.scrollWidget)

        self.disable_sip_card = SwitchSettingCard(
            FluentIcon.SETTING,
            "Disable System Integrity Protection (SIP)",
            "Allowing unrestricted modifications and installation of software, kexts, and kernel patches. Required for OpenCore Legacy Patcher and other tools.",
            configItem=None,
            parent=group
        )
        self.disable_sip_card.setObjectName("disable_sip")
        self.disable_sip_card.switchButton.setChecked(self.settings.get("disable_sip", True))
        self.disable_sip_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("disable_sip", checked))
        group.addSettingCard(self.disable_sip_card)

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

        self.secure_boot_config = OptionsConfigItem(
            "Security",
            "SecureBootModel",
            secure_boot_value,
            OptionsValidator(secure_boot_values)
        )
        self.secure_boot_config.valueChanged.connect(lambda value: self.settings.set("secure_boot_model", value))

        self.secure_boot_card = ComboBoxSettingCard(
            self.secure_boot_config,
            FluentIcon.CERTIFICATE,
            "Secure Boot Model",
            "Sets Apple Secure Boot hardware model for security level: Default (based on SMBIOS board identifier), Disabled (Medium security), or specific value for Full security (e.g. j137, j680, etc.)",
            secure_boot_values,
            group
        )
        self.secure_boot_card.setObjectName("secure_boot_model")
        group.addSettingCard(self.secure_boot_card)

        return group

    def create_smbios_group(self):
        group = SettingCardGroup("SMBIOS Settings", self.scrollWidget)

        self.random_smbios_card = SwitchSettingCard(
            FluentIcon.SYNC,
            "Generate random SMBIOS",
            "Automatically generates new random serial numbers for each build to ensure unique system identifiers",
            configItem=None,
            parent=group
        )
        self.random_smbios_card.setObjectName("random_smbios")
        self.random_smbios_card.switchButton.setChecked(self.settings.get("random_smbios", True))
        self.random_smbios_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("random_smbios", checked))
        group.addSettingCard(self.random_smbios_card)

        self.preserve_smbios_card = SwitchSettingCard(
            FluentIcon.SAVE,
            "Preserve SMBIOS between builds",
            "Maintains the same SMBIOS values across multiple builds for consistency with iCloud and other services",
            configItem=None,
            parent=group
        )
        self.preserve_smbios_card.setObjectName("preserve_smbios")
        self.preserve_smbios_card.switchButton.setChecked(self.settings.get("preserve_smbios", False))
        self.preserve_smbios_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("preserve_smbios", checked))
        group.addSettingCard(self.preserve_smbios_card)

        return group

    def create_appearance_group(self):
        group = SettingCardGroup("Appearance", self.scrollWidget)

        theme_values = [
            "Light",
            "Dark",
        ]
        theme_value = self.settings.get("theme", "Light")
        if theme_value not in theme_values:
            theme_value = "Light"

        self.theme_config = OptionsConfigItem(
            "Appearance",
            "Theme",
            theme_value,
            OptionsValidator(theme_values)
        )

        def on_theme_changed(value):
            self.settings.set("theme", value)
            if value == "Dark":
                setTheme(Theme.DARK)
            else:
                setTheme(Theme.LIGHT)

        self.theme_config.valueChanged.connect(on_theme_changed)

        self.theme_card = ComboBoxSettingCard(
            self.theme_config,
            FluentIcon.BRUSH,
            "Theme",
            "Selects the application color theme.",
            theme_values,
            group
        )
        self.theme_card.setObjectName("theme")
        group.addSettingCard(self.theme_card)

        return group

    def create_update_settings_group(self):
        group = SettingCardGroup("Updates & Downloads", self.scrollWidget)

        self.auto_update_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            "Check for updates on startup",
            "Automatically checks for new OpCore Simplify updates when the application launches to keep you up to date",
            configItem=None,
            parent=group
        )
        self.auto_update_card.setObjectName("auto_update_check")
        self.auto_update_card.switchButton.setChecked(self.settings.get("auto_update_check", True))
        self.auto_update_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("auto_update_check", checked))
        group.addSettingCard(self.auto_update_card)

        return group

    def create_advanced_group(self):
        group = SettingCardGroup("Advanced Settings", self.scrollWidget)

        self.debug_logging_card = SwitchSettingCard(
            FluentIcon.DEVELOPER_TOOLS,
            "Enable debug logging",
            "Enables detailed debug logging throughout the application for advanced troubleshooting and diagnostics",
            configItem=None,
            parent=group
        )
        self.debug_logging_card.setObjectName("enable_debug_logging")
        self.debug_logging_card.switchButton.setChecked(self.settings.get("enable_debug_logging", False))
        self.debug_logging_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("enable_debug_logging", checked))
        group.addSettingCard(self.debug_logging_card)

        return group

    def create_help_group(self):
        group = SettingCardGroup("Help & Documentation", self.scrollWidget)

        self.opencore_docs_card = HyperlinkCard(
            "https://dortania.github.io/OpenCore-Install-Guide/",
            "OpenCore Install Guide",
            FluentIcon.BOOK_SHELF,
            "OpenCore Documentation",
            "Complete guide for installing macOS with OpenCore",
            group
        )
        group.addSettingCard(self.opencore_docs_card)

        self.troubleshoot_card = HyperlinkCard(
            "https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/troubleshooting.html",
            "Troubleshooting",
            FluentIcon.HELP,
            "Troubleshooting Guide",
            "Solutions to common OpenCore installation issues",
            group
        )
        group.addSettingCard(self.troubleshoot_card)

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
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Build Output Directory",
            self.settings.get("build_output_directory", "") or os.path.expanduser("~")
        )

        if folder:
            self.settings.set("build_output_directory", folder)
            self.output_dir_card.setContent(folder)
            self.controller.update_status("Output directory updated successfully", "success")

    def reset_to_defaults(self):
        result = show_question_dialog(
            self.controller,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?"
        )

        if result:
            self.settings.settings = self.settings.defaults.copy()
            self.settings.save_settings()

            for widget in self.findChildren(QWidget):
                key = widget.objectName()
                if key and key in self.settings.defaults:
                    default_value = self.settings.defaults.get(key)
                    self._update_widget_value(widget, default_value)

            self.controller.update_status("All settings reset to defaults", "success")

    def get_git_version(self):
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

            sha_version_file = os.path.join(script_dir, 'sha_version.txt')
            if os.path.exists(sha_version_file):
                with open(sha_version_file, 'r') as f:
                    version = f.read().strip()
                    if version:
                        return version
        except Exception:
            pass

        return "unknown"