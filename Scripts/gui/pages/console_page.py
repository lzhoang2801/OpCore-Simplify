"""
Console log page - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, FluentIcon
)

from ..styles import COLORS, SPACING


class ConsolePage(QWidget):
    """Console log viewer"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the console page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], 
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])
        
        # Title
        title_label = SubtitleLabel("Console Log")
        layout.addWidget(title_label)
        
        subtitle_label = BodyLabel("View application console output")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(SPACING['large'])
        
        # Console card
        console_card = CardWidget()
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(SPACING['large'], SPACING['large'], 
                                         SPACING['large'], SPACING['large'])
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        clear_btn = PushButton(FluentIcon.DELETE, "Clear")
        clear_btn.clicked.connect(self.clear_console)
        toolbar.addWidget(clear_btn)
        
        save_btn = PushButton(FluentIcon.SAVE, "Save to File")
        save_btn.clicked.connect(self.save_console)
        toolbar.addWidget(save_btn)
        
        toolbar.addStretch()
        console_layout.addLayout(toolbar)
        
        # Console text area
        self.console_text = TextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setPlainText("Console output will appear here...")
        self.console_text.setMinimumHeight(500)
        console_layout.addWidget(self.console_text)
        
        layout.addWidget(console_card)
    
    def clear_console(self):
        """Clear console output"""
        self.console_text.clear()
    
    def save_console(self):
        """Save console output to file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Console Log",
            "console.log",
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.console_text.toPlainText())
                self.controller.update_status("Console log saved successfully", 'success')
            except Exception as e:
                self.controller.update_status(f"Failed to save log: {str(e)}", 'error')
    
    def refresh(self):
        """Refresh page content"""
        pass
