"""
Welcome/Home page showing introduction and important notices from README
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CardWidget, StrongBodyLabel,
    FluentIcon, IconWidget, InfoBarIcon
)

from ..styles import COLORS, SPACING


class HomePage(QWidget):
    """Welcome/Home page with introduction and important information"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("homePage")
        self.controller = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the home page UI"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])

        # Welcome header
        welcome_label = SubtitleLabel("Welcome to OpCore Simplify")
        layout.addWidget(welcome_label)

        # Introduction card
        intro_card = CardWidget()
        intro_layout = QVBoxLayout(intro_card)
        intro_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                       SPACING['large'], SPACING['large'])
        intro_layout.setSpacing(SPACING['medium'])

        intro_title = StrongBodyLabel("Introduction")
        intro_layout.addWidget(intro_title)

        intro_text = BodyLabel(
            "A specialized tool that streamlines OpenCore EFI creation by automating the essential "
            "setup process and providing standardized configurations. Designed to reduce manual effort "
            "while ensuring accuracy in your Hackintosh journey."
        )
        intro_text.setWordWrap(True)
        intro_text.setStyleSheet("color: #605E5C; line-height: 1.6;")
        intro_layout.addWidget(intro_text)

        layout.addWidget(intro_card)

        # Note card
        note_card = CardWidget()
        note_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['note_bg']};
                border-left: 4px solid {COLORS['note_border']};
            }}
        """)
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                      SPACING['large'], SPACING['large'])
        note_layout.setSpacing(SPACING['medium'])

        # Note header with icon
        note_header_layout = QVBoxLayout()
        note_header_layout.setSpacing(SPACING['small'])
        
        note_icon_label = StrongBodyLabel("ℹ  NOTE")
        note_icon_label.setStyleSheet(f"color: {COLORS['note_text']}; font-size: 14px;")
        note_header_layout.addWidget(note_icon_label)
        
        note_layout.addLayout(note_header_layout)

        note_title = StrongBodyLabel("OpenCore Legacy Patcher 3.0.0 – Now Supports macOS Tahoe 26!")
        note_title.setStyleSheet(f"color: {COLORS['note_text']};")
        note_layout.addWidget(note_title)

        note_text = BodyLabel(
            "The long awaited version 3.0.0 of OpenCore Legacy Patcher is here, bringing initial "
            "support for macOS Tahoe 26 to the community!\n\n"
            "⚠ Please Note:\n"
            "• Only OpenCore-Patcher 3.0.0 from the lzhoang2801/OpenCore-Legacy-Patcher repository "
            "provides support for macOS Tahoe 26 with early patches.\n"
            "• Official Dortania releases or older patches will NOT work with macOS Tahoe 26."
        )
        note_text.setWordWrap(True)
        note_text.setStyleSheet("color: #424242; line-height: 1.6;")
        note_layout.addWidget(note_text)

        layout.addWidget(note_card)

        # Warning card
        warning_card = CardWidget()
        warning_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['warning_bg']};
                border-left: 4px solid {COLORS['warning_border']};
            }}
        """)
        warning_layout = QVBoxLayout(warning_card)
        warning_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                         SPACING['large'], SPACING['large'])
        warning_layout.setSpacing(SPACING['medium'])

        # Warning header with icon
        warning_header_layout = QVBoxLayout()
        warning_header_layout.setSpacing(SPACING['small'])
        
        warning_icon_label = StrongBodyLabel("⚠  WARNING")
        warning_icon_label.setStyleSheet(f"color: {COLORS['warning_text']}; font-size: 14px;")
        warning_header_layout.addWidget(warning_icon_label)
        
        warning_layout.addLayout(warning_header_layout)

        warning_text = BodyLabel(
            "While OpCore Simplify significantly reduces setup time, the Hackintosh journey still requires:\n\n"
            "• Understanding basic concepts from the Dortania Guide\n"
            "• Testing and troubleshooting during the installation process\n"
            "• Patience and persistence in resolving any issues that arise\n\n"
            "Our tool does not guarantee a successful installation in the first attempt, but it should help you get started."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("color: #424242; line-height: 1.6;")
        warning_layout.addWidget(warning_text)

        layout.addWidget(warning_card)

        # Getting Started section
        getting_started_card = CardWidget()
        getting_started_layout = QVBoxLayout(getting_started_card)
        getting_started_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                                 SPACING['large'], SPACING['large'])
        getting_started_layout.setSpacing(SPACING['medium'])

        getting_started_title = StrongBodyLabel("Getting Started")
        getting_started_layout.addWidget(getting_started_title)

        getting_started_text = BodyLabel(
            "Follow these steps to build your OpenCore EFI:\n\n"
            "1. Upload Hardware Report - Load your system hardware information\n"
            "2. Check Compatibility - Verify your hardware is supported\n"
            "3. Configure Settings - Customize ACPI patches, kexts, and SMBIOS\n"
            "4. Build EFI - Generate your OpenCore EFI folder"
        )
        getting_started_text.setWordWrap(True)
        getting_started_text.setStyleSheet("color: #605E5C; line-height: 1.8;")
        getting_started_layout.addWidget(getting_started_text)

        layout.addWidget(getting_started_card)

        layout.addStretch()

        # Set content widget to scroll area
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def refresh(self):
        """Refresh page content"""
        pass
