"""
Custom dialog implementations using qfluentwidgets
Following qfluentwidgets design patterns by extending MessageBoxBase
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import MessageBoxBase, LineEdit, ComboBox, MessageBox


class InputMessageBox(MessageBoxBase):
    """Input dialog using qfluentwidgets MessageBoxBase pattern"""
    
    def __init__(self, title: str, content: str, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.placeholder = placeholder
        
        self.titleLabel = QLabel(title, self.widget)
        self.contentLabel = QLabel(content, self.widget)
        self.inputLineEdit = LineEdit(self.widget)
        
        if placeholder:
            self.inputLineEdit.setPlaceholderText(placeholder)
        
        # Setup UI
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.contentLabel.setWordWrap(True)
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.inputLineEdit)
        
        # Set fixed width for the dialog
        self.widget.setMinimumWidth(400)
        
        # Focus on input field
        self.inputLineEdit.setFocus()
        
    def getText(self):
        """Get the entered text"""
        return self.inputLineEdit.text()


class ChoiceMessageBox(MessageBoxBase):
    """Choice/dropdown dialog using qfluentwidgets MessageBoxBase pattern"""
    
    def __init__(self, title: str, content: str, choices: list, 
                 default_value: str = None, warning: str = None, 
                 note: str = None, parent=None):
        """
        Initialize choice dialog
        
        Args:
            title: Dialog title
            content: Dialog message
            choices: List of choice dicts with 'value', 'label', and optional 'description'
            default_value: Default value to select
            warning: Warning message to display
            note: Note message to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.choices = choices
        self.choice_values = []
        
        # Create UI elements
        self.titleLabel = QLabel(title, self.widget)
        self.contentLabel = QLabel(content, self.widget)
        self.comboBox = ComboBox(self.widget)
        
        # Setup title and content
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.contentLabel.setWordWrap(True)
        
        # Populate combo box
        if choices:
            default_index = 0
            for idx, choice in enumerate(choices):
                # Get the display text (label)
                label = choice.get('label', choice.get('value', str(idx)))
                self.comboBox.addItem(label)
                
                # Store the value for later retrieval
                value = choice.get('value', str(idx))
                self.choice_values.append(value)
                
                # Set default if matches
                if default_value and value == default_value:
                    default_index = idx
            
            self.comboBox.setCurrentIndex(default_index)
        
        # Add widgets to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.comboBox)
        
        # Add warning or note if provided
        if warning:
            self.warningLabel = QLabel(f"⚠️ {warning}", self.widget)
            self.warningLabel.setWordWrap(True)
            self.warningLabel.setStyleSheet("color: #ff9800; margin-top: 10px;")
            self.viewLayout.addWidget(self.warningLabel)
        elif note:
            self.noteLabel = QLabel(f"ℹ️ {note}", self.widget)
            self.noteLabel.setWordWrap(True)
            self.noteLabel.setStyleSheet("color: #2196F3; margin-top: 10px;")
            self.viewLayout.addWidget(self.noteLabel)
        
        # Set minimum width for the dialog
        self.widget.setMinimumWidth(500)
        
        # Focus on combo box
        self.comboBox.setFocus()
        
    def getSelectedValue(self):
        """Get the value of the selected item"""
        selected_index = self.comboBox.currentIndex()
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
    dialog = InputMessageBox(title, content, placeholder, parent)
    if dialog.exec():
        return dialog.getText(), True
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
        
    dialog = ChoiceMessageBox(title, content, choices, default_value, warning, note, parent)
    if dialog.exec():
        return dialog.getSelectedValue(), True
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
    
    # The MessageBox class already handles the exec() and returns Accepted/Rejected
    return dialog.exec()

