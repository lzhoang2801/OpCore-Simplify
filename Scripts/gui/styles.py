"""
Centralized styling and theming for OpCore Simplify GUI with qfluentwidgets
"""

from PyQt6.QtGui import QColor

# Color palette - Fluent Design System inspired
COLORS = {
    # Primary colors
    'primary': '#0078D4',
    'primary_dark': '#005A9E',
    'primary_light': '#4CC2FF',
    'primary_hover': '#106EBE',

    # Background colors
    'bg_main': '#FFFFFF',
    'bg_secondary': '#F3F3F3',
    'bg_sidebar': '#F7F7F7',
    'bg_hover': '#E8E8E8',
    'bg_selected': '#0078D4',
    'bg_card': '#FAFAFA',

    # Text colors
    'text_primary': '#000000',
    'text_secondary': '#605E5C',
    'text_tertiary': '#8A8886',
    'text_sidebar': '#201F1E',
    'text_sidebar_selected': '#FFFFFF',

    # Status colors
    'success': '#107C10',
    'warning': '#FF8C00',
    'error': '#E81123',
    'info': '#0078D4',
    
    # Note and Warning section colors
    'note_bg': '#E3F2FD',
    'note_border': '#2196F3',
    'note_text': '#1565C0',
    'warning_bg': '#FFF3E0',
    'warning_border': '#FF9800',
    'warning_text': '#F57C00',

    # Border colors
    'border': '#D1D1D1',
    'border_light': '#EDEBE9',
    'border_focus': '#0078D4',
}

# Spacing and sizing
SPACING = {
    'tiny': 4,
    'small': 8,
    'medium': 12,
    'large': 16,
    'xlarge': 20,
    'xxlarge': 24,
    'xxxlarge': 32,
}

SIZES = {
    'sidebar_width': 220,
    'sidebar_item_height': 40,
    'button_height': 32,
    'button_padding_x': 16,
    'button_padding_y': 6,
    'input_height': 32,
    'icon_size': 16,
}

# Border radius
RADIUS = {
    'small': 4,
    'medium': 6,
    'large': 8,
    'xlarge': 10,
    'button': 4,
    'card': 8,
}
