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


def create_info_widget(text, color=None):
    """Create a simple label widget for displaying information"""
    label = BodyLabel(text)
    label.setWordWrap(True)
    if color:
        label.setStyleSheet(f"color: {color};")
    return label


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
                # Processor Name group
                name = cpu_info.get('Processor Name', 'Unknown')
                cpu_card.addGroup(
                    FluentIcon.TAG,
                    "Processor",
                    name,
                    QWidget()
                )
                
                # Compatibility group
                compat = cpu_info.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                cpu_card.addGroup(
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color)
                )
                
                # Additional details group if available
                details = []
                if cpu_info.get('Codename'):
                    details.append(f"Codename: {cpu_info.get('Codename')}")
                if cpu_info.get('Core Count'):
                    details.append(f"Cores: {cpu_info.get('Core Count')}")
                
                if details:
                    cpu_card.addGroup(
                        FluentIcon.INFO,
                        "Details",
                        " • ".join(details),
                        QWidget()
                    )
            
            self.cards_layout.addWidget(cpu_card)
        
        # GPU Card
        if 'GPU' in report and report['GPU']:
            gpu_card = GroupHeaderCardWidget("Graphics", self)
            
            for idx, (gpu_name, gpu_info) in enumerate(report['GPU'].items()):
                # GPU Name and Type group
                device_type = gpu_info.get('Device Type', 'Unknown')
                gpu_card.addGroup(
                    FluentIcon.PHOTO,
                    gpu_name,
                    f"Type: {device_type}",
                    QWidget()
                )
                
                # Compatibility group
                compat = gpu_info.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                gpu_card.addGroup(
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color)
                )
                
                # OCLP Compatibility if available
                if 'OCLP Compatibility' in gpu_info:
                    oclp_compat = gpu_info.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                    gpu_card.addGroup(
                        FluentIcon.IOT,
                        "OCLP Compatibility",
                        oclp_text,
                        create_info_widget("Extended support with OpenCore Legacy Patcher", "#605E5C")
                    )
                
                # Connected monitors
                if 'Monitor' in report:
                    connected_monitors = []
                    for monitor_name, monitor_info in report['Monitor'].items():
                        if monitor_info.get('Connected GPU') == gpu_name:
                            connector = monitor_info.get('Connector Type', 'Unknown')
                            connected_monitors.append(f"{monitor_name} ({connector})")
                    
                    if connected_monitors:
                        gpu_card.addGroup(
                            FluentIcon.VIEW,
                            "Connected Displays",
                            ", ".join(connected_monitors),
                            QWidget()
                        )
            
            self.cards_layout.addWidget(gpu_card)
        
        # Sound Card
        if 'Sound' in report and report['Sound']:
            sound_card = GroupHeaderCardWidget("Audio", self)
            
            for audio_device, audio_props in report['Sound'].items():
                # Audio Device group
                sound_card.addGroup(
                    FluentIcon.MUSIC,
                    audio_device,
                    "",
                    QWidget()
                )
                
                # Compatibility group
                compat = audio_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                sound_card.addGroup(
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color)
                )
                
                # Audio endpoints
                endpoints = audio_props.get('Audio Endpoints', [])
                if endpoints:
                    sound_card.addGroup(
                        FluentIcon.HEADPHONE,
                        "Audio Endpoints",
                        ", ".join(endpoints),
                        QWidget()
                    )
            
            self.cards_layout.addWidget(sound_card)
        
        # Network Card
        if 'Network' in report and report['Network']:
            network_card = GroupHeaderCardWidget("Network", self)
            
            for device_name, device_props in report['Network'].items():
                # Network Device group
                network_card.addGroup(
                    FluentIcon.WIFI,
                    device_name,
                    "",
                    QWidget()
                )
                
                # Compatibility group
                compat = device_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                network_card.addGroup(
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color)
                )
                
                # OCLP Compatibility if available
                if 'OCLP Compatibility' in device_props:
                    oclp_compat = device_props.get('OCLP Compatibility')
                    oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                    network_card.addGroup(
                        FluentIcon.IOT,
                        "OCLP Compatibility",
                        oclp_text,
                        create_info_widget("Extended support with OpenCore Legacy Patcher", "#605E5C")
                    )
                
                # Continuity support information (from compatibility_checker.py logic)
                device_id = device_props.get('Device ID', '')
                if device_id:
                    continuity_info = ""
                    continuity_color = "#605E5C"
                    
                    if device_id in pci_data.BroadcomWiFiIDs:
                        continuity_info = "Full support (AirDrop, Handoff, etc.)"
                        continuity_color = "#107C10"
                    elif device_id in pci_data.IntelWiFiIDs:
                        continuity_info = "Partial (Handoff with AirportItlwm) - AirDrop, Instant Hotspot not available"
                        continuity_color = "#FDB913"
                    elif device_id in pci_data.AtherosWiFiIDs:
                        continuity_info = "Limited support"
                        continuity_color = "#D13438"
                    
                    if continuity_info:
                        network_card.addGroup(
                            FluentIcon.SYNC,
                            "Continuity Features",
                            continuity_info,
                            create_info_widget("", continuity_color)
                        )
            
            self.cards_layout.addWidget(network_card)
        
        # Storage Controllers Card
        if 'Storage Controllers' in report and report['Storage Controllers']:
            storage_card = GroupHeaderCardWidget("Storage", self)
            
            for controller_name, controller_props in report['Storage Controllers'].items():
                # Storage Controller group
                storage_card.addGroup(
                    FluentIcon.FOLDER,
                    controller_name,
                    "",
                    QWidget()
                )
                
                # Compatibility group
                compat = controller_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                storage_card.addGroup(
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color)
                )
            
            self.cards_layout.addWidget(storage_card)
        
        # Bluetooth Card
        if 'Bluetooth' in report and report['Bluetooth']:
            bluetooth_card = GroupHeaderCardWidget("Bluetooth", self)
            
            for bluetooth_name, bluetooth_props in report['Bluetooth'].items():
                # Bluetooth Device group
                bluetooth_card.addGroup(
                    FluentIcon.BLUETOOTH,
                    bluetooth_name,
                    "",
                    QWidget()
                )
                
                # Compatibility group
                compat = bluetooth_props.get('Compatibility', (None, None))
                compat_text, compat_color = self.format_compatibility(compat)
                bluetooth_card.addGroup(
                    FluentIcon.ACCEPT,
                    "macOS Compatibility",
                    compat_text,
                    create_info_widget("", compat_color)
                )
            
            self.cards_layout.addWidget(bluetooth_card)
        
        # Biometric Card (if exists)
        if 'Biometric' in report and report['Biometric']:
            bio_card = GroupHeaderCardWidget("Biometric", self)
            
            for bio_device, bio_props in report['Biometric'].items():
                # Biometric Device group
                bio_card.addGroup(
                    FluentIcon.FINGERPRINT,
                    bio_device,
                    "Unsupported",
                    create_info_widget("⚠️ Biometric authentication requires Apple T2 Chip - Not available for Hackintosh systems", "#FDB913")
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
            
            version_card.addGroup(
                FluentIcon.HISTORY,
                "Native Support Range",
                f"{min_ver_name} to {max_ver_name}",
                create_info_widget("Fully supported macOS versions for your hardware", "#107C10")
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
                version_card.addGroup(
                    FluentIcon.IOT,
                    "OCLP Extended Support",
                    f"{oclp_min_name} to {oclp_max_name}",
                    create_info_widget("Additional macOS versions supported with OpenCore Legacy Patcher", "#0078D4")
                )
            
            self.cards_layout.addWidget(version_card)
        
        # Add stretch at the end
        self.cards_layout.addStretch()
    
    def refresh(self):
        """Refresh page content"""
        self.update_display()
