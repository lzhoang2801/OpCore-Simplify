from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts import compatibility_checker
from Scripts import utils

class HardwareCustomizer:
    def __init__(self):
        self.compatibility_checker = compatibility_checker.CompatibilityChecker()
        self.utils = utils.Utils()

    def hardware_customization(self, hardware_report, macos_version):
        self.hardware_report = hardware_report
        self.macos_version = macos_version
        self.customized_hardware = {}
        self.disabled_devices = {}
        self.selected_devices = {}
        needs_oclp = False

        self.utils.head("Hardware Customization")

        for device_type, devices in self.hardware_report.items():
            if not device_type in ("GPU", "Sound", "Biometric", "Network", "Storage Controllers", "Bluetooth", "SD Controller"):
                self.customized_hardware[device_type] = devices
                continue

            self.customized_hardware[device_type] = {}
            
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
            self.utils.head("Device Selection Summary")
            print("")
            print("Selected devices:")
            print("")
            print("Type          Device                                     Device ID")
            print("------------------------------------------------------------------")
            for device_type, device_dict in self.selected_devices.items():
                for device_name, device_props in device_dict.items():
                    device_id = device_props.get("Device ID", "Unknown")
                    print("{:<13} {:<42} {}".format(device_type, device_name[:38], device_id))
            print("")
            print("All other devices of the same type have been disabled.")
            print("")
            self.utils.request_input("Press Enter to continue...")
        
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

        if len(devices) > 1:       
            print("\n*** Multiple {} Devices Detected".format(device_type))
            if device_type == "WiFi" or device_type == "Bluetooth":
                print(f"macOS works best with only one {device_type} device enabled.")
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
                    print("Multiple active GPUs can cause kext conflicts in macOS.")
                
                device_groups = []
                if _apu_index:
                    device_groups.append({_apu_index} | _other_indices)
                if _navi_22_indices:
                    device_groups.append(_navi_22_indices | _other_indices)
                if _navi_indices or _intel_gpu_indices or _other_indices:
                    device_groups.append(_navi_indices | _intel_gpu_indices | _other_indices)
                
            selected_devices = self._select_device(device_type, devices, device_groups)
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

    def _select_device(self, device_type, devices, device_groups=None):
        print("")
        if device_groups:
            print("Please select a {} combination configuration:".format(device_type))
        else:
            print("Please select which {} device you want to use:".format(device_type))
        print("")
        
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
            
            for idx, (group_devices, _, group_compatibility) in enumerate(valid_combinations, start=1):
                print("{}. {}".format(idx, " + ".join(group_devices)))
                if group_compatibility:
                    print("   Compatibility: {}".format(self.compatibility_checker.show_macos_compatibility(group_compatibility)))
                if len(group_devices) == 1:
                    device_props = devices[group_devices[0]]
                    if device_props.get("OCLP Compatibility"):
                        oclp_compatibility = device_props.get("OCLP Compatibility")
                        if self.utils.parse_darwin_version(oclp_compatibility[0]) > self.utils.parse_darwin_version(group_compatibility[0]):
                            print("   OCLP Compatibility: {}".format(self.compatibility_checker.show_macos_compatibility((oclp_compatibility[0], os_data.get_lowest_darwin_version()))))
                print("")
            
            while True:
                choice = self.utils.request_input(f"Select a {device_type} combination (1-{len(valid_combinations)}): ")
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(valid_combinations):
                        selected_devices, _, _ = valid_combinations[choice_num - 1]

                        for device in devices:
                            if device not in selected_devices:
                                self._disable_device(device_type, device, devices[device])

                        return selected_devices
                    else:
                        print("Invalid option. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            for index, device_name in enumerate(devices, start=1):
                device_props = devices[device_name]
                compatibility = device_props.get("Compatibility")
                
                print("{}. {}".format(index, device_name))
                print("   Device ID: {}".format(device_props.get("Device ID", "Unknown")))
                print("   Compatibility: {}".format(self.compatibility_checker.show_macos_compatibility(compatibility)))
                
                if device_props.get("OCLP Compatibility"):
                    oclp_compatibility = device_props.get("OCLP Compatibility")
                    if self.utils.parse_darwin_version(oclp_compatibility[0]) > self.utils.parse_darwin_version(compatibility[0]):
                        print("   OCLP Compatibility: {}".format(self.compatibility_checker.show_macos_compatibility((oclp_compatibility[0], os_data.get_lowest_darwin_version()))))
                print()
            
            while True:
                choice = self.utils.request_input(f"Select a {device_type} device (1-{len(devices)}): ")
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(devices):
                        selected_device = list(devices)[choice_num - 1]
                        
                        for device in devices:
                            if device != selected_device:
                                self._disable_device(device_type, device, devices[device])
                        
                        return [selected_device]
                    else:
                        print("Invalid option. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")

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