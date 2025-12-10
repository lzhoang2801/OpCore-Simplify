from typing import Union
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, BodyLabel, LineEdit, PushButton

class CustomMessageDialog(MessageBoxBase):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        
        self.titleLabel = SubtitleLabel(title, self.widget)
        self.contentLabel = BodyLabel(content, self.widget)
        self.contentLabel.setWordWrap(True)
        
        is_html = bool(re.search(r'<[^>]+>', content))
        
        if is_html:
            self.contentLabel.setTextFormat(Qt.TextFormat.RichText)
            self.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            self.contentLabel.setOpenExternalLinks(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        
        self.widget.setMinimumWidth(450)
        
        self.custom_widget = None
        self.input_field = None
        
    def add_input(self, placeholder: str = "", default_value: str = ""):
        self.input_field = LineEdit(self.widget)
        if placeholder:
            self.input_field.setPlaceholderText(placeholder)
        if default_value:
            self.input_field.setText(str(default_value))
        
        self.viewLayout.addWidget(self.input_field)
        self.input_field.setFocus()
        return self.input_field

    def add_custom_widget(self, widget: QWidget):
        self.custom_widget = widget
        self.viewLayout.addWidget(widget)

    def configure_buttons(self, yes_text: str = "OK", no_text: str = "Cancel", show_cancel: bool = True):
        self.yesButton.setText(yes_text)
        self.cancelButton.setText(no_text)
        self.cancelButton.setVisible(show_cancel)

def show_info(title: str, content: str, parent=None) -> None:
    dialog = CustomMessageDialog(title, content, parent)
    dialog.configure_buttons(yes_text="OK", show_cancel=False)
    dialog.exec()

def show_confirmation(title: str, content: str, parent=None, yes_text="Yes", no_text="No") -> bool:
    dialog = CustomMessageDialog(title, content, parent)
    dialog.configure_buttons(yes_text=yes_text, no_text=no_text, show_cancel=True)
    return dialog.exec()

def ask_network_count(total_networks: int, parent=None) -> Union[int, str]:
    content = (
        f"Found {total_networks} WiFi networks on this device.<br><br>"
        "How many networks would you like to process?<br>"
        "<ul>"
        f"<li>Enter a number (1-{total_networks})</li>"
        "<li>Or select 'Process All'</li>"
        "</ul>"
    )
    
    dialog = CustomMessageDialog("WiFi Network Retrieval", content, parent)
    dialog.input_field = dialog.add_input(placeholder=f"1-{total_networks} (Default: 5)", default_value="5")
    
    button_layout = QHBoxLayout()
    all_btn = PushButton("Process All Networks", dialog.widget)
    button_layout.addWidget(all_btn)
    button_layout.addStretch()
    dialog.viewLayout.addLayout(button_layout)
    
    result = {'value': 5}
    
    def on_all_clicked():
        result['value'] = 'a'
        dialog.accept()
        
    all_btn.clicked.connect(on_all_clicked)
    
    def on_accept():
        if result['value'] == 'a':
            return
        
        text = dialog.input_field.text().strip()
        if not text:
            result['value'] = 5
        elif text.lower() == 'a':
            result['value'] = 'a'
        else:
            try:
                val = int(text)
                result['value'] = min(max(1, val), total_networks)
            except ValueError:
                result['value'] = 5
    
    original_accept = dialog.accept
    def custom_accept():
        on_accept()
        original_accept()
        
    dialog.accept = custom_accept
    
    if dialog.exec():
        return result['value']

    return 5