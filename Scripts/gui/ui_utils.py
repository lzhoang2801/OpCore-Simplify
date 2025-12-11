from typing import Optional, Tuple, TYPE_CHECKING

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qfluentwidgets import FluentIcon, BodyLabel

from .styles import SPACING, COLORS

if TYPE_CHECKING:
    from qfluentwidgets import GroupHeaderCardWidget, CardGroupWidget


def build_icon_label(icon: FluentIcon, color: str, size: int = 32) -> QLabel:
    label = QLabel()
    label.setPixmap(icon.icon(color=color).pixmap(size, size))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setFixedSize(size + 12, size + 12)
    return label


def create_info_widget(text: str, color: Optional[str] = None) -> QWidget:
    if not text:
        return QWidget()
    
    label = BodyLabel(text)
    label.setWordWrap(True)
    if color:
        label.setStyleSheet(f"color: {color};")
    return label


def colored_icon(icon: FluentIcon, color_hex: str) -> FluentIcon:
    if not icon or not color_hex:
        return icon
    
    tint = QColor(color_hex)
    return icon.colored(tint, tint)


def get_compatibility_icon(compat_tuple: Optional[Tuple[Optional[str], Optional[str]]]) -> FluentIcon:
    if not compat_tuple or compat_tuple == (None, None):
        return colored_icon(FluentIcon.CLOSE, COLORS['error'])
    return colored_icon(FluentIcon.ACCEPT, COLORS['success'])


def add_group_with_indent(
    card: 'GroupHeaderCardWidget',
    icon: FluentIcon, 
    title: str, 
    content: str, 
    widget: Optional[QWidget] = None, 
    indent_level: int = 0
) -> 'CardGroupWidget':
    if widget is None:
        widget = QWidget()
    
    group = card.addGroup(icon, title, content, widget)
    
    if indent_level > 0:
        base_margin = 24
        indent = 20 * indent_level
        group.hBoxLayout.setContentsMargins(base_margin + indent, 10, 24, 10)
    
    return group


def create_step_indicator(step_number: int, total_steps: int = 4, color: str = "#0078D4") -> BodyLabel:
    label = BodyLabel(f"STEP {step_number} OF {total_steps}")
    label.setStyleSheet(f"color: {color}; font-weight: bold;")
    return label


def create_vertical_spacer(spacing: int = SPACING['medium']) -> QWidget:
    spacer = QWidget()
    spacer.setFixedHeight(spacing)
    return spacer