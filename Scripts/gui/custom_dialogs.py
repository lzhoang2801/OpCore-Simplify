"""
Custom dialog implementations using qfluentwidgets.
Following qfluentwidgets design patterns by extending MessageBoxBase.
"""

import platform

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


class KextsDialog(QDialog):
    """Custom dialog for Kext selection with checkboxes and categorization"""

    def __init__(self, kext_maestro, macos_version, parent=None):
        """
        Initialize Kexts dialog

        Args:
            kext_maestro: KextMaestro instance with kexts list
            macos_version: Target macOS version (Darwin format)
            parent: Parent widget
        """
        super().__init__(parent)
        self.kext_maestro = kext_maestro
        self.kexts = kext_maestro.kexts
        self.macos_version = macos_version
        self.utils = kext_maestro.utils
        self.checkboxes = []  # Store references to checkboxes
        self.original_state = {}  # Store original checked state

        # Store original state
        for idx, kext in enumerate(self.kexts):
            self.original_state[idx] = kext.checked

        self.setWindowTitle("Customize Kernel Extensions")
        self.setMinimumSize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Customize Kernel Extensions")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description
        desc_label = BodyLabel(
            f"Select kernel extensions (kexts) for your system. "
            f"Grayed-out items are not supported by macOS version {self.macos_version}."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(desc_label)

        # Scroll area for kexts
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

        self.populate_kexts()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Give it stretch factor

        # Note
        note_label = BodyLabel(
            "ℹ️ Note: When a plugin of a kext is selected, the entire kext will be automatically "
            "selected. Required kexts cannot be unchecked."
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

    def populate_kexts(self):
        """Populate the kexts list with checkboxes"""
        from PyQt6.QtWidgets import QCheckBox

        current_category = None

        for index, kext in enumerate(self.kexts):
            # Check if kext is supported
            is_supported = (
                self.utils.parse_darwin_version(kext.min_darwin_version) <=
                self.utils.parse_darwin_version(self.macos_version) <=
                self.utils.parse_darwin_version(kext.max_darwin_version)
            )

            # Add category header if changed
            if kext.category != current_category:
                current_category = kext.category
                if self.scroll_layout.count() > 0:  # Add spacing before category
                    self.scroll_layout.addSpacing(10)

                category_label = QLabel(f"Category: {current_category if current_category else 'Uncategorized'}")
                category_label.setStyleSheet(
                    "font-weight: bold; font-size: 13px; color: #323130; "
                    "border-bottom: 2px solid #0078D4; padding: 5px 0px;"
                )
                self.scroll_layout.addWidget(category_label)

            # Create checkbox for kext
            display_text = f"{kext.name} - {kext.description}"
            checkbox = QCheckBox(display_text)
            checkbox.setChecked(kext.checked)
            checkbox.setProperty("kext_index", index)

            # Style based on support status and checked state
            if kext.checked:
                if kext.required:
                    checkbox.setStyleSheet(
                        "font-weight: bold; color: #107C10; padding: 5px;"
                    )
                    checkbox.setEnabled(False)  # Required kexts can't be unchecked
                else:
                    checkbox.setStyleSheet(
                        "font-weight: bold; color: #107C10; padding: 5px;"
                    )
            elif not is_supported:
                checkbox.setStyleSheet(
                    "color: #A19F9D; padding: 5px;"
                )
            else:
                checkbox.setStyleSheet("padding: 5px;")

            # Connect checkbox to handler
            checkbox.stateChanged.connect(lambda state, idx=index: self.on_kext_toggled(idx, state))

            self.checkboxes.append(checkbox)
            self.scroll_layout.addWidget(checkbox)

        self.scroll_layout.addStretch()

    def on_kext_toggled(self, index, state):
        """Handle kext checkbox toggle"""
        from PyQt6.QtCore import Qt

        kext = self.kexts[index]
        
        if state == Qt.CheckState.Checked.value:
            # Check the kext and verify compatibility
            allow_unsupported = self.verify_single_kext_compatibility(index)
            self.kext_maestro.check_kext(index, self.macos_version, allow_unsupported)
        else:
            # Uncheck the kext if it's not required
            if not kext.required:
                self.kext_maestro.uncheck_kext(index)

        # Update all checkboxes to reflect dependencies
        self.update_checkboxes()

    def verify_single_kext_compatibility(self, index):
        """Verify compatibility for a single kext and prompt user if needed"""
        kext = self.kexts[index]
        
        # Check if kext is compatible
        is_compatible = (
            self.utils.parse_darwin_version(kext.min_darwin_version) <=
            self.utils.parse_darwin_version(self.macos_version) <=
            self.utils.parse_darwin_version(kext.max_darwin_version)
        )
        
        if is_compatible:
            return False
        
        # Kext is incompatible - ask user
        # Check if Lilu is in the exact list of required kexts (not substring match)
        is_lilu_dependent = "Lilu" in kext.requires_kexts
        
        message = (
            f"The kext '{kext.name}' is incompatible with macOS version {self.macos_version}.\n\n"
        )
        
        if is_lilu_dependent:
            message += (
                "This is a Lilu plugin. Using the '-lilubetaall' boot argument will force it to load.\n\n"
            )
        
        message += (
            "Forcing unsupported kexts can cause system instability. Proceed with caution.\n\n"
            "Do you want to force load this kext on the unsupported macOS version?"
        )
        
        result = show_question_dialog(
            self,
            "Kext Compatibility Warning",
            message,
            default='no',
            warning='This may cause system instability!'
        )
        
        return result

    def update_checkboxes(self):
        """Update all checkboxes to reflect current state"""
        for index, checkbox in enumerate(self.checkboxes):
            kext = self.kexts[index]
            
            # Block signals while updating to avoid recursion
            checkbox.blockSignals(True)
            checkbox.setChecked(kext.checked)
            checkbox.blockSignals(False)
            
            # Update style
            is_supported = (
                self.utils.parse_darwin_version(kext.min_darwin_version) <=
                self.utils.parse_darwin_version(self.macos_version) <=
                self.utils.parse_darwin_version(kext.max_darwin_version)
            )
            
            if kext.checked:
                if kext.required:
                    checkbox.setStyleSheet(
                        "font-weight: bold; color: #107C10; padding: 5px;"
                    )
                    checkbox.setEnabled(False)
                else:
                    checkbox.setStyleSheet(
                        "font-weight: bold; color: #107C10; padding: 5px;"
                    )
                    checkbox.setEnabled(True)
            elif not is_supported:
                checkbox.setStyleSheet(
                    "color: #A19F9D; padding: 5px;"
                )
                checkbox.setEnabled(True)
            else:
                checkbox.setStyleSheet("padding: 5px;")
                checkbox.setEnabled(True)

    def cancel(self):
        """Handle cancel button - restore original state"""
        # Restore original checked state
        for idx, original_checked in self.original_state.items():
            self.kexts[idx].checked = original_checked
        
        self.reject()


def show_kexts_dialog(parent, kext_maestro, macos_version):
    """
    Show Kexts selection dialog

    Args:
        parent: Parent widget
        kext_maestro: KextMaestro instance with kexts list
        macos_version: Target macOS version (Darwin format)

    Returns:
        bool: True if OK was clicked, False if canceled
    """
    dialog = KextsDialog(kext_maestro, macos_version, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted


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
    """Custom dialog for macOS version selection"""

    def __init__(self, hardware_report, native_macos_version, ocl_patched_macos_version, utils, parent=None):
        """
        Initialize macOS Version dialog

        Args:
            hardware_report: Hardware report data dictionary
            native_macos_version: Tuple of (min, suggested, max) native Darwin versions
            ocl_patched_macos_version: Tuple of (max, min) OCLP Darwin versions or None
            utils: Utils instance for version parsing
            parent: Parent widget
        """
        super().__init__(parent)
        self.hardware_report = hardware_report
        self.native_macos_version = native_macos_version
        self.ocl_patched_macos_version = ocl_patched_macos_version
        self.utils = utils
        self.result_version = None
        
        # Calculate suggested version (same logic as CLI)
        self.suggested_macos_version = self.calculate_suggested_version()
        
        self.setWindowTitle("Select macOS Version")
        self.setMinimumSize(700, 600)
        self.setup_ui()

    def calculate_suggested_version(self):
        """Calculate suggested macOS version based on hardware compatibility"""
        from ..datasets import os_data
        
        suggested_macos_version = self.native_macos_version[1]
        
        # Check device compatibility constraints
        for device_type in ("GPU", "Network", "Bluetooth", "SD Controller"):
            if device_type in self.hardware_report:
                for device_name, device_props in self.hardware_report[device_type].items():
                    if device_props.get("Compatibility", (None, None)) != (None, None):
                        if device_type == "GPU" and device_props.get("Device Type") == "Integrated GPU":
                            device_id = device_props.get("Device ID", "00000000")[5:]

                            if device_props.get("Manufacturer") == "AMD" or device_id.startswith(("59", "87C0")):
                                suggested_macos_version = "22.99.99"
                            elif device_id.startswith(("09", "19")):
                                suggested_macos_version = "21.99.99"

                        if self.utils.parse_darwin_version(suggested_macos_version) > self.utils.parse_darwin_version(device_props.get("Compatibility")[0]):
                            suggested_macos_version = device_props.get("Compatibility")[0]
        
        # Avoid beta versions by decrementing to previous major version
        while True:
            if "Beta" in os_data.get_macos_name_by_darwin(suggested_macos_version):
                suggested_macos_version = "{}{}".format(int(suggested_macos_version[:2]) - 1, suggested_macos_version[2:])
            else:
                break
        
        return suggested_macos_version

    def setup_ui(self):
        """Setup the dialog UI"""
        from ..datasets import os_data
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Select macOS Version")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Suggestion message if suggested differs from native
        if self.native_macos_version[1][:2] != self.suggested_macos_version[:2]:
            suggestion_label = BodyLabel(
                f"Suggested: For better compatibility and stability, we suggest you to use only "
                f"{os_data.get_macos_name_by_darwin(self.suggested_macos_version)} or older."
            )
            suggestion_label.setWordWrap(True)
            suggestion_label.setStyleSheet(f"color: {COLORS['info']}; font-weight: 500; padding: 10px; "
                                          f"background-color: #E1F5FE; border-radius: 4px;")
            layout.addWidget(suggestion_label)

        # Description
        desc_label = BodyLabel("Available macOS versions:")
        desc_label.setStyleSheet("color: #605E5C; font-weight: 500;")
        layout.addWidget(desc_label)

        # Scroll area for versions
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
        self.populate_versions()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Give it stretch factor

        # Note
        note_label = BodyLabel(
            "ℹ️ Note: Versions marked with 'Requires OpenCore Legacy Patcher' need OCLP to enable "
            "dropped GPU and WiFi support. The suggested version is recommended for optimal compatibility."
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
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = PrimaryPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def populate_versions(self):
        """Populate the versions list with radio buttons"""
        from ..datasets import os_data
        
        # Calculate version range
        oclp_min = int(self.ocl_patched_macos_version[-1][:2]) if self.ocl_patched_macos_version else 99
        oclp_max = int(self.ocl_patched_macos_version[0][:2]) if self.ocl_patched_macos_version else 0
        min_version = min(int(self.native_macos_version[0][:2]), oclp_min)
        max_version = max(int(self.native_macos_version[-1][:2]), oclp_max)

        suggested_darwin_major = int(self.suggested_macos_version[:2])

        for darwin_version in range(min_version, max_version + 1):
            name = os_data.get_macos_name_by_darwin(str(darwin_version))
            requires_oclp = oclp_min <= darwin_version <= oclp_max
            
            # Build display text
            display_text = f"{darwin_version}. {name}"
            if requires_oclp:
                display_text += " (Requires OpenCore Legacy Patcher)"
            
            # Create radio button
            radio = QRadioButton(display_text)
            radio.setProperty("darwin_version", darwin_version)
            
            # Style based on suggestion and OCLP requirement
            if darwin_version == suggested_darwin_major:
                radio.setChecked(True)
                radio.setStyleSheet(
                    "font-weight: bold; color: #107C10; padding: 8px;"
                )
            elif requires_oclp:
                radio.setStyleSheet(
                    f"color: {COLORS['warning']}; padding: 8px;"
                )
            else:
                radio.setStyleSheet("padding: 8px;")
            
            # Connect to button group
            self.button_group.addButton(radio, darwin_version)
            self.scroll_layout.addWidget(radio)

        self.scroll_layout.addStretch()

    def accept(self):
        """Handle OK button click"""
        # Get selected radio button
        checked_button = self.button_group.checkedButton()
        if checked_button:
            darwin_major = checked_button.property("darwin_version")
            # Convert to full Darwin version format (e.g., "22.99.99")
            target_version = f"{darwin_major}.99.99"
            
            # Validate the selected version is in valid range (same logic as CLI)
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
                # This shouldn't happen since we only show valid versions
                # but keeping it for safety
                from qfluentwidgets import MessageBox
                MessageBox(
                    "Invalid Version",
                    "The selected version is not valid for your hardware.",
                    self
                ).exec()
                return
        
        super().accept()

    def get_selected_version(self):
        """Return the selected Darwin version"""
        return self.result_version


def show_macos_version_dialog(parent, hardware_report, native_macos_version, ocl_patched_macos_version, utils):
    """
    Show macOS version selection dialog

    Args:
        parent: Parent widget
        hardware_report: Hardware report data dictionary
        native_macos_version: Tuple of (min, suggested, max) native Darwin versions
        ocl_patched_macos_version: Tuple of (max, min) OCLP Darwin versions or None
        utils: Utils instance for version parsing

    Returns:
        tuple: (darwin_version, ok) where darwin_version is selected version and ok is True if OK was clicked
    """
    dialog = MacOSVersionDialog(hardware_report, native_macos_version, ocl_patched_macos_version, utils, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_version(), True
    return None, False


class BeforeUsingEFIDialog(QDialog):
    """Dialog showing requirements before using the built EFI"""

    def __init__(self, bios_requirements, result_dir, parent=None):
        """
        Initialize Before Using EFI dialog
        
        Args:
            bios_requirements: List of BIOS requirement strings
            result_dir: Path to the built EFI result directory
            parent: Parent widget
        """
        super().__init__(parent)
        self.bios_requirements = bios_requirements
        self.result_dir = result_dir
        
        self.setWindowTitle("Before Using EFI")
        self.setMinimumSize(700, 500)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Before Using EFI")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description
        desc_label = BodyLabel("Please complete the following steps:")
        desc_label.setStyleSheet(f"color: {COLORS['warning']}; font-weight: 500; font-size: 14px;")
        layout.addWidget(desc_label)

        # Scroll area for content
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
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(15, 15, 15, 15)

        # BIOS/UEFI Settings section
        if self.bios_requirements:
            bios_label = QLabel("BIOS/UEFI Settings Required:")
            bios_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #323130;")
            scroll_layout.addWidget(bios_label)
            
            for requirement in self.bios_requirements:
                req_label = BodyLabel(f"  • {requirement}")
                req_label.setWordWrap(True)
                req_label.setStyleSheet("padding-left: 10px; color: #605E5C;")
                scroll_layout.addWidget(req_label)
            
            scroll_layout.addSpacing(10)

        # USB Mapping section
        usb_label = QLabel("USB Mapping:")
        usb_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #323130;")
        scroll_layout.addWidget(usb_label)

        # Determine path separator based on OS
        path_sep = "\\" if platform.system() == "Windows" else "/"
        kexts_path = f"EFI{path_sep}OC{path_sep}Kexts"
        
        usb_instructions = [
            "Use USBToolBox tool to map USB ports.",
            f"Add created UTBMap.kext into the {kexts_path} folder.",
            f"Remove UTBDefault.kext in the {kexts_path} folder.",
            "Edit config.plist:",
            "  - Use ProperTree to open your config.plist.",
            "  - Run OC Snapshot by pressing Command/Ctrl + R.",
            "  - If you have more than 15 ports on a single controller, enable the XhciPortLimit patch.",
            "  - Save the file when finished."
        ]
        
        for instruction in usb_instructions:
            inst_label = BodyLabel(f"  • {instruction}")
            inst_label.setWordWrap(True)
            inst_label.setStyleSheet("padding-left: 10px; color: #605E5C;")
            scroll_layout.addWidget(inst_label)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        # Agreement section
        agreement_label = BodyLabel(
            'Type "AGREE" below to acknowledge these requirements and open the built EFI folder.'
        )
        agreement_label.setWordWrap(True)
        agreement_label.setStyleSheet("font-weight: 500; color: #323130; margin-top: 10px;")
        layout.addWidget(agreement_label)

        # Input field for AGREE
        self.agree_input = LineEdit()
        self.agree_input.setPlaceholderText('Type "AGREE" here...')
        layout.addWidget(self.agree_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        # Cancel button
        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # OK button
        ok_btn = PrimaryPushButton("Open EFI Folder")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def accept(self):
        """Handle OK button - validate AGREE input"""
        if self.agree_input.text().strip().upper() == "AGREE":
            super().accept()
        else:
            # Show error message
            MessageBox(
                "Invalid Input",
                'Please type "AGREE" to acknowledge the requirements.',
                self
            ).exec()


def show_before_using_efi_dialog(parent, bios_requirements, result_dir):
    """
    Show Before Using EFI dialog
    
    Args:
        parent: Parent widget
        bios_requirements: List of BIOS requirement strings
        result_dir: Path to the built EFI result directory
    
    Returns:
        bool: True if AGREE was typed and OK clicked, False otherwise
    """
    dialog = BeforeUsingEFIDialog(bios_requirements, result_dir, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted
