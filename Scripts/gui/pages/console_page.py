"""Console log page - elevated qfluentwidgets experience"""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    LineEdit,
    StrongBodyLabel,
    SubtitleLabel,
    SwitchButton,
    TextEdit,
    FluentIcon,
    ScrollArea,
    CommandBar,
    Action,
)

from ..styles import COLORS, SPACING, RADIUS


class ConsolePage(ScrollArea):
    """Console log viewer with rich filtering and controls"""

    LEVELS = ("All", "Info", "Warning", "Error", "Debug")

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("consolePage")
        self.controller = parent
        
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)

        self._log_entries: list[tuple[str, str]] = []
        self._auto_scroll_enabled = True
        self._last_update_text = "--"

        self.setup_ui()
        self._apply_filters()

    def setup_ui(self):
        # Configure scroll area
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        
        # Set layout spacing and margins
        layout = self.expandLayout
        layout.setContentsMargins(
            SPACING['xxlarge'],
            SPACING['xlarge'],
            SPACING['xxlarge'],
            SPACING['xlarge'],
        )
        layout.setSpacing(SPACING['large'])

        # Page header
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Console Log")
        header_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Real-time application logs and events")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        header_layout.addWidget(subtitle_label)

        layout.addWidget(header_container)

        # Simple filter controls in a single clean card
        filter_card = CardWidget()
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
        )
        filter_layout.setSpacing(SPACING['medium'])

        # Filter row with level and search side by side
        filter_row = QHBoxLayout()
        filter_row.setSpacing(SPACING['medium'])

        # Level filter
        level_label = BodyLabel("Level:")
        filter_row.addWidget(level_label)
        
        self.level_filter = ComboBox()
        self.level_filter.addItems(self.LEVELS)
        self.level_filter.currentTextChanged.connect(self._apply_filters)
        self.level_filter.setMinimumWidth(140)
        filter_row.addWidget(self.level_filter)

        # Search input
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search in logs...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self.search_input, stretch=1)

        filter_layout.addLayout(filter_row)

        # Toggle switches row
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(SPACING['large'])

        # Auto-scroll toggle
        auto_scroll_container = QWidget()
        auto_scroll_layout = QHBoxLayout(auto_scroll_container)
        auto_scroll_layout.setContentsMargins(0, 0, 0, 0)
        auto_scroll_layout.setSpacing(SPACING['small'])
        
        auto_scroll_label = BodyLabel("Auto-scroll")
        auto_scroll_layout.addWidget(auto_scroll_label)
        
        self.auto_scroll_switch = SwitchButton()
        self.auto_scroll_switch.setChecked(True)
        self.auto_scroll_switch.checkedChanged.connect(self._toggle_auto_scroll)
        auto_scroll_layout.addWidget(self.auto_scroll_switch)
        auto_scroll_layout.addStretch()
        
        toggle_row.addWidget(auto_scroll_container)

        # Word wrap toggle
        wrap_container = QWidget()
        wrap_layout = QHBoxLayout(wrap_container)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(SPACING['small'])
        
        wrap_label = BodyLabel("Word Wrap")
        wrap_layout.addWidget(wrap_label)
        
        self.wrap_switch = SwitchButton()
        self.wrap_switch.setChecked(True)
        self.wrap_switch.checkedChanged.connect(self._toggle_wrap_mode)
        wrap_layout.addWidget(self.wrap_switch)
        wrap_layout.addStretch()
        
        toggle_row.addWidget(wrap_container)
        toggle_row.addStretch()

        filter_layout.addLayout(toggle_row)

        # Filter status
        self.filter_status_label = BodyLabel("Showing all logs")
        self.filter_status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        filter_layout.addWidget(self.filter_status_label)

        layout.addWidget(filter_card)

        # Console output card
        console_card = CardWidget()
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
        )
        console_layout.setSpacing(SPACING['medium'])

        # Console header with CommandBar
        console_header = QHBoxLayout()
        console_title = StrongBodyLabel("Console Output")
        console_header.addWidget(console_title)
        console_header.addStretch()

        # Create CommandBar with actions
        self.command_bar = CommandBar(self.scrollWidget)
        
        # Clear action
        clear_action = Action(FluentIcon.DELETE, "Clear")
        clear_action.triggered.connect(self.clear_console)
        clear_action.setToolTip("Clear all console logs")
        self.command_bar.addAction(clear_action)
        
        # Copy action
        copy_action = Action(FluentIcon.COPY, "Copy")
        copy_action.triggered.connect(self.copy_console)
        copy_action.setToolTip("Copy visible logs to clipboard")
        self.command_bar.addAction(copy_action)
        
        # Export action (primary)
        export_action = Action(FluentIcon.SAVE, "Export")
        export_action.triggered.connect(self.save_console)
        export_action.setToolTip("Export logs to file")
        self.command_bar.addAction(export_action)
        
        self.command_bar.addSeparator()
        
        # Jump to bottom action
        jump_action = Action(FluentIcon.DOWN, "Jump to Bottom")
        jump_action.triggered.connect(self.scroll_to_bottom)
        jump_action.setToolTip("Scroll to the bottom of the console")
        self.command_bar.addAction(jump_action)
        
        console_header.addWidget(self.command_bar)
        console_layout.addLayout(console_header)

        # Console text area
        self.console_text = TextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setPlaceholderText(
            "Console logs will appear here...\n\n"
            "Waiting for application events..."
        )
        self.console_text.setMinimumHeight(450)
        self.console_text.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border: 1px solid {COLORS['border_light']};"
            f"border-radius: {RADIUS['card']}px;"
            "font-family: 'Consolas', 'Monaco', 'Courier New', monospace;"
            "font-size: 13px;"
            "padding: 8px;"
        )
        console_layout.addWidget(self.console_text)

        layout.addWidget(console_card)
        layout.addStretch()

    def _apply_filters(self):
        """Apply current filter settings to log entries"""
        level = self.level_filter.currentText() if hasattr(self, 'level_filter') else self.LEVELS[0]
        query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""

        filtered: list[str] = []
        for entry_level, entry_text in self._log_entries:
            if level != "All" and entry_level.lower() != level.lower():
                continue
            if query and query not in entry_text.lower():
                continue
            filtered.append(entry_text)

        if filtered:
            self.console_text.setPlainText("\n".join(filtered))
        else:
            placeholder = "No logs match the current filters." if self._log_entries else "Console logs will appear here...\n\nWaiting for application events..."
            self.console_text.setPlainText(placeholder)

        if self._auto_scroll_enabled and filtered:
            self.scroll_to_bottom()

        self._update_metrics(len(filtered), level)

    def _update_metrics(self, visible_count: int, level: str):
        """Update the filter status display"""
        # Update filter status label with detailed information
        if len(self._log_entries) == 0:
            status_text = "No logs yet"
        elif visible_count == len(self._log_entries):
            status_text = f"Showing all {visible_count} log(s)"
        else:
            status_text = f"Showing {visible_count} of {len(self._log_entries)} log(s)"
        
        if level != "All":
            status_text += f" · Filter: {level}"
        
        search_query = self.search_input.text().strip() if hasattr(self, 'search_input') else ""
        if search_query:
            status_text += f" · Search: '{search_query}'"
            
        self.filter_status_label.setText(status_text)

    def _toggle_auto_scroll(self, checked: bool):
        self._auto_scroll_enabled = checked

    def _toggle_wrap_mode(self, checked: bool):
        mode = (
            QTextEdit.LineWrapMode.WidgetWidth
            if checked
            else QTextEdit.LineWrapMode.NoWrap
        )
        self.console_text.setLineWrapMode(mode)

    def append_log(self, message: str, level: str = "Info"):
        normalized_level = level.capitalize() if level else "Info"
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{normalized_level.upper()}] {message}"
        self._log_entries.append((normalized_level, formatted))
        self._last_update_text = timestamp
        self._apply_filters()

    def clear_console(self):
        self._log_entries.clear()
        self._last_update_text = "--"
        self._apply_filters()

    def copy_console(self):
        QApplication.clipboard().setText(self.console_text.toPlainText())
        self.controller.update_status("Console log copied", 'success')

    def save_console(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Console Log",
            "console.log",
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.console_text.toPlainText())
                self.controller.update_status("Console log saved successfully", 'success')
            except Exception as exc:  # pragma: no cover - surfaced via status chip
                self.controller.update_status(f"Failed to save log: {exc}", 'error')

    def scroll_to_bottom(self):
        scroll_bar = self.console_text.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def refresh(self):
        """Allow parent controller to request a soft refresh."""
        self._apply_filters()
