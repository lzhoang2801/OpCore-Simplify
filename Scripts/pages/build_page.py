import platform

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CardWidget, TextEdit,
    StrongBodyLabel, ProgressBar, PrimaryPushButton, FluentIcon,
    ScrollArea, TitleLabel
)

from Scripts.styles import COLORS, SPACING, RADIUS
from Scripts import ui_utils
from Scripts.custom_dialogs import show_confirmation

DEFAULT_LOG_TEXT = "Build log will appear here..."


class BuildPage(ScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("buildPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.build_in_progress = False
        self.build_successful = False
        self.ui_utils = ui_utils.UIUtils()
        self.page()

    def page(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])
        self.expandLayout.setSpacing(SPACING['xlarge'])

        layout = self.expandLayout

        layout.addWidget(self.ui_utils.create_step_indicator(4))

        title_label = TitleLabel("Build OpenCore EFI")
        layout.addWidget(title_label)

        subtitle_label = BodyLabel("Build your customized OpenCore EFI ready for installation")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle_label)

        layout.addSpacing(SPACING['medium'])

        self.instructions_after_build_card = CardWidget(self.scrollWidget)
        
        self.instructions_after_build_card.setStyleSheet(f"""
            CardWidget {{
                background-color: {COLORS['warning_bg']};
                border: 1px solid rgba(245, 124, 0, 0.25);
                border-radius: {RADIUS['card']}px;
            }}
        """)
        instructions_after_layout = QHBoxLayout(self.instructions_after_build_card)
        instructions_after_layout.setContentsMargins(SPACING['large'], SPACING['large'], SPACING['large'], SPACING['large'])
        instructions_after_layout.setSpacing(SPACING['large'])

        warning_icon = self.ui_utils.build_icon_label(FluentIcon.MEGAPHONE, COLORS['warning_text'], size=40)
        instructions_after_layout.addWidget(warning_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        warning_text_layout = QVBoxLayout()
        warning_text_layout.setSpacing(SPACING['small'])

        warning_title = StrongBodyLabel("Before Using Your EFI")
        warning_title.setStyleSheet("color: {}; font-size: 16px;".format(COLORS['warning_text']))
        warning_text_layout.addWidget(warning_title)

        instructions_after_intro = BodyLabel(
            "Please complete these important steps before using the built EFI:"
        )
        instructions_after_intro.setWordWrap(True)
        instructions_after_intro.setStyleSheet("color: #424242; line-height: 1.6;")
        warning_text_layout.addWidget(instructions_after_intro)
        
        self.instructions_after_content = QWidget()
        self.instructions_after_content_layout = QVBoxLayout(self.instructions_after_content)
        self.instructions_after_content_layout.setContentsMargins(0, 0, 0, 0)
        self.instructions_after_content_layout.setSpacing(SPACING['medium'])
        warning_text_layout.addWidget(self.instructions_after_content)

        instructions_after_layout.addLayout(warning_text_layout)
        
        self.instructions_after_build_card.setVisible(False)
        layout.addWidget(self.instructions_after_build_card)

        build_control_card = CardWidget(self.scrollWidget)
        build_control_card.setBorderRadius(RADIUS['card'])
        build_control_layout = QVBoxLayout(build_control_card)
        build_control_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                               SPACING['large'], SPACING['large'])
        build_control_layout.setSpacing(SPACING['xlarge'])
        
        control_header_layout = QHBoxLayout()
        control_header_layout.setSpacing(SPACING['medium'])
        control_icon = self.ui_utils.build_icon_label(FluentIcon.DEVELOPER_TOOLS, COLORS['primary'], size=28)
        control_header_layout.addWidget(control_icon)
        
        control_title = SubtitleLabel("Build Control")
        control_title.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        control_header_layout.addWidget(control_title)
        control_header_layout.addStretch()
        build_control_layout.addLayout(control_header_layout)

        action_section = QWidget()
        action_layout = QVBoxLayout(action_section)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING['medium'])

        self.build_btn = PrimaryPushButton(FluentIcon.DEVELOPER_TOOLS, "Build OpenCore EFI")
        self.build_btn.clicked.connect(self.start_build)
        self.build_btn.setFixedHeight(48)
        self.controller.build_btn = self.build_btn
        action_layout.addWidget(self.build_btn)

        self.open_result_btn = PrimaryPushButton(FluentIcon.FOLDER, "Open Result Folder")
        self.open_result_btn.clicked.connect(self.open_result)
        self.open_result_btn.setFixedHeight(48)
        self.open_result_btn.setEnabled(False)
        self.controller.open_result_btn = self.open_result_btn
        action_layout.addWidget(self.open_result_btn)
        
        build_control_layout.addWidget(action_section)

        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(SPACING['medium'])

        status_row = QHBoxLayout()
        status_row.setSpacing(SPACING['medium'])
        
        self.status_icon_label = QLabel()
        self.status_icon_label.setFixedSize(28, 28)
        status_row.addWidget(self.status_icon_label)
        
        self.progress_label = StrongBodyLabel("Ready to build")
        self.progress_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px; font-weight: 600;")
        status_row.addWidget(self.progress_label)
        status_row.addStretch()
        
        progress_layout.addLayout(status_row)

        self.progress_bar = ProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(True)
        self.controller.progress_bar = self.progress_bar
        progress_layout.addWidget(self.progress_bar)
        
        self.controller.progress_label = self.progress_label
        self.progress_container.setVisible(False)
        
        build_control_layout.addWidget(self.progress_container)
        layout.addWidget(build_control_card)

        log_card = CardWidget(self.scrollWidget)
        log_card.setBorderRadius(RADIUS['card'])
        log_card_layout = QVBoxLayout(log_card)
        log_card_layout.setContentsMargins(SPACING['large'], SPACING['large'],
                                          SPACING['large'], SPACING['large'])
        log_card_layout.setSpacing(SPACING['medium'])
        
        log_header_layout = QHBoxLayout()
        log_header_layout.setSpacing(SPACING['medium'])
        log_icon = self.ui_utils.build_icon_label(FluentIcon.DOCUMENT, COLORS['primary'], size=28)
        log_header_layout.addWidget(log_icon)
        
        log_title = SubtitleLabel("Build Log")
        log_title.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        log_header_layout.addWidget(log_title)
        log_header_layout.addStretch()
        log_card_layout.addLayout(log_header_layout)
        
        log_description = BodyLabel("Detailed build process information and status updates")
        log_description.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        log_card_layout.addWidget(log_description)

        self.build_log = TextEdit()
        self.build_log.setReadOnly(True)
        self.build_log.setPlainText(DEFAULT_LOG_TEXT)
        self.build_log.setMinimumHeight(400)
        self.build_log.setStyleSheet(f"""
            TextEdit {{
                background-color: rgba(0, 0, 0, 0.03);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: {RADIUS['small']}px;
                padding: {SPACING['large']}px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.7;
            }}
        """)
        self.controller.build_log = self.build_log
        log_card_layout.addWidget(self.build_log)
        
        layout.addWidget(log_card)

        layout.addStretch()

    def start_build(self):
        if not self.controller.hardware_state.hardware_report:
            self.controller.update_status("Please select hardware report first", 'warning')
            return

        if self.controller.hardware_state.compatibility_error:
            self.controller.update_status("Incompatible hardware detected, please select different hardware report and try again", 'warning')
            return

        if not self.controller.macos_state.darwin_version:
            self.controller.update_status("Please select target macOS version first", 'warning')
            return

        if self.controller.macos_state.needs_oclp:
            content = (
                "1. OpenCore Legacy Patcher allows restoring support for dropped GPUs and Broadcom WiFi on newer versions of macOS, and also enables AppleHDA on macOS Tahoe 26.<br>"
                "2. OpenCore Legacy Patcher needs SIP disabled for applying custom kernel patches, which can cause instability, security risks and update issues.<br>"
                "3. OpenCore Legacy Patcher does not officially support the Hackintosh community.<br><br>"
                "<b><font color='{info_color}'>Support for macOS Tahoe 26:</font></b><br>"
                "To patch macOS Tahoe 26, you must download OpenCore-Patcher 3.0.0 or newer from my repository: <a href='https://github.com/lzhoang2801/OpenCore-Legacy-Patcher/releases/tag/3.0.0'>lzhoang2801/OpenCore-Legacy-Patcher</a>.<br>"
                "Official Dortania releases or older patches will NOT work with macOS Tahoe 26."
            ).format(error_color=COLORS['error'], info_color='#00BCD4')
            if not show_confirmation("OpenCore Legacy Patcher Warning", content, parent=self.window()):
                return

        self.build_in_progress = True
        self.build_successful = False
        self.build_btn.setEnabled(False)
        self.build_btn.setText("Building...")
        self.open_result_btn.setEnabled(False)
        
        self.progress_container.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.update_status_icon("building")
        self.progress_label.setText("Preparing to build...")
        self.progress_label.setStyleSheet(f"color: {COLORS['primary']};")
        
        self.instructions_after_build_card.setVisible(False)
        self.build_log.clear()
        
        self.controller.build_efi()

    def update_status_icon(self, status):
        icon_size = 28
        icon_map = {
            "building": (FluentIcon.SYNC, COLORS['primary']),
            "success": (FluentIcon.COMPLETED, COLORS['success']),
            "error": (FluentIcon.CLOSE, COLORS['error']),
        }
        
        if status in icon_map:
            icon, color = icon_map[status]
            pixmap = icon.icon(color=color).pixmap(icon_size, icon_size)
            self.status_icon_label.setPixmap(pixmap)

    def show_post_build_instructions(self, bios_requirements):
        while self.instructions_after_content_layout.count():
            item = self.instructions_after_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if bios_requirements:
            bios_header = StrongBodyLabel("1. BIOS/UEFI Settings Required:")
            bios_header.setStyleSheet(f"color: {COLORS['warning_text']}; font-size: 14px;")
            self.instructions_after_content_layout.addWidget(bios_header)
            
            bios_text = "\n".join([f"  • {req}" for req in bios_requirements])
            bios_label = BodyLabel(bios_text)
            bios_label.setWordWrap(True)
            bios_label.setStyleSheet("color: #424242; line-height: 1.6;")
            self.instructions_after_content_layout.addWidget(bios_label)
            
            self.instructions_after_content_layout.addSpacing(SPACING['medium'])
        
        usb_header = StrongBodyLabel(f"{'2' if bios_requirements else '1'}. USB Port Mapping:")
        usb_header.setStyleSheet(f"color: {COLORS['warning_text']}; font-size: 14px;")
        self.instructions_after_content_layout.addWidget(usb_header)
        
        path_sep = "\\" if platform.system() == "Windows" else "/"
        
        usb_mapping_instructions = (
            "1. Use USBToolBox tool to map USB ports<br>"
            "2. Add created UTBMap.kext into the EFI{path_sep}OC{path_sep}Kexts folder<br>"
            "3. Remove UTBDefault.kext from the EFI{path_sep}OC{path_sep}Kexts folder<br>"
            "4. Edit config.plist using ProperTree:<br>"
            "   a. Run OC Snapshot (Command/Ctrl + R)<br>"
            "   b. Enable XhciPortLimit quirk if you have more than 15 ports per controller<br>"
            "   c. Save the file when finished."
        ).format(path_sep=path_sep)
        
        usb_label = BodyLabel(usb_mapping_instructions)
        usb_label.setWordWrap(True)
        usb_label.setStyleSheet("color: #424242; line-height: 1.6;")
        self.instructions_after_content_layout.addWidget(usb_label)
        
        self.instructions_after_build_card.setVisible(True)

    def on_build_complete(self, success=True, bios_requirements=None):
        self.build_in_progress = False
        self.build_successful = success
        
        if success:
            self.update_status_icon("success")
            self.progress_label.setText("✓ Build completed successfully!")
            self.progress_label.setStyleSheet(f"color: {COLORS['success']};")
            self.progress_bar.setValue(100)
            
            self.show_post_build_instructions(bios_requirements)
            
            self.build_btn.setText("Build OpenCore EFI")
            self.build_btn.setEnabled(True)
            self.open_result_btn.setEnabled(True)
            
            success_message = 'Your OpenCore EFI has been built successfully!'
            if bios_requirements is not None:
                success_message += ' Review the important instructions below.'
            
            self.controller.update_status(success_message, 'success')
        else:
            self.update_status_icon("error")
            self.progress_label.setText("Build OpenCore EFI failed")
            self.progress_label.setStyleSheet(f"color: {COLORS['error']};")
            
            self.build_btn.setText("Retry Build OpenCore EFI")
            self.build_btn.setEnabled(True)
            self.open_result_btn.setEnabled(False)
            
            self.controller.update_status("An error occurred during the build. Check the log for details.", 'error')

    def open_result(self):
        result_dir = self.controller.backend.result_dir
        try:
            self.controller.backend.u.open_folder(result_dir)
        except Exception as e:
            self.controller.update_status("Failed to open result folder: {}".format(e), 'warning')

    def refresh(self):
        if not self.build_in_progress:
            if self.build_successful:
                self.progress_container.setVisible(True)
                self.open_result_btn.setEnabled(True)
            else:
                log_text = self.build_log.toPlainText()
                if not log_text or log_text == DEFAULT_LOG_TEXT:
                    self.progress_container.setVisible(False)
                self.open_result_btn.setEnabled(False)
