"""
Custom dialog implementations using qfluentwidgets
"""

from PyQt6.QtWidgets import QDialog, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import Dialog, MessageBox, LineEdit, ComboBox


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
    
    def __init__(self, title: str, content: str, choices: list, default_value: str = None, 
                 warning: str = None, note: str = None, parent=None):
        """
        Initialize choice dialog
        
        Args:
            title: Dialog title
            content: Dialog message
            choices: List of choice dicts with 'value', 'label', and 'description'
            default_value: Default value to select
            warning: Warning message to display
            note: Note message to display
            parent: Parent widget
        """
        super().__init__(title, content, parent)
        
        # Store choices for value mapping
        self.choices = choices
        self.choice_values = []
        
        # Add combo box
        self.combo_box = ComboBox(self)
        
        if choices:
            # Build display items from choices
            default_index = 0
            for idx, choice in enumerate(choices):
                # Get the display text (label with description as tooltip)
                label = choice.get('label', choice.get('value', str(idx)))
                self.combo_box.addItem(label)
                
                # Store the value for later retrieval
                value = choice.get('value', str(idx))
                self.choice_values.append(value)
                
                # Set default if matches
                if default_value and value == default_value:
                    default_index = idx
            
            self.combo_box.setCurrentIndex(default_index)
        
        # Insert combo box before buttons
        self.textLayout.addWidget(self.combo_box)
        
        # Add warning or note if provided
        if warning:
            warning_label = QLabel(f"⚠️ {warning}")
            warning_label.setWordWrap(True)
            warning_label.setStyleSheet("color: #ff9800; margin-top: 10px;")
            self.textLayout.addWidget(warning_label)
        elif note:
            note_label = QLabel(f"ℹ️ {note}")
            note_label.setWordWrap(True)
            note_label.setStyleSheet("color: #2196F3; margin-top: 10px;")
            self.textLayout.addWidget(note_label)
        
        self.combo_box.setFocus()
        
        # Adjust dialog size
        self.resize(500, 300)
        
    def get_selected_value(self):
        """Get the value of the selected item"""
        selected_index = self.combo_box.currentIndex()
        if 0 <= selected_index < len(self.choice_values):
            return self.choice_values[selected_index]
        return None


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


def show_choice_dialog(parent, title: str, content: str, choices: list, 
                       default_value: str = None, warning: str = None, note: str = None):
    """
    Show a choice dialog and return the selected value
    
    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/prompt
        choices: List of choice dicts with 'value', 'label', and optional 'description'
        default_value: Default value to select
        warning: Warning message to display
        note: Note message to display
        
    Returns:
        tuple: (value, ok) where value is the selected value and ok is True if OK was clicked
    """
    if not choices:
        return None, False
        
    dialog = ChoiceDialog(title, content, choices, default_value, warning, note, parent)
    if dialog.exec():
        return dialog.get_selected_value(), True
    return None, False


def show_question_dialog(parent, title: str, content: str, default: str = 'no', warning: str = None):
    """
    Show a yes/no question dialog
    
    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/question
        default: Default option ('yes' or 'no')
        warning: Optional warning message to append
        
    Returns:
        bool: True if Yes was clicked, False otherwise
    """
    # Add warning to content if provided
    if warning:
        content = f"{content}\n\n⚠️ {warning}"
    
    dialog = MessageBox(title, content, parent)
    dialog.yesButton.setText("Yes")
    dialog.cancelButton.setText("No")
    
    # exec() returns QDialog.Accepted (1) for accept and QDialog.Rejected (0) for reject
    return dialog.exec() == QDialog.DialogCode.Accepted
