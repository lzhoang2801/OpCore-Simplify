"""
Step 2: Compatibility checker - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ScrollArea
)

from ..styles import COLORS, SPACING


class CompatibilityPage(QWidget):
    """Step 2: View hardware compatibility"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("compatibilityPage")
        self.controller = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the compatibility page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], 
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])
        
        # Step indicator
        step_label = BodyLabel("STEP 2 OF 4")
        step_label.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(step_label)
        
        # Title
        title_label = SubtitleLabel("Hardware Compatibility")
        layout.addWidget(title_label)
        
        subtitle_label = BodyLabel("Review hardware compatibility with macOS")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(SPACING['large'])
        
        # Compatibility results card
        results_card = CardWidget()
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(SPACING['large'], SPACING['large'], 
                                         SPACING['large'], SPACING['large'])
        
        card_title = StrongBodyLabel("Compatibility Report")
        results_layout.addWidget(card_title)
        
        # Text area for compatibility details
        self.compatibility_text = TextEdit()
        self.compatibility_text.setReadOnly(True)
        self.compatibility_text.setPlainText("Load a hardware report to see compatibility information")
        self.compatibility_text.setMinimumHeight(400)
        results_layout.addWidget(self.compatibility_text)
        
        layout.addWidget(results_card)
        layout.addStretch()
    
    def update_display(self):
        """Update compatibility display"""
        if not self.controller.hardware_report:
            self.compatibility_text.setPlainText("Load a hardware report to see compatibility information")
            return
        
        # Format compatibility report
        report_text = []
        report_text.append("=== Hardware Compatibility Report ===\n")
        
        # CPU Compatibility
        if 'CPU' in self.controller.hardware_report:
            report_text.append("\n--- CPU ---")
            cpu_info = self.controller.hardware_report['CPU']
            if isinstance(cpu_info, dict):
                report_text.append(f"Name: {cpu_info.get('Processor Name', 'Unknown')}")
                compat = cpu_info.get('Compatibility', ('Unknown', 'Unknown'))
                if isinstance(compat, tuple) and len(compat) == 2:
                    report_text.append(f"Compatibility: {compat[0]} - {compat[1]}")
                else:
                    report_text.append(f"Compatibility: Unknown")
        
        # GPU Compatibility
        if 'GPU' in self.controller.hardware_report:
            report_text.append("\n--- GPU ---")
            for gpu_name, gpu_info in self.controller.hardware_report['GPU'].items():
                report_text.append(f"Name: {gpu_name}")
                report_text.append(f"Type: {gpu_info.get('Device Type', 'Unknown')}")
                compat = gpu_info.get('Compatibility', ('Unknown', 'Unknown'))
                report_text.append(f"Compatibility: {compat[0]} - {compat[1]}")
        
        # Network Compatibility
        if 'Network' in self.controller.hardware_report:
            report_text.append("\n--- Network ---")
            for net_name, net_info in self.controller.hardware_report['Network'].items():
                report_text.append(f"Name: {net_name}")
                compat = net_info.get('Compatibility', ('Unknown', 'Unknown'))
                report_text.append(f"Compatibility: {compat[0]} - {compat[1]}")
        
        # macOS Version Support
        if self.controller.native_macos_version:
            report_text.append("\n--- macOS Version Support ---")
            from datasets import os_data
            min_ver = os_data.get_macos_name_by_darwin(self.controller.native_macos_version[0])
            max_ver = os_data.get_macos_name_by_darwin(self.controller.native_macos_version[-1])
            report_text.append(f"Supported Range: {min_ver} to {max_ver}")
        
        self.compatibility_text.setPlainText("\n".join(report_text))
    
    def refresh(self):
        """Refresh page content"""
        self.update_display()
