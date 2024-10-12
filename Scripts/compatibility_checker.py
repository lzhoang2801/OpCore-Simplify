from Scripts.datasets import chipset_data
from Scripts.datasets import gpu_data
from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts import codec_layouts
from Scripts import utils
import time

class CompatibilityChecker:
    def __init__(self):
        self.utils = utils.Utils()
        self.hardware_report = None
        self.max_supported_macos_version = os_data.get_latest_darwin_version()
        self.min_supported_macos_version = os_data.get_lowest_darwin_version()

    def show_macos_compatibility(self, device_compatibility):
        if not device_compatibility:
            return "\033[90mUnchecked\033[0m"
        
        if not device_compatibility[0]:
            return "\033[0;31mUnsupported\033[0m"
        
        max_compatibility = self.utils.parse_darwin_version(device_compatibility[0])
        min_compatibility = self.utils.parse_darwin_version(device_compatibility[-1])
        max_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())
        min_version = self.utils.parse_darwin_version(os_data.get_lowest_darwin_version())

        if min_version < min_compatibility and max_compatibility < max_version:
            return "\033[1;32m{} - {}\033[0m".format(
                os_data.get_macos_name_by_darwin(device_compatibility[0]), 
                os_data.get_macos_name_by_darwin(device_compatibility[-1])
            )
        
        if max_compatibility == min_version:
            return "\033[1;36mMaximum support up to {}\033[0m".format(
                os_data.get_macos_name_by_darwin(device_compatibility[-1])
            )
        
        return "\033[1;36mUp to {}\033[0m".format(
            os_data.get_macos_name_by_darwin(device_compatibility[0])
        )
        
    def is_low_end_intel_cpu(self, processor_name):
        return any(cpu_branding in processor_name for cpu_branding in ("Celeron", "Pentium"))

    def check_cpu_compatibility(self):
        if "SSE4" not in self.hardware_report.get("CPU").get("SIMD Features"):
            self.max_supported_macos_version = self.min_supported_macos_version = None
            return
        
        if "SSE4.2" not in self.hardware_report.get("CPU").get("SIMD Features"):
            self.min_supported_macos_version = "18.0.0"
            if "SSE4.1" in self.hardware_report.get("CPU").get("SIMD Features"):
                self.max_supported_macos_version = "21.99.99"

        self.hardware_report["CPU"]["Compatibility"] = (self.max_supported_macos_version, self.min_supported_macos_version)
        print("{}- {}: {}".format(" "*3, self.hardware_report.get("CPU").get("Processor Name"), self.show_macos_compatibility(self.hardware_report["CPU"].get("Compatibility"))))

    def check_gpu_compatibility(self):
        gpu_compatibility = []
        max_supported_gpu_version = min_supported_gpu_version = None

        for gpu_name, gpu_props in self.hardware_report.get("GPU").items():
            gpu_manufacturer = gpu_props.get("Manufacturer")
            gpu_codename = gpu_props.get("Codename")
            device_id = gpu_props.get("Device ID")[5:]

            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()

            if "Intel" in gpu_manufacturer:               
                if device_id.startswith("01") and not device_id[-2] in ("5", "6") and not device_id in ("0102", "0106", "010A"):
                    max_version = "17.99.99"
                elif device_id.startswith("01") and not device_id in ("0152", "0156"):
                    max_version = "20.99.99"
                elif device_id.startswith(("04", "0A", "0C", "0D", "0B", "16")):
                    max_version = "21.99.99"
                elif device_id.startswith(("09", "19", "59")) and device_id != "5917":
                    max_version = "22.99.99"
                elif device_id == "87C0":
                    max_version = "23.99.99"
                elif device_id.startswith(("59", "3E", "87", "9B")):
                    pass
                elif device_id.startswith("8A"):
                    min_version = "19.4.0"
                else:
                    max_version = min_version = None

                if self.is_low_end_intel_cpu(self.hardware_report.get("CPU").get("Processor Name")) or self.utils.contains_any(chipset_data.IntelChipsets, self.hardware_report.get("Motherboard").get("Chipset"), start=116, end=130):
                    max_version = min_version = None
            elif "AMD" in gpu_manufacturer:
                if "Navi 2" in gpu_codename:
                    if not "AVX2" in self.hardware_report.get("CPU").get("SIMD Features"):
                        max_version = "21.99.99"
                    else:
                        if gpu_codename in ("Navi 23", "Navi 22"):
                            min_version = "21.2.0"
                        elif "Navi 21" in gpu_codename:
                            min_version = "20.5.0"
                        else:
                            max_version = min_version = None
                elif "Navi 1" in gpu_codename:
                    min_version = "19.0.0"
                elif "Vega 20" in gpu_codename:
                    min_version = "18.6.0"
                elif gpu_codename in ("Vega 10", "Polaris", "Baffin", "Ellesmere") or device_id == "699F":
                    min_version = "17.0.0"
                elif self.utils.contains_any(gpu_data.AMDCodenames, gpu_codename):
                    max_version = "21.99.99"
                elif device_id in ("15D8", "15DD", "15E7", "1636", "1638", "164C"):
                    min_version = "19.0.0"
                else:
                    max_version = min_version = None
            elif "NVIDIA" in gpu_manufacturer:
                if "Kepler" in gpu_codename:
                    max_version = "20.99.99"
                elif gpu_codename in ("Pascal", "Maxwell", "Fermi", "Tesla"):
                    max_version = "17.99.99"
                    min_version = "17.0.0"
                else:
                    max_version = min_version = None

            if max_version == min_version and max_version == None:
                gpu_props["Compatibility"] = (None, None)
            else:
                gpu_props["Compatibility"] = (max_version, min_version)
                max_supported_gpu_version = max_version if not max_supported_gpu_version else max_version if self.utils.parse_darwin_version(max_version) < self.utils.parse_darwin_version(max_supported_gpu_version) else max_supported_gpu_version
                min_supported_gpu_version = min_version if not min_supported_gpu_version else min_version if self.utils.parse_darwin_version(min_version) > self.utils.parse_darwin_version(min_supported_gpu_version) else min_supported_gpu_version
            print("{}- {}: {}".format(" "*3, gpu_name, self.show_macos_compatibility(gpu_props.get("Compatibility"))))

        if max_supported_gpu_version == min_supported_gpu_version and max_supported_gpu_version == None:
            self.utils.request_input("\n\nYour hardware is not compatible with macOS!")
            self.utils.exit_program()

        self.max_supported_macos_version = max_supported_gpu_version if self.utils.parse_darwin_version(max_supported_gpu_version) < self.utils.parse_darwin_version(self.max_supported_macos_version) else self.max_supported_macos_version
        self.min_supported_macos_version = min_supported_gpu_version if self.utils.parse_darwin_version(min_supported_gpu_version) > self.utils.parse_darwin_version(self.min_supported_macos_version) else self.min_supported_macos_version

        return gpu_compatibility

    def check_sound_compatibility(self):
        supported_audio = {}
        
        for audio_device, audio_props in self.hardware_report.get("Sound", {}).items():
            codec_id = audio_props.get("Device ID")
            if "USB" in audio_props.get("Bus Type") or \
                codec_id.startswith("1002") or \
                codec_id in codec_layouts.data:
                audio_props["Compatibility"] = (os_data.get_latest_darwin_version(), os_data.get_lowest_darwin_version())
                if codec_id in codec_layouts.data:
                    supported_audio = {**{audio_device: audio_props}, **supported_audio}
                else:
                    supported_audio[audio_device] = audio_props
            else:
                audio_props["Compatibility"] = (None, None)
            print("{}- {}: {}".format(" "*3, audio_device, self.show_macos_compatibility(audio_props.get("Compatibility"))))
        
        self.hardware_report["Sound"] = supported_audio

    def check_biometric_compatibility(self):
        for biometric_device, biometric_props in self.hardware_report.get("Biometric", {}).items():
            biometric_props["Compatibility"] = (None, None)
            print("{}- {}: {}".format(" "*3, biometric_device, self.show_macos_compatibility(biometric_props.get("Compatibility"))))

    def check_network_compatibility(self):
        for device_name, device_props in self.hardware_report.get("Network", {}).items():
            bus_type = device_props.get("Bus Type")
            device_id = device_props.get("Device ID")
            is_device_supported = device_id in pci_data.NetworkIDs

            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()

            if bus_type.startswith("PCI"):
                if device_id in ("8086-125B", "8086-125C", "8086-125D", "8086-3102"):
                    min_version = "19.0.0"
                elif device_id in ("10EC-3000", "10EC-8125", "1186-8125"):
                    max_version = "23.99.99"

            if not is_device_supported:
                device_props["Compatibility"] = (None, None)
            else:
                device_props["Compatibility"] = (max_version, min_version)
            print("{}- {}: {}".format(" "*3, device_name, self.show_macos_compatibility(device_props.get("Compatibility"))))

    def check_storage_compatibility(self):
        for controller_name, controller_props in self.hardware_report.get("Storage Controllers", {}).items():
            if "PCI" in controller_props.get("Bus Type"):
                device_id = controller_props.get("Device ID")

                if device_id in pci_data.IntelVMDIDs:
                    self.utils.request_input("\n\nDisable Intel RST VMD in the BIOS before exporting the hardware report and try again with the new report")
                    self.utils.exit_program()
                elif device_id in pci_data.UnsupportedNVMeSSDIDs:
                    controller_props["Compatibility"] = (None, None)
                print("{}- {}: {}".format(" "*3, controller_name if not device_id in pci_data.UnsupportedNVMeSSDIDs else pci_data.UnsupportedNVMeSSDIDs.get(device_id), self.show_macos_compatibility(controller_props.get("Compatibility"))))
        
    def check_sd_controller_compatibility(self):
        for controller_name, controller_props in self.hardware_report.get("SD Controller", {}).items():
            if controller_props.get("Device ID") not in pci_data.RealtekCardReaderIDs:
                controller_props["Compatibility"] = (None, None)
            else:
                controller_props["Compatibility"] = (os_data.get_latest_darwin_version(), os_data.get_lowest_darwin_version())
            print("{}- {}: {}".format(" "*3, controller_name, self.show_macos_compatibility(controller_props.get("Compatibility"))))

    def get_unsupported_devices(self, macos_verison):
        new_hardware_report = {}
        unsupported_device = {}

        for device_type, devices in self.hardware_report.items():
            if device_type in ("Motherboard", "CPU", "USB Controllers", "Input", "Bluetooth", "System Devices"):
                new_hardware_report[device_type] = devices
                continue

            new_hardware_report[device_type] = {}

            for device_name, device_props in devices.items():
                device_compatibility = device_props.get("Compatibility")

                if device_compatibility:
                    if device_compatibility[0] is None or not self.utils.parse_darwin_version(device_compatibility[0]) >= self.utils.parse_darwin_version(macos_verison) >= self.utils.parse_darwin_version(device_compatibility[-1]):
                        unsupported_device["{}: {}".format(device_props.get("Device Type") or device_type, device_name if not device_props.get("Device ID") in pci_data.UnsupportedNVMeSSDIDs else pci_data.UnsupportedNVMeSSDIDs.get(device_props.get("Device ID")))] = device_props
                    else:
                        new_hardware_report[device_type][device_name] = device_props
                else:
                    new_hardware_report[device_type][device_name] = device_props

            if not new_hardware_report[device_type]:
                del new_hardware_report[device_type]

        return new_hardware_report, unsupported_device

    def check_compatibility(self, hardware_report):
        self.hardware_report = hardware_report

        self.utils.head("Compatibility Checker")
        print()

        steps = [
            ('CPU', self.check_cpu_compatibility),
            ('GPU', self.check_gpu_compatibility),
            ('Sound', self.check_sound_compatibility),
            ('Biometric', self.check_biometric_compatibility),
            ('Network', self.check_network_compatibility),
            ('Storage Controllers', self.check_storage_compatibility),
            ('SD Controller', self.check_sd_controller_compatibility)
        ]

        index = 0
        for device_type, function in steps:
            if self.hardware_report.get(device_type):
                index += 1
                print("{}. {}:".format(index, device_type))
                time.sleep(1)
                function()

        print("")
        self.utils.request_input()
        
        return (self.min_supported_macos_version, self.max_supported_macos_version), *self.get_unsupported_devices(self.max_supported_macos_version)