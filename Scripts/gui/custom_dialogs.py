"""
Custom dialog implementations using qfluentwidgets.
Following qfluentwidgets design patterns by extending MessageBoxBase.
"""

import platform
from typing import Optional, List, Dict, Any, Tuple

from PyQt6.QtWidgets import (
    QLabel, QDialog, QVBoxLayout, QHBoxLayout,
    QScrollArea, QWidget, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    MessageBoxBase, LineEdit, ComboBox, MessageBox, 
    PushButton, PrimaryPushButton, BodyLabel
)

from .styles import COLORS
from ..datasets import os_data

# Dialog size constants
MIN_DIALOG_WIDTH = 400
STANDARD_DIALOG_WIDTH = 500
WIDE_DIALOG_WIDTH = 600
LARGE_DIALOG_WIDTH = 700
XLARGE_DIALOG_WIDTH = 900
XXLARGE_DIALOG_WIDTH = 1000

# Standard dialog heights
MIN_DIALOG_HEIGHT = 500
STANDARD_DIALOG_HEIGHT = 600
LARGE_DIALOG_HEIGHT = 700

# Layout constants
BASE_MARGIN = 24
INDENT_PER_LEVEL = 20


class InputMessageBox(MessageBoxBase):
    """Input dialog using qfluentwidgets MessageBoxBase pattern."""

    def __init__(self, title: str, content: str, placeholder: str = "", parent=None):
        """
        Initialize input dialog.
        
        Args:
            title: Dialog title
            content: Dialog message/prompt
            placeholder: Placeholder text for input field
            parent: Parent widget
        """
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
        self.widget.setMinimumWidth(MIN_DIALOG_WIDTH)

        # Focus on input field
        self.inputLineEdit.setFocus()

    def getText(self) -> str:
        """Get the entered text."""
        return self.inputLineEdit.text()


class ChoiceMessageBox(MessageBoxBase):
    """Choice/dropdown dialog using qfluentwidgets MessageBoxBase pattern."""

    def __init__(
        self, 
        title: str, 
        content: str, 
        choices: List[Dict[str, Any]],
        default_value: Optional[str] = None, 
        warning: Optional[str] = None,
        note: Optional[str] = None, 
        parent=None
    ):
        """
        Initialize choice dialog.

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
        self.choice_values: List[str] = []

        # Create UI elements
        self.titleLabel = QLabel(title, self.widget)
        self.contentLabel = QLabel(content, self.widget)
        self.comboBox = ComboBox(self.widget)

        # Setup title and content
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.contentLabel.setWordWrap(True)

        # Populate combo box and build descriptions text
        descriptions_text: List[str] = []
        if choices:
            default_index = 0
            for idx, choice in enumerate(choices):
                # Get the display text (label)
                label = choice.get('label', choice.get('value', str(idx)))
                self.comboBox.addItem(label)

                # Store the value for later retrieval
                value = choice.get('value', str(idx))
                self.choice_values.append(value)

                # Build description text if available
                description = choice.get('description')
                if description:
                    if descriptions_text:
                        # Add separator between descriptions
                        descriptions_text.append(f"\n{label}:\n{description}")
                    else:
                        # First description - no leading newline
                        descriptions_text.append(f"{label}:\n{description}")

                # Set default if matches
                if default_value and value == default_value:
                    default_index = idx

            self.comboBox.setCurrentIndex(default_index)

        # Add widgets to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.comboBox)

        # Add descriptions if available
        if descriptions_text:
            self.descriptionsLabel = QLabel('\n'.join(descriptions_text), self.widget)
            self.descriptionsLabel.setWordWrap(True)
            self.descriptionsLabel.setStyleSheet(
                f"color: {COLORS['text_secondary']}; margin-top: 10px; font-size: 12px;")
            self.viewLayout.addWidget(self.descriptionsLabel)

        # Add warning or note if provided
        if warning:
            self.warningLabel = QLabel(f"⚠️ {warning}", self.widget)
            self.warningLabel.setWordWrap(True)
            self.warningLabel.setStyleSheet(
                f"color: {COLORS['warning']}; margin-top: 10px; font-weight: 500;")
            self.viewLayout.addWidget(self.warningLabel)
        elif note:
            self.noteLabel = QLabel(f"ℹ️ {note}", self.widget)
            self.noteLabel.setWordWrap(True)
            self.noteLabel.setStyleSheet(
                f"color: {COLORS['info']}; margin-top: 10px; font-weight: 500;")
            self.viewLayout.addWidget(self.noteLabel)

        # Set minimum width for the dialog
        self.widget.setMinimumWidth(STANDARD_DIALOG_WIDTH)

        # Focus on combo box
        self.comboBox.setFocus()

    def getSelectedValue(self) -> Optional[str]:
        """Get the value of the selected item."""
        selected_index = self.comboBox.currentIndex()
        if 0 <= selected_index < len(self.choice_values):
            return self.choice_values[selected_index]
        return None


class InfoMessageBox(MessageBoxBase):
    """Info dialog using qfluentwidgets MessageBoxBase pattern with better support for long content."""

    def __init__(self, title: str, content: str, parent=None):
        """
        Initialize info dialog.

        Args:
            title: Dialog title
            content: Dialog message (can be multi-line)
            parent: Parent widget
        """
        super().__init__(parent)

        # Create UI elements
        self.titleLabel = QLabel(title, self.widget)
        self.contentLabel = QLabel(content, self.widget)

        # Setup title and content
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.contentLabel.setWordWrap(True)
        self.contentLabel.setTextFormat(Qt.TextFormat.PlainText)

        # Add widgets to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)

        # Set minimum width for the dialog to handle longer content
        self.widget.setMinimumWidth(WIDE_DIALOG_WIDTH)

        # Hide cancel button for info dialogs
        self.cancelButton.hide()
        self.yesButton.setText("OK")


def show_input_dialog(parent, title: str, content: str, placeholder: str = "") -> Tuple[str, bool]:
    """
    Show an input dialog and return the entered text.

    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/prompt
        placeholder: Placeholder text for input field

    Returns:
        Tuple of (text, ok) where text is the entered text and ok is True if OK was clicked
    """
    dialog = InputMessageBox(title, content, placeholder, parent)
    if dialog.exec():
        return dialog.getText(), True
    return "", False


def show_choice_dialog(
    parent, 
    title: str, 
    content: str, 
    choices: List[Dict[str, Any]],
    default_value: Optional[str] = None, 
    warning: Optional[str] = None, 
    note: Optional[str] = None
) -> Tuple[Optional[str], bool]:
    """
    Show a choice dialog and return the selected value.

    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/prompt
        choices: List of choice dicts with 'value', 'label', and optional 'description'
        default_value: Default value to select
        warning: Warning message to display
        note: Note message to display

    Returns:
        Tuple of (value, ok) where value is the selected value and ok is True if OK was clicked
    """
    if not choices:
        return None, False

    dialog = ChoiceMessageBox(title, content, choices, default_value, warning, note, parent)
    if dialog.exec():
        return dialog.getSelectedValue(), True
    return None, False


def show_question_dialog(
    parent, 
    title: str, 
    content: str, 
    default: str = 'no', 
    warning: Optional[str] = None
) -> bool:
    if warning:
        content = f"{content}\n\n⚠️ {warning}"

    dialog = MessageBox(title, content, parent)
    
    if '<' in content and '>' in content:
        dialog.contentLabel.setTextFormat(Qt.TextFormat.RichText)
        dialog.contentLabel.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        dialog.contentLabel.setOpenExternalLinks(True)
        
    dialog.yesButton.setText("Yes")
    dialog.cancelButton.setText("No")

    return dialog.exec() == QDialog.DialogCode.Accepted


def show_info_dialog(parent, title: str, content: str) -> str:
    """
    Show an informational dialog with OK button

    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content/message

    Returns:
        str: Empty string for consistency with request_input
    """
    dialog = InfoMessageBox(title, content, parent)
    dialog.exec()
    return ""
