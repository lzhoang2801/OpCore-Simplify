"""
Step 1: Upload hardware report and ACPI tables.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget,
    FluentIcon, StrongBodyLabel, InfoBar, InfoBarPosition
)

from ..styles import SPACING
from ..ui_utils import create_step_indicator


class UploadPage(QWidget):
    """Step 1: Upload hardware report and ACPI tables."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("uploadPage")
        self.controller = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the upload page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])

        # Step indicator
        layout.addWidget(create_step_indicator(1))

        # Title
        title_label = SubtitleLabel("Upload Hardware Report")
        layout.addWidget(title_label)

        subtitle_label = BodyLabel(
            "Start by loading your system hardware information")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(SPACING['large'])

        # Upload card
        upload_card = CardWidget()
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                         SPACING['large'], SPACING['large'])

        card_title = StrongBodyLabel("Upload Methods")
        upload_layout.addWidget(card_title)

        # Select file button
        self.select_btn = PushButton(
            FluentIcon.FOLDER_ADD, "Select Hardware Report")
        self.select_btn.clicked.connect(self.select_report)
        upload_layout.addWidget(self.select_btn)

        # Export button (Windows only) - import os only when needed
        import os
        if os.name == 'nt':
            self.export_btn = PushButton(
                FluentIcon.DOWNLOAD, "Export Hardware Report")
            self.export_btn.clicked.connect(self.export_report)
            upload_layout.addWidget(self.export_btn)

        layout.addWidget(upload_card)

        # Status card
        status_card = CardWidget()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                         SPACING['large'], SPACING['large'])

        status_title = StrongBodyLabel("Current Status")
        status_layout.addWidget(status_title)

        self.status_label = BodyLabel("No hardware report loaded")
        self.status_label.setStyleSheet("color: #605E5C;")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_card)

        # Instructions card
        instructions_card = CardWidget()
        instructions_layout = QVBoxLayout(instructions_card)
        instructions_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                               SPACING['large'], SPACING['large'])

        instructions_title = StrongBodyLabel("Instructions")
        instructions_layout.addWidget(instructions_title)

        instructions_text = BodyLabel(
            "1. On Windows, use 'Export Hardware Report' for best results\n"
            "2. Alternatively, use Hardware Sniffer to generate Report.json\n"
            "3. Make sure to include ACPI dump for proper configuration"
        )
        instructions_text.setStyleSheet("color: #605E5C;")
        instructions_text.setWordWrap(True)
        instructions_layout.addWidget(instructions_text)

        layout.addWidget(instructions_card)

        layout.addStretch()

    def select_report(self):
        """Select hardware report file."""
        file_path = self.controller.select_hardware_report_gui()
        if not file_path:
            return
        
        # Validate and load report
        is_valid, errors, warnings, data = self.controller.ocpe.v.validate_report(file_path)

        if not is_valid or errors:
            InfoBar.error(
                title='Invalid Report',
                content='The selected report file is invalid. Please try again.',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            return

        # Load the report
        self.controller.load_hardware_report(file_path, data)

    def export_report(self):
        """Export hardware report."""
        self.controller.export_hardware_report()

    def update_status(self):
        """Update status display."""
        if self.controller.hardware_report_path != "Not selected":
            self.status_label.setText(
                f"Loaded: {self.controller.hardware_report_path}")
        else:
            self.status_label.setText("No hardware report loaded")

    def refresh(self):
        """Refresh page content."""
        self.update_status()
