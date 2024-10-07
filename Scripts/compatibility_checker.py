from Scripts.datasets import chipset_data
from Scripts.datasets import cpu_data
from Scripts.datasets import gpu_data
from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts import codec_layouts
from Scripts import utils

class CompatibilityChecker:
    def __init__(self):
        self.utils = utils.Utils()

    def is_low_end_intel_cpu(self, processor_name):
        return any(brand in processor_name for brand in ["Celeron", "Pentium"])

    def check_cpu_compatibility(self, processor_name, simd_features):
        if "SSE4" not in simd_features:
            self.max_supported_macos_version = self.min_supported_macos_version = (-1, -1, -1)
            self.unsupported_devices.append("CPU: {}".format(processor_name))
            return
        
        if "SSE4.2" not in simd_features:
            self.min_supported_macos_version = (18, 0, 0)
            if "SSE4.1" in simd_features:
                self.max_supported_macos_version = (21, 99, 99)

    def check_gpu_compatibility(self, motherboard_chipset, processor_name, simd_features, gpu_info):
        supported_gpus = {}
        is_supported_discrete_gpu = False

        for gpu_name, gpu_props in gpu_info.items():
            gpu_manufacturer = gpu_props.get("Manufacturer")
            gpu_codename = gpu_props.get("Codename")
            device_id = gpu_props.get("Device ID")
            device_type = gpu_props.get("Device Type")
            is_supported_gpu = True

            if "Integrated GPU" in device_type:
                if "Intel" in gpu_manufacturer:
                    if self.utils.contains_any(cpu_data.IntelCPUGenerations, gpu_codename, end=12) and \
                        not self.is_low_end_intel_cpu(processor_name) and \
                        not "2000" in gpu_name and not "2500" in gpu_name:
                        self.min_supported_macos_version = max((17, 0, 0), self.min_supported_macos_version)
                        if "Sandy Bridge" in gpu_codename:
                            self.max_supported_macos_version = max((17, 99, 99), self.max_supported_macos_version if is_supported_discrete_gpu else (-1, -1, -1))
                        elif "Ivy Bridge" in gpu_codename:
                            self.max_supported_macos_version = max((20, 99, 99), self.max_supported_macos_version if is_supported_discrete_gpu else (-1, -1, -1))
                        elif "Haswell" in gpu_codename or "Broadwell" in gpu_codename:
                            self.max_supported_macos_version = max((21, 99, 99), self.max_supported_macos_version if is_supported_discrete_gpu else (-1, -1, -1))
                        elif "Skylake" in gpu_codename or "Kaby Lake" in gpu_codename and not "-r" in gpu_codename.lower():
                            self.max_supported_macos_version = max((22, 99, 99), self.max_supported_macos_version if is_supported_discrete_gpu else (-1, -1, -1))
                        elif "Amber Lake" in gpu_codename or "Whiskey Lake" in gpu_codename:
                            self.min_supported_macos_version = max((17, 0, 0), self.min_supported_macos_version if is_supported_discrete_gpu else (-1, -1, -1))
                            self.max_supported_macos_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())
                        elif not is_supported_discrete_gpu and "Comet Lake" in gpu_codename and self.utils.contains_any(chipset_data.IntelChipsets, motherboard_chipset, start=116, end=130):
                            self.max_supported_macos_version = self.min_supported_macos_version = (-1, -1, -1)
                        elif "Ice Lake" in gpu_codename:
                            self.min_supported_macos_version = max((19, 4, 0), self.min_supported_macos_version)
                            self.max_supported_macos_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())
                        else:
                            self.max_supported_macos_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())
                    else:
                        is_supported_gpu = False
                        if not is_supported_discrete_gpu:
                            self.max_supported_macos_version = self.min_supported_macos_version = (-1, -1, -1)
                elif "AMD" in gpu_manufacturer:
                    is_supported_gpu = gpu_codename in ("Picasso", "Raven Ridge", "Barcelo", "Renoir", "Cezanne", "Lucienne")
                    if is_supported_gpu:
                        self.max_supported_macos_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())
                        self.min_supported_macos_version = max((19, 0, 0), self.min_supported_macos_version)
            elif "Discrete GPU" in device_type:
                if "AMD" in gpu_manufacturer:
                    is_supported_discrete_gpu = True

                    if "Navi 2" in gpu_codename:
                        if not "AVX2" in simd_features:
                            self.max_supported_macos_version = min((21, 99, 99), self.max_supported_macos_version)
                        else:
                            if gpu_codename in ("Navi 23", "Navi 22"):
                                self.min_supported_macos_version = max((21, 2, 0), self.min_supported_macos_version)
                            elif "Navi 21" in gpu_codename:
                                self.min_supported_macos_version = max((20, 5, 0), self.min_supported_macos_version)
                            else:
                                self.max_supported_macos_version = self.min_supported_macos_version = (-1, -1, -1)
                                is_supported_discrete_gpu = is_supported_gpu = False
                    elif "Navi 1" in gpu_codename:
                        self.min_supported_macos_version = max((19, 0, 0), self.min_supported_macos_version)
                    elif "Vega 20" in gpu_codename:
                        self.min_supported_macos_version = max((18, 6, 0), self.min_supported_macos_version)
                    elif "Vega 10" in gpu_codename or "Polaris" in gpu_codename or "Baffin" in gpu_codename or "Ellesmere" in gpu_codename or device_id.endswith("699F"):
                        self.min_supported_macos_version = max((17, 0, 0), self.min_supported_macos_version)
                    elif self.utils.contains_any(gpu_data.AMDCodenames, gpu_codename):
                        self.max_supported_macos_version = (21, 99, 99)
                    else:
                        self.max_supported_macos_version = self.min_supported_macos_version = (-1, -1, -1)
                        is_supported_discrete_gpu = is_supported_gpu = False
                elif "NVIDIA" in gpu_manufacturer:
                    is_supported_discrete_gpu = True

                    if "Kepler" in gpu_codename:
                        self.max_supported_macos_version = (20, 99, 99)
                    elif "Pascal" in gpu_codename or "Maxwell" in gpu_codename or "Fermi" in gpu_codename or "Tesla" in gpu_codename:
                        self.max_supported_macos_version = (17, 99, 99)
                        self.min_supported_macos_version = (17, 0, 0)
                    else:
                        self.max_supported_macos_version = self.min_supported_macos_version = (-1, -1, -1)
                        is_supported_discrete_gpu = is_supported_gpu = False

            if not is_supported_gpu:
                self.unsupported_devices["{}: {}".format(device_type, gpu_name)] = gpu_props
            else:
                supported_gpus[gpu_name] = gpu_props

        return supported_gpus

    def check_audio_compatibility(self, audio_info):
        supported_audio = {}
        
        for audio_device, audio_props in audio_info.items():
            codec_id = audio_props.get("Device ID")
            if "USB" in audio_props.get("Bus Type") or \
                codec_id.startswith("8086") or \
                codec_id.startswith("1002") or \
                codec_id in codec_layouts.data:
                if codec_id in codec_layouts.data:
                    supported_audio = {**{audio_device: audio_props}, **supported_audio}
                else:
                    supported_audio[audio_device] = audio_props
            else:
                self.unsupported_devices["Audio: {}".format(audio_device)] = audio_props
        
        return supported_audio

    def check_biometric_compatibility(self, hardware_report):
        biometric = hardware_report.get("Biometric", {})
        if biometric:
            for biometric_device, biometric_props in biometric.items():
                self.unsupported_devices["Biometric: {}".format(biometric_device)] = biometric_props
            
            del hardware_report["Biometric"]

    def check_network_compatibility(self, network_info):
        supported_network = {}
        
        for device_name, device_props in network_info.items():
            bus_type = device_props.get("Bus Type")
            device_id = device_props.get("Device ID")
            is_device_supported = device_id in pci_data.NetworkIDs

            if bus_type.startswith("PCI"):
                if device_id in ("8086-125B", "8086-125C", "8086-125D", "8086-3102"):
                    self.min_supported_macos_version = (19, 0, 0)

            if not is_device_supported:
                self.unsupported_devices["Network: {}".format(device_name)] = device_props
            else:
                supported_network[device_name] = device_props

        return supported_network

    def check_storage_compatibility(self, storage_controller_info):
        supported_storage = {}

        for controller_name, controller_props in storage_controller_info.items():
            if "PCI" in controller_props.get("Bus Type"):
                device_id = controller_props.get("Device ID")
                if device_id in pci_data.IntelVMDIDs:
                    raise Exception("Disable Intel RST VMD in the BIOS before exporting the AIDA64 report and try again with the new report")
                elif device_id in pci_data.UnsupportedNVMeSSDIDs:
                    self.unsupported_devices["Storage: {}".format(pci_data.UnsupportedNVMeSSDIDs[device_id])] = controller_props
                else:
                    supported_storage[controller_name] = controller_props
        
        return supported_storage

    def check_sd_controller_compatibility(self, hardware_report):
        if not hardware_report.get("SD Controller"):
            return
        
        supported_sd_controller = {}

        for controller_name, controller_props in hardware_report.get("SD Controller", {}).items():
            if controller_props.get("Device ID") not in pci_data.RealtekCardReaderIDs:
                self.unsupported_devices["SD Controller: {}".format(controller_name)] = controller_props
            else:
                supported_sd_controller[controller_name] = controller_props

        if supported_sd_controller:
            hardware_report["SD Controller"] = supported_sd_controller
        else:
            del hardware_report["SD Controller"]

    def check_compatibility(self, hardware_report):
        self.utils.head("Compatibility Checker")
        print("")

        self.max_supported_macos_version = self.utils.parse_darwin_version(os_data.get_latest_darwin_version())
        self.min_supported_macos_version = self.utils.parse_darwin_version(os_data.get_lowest_darwin_version())
        self.unsupported_devices = {}

        self.check_cpu_compatibility(
            hardware_report.get("CPU").get("Processor Name"),
            hardware_report.get("CPU").get("SIMD Features")
        )

        if self.max_supported_macos_version != (-1, -1, -1):
            hardware_report["GPU"] = self.check_gpu_compatibility(
                hardware_report.get("Motherboard").get("Chipset"), 
                hardware_report.get("CPU").get("Processor Name"),
                hardware_report.get("CPU").get("SIMD Features"), 
                hardware_report.get("GPU")
            )
            if hardware_report.get("GPU"):
                hardware_report["Sound"] = self.check_audio_compatibility(hardware_report.get("Sound"))
                self.check_biometric_compatibility(hardware_report)
                hardware_report["Network"] = self.check_network_compatibility(hardware_report.get("Network"))
                hardware_report["Storage Controllers"] = self.check_storage_compatibility(hardware_report.get("Storage Controllers"))
                self.check_sd_controller_compatibility(hardware_report)

        if self.max_supported_macos_version[0] == -1:
            self.u.request_input("Your hardware is not compatible with macOS!")
            self.u.exit_program()

        return (".".join(str(item) for item in self.min_supported_macos_version), ".".join(str(item) for item in self.max_supported_macos_version)), self.unsupported_devices