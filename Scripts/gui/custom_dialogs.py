"""
Custom dialog implementations using qfluentwidgets.
Following qfluentwidgets design patterns by extending MessageBoxBase.
"""

from PyQt6.QtWidgets import (
    QLabel, QDialog, QVBoxLayout, QHBoxLayout,
    QScrollArea, QWidget, QPushButton, QButtonGroup,
    QRadioButton
)
from PyQt6.QtCore import Qt
from qfluentwidgets import MessageBoxBase, LineEdit, ComboBox, MessageBox, PushButton, PrimaryPushButton, BodyLabel

from .styles import COLORS


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

        # Populate combo box and build descriptions text
        descriptions_text = []
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
            self.descriptionsLabel = QLabel(
                '\n'.join(descriptions_text), self.widget)
            self.descriptionsLabel.setWordWrap(True)
            self.descriptionsLabel.setStyleSheet(
                f"color: {COLORS['text_secondary']}; margin-top: 10px; font-size: 12px;")
            self.viewLayout.addWidget(self.descriptionsLabel)

        # Add warning or note if provided
        if warning:
            self.warningLabel = QLabel(f"⚠️ {warning}", self.widget)
            self.warningLabel.setWordWrap(True)
            # Using theme-aware warning color
            self.warningLabel.setStyleSheet(
                f"color: {COLORS['warning']}; margin-top: 10px; font-weight: 500;")
            self.viewLayout.addWidget(self.warningLabel)
        elif note:
            self.noteLabel = QLabel(f"ℹ️ {note}", self.widget)
            self.noteLabel.setWordWrap(True)
            # Using theme-aware info color
            self.noteLabel.setStyleSheet(
                f"color: {COLORS['info']}; margin-top: 10px; font-weight: 500;")
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


class InfoMessageBox(MessageBoxBase):
    """Info dialog using qfluentwidgets MessageBoxBase pattern with better support for long content"""

    def __init__(self, title: str, content: str, parent=None):
        """
        Initialize info dialog

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
        self.widget.setMinimumWidth(600)

        # Hide cancel button for info dialogs
        self.cancelButton.hide()
        self.yesButton.setText("OK")


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

    dialog = ChoiceMessageBox(title, content, choices,
                              default_value, warning, note, parent)
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

    # exec() returns QDialog.DialogCode.Accepted if Yes is clicked, Rejected otherwise
    return dialog.exec() == QDialog.DialogCode.Accepted


def show_info_dialog(parent, title: str, content: str):
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


class SMBIOSDialog(QDialog):
    """Custom dialog for SMBIOS model selection with filtering and categorization"""

    def __init__(self, mac_devices, selected_model, default_model, macos_version, is_laptop, utils, parent=None):
        """
        Initialize SMBIOS dialog

        Args:
            mac_devices: List of MacDevice objects
            selected_model: Currently selected SMBIOS model
            default_model: Default/recommended SMBIOS model
            macos_version: Target macOS version (Darwin format)
            is_laptop: Boolean indicating if hardware is laptop
            utils: Utils instance for version parsing
            parent: Parent widget
        """
        super().__init__(parent)
        self.mac_devices = mac_devices
        self.selected_model = selected_model
        self.default_model = default_model
        self.macos_version = macos_version
        self.is_laptop = is_laptop
        self.utils = utils
        self.show_all_models = False
        self.result_model = selected_model

        self.setWindowTitle("Customize SMBIOS Model")
        self.setMinimumSize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Customize SMBIOS Model")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description
        desc_label = BodyLabel(
            "Compatible models only" if not self.show_all_models else "All available models"
        )
        desc_label.setStyleSheet("color: #605E5C;")
        self.desc_label = desc_label
        layout.addWidget(desc_label)

        # Scroll area for models
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
        self.populate_models()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Give it stretch factor

        # Note
        note_label = BodyLabel(
            f"ℹ️ Note: Grayed-out models are not officially supported by this macOS version."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 5px;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Show all/compatible toggle
        self.toggle_btn = PushButton(
            "Show All Models" if not self.show_all_models else "Show Compatible Only"
        )
        self.toggle_btn.clicked.connect(self.toggle_filter)
        button_layout.addWidget(self.toggle_btn)

        # Restore default button
        if self.selected_model != self.default_model:
            self.restore_btn = PushButton(f"Restore Default ({self.default_model})")
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

    def populate_models(self):
        """Populate the models list with radio buttons"""
        # Clear existing widgets
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_category = None

        for index, device in enumerate(self.mac_devices):
            # Check if model is supported
            is_supported = (
                self.utils.parse_darwin_version(device.initial_support) <=
                self.utils.parse_darwin_version(self.macos_version) <=
                self.utils.parse_darwin_version(device.last_supported_version)
            )

            # Filter logic (same as CLI)
            if (device.name not in (self.default_model, self.selected_model) and
                not self.show_all_models and
                (not is_supported or
                 (self.is_laptop and not device.name.startswith("MacBook")) or
                 (not self.is_laptop and device.name.startswith("MacBook")))):
                continue

            # Extract category (e.g., "iMac", "MacBookPro")
            category = device.name.split(next((char for char in device.name if char.isdigit()), ''))[0]

            # Add category header if changed
            if category != current_category:
                current_category = category
                if self.scroll_layout.count() > 0:  # Add spacing before category
                    self.scroll_layout.addSpacing(10)

                category_label = QLabel(f"Category: {category if category else 'Uncategorized'}")
                category_label.setStyleSheet(
                    "font-weight: bold; font-size: 13px; color: #323130; "
                    "border-bottom: 2px solid #0078D4; padding: 5px 0px;"
                )
                self.scroll_layout.addWidget(category_label)

            # Create radio button for model
            display_text = f"{device.name} - {device.cpu} ({device.cpu_generation})"
            if device.discrete_gpu:
                display_text += f" - {device.discrete_gpu}"

            radio = QRadioButton(display_text)
            radio.setProperty("model_name", device.name)
            radio.setProperty("device_index", index)

            # Style based on support status
            if device.name == self.selected_model:
                radio.setChecked(True)
                radio.setStyleSheet(
                    "font-weight: bold; color: #107C10; padding: 5px;"
                )
            elif not is_supported:
                radio.setStyleSheet(
                    "color: #A19F9D; padding: 5px;"
                )
            else:
                radio.setStyleSheet("padding: 5px;")

            # Connect to button group
            self.button_group.addButton(radio, index)
            self.scroll_layout.addWidget(radio)

        self.scroll_layout.addStretch()

    def toggle_filter(self):
        """Toggle between showing all models and compatible models only"""
        self.show_all_models = not self.show_all_models
        self.toggle_btn.setText(
            "Show All Models" if not self.show_all_models else "Show Compatible Only"
        )
        self.desc_label.setText(
            "Compatible models only" if not self.show_all_models else "All available models"
        )
        self.populate_models()

    def restore_default(self):
        """Restore the default SMBIOS model"""
        self.result_model = self.default_model
        self.selected_model = self.default_model
        self.populate_models()

    def accept(self):
        """Handle OK button click"""
        # Get selected radio button
        checked_button = self.button_group.checkedButton()
        if checked_button:
            self.result_model = checked_button.property("model_name")
        super().accept()

    def get_selected_model(self):
        """Return the selected model"""
        return self.result_model


def show_smbios_dialog(parent, mac_devices, selected_model, default_model, macos_version, is_laptop, utils):
    """
    Show SMBIOS model selection dialog

    Args:
        parent: Parent widget
        mac_devices: List of MacDevice objects
        selected_model: Currently selected SMBIOS model
        default_model: Default/recommended SMBIOS model
        macos_version: Target macOS version (Darwin format)
        is_laptop: Boolean indicating if hardware is laptop
        utils: Utils instance for version parsing

    Returns:
        tuple: (model_name, ok) where model_name is selected model and ok is True if OK was clicked
    """
    dialog = SMBIOSDialog(mac_devices, selected_model, default_model, macos_version, is_laptop, utils, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_model(), True
    return selected_model, False
