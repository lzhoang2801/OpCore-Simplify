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

class ACPIPatchesDialog(QDialog):
    """Custom dialog for ACPI Patch selection with checkboxes"""

    def __init__(self, acpi_guru, parent=None):
        """
        Initialize ACPI Patches dialog

        Args:
            acpi_guru: ACPIGuru instance with patches list
            parent: Parent widget
        """
        super().__init__(parent)
        self.acpi_guru = acpi_guru
        self.patches = acpi_guru.patches
        self.checkboxes = []  # Store references to checkboxes
        self.original_state = {}  # Store original checked state

        # Store original state
        for idx, patch in enumerate(self.patches):
            self.original_state[idx] = patch.checked

        self.setWindowTitle("Customize ACPI Patches")
        self.setMinimumSize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Customize ACPI Patches")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description
        desc_label = BodyLabel(
            "Select ACPI patches for your system. "
            "These patches modify ACPI tables to enable proper hardware support in macOS."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(desc_label)

        # Scroll area for patches
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E1DFDD;
                border-radius: 4px;
                background-color: white;
            }
        """)

        # Container widget for scroll area
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)

        self.populate_patches()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Give it stretch factor

        # Note
        note_label = BodyLabel(
            "ℹ️ Note: Selected patches will be applied when building the OpenCore EFI. "
            "Choose patches based on your hardware requirements."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 5px;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        # Cancel and OK buttons
        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(cancel_btn)

        ok_btn = PrimaryPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def populate_patches(self):
        """Populate the patches list with checkboxes"""
        from PyQt6.QtWidgets import QCheckBox

        for index, patch in enumerate(self.patches):
            # Create checkbox for patch
            display_text = f"{patch.name} - {patch.description}"
            checkbox = QCheckBox(display_text)
            checkbox.setChecked(patch.checked)
            checkbox.setProperty("patch_index", index)

            # Style based on checked state
            if patch.checked:
                checkbox.setStyleSheet(
                    "font-weight: bold; color: #107C10; padding: 5px;"
                )
            else:
                checkbox.setStyleSheet("padding: 5px;")

            # Connect checkbox to handler
            checkbox.stateChanged.connect(lambda state, idx=index: self.on_patch_toggled(idx, state))

            self.checkboxes.append(checkbox)
            self.scroll_layout.addWidget(checkbox)

        self.scroll_layout.addStretch()

    def on_patch_toggled(self, index, state):
        """Handle patch checkbox toggle"""
        from PyQt6.QtCore import Qt

        patch = self.patches[index]
        patch.checked = state == Qt.CheckState.Checked.value

        # Update checkbox style
        self.update_checkbox_style(index)

    def update_checkbox_style(self, index):
        """Update checkbox style based on checked state"""
        checkbox = self.checkboxes[index]
        patch = self.patches[index]
        
        # Block signals while updating to avoid recursion
        checkbox.blockSignals(True)
        checkbox.setChecked(patch.checked)
        checkbox.blockSignals(False)
        
        # Update style
        if patch.checked:
            checkbox.setStyleSheet(
                "font-weight: bold; color: #107C10; padding: 5px;"
            )
        else:
            checkbox.setStyleSheet("padding: 5px;")

    def cancel(self):
        """Handle cancel button - restore original state"""
        # Restore original checked state
        for idx, original_checked in self.original_state.items():
            self.patches[idx].checked = original_checked
        
        self.reject()


def show_acpi_patches_dialog(parent, acpi_guru):
    """
    Show ACPI Patches selection dialog

    Args:
        parent: Parent widget
        acpi_guru: ACPIGuru instance with patches list

    Returns:
        bool: True if OK was clicked, False if canceled
    """
    dialog = ACPIPatchesDialog(acpi_guru, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted
