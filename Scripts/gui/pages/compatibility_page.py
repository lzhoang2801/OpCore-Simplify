"""
Step 2: Compatibility checker - qfluentwidgets version
"""
from ...datasets import os_data, pci_data
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ScrollArea, FluentIcon, IconWidget, GroupHeaderCardWidget,
    TitleLabel, setFont
)

from ..styles import COLORS, SPACING

# Import os_data and pci_data for version names and device checks
import sys
import os
from pathlib import Path

# Add Scripts directory to path for dataset imports
scripts_path = Path(__file__).parent.parent.parent
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Create a reusable empty widget instance - REMOVED as it can cause layout issues
# Each addGroup call should get its own QWidget instance


def create_info_widget(text, color=None):
    """Create a simple label widget for displaying information"""
    if not text:
        # Return new empty widget if no text (don't reuse)
        return QWidget()
    label = BodyLabel(text)
    label.setWordWrap(True)
    if color:
        label.setStyleSheet(f"color: {color};")
    return label


def add_group_with_indent(card, icon, title, content, widget=None, indent_level=0):
    """
    Add a group to a GroupHeaderCardWidget with optional indentation.

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


def get_compatibility_icon(compat_tuple):
    """
    Get the appropriate FluentIcon based on compatibility status.

    Args:
        compat_tuple: Compatibility tuple (max_version, min_version) or (None, None)

    Returns:
        FluentIcon: ACCEPT for supported, CANCEL for unsupported
    """
    if not compat_tuple or compat_tuple == (None, None):
        return FluentIcon.CANCEL  # Unsupported
    return FluentIcon.ACCEPT  # Supported


class CompatibilityPage(ScrollArea):
    """Step 2: View hardware compatibility"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("compatibilityPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout()
        # Explicitly set the layout on the scroll widget to ensure proper display
        self.scrollWidget.setLayout(self.expandLayout)
        self.setup_ui()

    def setup_ui(self):
        """Setup the compatibility page UI"""
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # Enable transparent background for proper styling
        self.enableTransparentBackground()

        # Initialize layout for compatibility cards
        self.__initLayout()

    def __initLayout(self):
        """Initialize the expand layout with compatibility cards"""
        # Set layout spacing and margins
        self.expandLayout.setSpacing(SPACING['large'])
        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])

        # Step indicator
        step_label = BodyLabel("STEP 2 OF 4")
        step_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        self.expandLayout.addWidget(step_label)

        # Header section with title and description
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Hardware Compatibility")
        header_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Review hardware compatibility with macOS")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        header_layout.addWidget(subtitle_label)

        self.expandLayout.addWidget(header_container)
        self.expandLayout.addSpacing(SPACING['large'])

        # macOS version support card - positioned at the top of content area
        self.macos_version_card = CardWidget(self.scrollWidget)
        self.macos_version_card.setFixedWidth(320)
        self.macos_version_card.setVisible(
            False)  # Hidden until data is loaded

        version_card_layout = QVBoxLayout(self.macos_version_card)
        version_card_layout.setContentsMargins(SPACING['medium'], SPACING['medium'],
                                               SPACING['medium'], SPACING['medium'])
        version_card_layout.setSpacing(SPACING['small'])

        self.version_card_title = StrongBodyLabel("macOS Version Support")
        self.version_card_title.setStyleSheet(
            f"color: {COLORS['primary']}; font-size: 14px;")
        version_card_layout.addWidget(self.version_card_title)

        self.version_card_content = QVBoxLayout()
        self.version_card_content.setSpacing(SPACING['small'])
        version_card_layout.addLayout(self.version_card_content)

        self.expandLayout.addWidget(self.macos_version_card)

        # Placeholder message (will be replaced when hardware report is loaded)
        self.placeholder_label = BodyLabel(
            "Load a hardware report to see compatibility information")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
        self.expandLayout.addWidget(self.placeholder_label)

    def update_macos_version_card(self):
        """Update the macOS version support card in the header"""
        # Clear existing content (widgets and spacers)
        while self.version_card_content.count() > 0:
            item = self.version_card_content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.controller.native_macos_version:
            self.macos_version_card.setVisible(False)
            return

        # Show the card
        self.macos_version_card.setVisible(True)

        def create_support_row(title, version_text, icon, color):
            """Compact row with icon, label, and value to keep card minimal"""
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING['small'])

            icon_widget = IconWidget(icon)
            icon_widget.setFixedSize(18, 18)
            row_layout.addWidget(icon_widget)

            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(0)

            title_label = BodyLabel(title)
            title_label.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-weight: 500;")
            text_layout.addWidget(title_label)

            value_label = StrongBodyLabel(version_text)
            value_label.setStyleSheet(f"color: {color}; font-size: 13px;")
            value_label.setWordWrap(True)
            text_layout.addWidget(value_label)

            row_layout.addLayout(text_layout)
            row_layout.addStretch()
            return row_widget

        # native_macos_version tuple format: (min_version, max_version)
        # Index [0] = earliest supported version
        # Index [-1] = latest supported version
        min_ver_name = os_data.get_macos_name_by_darwin(
            self.controller.native_macos_version[0])
        max_ver_name = os_data.get_macos_name_by_darwin(
            self.controller.native_macos_version[-1])

        native_range = min_ver_name if min_ver_name == max_ver_name else f"{min_ver_name} to {max_ver_name}"
        self.version_card_content.addWidget(
            create_support_row("Native Support", native_range,
                               FluentIcon.ACCEPT, COLORS['success'])
        )

        # Add OCLP info if available
        if self.controller.ocl_patched_macos_version:
            self.version_card_content.addSpacing(SPACING['small'])

            # ocl_patched_macos_version tuple format: (max_version, min_version)
            # Index [0] = latest supported version
            # Index [-1] = earliest supported version
            oclp_max_name = os_data.get_macos_name_by_darwin(
                self.controller.ocl_patched_macos_version[0])
            oclp_min_name = os_data.get_macos_name_by_darwin(
                self.controller.ocl_patched_macos_version[-1])
            oclp_range = oclp_min_name if oclp_min_name == oclp_max_name else f"{oclp_min_name} to {oclp_max_name}"
            self.version_card_content.addWidget(
                create_support_row("OCLP Extended", oclp_range,
                                   FluentIcon.IOT, COLORS['primary'])
            )

    def format_compatibility(self, compat_tuple):
        """
        Format compatibility tuple to readable string with color.

        Note: Device compatibility tuples have format (max_version, min_version)
        where index [0] is the highest/latest version and [-1] is the lowest/earliest.
        """
        if not compat_tuple or compat_tuple == (None, None):
            return "Unsupported", "#D13438"  # Red

        max_ver, min_ver = compat_tuple  # First element is max, second is min

        if max_ver and min_ver:
            max_name = os_data.get_macos_name_by_darwin(max_ver)
            min_name = os_data.get_macos_name_by_darwin(min_ver)

            if max_name == min_name:
                return f"Up to {max_name}", "#0078D4"  # Blue
            else:
                # Display as min to max (earliest to latest) for user clarity
                return f"{min_name} to {max_name}", "#107C10"  # Green

        return "Unknown", "#605E5C"  # Gray

    def update_display(self):
        """Update compatibility display with GroupHeaderCardWidget for better organization"""
        # Clear existing cards (except the macOS version card which should be the first widget)
        # Collect all widgets to remove (keeping track of which to preserve)
        widgets_to_remove = []

        for i in range(self.expandLayout.count()):
            item = self.expandLayout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                # Keep the macOS version card, remove everything else
                if widget != self.macos_version_card:
                    widgets_to_remove.append(widget)

        # Now remove all the widgets we identified
        for widget in widgets_to_remove:
            self.expandLayout.removeWidget(widget)
            widget.deleteLater()

        if not self.controller.hardware_report:
            self.placeholder_label = BodyLabel(
                "Load a hardware report to see compatibility information")
            self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.placeholder_label.setStyleSheet(
                "color: #605E5C; padding: 40px;")
            self.expandLayout.addWidget(self.placeholder_label)
            return

        report = self.controller.hardware_report
        cards_added = 0  # Track if any cards were created

        # CPU Card
        if 'CPU' in report:
            cpu_card = GroupHeaderCardWidget(self.scrollWidget)
            cpu_card.setTitle("CPU")
            cpu_info = report['CPU']

            if isinstance(cpu_info, dict):
                # Processor Name group (main item - no indent)
                name = cpu_info.get('Processor Name', 'Unknown')
                add_group_with_indent(
                    cpu_card,
                    FluentIcon.TAG,
                    "Processor",
                    name,
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = cpu_info.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                add_group_with_indent(
                    cpu_card,
                    get_compatibility_icon(compat),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )

                # Additional details group if available (child item - indent level 1)
                details = []
                if cpu_info.get('Codename'):
                    details.append(f"Codename: {cpu_info.get('Codename')}")
                if cpu_info.get('Core Count'):
                    details.append(f"Cores: {cpu_info.get('Core Count')}")

                if details:
                    add_group_with_indent(
                        cpu_card,
                        FluentIcon.INFO,
                        "Details",
                        " • ".join(details),
                        indent_level=1
                    )

            self.expandLayout.addWidget(cpu_card)
            cards_added += 1

        # GPU Card
        if 'GPU' in report and report['GPU']:
            gpu_card = GroupHeaderCardWidget(self.scrollWidget)
            gpu_card.setTitle("Graphics")

            for idx, (gpu_name, gpu_info) in enumerate(report['GPU'].items()):
                # GPU Name and Type group (main item - no indent)
                device_type = gpu_info.get('Device Type', 'Unknown')
                add_group_with_indent(
                    gpu_card,
                    FluentIcon.PHOTO,
                    gpu_name,
                    f"Type: {device_type}",
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = gpu_info.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                add_group_with_indent(
                    gpu_card,
                    get_compatibility_icon(compat),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )

                # OCLP Compatibility if available (child item - indent level 1)
                if 'OCLP Compatibility' in gpu_info:
                    oclp_compat = gpu_info.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(
                        oclp_compat)
                    add_group_with_indent(
                        gpu_card,
                        FluentIcon.IOT,
                        "OCLP Compatibility",
                        oclp_text,
                        create_info_widget(
                            "Extended support with OpenCore Legacy Patcher", COLORS['text_secondary']),
                        indent_level=1
                    )

                # Connected monitors (child item - indent level 1)
                if 'Monitor' in report:
                    connected_monitors = []
                    for monitor_name, monitor_info in report['Monitor'].items():
                        if monitor_info.get('Connected GPU') == gpu_name:
                            connector = monitor_info.get(
                                'Connector Type', 'Unknown')
                            connected_monitors.append(
                                f"{monitor_name} ({connector})")

                    if connected_monitors:
                        add_group_with_indent(
                            gpu_card,
                            FluentIcon.VIEW,
                            "Connected Displays",
                            ", ".join(connected_monitors),
                            indent_level=1
                        )

            self.expandLayout.addWidget(gpu_card)
            cards_added += 1

        # Sound Card
        if 'Sound' in report and report['Sound']:
            sound_card = GroupHeaderCardWidget(self.scrollWidget)
            sound_card.setTitle("Audio")

            for audio_device, audio_props in report['Sound'].items():
                # Audio Device group (main item - no indent)
                add_group_with_indent(
                    sound_card,
                    FluentIcon.MUSIC,
                    audio_device,
                    "",
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = audio_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                add_group_with_indent(
                    sound_card,
                    get_compatibility_icon(compat),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )

                # Audio endpoints (child item - indent level 1)
                endpoints = audio_props.get('Audio Endpoints', [])
                if endpoints:
                    add_group_with_indent(
                        sound_card,
                        FluentIcon.HEADPHONE,
                        "Audio Endpoints",
                        ", ".join(endpoints),
                        indent_level=1
                    )

            self.expandLayout.addWidget(sound_card)
            cards_added += 1

        # Network Card
        if 'Network' in report and report['Network']:
            network_card = GroupHeaderCardWidget(self.scrollWidget)
            network_card.setTitle("Network")

            for device_name, device_props in report['Network'].items():
                # Network Device group (main item - no indent)
                add_group_with_indent(
                    network_card,
                    FluentIcon.WIFI,
                    device_name,
                    "",
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = device_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                add_group_with_indent(
                    network_card,
                    get_compatibility_icon(compat),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )

                # OCLP Compatibility if available (child item - indent level 1)
                if 'OCLP Compatibility' in device_props:
                    oclp_compat = device_props.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(
                        oclp_compat)
                    add_group_with_indent(
                        network_card,
                        FluentIcon.IOT,
                        "OCLP Compatibility",
                        oclp_text,
                        create_info_widget(
                            "Extended support with OpenCore Legacy Patcher", COLORS['text_secondary']),
                        indent_level=1
                    )

                # Continuity support information (child item - indent level 1)
                device_id = device_props.get('Device ID', '')
                if device_id:
                    continuity_info = ""
                    continuity_color = COLORS['text_secondary']

                    if device_id in pci_data.BroadcomWiFiIDs:
                        continuity_info = "Full support (AirDrop, Handoff, etc.)"
                        continuity_color = COLORS['success']
                    elif device_id in pci_data.IntelWiFiIDs:
                        continuity_info = "Partial (Handoff with AirportItlwm) - AirDrop, Instant Hotspot not available"
                        continuity_color = COLORS['warning']
                    elif device_id in pci_data.AtherosWiFiIDs:
                        continuity_info = "Limited support"
                        continuity_color = COLORS['error']

                    if continuity_info:
                        add_group_with_indent(
                            network_card,
                            FluentIcon.SYNC,
                            "Continuity Features",
                            continuity_info,
                            create_info_widget("", continuity_color),
                            indent_level=1
                        )

            self.expandLayout.addWidget(network_card)
            cards_added += 1

        # Storage Controllers Card
        if 'Storage Controllers' in report and report['Storage Controllers']:
            storage_card = GroupHeaderCardWidget(self.scrollWidget)
            storage_card.setTitle("Storage")

            for controller_name, controller_props in report['Storage Controllers'].items():
                # Storage Controller group (main item - no indent)
                add_group_with_indent(
                    storage_card,
                    FluentIcon.FOLDER,
                    controller_name,
                    "",
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = controller_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                add_group_with_indent(
                    storage_card,
                    get_compatibility_icon(compat),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )

            self.expandLayout.addWidget(storage_card)
            cards_added += 1

        # Bluetooth Card
        if 'Bluetooth' in report and report['Bluetooth']:
            bluetooth_card = GroupHeaderCardWidget(self.scrollWidget)
            bluetooth_card.setTitle("Bluetooth")

            for bluetooth_name, bluetooth_props in report['Bluetooth'].items():
                # Bluetooth Device group (main item - no indent)
                add_group_with_indent(
                    bluetooth_card,
                    FluentIcon.BLUETOOTH,
                    bluetooth_name,
                    "",
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = bluetooth_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                add_group_with_indent(
                    bluetooth_card,
                    get_compatibility_icon(compat),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )

            self.expandLayout.addWidget(bluetooth_card)
            cards_added += 1

        # Biometric Card (if exists)
        if 'Biometric' in report and report['Biometric']:
            bio_card = GroupHeaderCardWidget(self.scrollWidget)
            bio_card.setTitle("Biometric")

            for bio_device, bio_props in report['Biometric'].items():
                # Biometric Device group (main item - no indent)
                add_group_with_indent(
                    bio_card,
                    FluentIcon.FINGERPRINT,
                    bio_device,
                    "Unsupported",
                    indent_level=0
                )

                # Compatibility group (child item - indent level 1)
                compat = bio_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                warning_message = "\n".join([
                    "⚠️ Biometric authentication requires Apple T2 Chip",
                    "Not available for Hackintosh systems"
                ])
                add_group_with_indent(
                    bio_card,
                    FluentIcon.MEGAPHONE,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget(warning_message, COLORS['warning']),
                    indent_level=1
                )

            self.expandLayout.addWidget(bio_card)
            cards_added += 1

        # If no cards were added, show a message
        if cards_added == 0:
            no_data_label = BodyLabel(
                "No compatible hardware information found in the report.\n"
                "Please ensure the hardware report contains valid device data."
            )
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #D13438; padding: 40px;")
            no_data_label.setWordWrap(True)
            self.expandLayout.addWidget(no_data_label)

        # Update the macOS version card in the header
        self.update_macos_version_card()

        # Force layout update to ensure widgets are displayed
        self.scrollWidget.updateGeometry()
        self.scrollWidget.update()
        self.update()

    def refresh(self):
        """Refresh page content"""
        self.update_display()
