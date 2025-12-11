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


class MacOSVersionDialog(QDialog):
    def __init__(self, parent, native_macos_version, ocl_patched_macos_version, suggested_version, utils):
        super().__init__(parent)
        self.parent = parent
        self.native_macos_version = native_macos_version
        self.ocl_patched_macos_version = ocl_patched_macos_version
        self.suggested_version = suggested_version
        self.utils = utils
        self.result_version = None
        self.button_group = QButtonGroup(self)

        self.setWindowTitle("Select macOS Version")
        self.setMinimumSize(700, 600)
        self.dialog()

    def dialog(self):        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Select macOS Version")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        if self.native_macos_version[1][:2] != self.suggested_version[:2]:
            suggestion_label = BodyLabel(
                f"Suggested: For better compatibility and stability, we suggest you to use only "
                f"{os_data.get_macos_name_by_darwin(self.suggested_version)} or older."
            )
            suggestion_label.setWordWrap(True)
            suggestion_label.setStyleSheet(f"color: {COLORS['info']}; font-weight: 500; padding: 10px; "
                                          f"background-color: #E1F5FE; border-radius: 4px;")
            layout.addWidget(suggestion_label)

        desc_label = BodyLabel("Available macOS versions:")
        desc_label.setStyleSheet("color: #605E5C; font-weight: 500;")
        layout.addWidget(desc_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E1DFDD;
                border-radius: 4px;
                background-color: white;
            }
        """)

        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)

        self.button_group = QButtonGroup(self)
        self.populate_versions()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        note_label = BodyLabel(
            "ℹ️ Note: Versions marked with 'Requires OpenCore Legacy Patcher' need OCLP to enable "
            "dropped GPU and WiFi support. The suggested version is recommended for optimal compatibility."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 5px;")
        layout.addWidget(note_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = PrimaryPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def populate_versions(self):
        oclp_min = int(self.ocl_patched_macos_version[-1][:2]) if self.ocl_patched_macos_version else 99
        oclp_max = int(self.ocl_patched_macos_version[0][:2]) if self.ocl_patched_macos_version else 0
        native_min = int(self.native_macos_version[0][:2])
        native_max = int(self.native_macos_version[-1][:2])

        suggested_label = "(Suggested for you)"
        suggested_darwin_major = int(
            self.suggested_version.split('.')[0]) if self.suggested_version else -1

        for darwin_major in range(min(native_min, oclp_min), max(native_max, oclp_max) + 1):
            is_oclp = oclp_min <= darwin_major <= oclp_max
            is_native = native_min <= darwin_major <= native_max

            if not is_oclp and not is_native:
                continue

            name = os_data.get_macos_name_by_darwin(str(darwin_major))
            is_suggested = (darwin_major == suggested_darwin_major)

            self.create_version_radio_button(
                darwin_major, name, is_oclp, is_suggested, suggested_label)

        self.scroll_layout.addStretch()

    def create_version_radio_button(self, darwin_major, name, is_oclp, is_suggested, suggested_label):
        display_text = f"{darwin_major}. {name}"
        if is_oclp:
            display_text += " (Requires OpenCore Legacy Patcher)"
        if is_suggested:
            display_text += f" {suggested_label}"

        radio = QRadioButton(display_text)
        radio.setProperty("darwin_version", darwin_major)
        
        if is_suggested:
            radio.setStyleSheet(
                "font-weight: bold; color: #107C10; padding: 8px;"
            )
        elif is_oclp:
            radio.setStyleSheet(
                f"color: {COLORS['warning']}; padding: 8px;"
            )
        else:
            radio.setStyleSheet("padding: 8px;")
        
        self.button_group.addButton(radio, darwin_major)
        self.scroll_layout.addWidget(radio)

    def accept(self):
        checked_button = self.button_group.checkedButton()
        if checked_button:
            darwin_major = checked_button.property("darwin_version")
            target_version = f"{darwin_major}.99.99"
            
            is_valid = False
            if self.ocl_patched_macos_version:
                if (self.utils.parse_darwin_version(self.ocl_patched_macos_version[-1]) <= 
                    self.utils.parse_darwin_version(target_version) <= 
                    self.utils.parse_darwin_version(self.ocl_patched_macos_version[0])):
                    is_valid = True
            
            if not is_valid:
                if (self.utils.parse_darwin_version(self.native_macos_version[0]) <= 
                    self.utils.parse_darwin_version(target_version) <= 
                    self.utils.parse_darwin_version(self.native_macos_version[-1])):
                    is_valid = True
            
            if is_valid:
                self.result_version = target_version
            else:
                MessageBox(
                    "Invalid Version",
                    "The selected version is not valid for your hardware.",
                    self
                ).exec()
                return
        
        super().accept()

    def get_selected_version(self):
        return self.result_version


def show_macos_version_dialog(parent, native_macos_version, ocl_patched_macos_version, suggested_version, utils):
    dialog = MacOSVersionDialog(parent, native_macos_version, ocl_patched_macos_version, suggested_version, utils)
    result = dialog.exec()
    selected_version = dialog.get_selected_version()
    return selected_version, result == QDialog.DialogCode.Accepted

class CodecLayoutDialog(QDialog):
    """Custom dialog for audio codec layout selection"""

    def __init__(self, codec_id, available_layouts, default_layout, recommended_layouts, parent=None):
        """
        Initialize Codec Layout dialog

        Args:
            codec_id: Audio codec device ID
            available_layouts: List of Layout objects with id and comment
            default_layout: Default/recommended Layout object
            recommended_layouts: List of recommended Layout objects
            parent: Parent widget
        """
        super().__init__(parent)
        self.codec_id = codec_id
        self.available_layouts = available_layouts
        self.default_layout = default_layout
        self.recommended_layouts = recommended_layouts
        self.selected_layout = default_layout
        self.result_layout_id = default_layout.id if default_layout else None

        self.setWindowTitle("Choosing Codec Layout ID")
        self.setMinimumSize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Choosing Codec Layout ID")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description with codec ID
        desc_label = BodyLabel(
            f"Select the audio codec layout for {self.codec_id}.\n"
            f"Recommended layouts are from trusted authors (Mirone, InsanelyDeepak, Toleda, DalianSky)."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(desc_label)

        # Scroll area for layouts
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

        # Radio button group
        self.button_group = QButtonGroup(self)
        self.populate_layouts()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Give it stretch factor

        # Note
        note_label = BodyLabel(
            "ℹ️ Note: The default layout (marked with ⭐) may not be optimal. "
            "Test different layouts to find what works best for your system."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 5px;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Restore default button
        if self.selected_layout != self.default_layout:
            self.restore_btn = PushButton(f"Restore Default (ID: {self.default_layout.id})")
            self.restore_btn.clicked.connect(self.restore_default)
            button_layout.addWidget(self.restore_btn)

        button_layout.addStretch()

        # Cancel and OK buttons
        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = PrimaryPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def populate_layouts(self):
        """Populate the layouts list with radio buttons"""
        # Clear existing widgets
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get recommended layout IDs for quick lookup
        recommended_ids = [layout.id for layout in self.recommended_layouts] if self.recommended_layouts else []

        # Add recommended section header if there are recommended layouts
        if recommended_ids:
            recommended_header = QLabel("⭐ Recommended Layouts")
            recommended_header.setStyleSheet(
                "font-weight: bold; font-size: 13px; color: #107C10; "
                "border-bottom: 2px solid #107C10; padding: 5px 0px; margin-top: 5px;"
            )
            self.scroll_layout.addWidget(recommended_header)

            # Add recommended layouts first
            for index, layout in enumerate(self.available_layouts):
                if layout.id in recommended_ids:
                    self._add_layout_radio(index, layout, is_recommended=True)

            # Add separator
            self.scroll_layout.addSpacing(15)
            
            # Other layouts header
            other_header = QLabel("Other Available Layouts")
            other_header.setStyleSheet(
                "font-weight: bold; font-size: 13px; color: #605E5C; "
                "border-bottom: 2px solid #E1DFDD; padding: 5px 0px;"
            )
            self.scroll_layout.addWidget(other_header)

        # Add other layouts
        for index, layout in enumerate(self.available_layouts):
            if not recommended_ids or layout.id not in recommended_ids:
                self._add_layout_radio(index, layout, is_recommended=False)

        self.scroll_layout.addStretch()

    def _add_layout_radio(self, index, layout, is_recommended):
        """Helper method to add a radio button for a layout"""
        # Format display text
        star = "⭐ " if is_recommended else ""
        display_text = f"{star}ID {layout.id:3d} - {layout.comment or 'No description'}"

        radio = QRadioButton(display_text)
        radio.setProperty("layout_id", layout.id)
        radio.setProperty("layout_index", index)

        # Check if this is the selected layout
        if layout.id == self.selected_layout.id:
            radio.setChecked(True)
            radio.setStyleSheet(
                "font-weight: bold; color: #107C10; padding: 5px;"
            )
        elif is_recommended:
            radio.setStyleSheet(
                "color: #323130; padding: 5px;"
            )
        else:
            radio.setStyleSheet(
                "color: #605E5C; padding: 5px;"
            )

        # Connect to button group
        self.button_group.addButton(radio, index)
        self.scroll_layout.addWidget(radio)

    def restore_default(self):
        """Restore the default codec layout"""
        self.selected_layout = self.default_layout
        self.result_layout_id = self.default_layout.id
        self.populate_layouts()

    def accept(self):
        """Handle OK button click"""
        # Get selected radio button
        checked_button = self.button_group.checkedButton()
        if checked_button:
            layout_id = checked_button.property("layout_id")
            self.result_layout_id = layout_id
            
            # Find and store the selected layout object
            for layout in self.available_layouts:
                if layout.id == layout_id:
                    self.selected_layout = layout
                    break
        
        super().accept()

    def get_selected_layout_id(self):
        """Return the selected layout ID"""
        return self.result_layout_id


def show_codec_layout_dialog(parent, codec_id, available_layouts, default_layout, recommended_layouts):
    """
    Show Codec Layout selection dialog

    Args:
        parent: Parent widget
        codec_id: Audio codec device ID
        available_layouts: List of Layout objects with id and comment
        default_layout: Default/recommended Layout object
        recommended_layouts: List of recommended Layout objects

    Returns:
        tuple: (layout_id, ok) where layout_id is selected ID and ok is True if OK was clicked
    """
    dialog = CodecLayoutDialog(codec_id, available_layouts, default_layout, recommended_layouts, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_layout_id(), True
    return None, False

