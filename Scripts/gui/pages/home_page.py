"""Welcome/Home page showing introduction and important notices."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CardWidget, StrongBodyLabel,
    FluentIcon, ScrollArea
)

from ..styles import COLORS, SPACING, RADIUS
from ..ui_utils import build_icon_label


class HomePage(ScrollArea):
    """Welcome/Home page with introduction and important information"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("homePage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.setup_ui()

    def setup_ui(self):
        """Setup the home page UI"""
        # Configure scroll area
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

        # Set layout spacing and margins
        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                             SPACING['xxlarge'], SPACING['xlarge'])
        self.expandLayout.setSpacing(SPACING['large'])

        layout = self.expandLayout

        # Welcome header
        welcome_label = SubtitleLabel("Welcome to OpCore Simplify")
        welcome_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(welcome_label)

        # Hero section
        hero_card = CardWidget()
        # hero_card.setStyleSheet(f"""
        #     CardWidget {{
        #         border: none;
        #         border-radius: {RADIUS['card']}px;
        #         background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        #             stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
        #         color: #FFFFFF;
        #     }}
        # """)
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(SPACING['xxlarge'], SPACING['large'],
                                       SPACING['xxlarge'], SPACING['large'])
        hero_layout.setSpacing(SPACING['xxlarge'])

        hero_text = QVBoxLayout()
        hero_text.setSpacing(SPACING['medium'])

        hero_title = StrongBodyLabel("Introduction")
        hero_title.setStyleSheet("font-size: 18px;")
        hero_text.addWidget(hero_title)

        hero_body = BodyLabel(
            "A specialized tool that streamlines OpenCore EFI creation by automating the essential "
            "setup process and providing standardized configurations. Designed to reduce manual effort "
            "while ensuring accuracy in your Hackintosh journey."
        )
        hero_body.setWordWrap(True)
        hero_body.setStyleSheet(
            "line-height: 1.6;")
        hero_text.addWidget(hero_body)

        hero_layout.addLayout(hero_text, 2)

        rocket_label = build_icon_label(
            FluentIcon.ROBOT, COLORS['primary'], size=64)
        hero_layout.addWidget(
            rocket_label, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(hero_card)

        # Note card with Fluent icon
        note_card = CardWidget()
        note_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['note_bg']};
                border: 1px solid rgba(21, 101, 192, 0.2);
                border-radius: {RADIUS['card']}px;
            }}
        """)
        note_layout = QHBoxLayout(note_card)
        note_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                       SPACING['large'], SPACING['large'])
        note_layout.setSpacing(SPACING['large'])

        note_icon = build_icon_label(
            FluentIcon.INFO, COLORS['note_text'], size=40)
        note_layout.addWidget(note_icon)

        note_text_layout = QVBoxLayout()
        note_text_layout.setSpacing(SPACING['small'])

        note_title = StrongBodyLabel(
            "OpenCore Legacy Patcher 3.0.0 - Now Supports macOS Tahoe 26!")
        note_title.setStyleSheet(f"color: {COLORS['note_text']};")
        note_text_layout.addWidget(note_title)

        note_body = BodyLabel(
            "The long awaited version 3.0.0 of OpenCore Legacy Patcher is here, bringing initial "
            "support for macOS Tahoe 26 to the community!\n\n"
            "Please Note:\n"
            "• Only OpenCore-Patcher 3.0.0 from the lzhoang2801/OpenCore-Legacy-Patcher repository "
            "provides support for macOS Tahoe 26 with early patches.\n"
            "• Official Dortania releases or older patches will NOT work with macOS Tahoe 26."
        )
        note_body.setWordWrap(True)
        note_body.setStyleSheet("color: #424242; line-height: 1.6;")
        note_text_layout.addWidget(note_body)

        note_layout.addLayout(note_text_layout)
        layout.addWidget(note_card)

        # Warning card with layered design
        warning_card = CardWidget()
        warning_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['warning_bg']};
                border: 1px solid rgba(245, 124, 0, 0.25);
                border-radius: {RADIUS['card']}px;
            }}
        """)
        warning_layout = QHBoxLayout(warning_card)
        warning_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                          SPACING['large'], SPACING['large'])
        warning_layout.setSpacing(SPACING['large'])

        warning_icon = build_icon_label(
            FluentIcon.MEGAPHONE, COLORS['warning_text'], size=40)
        warning_layout.addWidget(warning_icon)

        warning_text_layout = QVBoxLayout()
        warning_text_layout.setSpacing(SPACING['small'])

        warning_title = StrongBodyLabel("WARNING")
        warning_title.setStyleSheet(f"color: {COLORS['warning_text']};")
        warning_text_layout.addWidget(warning_title)

        warning_points = BodyLabel(
            "While OpCore Simplify significantly reduces setup time, the Hackintosh journey still requires:\n\n"
            "• Understanding basic concepts from the Dortania Guide\n"
            "• Testing and troubleshooting during the installation process\n"
            "• Patience and persistence in resolving any issues that arise\n\n"
            "Our tool does not guarantee a successful installation in the first attempt, but it should help you get started."
        )
        warning_points.setWordWrap(True)
        warning_points.setStyleSheet("color: #424242; line-height: 1.6;")
        warning_text_layout.addWidget(warning_points)

        warning_layout.addLayout(warning_text_layout)
        layout.addWidget(warning_card)

        # Getting Started timeline
        steps_card = CardWidget()
        steps_layout = QVBoxLayout(steps_card)
        steps_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                        SPACING['large'], SPACING['large'])
        steps_layout.setSpacing(SPACING['medium'])

        steps_title = StrongBodyLabel("Getting Started")
        steps_layout.addWidget(steps_title)

        step_items = [
            (FluentIcon.FOLDER_ADD, "1. Upload Hardware Report",
             "Load your system hardware information."),
            (FluentIcon.CHECKBOX, "2. Check Compatibility",
             "Verify your hardware is supported."),
            (FluentIcon.EDIT, "3. Configure Settings",
             "Customize ACPI patches, kexts, and SMBIOS."),
            (FluentIcon.DEVELOPER_TOOLS, "4. Build EFI",
             "Generate your OpenCore EFI folder."),
        ]

        for idx, (icon, title, desc) in enumerate(step_items):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING['medium'])

            row_icon = build_icon_label(icon, COLORS['primary'])
            row_layout.addWidget(row_icon)

            text_col = QVBoxLayout()
            text_col.setSpacing(SPACING['tiny'])
            title_label = StrongBodyLabel(title)
            desc_label = BodyLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                f"color: {COLORS['text_secondary']}; line-height: 1.6;")
            text_col.addWidget(title_label)
            text_col.addWidget(desc_label)
            row_layout.addLayout(text_col)

            steps_layout.addWidget(row)

            if idx < len(step_items) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setStyleSheet("color: #E1DFDD;")
                steps_layout.addWidget(divider)

        layout.addWidget(steps_card)

        layout.addStretch()

    def refresh(self):
        """Refresh page content"""
        pass
