from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from qfluentwidgets import SubtitleLabel, BodyLabel, CardWidget, StrongBodyLabel, FluentIcon, ScrollArea

from Scripts.styles import COLORS, SPACING, RADIUS
from Scripts import utils


class HomePage(ScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("homePage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.utils = utils.Utils()
        self.page()

    def page(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        
        self.scrollWidget.setStyleSheet("QWidget { background: transparent; }")
        
        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])
        self.expandLayout.setSpacing(SPACING['large'])

        self.expandLayout.addWidget(self._create_title_label())
        self.expandLayout.addWidget(self._create_hero_section())
        self.expandLayout.addWidget(self._create_note_card())
        self.expandLayout.addWidget(self._create_warning_card())
        self.expandLayout.addWidget(self._create_guide_card())

        self.expandLayout.addStretch()

    def _create_title_label(self):
        title_label = SubtitleLabel("Welcome to OpCore Simplify")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        return title_label

    def _create_hero_section(self):
        hero_card = CardWidget()
        
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        hero_layout.setSpacing(SPACING['large'])

        hero_text = QVBoxLayout()
        hero_text.setSpacing(SPACING['medium'])

        hero_title = StrongBodyLabel("Introduction")
        hero_title.setStyleSheet("font-size: 18px; color: {};".format(COLORS['primary']))
        hero_text.addWidget(hero_title)

        hero_body = BodyLabel(
            "A specialized tool that streamlines OpenCore EFI creation by automating the essential setup process and providing standardized configurations.<br>"
            "Designed to reduce manual effort while ensuring accuracy in your Hackintosh journey."
        )
        hero_body.setWordWrap(True)
        hero_body.setStyleSheet("line-height: 1.6; font-size: 14px;")
        hero_text.addWidget(hero_body)

        hero_layout.addLayout(hero_text, 2)

        robot_icon = self.utils.build_icon_label(FluentIcon.ROBOT, COLORS['primary'], size=64)
        hero_layout.addWidget(robot_icon, 1, Qt.AlignmentFlag.AlignVCenter)

        return hero_card

    def _create_note_card(self):
        note_card = CardWidget()
        
        note_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['note_bg']};
                border: 1px solid rgba(21, 101, 192, 0.2);
                border-radius: {RADIUS['card']}px;
            }}
        """)
        note_layout = QHBoxLayout(note_card)
        note_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        note_layout.setSpacing(SPACING['large'])

        note_icon = self.utils.build_icon_label(FluentIcon.INFO, COLORS['note_text'], size=40)
        note_layout.addWidget(note_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        note_text_layout = QVBoxLayout()
        note_text_layout.setSpacing(SPACING['small'])

        note_title = StrongBodyLabel("OpenCore Legacy Patcher 3.0.0 - Now Supports macOS Tahoe 26!")
        note_title.setStyleSheet("color: {}; font-size: 16px;".format(COLORS['note_text']))
        note_text_layout.addWidget(note_title)

        note_body = BodyLabel(
            "The long awaited version 3.0.0 of OpenCore Legacy Patcher is here, bringing <b>initial support for macOS Tahoe 26</b> to the community!<br><br>"
            "<b>Please Note:</b><br>"
            "- Only OpenCore-Patcher 3.0.0 from the <a href='https://github.com/lzhoang2801/OpenCore-Legacy-Patcher/releases/tag/3.0.0' style='color: #0078D4; text-decoration: none;'>lzhoang2801/OpenCore-Legacy-Patcher</a> repository provides support for macOS Tahoe 26 with early patches.<br>"
            "- Official Dortania releases or older patches <b>will NOT work</b> with macOS Tahoe 26."
        )
        note_body.setWordWrap(True)
        note_body.setOpenExternalLinks(True)
        note_body.setStyleSheet("color: #424242; line-height: 1.6;")
        note_text_layout.addWidget(note_body)

        note_layout.addLayout(note_text_layout)

        return note_card

    def _create_warning_card(self):
        warning_card = CardWidget()
        
        warning_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['warning_bg']};
                border: 1px solid rgba(245, 124, 0, 0.25);
                border-radius: {RADIUS['card']}px;
            }}
        """)
        warning_layout = QHBoxLayout(warning_card)
        warning_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        warning_layout.setSpacing(SPACING['large'])

        warning_icon = self.utils.build_icon_label(FluentIcon.MEGAPHONE, COLORS['warning_text'], size=40)
        warning_layout.addWidget(warning_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        warning_text_layout = QVBoxLayout()
        warning_text_layout.setSpacing(SPACING['small'])

        warning_title = StrongBodyLabel("WARNING")
        warning_title.setStyleSheet("color: {}; font-size: 16px;".format(COLORS['warning_text']))
        warning_text_layout.addWidget(warning_title)

        warning_points = BodyLabel(
            "While OpCore Simplify significantly reduces setup time, the Hackintosh journey still requires:<br><br>"
            "- Understanding basic concepts from the <a href='https://dortania.github.io/OpenCore-Install-Guide/' style='color: #F57C00; text-decoration: none;'>Dortania Guide</a><br>"
            "- Testing and troubleshooting during the installation process.<br>"
            "- Patience and persistence in resolving any issues that arise.<br><br>"
            "Our tool does not guarantee a successful installation in the first attempt, but it should help you get started."
        )
        warning_points.setWordWrap(True)
        warning_points.setOpenExternalLinks(True)
        warning_points.setStyleSheet("color: #424242; line-height: 1.6;")
        warning_text_layout.addWidget(warning_points)

        warning_layout.addLayout(warning_text_layout)

        return warning_card

    def _create_guide_card(self):
        guide_card = CardWidget()
        guide_layout = QVBoxLayout(guide_card)
        guide_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        guide_layout.setSpacing(SPACING['medium'])

        guide_title = StrongBodyLabel("Getting Started")
        guide_title.setStyleSheet("font-size: 18px;")
        guide_layout.addWidget(guide_title)

        step_items = [
            (FluentIcon.FOLDER_ADD, "1. Select Hardware Report", "Select hardware report of target system you want to build EFI for."),
            (FluentIcon.CHECKBOX, "2. Check Compatibility", "Review hardware compatibility with macOS."),
            (FluentIcon.EDIT, "3. Configure Settings", "Customize ACPI patches, kexts, and config for your OpenCore EFI."),
            (FluentIcon.DEVELOPER_TOOLS, "4. Build EFI", "Generate your OpenCore EFI."),
        ]

        for idx, (icon, title, desc) in enumerate(step_items):
            guide_layout.addWidget(self._create_guide_row(icon, title, desc))

            if idx < len(step_items) - 1:
                guide_layout.addWidget(self._create_divider())

        return guide_card

    def _create_guide_row(self, icon, title, desc):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING['medium'])

        icon_container = QWidget()
        icon_container.setFixedWidth(40)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        row_icon = self.utils.build_icon_label(icon, COLORS['primary'], size=24)
        icon_layout.addWidget(row_icon)
        
        row_layout.addWidget(icon_container)

        text_col = QVBoxLayout()
        text_col.setSpacing(SPACING['tiny'])
        
        title_label = StrongBodyLabel(title)
        title_label.setStyleSheet("font-size: 14px;")
        
        desc_label = BodyLabel(desc)
        desc_label.setWordWrap(True)
        
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.4;")
        
        text_col.addWidget(title_label)
        text_col.addWidget(desc_label)
        row_layout.addLayout(text_col)

        return row

    def _create_divider(self):
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {COLORS['border_light']};")
        return divider

    def refresh(self):
        pass