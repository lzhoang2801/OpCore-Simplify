"""
Step 2: Compatibility checker - displays hardware compatibility information.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, ScrollArea, FluentIcon,
    GroupHeaderCardWidget, StrongBodyLabel
)

from ..styles import COLORS, SPACING
from ..ui_utils import create_info_widget, colored_icon, add_group_with_indent, create_step_indicator, \
    get_compatibility_icon
from ...datasets import os_data, pci_data

# Add Scripts directory to path for dataset imports
scripts_path = Path(__file__).parent.parent.parent
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

class CompatibilityPage(ScrollArea):
    """Step 2: View hardware compatibility."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("compatibilityPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        
        # Initialize widget references
        self.contentWidget = None
        self.contentLayout = None
        self.version_support_container = None
        self.native_support_label = None
        self.ocl_support_label = None
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the compatibility page UI."""
        # Configure scroll area
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

        # Set layout spacing and margins
        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                             SPACING['xxlarge'], SPACING['xlarge'])
        self.expandLayout.setSpacing(SPACING['large'])

        # Step indicator
        self.expandLayout.addWidget(create_step_indicator(2))

        # Header section with title and description
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['large'])

        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Hardware Compatibility")
        title_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Review hardware compatibility with macOS")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(title_block, 1)

        self.version_support_container = QWidget()
        self.version_support_container.setVisible(False)
        support_layout = QVBoxLayout(self.version_support_container)
        support_layout.setContentsMargins(0, 0, 0, 0)
        support_layout.setSpacing(SPACING['tiny'])

        support_title = StrongBodyLabel("macOS Support Range")
        support_title.setStyleSheet(
            f"color: {COLORS['primary']}; font-size: 13px;")
        support_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        support_layout.addWidget(support_title)

        self.native_support_label = StrongBodyLabel("")
        self.native_support_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.native_support_label.setWordWrap(True)
        support_layout.addWidget(self.native_support_label)

        self.ocl_support_label = BodyLabel("")
        self.ocl_support_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.ocl_support_label.setWordWrap(True)
        support_layout.addWidget(self.ocl_support_label)

        header_layout.addWidget(
            self.version_support_container, 0, Qt.AlignmentFlag.AlignTop)

        self.expandLayout.addWidget(header_container)
        self.expandLayout.addSpacing(SPACING['large'])

        # Dynamic content container that holds all compatibility cards
        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(SPACING['large'])
        self.expandLayout.addWidget(self.contentWidget)

        # Placeholder message (will be replaced when hardware report is loaded)
        self.placeholder_label = BodyLabel(
            "Load a hardware report to see compatibility information")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
        self.placeholder_label.setWordWrap(True)
        self.contentLayout.addWidget(self.placeholder_label)
        self.contentLayout.addStretch()

    def update_macos_version_card(self):
        """Update the macOS version support text in the header"""
        if not self.version_support_container:
            return

        if not self.controller.native_macos_version:
            self.version_support_container.setVisible(False)
            self.native_support_label.setText("")
            self.ocl_support_label.setText("")
            return

        # native_macos_version tuple format: (min_version, max_version)
        min_ver_name = os_data.get_macos_name_by_darwin(
            self.controller.native_macos_version[0])
        max_ver_name = os_data.get_macos_name_by_darwin(
            self.controller.native_macos_version[-1])

        native_range = min_ver_name if min_ver_name == max_ver_name else f"{min_ver_name} to {max_ver_name}"
        self.native_support_label.setText(f"Native: {native_range}")
        self.native_support_label.setStyleSheet(
            f"color: {COLORS['success']}; font-size: 13px;")

        if self.controller.ocl_patched_macos_version:
            oclp_max_name = os_data.get_macos_name_by_darwin(
                self.controller.ocl_patched_macos_version[0])
            oclp_min_name = os_data.get_macos_name_by_darwin(
                self.controller.ocl_patched_macos_version[-1])
            oclp_range = oclp_min_name if oclp_min_name == oclp_max_name else f"{oclp_min_name} to {oclp_max_name}"
            self.ocl_support_label.setText(f"OCLP: {oclp_range}")
            self.ocl_support_label.setStyleSheet(
                f"color: {COLORS['primary']}; font-size: 12px;")
            self.ocl_support_label.setVisible(True)
        else:
            self.ocl_support_label.setVisible(False)
            self.ocl_support_label.setText("")

        self.version_support_container.setVisible(True)

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
        if not self.contentLayout:
            return

        # Clear existing dynamic content
        while self.contentLayout.count() > 0:
            item = self.contentLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.controller.hardware_report:
            if self.version_support_container:
                self.version_support_container.setVisible(False)
            self.placeholder_label = BodyLabel(
                "Load a hardware report to see compatibility information")
            self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.placeholder_label.setStyleSheet(
                "color: #605E5C; padding: 40px;")
            self.placeholder_label.setWordWrap(True)
            self.contentLayout.addWidget(self.placeholder_label)
            self.contentLayout.addStretch()
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
                    colored_icon(FluentIcon.TAG, COLORS['primary']),
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
                        colored_icon(FluentIcon.INFO, COLORS['info']),
                        "Details",
                        " • ".join(details),
                        indent_level=1
                    )

            self.contentLayout.addWidget(cpu_card)
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
                    colored_icon(FluentIcon.PHOTO, COLORS['primary']),
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
                        colored_icon(FluentIcon.IOT, COLORS['primary']),
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
                            colored_icon(FluentIcon.VIEW, COLORS['info']),
                            "Connected Displays",
                            ", ".join(connected_monitors),
                            indent_level=1
                        )

            self.contentLayout.addWidget(gpu_card)
            cards_added += 1

        # Sound Card
        if 'Sound' in report and report['Sound']:
            sound_card = GroupHeaderCardWidget(self.scrollWidget)
            sound_card.setTitle("Audio")

            for audio_device, audio_props in report['Sound'].items():
                # Audio Device group (main item - no indent)
                add_group_with_indent(
                    sound_card,
                    colored_icon(FluentIcon.MUSIC, COLORS['primary']),
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
                        colored_icon(FluentIcon.HEADPHONE, COLORS['info']),
                        "Audio Endpoints",
                        ", ".join(endpoints),
                        indent_level=1
                    )

            self.contentLayout.addWidget(sound_card)
            cards_added += 1

        # Network Card
        if 'Network' in report and report['Network']:
            network_card = GroupHeaderCardWidget(self.scrollWidget)
            network_card.setTitle("Network")

            for device_name, device_props in report['Network'].items():
                # Network Device group (main item - no indent)
                add_group_with_indent(
                    network_card,
                    colored_icon(FluentIcon.WIFI, COLORS['primary']),
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
                        colored_icon(FluentIcon.IOT, COLORS['primary']),
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
                            colored_icon(FluentIcon.SYNC, continuity_color),
                            "Continuity Features",
                            continuity_info,
                            create_info_widget("", continuity_color),
                            indent_level=1
                        )

            self.contentLayout.addWidget(network_card)
            cards_added += 1

        # Storage Controllers Card
        if 'Storage Controllers' in report and report['Storage Controllers']:
            storage_card = GroupHeaderCardWidget(self.scrollWidget)
            storage_card.setTitle("Storage")

            for controller_name, controller_props in report['Storage Controllers'].items():
                # Storage Controller group (main item - no indent)
                add_group_with_indent(
                    storage_card,
                    colored_icon(FluentIcon.FOLDER, COLORS['primary']),
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

            self.contentLayout.addWidget(storage_card)
            cards_added += 1

        # Bluetooth Card
        if 'Bluetooth' in report and report['Bluetooth']:
            bluetooth_card = GroupHeaderCardWidget(self.scrollWidget)
            bluetooth_card.setTitle("Bluetooth")

            for bluetooth_name, bluetooth_props in report['Bluetooth'].items():
                # Bluetooth Device group (main item - no indent)
                add_group_with_indent(
                    bluetooth_card,
                    colored_icon(FluentIcon.BLUETOOTH, COLORS['primary']),
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

            self.contentLayout.addWidget(bluetooth_card)
            cards_added += 1

        # Biometric Card (if exists)
        if 'Biometric' in report and report['Biometric']:
            bio_card = GroupHeaderCardWidget(self.scrollWidget)
            bio_card.setTitle("Biometric")

            for bio_device, bio_props in report['Biometric'].items():
                # Biometric Device group (main item - no indent)
                add_group_with_indent(
                    bio_card,
                    colored_icon(FluentIcon.FINGERPRINT, COLORS['warning']),
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
                    colored_icon(FluentIcon.MEGAPHONE, COLORS['warning']),
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget(warning_message, COLORS['warning']),
                    indent_level=1
                )

            self.contentLayout.addWidget(bio_card)
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
            self.contentLayout.addWidget(no_data_label)

        # Keep page from collapsing when few/no cards are present
        self.contentLayout.addStretch()

        # Update the macOS version info in the header
        self.update_macos_version_card()

        # Force layout update to ensure widgets are displayed
        self.scrollWidget.updateGeometry()
        self.scrollWidget.update()
        self.update()

    def refresh(self):
        """Refresh page content"""
        self.update_display()
