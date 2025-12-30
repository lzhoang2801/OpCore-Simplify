from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts.custom_dialogs import show_confirmation, show_info, show_options_dialog
from Scripts import utils

class HardwareCustomizer:
    def __init__(self, utils_instance=None):
        self.utils = utils_instance if utils_instance else utils.Utils()

    def show_macos_compatibility(self, device_compatibility):
        if not device_compatibility:
            return "<span style='color:gray'>Unchecked</span>"
        
        if not device_compatibility[0]:
            return "<span style='color:red'>Unsupported</span>"
        
        max_compatibility = self.utils.parse_darwin_version(device_compatibility[0])[0]
        min_compatibility = self.utils.parse_darwin_version(device_compatibility[-1])[0]
        max_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())[0]
        min_version = self.utils.parse_darwin_version(os_data.get_lowest_darwin_version())[0]

        if max_compatibility == min_version:
            return "<span style='color:blue'>Maximum support up to {}</span>".format(
                os_data.get_macos_name_by_darwin(device_compatibility[-1])
            )

        if min_version < min_compatibility or max_compatibility < max_version:
            return "<span style='color:green'>{} to {}</span>".format(
                os_data.get_macos_name_by_darwin(device_compatibility[-1]), 
                os_data.get_macos_name_by_darwin(device_compatibility[0])
            )
        
        return "<span style='color:blue'>Up to {}</span>".format(
            os_data.get_macos_name_by_darwin(device_compatibility[0])
        )

    def hardware_customization(self, hardware_report, macos_version):
        self.hardware_report = hardware_report
        self.macos_version = macos_version
        self.customized_hardware = {}
        self.disabled_devices = {}
        self.selected_devices = {}
        needs_oclp = False

        self.utils.log_message("[HARDWARE CUSTOMIZATION] Starting hardware customization", level="INFO")

        for device_type, devices in self.hardware_report.items():
            if not device_type in ("BIOS", "GPU", "Sound", "Biometric", "Network", "Storage Controllers", "Bluetooth", "SD Controller"):
                self.customized_hardware[device_type] = devices
                continue

            self.customized_hardware[device_type] = {}

            if device_type == "BIOS":
                self.customized_hardware[device_type] = devices.copy()

                if devices.get("Firmware Type") != "UEFI":
                    content = (
                        "Would you like to build the EFI for UEFI?<br>"
                        "If yes, please make sure to update your BIOS and enable UEFI Boot Mode in your BIOS settings.<br>"
                        "You can still proceed with Legacy if you prefer."
                    )
                    if show_confirmation("BIOS Firmware Type is not UEFI", content):
                        self.utils.log_message("[HARDWARE CUSTOMIZATION] BIOS Firmware Type is not UEFI, building EFI for UEFI", level="INFO")
                        self.customized_hardware[device_type]["Firmware Type"] = "UEFI"
                    else:
                        self.utils.log_message("[HARDWARE CUSTOMIZATION] BIOS Firmware Type is not UEFI, building EFI for Legacy", level="INFO")
                        self.customized_hardware[device_type]["Firmware Type"] = "Legacy"

                continue
            
            for device_name in devices:
                device_props = devices[device_name].copy()
                if device_props.get("OCLP Compatibility") and self.utils.parse_darwin_version(device_props.get("OCLP Compatibility")[0]) >= self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version(device_props.get("OCLP Compatibility")[-1]):
                    self.customized_hardware[device_type][device_name] = device_props
                    needs_oclp = True
                    continue

                device_compatibility = device_props.get("Compatibility", (os_data.get_latest_darwin_version(), os_data.get_lowest_darwin_version()))

                try:
                    if self.utils.parse_darwin_version(device_compatibility[0]) >= self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version(device_compatibility[-1]):
                        self.customized_hardware[device_type][device_name] = device_props
                except:
                    self.disabled_devices["{}: {}{}".format(device_props["Device Type"] if not "Unknown" in device_props.get("Device Type", "Unknown") else device_type, device_name, "" if not device_props.get("Audio Endpoints") else " ({})".format(", ".join(device_props.get("Audio Endpoints"))))] = device_props

                if self.customized_hardware[device_type].get(device_name) and self.customized_hardware[device_type][device_name].get("OCLP Compatibility"):
                    del self.customized_hardware[device_type][device_name]["OCLP Compatibility"]

            if not self.customized_hardware[device_type]:
                del self.customized_hardware[device_type]
            else:
                if device_type in ("GPU", "Network", "Bluetooth"):
                    self._handle_device_selection(device_type if device_type != "Network" else "WiFi")
        
        if self.selected_devices:
            content = "The following devices have been selected for your configuration:<br>"
            content += "<table width='100%' cellpadding='4'>"
            content += "<tr>"
            content += "<td><b>Category</b></td>"
            content += "<td><b>Device Name</b></td>"
            content += "<td><b>Device ID</b></td>"
            content += "</tr>"

            for device_type, device_dict in self.selected_devices.items():
                for device_name, device_props in device_dict.items():
                    device_id = device_props.get("Device ID", "Unknown")
                    content += "<tr>"
                    content += "<td>{}</td>".format(device_type)
                    content += "<td>{}</td>".format(device_name)
                    content += "<td>{}</td>".format(device_id)
                    content += "</tr>"
            
            content += "</table>"
            content += "<p><i>Note: Unselected devices in these categories have been disabled.</i></p>"
            show_info("Hardware Configuration Summary", content)

        return self.customized_hardware, self.disabled_devices, needs_oclp

    def _get_device_combinations(self, device_indices):
        devices = sorted(list(device_indices))
        n = len(devices)
        all_combinations = []

        if n == 0:
            return []
        
        for i in range(1, 1 << n):
            current_combination = []
            for j in range(n):
                if (i >> j) & 1:
                    current_combination.append(devices[j])
            
            if 1 <= len(current_combination) <= n:
                all_combinations.append(current_combination)

        all_combinations.sort(key=lambda combo: (len(combo), combo))

        return all_combinations

    def _handle_device_selection(self, device_type):
        devices = self._get_compatible_devices(device_type)
        device_groups = None

        title = "Multiple {} Devices Detected".format(device_type)
        content = []

        if len(devices) > 1:       
            if device_type == "WiFi" or device_type == "Bluetooth":
                content.append("macOS works best with only one {} device enabled.<br>".format(device_type))
            elif device_type == "GPU":
                _apu_index = None
                _navi_22_indices = set()
                _navi_indices = set()
                _intel_gpu_indices = set()
                _other_indices = set()

                for index, (gpu_name, gpu_props) in enumerate(devices.items()):
                    gpu_manufacturer = gpu_props.get("Manufacturer")
                    gpu_codename = gpu_props.get("Codename")
                    gpu_type = gpu_props.get("Device Type")

                    if gpu_manufacturer == "AMD":
                        if gpu_type == "Integrated GPU":
                            _apu_index = index
                            continue
                        elif gpu_type == "Discrete GPU":
                            if gpu_codename.startswith("Navi"):
                                if gpu_codename == "Navi 22":
                                    _navi_22_indices.add(index)
                                else:
                                    _navi_indices.add(index)
                                continue
                    elif gpu_manufacturer == "Intel":
                        _intel_gpu_indices.add(index)
                        continue

                    _other_indices.add(index)

                if _apu_index or _navi_22_indices:
                    content.append("Multiple active GPUs can cause kext conflicts in macOS.")
                
                device_groups = []
                if _apu_index:
                    device_groups.append({_apu_index} | _other_indices)
                if _navi_22_indices:
                    device_groups.append(_navi_22_indices | _other_indices)
                if _navi_indices or _intel_gpu_indices or _other_indices:
                    device_groups.append(_navi_indices | _intel_gpu_indices | _other_indices)
                
            selected_devices = self._select_device(device_type, devices, device_groups, title, content)
            if selected_devices:
                for selected_device in selected_devices:
                    if not device_type in self.selected_devices:
                        self.selected_devices[device_type] = {}

                    self.selected_devices[device_type][selected_device] = devices[selected_device]

    def _get_compatible_devices(self, device_type):
        compatible_devices = {}
        
        if device_type == "WiFi":
            hardware_category = "Network"
        else:
            hardware_category = device_type
        
        for device_name, device_props in self.customized_hardware.get(hardware_category, {}).items():
            if device_type == "WiFi":
                device_id = device_props.get("Device ID")

                if device_id not in pci_data.WirelessCardIDs:
                    continue

            compatible_devices[device_name] = device_props
        
        return compatible_devices

    def _select_device(self, device_type, devices, device_groups=None, title=None, content=None):
        self.utils.log_message("[HARDWARE CUSTOMIZATION] Starting device selection for {}".format(device_type), level="INFO")
        if device_groups:
            content.append("Please select a {} combination configuration:".format(device_type))
        else:
            content.append("Please select which {} device you want to use:".format(device_type))

        options = []

        if device_groups:
            valid_combinations = []

            for group in device_groups:
                device_combinations = self._get_device_combinations(group)
                for device_combination in device_combinations:
                    group_devices = []
                    group_compatibility = None
                    group_indices = set()
                    has_oclp_required = False
                    
                    for index in device_combination:
                        device_name = list(devices.keys())[index]
                        device_props = devices[device_name]
                        group_devices.append(device_name)
                        group_indices.add(index)
                        compatibility = device_props.get("Compatibility")
                        if compatibility:
                            if group_compatibility is None:
                                group_compatibility = compatibility
                            else:
                                if self.utils.parse_darwin_version(compatibility[0]) < self.utils.parse_darwin_version(group_compatibility[0]):
                                    group_compatibility = (compatibility[0], group_compatibility[1])
                                if self.utils.parse_darwin_version(compatibility[1]) > self.utils.parse_darwin_version(group_compatibility[1]):
                                    group_compatibility = (group_compatibility[0], compatibility[1])
                        
                        if device_props.get("OCLP Compatibility"):
                            has_oclp_required = True

                    if has_oclp_required and len(device_combination) > 1:
                        continue

                    if group_devices and (group_devices, group_indices, group_compatibility) not in valid_combinations:
                        valid_combinations.append((group_devices, group_indices, group_compatibility))

            valid_combinations.sort(key=lambda x: (len(x[0]), x[2][0]))
            
            for group_devices, group_indices, group_compatibility in valid_combinations:
                option = "<b>{}</b>".format(" + ".join(group_devices))
                if group_compatibility:
                    option += "<br>Compatibility: {}".format(self.show_macos_compatibility(group_compatibility))
                if len(group_devices) == 1:
                    device_props = devices[group_devices[0]]
                    if device_props.get("OCLP Compatibility"):
                        option += "<br>OCLP Compatibility: {}".format(self.show_macos_compatibility((device_props.get("OCLP Compatibility")[0], os_data.get_lowest_darwin_version())))
                options.append(option)
        else:
            for device_name, device_props in devices.items():
                compatibility = device_props.get("Compatibility")
                
                option = "<b>{}</b>".format(device_name)
                option += "<br>Device ID: {}".format(device_props.get("Device ID", "Unknown"))
                option += "<br>Compatibility: {}".format(self.show_macos_compatibility(compatibility))
                
                if device_props.get("OCLP Compatibility"):
                    oclp_compatibility = device_props.get("OCLP Compatibility")
                    if self.utils.parse_darwin_version(oclp_compatibility[0]) > self.utils.parse_darwin_version(compatibility[0]):
                        option += "<br>OCLP Compatibility: {}".format(self.show_macos_compatibility((oclp_compatibility[0], os_data.get_lowest_darwin_version())))
                options.append(option)

        self.utils.log_message("[HARDWARE CUSTOMIZATION] Options: {}".format(", ".join(option.split("<br>")[0].replace("<b>", "").replace("</b>", "").strip() for option in options)), level="INFO")
            
        while True:
            choice_num = show_options_dialog(title, "<br>".join(content), options, default_index=len(options) - 1)

            if choice_num is None:
                continue
            
            if device_groups:
                selected_devices, _, _ = valid_combinations[choice_num]
            else:
                selected_devices = [list(devices)[choice_num]]

            for device in devices:
                if device not in selected_devices:
                    self._disable_device(device_type, device, devices[device])

            self.utils.log_message("[HARDWARE CUSTOMIZATION] Selected devices: {}".format(", ".join(selected_devices)), level="INFO")
            return selected_devices

    def _disable_device(self, device_type, device_name, device_props):
        if device_type == "WiFi":
            device_id = device_props.get("Device ID")
            if not device_id or device_id not in pci_data.WirelessCardIDs:
                return

            hardware_category = "Network"
        else:
            hardware_category = device_type

        if (hardware_category in self.customized_hardware and device_name in self.customized_hardware[hardware_category]):
            del self.customized_hardware[hardware_category][device_name]
            
            if not self.customized_hardware[hardware_category]:
                del self.customized_hardware[hardware_category]
        
        self.disabled_devices["{}: {}".format(hardware_category, device_name)] = device_props