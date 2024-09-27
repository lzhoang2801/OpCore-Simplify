from Scripts.datasets import chipset_data
from Scripts.datasets import cpu_data
from Scripts.datasets import os_data
from Scripts import codec_layouts
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
                "Enable": True
            })
        elif "B650" in motherboard_chipset or "X670" in motherboard_chipset:
            booter_mmiowhitelist.append({
                "Address": 4244635648,
                "Comment": "MMIO 0xFD000000",
                "Enable": True
            })
        
        return booter_mmiowhitelist

    def check_mats_support(self, cpu_manufacturer, motherboard_chipset):
        return "AMD" in cpu_manufacturer or \
            not self.utils.contains_any(chipset_data.IntelChipsets, motherboard_chipset, start=97) is None or \
            not self.utils.contains_any(chipset_data.IntelChipsets, motherboard_chipset, start=49, end=60) is None

    def check_resizable_bar_support(self, motherboard_chipset, cpu_codename):
        return not self.utils.contains_any(chipset_data.AMDChipsets, motherboard_chipset) is None or not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=10) is None

    def is_low_end_intel_cpu(self, processor_name):
        return any(brand in processor_name for brand in ["Celeron", "Pentium"])
            
    def deviceproperties(self, cpu_codename, intel_mei, igpu_properties):
        deviceproperties_add = {}

        if igpu_properties:
            deviceproperties_add["PciRoot(0x0)/Pci(0x2,0x0)"] = igpu_properties
        if intel_mei:
            if "Sandy Bridge" in cpu_codename and intel_mei.get("Device ID") in "8086-1E3A":
                deviceproperties_add["PciRoot(0x0)/Pci(0x16,0x0)"] = {
                    "device-id": "3A1C0000"
                }
            elif "Ivy Bridge" in cpu_codename and intel_mei.get("Device ID") in "8086-1C3A":
                deviceproperties_add["PciRoot(0x0)/Pci(0x16,0x0)"] = {
                    "device-id": "3A1E0000"
                }

        for key, value in deviceproperties_add.items():
            for key_child, value_child in value.items():
                if isinstance(value_child, str):
                    deviceproperties_add[key][key_child] = self.utils.hex_to_bytes(deviceproperties_add[key][key_child])

        return deviceproperties_add

    def block_kext_bundle(self, network, macos_version):
        kernel_block = []

        if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
            for network_name, network_props in network.items():
                if network_props.get("Device ID") in ["14E4-43A0", "14E4-43A3", "14E4-43BA"]:
                    kernel_block.append({
                        "Arch": "x86_64",
                        "Comment": "Allow IOSkywalk Downgrade",
                        "Enabled": True,
                        "Identifier": "com.apple.iokit.IOSkywalkFamily",
                        "MaxKernel": "",
                        "MinKernel": "",
                        "Strategy": "Exclude"
                    })
        
        return kernel_block

    def is_low_end_haswell_plus(self, processor_name, cpu_codename):
        return self.is_low_end_intel_cpu(processor_name) and not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=2) is None

    def is_intel_hedt_cpu(self, cpu_codename):
        return "-E" in cpu_codename and not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=4) is None or \
            ("-X" in cpu_codename or "-W" in cpu_codename) and not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=4, end=6) is None
            
    def spoof_cpuid(self, processor_name, cpu_codename, macos_version):
        if self.is_low_end_haswell_plus(processor_name, cpu_codename):
            return self.cpuids.get("Ivy Bridge")
        elif "Haswell" in cpu_codename and self.is_intel_hedt_cpu(cpu_codename):
            return self.cpuids.get("Haswell")
        elif "Broadwell" in cpu_codename and self.is_intel_hedt_cpu(cpu_codename):
            return self.cpuids.get("Broadwell")
        elif "Ice Lake" not in cpu_codename and self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=10):
            if not "Comet Lake" in cpu_codename:
                return self.cpuids.get("Comet Lake")
            if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("19.0.0"):
                return self.cpuids.get("Coffee Lake")
            
        return None
    
    def load_kernel_patch(self, motherboard_chipset, cpu_manufacturer, cpu_codename, cpu_cores, gpu_manufacturer, tsc_sync):
        kernel_patch = []

        if "AMD" in cpu_manufacturer:
            kernel_patch.extend(self.g.get_amd_kernel_patches())
        elif tsc_sync:
            kernel_patch.extend(self.g.get_amd_kernel_patches()[-6:-4])
        
        if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=13) and int(cpu_cores) > 6:
            kernel_patch.append({
                "Arch": "Any",
                "Base": "_cpu_thread_alloc",
                "Comment": "Force enable Hyper Threading for macOS Mojave or later",
                "Count": 1,
                "Enabled": True,
                "Find": self.utils.hex_to_bytes("8B8894010000"),
                "Identifier": "kernel",
                "Limit": 0,
                "Mask": self.utils.hex_to_bytes(""),
                "MaxKernel": "",
                "MinKernel": "18.0.0",
                "Replace": self.utils.hex_to_bytes("B9FF00000090"),
                "ReplaceMask": self.utils.hex_to_bytes(""),
                "Skip": 0
            })

        for patch in kernel_patch:
            if "cpuid_cores_per_package" in patch["Comment"]:
                patch["Replace"] = patch["Replace"].hex()
                patch["Replace"] = self.utils.hex_to_bytes(patch["Replace"][:2] + self.utils.int_to_hex(int(cpu_cores)) + patch["Replace"][4:])
            elif "IOPCIIsHotplugPort" in patch["Comment"]:
                if self.utils.contains_any(chipset_data.AMDChipsets, motherboard_chipset, start=6):
                    patch["Enabled"] = True
            if "_mtrr_update_action" in patch["Comment"]:
                if chipset_data.AMDChipsets[0].lower() in motherboard_chipset.lower():
                    patch["Enabled"] = False
                elif "AMD" in gpu_manufacturer:
                    if "algrey" in patch["Comment"].lower():
                        patch["Enabled"] = False
                    elif "shaneee" in patch["Comment"].lower():
                        patch["Enabled"] = True
        
        return kernel_patch

    def boot_args(self, motherboard_name, platform, cpu_manufacturer, cpu_codename, cpu_cores, discrete_gpu_codename, discrete_gpu_id, integrated_gpu_name, codec_id, touchpad_communication, unsupported_devices, custom_cpu_name, macos_version):
        boot_args = [
            "-v",
            "debug=0x100",
            "keepsyms=1"
        ]

        if codec_id in codec_layouts.data:
            boot_args.append("alcid={}".format(random.choice(codec_layouts.data.get(codec_id))))

        if "AMD" in cpu_manufacturer or self.is_intel_hedt_cpu(cpu_codename):
            boot_args.append("npci=0x2000")

        if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
            boot_args.append("revpatch=sbvmm{}".format(",cpuname" if custom_cpu_name else ""))

        if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=13) and int(cpu_cores) > 6:
            boot_args.append("-ctrsmt")

        if "Intel" in cpu_manufacturer:
            if "UHD" in integrated_gpu_name and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("19.0.0"):
                boot_args.append("igfxonln=1")

            if "Ice Lake" in cpu_codename:
                boot_args.extend(["-noDC9", "-igfxcdc", "-igfxdvmt", "-igfxdbeo"])

            if "Laptop" in platform:
                if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=6):
                    boot_args.append("-igfxbl{}".format("t" if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0") else "r"))

        if "Navi" in discrete_gpu_codename and not "Navi 2" in discrete_gpu_codename:
            boot_args.append("agdpmod=pikera")

        if not "SURFACE" in motherboard_name and "I2C" in touchpad_communication:
            boot_args.append("-vi2c-force-polling")

        if "Beta" in os_data.get_macos_name_by_darwin(macos_version):
            boot_args.append("-lilubetaall")

        if "Discrete GPU" in unsupported_devices:
            boot_args.append("-wegnoegpu")

        if "Integrated GPU" in unsupported_devices:
            boot_args.append("-wegnoigpu")

        if discrete_gpu_id in ["1002-6610", "1002-682B", "1002-6837", "1002-683D", "1002-683F"]:
            boot_args.append("radpg=15")

        if discrete_gpu_id in ["1002-67B0", "1002-67B1", "1002-67B8", "1002-6810", "1002-6811"]:
            boot_args.append("-raddvi")

        return " ".join(boot_args)
    
    def csr_active_config(self, macos_version):
        if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("20.0.0"):
            return "03080000"
        elif self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("18.0.0"):
            return "FF070000"
        else:
            return "FF030000"
        
    def load_drivers(self):
        uefi_drivers = []

        for driver_path in ["OpenCanopy.efi", "OpenHfsPlus.efi", "OpenRuntime.efi", "ResetNvramEntry.efi"]:
            uefi_drivers.append({
                "Arguments": "",
                "Comment": "",
                "Enabled": True,
                "LoadEarly": False,
                "Path": driver_path
            })
        
        return uefi_drivers

    def genarate(self, hardware, efi_option, config):
        del config["#WARNING - 1"]
        del config["#WARNING - 2"]
        del config["#WARNING - 3"]
        del config["#WARNING - 4"]
        config["ACPI"]["Add"] = efi_option.get("ACPI").get("Add")
        config["ACPI"]["Delete"] = efi_option.get("ACPI").get("Delete")
        config["ACPI"]["Patch"] = efi_option.get("ACPI").get("Patch")

        config["Booter"]["MmioWhitelist"] = self.mmio_whitelist(hardware.get("Motherboard Chipset"))
        config["Booter"]["Patch"] = []
        config["Booter"]["Quirks"]["DevirtualiseMmio"] = self.check_mats_support(hardware.get("CPU Manufacturer"), hardware.get("Motherboard Chipset"))
        if "AMD" in hardware.get("CPU Manufacturer") and not "TRX40" in hardware.get("Motherboard Chipset"):
            config["Booter"]["Quirks"]["DevirtualiseMmio"] = False
        config["Booter"]["Quirks"]["EnableWriteUnprotector"] = False if "AMD" in hardware.get("CPU Manufacturer") else not config["Booter"]["Quirks"]["DevirtualiseMmio"]
        config["Booter"]["Quirks"]["ProtectUefiServices"] = "Z390" in hardware.get("Motherboard Chipset") or \
            not self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware.get("CPU Codename"), start=10) is None
        config["Booter"]["Quirks"]["RebuildAppleMemoryMap"] = not config["Booter"]["Quirks"]["EnableWriteUnprotector"]
        config["Booter"]["Quirks"]["ResizeAppleGpuBars"] = 0 if self.check_resizable_bar_support(
            hardware.get("Motherboard Chipset"), 
            hardware.get("CPU Codename")
        ) else -1
        config["Booter"]["Quirks"]["SetupVirtualMap"] = not (not self.utils.contains_any(chipset_data.AMDChipsets, hardware.get("Motherboard Chipset"), end=5) is None or \
            "ASUS" in hardware.get("Motherboard Name") and self.is_intel_hedt_cpu(hardware.get("CPU Codename")) and config["Booter"]["Quirks"]["DevirtualiseMmio"])
        config["Booter"]["Quirks"]["SyncRuntimePermissions"] = config["Booter"]["Quirks"]["RebuildAppleMemoryMap"]

        config["DeviceProperties"]["Add"] = self.deviceproperties(hardware.get("CPU Codename"), hardware.get("Intel MEI"), efi_option.get("iGPU Properties"))

        config["Kernel"]["Add"] = efi_option.get("Kernel_Add")
        config["Kernel"]["Block"] = self.block_kext_bundle(hardware.get("Network"), efi_option.get("macOS Version"))
        spoof_cpuid = self.spoof_cpuid(
            hardware.get("Processor Name"), 
            hardware.get("CPU Codename"), 
            efi_option.get("macOS Version")
        )
        if spoof_cpuid:
            config["Kernel"]["Emulate"]["Cpuid1Data"] = self.utils.hex_to_bytes("{}{}".format(spoof_cpuid, "0"*8*3))
            config["Kernel"]["Emulate"]["Cpuid1Mask"] = self.utils.hex_to_bytes("{}{}".format("F"*8, "0"*8*3))
        config["Kernel"]["Emulate"]["DummyPowerManagement"] = "AMD" in hardware.get("CPU Manufacturer") or \
            self.is_low_end_intel_cpu(hardware.get("Processor Name"))
        config["Kernel"]["Force"] = []
        config["Kernel"]["Patch"] = self.load_kernel_patch(
            hardware.get("Motherboard Chipset"),
            hardware.get("CPU Manufacturer"), 
            hardware.get("CPU Codename"), 
            hardware["CPU Cores"], 
            hardware["Discrete GPU"].get("Manufacturer", "") or hardware["Integrated GPU"].get("Manufacturer", ""), 
            efi_option.get("Synchronize the TSC")
        )
        config["Kernel"]["Quirks"]["AppleCpuPmCfgLock"] = not self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware.get("CPU Codename"), end=2) is None
        config["Kernel"]["Quirks"]["AppleXcpmCfgLock"] = False if "AMD" in hardware.get("CPU Manufacturer") else not config["Kernel"]["Quirks"]["AppleCpuPmCfgLock"]
        config["Kernel"]["Quirks"]["AppleXcpmExtraMsrs"] = self.is_intel_hedt_cpu(hardware.get("CPU Codename")) and not self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware.get("CPU Codename"), end=4) is None
        config["Kernel"]["Quirks"]["CustomSMBIOSGuid"] = True
        config["Kernel"]["Quirks"]["DisableIoMapper"] = not "AMD" in hardware.get("CPU Manufacturer")
        config["Kernel"]["Quirks"]["DisableRtcChecksum"] = "ASUS" in hardware.get("Motherboard Name") or "HP" in hardware.get("Motherboard Name")
        config["Kernel"]["Quirks"]["LapicKernelPanic"] = "HP" in hardware.get("Motherboard Name")
        config["Kernel"]["Quirks"]["PanicNoKextDump"] = config["Kernel"]["Quirks"]["PowerTimeoutKernelPanic"] = True
        config["Kernel"]["Quirks"]["ProvideCurrentCpuInfo"] = "AMD" in hardware.get("CPU Manufacturer") or \
            not self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware.get("CPU Codename"), start=13) is None

        config["Misc"]["BlessOverride"] = []
        config["Misc"]["Boot"]["HideAuxiliary"] = False
        config["Misc"]["Boot"]["LauncherOption"] = "Full"
        config["Misc"]["Boot"]["PickerMode"] = "External"
        config["Misc"]["Boot"]["Timeout"] = 10
        config["Misc"]["Debug"]["AppleDebug"] = config["Misc"]["Debug"]["ApplePanic"] = False
        config["Misc"]["Debug"]["DisableWatchDog"] = True
        config["Misc"]["Debug"]["Target"] = 0
        config["Misc"]["Entries"] = []
        config["Misc"]["Security"]["AllowSetDefault"] = True
        config["Misc"]["Security"]["ScanPolicy"] = 0
        config["Misc"]["Security"]["SecureBootModel"] = "Default" if self.utils.parse_darwin_version("20.0.0") <= self.utils.parse_darwin_version(efi_option.get("macOS Version")) < self.utils.parse_darwin_version("23.0.0") else "Disabled"
        config["Misc"]["Security"]["Vault"] = "Optional"
        config["Misc"]["Tools"] = []

        if efi_option.get("Custom CPU Name"):
            config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpu"] = 1
            config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revcpuname"] = hardware.get("Processor Name")
        del config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["#INFO (prev-lang:kbd)"]
        config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] = self.boot_args(
            hardware.get("Motherboard Name"), 
            hardware.get("Platform"), 
            hardware.get("CPU Manufacturer"), 
            hardware.get("CPU Codename"), 
            hardware.get("CPU Cores"), 
            hardware.get("Discrete GPU").get("GPU Codename", ""), 
            hardware.get("Discrete GPU").get("Device ID", ""), 
            hardware.get("Integrated GPU Name"), 
            hardware.get("Codec ID"),
            hardware.get("Touchpad Communication"),
            ", ".join(list(hardware.get("Unsupported Devices").keys())),
            efi_option.get("Custom CPU Name"), 
            efi_option.get("macOS Version")
        )
        config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = self.utils.hex_to_bytes(self.csr_active_config(efi_option.get("macOS Version")))
        config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["prev-lang:kbd"] = "en:252"
        if efi_option.get("Custom CPU Name"):
            config["NVRAM"]["Delete"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"].extend(["revcpu", "revcpuname"])
        config["NVRAM"]["Delete"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].append("csr-active-config")

        config["PlatformInfo"]["Generic"].update(self.smbios.generate(efi_option.get("SMBIOS")))
        if efi_option.get("Custom CPU Name"):
            config["PlatformInfo"]["Generic"]["ProcessorType"] = 1537 if int(hardware["CPU Cores"]) < 8 else 3841
        config["PlatformInfo"]["Generic"]["ROM"] = self.utils.hex_to_bytes(config["PlatformInfo"]["Generic"]["ROM"])
        config["PlatformInfo"]["UpdateSMBIOSMode"] = "Custom"

        config["UEFI"]["APFS"]["MinDate"] = config["UEFI"]["APFS"]["MinVersion"] = -1
        config["UEFI"]["Drivers"] = self.load_drivers()
        config["UEFI"]["Quirks"]["IgnoreInvalidFlexRatio"] = not self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware.get("CPU Codename"), end=4) is None
        config["UEFI"]["Quirks"]["ReleaseUsbOwnership"] = True
        config["UEFI"]["Quirks"]["UnblockFsConnect"] = "HP" in hardware.get("Motherboard Name")
        config["UEFI"]["ReservedMemory"] = []

        return config