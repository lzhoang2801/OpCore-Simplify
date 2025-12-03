"""
WiFi Profile Extractor - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, FluentIcon, LineEdit
)

from ..styles import COLORS, SPACING


class WiFiPage(QWidget):
    """WiFi Profile Extractor"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("wifiPage")
        self.controller = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the WiFi page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], 
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])
        
        # Title
        title_label = SubtitleLabel("WiFi Profile Extractor")
        layout.addWidget(title_label)
        
        subtitle_label = BodyLabel("Extract WiFi profiles for itlwm kext")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(SPACING['large'])
        
        # Extract card
        extract_card = CardWidget()
        extract_layout = QVBoxLayout(extract_card)
        extract_layout.setContentsMargins(SPACING['large'], SPACING['large'], 
                                         SPACING['large'], SPACING['large'])
        
        card_title = StrongBodyLabel("Extract WiFi Profiles")
        extract_layout.addWidget(card_title)
        
        info_label = BodyLabel(
            "This tool extracts saved WiFi profiles from your system and formats them\n"
            "for use with the itlwm kext to enable automatic WiFi connection at boot time."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #605E5C;")
        extract_layout.addWidget(info_label)
        
        # Extract button
        self.extract_btn = PushButton(FluentIcon.DOWNLOAD, "Extract WiFi Profiles")
        self.extract_btn.clicked.connect(self.extract_profiles)
        extract_layout.addWidget(self.extract_btn)
        
        layout.addWidget(extract_card)
        
        # Results card
        results_card = CardWidget()
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(SPACING['large'], SPACING['large'], 
                                         SPACING['large'], SPACING['large'])
        
        results_title = StrongBodyLabel("Extracted Profiles")
        results_layout.addWidget(results_title)
        
        # Results text area
        self.results_text = TextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlainText("No profiles extracted yet...")
        self.results_text.setMinimumHeight(300)
        results_layout.addWidget(self.results_text)
        
        # Save button
        self.save_btn = PushButton(FluentIcon.SAVE, "Save Profiles")
        self.save_btn.clicked.connect(self.save_profiles)
        self.save_btn.setEnabled(False)
        results_layout.addWidget(self.save_btn)
        
        layout.addWidget(results_card)
        layout.addStretch()
    
    def extract_profiles(self):
        """Extract WiFi profiles"""
        try:
            # Use the WiFi profile extractor from the original code
            import os
            if os.name == 'nt':
                # Windows extraction logic
                self.results_text.setPlainText("Extracting WiFi profiles...")
                # This would call the actual extractor
                self.controller.update_status("WiFi profile extraction not yet implemented", 'info')
            else:
                self.controller.update_status("WiFi extraction is only supported on Windows", 'warning')
        except Exception as e:
            self.controller.update_status(f"Extraction failed: {str(e)}", 'error')
    
    def save_profiles(self):
        """Save extracted profiles to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save WiFi Profiles",
            "wifi_profiles.plist",
            "Property List (*.plist);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.results_text.toPlainText())
                self.controller.update_status("WiFi profiles saved successfully", 'success')
            except Exception as e:
                self.controller.update_status(f"Failed to save profiles: {str(e)}", 'error')
    
    def refresh(self):
        """Refresh page content"""
        pass
