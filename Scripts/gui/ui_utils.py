"""
Common UI utility functions and helper methods for OpCore Simplify GUI.
This module provides reusable UI components and patterns used across pages.
"""

from typing import Optional, Tuple, TYPE_CHECKING
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qfluentwidgets import FluentIcon, BodyLabel

from .styles import SPACING, COLORS

# Import types only for type checking to avoid circular imports
if TYPE_CHECKING:
    from qfluentwidgets import GroupHeaderCardWidget, CardGroupWidget


def build_icon_label(icon: FluentIcon, color: str, size: int = 32) -> QLabel:
    """
    Create a QLabel with a tinted Fluent icon pixmap.
    
    Args:
        icon: FluentIcon to display
        color: Hex color string for tinting the icon
        size: Size of the icon in pixels (default: 32)
        
    Returns:
        QLabel: Configured label with the icon
    """
    label = QLabel()
    label.setPixmap(icon.icon(color=color).pixmap(size, size))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setFixedSize(size + 12, size + 12)
    return label


def create_info_widget(text: str, color: Optional[str] = None) -> QWidget:
    """
    Create a simple label widget for displaying information.
    
    Args:
        text: Text to display
        color: Optional hex color for the text
        
    Returns:
        QWidget: Widget containing the label, or empty widget if no text
    """
    if not text:
        return QWidget()
    
    label = BodyLabel(text)
    label.setWordWrap(True)
    if color:
        label.setStyleSheet(f"color: {color};")
    return label


def colored_icon(icon: FluentIcon, color_hex: str) -> FluentIcon:
    """
    Return a Fluent icon tinted for both light and dark themes.
    
    Args:
        icon: FluentIcon to tint
        color_hex: Hex color string for tinting
        
    Returns:
        FluentIcon: Tinted icon
    """
    if not icon or not color_hex:
        return icon
    
    tint = QColor(color_hex)
    return icon.colored(tint, tint)


def get_compatibility_icon(compat_tuple: Optional[Tuple[Optional[str], Optional[str]]]) -> FluentIcon:
    """
    Get the appropriate FluentIcon based on compatibility status.
    
    Args:
        compat_tuple: Compatibility tuple (max_version, min_version) or (None, None)
        
    Returns:
        FluentIcon: ACCEPT (green) for supported, CLOSE (red) for unsupported
    """
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
    """
    Add a group to a GroupHeaderCardWidget with optional indentation.
    This is a common pattern used across multiple pages.
    
    Args:
        card: The GroupHeaderCardWidget instance
        icon: Icon for the group
        title: Title text
        content: Content/description text
        widget: Widget to add (default: new empty QWidget)
        indent_level: 0 for main items, 1+ for child items (each level adds 20px left margin)
        
    Returns:
        CardGroupWidget: The created group widget
    """
    if widget is None:
        widget = QWidget()
    
    group = card.addGroup(icon, title, content, widget)
    
    # Apply indentation if needed
    if indent_level > 0:
        base_margin = 24
        indent = 20 * indent_level
        group.hBoxLayout.setContentsMargins(base_margin + indent, 10, 24, 10)
    
    return group


def create_step_indicator(step_number: int, total_steps: int = 4, color: str = "#0078D4") -> BodyLabel:
    """
    Create a consistent step indicator label.
    
    Args:
        step_number: Current step number (1-based)
        total_steps: Total number of steps (default: 4)
        color: Color for the label (default: primary blue)
        
    Returns:
        BodyLabel: Configured step indicator label
    """
    label = BodyLabel(f"STEP {step_number} OF {total_steps}")
    label.setStyleSheet(f"color: {color}; font-weight: bold;")
    return label


def create_vertical_spacer(spacing: int = SPACING['medium']) -> QWidget:
    """
    Create a vertical spacer widget.
    
    Args:
        spacing: Height of the spacer in pixels
        
    Returns:
        QWidget: Empty widget with fixed height
    """
    spacer = QWidget()
    spacer.setFixedHeight(spacing)
    return spacer
