from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from qfluentwidgets import SubtitleLabel, BodyLabel, ScrollArea, FluentIcon, GroupHeaderCardWidget

from ..styles import COLORS, SPACING
from ..ui_utils import create_info_widget, colored_icon, add_group_with_indent, create_step_indicator, get_compatibility_icon
from ...datasets import os_data, pci_data


class CompatibilityStatusBanner(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(12)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel()
        self.title_label = QLabel()
        font = QFont()
        font.setBold(True)
        font.setPixelSize(16)
        self.title_label.setFont(font)
        
        self.header_layout.addWidget(self.icon_label)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        
        self.layout.addLayout(self.header_layout)
        
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("font-size: 14px; color: #323130;")
        self.layout.addWidget(self.message_label)
        
        self.note_label = QLabel()
        self.note_label.setWordWrap(True)
        note_font = QFont()
        note_font.setItalic(True)
        note_font.setPixelSize(12)
        self.note_label.setFont(note_font)
        self.layout.addWidget(self.note_label)

        self.setVisible(False)

    def _update_style(self, bg_color, border_color, note_color, icon, title, message, note):
        self.setStyleSheet(f"""
            CompatibilityStatusBanner {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)
        self.title_label.setStyleSheet(f"color: {border_color};")
        self.title_label.setText(title)
        
        self.icon_label.setPixmap(icon.icon(color=QColor(border_color)).pixmap(20, 20))
        
        self.message_label.setText(message)
        
        if note:
            self.note_label.setText(note)
            self.note_label.setStyleSheet(f"color: {note_color};")
            self.note_label.setVisible(True)
        else:
            self.note_label.setVisible(False)
            
        self.setVisible(True)

    def show_error(self, title, message, note=""):
        self._update_style("#FDE7E9", "#D13438", "#A4262C", FluentIcon.CANCEL, title, message, note)

    def show_success(self, title, message, note=""):
        self._update_style("#DFF6DD", "#107C10", "#0E5C0E", FluentIcon.ACCEPT, title, message, note)

class CompatibilityPage(ScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("compatibilityPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        
        self.contentWidget = None
        self.contentLayout = None
        self.version_support_container = None
        self.native_support_label = None
        self.ocl_support_label = None
        
        self.setup_ui()

    def setup_ui(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

        self.expandLayout.setContentsMargins(SPACING['xxlarge'], SPACING['xlarge'], SPACING['xxlarge'], SPACING['xlarge'])
        self.expandLayout.setSpacing(SPACING['large'])

        self.expandLayout.addWidget(create_step_indicator(2))

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['large'])

        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING['tiny'])

        title_label = SubtitleLabel("Hardware Compatibility")
        title_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Review hardware compatibility with macOS")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(title_block, 1)

        self.expandLayout.addWidget(header_container)
        
        self.status_banner = CompatibilityStatusBanner(self.scrollWidget)
        self.expandLayout.addWidget(self.status_banner)
        
        self.expandLayout.addSpacing(SPACING['large'])

        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(SPACING['large'])
        self.expandLayout.addWidget(self.contentWidget)

        self.placeholder_label = BodyLabel("Load a hardware report to see compatibility information")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
        self.placeholder_label.setWordWrap(True)
        self.contentLayout.addWidget(self.placeholder_label)
        self.contentLayout.addStretch()

    def update_status_banner(self):
        if not self.controller.hardware_state.hardware_report:
            self.status_banner.setVisible(False)
            return

        if self.controller.hardware_state.compatibility_error:
            self._show_error_banner()
            return

        self._show_support_banner()

    def _show_error_banner(self):
        codes = self.controller.hardware_state.compatibility_error
        if isinstance(codes, str):
            codes = [codes]

        code_map = {
            "ERROR_MISSING_SSE4": (
                "Missing required SSE4.x instruction set.",
                "Your CPU is not supported by macOS versions newer than Sierra (10.12)."
            ),
            "ERROR_NO_COMPATIBLE_GPU": (
                "You cannot install macOS without a supported GPU.",
                "Please do NOT spam my inbox or issue tracker about this issue anymore!"
            ),
            "ERROR_INTEL_VMD": (
                "Intel VMD controllers are not supported in macOS.",
                "Please disable Intel VMD in the BIOS settings and try again with new hardware report."
            ),
            "ERROR_NO_COMPATIBLE_STORAGE": (
                "No compatible storage controller for macOS was found!",
                "Consider purchasing a compatible SSD NVMe for your system."
            )
        }

        title = "Hardware Compatibility Issue"
        messages = []
        notes = []
        for code in codes:
            msg, note = code_map.get(code, (code, ""))
            messages.append(msg)
            if note:
                notes.append(note)

        self.status_banner.show_error(
            title,
            "\n".join(messages),
            "\n".join(notes)
        )

    def _show_support_banner(self):
        if self.controller.macos_state.native_version:
            min_ver_name = os_data.get_macos_name_by_darwin(self.controller.macos_state.native_version[0])
            max_ver_name = os_data.get_macos_name_by_darwin(self.controller.macos_state.native_version[-1])
            native_range = min_ver_name if min_ver_name == max_ver_name else f"{min_ver_name} to {max_ver_name}"
            
            message = f"Native support: {native_range}"
            
            if self.controller.macos_state.ocl_patched_version:
                 oclp_max_name = os_data.get_macos_name_by_darwin(self.controller.macos_state.ocl_patched_version[0])
                 oclp_min_name = os_data.get_macos_name_by_darwin(self.controller.macos_state.ocl_patched_version[-1])
                 oclp_range = oclp_min_name if oclp_min_name == oclp_max_name else f"{oclp_min_name} to {oclp_max_name}"
                 message += f"\nOCLP support: {oclp_range}"

            self.status_banner.show_success("Hardware is Compatible", message)
        else:
            self.status_banner.show_error(
                "Incompatible Hardware",
                "No supported macOS version found for this hardware configuration."
            )

    def format_compatibility(self, compat_tuple):
        if not compat_tuple or compat_tuple == (None, None):
            return "Unsupported", "#D13438"

        max_ver, min_ver = compat_tuple

        if max_ver and min_ver:
            max_name = os_data.get_macos_name_by_darwin(max_ver)
            min_name = os_data.get_macos_name_by_darwin(min_ver)

            if max_name == min_name:
                return f"Up to {max_name}", "#0078D4"
            else:
                return f"{min_name} to {max_name}", "#107C10"

        return "Unknown", "#605E5C"

    def update_display(self):
        if not self.contentLayout:
            return

        while self.contentLayout.count() > 0:
            item = self.contentLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.controller.hardware_state.hardware_report:
            if self.version_support_container:
                self.version_support_container.setVisible(False)
            self._show_placeholder()
            return

        report = self.controller.hardware_state.hardware_report
        cards_added = 0

        cards_added += self._add_cpu_card(report)
        cards_added += self._add_gpu_card(report)
        cards_added += self._add_sound_card(report)
        cards_added += self._add_network_card(report)
        cards_added += self._add_storage_card(report)
        cards_added += self._add_bluetooth_card(report)
        cards_added += self._add_biometric_card(report)
        cards_added += self._add_sd_card(report)

        if cards_added == 0:
            self._show_no_data_label()

        self.contentLayout.addStretch()
        self.update_status_banner()
        self.scrollWidget.updateGeometry()
        self.scrollWidget.update()
        self.update()

    def _show_placeholder(self):
        self.placeholder_label = BodyLabel("Load a hardware report to see compatibility information")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
        self.placeholder_label.setWordWrap(True)
        self.contentLayout.addWidget(self.placeholder_label)
        self.contentLayout.addStretch()

    def _show_no_data_label(self):
        no_data_label = BodyLabel(
            "No compatible hardware information found in the report.\n"
            "Please ensure the hardware report contains valid device data."
        )
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_data_label.setStyleSheet("color: #D13438; padding: 40px;")
        no_data_label.setWordWrap(True)
        self.contentLayout.addWidget(no_data_label)

    def _add_compatibility_group(self, card, title, compat):
        compat_text, compat_color = self.format_compatibility(compat)
        add_group_with_indent(
            card,
            get_compatibility_icon(compat),
            title,
            compat_text,
            create_info_widget("", compat_color),
            indent_level=1
        )

    def _add_cpu_card(self, report):
        if 'CPU' not in report: return 0
        cpu_info = report['CPU']
        if not isinstance(cpu_info, dict): return 0
        
        cpu_card = GroupHeaderCardWidget(self.scrollWidget)
        cpu_card.setTitle("CPU")
        
        name = cpu_info.get('Processor Name', 'Unknown')
        add_group_with_indent(
            cpu_card,
            colored_icon(FluentIcon.TAG, COLORS['primary']),
            "Processor",
            name,
            indent_level=0
        )

        self._add_compatibility_group(cpu_card, "macOS Compatibility", cpu_info.get('Compatibility', (None, None)))

        details = []
        if cpu_info.get('Codename'):
            details.append(f"Codename: {cpu_info.get('Codename')}")
        if cpu_info.get('Core Count'):
            details.append(f"Cores: {cpu_info.get('Core Count')}")

        if details:
            add_group_with_indent(
                cpu_card,
                colored_icon(FluentIcon.INFO, COLORS['info']),
                "Details",
                " • ".join(details),
                indent_level=1
            )

        self.contentLayout.addWidget(cpu_card)
        return 1

    def _add_gpu_card(self, report):
        if 'GPU' not in report or not report['GPU']: return 0
        
        gpu_card = GroupHeaderCardWidget(self.scrollWidget)
        gpu_card.setTitle("Graphics")

        for idx, (gpu_name, gpu_info) in enumerate(report['GPU'].items()):
            device_type = gpu_info.get('Device Type', 'Unknown')
            add_group_with_indent(
                gpu_card,
                colored_icon(FluentIcon.PHOTO, COLORS['primary']),
                gpu_name,
                f"Type: {device_type}",
                indent_level=0
            )

            self._add_compatibility_group(gpu_card, "macOS Compatibility", gpu_info.get('Compatibility', (None, None)))

            if 'OCLP Compatibility' in gpu_info:
                oclp_compat = gpu_info.get('OCLP Compatibility')
                oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                add_group_with_indent(
                    gpu_card,
                    colored_icon(FluentIcon.IOT, COLORS['primary']),
                    "OCLP Compatibility",
                    oclp_text,
                    create_info_widget("Extended support with OpenCore Legacy Patcher", COLORS['text_secondary']),
                    indent_level=1
                )

            if 'Monitor' in report:
                self._add_monitor_info(gpu_card, gpu_name, gpu_info, report['Monitor'])

        self.contentLayout.addWidget(gpu_card)
        return 1

    def _add_monitor_info(self, gpu_card, gpu_name, gpu_info, monitors):
        connected_monitors = []
        for monitor_name, monitor_info in monitors.items():
            if monitor_info.get('Connected GPU') == gpu_name:
                connector = monitor_info.get('Connector Type', 'Unknown')
                monitor_str = f"{monitor_name} ({connector})"
                
                manufacturer = gpu_info.get('Manufacturer', '')
                raw_device_id = gpu_info.get('Device ID', '')
                device_id = raw_device_id[5:] if len(raw_device_id) > 5 else raw_device_id

                if "Intel" in manufacturer and device_id.startswith(("01", "04", "0A", "0C", "0D")):
                    if connector == "VGA":
                        monitor_str += " (Unsupported)"

                connected_monitors.append(monitor_str)

        if connected_monitors:
            add_group_with_indent(
                gpu_card,
                colored_icon(FluentIcon.VIEW, COLORS['info']),
                "Connected Displays",
                ", ".join(connected_monitors),
                indent_level=1
            )

    def _add_sound_card(self, report):
        if 'Sound' not in report or not report['Sound']: return 0
        
        sound_card = GroupHeaderCardWidget(self.scrollWidget)
        sound_card.setTitle("Audio")

        for audio_device, audio_props in report['Sound'].items():
            add_group_with_indent(
                sound_card,
                colored_icon(FluentIcon.MUSIC, COLORS['primary']),
                audio_device,
                "",
                indent_level=0
            )

            self._add_compatibility_group(sound_card, "macOS Compatibility", audio_props.get('Compatibility', (None, None)))

            endpoints = audio_props.get('Audio Endpoints', [])
            if endpoints:
                add_group_with_indent(
                    sound_card,
                    colored_icon(FluentIcon.HEADPHONE, COLORS['info']),
                    "Audio Endpoints",
                    ", ".join(endpoints),
                    indent_level=1
                )

        self.contentLayout.addWidget(sound_card)
        return 1

    def _add_network_card(self, report):
        if 'Network' not in report or not report['Network']: return 0
        
        network_card = GroupHeaderCardWidget(self.scrollWidget)
        network_card.setTitle("Network")

        for device_name, device_props in report['Network'].items():
            add_group_with_indent(
                network_card,
                colored_icon(FluentIcon.WIFI, COLORS['primary']),
                device_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(network_card, "macOS Compatibility", device_props.get('Compatibility', (None, None)))

            if 'OCLP Compatibility' in device_props:
                oclp_compat = device_props.get('OCLP Compatibility')
                oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                add_group_with_indent(
                    network_card,
                    colored_icon(FluentIcon.IOT, COLORS['primary']),
                    "OCLP Compatibility",
                    oclp_text,
                    create_info_widget("Extended support with OpenCore Legacy Patcher", COLORS['text_secondary']),
                    indent_level=1
                )

            self._add_continuity_info(network_card, device_props)

        self.contentLayout.addWidget(network_card)
        return 1

    def _add_continuity_info(self, network_card, device_props):
        device_id = device_props.get('Device ID', '')
        if not device_id: return
        
        continuity_info = ""
        continuity_color = COLORS['text_secondary']

        if device_id in pci_data.BroadcomWiFiIDs:
            continuity_info = "Full support (AirDrop, Handoff, Universal Clipboard, Instant Hotspot, etc.)"
            continuity_color = COLORS['success']
        elif device_id in pci_data.IntelWiFiIDs:
            continuity_info = "Partial (Handoff and Universal Clipboard with AirportItlwm) - AirDrop, Universal Clipboard, Instant Hotspot,... not available"
            continuity_color = COLORS['warning']
        elif device_id in pci_data.AtherosWiFiIDs:
            continuity_info = "Limited support (No Continuity features available). Atheros cards are not recommended for macOS."
            continuity_color = COLORS['error']

        if continuity_info:
            add_group_with_indent(
                network_card,
                colored_icon(FluentIcon.SYNC, continuity_color),
                "Continuity Features",
                continuity_info,
                create_info_widget("", continuity_color),
                indent_level=1
            )

    def _add_storage_card(self, report):
        if 'Storage Controllers' not in report or not report['Storage Controllers']: return 0
        
        storage_card = GroupHeaderCardWidget(self.scrollWidget)
        storage_card.setTitle("Storage")

        for controller_name, controller_props in report['Storage Controllers'].items():
            add_group_with_indent(
                storage_card,
                colored_icon(FluentIcon.FOLDER, COLORS['primary']),
                controller_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(storage_card, "macOS Compatibility", controller_props.get('Compatibility', (None, None)))

            disk_drives = controller_props.get("Disk Drives", [])
            if disk_drives:
                add_group_with_indent(
                    storage_card,
                    colored_icon(FluentIcon.FOLDER, COLORS['info']),
                    "Disk Drives",
                    ", ".join(disk_drives),
                    indent_level=1
                )

        self.contentLayout.addWidget(storage_card)
        return 1

    def _add_bluetooth_card(self, report):
        if 'Bluetooth' not in report or not report['Bluetooth']: return 0
        
        bluetooth_card = GroupHeaderCardWidget(self.scrollWidget)
        bluetooth_card.setTitle("Bluetooth")

        for bluetooth_name, bluetooth_props in report['Bluetooth'].items():
            add_group_with_indent(
                bluetooth_card,
                colored_icon(FluentIcon.BLUETOOTH, COLORS['primary']),
                bluetooth_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(bluetooth_card, "macOS Compatibility", bluetooth_props.get('Compatibility', (None, None)))

        self.contentLayout.addWidget(bluetooth_card)
        return 1

    def _add_biometric_card(self, report):
        if 'Biometric' not in report or not report['Biometric']: return 0
        bio_card = GroupHeaderCardWidget(self.scrollWidget)
        bio_card.setTitle("Biometric")

        add_group_with_indent(
            bio_card,
            colored_icon(FluentIcon.CLOSE, COLORS['warning']),
            "Hardware Limitation",
            "Biometric authentication in macOS requires Apple T2 Chip, which is not available for Hackintosh systems.",
            create_info_widget("", COLORS['warning']),
            indent_level=0
        )

        for bio_device, bio_props in report['Biometric'].items():
            add_group_with_indent(
                bio_card,
                colored_icon(FluentIcon.FINGERPRINT, COLORS['error']),
                bio_device,
                "Unsupported",
                indent_level=0
            )

        self.contentLayout.addWidget(bio_card)
        return 1

    def _add_sd_card(self, report):
        if 'SD Controller' not in report or not report['SD Controller']: return 0
        
        sd_card = GroupHeaderCardWidget(self.scrollWidget)
        sd_card.setTitle("SD Controller")

        for controller_name, controller_props in report['SD Controller'].items():
            add_group_with_indent(
                sd_card,
                colored_icon(FluentIcon.SAVE, COLORS['primary']),
                controller_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(sd_card, "macOS Compatibility", controller_props.get('Compatibility', (None, None)))

        self.contentLayout.addWidget(sd_card)
        return 1

    def refresh(self):
        self.update_display()