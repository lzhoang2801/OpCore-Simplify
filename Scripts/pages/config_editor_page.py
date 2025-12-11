"""
Config.plist Editor Page - TreeView-based plist editor with OC Snapshot functionality
"""

import json
import os
import plistlib
from collections import OrderedDict
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
    QTreeWidgetItem, QTreeWidgetItemIterator
)
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CardWidget,
    StrongBodyLabel, FluentIcon,
    InfoBar, InfoBarPosition, MessageBox, ComboBox as FluentComboBox,
    SearchLineEdit, TreeWidget, RoundMenu, CommandBar, Action,
    MessageBoxBase, LineEdit, SpinBox as FluentSpinBox,
    PlainTextEdit
)

from ..styles import COLORS, SPACING
from ...datasets import kext_data

# Constants
MAX_UNDO_LEVELS = 50
OC_STORAGE_SAFE_PATH_MAX = 128

# Default values by type
TYPE_DEFAULTS = {
    "String": "",
    "Number": 0,
    "Boolean": False,
    "Dictionary": OrderedDict(),
    "Array": [],
    "Data": b""
}


class AddDictKeyDialog(MessageBoxBase):
    """Fluent Design dialog for adding a dictionary key"""
    
    def __init__(self, parent=None, existing_keys=None):
        super().__init__(parent)
        self.existing_keys = existing_keys or []
        
        self.titleLabel = SubtitleLabel("Add Dictionary Key")
        self.key_name_label = BodyLabel("Key Name:")
        self.key_name_input = LineEdit()
        self.key_name_input.setPlaceholderText("Enter unique key name...")
        self.key_name_input.setClearButtonEnabled(True)
        
        self.type_label = BodyLabel("Value Type:")
        self.type_combo = FluentComboBox()
        self.type_combo.addItems(["String", "Number", "Boolean", "Dictionary", "Array", "Data"])
        self.type_combo.setCurrentIndex(0)
        
        # Add widgets to dialog
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.key_name_label)
        self.viewLayout.addWidget(self.key_name_input)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.type_label)
        self.viewLayout.addWidget(self.type_combo)
        
        self.yesButton.setText("Add")
        self.cancelButton.setText("Cancel")
        
        # Set dialog size
        self.widget.setMinimumWidth(400)
        
        # Connect validation to yes button
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self._on_yes_clicked)
        
    def _on_yes_clicked(self):
        """Handle yes button click with validation"""
        if self.validate():
            self.accept()
        
    def validate(self):
        """Validate the input before accepting"""
        key_name = self.key_name_input.text().strip()
        if not key_name:
            InfoBar.warning(
                title="Invalid Input",
                content="Key name cannot be empty",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return False
        
        if key_name in self.existing_keys:
            InfoBar.warning(
                title="Duplicate Key",
                content=f"Key '{key_name}' already exists",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return False
        
        return True
    
    def get_values(self):
        """Get the input values"""
        return self.key_name_input.text().strip(), self.type_combo.currentText()


class AddArrayItemDialog(MessageBoxBase):
    """Fluent Design dialog for adding an array item"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.titleLabel = SubtitleLabel("Add Array Item")
        self.type_label = BodyLabel("Select the type of item to add:")
        self.type_combo = FluentComboBox()
        self.type_combo.addItems(["String", "Number", "Boolean", "Dictionary", "Array"])
        self.type_combo.setCurrentIndex(0)
        
        # Add widgets to dialog
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.type_label)
        self.viewLayout.addWidget(self.type_combo)
        
        self.yesButton.setText("Add")
        self.cancelButton.setText("Cancel")
        
        # Set dialog size
        self.widget.setMinimumWidth(350)
        
    def get_value_type(self):
        """Get the selected type"""
        return self.type_combo.currentText()


class ValueEditDialog(MessageBoxBase):
    """Fluent Design dialog for editing plist values"""
    
    def __init__(self, parent, value_type, current_value):
        super().__init__(parent)
        self.value_type = value_type
        self.current_value = current_value
        
        self.titleLabel = SubtitleLabel(f"Edit {value_type}")
        
        # Create appropriate input widget based on type
        if value_type == "Boolean":
            self.value_label = BodyLabel("Select the boolean value:")
            self.widget = FluentComboBox()
            self.widget.addItems(["true", "false"])
            self.widget.setCurrentText("true" if current_value else "false")
        elif value_type == "Number":
            self.value_label = BodyLabel("Enter new number value:")
            self.widget = FluentSpinBox()
            self.widget.setRange(-2147483648, 2147483647)
            self.widget.setValue(current_value)
        elif value_type == "String":
            self.value_label = BodyLabel("Enter new string value:")
            self.widget = LineEdit()
            self.widget.setText(current_value)
            self.widget.setClearButtonEnabled(True)
            self.widget.setPlaceholderText("Enter text...")
        elif value_type == "Data":
            self.value_label = BodyLabel("Enter hexadecimal data (without 0x prefix):")
            self.widget = PlainTextEdit()
            self.widget.setPlainText(current_value.hex())
            self.widget.setMaximumHeight(150)
            self.widget.setPlaceholderText("Enter hex bytes (e.g., A1B2C3)...")
        else:
            self.value_label = BodyLabel(f"Enter new {value_type.lower()} value:")
            self.widget = LineEdit()
            self.widget.setText(str(current_value))
            self.widget.setClearButtonEnabled(True)
        
        # Add widgets to dialog
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.value_label)
        self.viewLayout.addWidget(self.widget)
        
        self.yesButton.setText("Save")
        self.cancelButton.setText("Cancel")
        
        # Set dialog size
        self.widget.setMinimumWidth(400)
    
    def get_value(self):
        """Get the edited value"""
        if self.value_type == "Boolean":
            return self.widget.currentText() == "true"
        elif self.value_type == "Number":
            return self.widget.value()
        elif self.value_type == "String":
            return self.widget.text()
        elif self.value_type == "Data":
            try:
                return bytes.fromhex(self.widget.toPlainText().replace(" ", ""))
            except (ValueError, AttributeError):
                return self.current_value
        else:
            return self.widget.text()


class PlistTreeWidget(TreeWidget):
    """Custom TreeWidget for displaying and editing plist data with drag-and-drop using Fluent Design"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_page = None  # Will be set by ConfigEditorPage
        self.setHeaderLabels(["Key", "Type", "Value"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 400)
        self.itemDoubleClicked.connect(self.edit_item)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(TreeWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        
    def show_context_menu(self, position):
        """Show context menu for tree items using Fluent Design RoundMenu"""
        item = self.itemAt(position)
        if not item:
            return
        
        menu = RoundMenu(parent=self)
        item_type = item.text(1)
        
        # Add actions based on item type
        if item_type == "Array":
            add_action = Action(FluentIcon.ADD, "Add Item")
            add_action.triggered.connect(lambda: self.add_array_item(item))
            menu.addAction(add_action)
        
        if item_type == "Dictionary":
            add_key_action = Action(FluentIcon.ADD, "Add Key")
            add_key_action.triggered.connect(lambda: self.add_dict_key(item))
            menu.addAction(add_key_action)
        
        # Remove actions for items within arrays or dictionaries
        # Allow removing any item (including Dictionary and Array) if it has a parent
        if item.parent():
            parent_type = item.parent().text(1)
            if parent_type == "Array":
                remove_action = Action(FluentIcon.DELETE, "Remove Item")
                remove_action.triggered.connect(lambda: self.remove_array_item(item))
                menu.addAction(remove_action)
            elif parent_type == "Dictionary":
                remove_key_action = Action(FluentIcon.DELETE, "Remove Key")
                remove_key_action.triggered.connect(lambda: self.remove_dict_key(item))
                menu.addAction(remove_key_action)
        
        if menu.actions():
            menu.exec(self.viewport().mapToGlobal(position))
    
    def add_dict_key(self, dict_item):
        """Add a new key to a dictionary using Fluent Design dialog"""
        # Get existing keys
        existing_keys = [dict_item.child(i).text(0) for i in range(dict_item.childCount())]
        
        # Show custom dialog (validation happens automatically)
        # Parent to main window and make modal
        dialog = AddDictKeyDialog(self.window(), existing_keys)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        if dialog.exec():
            key_name, value_type = dialog.get_values()
            
            # Create new item
            new_item = QTreeWidgetItem(dict_item)
            new_item.setText(0, key_name)
            
            # Set default value based on type
            if value_type == "String":
                new_item.setText(1, "String")
                new_item.setText(2, "")
                new_item.setData(2, Qt.ItemDataRole.UserRole, "")
            elif value_type == "Number":
                new_item.setText(1, "Number")
                new_item.setText(2, "0")
                new_item.setData(2, Qt.ItemDataRole.UserRole, 0)
            elif value_type == "Boolean":
                new_item.setText(1, "Boolean")
                new_item.setText(2, "false")
                new_item.setData(2, Qt.ItemDataRole.UserRole, False)
            elif value_type == "Dictionary":
                new_item.setText(1, "Dictionary")
                new_item.setText(2, "0 items")
                new_item.setData(2, Qt.ItemDataRole.UserRole, OrderedDict())
            elif value_type == "Array":
                new_item.setText(1, "Array")
                new_item.setText(2, "0 items")
                new_item.setData(2, Qt.ItemDataRole.UserRole, [])
            elif value_type == "Data":
                new_item.setText(1, "Data")
                new_item.setText(2, "")
                new_item.setData(2, Qt.ItemDataRole.UserRole, b"")
            
            dict_item.setExpanded(True)
            
            # Save state for undo
            if self.editor_page:
                self.editor_page.save_state()
    
    def remove_dict_key(self, item):
        """Remove a key from a dictionary using Fluent Design confirmation"""
        key_name = item.text(0)
        item_type = item.text(1)
        
        # Create confirmation dialog with item type info
        # Parent to main window and make modal
        w = MessageBox(
            "Remove Dictionary Key",
            f"Are you sure you want to remove the key '{key_name}' ({item_type})?\n\nThis action can be undone.",
            self.window()
        )
        w.setWindowModality(Qt.WindowModality.ApplicationModal)
        w.yesButton.setText("Remove")
        w.cancelButton.setText("Cancel")
        
        if w.exec():
            parent = item.parent()
            if parent:
                index = parent.indexOfChild(item)
                parent.takeChild(index)
                
                # Save state for undo
                if self.editor_page:
                    self.editor_page.save_state()
                    
                # Show success message
                InfoBar.success(
                    title='Key Removed',
                    content=f"Key '{key_name}' ({item_type}) removed successfully",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self.window()
                )
    
    def add_array_item(self, array_item):
        """Add a new item to an array using Fluent Design dialog"""
        # Show custom dialog
        # Parent to main window and make modal
        dialog = AddArrayItemDialog(self.window())
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        if dialog.exec():
            item_type = dialog.get_value_type()
            
            # Create new item
            index = array_item.childCount()
            new_item = QTreeWidgetItem(array_item)
            new_item.setText(0, f"Item {index}")
            
            # Set default value based on type
            if item_type == "String":
                new_item.setText(1, "String")
                new_item.setText(2, "")
                new_item.setData(2, Qt.ItemDataRole.UserRole, "")
            elif item_type == "Number":
                new_item.setText(1, "Number")
                new_item.setText(2, "0")
                new_item.setData(2, Qt.ItemDataRole.UserRole, 0)
            elif item_type == "Boolean":
                new_item.setText(1, "Boolean")
                new_item.setText(2, "false")
                new_item.setData(2, Qt.ItemDataRole.UserRole, False)
            elif item_type == "Dictionary":
                new_item.setText(1, "Dictionary")
                new_item.setText(2, "0 items")
                new_item.setData(2, Qt.ItemDataRole.UserRole, OrderedDict())
            elif value_type == "Array":
                new_item.setText(1, "Array")
                new_item.setText(2, "0 items")
                new_item.setData(2, Qt.ItemDataRole.UserRole, [])
            
            array_item.setExpanded(True)
            
            # Save state for undo
            if self.editor_page:
                self.editor_page.save_state()
    
    def remove_array_item(self, item):
        """Remove an item from an array using Fluent Design confirmation"""
        item_name = item.text(0)
        item_type = item.text(1)
        
        # Create confirmation dialog
        # Parent to main window and make modal
        w = MessageBox(
            "Remove Array Item",
            f"Are you sure you want to remove '{item_name}' ({item_type})?\n\nThis action can be undone.",
            self.window()
        )
        w.setWindowModality(Qt.WindowModality.ApplicationModal)
        w.yesButton.setText("Remove")
        w.cancelButton.setText("Cancel")
        
        if w.exec():
            parent = item.parent()
            if parent:
                index = parent.indexOfChild(item)
                parent.takeChild(index)
                
                # Renumber remaining items
                for i in range(parent.childCount()):
                    child = parent.child(i)
                    child.setText(0, f"Item {i}")
                
                # Save state for undo
                if self.editor_page:
                    self.editor_page.save_state()
                    
                # Show success message
                InfoBar.success(
                    title='Item Removed',
                    content=f"Array item '{item_name}' removed successfully",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self.window()
                )
        
    def populate_tree(self, data, parent=None):
        """Populate tree with plist data"""
        if parent is None:
            self.clear()
            parent = self.invisibleRootItem()
            
        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem(parent)
                item.setText(0, str(key))
                self._set_item_value(item, value)
                if isinstance(value, (dict, list)):
                    self.populate_tree(value, item)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = QTreeWidgetItem(parent)
                item.setText(0, f"Item {i}")
                self._set_item_value(item, value)
                if isinstance(value, (dict, list)):
                    self.populate_tree(value, item)
    
    def _set_item_value(self, item, value):
        """Set item type and value based on data type"""
        if isinstance(value, bool):
            item.setText(1, "Boolean")
            item.setText(2, "true" if value else "false")
            item.setData(2, Qt.ItemDataRole.UserRole, value)
        elif isinstance(value, int):
            item.setText(1, "Number")
            item.setText(2, str(value))
            item.setData(2, Qt.ItemDataRole.UserRole, value)
        elif isinstance(value, str):
            item.setText(1, "String")
            item.setText(2, value)
            item.setData(2, Qt.ItemDataRole.UserRole, value)
        elif isinstance(value, bytes):
            item.setText(1, "Data")
            item.setText(2, value.hex()[:50] + "..." if len(value) > 25 else value.hex())
            item.setData(2, Qt.ItemDataRole.UserRole, value)
        elif isinstance(value, dict):
            item.setText(1, "Dictionary")
            item.setText(2, f"{len(value)} items")
            item.setData(2, Qt.ItemDataRole.UserRole, value)
        elif isinstance(value, list):
            item.setText(1, "Array")
            item.setText(2, f"{len(value)} items")
            item.setData(2, Qt.ItemDataRole.UserRole, value)
        else:
            item.setText(1, "Unknown")
            item.setText(2, str(value))
            item.setData(2, Qt.ItemDataRole.UserRole, value)
    
    def edit_item(self, item, column):
        """Edit item value when double-clicked using Fluent Design dialog"""
        if column != 2:  # Only allow editing the value column
            return
            
        item_type = item.text(1)
        current_value = item.data(2, Qt.ItemDataRole.UserRole)
        
        # Don't allow editing containers
        if item_type in ("Dictionary", "Array"):
            return
        
        # Parent to main window and make modal
        dialog = ValueEditDialog(self.window(), item_type, current_value)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        if dialog.exec():
            new_value = dialog.get_value()
            item.setData(2, Qt.ItemDataRole.UserRole, new_value)
            self._set_item_value(item, new_value)
            
            # Save state for undo
            if self.editor_page:
                self.editor_page.save_state()
    
    def get_tree_data(self):
        """Extract data from tree back to dictionary/list format"""
        return self._get_item_data(self.invisibleRootItem())
    
    def _get_item_data(self, parent):
        """Recursively extract data from tree items"""
        child_count = parent.childCount()
        
        # Check if this is a root or if parent is array
        if parent == self.invisibleRootItem():
            # Root level - assume dictionary
            result = OrderedDict()
            for i in range(child_count):
                child = parent.child(i)
                key = child.text(0)
                value = self._get_single_item_data(child)
                result[key] = value
            return result
        
        # Check parent type
        parent_type = parent.text(1) if parent != self.invisibleRootItem() else "Dictionary"
        
        if parent_type == "Array":
            result = []
            for i in range(child_count):
                child = parent.child(i)
                value = self._get_single_item_data(child)
                result.append(value)
            return result
        else:  # Dictionary
            result = OrderedDict()
            for i in range(child_count):
                child = parent.child(i)
                key = child.text(0)
                value = self._get_single_item_data(child)
                result[key] = value
            return result
    
    def _get_single_item_data(self, item):
        """Get data for a single item"""
        item_type = item.text(1)
        
        if item_type in ("Dictionary", "Array"):
            return self._get_item_data(item)
        else:
            return item.data(2, Qt.ItemDataRole.UserRole)




class ConfigEditorPage(QWidget):
    """Config.plist Editor Page with TreeView, OC Snapshot, and Undo/Redo"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("configEditorPage")
        self.controller = parent
        self.current_file = None
        self.plist_data = None
        
        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_stack = MAX_UNDO_LEVELS  # Limit undo history
        
        self.setup_ui()
    
    def _get_window(self):
        """Get the main window"""
        return self.window()
    
    def _show_info_bar(self, title, content, info_type="success", duration=2000):
        """Show an info bar notification"""
        info_func = {
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error,
            "info": InfoBar.info
        }.get(info_type, InfoBar.success)
        
        info_func(
            title=title,
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=self._get_window()
        )
    
    def _create_default_value(self, value_type):
        """Create a default value for the given type"""
        return TYPE_DEFAULTS.get(value_type, "")
    
    def save_state(self):
        """Save current tree state to undo stack"""
        if len(self.undo_stack) >= self.max_undo_stack:
            self.undo_stack.pop(0)  # Remove oldest state
        
        current_state = self.tree.get_tree_data()
        self.undo_stack.append(current_state)
        self.redo_stack.clear()  # Clear redo stack on new action
        
        # Update button states
        self.undo_action.setEnabled(True)
        self.redo_action.setEnabled(False)
    
    def undo(self):
        """Undo last change"""
        if not self.undo_stack:
            return
        
        # Save current state to redo stack
        current_state = self.tree.get_tree_data()
        self.redo_stack.append(current_state)
        
        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.plist_data = previous_state
        self.tree.populate_tree(self.plist_data)
        self.tree.expandAll()  # Expand all items after undo
        
        # Update button states
        self.undo_action.setEnabled(len(self.undo_stack) > 0)
        self.redo_action.setEnabled(True)
        
        InfoBar.success(
            title='Undo',
            content='Changes reverted',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=1000,
            parent=self
        )
    
    def redo(self):
        """Redo last undone change"""
        if not self.redo_stack:
            return
        
        # Save current state to undo stack
        current_state = self.tree.get_tree_data()
        self.undo_stack.append(current_state)
        
        # Restore redo state
        redo_state = self.redo_stack.pop()
        self.plist_data = redo_state
        self.tree.populate_tree(self.plist_data)
        self.tree.expandAll()  # Expand all items after redo
        
        # Update button states
        self.undo_action.setEnabled(True)
        self.redo_action.setEnabled(len(self.redo_stack) > 0)
        
        InfoBar.success(
            title='Redo',
            content='Changes reapplied',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=1000,
            parent=self
        )
        
    def setup_ui(self):
        """Setup the config editor page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])
        
        # Title section
        title_label = SubtitleLabel("Config.plist Editor")
        layout.addWidget(title_label)
        
        subtitle_label = BodyLabel("Load, edit, and manage your OpenCore configuration")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(SPACING['medium'])
        
        # Toolbar with CommandBar for modern Fluent Design look
        toolbar_card = CardWidget()
        toolbar_layout = QVBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(SPACING['large'], SPACING['medium'],
                                         SPACING['large'], SPACING['medium'])
        toolbar_layout.setSpacing(SPACING['small'])
        
        # CommandBar with primary actions
        self.command_bar = CommandBar(self)
        # Show text beside icons for better clarity
        self.command_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # File operations
        self.load_action = Action(FluentIcon.FOLDER, "Load")
        self.load_action.triggered.connect(self.load_config)
        self.command_bar.addAction(self.load_action)
        
        self.save_action = Action(FluentIcon.SAVE, "Save")
        self.save_action.triggered.connect(self.save_config)
        self.save_action.setEnabled(False)
        self.command_bar.addAction(self.save_action)
        
        self.save_as_action = Action(FluentIcon.SAVE_AS, "Save As")
        self.save_as_action.triggered.connect(self.save_config_as)
        self.save_as_action.setEnabled(False)
        self.command_bar.addAction(self.save_as_action)
        
        self.command_bar.addSeparator()
        
        # OC Snapshot operations
        self.snapshot_action = Action(FluentIcon.SYNC, "OC Snapshot")
        self.snapshot_action.triggered.connect(self.oc_snapshot)
        self.snapshot_action.setEnabled(False)
        self.command_bar.addAction(self.snapshot_action)
        
        self.clean_snapshot_action = Action(FluentIcon.DELETE, "Clean Snapshot")
        self.clean_snapshot_action.triggered.connect(self.oc_clean_snapshot)
        self.clean_snapshot_action.setEnabled(False)
        self.command_bar.addAction(self.clean_snapshot_action)
        
        self.command_bar.addSeparator()
        
        # Undo/Redo actions
        self.undo_action = Action(FluentIcon.RETURN, "Undo")
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        self.command_bar.addAction(self.undo_action)
        
        self.redo_action = Action(FluentIcon.SYNC, "Redo")
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        self.command_bar.addAction(self.redo_action)
        
        self.command_bar.addSeparator()
        
        # Validation actions
        self.validate_action = Action(FluentIcon.ACCEPT, "Validate")
        self.validate_action.triggered.connect(self.validate_config)
        self.validate_action.setEnabled(False)
        self.command_bar.addAction(self.validate_action)
        
        self.export_validation_action = Action(FluentIcon.DOCUMENT, "Export Report")
        self.export_validation_action.triggered.connect(self.export_validation)
        self.export_validation_action.setEnabled(False)
        self.command_bar.addAction(self.export_validation_action)
        
        toolbar_layout.addWidget(self.command_bar)
        
        # Current file label
        self.file_label = BodyLabel("No file loaded")
        self.file_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        toolbar_layout.addWidget(self.file_label)
        
        layout.addWidget(toolbar_card)
        
        # Tree view card
        tree_card = CardWidget()
        tree_layout = QVBoxLayout(tree_card)
        tree_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                      SPACING['large'], SPACING['large'])
        
        # Header with search
        header_layout = QHBoxLayout()
        tree_title = StrongBodyLabel("Configuration Tree")
        header_layout.addWidget(tree_title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_box = SearchLineEdit()
        self.search_box.setPlaceholderText("Search keys...")
        self.search_box.setFixedWidth(250)
        self.search_box.textChanged.connect(self.filter_tree)
        header_layout.addWidget(self.search_box)
        
        tree_layout.addLayout(header_layout)
        
        help_label = BodyLabel("Double-click to edit • Right-click to add/remove • Drag to reorder • Undo/Redo available")
        help_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-size: 12px;")
        tree_layout.addWidget(help_label)
        
        tree_layout.addSpacing(SPACING['small'])
        
        # Tree widget
        self.tree = PlistTreeWidget()
        self.tree.editor_page = self  # Set reference for undo functionality
        tree_layout.addWidget(self.tree)
        
        layout.addWidget(tree_card, 1)
    
    def filter_tree(self, text):
        """Filter tree items based on search text"""
        if not text:
            # Show all items
            iterator = QTreeWidgetItemIterator(self.tree)
            while iterator.value():
                item = iterator.value()
                item.setHidden(False)
                iterator += 1
            return
        
        text = text.lower()
        iterator = QTreeWidgetItemIterator(self.tree)
        
        # First pass: hide all items
        while iterator.value():
            item = iterator.value()
            item.setHidden(True)
            iterator += 1
        
        # Second pass: show matching items and their parents
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if text in item.text(0).lower() or text in item.text(2).lower():
                # Show this item and all its parents
                current = item
                while current:
                    current.setHidden(False)
                    current = current.parent()
                
                # Show all children
                self._show_all_children(item)
            iterator += 1
    
    def _show_all_children(self, item):
        """Recursively show all children of an item"""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setHidden(False)
            self._show_all_children(child)
        
    
    def load_config(self):
        """Load a config.plist file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select config.plist",
            "",
            "Plist Files (*.plist);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Use utils.read_file for consistent file handling
            self.plist_data = self.controller.ocpe.u.read_file(file_path)
            
            if self.plist_data is None:
                raise FileNotFoundError(f"Could not read file: {file_path}")
            
            if not isinstance(self.plist_data, dict):
                raise ValueError("Invalid plist format: root element must be a dictionary")
            
            self.current_file = file_path
            self.tree.populate_tree(self.plist_data)
            self.tree.expandAll()  # Expand all tree items on load
            self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
            
            # Clear undo/redo stacks on new file load
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.undo_action.setEnabled(False)
            self.redo_action.setEnabled(False)
            
            # Save initial state
            self.save_state()
            
            # Enable buttons
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.snapshot_action.setEnabled(True)
            self.clean_snapshot_action.setEnabled(True)
            self.validate_action.setEnabled(True)
            
            InfoBar.success(
                title='Success',
                content=f'Loaded {os.path.basename(file_path)}',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            
        except (FileNotFoundError, ValueError) as e:
            MessageBox(
                "Error Loading File",
                str(e),
                self
            ).exec()
        except Exception as e:
            MessageBox(
                "Error Loading File",
                f"Failed to load config.plist:\n{str(e)}",
                self
            ).exec()
    
    def save_config(self):
        """Save the current config.plist"""
        if not self.current_file:
            self.save_config_as()
            return
            
        try:
            # Get data from tree
            data = self.tree.get_tree_data()
            
            # Use utils.write_file for consistent file handling
            self.controller.ocpe.u.write_file(self.current_file, data)
            
            InfoBar.success(
                title='Saved',
                content=f'Saved {os.path.basename(self.current_file)}',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            
        except Exception as e:
            MessageBox(
                "Error Saving File",
                f"Failed to save config.plist:\n{str(e)}",
                self
            ).exec()
    
    def save_config_as(self):
        """Save the config.plist to a new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save config.plist As",
            "config.plist",
            "Plist Files (*.plist);;All Files (*)"
        )
        
        if not file_path:
            return
            
        self.current_file = file_path
        self.save_config()
        self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
    
    def oc_snapshot(self):
        """Perform OC Snapshot"""
        self._perform_snapshot(clean=False)
    
    def oc_clean_snapshot(self):
        """Perform OC Clean Snapshot"""
        self._perform_snapshot(clean=True)
    
    def _perform_snapshot(self, clean=False):
        """Perform OC Snapshot operation"""
        if not self.plist_data:
            MessageBox(
                "No Config Loaded",
                "Please load a config.plist file first.",
                self
            ).exec()
            return
        
        # Get target directory from current file's directory
        target_dir = os.path.dirname(self.current_file) if self.current_file else None
        
        # Prompt for OC folder
        oc_folder = QFileDialog.getExistingDirectory(
            self,
            "Select OC Folder",
            target_dir or ""
        )
        
        if not oc_folder:
            return
        
        # Verify folder structure
        oc_acpi = os.path.join(oc_folder, "ACPI")
        oc_drivers = os.path.join(oc_folder, "Drivers")
        oc_kexts = os.path.join(oc_folder, "Kexts")
        oc_tools = os.path.join(oc_folder, "Tools")
        
        missing = []
        if not os.path.isdir(oc_acpi):
            missing.append("ACPI")
        if not os.path.isdir(oc_drivers):
            missing.append("Drivers")
        if not os.path.isdir(oc_kexts):
            missing.append("Kexts")
        
        if missing:
            # Try OC subfolder
            oc_folder_alt = os.path.join(oc_folder, "OC")
            if os.path.isdir(oc_folder_alt):
                oc_acpi = os.path.join(oc_folder_alt, "ACPI")
                oc_drivers = os.path.join(oc_folder_alt, "Drivers")
                oc_kexts = os.path.join(oc_folder_alt, "Kexts")
                oc_tools = os.path.join(oc_folder_alt, "Tools")
                
                missing = []
                if not os.path.isdir(oc_acpi):
                    missing.append("ACPI")
                if not os.path.isdir(oc_drivers):
                    missing.append("Drivers")
                if not os.path.isdir(oc_kexts):
                    missing.append("Kexts")
                    
                if not missing:
                    oc_folder = oc_folder_alt
        
        if missing:
            MessageBox(
                "Incorrect OC Folder Structure",
                f"The following required folders do not exist:\n\n{', '.join(missing)}\n\nPlease make sure you're selecting a valid OC folder.",
                self
            ).exec()
            return
        
        try:
            # Get current tree data
            tree_data = self.tree.get_tree_data()
            
            # Perform snapshot operations
            self._snapshot_acpi(tree_data, oc_acpi, clean)
            self._snapshot_kexts(tree_data, oc_kexts, clean)
            self._snapshot_drivers(tree_data, oc_drivers, clean)
            self._snapshot_tools(tree_data, oc_tools, clean)
            
            # Update tree
            self.tree.populate_tree(tree_data)
            self.tree.expandAll()  # Expand all items after snapshot
            self.plist_data = tree_data
            
            # Save state for undo
            self.save_state()
            
            InfoBar.success(
                title='Snapshot Complete',
                content='OC Snapshot completed successfully',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            MessageBox(
                "Snapshot Error",
                f"Error during OC Snapshot:\n{str(e)}",
                self
            ).exec()
    
    def _snapshot_acpi(self, tree_data, oc_acpi, clean):
        """Snapshot ACPI folder"""
        config = {
            "section": ["ACPI", "Add"],
            "path_key": "Path",
            "extensions": [".aml", ".bin"],
            "template": lambda path: OrderedDict([
                ("Comment", os.path.basename(path)),
                ("Enabled", True),
                ("Path", path)
            ])
        }
        self._snapshot_folder_generic(tree_data, oc_acpi, clean, config)
    
    def _snapshot_folder_generic(self, tree_data, folder_path, clean, config):
        """Generic folder snapshot logic"""
        # Ensure section exists
        section = config["section"]
        current = tree_data
        for key in section[:-1]:
            if key not in current:
                current[key] = OrderedDict()
            current = current[key]
        
        if section[-1] not in current:
            current[section[-1]] = []
        
        # Scan folder
        new_items = []
        for root, dirs, files in os.walk(folder_path):
            for name in files:
                if not name.startswith("."):
                    ext_match = any(name.lower().endswith(ext) for ext in config["extensions"])
                    if ext_match:
                        full_path = os.path.join(root, name)
                        rel_path = os.path.relpath(full_path, folder_path).replace("\\", "/")
                        new_items.append(rel_path)
        
        # Build new list
        existing = [] if clean else current[section[-1]]
        path_key = config["path_key"]
        existing_paths = [
            x.get(path_key, "").lower() if isinstance(x, dict) else x.lower()
            for x in existing
        ]
        
        # Add new entries
        for item_path in sorted(new_items, key=lambda x: x.lower()):
            if item_path.lower() not in existing_paths:
                new_entry = config["template"](item_path)
                existing.append(new_entry)
        
        # Remove entries that don't exist
        new_items_lower = [x.lower() for x in new_items]
        filtered = []
        for entry in existing:
            path = entry.get(path_key, "").lower() if isinstance(entry, dict) else entry.lower()
            if path in new_items_lower:
                filtered.append(entry)
        
        current[section[-1]] = filtered
    
    def _snapshot_kexts(self, tree_data, oc_kexts, clean):
        """Snapshot Kexts folder"""
        # Ensure Kernel->Add exists
        if "Kernel" not in tree_data:
            tree_data["Kernel"] = OrderedDict()
        if "Add" not in tree_data["Kernel"]:
            tree_data["Kernel"]["Add"] = []
        
        # Scan kexts
        kext_list = []
        for root, dirs, files in os.walk(oc_kexts):
            for name in sorted(dirs, key=lambda x: x.lower()):
                if name.startswith(".") or not name.lower().endswith(".kext"):
                    continue
                
                kext_path = os.path.join(root, name)
                rel_path = os.path.relpath(kext_path, oc_kexts).replace("\\", "/")
                
                # Find Info.plist
                info_plist_path = None
                for kroot, kdirs, kfiles in os.walk(kext_path):
                    if "Info.plist" in kfiles:
                        info_plist_path = os.path.join(kroot, "Info.plist")
                        break
                
                if not info_plist_path:
                    continue
                
                try:
                    with open(info_plist_path, 'rb') as f:
                        info_plist = plistlib.load(f)
                    
                    if "CFBundleIdentifier" not in info_plist:
                        continue
                    
                    plist_rel_path = os.path.relpath(info_plist_path, kext_path).replace("\\", "/")
                    
                    # Find executable
                    exec_path = ""
                    if "CFBundleExecutable" in info_plist:
                        exec_name = info_plist["CFBundleExecutable"]
                        exec_full = os.path.join(kext_path, "Contents", "MacOS", exec_name)
                        if os.path.exists(exec_full) and os.path.getsize(exec_full) > 0:
                            exec_path = f"Contents/MacOS/{exec_name}"
                    
                    kext_entry = OrderedDict([
                        ("Arch", "Any"),
                        ("BundlePath", rel_path),
                        ("Comment", name),
                        ("Enabled", True),
                        ("ExecutablePath", exec_path),
                        ("MaxKernel", ""),
                        ("MinKernel", ""),
                        ("PlistPath", plist_rel_path)
                    ])
                    
                    kext_list.append(kext_entry)
                    
                except Exception as e:
                    print(f"Error processing kext {name}: {e}")
                    continue
        
        # Build new kext list
        add = [] if clean else tree_data["Kernel"]["Add"]
        existing_bundles = [x.get("BundlePath", "").lower() for x in add if isinstance(x, dict)]
        
        for kext in kext_list:
            if kext["BundlePath"].lower() not in existing_bundles:
                add.append(kext)
        
        # Remove entries that don't exist
        new_add = []
        kext_bundles = [k["BundlePath"].lower() for k in kext_list]
        for entry in add:
            if isinstance(entry, dict) and entry.get("BundlePath", "").lower() in kext_bundles:
                # Update paths if needed
                matching_kext = next((k for k in kext_list if k["BundlePath"].lower() == entry.get("BundlePath", "").lower()), None)
                if matching_kext:
                    if "ExecutablePath" in matching_kext:
                        entry["ExecutablePath"] = matching_kext["ExecutablePath"]
                    if "PlistPath" in matching_kext:
                        entry["PlistPath"] = matching_kext["PlistPath"]
                new_add.append(entry)
        
        tree_data["Kernel"]["Add"] = new_add
    
    def _snapshot_drivers(self, tree_data, oc_drivers, clean):
        """Snapshot Drivers folder"""
        config = {
            "section": ["UEFI", "Drivers"],
            "path_key": "Path",
            "extensions": [".efi"],
            "template": lambda path: OrderedDict([
                ("Arguments", ""),
                ("Comment", os.path.basename(path)),
                ("Enabled", True),
                ("LoadEarly", False),
                ("Path", path)
            ])
        }
        self._snapshot_folder_generic(tree_data, oc_drivers, clean, config)
    
    def _snapshot_tools(self, tree_data, oc_tools, clean):
        """Snapshot Tools folder"""
        if not os.path.isdir(oc_tools):
            return  # Tools folder is optional
        
        config = {
            "section": ["Misc", "Tools"],
            "path_key": "Path",
            "extensions": [".efi"],
            "template": lambda path: OrderedDict([
                ("Arguments", ""),
                ("Auxiliary", True),
                ("Comment", os.path.basename(path)),
                ("Enabled", True),
                ("Flavour", "Auto"),
                ("FullNvramAccess", False),
                ("Path", path),
                ("RealPath", False),
                ("TextMode", False)
            ])
        }
        self._snapshot_folder_generic(tree_data, oc_tools, clean, config)
    
    def validate_config(self):
        """Validate the loaded config.plist"""
        if not self.plist_data:
            MessageBox(
                "No Config Loaded",
                "Please load a config.plist file first.",
                self
            ).exec()
            return
        
        # Get current tree data
        tree_data = self.tree.get_tree_data()
        
        # Perform validation checks
        issues = []
        warnings = []
        
        # 1. Check required sections exist
        required_sections = {
            "ACPI": ["Add", "Delete", "Patch", "Quirks"],
            "Booter": ["Quirks"],
            "DeviceProperties": ["Add"],
            "Kernel": ["Add", "Block", "Patch", "Quirks"],
            "Misc": ["Boot", "Debug", "Security", "Tools"],
            "NVRAM": ["Add", "Delete"],
            "PlatformInfo": ["Generic"],
            "UEFI": ["Drivers", "Input", "Output", "ProtocolOverrides", "Quirks"]
        }
        
        for section, subsections in required_sections.items():
            if section not in tree_data:
                issues.append(f"Missing required section: {section}")
            else:
                for subsection in subsections:
                    if subsection not in tree_data[section]:
                        warnings.append(f"Missing recommended subsection: {section} -> {subsection}")
        
        # 2. Check path lengths (OC_STORAGE_SAFE_PATH_MAX = 128)
        path_issues = self._check_path_lengths(tree_data)
        if path_issues:
            issues.extend(path_issues)
        
        # 3. Check for duplicate entries
        duplicate_issues = self._check_duplicates(tree_data)
        if duplicate_issues:
            warnings.extend(duplicate_issues)
        
        # 4. Check kext dependencies
        kext_issues = self._check_kext_order(tree_data)
        if kext_issues:
            warnings.extend(kext_issues)
        
        # Store validation results for export
        self.last_validation_results = {
            "timestamp": datetime.now().isoformat(),
            "file": self.current_file or "Unsaved",
            "errors": issues,
            "warnings": warnings
        }
        
        # Enable export button if there are results
        self.export_validation_action.setEnabled(True)
        
        # Display validation results
        if not issues and not warnings:
            MessageBox(
                "Validation Successful",
                "✓ No issues found in config.plist\n\nYour configuration appears to be properly structured.",
                self
            ).exec()
        else:
            result_text = []
            
            if issues:
                result_text.append("❌ ERRORS:\n")
                for issue in issues:
                    result_text.append(f"  • {issue}")
                result_text.append("")
            
            if warnings:
                result_text.append("⚠️  WARNINGS:\n")
                for warning in warnings:
                    result_text.append(f"  • {warning}")
            
            MessageBox(
                "Validation Results",
                "\n".join(result_text),
                self
            ).exec()
    
    def export_validation(self):
        """Export validation results to a file"""
        if not hasattr(self, 'last_validation_results'):
            MessageBox(
                "No Validation Results",
                "Please run validation first before exporting.",
                self
            ).exec()
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Validation Report",
            f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                # Export as JSON
                with open(file_path, 'w') as f:
                    json.dump(self.last_validation_results, f, indent=2)
            else:
                # Export as text
                with open(file_path, 'w') as f:
                    f.write("OpenCore Config.plist Validation Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Timestamp: {self.last_validation_results['timestamp']}\n")
                    f.write(f"File: {self.last_validation_results['file']}\n\n")
                    
                    if self.last_validation_results['errors']:
                        f.write("ERRORS:\n")
                        f.write("-" * 50 + "\n")
                        for error in self.last_validation_results['errors']:
                            f.write(f"  • {error}\n")
                        f.write("\n")
                    
                    if self.last_validation_results['warnings']:
                        f.write("WARNINGS:\n")
                        f.write("-" * 50 + "\n")
                        for warning in self.last_validation_results['warnings']:
                            f.write(f"  • {warning}\n")
                        f.write("\n")
                    
                    if not self.last_validation_results['errors'] and not self.last_validation_results['warnings']:
                        f.write("✓ No issues found. Configuration is valid.\n")
            
            InfoBar.success(
                title='Exported',
                content=f'Validation report saved to {os.path.basename(file_path)}',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            
        except Exception as e:
            MessageBox(
                "Export Error",
                f"Failed to export validation report:\n{str(e)}",
                self
            ).exec()
    
    def _check_path_lengths(self, tree_data):
        """Check if any paths exceed OC_STORAGE_SAFE_PATH_MAX (128 chars)"""
        issues = []
        
        # Check ACPI paths
        if "ACPI" in tree_data and "Add" in tree_data["ACPI"]:
            for entry in tree_data["ACPI"]["Add"]:
                if isinstance(entry, dict) and "Path" in entry:
                    if len(entry["Path"]) > OC_STORAGE_SAFE_PATH_MAX - 1:
                        issues.append(f"ACPI path too long ({len(entry['Path'])} chars): {entry['Path'][:50]}...")
        
        # Check Kernel/Kext paths
        if "Kernel" in tree_data and "Add" in tree_data["Kernel"]:
            for entry in tree_data["Kernel"]["Add"]:
                if isinstance(entry, dict):
                    bundle_path = entry.get("BundlePath", "")
                    if len(bundle_path) > OC_STORAGE_SAFE_PATH_MAX - 1:
                        issues.append(f"Kext BundlePath too long ({len(bundle_path)} chars): {bundle_path[:50]}...")
                    
                    # Check combined paths for ExecutablePath and PlistPath
                    if "ExecutablePath" in entry:
                        combined = bundle_path + "/" + entry["ExecutablePath"]
                        if len(combined) > OC_STORAGE_SAFE_PATH_MAX:
                            issues.append(f"Kext ExecutablePath too long when combined ({len(combined)} chars): {entry.get('Comment', 'Unknown')}")
                    
                    if "PlistPath" in entry:
                        combined = bundle_path + "/" + entry["PlistPath"]
                        if len(combined) > OC_STORAGE_SAFE_PATH_MAX:
                            issues.append(f"Kext PlistPath too long when combined ({len(combined)} chars): {entry.get('Comment', 'Unknown')}")
        
        # Check Driver paths
        if "UEFI" in tree_data and "Drivers" in tree_data["UEFI"]:
            for entry in tree_data["UEFI"]["Drivers"]:
                path = entry.get("Path", "") if isinstance(entry, dict) else entry
                if len(path) > OC_STORAGE_SAFE_PATH_MAX - 1:
                    issues.append(f"Driver path too long ({len(path)} chars): {path[:50]}...")
        
        # Check Tool paths
        if "Misc" in tree_data and "Tools" in tree_data["Misc"]:
            for entry in tree_data["Misc"]["Tools"]:
                if isinstance(entry, dict) and "Path" in entry:
                    if len(entry["Path"]) > OC_STORAGE_SAFE_PATH_MAX - 1:
                        issues.append(f"Tool path too long ({len(entry['Path'])} chars): {entry['Path'][:50]}...")
        
        return issues
    
    def _check_duplicates(self, tree_data):
        """Check for duplicate entries"""
        warnings = []
        
        # Check duplicate ACPI paths
        if "ACPI" in tree_data and "Add" in tree_data["ACPI"]:
            paths = [entry.get("Path", "").lower() for entry in tree_data["ACPI"]["Add"] if isinstance(entry, dict)]
            duplicates = [p for p in set(paths) if paths.count(p) > 1]
            if duplicates:
                warnings.append(f"Duplicate ACPI paths found: {', '.join(duplicates)}")
        
        # Check duplicate Kext bundle paths
        if "Kernel" in tree_data and "Add" in tree_data["Kernel"]:
            bundles = [entry.get("BundlePath", "").lower() for entry in tree_data["Kernel"]["Add"] if isinstance(entry, dict)]
            duplicates = [b for b in set(bundles) if bundles.count(b) > 1]
            if duplicates:
                warnings.append(f"Duplicate Kext bundle paths found: {', '.join(duplicates)}")
        
        return warnings
    
    def _check_kext_order(self, tree_data):
        """Check if kext dependencies are in correct order using comprehensive kext database"""
        warnings = []
        
        if "Kernel" not in tree_data or "Add" not in tree_data["Kernel"]:
            return warnings
        
        # Build kext dependencies map from kext_data
        kext_dependencies = {}
        for kext_info in kext_data.kexts:
            kext_name = f"{kext_info.name}.kext"
            # Convert required kext names to .kext format
            deps = [f"{dep}.kext" for dep in kext_info.requires_kexts]
            kext_dependencies[kext_name] = deps
        
        kexts = tree_data["Kernel"]["Add"]
        kext_names = [os.path.basename(k.get("BundlePath", "")) for k in kexts if isinstance(k, dict)]
        
        for i, kext in enumerate(kexts):
            if not isinstance(kext, dict):
                continue
            
            kext_name = os.path.basename(kext.get("BundlePath", ""))
            
            if kext_name in kext_dependencies:
                required_deps = kext_dependencies[kext_name]
                for dep in required_deps:
                    # Check if dependency exists and is before this kext
                    if dep in kext_names:
                        dep_index = kext_names.index(dep)
                        if dep_index > i:
                            warnings.append(f"Kext dependency order: {kext_name} should be loaded after {dep}")
        
        return warnings
