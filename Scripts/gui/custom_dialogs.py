"""
Custom dialog implementations using qfluentwidgets
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    Dialog, MessageBox, LineEdit, ComboBox, 
    PrimaryPushButton, PushButton, SubtitleLabel, BodyLabel
)


class InputDialog(Dialog):
    """Text input dialog using qfluentwidgets"""
    
    def __init__(self, title: str, content: str, parent=None, placeholder: str = ""):
        super().__init__(title, content, parent)
        
        # Add input field
        self.input_field = LineEdit(self)
        if placeholder:
            self.input_field.setPlaceholderText(placeholder)
        
        # Insert input field before buttons
        self.textLayout.addWidget(self.input_field)
        self.input_field.setFocus()
        
        # Adjust dialog size
        self.resize(400, 250)
        
    def get_text(self):
        """Get the entered text"""
        return self.input_field.text()


class ChoiceDialog(Dialog):
    """Choice/combo box dialog using qfluentwidgets"""
    
    def __init__(self, title: str, content: str, options: list, parent=None):
        super().__init__(title, content, parent)
        
        # Add combo box
        self.combo_box = ComboBox(self)
        self.combo_box.addItems(options)
        self.combo_box.setCurrentIndex(0)
        
        # Insert combo box before buttons
        self.textLayout.addWidget(self.combo_box)
        self.combo_box.setFocus()
        
        # Adjust dialog size
        self.resize(400, 250)
        
    def get_selected_item(self):
        """Get the selected item"""
        return self.combo_box.currentText()


def show_input_dialog(parent, title: str, content: str, placeholder: str = ""):
    """
    Show an input dialog and return the entered text
    
    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/prompt
        placeholder: Placeholder text for input field
        
    Returns:
        tuple: (text, ok) where text is the entered text and ok is True if OK was clicked
    """
    dialog = InputDialog(title, content, parent, placeholder)
    if dialog.exec():
        return dialog.get_text(), True
    return "", False


def show_choice_dialog(parent, title: str, content: str, options: list):
    """
    Show a choice dialog and return the selected item
    
    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/prompt
        options: List of options to choose from
        
    Returns:
        tuple: (item, ok) where item is the selected item and ok is True if OK was clicked
    """
    if not options:
        return None, False
        
    dialog = ChoiceDialog(title, content, options, parent)
    if dialog.exec():
        return dialog.get_selected_item(), True
    return None, False


def show_question_dialog(parent, title: str, content: str):
    """
    Show a yes/no question dialog
    
    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/question
        
    Returns:
        bool: True if Yes was clicked, False otherwise
    """
    dialog = MessageBox(title, content, parent)
    dialog.yesButton.setText("Yes")
    dialog.cancelButton.setText("No")
    
    return dialog.exec()
