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
                device_name = list(device_dict.keys())[0]
                device_props = list(device_dict.values())[0]
                device_id = device_props.get("Device ID", "Unknown")
                
                print("{:<13} {:<42} {}".format(device_type, device_name[:38], device_id))
            print("")
            print("All other devices of the same type have been disabled.")
            print("")
            self.utils.request_input("Press Enter to continue...")
        
        return self.customized_hardware, self.disabled_devices, needs_oclp

    def _handle_device_selection(self, device_type):
        devices = self._get_compatible_devices(device_type)
        if len(devices) > 1:       
            print("\n*** Multiple {} Devices Detected".format(device_type))
            if device_type == "WiFi" or device_type == "Bluetooth":
                print(f"macOS works best with only one {device_type} device enabled.")
            elif device_type == "GPU":
                _has_multiple_compatible_devices = False

                for gpu_name, gpu_props in devices.items():
                    gpu_manufacturer = gpu_props.get("Manufacturer")
                    gpu_codename = gpu_props.get("Codename")

                    if gpu_manufacturer == "AMD":
                        if gpu_props.get("Device Type") == "Integrated GPU":
                            _has_multiple_compatible_devices = True
                        elif gpu_props.get("Device Type") == "Discrete GPU" and gpu_codename == "Navi 22":
                            _has_multiple_compatible_devices = True

                if _has_multiple_compatible_devices:
                    print("Multiple active GPUs can cause kext conflicts in macOS.")
                    print("It's recommended to use only one GPU at a time.")
                else:
                    return
                
            selected_device = self._select_device(device_type, devices)
            if selected_device:
                self.selected_devices[device_type] = {
                    selected_device: devices[selected_device]
                }

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

    def _select_device(self, device_type, devices):
        print("")
        print("Please select which {} device you want to use:".format(device_type))
        print("")
        
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
                    
                    return selected_device
                else:
                    print("Invalid option. Please try again.")
            except:
                print("Please enter a number.")

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
        
        self.disabled_devices["{}: {}".format(device_type, device_name)] = device_props