from Scripts.datasets import gpu_data
from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts.datasets import codec_layouts
from Scripts import utils
from Scripts import settings

class CompatibilityChecker:
    def __init__(self, utils_instance=None, settings_instance=None):
        self.utils = utils_instance if utils_instance else utils.Utils()
        self.settings = settings_instance if settings_instance else settings.Settings()
        self.error_codes = []

    def is_low_end_intel_cpu(self, processor_name):
        return any(cpu_branding in processor_name for cpu_branding in ("Celeron", "Pentium"))

    def check_cpu_compatibility(self):
        max_version = os_data.get_latest_darwin_version()
        min_version = os_data.get_lowest_darwin_version()

        if "SSE4" not in self.hardware_report.get("CPU").get("SIMD Features"):
            max_version = min_version = None
        else:
            if "SSE4.2" not in self.hardware_report.get("CPU").get("SIMD Features"):
                min_version = "18.0.0"
                if "SSE4.1" in self.hardware_report.get("CPU").get("SIMD Features"):
                    max_version = "21.99.99"

        self.hardware_report["CPU"]["Compatibility"] = (max_version, min_version)
        
        if max_version == min_version and max_version == None:
            self.error_codes.append("ERROR_MISSING_SSE4")
            return

        self.max_native_macos_version = max_version
        self.min_native_macos_version = min_version

    def check_gpu_compatibility(self):
        for gpu_name, gpu_props in self.hardware_report["GPU"].items():
            gpu_manufacturer = gpu_props.get("Manufacturer")
            gpu_codename = gpu_props.get("Codename")
            device_id = gpu_props.get("Device ID")[5:]

            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()
            ocl_patched_max_version = "24.99.99"
            ocl_patched_min_version = "20.0.0"

            if "Intel" in gpu_manufacturer:
                if device_id.startswith(("0042", "0046")) and self.hardware_report.get("Motherboard").get("Platform") != "Desktop":
                    max_version = "17.99.99"
                elif device_id.startswith("01") and not device_id[-2] in ("5", "6") and not device_id in ("0102", "0106", "010A"):
                    max_version = "17.99.99"
                elif device_id.startswith("01") and not device_id in ("0152", "0156"):
                    max_version = "20.99.99"
                elif device_id.startswith(("04", "0A", "0C", "0D", "0B", "16")):
                    max_version = "21.99.99"
                elif device_id.startswith(("09", "19", "59", "3E", "87", "9B")) and not device_id in ("3E90", "3E93", "3E99", "3E9C", "3EA1", "3EA4", "9B21", "9BA0", "9BA2", "9BA4", "9BA5", "9BA8", "9BAA", "9BAB", "9BAC"):
                    pass
                elif device_id.startswith("8A"):
                    min_version = "19.4.0"
                else:
                    max_version = min_version = None

                if self.is_low_end_intel_cpu(self.hardware_report.get("CPU").get("Processor Name")):
                    max_version = min_version = None
            elif "AMD" in gpu_manufacturer:
                if "Navi 2" in gpu_codename:
                    if not "AVX2" in self.hardware_report.get("CPU").get("SIMD Features"):
                        max_version = "21.99.99"
                        ocl_patched_max_version = max_version
                    else:
                        if gpu_codename in ("Navi 23", "Navi 22"):
                            min_version = "21.2.0"
                        elif "Navi 21" in gpu_codename:
                            min_version = "20.5.0"
                        else:
                            max_version = min_version = None
                elif "Navi 1" in gpu_codename:
                    if not "AVX2" in self.hardware_report.get("CPU").get("SIMD Features"):
                        max_version = "21.99.99"
                        ocl_patched_min_version = "22.0.0"
                    min_version = "19.0.0"
                elif "Vega 20" in gpu_codename:
                    if not "AVX2" in self.hardware_report.get("CPU").get("SIMD Features"):
                        max_version = "21.99.99"
                        ocl_patched_min_version = "22.0.0"
                    min_version = "18.6.0"
                elif gpu_codename in ("Vega 10", "Polaris 22", "Polaris 20", "Baffin", "Ellesmere") or device_id in ("6995", "699F"):
                    if not "AVX2" in self.hardware_report.get("CPU").get("SIMD Features"):
                        max_version = "21.99.99"
                        ocl_patched_min_version = "22.0.0"
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

            if (max_version == min_version and max_version == None) or \
                ( "Intel" in gpu_manufacturer and device_id.startswith(("01", "04", "0A", "0C", "0D")) and \
                  all(monitor_info.get("Connector Type") == "VGA" and monitor_info.get("Connected GPU", gpu_name) == gpu_name for monitor_name, monitor_info in self.hardware_report.get("Monitor", {}).items())):
                gpu_props["Compatibility"] = (None, None)
            else:
                gpu_props["Compatibility"] = (max_version, min_version)
                if self.utils.parse_darwin_version(max_version) < self.utils.parse_darwin_version(ocl_patched_max_version):
                    gpu_props["OCLP Compatibility"] = (ocl_patched_max_version, ocl_patched_min_version if self.utils.parse_darwin_version(ocl_patched_min_version) > self.utils.parse_darwin_version("{}.{}.{}".format(int(max_version[:2]) + 1, 0, 0)) else "{}.{}.{}".format(int(max_version[:2]) + 1, 0, 0))

        max_supported_gpu_version = min_supported_gpu_version = None

        for gpu_name, gpu_props in self.hardware_report.get("GPU").items():
            if gpu_props.get("Compatibility") != (None, None):
                if all(other_gpu_props.get("Compatibility") == (None, None) for other_gpu_props in self.hardware_report.get("GPU").values() if other_gpu_props != gpu_props):
                    pass
                elif any(monitor_info.get("Connected GPU", gpu_name) != gpu_name for monitor_info in self.hardware_report.get("Monitor", {}).values() if monitor_info.get("Connector Type") == "Internal"):
                    gpu_props["Compatibility"] = (None, None)
                    if gpu_props.get("OCLP Compatibility"):
                        del gpu_props["OCLP Compatibility"]

                max_version, min_version = gpu_props.get("Compatibility")
                max_supported_gpu_version = max_version if not max_supported_gpu_version else max_version if self.utils.parse_darwin_version(max_version) > self.utils.parse_darwin_version(max_supported_gpu_version) else max_supported_gpu_version
                min_supported_gpu_version = min_version if not min_supported_gpu_version else min_version if self.utils.parse_darwin_version(min_version) < self.utils.parse_darwin_version(min_supported_gpu_version) else min_supported_gpu_version

            if gpu_props.get("OCLP Compatibility"):
                self.ocl_patched_macos_version = (gpu_props.get("OCLP Compatibility")[0], self.ocl_patched_macos_version[-1] if self.ocl_patched_macos_version and self.utils.parse_darwin_version(self.ocl_patched_macos_version[-1]) < self.utils.parse_darwin_version(gpu_props.get("OCLP Compatibility")[-1]) else gpu_props.get("OCLP Compatibility")[-1])
        
        if max_supported_gpu_version == min_supported_gpu_version and max_supported_gpu_version == None:
            self.error_codes.append("ERROR_NO_COMPATIBLE_GPU")
            return

        self.max_native_macos_version = max_supported_gpu_version if self.utils.parse_darwin_version(max_supported_gpu_version) < self.utils.parse_darwin_version(self.max_native_macos_version) else self.max_native_macos_version
        self.min_native_macos_version = min_supported_gpu_version if self.utils.parse_darwin_version(min_supported_gpu_version) > self.utils.parse_darwin_version(self.min_native_macos_version) else self.min_native_macos_version

    def check_sound_compatibility(self):
        for _, audio_props in self.hardware_report.get("Sound", {}).items():
            codec_id = audio_props.get("Device ID")

            max_version = min_version = None

            if "USB" in audio_props.get("Bus Type") or \
                codec_id.startswith("1002") or \
                codec_id.startswith("8086") and not codec_id in pci_data.IntelSSTIDs or \
                codec_id in codec_layouts.data:
                max_version, min_version = os_data.get_latest_darwin_version(), os_data.get_lowest_darwin_version()

            audio_props["Compatibility"] = (max_version, min_version)

    def check_biometric_compatibility(self):
        for _, biometric_props in self.hardware_report.get("Biometric", {}).items():
            biometric_props["Compatibility"] = (None, None)

    def check_network_compatibility(self):
        for device_name, device_props in self.hardware_report.get("Network", {}).items():
            bus_type = device_props.get("Bus Type")
            device_id = device_props.get("Device ID")
            
            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()
            ocl_patched_max_version = os_data.get_latest_darwin_version(include_beta=False)
            ocl_patched_min_version = "20.0.0"

            if device_id in pci_data.BroadcomWiFiIDs:
                device_index = pci_data.BroadcomWiFiIDs.index(device_id)

                if device_index == 13 or 17 < device_index < 21:
                    max_version = "22.99.99"
                    ocl_patched_min_version = "23.0.0"
                elif device_index < 12:
                    max_version = "17.99.99"
            elif device_id in pci_data.AtherosWiFiIDs[:8]:
                max_version = "17.99.99"
            elif device_id in pci_data.AtherosWiFiIDs[8:]:
                max_version = "20.99.99"
            elif device_id in pci_data.IntelI22XIDs:
                min_version = "19.0.0"
            elif device_id in pci_data.AquantiaAqtionIDs:
                min_version = "21.0.0"

            if device_id in pci_data.WirelessCardIDs:
                if not device_id in pci_data.IntelWiFiIDs and not device_id in pci_data.AtherosWiFiIDs[8:]:
                    device_props["OCLP Compatibility"] = (ocl_patched_max_version, ocl_patched_min_version)
                    self.ocl_patched_macos_version = (ocl_patched_max_version, self.ocl_patched_macos_version[-1] if self.ocl_patched_macos_version and self.utils.parse_darwin_version(self.ocl_patched_macos_version[-1]) < self.utils.parse_darwin_version(device_props.get("OCLP Compatibility")[-1]) else device_props.get("OCLP Compatibility")[-1])
                device_props["Compatibility"] = (max_version, min_version)
            elif device_id in pci_data.EthernetIDs + pci_data.WirelessUSBIDs:
                device_props["Compatibility"] = (max_version, min_version)

            if bus_type.startswith("PCI") and not device_props.get("Compatibility"):
                device_props["Compatibility"] = (None, None)

    def check_storage_compatibility(self):
        for controller_name, controller_props in self.hardware_report["Storage Controllers"].items():
            if controller_props.get("Bus Type") != "PCI":
                continue

            device_id = controller_props.get("Device ID")
            subsystem_id = controller_props.get("Subsystem ID", "0"*8)

            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()

            if device_id in pci_data.IntelVMDIDs:
                self.error_codes.append("ERROR_INTEL_VMD")
                return

            if next((device for device in pci_data.UnsupportedNVMeSSDIDs if device_id == device[0] and subsystem_id in device[1]), None):
                max_version = min_version = None

            controller_props["Compatibility"] = (max_version, min_version)

        if all(controller_props.get("Compatibility") == (None, None) for controller_name, controller_props in self.hardware_report["Storage Controllers"].items()):
            self.error_codes.append("ERROR_NO_COMPATIBLE_STORAGE")
            return

    def check_bluetooth_compatibility(self):
        for bluetooth_name, bluetooth_props in self.hardware_report.get("Bluetooth", {}).items():
            device_id = bluetooth_props.get("Device ID")
            
            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()

            if device_id in pci_data.AtherosBluetoothIDs:
                max_version = "20.99.99"
            elif device_id in pci_data.BluetoothIDs:
                pass
            else:
                max_version = min_version = None

            bluetooth_props["Compatibility"] = (max_version, min_version)
        
    def check_sd_controller_compatibility(self):
        for controller_name, controller_props in self.hardware_report.get("SD Controller", {}).items():
            device_id = controller_props.get("Device ID")

            max_version = os_data.get_latest_darwin_version()
            min_version = os_data.get_lowest_darwin_version()

            if device_id in pci_data.RealtekCardReaderIDs:
                if device_id in pci_data.RealtekCardReaderIDs[:5]:
                    max_version = "23.99.99"                
            else:
                max_version = min_version = None

            controller_props["Compatibility"] = (max_version, min_version)

    def check_compatibility(self, hardware_report):
        self.hardware_report = hardware_report
        self.ocl_patched_macos_version = None
        self.error_codes = []

        self.utils.log_message("[COMPATIBILITY CHECKER] Starting compatibility check...", level="INFO")

        steps = [
            ('CPU', self.check_cpu_compatibility),
            ('GPU', self.check_gpu_compatibility),
            ('Sound', self.check_sound_compatibility),
            ('Biometric', self.check_biometric_compatibility),
            ('Network', self.check_network_compatibility),
            ('Storage Controllers', self.check_storage_compatibility),
            ('Bluetooth', self.check_bluetooth_compatibility),
            ('SD Controller', self.check_sd_controller_compatibility)
        ]

        for device_type, function in steps:
            if self.hardware_report.get(device_type):
                function()

        if self.error_codes:
            self.utils.log_message("[COMPATIBILITY CHECKER] Compatibility check that found errors: {}".format(", ".join(self.error_codes)), level="INFO")
            return hardware_report, (None, None), None, self.error_codes

        self.utils.log_message("[COMPATIBILITY CHECKER] Compatibility check completed successfully", level="INFO")
        return hardware_report, (self.min_native_macos_version, self.max_native_macos_version), self.ocl_patched_macos_version, self.error_codes