from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import SubtitleLabel, BodyLabel, ScrollArea, FluentIcon, GroupHeaderCardWidget, CardWidget, StrongBodyLabel

from Scripts.styles import COLORS, SPACING
from Scripts import ui_utils
from Scripts.datasets import os_data, pci_data


class CompatibilityStatusBanner:
    def __init__(self, parent=None, ui_utils_instance=None, layout=None):
        self.parent = parent
        self.ui_utils = ui_utils_instance if ui_utils_instance else ui_utils.UIUtils()
        self.layout = layout
        self.card = None
        self.body_label = None
        self.note_label = None

    def _create_card(self, card_type, icon, title, message, note=""):
        body_text = message
        if note:
            body_text += "<br><br><i style=\"color: {}; font-size: 12px;\">{}</i>".format(COLORS["text_secondary"], note)
        
        if self.card:
            if self.layout:
                self.layout.removeWidget(self.card)
            self.card.setParent(None)
            self.card.deleteLater()
        
        self.card = self.ui_utils.custom_card(
            card_type=card_type,
            icon=icon,
            title=title,
            body=body_text,
            parent=self.parent
        )
        self.card.setVisible(True)
        
        if self.layout:
            self.layout.insertWidget(2, self.card)
        
        return self.card

    def show_error(self, title, message, note=""):
        self._create_card("error", FluentIcon.CLOSE, title, message, note)

    def show_success(self, title, message, note=""):
        self._create_card("success", FluentIcon.ACCEPT, title, message, note)
    
    def setVisible(self, visible):
        if self.card:
            self.card.setVisible(visible)

class CompatibilityPage(ScrollArea):
    def __init__(self, parent, ui_utils_instance=None):
        super().__init__(parent)
        self.setObjectName("compatibilityPage")
        self.controller = parent
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.ui_utils = ui_utils_instance if ui_utils_instance else ui_utils.UIUtils()
        self.contentWidget = None
        self.contentLayout = None
        self.native_support_label = None
        self.ocl_support_label = None
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        
        self._init_ui()

    def _init_ui(self):
        self.expandLayout.setContentsMargins(SPACING["xxlarge"], SPACING["xlarge"], SPACING["xxlarge"], SPACING["xlarge"])
        self.expandLayout.setSpacing(SPACING["large"])

        self.expandLayout.addWidget(self.ui_utils.create_step_indicator(2))

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING["large"])

        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING["tiny"])

        title_label = SubtitleLabel("Hardware Compatibility")
        title_layout.addWidget(title_label)

        subtitle_label = BodyLabel("Review hardware compatibility with macOS")
        subtitle_label.setStyleSheet("color: {};".format(COLORS["text_secondary"]))
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(title_block, 1)

        self.expandLayout.addWidget(header_container)
        
        self.status_banner = CompatibilityStatusBanner(self.scrollWidget, self.ui_utils, self.expandLayout)
        
        self.expandLayout.addSpacing(SPACING["large"])

        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(SPACING["large"])
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
            native_range = min_ver_name if min_ver_name == max_ver_name else "{} to {}".format(min_ver_name, max_ver_name)
            
            message = "Native macOS support: {}".format(native_range)
            
            if self.controller.macos_state.ocl_patched_version:
                 oclp_max_name = os_data.get_macos_name_by_darwin(self.controller.macos_state.ocl_patched_version[0])
                 oclp_min_name = os_data.get_macos_name_by_darwin(self.controller.macos_state.ocl_patched_version[-1])
                 oclp_range = oclp_min_name if oclp_min_name == oclp_max_name else "{} to {}".format(oclp_min_name, oclp_max_name)
                 message += "\nOpenCore Legacy Patcher extended support: {}".format(oclp_range)

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
                return "Up to {}".format(max_name), "#0078D4"
            else:
                return "{} to {}".format(min_name, max_name), "#107C10"

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
        self.placeholder_label = BodyLabel("Load hardware report to see compatibility information")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #605E5C; padding: 40px;")
        self.placeholder_label.setWordWrap(True)
        self.contentLayout.addWidget(self.placeholder_label)
        self.contentLayout.addStretch()

    def _show_no_data_label(self):
        no_data_card = self.ui_utils.custom_card(
            card_type="error",
            icon=FluentIcon.CLOSE,
            title="No compatible hardware information found in the report.",
            body="Please ensure the hardware report contains valid device data.",
            parent=self.scrollWidget
        )
        self.contentLayout.addWidget(no_data_card)

    def _add_compatibility_group(self, card, title, compat):
        compat_text, compat_color = self.format_compatibility(compat)
        self.ui_utils.add_group_with_indent(
            card,
            self.ui_utils.get_compatibility_icon(compat),
            title,
            compat_text,
            self.ui_utils.create_info_widget("", compat_color),
            indent_level=1
        )

    def _add_cpu_card(self, report):
        if "CPU" not in report: return 0
        cpu_info = report["CPU"]
        if not isinstance(cpu_info, dict): return 0
        
        cpu_card = GroupHeaderCardWidget(self.scrollWidget)
        cpu_card.setTitle("CPU")
        
        name = cpu_info.get("Processor Name", "Unknown")
        self.ui_utils.add_group_with_indent(
            cpu_card,
            self.ui_utils.colored_icon(FluentIcon.TAG, COLORS["primary"]),
            "Processor",
            name,
            indent_level=0
        )

        self._add_compatibility_group(cpu_card, "macOS Compatibility", cpu_info.get("Compatibility", (None, None)))

        details = []
        if cpu_info.get("Codename"):
            details.append("Codename: {}".format(cpu_info.get("Codename")))
        if cpu_info.get("Core Count"):
            details.append("Cores: {}".format(cpu_info.get("Core Count")))

        if details:
            self.ui_utils.add_group_with_indent(
                cpu_card,
                self.ui_utils.colored_icon(FluentIcon.INFO, COLORS["info"]),
                "Details",
                " • ".join(details),
                indent_level=1
            )

        self.contentLayout.addWidget(cpu_card)
        return 1

    def _add_gpu_card(self, report):
        if "GPU" not in report or not report["GPU"]: return 0
        
        gpu_card = GroupHeaderCardWidget(self.scrollWidget)
        gpu_card.setTitle("Graphics")

        for idx, (gpu_name, gpu_info) in enumerate(report["GPU"].items()):
            device_type = gpu_info.get("Device Type", "Unknown")
            self.ui_utils.add_group_with_indent(
                gpu_card,
                self.ui_utils.colored_icon(FluentIcon.PHOTO, COLORS["primary"]),
                gpu_name,
                "Type: {}".format(device_type),
                indent_level=0
            )

            self._add_compatibility_group(gpu_card, "macOS Compatibility", gpu_info.get("Compatibility", (None, None)))

            if "OCLP Compatibility" in gpu_info:
                oclp_compat = gpu_info.get("OCLP Compatibility")
                oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                self.ui_utils.add_group_with_indent(
                    gpu_card,
                    self.ui_utils.colored_icon(FluentIcon.IOT, COLORS["primary"]),
                    "OCLP Compatibility",
                    oclp_text,
                    self.ui_utils.create_info_widget("Extended support with OpenCore Legacy Patcher", COLORS["text_secondary"]),
                    indent_level=1
                )

            if "Monitor" in report:
                self._add_monitor_info(gpu_card, gpu_name, gpu_info, report["Monitor"])

        self.contentLayout.addWidget(gpu_card)
        return 1

    def _add_monitor_info(self, gpu_card, gpu_name, gpu_info, monitors):
        connected_monitors = []
        for monitor_name, monitor_info in monitors.items():
            if monitor_info.get("Connected GPU") == gpu_name:
                connector = monitor_info.get("Connector Type", "Unknown")
                monitor_str = "{} ({})".format(monitor_name, connector)
                
                manufacturer = gpu_info.get("Manufacturer", "")
                raw_device_id = gpu_info.get("Device ID", "")
                device_id = raw_device_id[5:] if len(raw_device_id) > 5 else raw_device_id

                if "Intel" in manufacturer and device_id.startswith(("01", "04", "0A", "0C", "0D")):
                    if connector == "VGA":
                        monitor_str += " (Unsupported)"
                
                connected_monitors.append(monitor_str)

        if connected_monitors:
            self.ui_utils.add_group_with_indent(
                gpu_card,
                self.ui_utils.colored_icon(FluentIcon.VIEW, COLORS["info"]),
                "Connected Displays",
                ", ".join(connected_monitors),
                indent_level=1
            )

    def _add_sound_card(self, report):
        if "Sound" not in report or not report["Sound"]: return 0
        
        sound_card = GroupHeaderCardWidget(self.scrollWidget)
        sound_card.setTitle("Audio")

        for audio_device, audio_props in report["Sound"].items():
            self.ui_utils.add_group_with_indent(
                sound_card,
                self.ui_utils.colored_icon(FluentIcon.MUSIC, COLORS["primary"]),
                audio_device,
                "",
                indent_level=0
            )

            self._add_compatibility_group(sound_card, "macOS Compatibility", audio_props.get("Compatibility", (None, None)))

            endpoints = audio_props.get("Audio Endpoints", [])
            if endpoints:
                self.ui_utils.add_group_with_indent(
                    sound_card,
                    self.ui_utils.colored_icon(FluentIcon.HEADPHONE, COLORS["info"]),
                    "Audio Endpoints",
                    ", ".join(endpoints),
                    indent_level=1
                )

        self.contentLayout.addWidget(sound_card)
        return 1

    def _add_network_card(self, report):
        if "Network" not in report or not report["Network"]: return 0
        
        network_card = GroupHeaderCardWidget(self.scrollWidget)
        network_card.setTitle("Network")

        for device_name, device_props in report["Network"].items():
            self.ui_utils.add_group_with_indent(
                network_card,
                self.ui_utils.colored_icon(FluentIcon.WIFI, COLORS["primary"]),
                device_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(network_card, "macOS Compatibility", device_props.get("Compatibility", (None, None)))

            if "OCLP Compatibility" in device_props:
                oclp_compat = device_props.get("OCLP Compatibility")
                oclp_text, oclp_color = self.format_compatibility(oclp_compat)
                self.ui_utils.add_group_with_indent(
                    network_card,
                    self.ui_utils.colored_icon(FluentIcon.IOT, COLORS["primary"]),
                    "OCLP Compatibility",
                    oclp_text,
                    self.ui_utils.create_info_widget("Extended support with OpenCore Legacy Patcher", COLORS["text_secondary"]),
                    indent_level=1
                )

            self._add_continuity_info(network_card, device_props)

        self.contentLayout.addWidget(network_card)
        return 1

    def _add_continuity_info(self, network_card, device_props):
        device_id = device_props.get("Device ID", "")
        if not device_id: return
        
        continuity_info = ""
        continuity_color = COLORS["text_secondary"]

        if device_id in pci_data.BroadcomWiFiIDs:
            continuity_info = "Full support (AirDrop, Handoff, Universal Clipboard, Instant Hotspot, etc.)"
            continuity_color = COLORS["success"]
        elif device_id in pci_data.IntelWiFiIDs:
            continuity_info = "Partial (Handoff and Universal Clipboard with AirportItlwm) - AirDrop, Universal Clipboard, Instant Hotspot,... not available"
            continuity_color = COLORS["warning"]
        elif device_id in pci_data.AtherosWiFiIDs:
            continuity_info = "Limited support (No Continuity features available). Atheros cards are not recommended for macOS."
            continuity_color = COLORS["error"]

        if continuity_info:
            self.ui_utils.add_group_with_indent(
                network_card,
                self.ui_utils.colored_icon(FluentIcon.SYNC, continuity_color),
                "Continuity Features",
                continuity_info,
                self.ui_utils.create_info_widget("", continuity_color),
                indent_level=1
            )

    def _add_storage_card(self, report):
        if "Storage Controllers" not in report or not report["Storage Controllers"]: return 0
        
        storage_card = GroupHeaderCardWidget(self.scrollWidget)
        storage_card.setTitle("Storage")

        for controller_name, controller_props in report["Storage Controllers"].items():
            self.ui_utils.add_group_with_indent(
                storage_card,
                self.ui_utils.colored_icon(FluentIcon.FOLDER, COLORS["primary"]),
                controller_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(storage_card, "macOS Compatibility", controller_props.get("Compatibility", (None, None)))

            disk_drives = controller_props.get("Disk Drives", [])
            if disk_drives:
                self.ui_utils.add_group_with_indent(
                    storage_card,
                    self.ui_utils.colored_icon(FluentIcon.FOLDER, COLORS["info"]),
                    "Disk Drives",
                    ", ".join(disk_drives),
                    indent_level=1
                )

        self.contentLayout.addWidget(storage_card)
        return 1

    def _add_bluetooth_card(self, report):
        if "Bluetooth" not in report or not report["Bluetooth"]: return 0
        
        bluetooth_card = GroupHeaderCardWidget(self.scrollWidget)
        bluetooth_card.setTitle("Bluetooth")

        for bluetooth_name, bluetooth_props in report["Bluetooth"].items():
            self.ui_utils.add_group_with_indent(
                bluetooth_card,
                self.ui_utils.colored_icon(FluentIcon.BLUETOOTH, COLORS["primary"]),
                bluetooth_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(bluetooth_card, "macOS Compatibility", bluetooth_props.get("Compatibility", (None, None)))

        self.contentLayout.addWidget(bluetooth_card)
        return 1

    def _add_biometric_card(self, report):
        if "Biometric" not in report or not report["Biometric"]: return 0
        bio_card = GroupHeaderCardWidget(self.scrollWidget)
        bio_card.setTitle("Biometric")

        self.ui_utils.add_group_with_indent(
            bio_card,
            self.ui_utils.colored_icon(FluentIcon.CLOSE, COLORS["warning"]),
            "Hardware Limitation",
            "Biometric authentication in macOS requires Apple T2 Chip, which is not available for Hackintosh systems.",
            self.ui_utils.create_info_widget("", COLORS["warning"]),
            indent_level=0
        )

        for bio_device, bio_props in report["Biometric"].items():
            self.ui_utils.add_group_with_indent(
                bio_card,
                self.ui_utils.colored_icon(FluentIcon.FINGERPRINT, COLORS["error"]),
                bio_device,
                "Unsupported",
                indent_level=0
            )

        self.contentLayout.addWidget(bio_card)
        return 1

    def _add_sd_card(self, report):
        if "SD Controller" not in report or not report["SD Controller"]: return 0
        
        sd_card = GroupHeaderCardWidget(self.scrollWidget)
        sd_card.setTitle("SD Controller")

        for controller_name, controller_props in report["SD Controller"].items():
            self.ui_utils.add_group_with_indent(
                sd_card,
                self.ui_utils.colored_icon(FluentIcon.SAVE, COLORS["primary"]),
                controller_name,
                "",
                indent_level=0
            )

            self._add_compatibility_group(sd_card, "macOS Compatibility", controller_props.get("Compatibility", (None, None)))

        self.contentLayout.addWidget(sd_card)
        return 1

    def refresh(self):
        self.update_display()