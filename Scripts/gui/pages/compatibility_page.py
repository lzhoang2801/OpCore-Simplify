"""
Step 2: Compatibility checker - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ScrollArea, FluentIcon, IconWidget
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


class HardwareCard(CardWidget):
    """Card widget for displaying hardware component information"""
    
    def __init__(self, title, icon, parent=None):
        super().__init__(parent)
        self.setObjectName("hardwareCard")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['large'], SPACING['large'], 
                                 SPACING['large'], SPACING['large'])
        layout.setSpacing(SPACING['medium'])
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(SPACING['small'])
        
        # Icon
        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(24, 24)
        header_layout.addWidget(icon_widget)
        
        # Title
        title_label = StrongBodyLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACING['small'])
        layout.addLayout(self.content_layout)
        
    def add_item(self, name, value, indent=0, color=None):
        """Add an information item to the card"""
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(indent * 20, 0, 0, 0)
        
        # Name label
        name_label = BodyLabel(name)
        name_label.setStyleSheet("color: #323130; font-weight: 500;")
        item_layout.addWidget(name_label)
        
        item_layout.addStretch()
        
        # Value label
        value_label = BodyLabel(str(value))
        if color:
            value_label.setStyleSheet(f"color: {color}; font-weight: 500;")
        else:
            value_label.setStyleSheet("color: #605E5C;")
        item_layout.addWidget(value_label)
        
        self.content_layout.addLayout(item_layout)
    
    def add_detail(self, text, indent=1, color=None):
        """Add a detail text line"""
        label = BodyLabel(text)
        label.setWordWrap(True)
        if color:
            label.setStyleSheet(f"color: {color}; font-size: 12px; margin-left: {indent * 20}px;")
        else:
            label.setStyleSheet(f"color: #605E5C; font-size: 12px; margin-left: {indent * 20}px;")
        self.content_layout.addWidget(label)
    
    def add_spacing(self):
        """Add vertical spacing"""
        self.content_layout.addSpacing(SPACING['small'])


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
        """Update compatibility display with rich UI"""
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
            cpu_card = HardwareCard("CPU", FluentIcon.DEVELOPER_TOOLS)
            cpu_info = report['CPU']
            
            if isinstance(cpu_info, dict):
                cpu_card.add_item("Name:", cpu_info.get('Processor Name', 'Unknown'), indent=0)
                
                compat = cpu_info.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                cpu_card.add_item("Compatibility:", compat_text, color=compat_color)
                
                # Additional CPU details
                if cpu_info.get('Codename'):
                    cpu_card.add_detail(f"Codename: {cpu_info.get('Codename')}", indent=1)
                if cpu_info.get('Core Count'):
                    cpu_card.add_detail(f"Cores: {cpu_info.get('Core Count')}", indent=1)
            
            self.cards_layout.addWidget(cpu_card)
        
        # GPU Card
        if 'GPU' in report and report['GPU']:
            gpu_card = HardwareCard("Graphics", FluentIcon.PHOTO)
            
            for gpu_name, gpu_info in report['GPU'].items():
                gpu_card.add_spacing()
                gpu_card.add_item("Name:", gpu_name, indent=0)
                
                device_type = gpu_info.get('Device Type', 'Unknown')
                gpu_card.add_detail(f"Type: {device_type}", indent=1)
                
                compat = gpu_info.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                gpu_card.add_item("Compatibility:", compat_text, indent=1, color=compat_color)
                
                # OCLP Compatibility if available
                if 'OCLP Compatibility' in gpu_info:
                    oclp_compat = gpu_info.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                    gpu_card.add_item("OCLP Compat:", oclp_text, indent=1, color=oclp_color)
                
                # Connected monitors
                if 'Monitor' in report:
                    connected_monitors = []
                    for monitor_name, monitor_info in report['Monitor'].items():
                        if monitor_info.get('Connected GPU') == gpu_name:
                            connector = monitor_info.get('Connector Type', 'Unknown')
                            connected_monitors.append(f"{monitor_name} ({connector})")
                    
                    if connected_monitors:
                        gpu_card.add_detail(f"Monitors: {', '.join(connected_monitors)}", indent=1, color="#0078D4")
            
            self.cards_layout.addWidget(gpu_card)
        
        # Sound Card
        if 'Sound' in report and report['Sound']:
            sound_card = HardwareCard("Audio", FluentIcon.MUSIC)
            
            for audio_device, audio_props in report['Sound'].items():
                sound_card.add_spacing()
                sound_card.add_item("Name:", audio_device, indent=0)
                
                compat = audio_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                sound_card.add_item("Compatibility:", compat_text, indent=1, color=compat_color)
                
                # Audio endpoints
                endpoints = audio_props.get('Audio Endpoints', [])
                if endpoints:
                    sound_card.add_detail(f"Endpoints: {', '.join(endpoints)}", indent=1)
            
            self.cards_layout.addWidget(sound_card)
        
        # Network Card
        if 'Network' in report and report['Network']:
            network_card = HardwareCard("Network", FluentIcon.WIFI)
            
            for device_name, device_props in report['Network'].items():
                network_card.add_spacing()
                network_card.add_item("Name:", device_name, indent=0)
                
                compat = device_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                network_card.add_item("Compatibility:", compat_text, indent=1, color=compat_color)
                
                # OCLP Compatibility if available
                if 'OCLP Compatibility' in device_props:
                    oclp_compat = device_props.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                    network_card.add_item("OCLP Compat:", oclp_text, indent=1, color=oclp_color)
                
                # Continuity support information (from compatibility_checker.py logic)
                device_id = device_props.get('Device ID', '')
                if device_id:
                    if device_id in pci_data.BroadcomWiFiIDs:
                        network_card.add_detail("Continuity: Full support (AirDrop, Handoff, etc.)", indent=1, color="#107C10")
                    elif device_id in pci_data.IntelWiFiIDs:
                        network_card.add_detail("Continuity: Partial (Handoff with AirportItlwm)", indent=1, color="#FDB913")
                        network_card.add_detail("Note: AirDrop, Instant Hotspot not available", indent=1, color="#605E5C")
                    elif device_id in pci_data.AtherosWiFiIDs:
                        network_card.add_detail("Continuity: Limited", indent=1, color="#D13438")
            
            self.cards_layout.addWidget(network_card)
        
        # Storage Controllers Card
        if 'Storage Controllers' in report and report['Storage Controllers']:
            storage_card = HardwareCard("Storage", FluentIcon.FOLDER)
            
            for controller_name, controller_props in report['Storage Controllers'].items():
                storage_card.add_spacing()
                storage_card.add_item("Name:", controller_name, indent=0)
                
                compat = controller_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                storage_card.add_item("Compatibility:", compat_text, indent=1, color=compat_color)
            
            self.cards_layout.addWidget(storage_card)
        
        # Bluetooth Card
        if 'Bluetooth' in report and report['Bluetooth']:
            bluetooth_card = HardwareCard("Bluetooth", FluentIcon.LABEL)
            
            for bluetooth_name, bluetooth_props in report['Bluetooth'].items():
                bluetooth_card.add_spacing()
                bluetooth_card.add_item("Name:", bluetooth_name, indent=0)
                
                compat = bluetooth_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                bluetooth_card.add_item("Compatibility:", compat_text, indent=1, color=compat_color)
            
            self.cards_layout.addWidget(bluetooth_card)
        
        # Biometric Card (if exists)
        if 'Biometric' in report and report['Biometric']:
            bio_card = HardwareCard("Biometric", FluentIcon.FINGERPRINT)
            bio_card.add_detail("⚠️ Biometric authentication requires Apple T2 Chip", indent=0, color="#FDB913")
            bio_card.add_detail("Not available for Hackintosh systems", indent=0, color="#605E5C")
            
            for bio_device, bio_props in report['Biometric'].items():
                bio_card.add_spacing()
                bio_card.add_item("Name:", bio_device, indent=0)
                bio_card.add_item("Compatibility:", "Unsupported", indent=1, color="#D13438")
            
            self.cards_layout.addWidget(bio_card)
        
        # macOS Version Support Summary Card
        if self.controller.native_macos_version:
            version_card = HardwareCard("macOS Version Support", FluentIcon.HISTORY)
            
            # native_macos_version tuple format: (min_version, max_version)
            # This is the ONLY tuple with this ordering - all device compatibility tuples are (max, min)
            # Index [0] = earliest supported version
            # Index [-1] = latest supported version
            min_ver_name = os_data.get_macos_name_by_darwin(self.controller.native_macos_version[0])
            max_ver_name = os_data.get_macos_name_by_darwin(self.controller.native_macos_version[-1])
            
            version_card.add_item("Supported Range:", f"{min_ver_name} to {max_ver_name}", color="#107C10")
            
            # Add OCLP info if available
            if self.controller.ocl_patched_macos_version:
                # ocl_patched_macos_version tuple format: (max_version, min_version)
                # Same as device compatibility tuples
                # Index [0] = latest supported version
                # Index [-1] = earliest supported version
                oclp_max_name = os_data.get_macos_name_by_darwin(self.controller.ocl_patched_macos_version[0])
                oclp_min_name = os_data.get_macos_name_by_darwin(self.controller.ocl_patched_macos_version[-1])
                # Display as earliest to latest for consistency
                version_card.add_item("OCLP Extended:", f"{oclp_min_name} to {oclp_max_name}", color="#0078D4")
                version_card.add_detail("With OpenCore Legacy Patcher support", indent=1, color="#605E5C")
            
            self.cards_layout.addWidget(version_card)
        
        # Add stretch at the end
        self.cards_layout.addStretch()
    
    def refresh(self):
        """Refresh page content"""
        self.update_display()
