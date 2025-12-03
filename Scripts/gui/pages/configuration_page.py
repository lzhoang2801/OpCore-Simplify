"""
Step 3: Configuration - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget,
    StrongBodyLabel, ComboBox, PrimaryPushButton
)

from ..styles import COLORS, SPACING


class ConfigurationPage(QWidget):
    """Step 3: Configuration options"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("configurationPage")
        self.controller = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the configuration page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])

        # Step indicator
        step_label = BodyLabel("STEP 3 OF 4")
        step_label.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(step_label)

        # Title
        title_label = SubtitleLabel("Configuration")
        layout.addWidget(title_label)

        subtitle_label = BodyLabel("Configure your OpenCore EFI settings")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(SPACING['large'])

        # Current configuration card
        config_card = CardWidget()
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                         SPACING['large'], SPACING['large'])

        card_title = StrongBodyLabel("Current Configuration")
        config_layout.addWidget(card_title)

        # macOS Version
        macos_layout = QHBoxLayout()
        macos_label = BodyLabel("macOS Version:")
        macos_layout.addWidget(macos_label)
        self.macos_value = BodyLabel("Not selected")
        self.macos_value.setStyleSheet("color: #605E5C;")
        macos_layout.addWidget(self.macos_value)
        macos_layout.addStretch()
        config_layout.addLayout(macos_layout)

        # SMBIOS Model
        smbios_layout = QHBoxLayout()
        smbios_label = BodyLabel("SMBIOS Model:")
        smbios_layout.addWidget(smbios_label)
        self.smbios_value = BodyLabel("Not selected")
        self.smbios_value.setStyleSheet("color: #605E5C;")
        smbios_layout.addWidget(self.smbios_value)
        smbios_layout.addStretch()
        config_layout.addLayout(smbios_layout)

        # Disabled Devices
        devices_layout = QHBoxLayout()
        devices_label = BodyLabel("Disabled Devices:")
        devices_layout.addWidget(devices_label)
        self.devices_value = BodyLabel("None")
        self.devices_value.setStyleSheet("color: #605E5C;")
        self.devices_value.setWordWrap(True)
        devices_layout.addWidget(self.devices_value)
        devices_layout.addStretch()
        config_layout.addLayout(devices_layout)

        layout.addWidget(config_card)

        # Customization options card
        custom_card = CardWidget()
        custom_layout = QVBoxLayout(custom_card)
        custom_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                         SPACING['large'], SPACING['large'])

        custom_title = StrongBodyLabel("Customization Options")
        custom_layout.addWidget(custom_title)

        # ACPI Patches button
        self.acpi_btn = PushButton("Customize ACPI Patches")
        self.acpi_btn.clicked.connect(self.customize_acpi)
        custom_layout.addWidget(self.acpi_btn)

        # Kexts button
        self.kexts_btn = PushButton("Customize Kexts")
        self.kexts_btn.clicked.connect(self.customize_kexts)
        custom_layout.addWidget(self.kexts_btn)

        # SMBIOS button
        self.smbios_btn = PushButton("Customize SMBIOS Model")
        self.smbios_btn.clicked.connect(self.customize_smbios)
        custom_layout.addWidget(self.smbios_btn)

        layout.addWidget(custom_card)
        layout.addStretch()

    def customize_acpi(self):
        """Customize ACPI patches"""
        # This would open a dialog or navigate to ACPI customization
        self.controller.update_status(
            "ACPI customization not yet implemented in GUI", 'info')

    def customize_kexts(self):
        """Customize kexts"""
        self.controller.update_status(
            "Kext customization not yet implemented in GUI", 'info')

    def customize_smbios(self):
        """Customize SMBIOS model"""
        self.controller.update_status(
            "SMBIOS customization not yet implemented in GUI", 'info')

    def update_display(self):
        """Update configuration display"""
        self.macos_value.setText(self.controller.macos_version_text)
        self.smbios_value.setText(self.controller.smbios_model_text)
        self.devices_value.setText(self.controller.disabled_devices_text)

    def refresh(self):
        """Refresh page content"""
        self.update_display()
