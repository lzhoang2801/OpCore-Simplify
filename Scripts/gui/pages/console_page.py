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
    PrimaryPushButton,
    PushButton,
    StrongBodyLabel,
    SubtitleLabel,
    SwitchButton,
    TextEdit,
    FluentIcon,
)

from ..styles import COLORS, SPACING, RADIUS


class ConsolePage(QWidget):
    """Console log viewer with rich filtering and controls"""

    LEVELS = ("All", "Info", "Warning", "Error", "Debug")

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("consolePage")
        self.controller = parent

        self._log_entries: list[tuple[str, str]] = []
        self._auto_scroll_enabled = True
        self._last_update_text = "--"

        self.setup_ui()
        self._apply_filters()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            SPACING['xxlarge'],
            SPACING['xlarge'],
            SPACING['xxlarge'],
            SPACING['xlarge'],
        )
        layout.setSpacing(SPACING['large'])



        header_row = QHBoxLayout()

        header_row.addStretch()



        self.lines_value = StrongBodyLabel("0")
        self.last_update_value = StrongBodyLabel("--")
        self.filter_value = StrongBodyLabel("Showing all levels")


        controls_card = CardWidget()
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
        )
        controls_layout.setSpacing(SPACING['medium'])

        controls_header = QHBoxLayout()
        controls_header.addWidget(SubtitleLabel("Live Console Stream"))
        controls_header.addStretch()
        self.filter_status_label = BodyLabel("Showing all logs")
        self.filter_status_label.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        controls_header.addWidget(self.filter_status_label)
        controls_layout.addLayout(controls_header)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(SPACING['medium'])

        self.level_filter = ComboBox()
        self.level_filter.addItems(self.LEVELS)
        self.level_filter.currentTextChanged.connect(self._apply_filters)
        self.level_filter.setMinimumWidth(140)
        filter_row.addWidget(self.level_filter)

        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search message text...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self.search_input, stretch=1)

        controls_layout.addLayout(filter_row)

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(SPACING['large'])

        self.auto_scroll_switch = SwitchButton()
        self.auto_scroll_switch.setChecked(True)
        self.auto_scroll_switch.checkedChanged.connect(self._toggle_auto_scroll)

        auto_scroll_container = self._build_toggle_container(
            "Auto-scroll", "Stick to the most recent entry", self.auto_scroll_switch
        )
        toggle_row.addWidget(auto_scroll_container, stretch=1)

        self.wrap_switch = SwitchButton()
        self.wrap_switch.setChecked(True)
        self.wrap_switch.checkedChanged.connect(self._toggle_wrap_mode)

        wrap_container = self._build_toggle_container(
            "Soft wrap", "Wrap long lines for readability", self.wrap_switch
        )
        toggle_row.addWidget(wrap_container, stretch=1)

        controls_layout.addLayout(toggle_row)
        layout.addWidget(controls_card)

        console_card = CardWidget()
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
            SPACING['large'],
        )
        console_layout.setSpacing(SPACING['medium'])

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACING['small'])

        clear_btn = PushButton(FluentIcon.DELETE, "Clear")
        clear_btn.clicked.connect(self.clear_console)
        toolbar.addWidget(clear_btn)

        copy_btn = PushButton(FluentIcon.COPY, "Copy")
        copy_btn.clicked.connect(self.copy_console)
        toolbar.addWidget(copy_btn)

        save_btn = PrimaryPushButton(FluentIcon.SAVE, "Export")
        save_btn.clicked.connect(self.save_console)
        toolbar.addWidget(save_btn)

        toolbar.addStretch()

        jump_btn = PushButton(FluentIcon.DOWN, "Jump to bottom")
        jump_btn.clicked.connect(self.scroll_to_bottom)
        toolbar.addWidget(jump_btn)

        console_layout.addLayout(toolbar)

        self.console_text = TextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setPlaceholderText(
            "Waiting for console events..."
        )
        self.console_text.setMinimumHeight(520)
        self.console_text.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border: 1px solid {COLORS['border_light']};"
            f"border-radius: {RADIUS['card']}px;"
            "font-family: 'JetBrains Mono', 'SFMono-Regular', monospace;"
            "font-size: 13px;"
        )
        console_layout.addWidget(self.console_text)

        layout.addWidget(console_card)

    def _build_metric_card(self, title: str, value_widget: StrongBodyLabel, caption: str) -> CardWidget:
        card = CardWidget()
        card.setObjectName("consoleMetricCard")
        card.setStyleSheet(
            f"CardWidget#consoleMetricCard {{"
            f"background: rgba(0, 0, 0, 0.25);"
            "border: 1px solid rgba(255,255,255,0.28);"
            f"border-radius: {RADIUS['card']}px;"
            "}}"
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(SPACING['tiny'])

        title_label = BodyLabel(title)
        title_label.setStyleSheet("color: rgba(255,255,255,0.85);")
        layout.addWidget(title_label)

        value_widget.setStyleSheet("color: #FFFFFF; font-size: 26px;")
        layout.addWidget(value_widget)

        caption_label = BodyLabel(caption)
        caption_label.setStyleSheet("color: rgba(255,255,255,0.7);")
        layout.addWidget(caption_label)

        return card

    def _build_toggle_container(self, title: str, description: str, switch: SwitchButton) -> CardWidget:
        container = CardWidget()
        inner_layout = QHBoxLayout(container)
        inner_layout.setContentsMargins(SPACING['medium'], SPACING['small'], SPACING['medium'], SPACING['small'])
        inner_layout.setSpacing(SPACING['medium'])

        text_column = QVBoxLayout()
        text_column.setSpacing(0)
        text_column.addWidget(StrongBodyLabel(title))
        desc_label = BodyLabel(description)
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        text_column.addWidget(desc_label)

        inner_layout.addLayout(text_column)
        inner_layout.addStretch()
        inner_layout.addWidget(switch)

        return container

    def _apply_filters(self):
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
            placeholder = "No console entries match the current filters." if self._log_entries else "Waiting for console events..."
            self.console_text.setPlainText(placeholder)

        self.filter_value.setText(f"{level} filter")

        if self._auto_scroll_enabled and filtered:
            self.scroll_to_bottom()

        self._update_metrics(len(filtered), level)

    def _update_metrics(self, visible_count: int, level: str):
        self.lines_value.setText(str(len(self._log_entries)))
        self.last_update_value.setText(self._last_update_text)
        self.filter_status_label.setText(
            f"{visible_count} line(s) visible · {level}"
        )

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
