from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QBrush, QColor

from qfluentwidgets import CardWidget, TreeWidget, BodyLabel, StrongBodyLabel

from Scripts.datasets.config_tooltips import get_tooltip
from Scripts.value_formatters import format_value, get_value_type
from Scripts.styles import SPACING, COLORS, RADIUS


class ConfigEditor(QWidget):    
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("configEditor")
        
        self.original_config = None
        self.modified_config = None
        self.context = {}
        
        self.mainLayout = QVBoxLayout(self)
        
        self._init_ui()
    
    def _init_ui(self):
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        
        card = CardWidget()
        card.setBorderRadius(RADIUS["card"])
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(SPACING["large"], SPACING["large"], SPACING["large"], SPACING["large"])
        card_layout.setSpacing(SPACING["medium"])

        title = StrongBodyLabel("Config Editor")
        card_layout.addWidget(title)
        
        description = BodyLabel("View differences between original and modified config.plist")
        description.setStyleSheet("color: {}; font-size: 13px;".format(COLORS["text_secondary"]))
        card_layout.addWidget(description)
        
        self.tree = TreeWidget()
        self.tree.setHeaderLabels(["Key", "", "Original", "Modified"])
        self.tree.setColumnCount(4)
        self.tree.setRootIsDecorated(True)
        self.tree.setItemsExpandable(True)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.itemExpanded.connect(self._update_tree_height)
        self.tree.itemCollapsed.connect(self._update_tree_height)
        
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        card_layout.addWidget(self.tree)
        self.mainLayout.addWidget(card)
    
    def load_configs(self, original, modified, context=None):
        self.original_config = original
        self.modified_config = modified
        self.context = context or {}

        self.tree.clear()
        
        self._render_config(self.original_config, self.modified_config, [])
        
        QTimer.singleShot(0, self._update_tree_height)
    
    def _get_all_keys_from_both_configs(self, original, modified):
        original_keys = set(original.keys()) if isinstance(original, dict) else set()
        modified_keys = set(modified.keys()) if isinstance(modified, dict) else set()
        return sorted(original_keys | modified_keys)
    
    def _determine_change_type(self, original_value, modified_value, key_in_original, key_in_modified):
        if not key_in_original:
            return "added"
        elif not key_in_modified:
            return "removed"
        elif original_value != modified_value:
            return "modified"
        return None
    
    def _get_effective_value(self, original_value, modified_value):
        return modified_value if modified_value is not None else original_value
    
    def _get_safe_value(self, value, default = None):
        return value if value is not None else default
    
    def _set_value_columns(self, item, original_value, modified_value, change_type, is_dict=False, is_array=False):
        if original_value is not None:
            if is_dict:
                item.setText(2, "<object: {} keys>".format(len(original_value)))
            elif is_array:
                item.setText(2, "<array: {} items>".format(len(original_value)))
            else:
                item.setText(2, format_value(original_value))
                item.setData(2, Qt.ItemDataRole.UserRole, get_value_type(original_value))
        else:
            item.setText(2, "")
        
        if change_type is not None and modified_value is not None:
            if is_dict:
                item.setText(3, "<object: {} keys>".format(len(modified_value)))
            elif is_array:
                item.setText(3, "<array: {} items>".format(len(modified_value)))
            else:
                item.setText(3, format_value(modified_value))
                item.setData(3, Qt.ItemDataRole.UserRole, get_value_type(modified_value))
        else:
            item.setText(3, "")
    
    def _build_path_string(self, path_parts):
        if not path_parts:
            return ""
        return ".".join(path_parts)
    
    def _build_array_path(self, path_parts, index):
        return path_parts + [f"[{index}]"]
    
    def _render_config(self, original, modified, path_parts, parent_item=None):
        if parent_item is None:
            parent_item = self.tree.invisibleRootItem()

        all_keys = self._get_all_keys_from_both_configs(original, modified)

        for key in all_keys:
            current_path_parts = path_parts + [key]
            current_path = self._build_path_string(current_path_parts)

            original_value = original.get(key) if isinstance(original, dict) else None
            modified_value = modified.get(key) if isinstance(modified, dict) else None

            key_in_original = key in original if isinstance(original, dict) else False
            key_in_modified = key in modified if isinstance(modified, dict) else False
            
            change_type = self._determine_change_type(
                original_value, modified_value, key_in_original, key_in_modified
            )
            effective_value = self._get_effective_value(original_value, modified_value)

            if isinstance(effective_value, list):
                self._render_array(
                    original_value if isinstance(original_value, list) else [],
                    modified_value if isinstance(modified_value, list) else [],
                    current_path_parts,
                    parent_item
                )
                continue

            item = QTreeWidgetItem(parent_item)
            item.setText(0, key)
            item.setData(0, Qt.ItemDataRole.UserRole, current_path)
            self._apply_highlighting(item, change_type)
            self._setup_tooltip(item, current_path, modified_value, original_value)

            if isinstance(effective_value, dict):
                item.setData(3, Qt.ItemDataRole.UserRole, "dict")
                self._set_value_columns(item, original_value, modified_value, change_type, is_dict=True)

                self._render_config(
                    self._get_safe_value(original_value, {}),
                    self._get_safe_value(modified_value, {}),
                    current_path_parts,
                    item
                )
            else:
                self._set_value_columns(item, original_value, modified_value, change_type)
        
    def _render_array(self, original_array, modified_array, path_parts, parent_item):
        change_type = self._determine_change_type(
            original_array, modified_array,
            original_array is not None, modified_array is not None
        )
        
        effective_original = self._get_safe_value(original_array, [])
        effective_modified = self._get_safe_value(modified_array, [])
        
        path_string = self._build_path_string(path_parts)
        array_key = path_parts[-1] if path_parts else "array"
        
        item = QTreeWidgetItem(parent_item)
        item.setText(0, array_key)
        item.setData(0, Qt.ItemDataRole.UserRole, path_string)
        item.setData(3, Qt.ItemDataRole.UserRole, "array")
        
        self._apply_highlighting(item, change_type)
        self._setup_tooltip(item, path_string, modified_array, original_array)
        self._set_value_columns(item, original_array, modified_array, change_type, is_array=True)
        
        original_len = len(effective_original)
        modified_len = len(effective_modified)
        max_len = max(original_len, modified_len)
        
        for i in range(max_len):
            original_element = effective_original[i] if i < original_len else None
            modified_element = effective_modified[i] if i < modified_len else None
            
            element_change_type = self._determine_change_type(
                original_element, modified_element,
                original_element is not None, modified_element is not None
            )
            
            effective_element = self._get_effective_value(original_element, modified_element)
            
            if effective_element is None:
                continue
            
            element_path_parts = self._build_array_path(path_parts, i)
            element_path = self._build_path_string(element_path_parts)
            
            element_item = QTreeWidgetItem(item)
            element_item.setText(0, "[{}]".format(i))
            element_item.setData(0, Qt.ItemDataRole.UserRole, element_path)
            
            self._apply_highlighting(element_item, element_change_type)
            self._setup_tooltip(element_item, element_path, modified_element, original_element)
            
            if isinstance(effective_element, dict):
                element_item.setData(3, Qt.ItemDataRole.UserRole, "dict")
                self._set_value_columns(element_item, original_element, modified_element, element_change_type, is_dict=True)
                
                self._render_config(
                    self._get_safe_value(original_element, {}),
                    self._get_safe_value(modified_element, {}),
                    element_path_parts,
                    element_item
                )
            elif isinstance(effective_element, list):
                element_item.setData(3, Qt.ItemDataRole.UserRole, "array")
                self._set_value_columns(element_item, original_element, modified_element, element_change_type, is_array=True)
                
                self._render_array(
                    self._get_safe_value(original_element, []),
                    self._get_safe_value(modified_element, []),
                    element_path_parts,
                    element_item
                )
            else:
                self._set_value_columns(element_item, original_element, modified_element, element_change_type)    
    
    def _apply_highlighting(self, item, change_type=None):
        if change_type == "added":
            color = "#E3F2FD"
            status_text = "A"
        elif change_type == "removed":
            color = "#FFEBEE"
            status_text = "R"
        elif change_type == "modified":
            color = "#FFF9C4"
            status_text = "M"
        else:
            color = None
            status_text = ""
            
        item.setText(1, status_text)
        
        if color:
            brush = QBrush(QColor(color))
        else:
            brush = QBrush()

        for col in range(4):
            item.setBackground(col, brush)
    
    def _setup_tooltip(self, item, key_path, value, original_value=None):
        tooltip_text = get_tooltip(key_path, value, original_value, self.context)
        item.setToolTip(0, tooltip_text)

    def _calculate_tree_height(self):
        if self.tree.topLevelItemCount() == 0:
            return self.tree.header().height() if self.tree.header().isVisible() else 0

        header_height = self.tree.header().height() if self.tree.header().isVisible() else 0

        first_item = self.tree.topLevelItem(0)
        row_height = 24
        if first_item:
            rect = self.tree.visualItemRect(first_item)
            if rect.height() > 0:
                row_height = rect.height()
            else:
                font_metrics = self.tree.fontMetrics()
                row_height = font_metrics.height() + 6

        def count_visible_rows(item):
            count = 1
            if item.isExpanded():
                for i in range(item.childCount()):
                    count += count_visible_rows(item.child(i))
            return count

        total_rows = 0
        for i in range(self.tree.topLevelItemCount()):
            total_rows += count_visible_rows(self.tree.topLevelItem(i))

        padding = 10
        return header_height + (total_rows * row_height) + padding

    def _update_tree_height(self):
        height = self._calculate_tree_height()
        if height > 0:
            self.tree.setFixedHeight(height)