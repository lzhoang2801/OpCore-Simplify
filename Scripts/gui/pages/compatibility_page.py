"""
Step 2: Compatibility checker - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ScrollArea, FluentIcon, IconWidget, GroupHeaderCardWidget
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
from datasets import os_data, pci_data

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


class CompatibilityPage(QWidget):
    """Step 2: View hardware compatibility"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("compatibilityPage")
        self.controller = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the compatibility page UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], 
                                      SPACING['xxlarge'], SPACING['xlarge'])
        main_layout.setSpacing(SPACING['large'])
        
        # Step indicator
        step_label = BodyLabel("STEP 2 OF 4")
        step_label.setStyleSheet("color: #0078D4; font-weight: bold;")
        main_layout.addWidget(step_label)
        
        # Title
        title_label = SubtitleLabel("Hardware Compatibility")
        main_layout.addWidget(title_label)
        
        subtitle_label = BodyLabel("Review hardware compatibility with macOS")
        subtitle_label.setStyleSheet("color: #605E5C;")
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(SPACING['medium'])
        
        # Scrollable area for cards
        scroll_area = ScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("compatibilityScrollArea")
        
        # Container widget for scroll area
        container = QWidget()
        self.cards_layout = QVBoxLayout(container)
        self.cards_layout.setSpacing(SPACING['medium'])
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder message
        self.placeholder_label = BodyLabel("Load a hardware report to see compatibility information")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
        self.cards_layout.addWidget(self.placeholder_label)
        
        self.cards_layout.addStretch()
        
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)
    
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
        # Clear existing cards
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.controller.hardware_report:
            self.placeholder_label = BodyLabel("Load a hardware report to see compatibility information")
            self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
            self.cards_layout.addWidget(self.placeholder_label)
            self.cards_layout.addStretch()
            return
        
        report = self.controller.hardware_report
        
        # CPU Card
        if 'CPU' in report:
            cpu_card = GroupHeaderCardWidget("CPU", self)
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
                    FluentIcon.ACCEPT,
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
            
            self.cards_layout.addWidget(cpu_card)
        
        # GPU Card
        if 'GPU' in report and report['GPU']:
            gpu_card = GroupHeaderCardWidget("Graphics", self)
            
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
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )
                
                # OCLP Compatibility if available (child item - indent level 1)
                if 'OCLP Compatibility' in gpu_info:
                    oclp_compat = gpu_info.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                    add_group_with_indent(
                        gpu_card,
                        FluentIcon.IOT,
                        "OCLP Compatibility",
                        oclp_text,
                        create_info_widget("Extended support with OpenCore Legacy Patcher", COLORS['text_secondary']),
                        indent_level=1
                    )
                
                # Connected monitors (child item - indent level 1)
                if 'Monitor' in report:
                    connected_monitors = []
                    for monitor_name, monitor_info in report['Monitor'].items():
                        if monitor_info.get('Connected GPU') == gpu_name:
                            connector = monitor_info.get('Connector Type', 'Unknown')
                            connected_monitors.append(f"{monitor_name} ({connector})")
                    
                    if connected_monitors:
                        add_group_with_indent(
                            gpu_card,
                            FluentIcon.VIEW,
                            "Connected Displays",
                            ", ".join(connected_monitors),
                            indent_level=1
                        )
            
            self.cards_layout.addWidget(gpu_card)
        
        # Sound Card
        if 'Sound' in report and report['Sound']:
            sound_card = GroupHeaderCardWidget("Audio", self)
            
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
                    FluentIcon.ACCEPT,
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
            
            self.cards_layout.addWidget(sound_card)
        
        # Network Card
        if 'Network' in report and report['Network']:
            network_card = GroupHeaderCardWidget("Network", self)
            
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
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )
                
                # OCLP Compatibility if available (child item - indent level 1)
                if 'OCLP Compatibility' in device_props:
                    oclp_compat = device_props.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                    add_group_with_indent(
                        network_card,
                        FluentIcon.IOT,
                        "OCLP Compatibility",
                        oclp_text,
                        create_info_widget("Extended support with OpenCore Legacy Patcher", COLORS['text_secondary']),
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
            
            self.cards_layout.addWidget(network_card)
        
        # Storage Controllers Card
        if 'Storage Controllers' in report and report['Storage Controllers']:
            storage_card = GroupHeaderCardWidget("Storage", self)
            
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
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )
            
            self.cards_layout.addWidget(storage_card)
        
        # Bluetooth Card
        if 'Bluetooth' in report and report['Bluetooth']:
            bluetooth_card = GroupHeaderCardWidget("Bluetooth", self)
            
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
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color),
                    indent_level=1
                )
            
            self.cards_layout.addWidget(bluetooth_card)
        
        # Biometric Card (if exists)
        if 'Biometric' in report and report['Biometric']:
            bio_card = GroupHeaderCardWidget("Biometric", self)
            
            for bio_device, bio_props in report['Biometric'].items():
                # Biometric Device group (main item - no indent, unsupported warning included)
                add_group_with_indent(
                    bio_card,
                    FluentIcon.FINGERPRINT,
                    bio_device,
                    "Unsupported",
                    create_info_widget("⚠️ Biometric authentication requires Apple T2 Chip - Not available for Hackintosh systems", COLORS['warning']),
                    indent_level=0
                )
            
            self.cards_layout.addWidget(bio_card)
        
        # macOS Version Support Summary Card
        if self.controller.native_macos_version:
            version_card = GroupHeaderCardWidget("macOS Version Support", self)
            
            # native_macos_version tuple format: (min_version, max_version)
            # This is the ONLY tuple with this ordering - all device compatibility tuples are (max, min)
            # Index [0] = earliest supported version
            # Index [-1] = latest supported version
            min_ver_name = os_data.get_macos_name_by_darwin(self.controller.native_macos_version[0])
            max_ver_name = os_data.get_macos_name_by_darwin(self.controller.native_macos_version[-1])
            
            add_group_with_indent(
                version_card,
                FluentIcon.HISTORY,
                "Native Support Range",
                f"{min_ver_name} to {max_ver_name}",
                create_info_widget("Fully supported macOS versions for your hardware", COLORS['success']),
                indent_level=0
            )
            
            # Add OCLP info if available
            if self.controller.ocl_patched_macos_version:
                # ocl_patched_macos_version tuple format: (max_version, min_version)
                # Same as device compatibility tuples
                # Index [0] = latest supported version
                # Index [-1] = earliest supported version
                oclp_max_name = os_data.get_macos_name_by_darwin(self.controller.ocl_patched_macos_version[0])
                oclp_min_name = os_data.get_macos_name_by_darwin(self.controller.ocl_patched_macos_version[-1])
                # Display as earliest to latest for consistency
                add_group_with_indent(
                    version_card,
                    FluentIcon.IOT,
                    "OCLP Extended Support",
                    f"{oclp_min_name} to {oclp_max_name}",
                    create_info_widget("Additional macOS versions supported with OpenCore Legacy Patcher", COLORS['primary']),
                    indent_level=0
                )
            
            self.cards_layout.addWidget(version_card)
        
        # Add stretch at the end
        self.cards_layout.addStretch()
    
    def refresh(self):
        """Refresh page content"""
        self.update_display()
