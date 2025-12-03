"""
Step 3: Configuration - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget,
    StrongBodyLabel, ComboBox, PrimaryPushButton, FluentIcon,
    IconWidget, GroupHeaderCardWidget, ToolTip, InfoBadge,
    InfoBadgePosition, ScrollArea
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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                       SPACING['xxlarge'], SPACING['xlarge'])
        main_layout.setSpacing(SPACING['large'])

        # Step indicator
        step_label = BodyLabel("STEP 3 OF 4")
        step_label.setStyleSheet("color: #0078D4; font-weight: bold;")
        main_layout.addWidget(step_label)

        # Header section with title and description
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Configuration")
        header_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Configure your OpenCore EFI settings")
        subtitle_label.setStyleSheet("color: #605E5C;")
        header_layout.addWidget(subtitle_label)

        main_layout.addWidget(header_container)
        main_layout.addSpacing(SPACING['medium'])

        # Scrollable area for configuration cards
        scroll_area = ScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("configurationScrollArea")

        # Container widget for scroll area
        container = QWidget()
        self.cards_layout = QVBoxLayout(container)
        self.cards_layout.setSpacing(SPACING['medium'])
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        # Current Configuration Card using GroupHeaderCardWidget
        config_card = GroupHeaderCardWidget("Current Configuration", self)
        
        # macOS Version group
        macos_widget = QWidget()
        macos_widget_layout = QHBoxLayout(macos_widget)
        macos_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.macos_value = BodyLabel("Not selected")
        self.macos_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        macos_widget_layout.addWidget(self.macos_value)
        macos_widget_layout.addStretch()
        
        config_card.addGroup(
            FluentIcon.GLOBE,
            "macOS Version",
            "Target operating system version",
            macos_widget
        )

        # SMBIOS Model group
        smbios_widget = QWidget()
        smbios_widget_layout = QHBoxLayout(smbios_widget)
        smbios_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.smbios_value = BodyLabel("Not selected")
        self.smbios_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        smbios_widget_layout.addWidget(self.smbios_value)
        smbios_widget_layout.addStretch()
        
        config_card.addGroup(
            FluentIcon.TAG,
            "SMBIOS Model",
            "System identifier for macOS",
            smbios_widget
        )

        # Disabled Devices group
        devices_widget = QWidget()
        devices_widget_layout = QVBoxLayout(devices_widget)
        devices_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.devices_value = BodyLabel("None")
        self.devices_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.devices_value.setWordWrap(True)
        devices_widget_layout.addWidget(self.devices_value)
        
        config_card.addGroup(
            FluentIcon.CANCEL,
            "Disabled Devices",
            "Hardware components excluded from configuration",
            devices_widget
        )

        self.cards_layout.addWidget(config_card)

        # Customization Options Card using GroupHeaderCardWidget
        custom_card = GroupHeaderCardWidget("Customization Options", self)

        # macOS Version customization
        macos_btn_widget = QWidget()
        macos_btn_layout = QVBoxLayout(macos_btn_widget)
        macos_btn_layout.setContentsMargins(0, 0, 0, 0)
        macos_btn_layout.setSpacing(SPACING['small'])
        
        self.macos_btn = PushButton(FluentIcon.GLOBE, "Select Version")
        self.macos_btn.clicked.connect(self.select_macos)
        self.macos_btn.setFixedWidth(180)
        macos_btn_layout.addWidget(self.macos_btn)
        
        custom_card.addGroup(
            FluentIcon.SETTING,
            "macOS Version",
            "Choose your target macOS version for optimal compatibility",
            macos_btn_widget
        )

        # ACPI Patches customization
        acpi_btn_widget = QWidget()
        acpi_btn_layout = QVBoxLayout(acpi_btn_widget)
        acpi_btn_layout.setContentsMargins(0, 0, 0, 0)
        acpi_btn_layout.setSpacing(SPACING['small'])
        
        self.acpi_btn = PushButton(FluentIcon.CODE, "Configure Patches")
        self.acpi_btn.clicked.connect(self.customize_acpi)
        self.acpi_btn.setFixedWidth(180)
        acpi_btn_layout.addWidget(self.acpi_btn)
        
        custom_card.addGroup(
            FluentIcon.DEVELOPER_TOOLS,
            "ACPI Patches",
            "Customize system ACPI table modifications for hardware compatibility",
            acpi_btn_widget
        )

        # Kexts customization
        kexts_btn_widget = QWidget()
        kexts_btn_layout = QVBoxLayout(kexts_btn_widget)
        kexts_btn_layout.setContentsMargins(0, 0, 0, 0)
        kexts_btn_layout.setSpacing(SPACING['small'])
        
        self.kexts_btn = PushButton(FluentIcon.LIBRARY, "Manage Kexts")
        self.kexts_btn.clicked.connect(self.customize_kexts)
        self.kexts_btn.setFixedWidth(180)
        kexts_btn_layout.addWidget(self.kexts_btn)
        
        custom_card.addGroup(
            FluentIcon.GRID,
            "Kernel Extensions",
            "Configure kexts (drivers) required for your hardware",
            kexts_btn_widget
        )

        # SMBIOS customization
        smbios_btn_widget = QWidget()
        smbios_btn_layout = QVBoxLayout(smbios_btn_widget)
        smbios_btn_layout.setContentsMargins(0, 0, 0, 0)
        smbios_btn_layout.setSpacing(SPACING['small'])
        
        self.smbios_btn = PushButton(FluentIcon.TAG, "Select Model")
        self.smbios_btn.clicked.connect(self.customize_smbios)
        self.smbios_btn.setFixedWidth(180)
        smbios_btn_layout.addWidget(self.smbios_btn)
        
        custom_card.addGroup(
            FluentIcon.COMPUTER,
            "SMBIOS Model",
            "Choose the Mac model your system will identify as",
            smbios_btn_widget
        )

        self.cards_layout.addWidget(custom_card)
        self.cards_layout.addStretch()

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    def select_macos(self):
        """Select macOS version"""
        # Check if hardware report is loaded
        if not self.controller.hardware_report:
            self.controller.update_status(
                "Please load a hardware report first", 'warning')
            return

        # Import the macOS version dialog
        from ..custom_dialogs import show_macos_version_dialog

        # Show the macOS version selection dialog
        selected_version, ok = show_macos_version_dialog(
            self.controller,
            self.controller.hardware_report,
            self.controller.native_macos_version,
            self.controller.ocl_patched_macos_version,
            self.controller.ocpe.u
        )

        if ok and selected_version:
            # Apply the selected macOS version
            self.controller.apply_macos_version(selected_version)
            self.controller.update_status(
                f"macOS version updated to {self.controller.macos_version_text}", 'success')

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
