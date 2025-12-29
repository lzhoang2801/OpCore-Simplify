import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ScrollArea, BodyLabel, PushButton, LineEdit, FluentIcon,
    SettingCardGroup, SwitchSettingCard, ComboBoxSettingCard,
    PushSettingCard, SpinBox,
    OptionsConfigItem, OptionsValidator, HyperlinkCard,
    StrongBodyLabel, CaptionLabel, SettingCard, SubtitleLabel,
    setTheme, Theme
)

from Scripts.custom_dialogs import show_confirmation
from Scripts.styles import COLORS, SPACING


class SettingsPage(ScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.settings = self.controller.backend.settings
        
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.enableTransparentBackground()
        
        self._init_ui()

    def _init_ui(self):
        self.expandLayout.setContentsMargins(SPACING["xxlarge"], SPACING["xlarge"], SPACING["xxlarge"], SPACING["xlarge"])
        self.expandLayout.setSpacing(SPACING["large"])

        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING["tiny"])

        title_label = SubtitleLabel("Settings")
        header_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Configure OpCore Simplify preferences")
        subtitle_label.setStyleSheet("color: {};".format(COLORS["text_secondary"]))
        header_layout.addWidget(subtitle_label)

        self.expandLayout.addWidget(header_container)
        self.expandLayout.addSpacing(SPACING["medium"])

        self.build_output_group = self.create_build_output_group()
        self.expandLayout.addWidget(self.build_output_group)

        self.macos_group = self.create_macos_version_group()
        self.expandLayout.addWidget(self.macos_group)

        #self.appearance_group = self.create_appearance_group()
        #self.expandLayout.addWidget(self.appearance_group)

        self.update_group = self.create_update_settings_group()
        self.expandLayout.addWidget(self.update_group)

        self.advanced_group = self.create_advanced_group()
        self.expandLayout.addWidget(self.advanced_group)

        self.help_group = self.create_help_group()
        self.expandLayout.addWidget(self.help_group)
        
        self.bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(self.bottom_widget)
        bottom_layout.setContentsMargins(0, SPACING["large"], 0, SPACING["large"])
        bottom_layout.setSpacing(SPACING["medium"])

        version_container = QHBoxLayout()
        version_container.setSpacing(SPACING["small"])

        version_label = StrongBodyLabel("Version:")
        version_container.addWidget(version_label)

        git_sha = self.get_git_version()
        version_value = CaptionLabel(git_sha)
        version_value.setStyleSheet("color: {}; font-family: \"Courier New\", monospace;".format(COLORS["text_secondary"]))
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
            self.settings.get("build_output_directory") or "Use temporary directory (default)",
            group
        )
        self.output_dir_card.setObjectName("build_output_directory")
        self.output_dir_card.clicked.connect(self.browse_output_directory)
        group.addSettingCard(self.output_dir_card)

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
        self.include_beta_card.switchButton.setChecked(self.settings.get_include_beta_versions())
        self.include_beta_card.switchButton.checkedChanged.connect(lambda checked: self.settings.set("include_beta_versions", checked))
        group.addSettingCard(self.include_beta_card)

        return group

    def create_appearance_group(self):
        group = SettingCardGroup("Appearance", self.scrollWidget)

        theme_values = [
            "Light",
            #"Dark",
        ]
        theme_value = self.settings.get_theme()
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
        self.auto_update_card.switchButton.setChecked(self.settings.get_auto_update_check())
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
        self.debug_logging_card.switchButton.setChecked(self.settings.get_enable_debug_logging())
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
            os.path.expanduser("~")
        )

        if folder:
            self.settings.set("build_output_directory", folder)
            self.output_dir_card.setContent(folder)
            self.controller.update_status("Output directory updated successfully", "success")

    def reset_to_defaults(self):
        result = show_confirmation("Reset Settings", "Are you sure you want to reset all settings to their default values?")

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
            main_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            sha_version_file = os.path.join(main_dir, "sha_version.txt")
            if os.path.exists(sha_version_file):
                with open(sha_version_file, "r") as f:
                    version = f.read().strip()
                    if version:
                        return version
        except Exception:
            pass

        return "unknown"