"""
Step 4: Build EFI - qfluentwidgets version
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PushButton, SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ProgressBar, PrimaryPushButton, FluentIcon
)

from ..styles import COLORS, SPACING


class BuildPage(QWidget):
    """Step 4: Build OpenCore EFI"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("buildPage")
        self.controller = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the build page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'],
                                  SPACING['xxlarge'], SPACING['xlarge'])
        layout.setSpacing(SPACING['large'])

        # Step indicator
        step_label = BodyLabel("STEP 4 OF 4")
        step_label.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(step_label)

        # Title
        title_label = SubtitleLabel("Build OpenCore EFI")
        layout.addWidget(title_label)

        subtitle_label = BodyLabel("Build your customized OpenCore EFI")
        subtitle_label.setStyleSheet("color: #605E5C;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(SPACING['large'])

        # Build card
        build_card = CardWidget()
        build_layout = QVBoxLayout(build_card)
        build_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                        SPACING['large'], SPACING['large'])

        card_title = StrongBodyLabel("Build Options")
        build_layout.addWidget(card_title)

        # Build button
        self.build_btn = PrimaryPushButton(
            FluentIcon.DEVELOPER_TOOLS, "Build OpenCore EFI")
        self.build_btn.clicked.connect(self.start_build)
        self.controller.build_btn = self.build_btn
        build_layout.addWidget(self.build_btn)

        # Progress bar
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(True)  # Make visible from the start
        self.progress_bar.setValue(0)
        self.controller.progress_bar = self.progress_bar
        build_layout.addWidget(self.progress_bar)
        
        # Progress status label
        self.progress_label = BodyLabel("Ready to build")
        self.progress_label.setStyleSheet("color: #605E5C;")
        build_layout.addWidget(self.progress_label)
        self.controller.progress_label = self.progress_label

        layout.addWidget(build_card)

        # Build log card
        log_card = CardWidget()
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                      SPACING['large'], SPACING['large'])

        log_title = StrongBodyLabel("Build Log")
        log_layout.addWidget(log_title)

        # Build log text area
        self.build_log = TextEdit()
        self.build_log.setReadOnly(True)
        self.build_log.setPlainText("Build log will appear here...")
        self.build_log.setMinimumHeight(300)
        self.controller.build_log = self.build_log
        log_layout.addWidget(self.build_log)

        # Open result button
        self.open_result_btn = PushButton(
            FluentIcon.FOLDER, "Open Result Folder")
        self.open_result_btn.clicked.connect(self.open_result)
        self.open_result_btn.setEnabled(False)
        self.controller.open_result_btn = self.open_result_btn
        log_layout.addWidget(self.open_result_btn)

        layout.addWidget(log_card)
        layout.addStretch()

    def start_build(self):
        """Start building EFI"""
        self.build_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting build...")
        self.build_log.clear()
        self.build_log.append("Starting build process...")
        self.build_log.append("")

        # Call controller build method
        self.controller.build_efi()

        # Re-enable button after build (should be done in callback)
        # For now, we'll just keep it disabled

    def open_result(self):
        """Open result folder"""
        import os
        import subprocess
        import platform

        result_dir = self.controller.ocpe.result_dir
        if os.path.exists(result_dir):
            if platform.system() == "Windows":
                os.startfile(result_dir)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", result_dir])
            else:
                subprocess.Popen(["xdg-open", result_dir])

    def refresh(self):
        """Refresh page content"""
        pass
