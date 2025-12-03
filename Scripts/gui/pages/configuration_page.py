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

        # macOS Version button
        self.macos_btn = PushButton("Select macOS Version")
        self.macos_btn.clicked.connect(self.select_macos)
        custom_layout.addWidget(self.macos_btn)

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

    def select_macos(self):
        """Select macOS version"""
        # This would open a dialog or navigate to ACPI customization
        self.controller.update_status(
            "Select macOS version is not yet implemented in GUI", 'info')

    def customize_acpi(self):
        """Customize ACPI patches"""
        # Check if hardware report is loaded
        if not self.controller.customized_hardware:
            self.controller.update_status(
                "Please load a hardware report first", 'warning')
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
        if not self.controller.customized_hardware:
            self.controller.update_status(
                "Please load a hardware report first", 'warning')
            return

        # Import the kexts dialog
        from ..custom_dialogs import show_kexts_dialog

        # Show the kexts dialog (macos_version is in Darwin kernel version format, e.g., "22.0.0")
        ok = show_kexts_dialog(
            self.controller,
            self.controller.ocpe.k,
            self.controller.macos_version
        )

        if ok:
            self.controller.update_status(
                "Kext configuration updated successfully", 'success')

    def customize_smbios(self):
        """Customize SMBIOS model"""
        # Check if hardware report is loaded
        if not self.controller.customized_hardware:
            self.controller.update_status(
                "Please load a hardware report first", 'warning')
            return

        # Import required modules
        from ...datasets.mac_model_data import mac_devices
        from ..custom_dialogs import show_smbios_dialog

        # Get current state
        current_model = self.controller.smbios_model_text
        default_model = self.controller.ocpe.s.select_smbios_model(
            self.controller.customized_hardware,
            self.controller.macos_version  # Use Darwin version
        )
        is_laptop = "Laptop" == self.controller.customized_hardware.get("Motherboard").get("Platform")

        # Show SMBIOS selection dialog
        selected_model, ok = show_smbios_dialog(
            self.controller,
            mac_devices,
            current_model,
            default_model,
            self.controller.macos_version,  # Use Darwin version
            is_laptop,
            self.controller.ocpe.u
        )

        if ok and selected_model != current_model:
            # Update the selected SMBIOS model
            self.controller.smbios_model_text = selected_model

            # Apply SMBIOS-specific options
            self.controller.ocpe.s.smbios_specific_options(
                self.controller.customized_hardware,
                selected_model,
                self.controller.macos_version,  # Use Darwin version
                self.controller.ocpe.ac.patches,
                self.controller.ocpe.k
            )

            # Update display
            self.update_display()
            self.controller.update_status(
                f"SMBIOS model updated to {selected_model}", 'success')

    def update_display(self):
        """Update configuration display"""
        self.macos_value.setText(self.controller.macos_version_text)
        self.smbios_value.setText(self.controller.smbios_model_text)
        self.devices_value.setText(self.controller.disabled_devices_text)

    def refresh(self):
        """Refresh page content"""
        self.update_display()
