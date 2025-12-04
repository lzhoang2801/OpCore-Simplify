"""
Step 3: Configuration - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget,
    StrongBodyLabel, ComboBox, PrimaryPushButton, FluentIcon,
    GroupHeaderCardWidget
)

from ..styles import COLORS, SPACING


def add_group_with_indent(card, icon, title, content, widget=None, indent_level=0):
    """
    Add a group to a GroupHeaderCardWidget with optional indentation.
    This pattern is consistent with compatibility_page.py.

    Args:
        card: The GroupHeaderCardWidget instance
        icon: Icon for the group
        title: Title text
        content: Content/description text
        widget: Widget to add (default: new empty QWidget)
        indent_level: 0 for main items, 1+ for child items (each level adds 20px left margin)

    Returns:
        The created CardGroupWidget
    """
    if widget is None:
        widget = QWidget()  # Create new instance each time

    group = card.addGroup(icon, title, content, widget)

    # Apply indentation if needed
    if indent_level > 0:
        # Get the horizontal layout (hBoxLayout) and adjust left margin
        # Default margins are (24, 10, 24, 10) - left, top, right, bottom
        base_margin = 24
        indent = 20 * indent_level
        group.hBoxLayout.setContentsMargins(base_margin + indent, 10, 24, 10)

    return group


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

        # Cards layout - directly in main layout without scroll area container
        self.cards_layout = main_layout
        
        # Track the position where cards should be inserted (after header)
        self.cards_start_index = main_layout.count()
        
        # Store reference to configuration card for dynamic updates
        self.config_card = None
        self._build_config_card()

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
            FluentIcon.CODE,
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
            FluentIcon.TAG,
            "SMBIOS Model",
            "Choose the Mac model your system will identify as",
            smbios_btn_widget
        )

        self.cards_layout.addWidget(custom_card)
        self.cards_layout.addStretch()

    def _build_config_card(self):
        """Build or rebuild the configuration card with current data"""
        # Remove old card if it exists
        if self.config_card is not None:
            self.cards_layout.removeWidget(self.config_card)
            self.config_card.deleteLater()
        
        # Create new configuration card
        self.config_card = GroupHeaderCardWidget("Current Configuration", self)
        
        # macOS Version group
        macos_widget = QWidget()
        macos_widget_layout = QHBoxLayout(macos_widget)
        macos_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.macos_value = BodyLabel(self.controller.macos_version_text if hasattr(self.controller, 'macos_version_text') else "Not selected")
        self.macos_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        macos_widget_layout.addWidget(self.macos_value)
        macos_widget_layout.addStretch()
        
        self.config_card.addGroup(
            FluentIcon.GLOBE,
            "macOS Version",
            "Target operating system version",
            macos_widget
        )

        # SMBIOS Model group
        smbios_widget = QWidget()
        smbios_widget_layout = QHBoxLayout(smbios_widget)
        smbios_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.smbios_value = BodyLabel(self.controller.smbios_model_text if hasattr(self.controller, 'smbios_model_text') else "Not selected")
        self.smbios_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
        smbios_widget_layout.addWidget(self.smbios_value)
        smbios_widget_layout.addStretch()
        
        self.config_card.addGroup(
            FluentIcon.TAG,
            "SMBIOS Model",
            "System identifier for macOS",
            smbios_widget
        )

        # Disabled Devices - display each device vertically
        disabled_devices = self.controller.disabled_devices if hasattr(self.controller, 'disabled_devices') and self.controller.disabled_devices is not None else {}
        
        if disabled_devices:
            # Add header for disabled devices section
            header_widget = QWidget()
            header_layout = QVBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_label = BodyLabel("Hardware components excluded from configuration")
            header_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            header_layout.addWidget(header_label)
            
            self.config_card.addGroup(
                FluentIcon.CANCEL,
                "Disabled Devices",
                "",
                header_widget
            )
            
            # Add each disabled device as a separate indented group
            for device_name in disabled_devices.keys():
                add_group_with_indent(
                    self.config_card,
                    FluentIcon.INFO,
                    device_name,
                    "",
                    None,  # No custom widget needed
                    indent_level=1
                )
        else:
            # No disabled devices - show success message
            none_widget = QWidget()
            none_layout = QVBoxLayout(none_widget)
            none_layout.setContentsMargins(0, 0, 0, 0)
            none_label = BodyLabel("All hardware components are compatible and enabled")
            none_label.setStyleSheet(f"color: {COLORS['success']};")
            none_layout.addWidget(none_label)
            
            self.config_card.addGroup(
                FluentIcon.ACCEPT,
                "Disabled Devices",
                "",
                none_widget
            )
        
        # Insert the card at the tracked position (after header, before other cards)
        self.cards_layout.insertWidget(self.cards_start_index, self.config_card)

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
        """Update configuration display by rebuilding the config card"""
        self._build_config_card()

    def refresh(self):
        """Refresh page content"""
        self.update_display()
