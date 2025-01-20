from Scripts.datasets import chipset_data
from Scripts.datasets import cpu_data
from Scripts.datasets import mac_model_data
from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts.datasets import codec_layouts
from Scripts import gathering_files
from Scripts import smbios
from Scripts import utils
import random

class ConfigProdigy:
    def __init__(self):
        self.g = gathering_files.gatheringFiles()
        self.smbios = smbios.SMBIOS()
        self.utils = utils.Utils()
        self.cpuids = {
            "Ivy Bridge": "A9060300",
            "Haswell": "C3060300",
            "Broadwell": "D4060300",
            "Coffee Lake": "EB060800",
            "Comet Lake": "55060A00"
        }

    def mmio_whitelist(self, motherboard_chipset):
        booter_mmiowhitelist = []

        if "Ice Lake" in motherboard_chipset:
            booter_mmiowhitelist.append({
                "Address": 4284481536,
                "Comment": "MMIO 0xFF600000",
                "Enabled": True
            })
        elif "B650" in motherboard_chipset or "X670" in motherboard_chipset:
            booter_mmiowhitelist.append({
                "Address": 4244635648,
                "Comment": "MMIO 0xFD000000",
                "Enabled": True
            })
        
        return booter_mmiowhitelist
    
    def add_booter_patch(self, smbios_model, macos_version):
        booter_patch = []

        mac_device = mac_model_data.get_mac_device_by_name(smbios_model)
        if not self.utils.parse_darwin_version(mac_device.initial_support) <= self.utils.parse_darwin_version(macos_version) <= self.utils.parse_darwin_version(mac_device.last_supported_version):
            booter_patch.append({
                "Arch": "x86_64",
                "Comment": "Skip Board ID check",
                "Count": 0,
                "Enabled": True,
                "Find": self.utils.hex_to_bytes("0050006C006100740066006F0072006D0053007500700070006F00720074002E0070006C006900730074"),
                "Identifier": "Apple",
                "Limit": 0,
                "Mask": self.utils.hex_to_bytes(""),
                "Replace": self.utils.hex_to_bytes("002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E002E"),
                "ReplaceMask": self.utils.hex_to_bytes(""),
                "Skip": 0
            })

        return booter_patch

    def is_low_end_intel_cpu(self, processor_name):
        return any(cpu_branding in processor_name for cpu_branding in ("Celeron", "Pentium"))
    
    def igpu_properties(self, platform, integrated_gpu, monitor, macos_version):
        igpu_properties = {}

        device_id = integrated_gpu[1].get("Device ID")[5:]

        if device_id.startswith("01") and not device_id[-2] in ("5", "6"):
            native_supported_ids = ("0106", "1106", "1601", "0116", "0126", "0102")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "26010000"
            igpu_properties["AAPL,snb-platform-id"] = "10000300"
            if platform == "Desktop":
                if not any(monitor_info.get("Connected GPU") == integrated_gpu[0] for monitor_name, monitor_info in monitor.items() if monitor_info.get("Connector Type") != "VGA"):
                    igpu_properties["AAPL,snb-platform-id"] = "00000500"
                    igpu_properties["device-id"] = "02010000"
            elif platform == "Laptop":
                if any(tuple(map(int, "1600x900".split("x"))) <= tuple(map(int, monitor_info.get("Resolution").split("x"))) for monitor_name, monitor_info in monitor.items()):
                    igpu_properties["AAPL00,DualLink"] = "01000000"
                igpu_properties["AAPL,snb-platform-id"] = "00000100"
        elif device_id.startswith("01"):
            native_supported_ids = ("0152", "0156", "0162", "0166")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "62010000"
            if platform == "Desktop":
                if not any(monitor_info.get("Connected GPU") == integrated_gpu[0] for monitor_name, monitor_info in monitor.items() if monitor_info.get("Connector Type") != "VGA"):
                    igpu_properties["AAPL,ig-platform-id"] = "07006201"
                igpu_properties["AAPL,ig-platform-id"] = "0A006601"
            elif platform == "NUC":
                igpu_properties["AAPL,ig-platform-id"] = "0B006601"
            elif platform == "Laptop":
                igpu_properties["AAPL,ig-platform-id"] = "03006601"
                if any(tuple(map(int, "1600x900".split("x"))) <= tuple(map(int, monitor_info.get("Resolution").split("x"))) for monitor_name, monitor_info in monitor.items()):
                    igpu_properties["AAPL,ig-platform-id"] = "04006601"
                    igpu_properties["framebuffer-memorycount"] = "02000000"
                    igpu_properties["framebuffer-pipecount"] = "02000000"
                    igpu_properties["framebuffer-portcount"] = "04000000"
                    igpu_properties["framebuffer-stolenmem"] = "00000004"
                    igpu_properties["framebuffer-con1-enable"] = "01000000"
                    igpu_properties["framebuffer-con1-alldata"] = "020500000004000007040000030400000004000081000000040600000004000081000000"
        elif device_id.startswith(("04", "0A", "0C", "0D")):
            native_supported_ids = ("0D26", "0A26", "0A2E", "0D22", "0412")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "12040000"
            if platform == "Desktop":
                if not any(monitor_info.get("Connected GPU") == integrated_gpu[0] for monitor_name, monitor_info in monitor.items() if monitor_info.get("Connector Type") != "VGA"):
                    igpu_properties["AAPL,ig-platform-id"] = "04001204"
                    return igpu_properties
                igpu_properties["AAPL,ig-platform-id"] = "0300220D"
                igpu_properties["framebuffer-stolenmem"] = "00003001"
                igpu_properties["framebuffer-fbmem"] = "00009000"
            elif platform == "NUC":
                igpu_properties["AAPL,ig-platform-id"] = "0300220D"
                igpu_properties["framebuffer-cursormem"] = "00009000"
            elif platform == "Laptop":
                igpu_properties["AAPL,ig-platform-id"] = "0600260A"
                if device_id.startswith(("0A2", "0D2")):
                    igpu_properties["AAPL,ig-platform-id"] = "0500260A"
                igpu_properties["framebuffer-cursormem"] = "00009000"
        elif device_id.startswith(("0B", "16")):
            native_supported_ids = ("0BD1", "0BD2", "0BD3", "1606", "160E", "1616", "161E", "1626", "1622", "1612", "162B")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "26160000"
            if platform == "Desktop":
                igpu_properties["AAPL,ig-platform-id"] = "07002216"
            elif platform == "NUC":
                igpu_properties["AAPL,ig-platform-id"] = "02001616"
            elif platform == "Laptop":
                igpu_properties["AAPL,ig-platform-id"] = "06002616"
            igpu_properties["framebuffer-stolenmem"] = "00003001"
            igpu_properties["framebuffer-fbmem"] = "00009000"
        elif device_id.startswith(("09", "19")) and self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("22.0.0"):
            native_supported_ids = ("1916", "191E", "1926", "1927", "1912", "1932", "1902", "1917", "193B", "191B")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "1B190000"
            if device_id in ("1906", "190B"):
                igpu_properties["device-id"] = "02190000"
            if device_id.startswith("191E"):
                igpu_properties["AAPL,ig-platform-id"] = "00001E19"
            if platform == "Desktop":
                if not any(monitor_info.get("Connected GPU") == integrated_gpu[0] for monitor_name, monitor_info in monitor.items()):
                    igpu_properties["AAPL,ig-platform-id"] = "01001219"
                    return igpu_properties
                igpu_properties["AAPL,ig-platform-id"] = "00001219"
            elif platform == "NUC":
                igpu_properties["AAPL,ig-platform-id"] = "02001619"
                if device_id.startswith(("1926", "1927")):
                    igpu_properties["AAPL,ig-platform-id"] = "02002619"
                elif device_id.startswith(("1932", "193B", "193A", "193D")):
                    igpu_properties["AAPL,ig-platform-id"] = "05003B19"
            elif platform == "Laptop":
                igpu_properties["AAPL,ig-platform-id"] = "00001619"
                if device_id.startswith(("1902", "1906", "190B")):
                    igpu_properties["AAPL,ig-platform-id"] = "00001B19"
            igpu_properties["framebuffer-stolenmem"] = "00003001"
            igpu_properties["framebuffer-fbmem"] = "00009000"
        elif device_id.startswith(("09", "19", "59", "87C0")):
            native_supported_ids = ("5912", "5916", "591B", "591C", "591E", "5926", "5927", "5923", "87C0")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "16590000"
            if device_id.startswith(("5917", "5916", "5921")):
                igpu_properties["AAPL,ig-platform-id"] = "00001659"
            if platform == "Desktop":
                if not any(monitor_info.get("Connected GPU") == integrated_gpu[0] for monitor_name, monitor_info in monitor.items()):
                    igpu_properties["AAPL,ig-platform-id"] = "03001259"
                    return igpu_properties
                igpu_properties["AAPL,ig-platform-id"] = "00001259"
            elif platform == "NUC":
                igpu_properties["AAPL,ig-platform-id"] = "00001E59"
                if device_id.startswith(("5912", "591B", "591A", "591D")):
                    igpu_properties["AAPL,ig-platform-id"] = "00001B59"
                elif device_id.startswith(("5926", "5927")):
                    igpu_properties["AAPL,ig-platform-id"] = "02002659"
            elif platform == "Laptop":
                igpu_properties["AAPL,ig-platform-id"] = "00001B59"
                if device_id.startswith(("5917", "87C0")):
                    igpu_properties["AAPL,ig-platform-id"] = "00001659"
                else:
                    igpu_properties["framebuffer-con1-alldata"] = "01050A00000800008701000002040A000008000087010000"
                    igpu_properties["framebuffer-con1-enable"] = "01000000"
                    igpu_properties["#framebuffer-con1-alldata"] = "01050A00000800008701000003060A000004000087010000"
                    igpu_properties["#framebuffer-con1-enable"] = "01000000"
            igpu_properties["framebuffer-stolenmem"] = "00003001"
            igpu_properties["framebuffer-fbmem"] = "00009000"
        elif device_id.startswith(("3E", "87", "9B")):
            native_supported_ids = ("3E9B", "3EA5", "3EA6", "3E92", "3E91", "3E98", "9BC8", "9BC5", "9BC4")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "9B3E0000"
            if platform == "Desktop":
                if not any(monitor_info.get("Connected GPU") == integrated_gpu[0] for monitor_name, monitor_info in monitor.items()):
                    igpu_properties["AAPL,ig-platform-id"] = "0300913E" if not device_id.startswith("9B") else "0300C89B"
                    return igpu_properties
                igpu_properties["AAPL,ig-platform-id"] = "07009B3E" if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("19.5.0") else "00009B3E"
                igpu_properties["framebuffer-stolenmem"] = "00003001"
            elif platform == "NUC":
                igpu_properties["AAPL,ig-platform-id"] = "07009B3E"
                if device_id.startswith(("3EA5", "3EA8")):
                    igpu_properties["AAPL,ig-platform-id"] = "0000A53E"
            elif platform == "Laptop":
                igpu_properties["AAPL,ig-platform-id"] = "0900A53E"
                if device_id.startswith(("3EA9", "3EA0")):
                    igpu_properties["AAPL,ig-platform-id"] = "00009B3E"
                igpu_properties["framebuffer-stolenmem"] = "00003001"
                igpu_properties["framebuffer-fbmem"] = "00009000"
        elif device_id.startswith("8A"):
            native_supported_ids = ("FF05", "8A70", "8A71", "8A51", "8A5C", "8A5D", "8A52", "8A53", "8A5A", "8A5B")
            if not device_id in native_supported_ids:
                igpu_properties["device-id"] = "528A0000"
            igpu_properties["AAPL,ig-platform-id"] = "0200518A"
            igpu_properties["enable-dbuf-early-optimizer"] = "01000000"
            igpu_properties["enable-dvmt-calc-fix"] = "01000000"
            igpu_properties["enable-cdclk-frequency-fix"] = "01000000"
            igpu_properties["framebuffer-stolenmem"] = "00003001"
            igpu_properties["framebuffer-fbmem"] = "00009000"

        if any(tuple(map(int, "3840x2160".split("x"))) <= tuple(map(int, monitor_info.get("Resolution").split("x"))) for monitor_name, monitor_info in monitor.items()):
            if platform == "Laptop":
                igpu_properties["enable-max-pixel-clock-override"] = "01000000"
            if igpu_properties.get("framebuffer-stolenmem"):
                del igpu_properties["framebuffer-stolenmem"]
            if igpu_properties.get("framebuffer-fbmem"):
                del igpu_properties["framebuffer-fbmem"]

        for key in igpu_properties.keys():
            if key not in ("AAPL,ig-platform-id", "device-id"):
                igpu_properties["framebuffer-patch-enable"] = "01000000"
                break

        return dict(sorted(igpu_properties.items(), key=lambda item: item[0]))
  
    def deviceproperties(self, hardware_report, unsupported_devices, macos_version, kexts):
        deviceproperties_add = {}

        def add_device_property(pci_path, properties):
            if not pci_path or not properties:
                return

            if not deviceproperties_add.get(pci_path):
                deviceproperties_add[pci_path] = {}

            deviceproperties_add[pci_path].update(properties)

        for kext in kexts:
            if kext.checked:
                if kext.name == "AirportItlwm" and self.utils.parse_darwin_version("24.0.0") <= self.utils.parse_darwin_version(macos_version):
                    for network_name, network_props in hardware_report.get("Network", {}).items():
                        device_id = network_props.get("Device ID")

                        if device_id in pci_data.NetworkIDs[21:108] and network_props.get("PCI Path"):
                            add_device_property(network_props.get("PCI Path"), {"IOName": "pci14e4,43a0"})
                elif kext.name == "WhateverGreen":
                    discrete_gpu = None
                    for gpu_name, gpu_info in hardware_report.get("GPU", {}).items():
                        if gpu_info.get("Device Type") == "Integrated GPU":
                            if "Intel" in gpu_info.get("Manufacturer"):
                                add_device_property(gpu_info.get("PCI Path", "PciRoot(0x0)/Pci(0x2,0x0)"), self.igpu_properties(
                                    "NUC" if "NUC" in hardware_report.get("Motherboard").get("Name") else hardware_report.get("Motherboard").get("Platform"), 
                                    (gpu_name, gpu_info),
                                    hardware_report.get("Monitor", {}),
                                    macos_version
                                ))
                                if deviceproperties_add[gpu_info.get("PCI Path", "PciRoot(0x0)/Pci(0x2,0x0)")]:
                                    if gpu_info.get("Codename") in ("Sandy Bridge", "Ivy Bridge"):
                                        intel_mei = next((device_props for device_name, device_props in hardware_report.get("System Devices").items() if "HECI" in device_name or "Management Engine Interface" in device_name), None)
                                        if intel_mei:
                                            if "Sandy Bridge" in gpu_info.get("Codename") and intel_mei.get("Device ID") in "8086-1E3A":
                                                add_device_property(intel_mei.get("PCI Path", "PciRoot(0x0)/Pci(0x16,0x0)"), {"device-id": "3A1C0000"})
                                            elif "Ivy Bridge" in gpu_info.get("Codename") and intel_mei.get("Device ID") in "8086-1C3A":
                                                add_device_property(intel_mei.get("PCI Path", "PciRoot(0x0)/Pci(0x16,0x0)"), {"device-id": "3A1E0000"})
                        elif gpu_info.get("Device Type") == "Discrete GPU":
                            discrete_gpu = gpu_info

                            if not gpu_info.get("Device ID") in pci_data.SpoofGPUIDs:
                                continue

                            add_device_property(gpu_info.get("PCI Path"), {
                                "device-id": self.utils.to_little_endian_hex(pci_data.SpoofGPUIDs.get(gpu_info.get("Device ID")).split("-")[-1]),
                                "model": gpu_name
                            })
                elif kext.name == "AppleALC":
                    if not hardware_report.get("Sound"):
                        continue

                    for codec_props in hardware_report.get("Sound").values():
                        codec_id = codec_props.get("Device ID")
                        controller_id = codec_props.get("Controller Device ID", "Unknown")
                        controller_props = next((props for props in hardware_report.get("System Devices", {}).values() if props.get("Device ID") == controller_id), {})

                        if codec_id in codec_layouts.data:
                            recommended_authors = ("Mirone", "InsanelyDeepak", "Toleda", "DalianSky")
                            recommended_layouts = [layout for layout in codec_layouts.data.get(codec_id) if self.utils.contains_any(recommended_authors, layout.comment) or hardware_report.get("Motherboard").get("Name").split(" ")[0].lower() in layout.comment.lower()]

                            add_device_property(controller_props.get("PCI Path"), {"layout-id": random.choice((recommended_layouts or codec_layouts.data.get(codec_id))).id})

        network_items = hardware_report.get("Network", {}).items()

        for network_name, network_props in network_items:
            device_id = network_props.get("Device ID")

            try:
                device_index = pci_data.NetworkIDs.index(device_id)
            except:
                continue

            if device_index < 18:
                add_device_property(network_props.get("PCI Path"), {"IOName": "pci14e4,43a0"})
            elif 228 < device_index < 258:
                add_device_property(network_props.get("PCI Path"), {
                    "IOName": "pci14e4,16b4",
                    "device-id": self.utils.hex_to_bytes("B4160000")
                })

        storage_controllers_items = hardware_report.get("Storage Controllers", {}).items()

        for device_name, device_props in list(network_items) + list(storage_controllers_items):
            if not device_props.get("ACPI Path"):
                add_device_property(device_props.get("PCI Path"), {"built-in": "01"})

        for device_name, device_props in unsupported_devices.items():
            if "GPU" in device_name and not device_props.get("Disabled", False):
                add_device_property(device_props.get("PCI Path"), {"disable-gpu": True})

        for key, value in deviceproperties_add.items():
            for key_child, value_child in value.items():
                if isinstance(value_child, str):
                    deviceproperties_add[key][key_child] = self.utils.hex_to_bytes(deviceproperties_add[key][key_child])

        return deviceproperties_add

    def block_kext_bundle(self, kexts):
        kernel_block = []

        for kext in kexts:
            if kext.checked:
                if kext.name == "IOSkywalkFamily":
                    kernel_block.append({
                        "Arch": "x86_64",
                        "Comment": "Allow IOSkywalk Downgrade",
                        "Enabled": True,
                        "Identifier": "com.apple.iokit.IOSkywalkFamily",
                        "MaxKernel": "",
                        "MinKernel": "23.0.0",
                        "Strategy": "Exclude"
                    })
        
        return kernel_block

    def is_low_end_haswell_plus(self, processor_name, cpu_codename):
        return self.is_low_end_intel_cpu(processor_name) and cpu_codename in cpu_data.IntelCPUGenerations[:38]

    def is_intel_hedt_cpu(self, cpu_codename):
        return cpu_codename in cpu_data.IntelCPUGenerations[21:] and cpu_codename.endswith(("-X", "-P", "-W", "-E", "-EP", "-EX"))
            
    def spoof_cpuid(self, processor_name, cpu_codename, macos_version):
        if self.is_low_end_haswell_plus(processor_name, cpu_codename):
            return self.cpuids.get("Ivy Bridge")
        elif "Haswell" in cpu_codename and self.is_intel_hedt_cpu(cpu_codename):
            return self.cpuids.get("Haswell")
        elif "Broadwell" in cpu_codename and self.is_intel_hedt_cpu(cpu_codename):
            return self.cpuids.get("Broadwell")
        elif "Ice Lake" not in cpu_codename and self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=10):
            if not "Comet Lake" in cpu_codename:
                return self.cpuids.get("Comet Lake")
            if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("19.0.0"):
                return self.cpuids.get("Coffee Lake")
            
        return None
    
    def load_kernel_patch(self, motherboard_chipset, cpu_manufacturer, cpu_codename, cpu_cores, gpu_manufacturer, networks, kexts):
        kernel_patch = []

        if "AMD" in cpu_manufacturer:
            kernel_patch.extend(self.g.get_kernel_patches("AMD Vanilla Patches", self.g.amd_vanilla_patches_url))

        if any(network_props.get("Device ID") in pci_data.NetworkIDs[263:270] for network_props in networks.values()):
            kernel_patch.extend(self.g.get_kernel_patches("Aquantia macOS Patches", self.g.aquantia_macos_patches_url))

        for kext in kexts:
            if kext.checked:
                if kext.name == "CpuTopologyRebuild":
                    kernel_patch.extend(self.g.get_kernel_patches("Hyper Threading Patches", self.g.hyper_threading_patches_url))
                elif kext.name == "ForgedInvariant":
                    if not "AMD" in cpu_manufacturer:
                        kernel_patch.extend(self.g.get_kernel_patches("AMD Vanilla Patches", self.g.amd_vanilla_patches_url)[-6:-4])
                elif kext.name == "CatalinaBCM5701Ethernet":
                    kernel_patch.append({
                        "Arch": "Any",
                        "Base": "",
                        "Comment": "Broadcom BCM577XX Patch",
                        "Count": 1,
                        "Enabled": True,
                        "Find": self.utils.hex_to_bytes("E8CA9EFFFF66898300050000"),
                        "Identifier": "com.apple.iokit.CatalinaBCM5701Ethernet",
                        "Limit": 0,
                        "Mask": self.utils.hex_to_bytes(""),
                        "MaxKernel": "",
                        "MinKernel": "20.0.0",
                        "Replace": self.utils.hex_to_bytes("B8B416000066898300050000"),
                        "ReplaceMask": self.utils.hex_to_bytes(""),
                        "Skip": 0
                    })

        for patch in kernel_patch:
            if "AppleEthernetAquantiaAqtion" in patch["Identifier"]:
                patch["Enabled"] = patch["Base"] != ""
            elif "cpuid_cores_per_package" in patch["Comment"]:
                patch["Replace"] = patch["Replace"].hex()
                patch["Replace"] = self.utils.hex_to_bytes(patch["Replace"][:2] + self.utils.int_to_hex(int(cpu_cores)) + patch["Replace"][4:])
            elif "IOPCIIsHotplugPort" in patch["Comment"]:
                if motherboard_chipset in chipset_data.AMDChipsets[17:] or cpu_codename in ("Raphael", "Storm Peak", "Phoenix", "Granite Ridge"):
                    patch["Enabled"] = True
            elif "_mtrr_update_action" in patch["Comment"]:
                if "TRX" in motherboard_chipset.upper():
                    patch["Enabled"] = False
                elif "AMD" in gpu_manufacturer:
                    if "algrey" in patch["Comment"].lower():
                        patch["Enabled"] = False
                    elif "shaneee" in patch["Comment"].lower():
                        patch["Enabled"] = True
        
        return kernel_patch

    def boot_args(self, hardware_report, macos_version, kexts, resize_bar):
        boot_args = [
            "-v",
            "debug=0x100",
            "keepsyms=1"
        ]

        if not resize_bar and ("AMD" in hardware_report.get("CPU").get("Manufacturer") or self.is_intel_hedt_cpu(hardware_report.get("CPU").get("Codename"))):
            boot_args.append("npci=0x2000")

        for kext in kexts:
            if not kext.checked:
                continue

            if "Lilu" in kext.requires_kexts and not self.utils.parse_darwin_version(kext.min_darwin_version) <= self.utils.parse_darwin_version(macos_version) <= self.utils.parse_darwin_version(kext.max_darwin_version):
                if not "-lilubetaall" in boot_args:
                    boot_args.append("-lilubetaall")

            if kext.name == "WhateverGreen":
                if  any(tuple(map(int, "3840x2160".split("x"))) <= tuple(map(int, monitor_info.get("Resolution").split("x"))) for monitor_name, monitor_info in hardware_report.get("Monitor", {}).items()) and \
                    self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("20.0.0"):
                    boot_args.append("-cdfon")

                if  "Intel" in hardware_report.get("CPU").get("Manufacturer") and \
                    "Integrated GPU" in list(hardware_report.get("GPU").items())[-1][-1].get("Device Type"):
                    intergrated_gpu = list(hardware_report.get("GPU").items())[-1]
                    if intergrated_gpu[-1].get("OCLP Compatibility"):
                        boot_args.append("ipc_control_port_options=0")

                    if "Ice Lake" in intergrated_gpu[-1].get("Codename"):
                        boot_args.extend(("-noDC9", "-igfxblr"))

                    if "Desktop" in hardware_report.get("Motherboard").get("Platform"):
                        if any(monitor_info.get("Connected GPU") == intergrated_gpu[0] for monitor_name, monitor_info in hardware_report.get("Monitor", {}).items()) and intergrated_gpu[-1].get("Device ID")[5:].startswith(("3E", "87", "9B")) and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("19.4.0"):
                            boot_args.append("igfxonln=1")
                        if any(monitor_info.get("Connector Type") in ("DVI", "HDMI") for monitor_name, monitor_info in hardware_report.get("Monitor", {}).items() if monitor_info.get("Connected GPU") == intergrated_gpu[0]):
                            boot_args.append("-igfxvesa")
                    elif "Laptop" in hardware_report.get("Motherboard").get("Platform"):
                        if intergrated_gpu[-1].get("Device ID")[5:].startswith(("59", "8C", "3E", "87", "9B")) and not intergrated_gpu[-1].get("Device ID").endswith("5917"):
                            boot_args.append("-igfxbl{}".format("t" if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("22.5.0") else "r"))

                discrete_gpu = list(hardware_report.get("GPU").items())[0][-1]
                if discrete_gpu.get("Device Type") == "Discrete GPU":
                    if "Navi" in discrete_gpu.get("Codename"):
                        boot_args.append("agdpmod=pikera")

                    if discrete_gpu.get("Device ID") in pci_data.SpoofGPUIDs:
                        boot_args.append("-radcodec")

                    if discrete_gpu.get("Device ID") in ("1002-6610", "1002-682B", "1002-6837", "1002-683D", "1002-683F"):
                        boot_args.append("radpg=15")

                    if discrete_gpu.get("Device ID") in ("1002-67B0", "1002-67B1", "1002-67B8", "1002-6810", "1002-6811"):
                        boot_args.append("-raddvi")

                    if discrete_gpu.get("OCLP Compatibility"):
                        if discrete_gpu.get("Manufacturer") == "AMD":
                            boot_args.append("-radvesa" if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("23.0.0") else "-amd_no_dgpu_accel")
                        elif discrete_gpu.get("Manufacturer") == "NVIDIA" and not "Kepler" in discrete_gpu.get("Codename"):
                            boot_args.extend(("nvda_drv_vrl=1", "ngfxcompat=1", "ngfxgl=1"))
            elif kext.name == "AppleALC":
                if not hardware_report.get("Sound"):
                    continue

                codec_props = list(hardware_report.get("Sound").items())[0][-1]
                codec_id = codec_props.get("Device ID")
                controller_id = codec_props.get("Controller Device ID", "Unknown")

                controller_props = next((props for props in hardware_report.get("System Devices", {}).values() if props.get("Device ID") == controller_id), {})
                pci_path = controller_props.get("PCI Path")

                if pci_path:
                    continue

                if codec_id in codec_layouts.data:
                    recommended_authors = ("Mirone", "InsanelyDeepak", "Toleda", "DalianSky")
                    recommended_layouts = [layout for layout in codec_layouts.data.get(codec_id) if self.utils.contains_any(recommended_authors, layout.comment) or hardware_report.get("Motherboard").get("Name").split(" ")[0].lower() in layout.comment.lower()]
                    boot_args.append("alcid={}".format(random.choice((recommended_layouts or codec_layouts.data.get(codec_id))).id))
            elif kext.name == "VoodooI2C":
                boot_args.append("-vi2c-force-polling")
            elif kext.name == "CpuTopologyRebuild":
                boot_args.append("ctrsmt=full")

        return " ".join(boot_args)
    
    def csr_active_config(self, macos_version):
        if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("20.0.0"):
            return "030A0000"
        elif self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("18.0.0"):
            return "FF070000"
        else:
            return "FF030000"
        
    def load_drivers(self):
        uefi_drivers = []

        for driver_path in ("HfsPlus.efi", "OpenCanopy.efi", "OpenRuntime.efi", "ResetNvramEntry.efi"):
            uefi_drivers.append({
                "Arguments": "",
                "Comment": "",
                "Enabled": True,
                "LoadEarly": False,
                "Path": driver_path
            })
        
        return uefi_drivers

    def genarate(self, hardware_report, unsupported_devices, smbios_model, macos_version, needs_oclp, kexts, config):
        del config["#WARNING - 1"]
        del config["#WARNING - 2"]
        del config["#WARNING - 3"]
        del config["#WARNING - 4"]

        config["Booter"]["MmioWhitelist"] = self.mmio_whitelist(hardware_report.get("Motherboard").get("Chipset"))
        config["Booter"]["Patch"] = self.add_booter_patch(smbios_model, macos_version)
        config["Booter"]["Quirks"]["DevirtualiseMmio"] = len(config["Booter"]["MmioWhitelist"]) != 0 or \
            hardware_report.get("Motherboard").get("Chipset") in chipset_data.IntelChipsets[101:] + chipset_data.IntelChipsets[79:89] or \
            hardware_report.get("Motherboard").get("Chipset") in chipset_data.IntelChipsets[93:101] and ("Desktop" in hardware_report.get("Motherboard").get("Platform") or not "-8" in hardware_report.get("CPU").get("Processor Name")) or \
            hardware_report.get("Motherboard").get("Chipset") == chipset_data.AMDChipsets[16]
        config["Booter"]["Quirks"]["EnableWriteUnprotector"] = not ("AMD" in hardware_report.get("CPU").get("Manufacturer") or hardware_report.get("Motherboard").get("Chipset") in chipset_data.IntelChipsets[79:89] + chipset_data.IntelChipsets[101:])
        config["Booter"]["Quirks"]["ProtectMemoryRegions"] = "GOOGLE" in hardware_report.get("Motherboard").get("Name") or any(device_props.get("Device ID") in pci_data.ChromebookIDs and device_props.get("Subsystem ID") in pci_data.ChromebookIDs[device_props.get("Device ID")] for device_props in hardware_report.get("System Devices", {}).values())
        config["Booter"]["Quirks"]["ProtectUefiServices"] = hardware_report.get("Motherboard").get("Chipset") in chipset_data.IntelChipsets[101:] or \
            hardware_report.get("Motherboard").get("Chipset") in chipset_data.IntelChipsets[93:101] and (not "-8" in hardware_report.get("CPU").get("Processor Name") or hardware_report.get("Motherboard").get("Chipset") == chipset_data.IntelChipsets[98])
        config["Booter"]["Quirks"]["RebuildAppleMemoryMap"] = not config["Booter"]["Quirks"]["EnableWriteUnprotector"]
        config["Booter"]["Quirks"]["ResizeAppleGpuBars"] = 0 if any(gpu_props.get("Resizable BAR", "Disabled") == "Enabled" for gpu_name, gpu_props in hardware_report.get("GPU", {}).items()) else -1
        config["Booter"]["Quirks"]["SetupVirtualMap"] = not hardware_report.get("Motherboard").get("Chipset") in chipset_data.AMDChipsets[11:17] + chipset_data.IntelChipsets[79:89]
        config["Booter"]["Quirks"]["SyncRuntimePermissions"] = "AMD" in hardware_report.get("CPU").get("Manufacturer") or hardware_report.get("Motherboard").get("Chipset") in chipset_data.IntelChipsets[79:89] + chipset_data.IntelChipsets[93:]

        config["DeviceProperties"]["Add"] = self.deviceproperties(hardware_report, unsupported_devices, macos_version, kexts)

        config["Kernel"]["Block"] = self.block_kext_bundle(kexts)
        spoof_cpuid = self.spoof_cpuid(
            hardware_report.get("CPU").get("Processor Name"), 
            hardware_report.get("CPU").get("Codename"), 
            macos_version
        )
        if spoof_cpuid:
            config["Kernel"]["Emulate"]["Cpuid1Data"] = self.utils.hex_to_bytes("{}{}".format(spoof_cpuid, "0"*8*3))
            config["Kernel"]["Emulate"]["Cpuid1Mask"] = self.utils.hex_to_bytes("{}{}".format("F"*8, "0"*8*3))
        config["Kernel"]["Emulate"]["DummyPowerManagement"] = "AMD" in hardware_report.get("CPU").get("Manufacturer") or \
            self.is_low_end_intel_cpu(hardware_report.get("CPU").get("Processor Name"))
        config["Kernel"]["Force"] = []
        config["Kernel"]["Patch"] = self.load_kernel_patch(
            hardware_report.get("Motherboard").get("Chipset"),
            hardware_report.get("CPU").get("Manufacturer"),
            hardware_report.get("CPU").get("Codename"), 
            hardware_report.get("CPU").get("Core Count"), 
            list(hardware_report.get("GPU").items())[0][-1].get("Manufacturer"),
            hardware_report.get("Network", {}),
            kexts
        )
        config["Kernel"]["Quirks"]["AppleCpuPmCfgLock"] = bool(self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware_report.get("CPU").get("Codename"), start=38))
        config["Kernel"]["Quirks"]["AppleXcpmCfgLock"] = False if "AMD" in hardware_report.get("CPU").get("Manufacturer") else not config["Kernel"]["Quirks"]["AppleCpuPmCfgLock"]
        config["Kernel"]["Quirks"]["AppleXcpmExtraMsrs"] = "-E" in hardware_report.get("CPU").get("Codename") and hardware_report.get("CPU").get("Codename") in cpu_data.IntelCPUGenerations[26:]
        config["Kernel"]["Quirks"]["CustomSMBIOSGuid"] = True
        config["Kernel"]["Quirks"]["DisableIoMapper"] = not "AMD" in hardware_report.get("CPU").get("Manufacturer")
        config["Kernel"]["Quirks"]["DisableRtcChecksum"] = "ASUS" in hardware_report.get("Motherboard").get("Name") or "HP " in hardware_report.get("Motherboard").get("Name")
        config["Kernel"]["Quirks"]["ForceAquantiaEthernet"] = any(network_props.get("Device ID") in pci_data.NetworkIDs[263:270] for network_props in hardware_report.get("Network", {}).values())
        config["Kernel"]["Quirks"]["LapicKernelPanic"] = "HP " in hardware_report.get("Motherboard").get("Name")
        config["Kernel"]["Quirks"]["PanicNoKextDump"] = config["Kernel"]["Quirks"]["PowerTimeoutKernelPanic"] = True
        config["Kernel"]["Quirks"]["ProvideCurrentCpuInfo"] = "AMD" in hardware_report.get("CPU").get("Manufacturer") or hardware_report.get("CPU").get("Codename") in cpu_data.IntelCPUGenerations[:2]

        config["Misc"]["BlessOverride"] = []
        config["Misc"]["Boot"]["HideAuxiliary"] = False
        config["Misc"]["Boot"]["PickerMode"] = "External"
        config["Misc"]["Boot"]["Timeout"] = 10
        config["Misc"]["Debug"]["AppleDebug"] = config["Misc"]["Debug"]["ApplePanic"] = False
        config["Misc"]["Debug"]["DisableWatchDog"] = True
        config["Misc"]["Debug"]["Target"] = 0
        config["Misc"]["Entries"] = []
        config["Misc"]["Security"]["AllowSetDefault"] = True
        config["Misc"]["Security"]["ScanPolicy"] = 0
        config["Misc"]["Security"]["SecureBootModel"] = "Default" if not needs_oclp and self.utils.parse_darwin_version("20.0.0") <= self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("23.0.0") else "Disabled"
        config["Misc"]["Security"]["Vault"] = "Optional"
        config["Misc"]["Tools"] = []

        del config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["#INFO (prev-lang:kbd)"]
        config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] = self.boot_args(hardware_report, macos_version, kexts, config["Booter"]["Quirks"]["ResizeAppleGpuBars"] == 0)
        config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = self.utils.hex_to_bytes(self.csr_active_config(macos_version))
        config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["prev-lang:kbd"] = "en:252"
        config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].append("csr-active-config")

        config["PlatformInfo"]["Generic"].update(self.smbios.generate_smbios(smbios_model))
        config["PlatformInfo"]["Generic"]["ROM"] = self.utils.hex_to_bytes(config["PlatformInfo"]["Generic"]["ROM"])
        config["PlatformInfo"]["UpdateSMBIOSMode"] = "Custom"

        config["UEFI"]["APFS"]["MinDate"] = config["UEFI"]["APFS"]["MinVersion"] = -1
        config["UEFI"]["Drivers"] = self.load_drivers()
        config["UEFI"]["Quirks"]["ForceOcWriteFlash"] = any(device_props.get("Device ID") in pci_data.ThinkPadTWX30IDs and device_props.get("Subsystem ID") in pci_data.ThinkPadTWX30IDs[device_props.get("Device ID")] for device_props in hardware_report.get("System Devices", {}).values())
        config["UEFI"]["Quirks"]["IgnoreInvalidFlexRatio"] = hardware_report.get("CPU").get("Codename") in cpu_data.IntelCPUGenerations[26:]
        config["UEFI"]["Quirks"]["ReleaseUsbOwnership"] = True
        config["UEFI"]["Quirks"]["UnblockFsConnect"] = "HP " in hardware_report.get("Motherboard").get("Name")
        config["UEFI"]["ReservedMemory"] = []

        for kext in kexts:
            if kext.checked:
                if kext.name == "BlueToolFixup":
                    config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["bluetoothExternalDongleFailed"] = self.utils.hex_to_bytes("00")
                    config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["bluetoothInternalControllerInfo"] = self.utils.hex_to_bytes("0000000000000000000000000000")
                elif kext.name == "RestrictEvents":
                    revpatch = []
                    revblock = []
                    if self.utils.parse_darwin_version(macos_version) > self.utils.parse_darwin_version("23.0.0") or \
                        len(config["Booter"]["Patch"]) and self.utils.parse_darwin_version(macos_version) > self.utils.parse_darwin_version("20.4.0"):
                        revpatch.append("sbvmm")
                    if  not (" Core" in hardware_report.get("CPU").get("Processor Name") and \
                        self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware_report.get("CPU").get("Codename"), start=4)):
                        config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpu"] = 1
                        config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpuname"] = hardware_report.get("CPU").get("Processor Name")
                        if self.utils.parse_darwin_version(macos_version) > self.utils.parse_darwin_version("23.0.0"):
                            revpatch.append("cpuname")
                        config["PlatformInfo"]["Generic"]["ProcessorType"] = 1537 if int(hardware_report.get("CPU").get("Core Count")) < 8 else 3841
                    if  "Intel" in hardware_report.get("CPU").get("Manufacturer") and \
                        "Integrated GPU" in list(hardware_report.get("GPU").items())[-1][-1].get("Device Type"):
                        intergrated_gpu = list(hardware_report.get("GPU").items())[-1][-1]
                        if intergrated_gpu.get("OCLP Compatibility"):
                            config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] = "-allow_amfi"
                            if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("20.4.0"):
                                if intergrated_gpu.get("Codename") in ("Broadwell", "Haswell", "Ivy Bridge", "Sandy Bridge"):
                                    revblock.append("media")
                                if intergrated_gpu.get("Codename") in ("Kaby Lake", "Skylake", "Broadwell", "Haswell"):
                                    revpatch.append("asset")
                                elif intergrated_gpu.get("Codename") in ("Ivy Bridge", "Sandy Bridge"):
                                    revpatch.append("f16c")
                    if revpatch:
                        config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revpatch"] = ",".join(revpatch)
                    if revblock:
                        config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revblock"] = ",".join(revblock)
        
        config["NVRAM"]["Delete"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"] = list(config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"].keys())
        config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] = list(config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].keys())

        return config