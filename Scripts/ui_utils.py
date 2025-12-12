from typing import Optional, Tuple, TYPE_CHECKING

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qfluentwidgets import FluentIcon, BodyLabel, CardWidget, StrongBodyLabel

from .styles import SPACING, COLORS, RADIUS

if TYPE_CHECKING:
    from qfluentwidgets import GroupHeaderCardWidget, CardGroupWidget

class UIUtils:
    def __init__(self):
        pass

    def build_icon_label(self, icon: FluentIcon, color: str, size: int = 32) -> QLabel:
        label = QLabel()
        label.setPixmap(icon.icon(color=color).pixmap(size, size))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedSize(size + 12, size + 12)
        return label

    def create_info_widget(self, text: str, color: Optional[str] = None) -> QWidget:
        if not text:
            return QWidget()
        
        label = BodyLabel(text)
        label.setWordWrap(True)
        if color:
            label.setStyleSheet(f"color: {color};")
        return label

    def colored_icon(self, icon: FluentIcon, color_hex: str) -> FluentIcon:
        if not icon or not color_hex:
            return icon
        
        tint = QColor(color_hex)
        return icon.colored(tint, tint)

    def get_compatibility_icon(self, compat_tuple: Optional[Tuple[Optional[str], Optional[str]]]) -> FluentIcon:
        if not compat_tuple or compat_tuple == (None, None):
            return self.colored_icon(FluentIcon.CLOSE, COLORS['error'])
        return self.colored_icon(FluentIcon.ACCEPT, COLORS['success'])

    def add_group_with_indent(self, card: 'GroupHeaderCardWidget', icon: FluentIcon, title: str, content: str, widget: Optional[QWidget] = None, indent_level: int = 0) -> 'CardGroupWidget':
        if widget is None:
            widget = QWidget()
        
        group = card.addGroup(icon, title, content, widget)
        
        if indent_level > 0:
            base_margin = 24
            indent = 20 * indent_level
            group.hBoxLayout.setContentsMargins(base_margin + indent, 10, 24, 10)
        
        return group

    def create_step_indicator(self, step_number: int, total_steps: int = 4, color: str = "#0078D4") -> BodyLabel:
        label = BodyLabel("STEP {} OF {}".format(step_number, total_steps))
        label.setStyleSheet("color: {}; font-weight: bold;".format(color))
        return label

    def create_vertical_spacer(self, spacing: int = SPACING['medium']) -> QWidget:
        spacer = QWidget()
        spacer.setFixedHeight(spacing)
        return spacer

    def custom_card(self, card_type: str = 'note', icon: Optional[FluentIcon] = None, title: str = '', body: str = '', custom_widget: Optional[QWidget] = None, parent: Optional[QWidget] = None) -> CardWidget:
        card_styles = {
            'note': {
                'bg': COLORS['note_bg'],
                'text': COLORS['note_text'],
                'border': 'rgba(21, 101, 192, 0.2)',
                'default_icon': FluentIcon.INFO
            },
            'warning': {
                'bg': COLORS['warning_bg'],
                'text': COLORS['warning_text'],
                'border': 'rgba(245, 124, 0, 0.25)',
                'default_icon': FluentIcon.MEGAPHONE
            },
            'success': {
                'bg': COLORS['success_bg'],
                'text': COLORS['success'],
                'border': 'rgba(16, 124, 16, 0.2)',
                'default_icon': FluentIcon.COMPLETED
            },
            'error': {
                'bg': '#FFEBEE',
                'text': COLORS['error'],
                'border': 'rgba(232, 17, 35, 0.25)',
                'default_icon': FluentIcon.CLOSE
            },
            'info': {
                'bg': COLORS['note_bg'],
                'text': COLORS['info'],
                'border': 'rgba(0, 120, 212, 0.2)',
                'default_icon': FluentIcon.INFO
            }
        }
        
        style = card_styles.get(card_type, card_styles['note'])
        
        if icon is None:
            icon = style['default_icon']
        
        card = CardWidget(parent)
        card.setStyleSheet(f"""
            CardWidget {{
                background-color: {style['bg']};
                border: 1px solid {style['border']};
                border-radius: {RADIUS['card']}px;
            }}
        """)
        
        main_layout = QHBoxLayout(card)
        main_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        main_layout.setSpacing(SPACING['large'])
        
        icon_label = self.build_icon_label(icon, style['text'], size=40)
        main_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(SPACING['small'])
        
        if title:
            title_label = StrongBodyLabel(title)
            title_label.setStyleSheet(f"color: {style['text']}; font-size: 16px;")
            text_layout.addWidget(title_label)
        
        if body:
            body_label = BodyLabel(body)
            body_label.setWordWrap(True)
            body_label.setOpenExternalLinks(True)
            body_label.setStyleSheet("color: #424242; line-height: 1.6;")
            text_layout.addWidget(body_label)
        
        if custom_widget:
            text_layout.addWidget(custom_widget)
        
        main_layout.addLayout(text_layout)
        
        return card