from typing import Union, List, Optional, Dict, Any
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QRadioButton, QButtonGroup, QVBoxLayout, QCheckBox, QScrollArea, QLabel
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
        self.button_group = None
        
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

    def add_radio_options(self, options: List[str], default_index: int = 0) -> QButtonGroup:
        self.button_group = QButtonGroup(self)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        for i, option_text in enumerate(options):
            is_html = bool(re.search(r'<[^>]+>', option_text))
            
            if is_html:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(8)
                
                radio = QRadioButton()
                label = BodyLabel(option_text)
                label.setTextFormat(Qt.TextFormat.RichText)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
                label.setOpenExternalLinks(True)
                label.setWordWrap(True)
                
                row_layout.addWidget(radio)
                row_layout.addWidget(label, 1)
                
                layout.addWidget(row_widget)
            else:
                radio = QRadioButton(option_text)
                layout.addWidget(radio)
            
            self.button_group.addButton(radio, i)
            
            if i == default_index:
                radio.setChecked(True)
                
        self.viewLayout.addWidget(container)
        return self.button_group
    
    def add_checklist(self, items: List[Union[str, Dict[str, Any]]], checked_indices: List[int] = None) -> List[QCheckBox]:
        if checked_indices is None:
            checked_indices = []
            
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        checkboxes = []
        current_category = None
        
        for i, item in enumerate(items):
            label_text = item
            category = None
            supported = True
            
            if isinstance(item, dict):
                label_text = item.get('label', '')
                category = item.get('category')
                supported = item.get('supported', True)
            
            if category and category != current_category:
                current_category = category
                
                if i > 0:
                    layout.addSpacing(10)
                    
                header = QLabel(f"Category: {category}")
                header.setStyleSheet("font-weight: bold; color: #0078D4; padding-top: 5px; padding-bottom: 5px; border-bottom: 1px solid #E1DFDD;")
                layout.addWidget(header)
                
            cb = QCheckBox(label_text)
            if i in checked_indices:
                cb.setChecked(True)
                
            if not supported:
                cb.setStyleSheet("color: #A19F9D;")
                
            layout.addWidget(cb)
            checkboxes.append(cb)
            
        layout.addStretch()
        scroll.setWidget(container)
        self.viewLayout.addWidget(scroll)
        return checkboxes

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

def show_options_dialog(title: str, content: str, options: List[str], default_index: int = 0, parent=None) -> Optional[int]:
    dialog = CustomMessageDialog(title, content, parent)
    dialog.add_radio_options(options, default_index)
    dialog.configure_buttons(yes_text="OK", show_cancel=True)
    
    if dialog.exec():
        return dialog.button_group.checkedId()
    return None

def show_checklist_dialog(title: str, content: str, items: List[Union[str, Dict[str, Any]]], checked_indices: List[int] = None, parent=None) -> Optional[List[int]]:
    dialog = CustomMessageDialog(title, content, parent)
    checkboxes = dialog.add_checklist(items, checked_indices)
    dialog.configure_buttons(yes_text="OK", show_cancel=True)
    
    if dialog.exec():
        return [i for i, cb in enumerate(checkboxes) if cb.isChecked()]
    return None

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