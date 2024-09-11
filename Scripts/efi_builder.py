from Scripts.datasets import cpu_data
from Scripts import acpi_guru
from Scripts import config_prodigy
from Scripts import kext_maestro
from Scripts import utils
import os
import shutil
import re

class builder:
    def __init__(self):
        self.acpi = acpi_guru.ACPIGuru()
        self.config = config_prodigy.ConfigProdigy()
        self.kext = kext_maestro.KextMaestro()
        self.utils = utils.Utils()
        self.oc_binary_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OcBinaryData")
        self.intel_igpu_properties = {
            "Ice Lake": {
                "Laptop": {
                    "AAPL,ig-platform-id": "0000528A",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Comet Lake": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "0300C89B",
                    "AAPL,ig-platform-id": "07009B3E",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "NUC": {
                    "AAPL,ig-platform-id": "07009B3E",
                    "device-id": "9B3E0000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "00009B3E",
                    "device-id": "9B3E0000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Coffee Lake": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "0300913E",
                    "AAPL,ig-platform-id": "07009B3E"
                },
                "NUC": {
                    "AAPL,ig-platform-id": "07009B3E",
                    "device-id": "9B3E0000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "0900A53E",
                    "device-id": "9B3E0000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Whiskey Lake": {
                "NUC": {
                    "AAPL,ig-platform-id": "07009B3E",
                    "device-id": "9B3E0000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "0900A53E",
                    "device-id": "9B3E0000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Amber Lake": {
                "Laptop": {
                    "AAPL,ig-platform-id": "0000C087",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Kaby Lake": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "03001259",
                    "AAPL,ig-platform-id": "00001259",
                    "device-id": "12590000"
                },
                "NUC": {
                    "AAPL,ig-platform-id": "00001659",
                    "device-id": "16590000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "00001B59",
                    "device-id": "1B590000",
                    "framebuffer-con1-alldata": "01050A00 00080000 87010000 02040A00 00080000 87010000 FF000000 01000000 20000000",
                    "framebuffer-con1-enable": "01000000",
                    "#framebuffer-con2-alldata": "01050A00 00080000 87010000 03060A00 00040000 87010000 FF000000 01000000 20000000",
                    "#framebuffer-con2-enable": "01000000",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Skylake": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "01001219",
                    "AAPL,ig-platform-id": "00001219"
                },
                "NUC": {
                    "AAPL,ig-platform-id": "05003B19",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "00001619",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Broadwell": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "07002216",
                    "AAPL,ig-platform-id": "07002216"
                },
                "NUC": {
                    "AAPL,ig-platform-id": "02001616",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "06002616",
                    "framebuffer-fbmem": "00009000",
                    "framebuffer-stolenmem": "00003001"
                }
            },
            "Haswell": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "04001204",
                    "AAPL,ig-platform-id": "0300220D"
                },
                "NUC": {
                    "AAPL,ig-platform-id": "0300220D",
                    "device-id": "12040000",
                    "framebuffer-cursormem": "00009000"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "0600260A",
                    "device-id": "12040000",
                    "framebuffer-cursormem": "00009000"
                }
            },
            "Ivy Bridge": {
                "Desktop": {
                    "AAPL,ig-platform-idEx": "07006201",
                    "AAPL,ig-platform-id": "0A006601"
                },
                "Laptop": {
                    "AAPL,ig-platform-id": "03006601"
                }
            },
            "Sandy Bridge": {
                "Desktop": {
                    "AAPL,snb-platform-idEx": "00000500",
                    "AAPL,snb-platform-id": "10000300",
                    "device-id": "26010000"
                },
                "Laptop": {
                    "AAPL,snb-platform-id": "00000100"
                }
            }
        }

    def is_low_end_intel_cpu(self, processor_name):
        return any(cpu_branding in processor_name for cpu_branding in ["Celeron", "Pentium"])
  
    def check_igpu_compatibility(self, cpu_codename, macos_version):
        return not (("Sandy Bridge" in cpu_codename and macos_version > (17, 0, 0)) or \
                    ("Ivy Bridge" in cpu_codename and macos_version > (20, 0, 0)) or \
                    (("Haswell" in cpu_codename or "Broadwell" in cpu_codename) and macos_version > (21, 0, 0)) or \
                    (("Skylake" in cpu_codename or "Kaby Lake" in cpu_codename) and macos_version > (22, 0, 0)) or \
                    (("Amber Lake" in cpu_codename or "Whiskey Lake" in cpu_codename) and macos_version == (17, 0, 0)) or \
                    ("Ice Lake" in cpu_codename and (19, 4, 0) > macos_version))

    def igpu_properties(self, platform, processor_name, gpu_codename, discrete_gpu, integrated_gpu_manufacturer, integrated_gpu_name, macos_version):
        if "Skylake".lower() in gpu_codename.lower() and macos_version > (21, 0, 0):
            gpu_codename = "Kaby Lake"
        if "Kaby Lake-R".upper() in gpu_codename.upper() and macos_version > (22, 0, 0):
            gpu_codename = "Coffee Lake"

        gpu_codename = self.utils.contains_any(cpu_data.IntelCPUGenerations, gpu_codename)
        if not "Intel" in integrated_gpu_manufacturer or not integrated_gpu_name or self.is_low_end_intel_cpu(processor_name) or not self.check_igpu_compatibility(gpu_codename, macos_version) or not self.intel_igpu_properties.get(gpu_codename, True):
            return {}
        
        igpu_properties = self.intel_igpu_properties[gpu_codename][platform]

        if "Desktop" in platform:
            if discrete_gpu:
                if "Sandy Bridge" in gpu_codename:
                    return {
                        "AAPL,snb-platform-id": igpu_properties["AAPL,snb-platform-idEx"],
                        "device-id": "02010000",
                    }
                else:
                    return {
                        "AAPL,ig-platform-id": igpu_properties["AAPL,ig-platform-idEx"]
                    }
            del igpu_properties["AAPL,ig-platform-idEx"]
            if "Haswell" in gpu_codename and not "440" in integrated_gpu_name:
                igpu_properties["device-id"] = "12040000"
            elif "Skylake" in gpu_codename and "P530" in integrated_gpu_name:
                igpu_properties["device-id"] = "12040000"
        else:
            if "Haswell" in gpu_codename and "5" in integrated_gpu_name:
                igpu_properties["AAPL,ig-platform-id"] = "0500260A"
                del igpu_properties["device-id"]
            elif "Broadwell" in gpu_codename and "56" in integrated_gpu_name:
                igpu_properties["device-id"] = "26160000"
            elif "Skylake" in gpu_codename:
                if "NUC" in platform:
                    if "51" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "00001E19"
                    elif "52" in integrated_gpu_name or "53" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "02001619"
                    elif "54" in integrated_gpu_name or "55" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "02002619"

                if "510" in integrated_gpu_name:
                    igpu_properties["AAPL,ig-platform-id"] = "00001B19"
                    igpu_properties["device-id"] = "02190000"
                elif "550" in integrated_gpu_name or "P530" in integrated_gpu_name:
                    igpu_properties["device-id"] = "16190000"
            elif "Kaby Lake" in gpu_codename:
                if "NUC" in platform:
                    if "15" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "00001E59"
                    elif "63" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "00001B59"
                    elif "40" in integrated_gpu_name or "65" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "02002659"
                else:
                    if "UHD" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "0000C087"
                        igpu_properties["device-id"] = "16590000"
            elif self.utils.contains_any(cpu_data.IntelCPUGenerations, gpu_codename, start=8, end=11):
                if "NUC" in platform:
                    if "55" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "0000A53E"
                        del igpu_properties["device-id"]
                else:
                    if "3" in integrated_gpu_name:
                        igpu_properties["AAPL,ig-platform-id"] = "0900A53E"

        igpu_properties["hda-gfx"] = "onboard-1"
        igpu_properties["framebuffer-patch-enable"] = "01000000"
        return igpu_properties   

    def system_product_info(self, platform, cpu_manufacturer, processor_name, cpu_codename, cpu_cores, discrete_gpu, igpu_props, macos_version):
        product_name = "iMacPro1,1" if macos_version < (19, 0, 0) or self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=12) else "MacPro7,1"

        if "AMD" in cpu_manufacturer and not discrete_gpu:
            product_name = "MacBookPro16,3" if "Laptop" in platform else "iMacPro1,1"

        if igpu_props:
            if "Kaby Lake-R".lower() in cpu_codename.lower() and macos_version > (22, 0, 0):
                cpu_codename = "Coffee Lake"

            if "Sandy Bridge" in cpu_codename:
                if "Desktop" in platform:
                    if macos_version < (18, 0, 0):
                        product_name = "iMac12,2"
                    else:
                        product_name = "MacPro6,1"
                elif "NUC" in platform:
                    product_name = "Macmini5,1" if int(cpu_cores) < 4 else "Macmini5,3"
                else:
                    product_name = "MacBookPro8,1" if int(cpu_cores) < 4 else "MacBookPro8,2"
            elif "Ivy Bridge" in cpu_codename:
                if macos_version == (20, 0, 0):
                    if "Desktop" in platform:
                        product_name = "iMac14,4" if not discrete_gpu else "iMac15,1"
                    elif "NUC" in platform:
                        product_name = "Macmini7,1"
                    else:
                        product_name = "MacBookPro11,1" if int(cpu_cores) < 4 else "MacBookPro11,5"
                elif macos_version < (20, 0, 0):
                    if "Desktop" in platform:
                        product_name = "iMac13,1" if not discrete_gpu else "iMac13,2"
                    elif "NUC" in platform:
                        product_name = "Macmini6,1" if int(cpu_cores) < 4 else "Macmini6,2"
                    else:
                        product_name = "MacBookPro10,2" if int(cpu_cores) < 4 else "MacBookPro10,1"
                else:
                    product_name = "MacPro6,1"
            elif "Haswell" in cpu_codename:
                if "Desktop" in platform:
                    product_name = "iMac14,4" if not discrete_gpu else "iMac15,1"
                    if macos_version == (21, 0, 0):
                        product_name = "iMac16,2" if not discrete_gpu else "iMac17,1"
                elif "NUC" in platform:
                    product_name = "Macmini7,1"
                else:
                    product_name = "MacBookPro11,1" if macos_version < (21, 0, 0) and int(cpu_cores) < 4 else "MacBookPro11,5"
            elif "Broadwell" in cpu_codename:
                if "Desktop" in platform:
                    product_name = "iMac16,2" if not discrete_gpu else "iMac17,1"
                elif "NUC" in platform:
                    product_name = "iMac16,1"
                else:
                    product_name = "MacBookPro12,1" if int(cpu_cores) < 4 else "MacBookPro11,5"
            elif "Skylake" in cpu_codename:
                product_name = "iMac17,1"
                if "Laptop" in platform:
                    product_name = "MacBookPro13,1" if int(cpu_cores) < 4 else "MacBookPro13,3"
            elif self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=8, end=11):
                product_name = "Macmini8,1"
                if "Desktop" in platform:
                    product_name = "iMac18,3" if macos_version == (17, 0, 0) else "iMac19,1"
                    if "Comet Lake" in cpu_codename:
                        product_name = "iMac20,1" if int(cpu_cores) < 10 else "iMac20,2"
                elif "Laptop" in platform:
                    if "-8" in processor_name:
                        product_name = "MacBookPro15,2" if int(cpu_cores) < 6 else "MacBookPro15,3"
                    else:
                        product_name = "MacBookPro16,3" if int(cpu_cores) < 6 else "MacBookPro16,1"
            elif "Kaby Lake" in cpu_codename:
                product_name = "iMac18,1" if not discrete_gpu else "iMac18,3"
                if "Laptop" in platform:
                    product_name = "MacBookPro14,1" if int(cpu_cores) < 4 else "MacBookPro14,3"
            elif "Amber Lake" in cpu_codename:
                product_name = "MacBookAir8,1"
            elif "Ice Lake" in cpu_codename:
                product_name = "MacBookAir9,1" if int(cpu_cores) < 4 else "MacBookPro16,2"

        return product_name

    def clean_up(self, config, efi_directory):
        files_to_remove = []

        drivers_directory = os.path.join(efi_directory, "EFI", "OC", "Drivers")
        driver_list = self.utils.find_matching_paths(drivers_directory, ".efi")
        driver_loaded = [kext.get("Path") for kext in config.get("UEFI").get("Drivers")]
        for driver_path in driver_list:
            if not driver_path in driver_loaded:
                files_to_remove.append(os.path.join(drivers_directory, driver_path))

        kexts_directory = os.path.join(efi_directory, "EFI", "OC", "Kexts")
        kext_list = self.utils.find_matching_paths(kexts_directory, ".kext")
        kext_loaded = [os.path.basename(kext.get("BundlePath")) for kext in config.get("Kernel").get("Add")]
        for kext_path in kext_list:
            if not os.path.basename(kext_path) in kext_loaded:
                files_to_remove.append(os.path.join(kexts_directory, kext_path))

        tools_directory = os.path.join(efi_directory, "EFI", "OC", "Tools")
        tool_list = self.utils.find_matching_paths(tools_directory, ".efi")
        tool_loaded = [tool.get("Path") for tool in config.get("Misc").get("Tools")]
        for tool_path in tool_list:
            if not tool_path in tool_loaded:
                files_to_remove.append(os.path.join(tools_directory, tool_path))

        error = None
        for path in files_to_remove:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                error = True
                print("\nFailed to remove file: {}".format(e), end="")
                continue

        if error:
            print("")
            self.utils.request_input()

    def build_efi(self, hardware, macos_version):
        efi_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Results")
        
        self.utils.mkdirs(efi_directory)
        
        if not os.path.exists(self.kext.ock_files_dir):
            raise Exception("Directory '{}' does not exist.".format(self.kext.ock_files_dir))
        
        source_efi_dir = os.path.join(self.kext.ock_files_dir, "OpenCore")
        shutil.copytree(source_efi_dir, efi_directory, dirs_exist_ok=True)
        shutil.copytree(self.oc_binary_data_dir, os.path.join(efi_directory, "EFI", "OC"), dirs_exist_ok=True)

        hardware_shorc = {}
        hardware_shorc["Motherboard Name"] = hardware["Motherboard"].get("Motherboard Name").upper()
        hardware_shorc["Motherboard Chipset"] = hardware["Motherboard"].get("Motherboard Chipset").upper()
        hardware_shorc["Platform"] = hardware["Motherboard"].get("Platform")
        hardware_shorc["CPU Configuration"] = hardware["CPU"].get("CPU Configuration")
        hardware_shorc["CPU Manufacturer"] = hardware["CPU"].get("CPU Manufacturer")
        hardware_shorc["Processor Name"] = hardware["CPU"].get("Processor Name")
        hardware_shorc["CPU Cores"] = hardware["CPU"].get("CPU Cores")
        hardware_shorc["CPU Codename"] = hardware["CPU"].get("CPU Codename")
        hardware_shorc["Instruction Set"] = hardware["CPU"].get("Instruction Set")
        hardware_shorc["Integrated GPU"] = list(hardware.get("GPU").items())[-1][1] if "Integrated GPU" in list(hardware.get("GPU").items())[-1][1]["Device Type"] else {}
        hardware_shorc["Integrated GPU Name"] = list(hardware.get("GPU").keys())[-1] if hardware_shorc["Integrated GPU"] else ""
        hardware_shorc["Discrete GPU"] = list(hardware.get("GPU").items())[0][1].copy() if "Discrete GPU" in list(hardware.get("GPU").items())[0][1]["Device Type"] else {}
        if hardware_shorc["Discrete GPU"]:
            hardware_shorc["Discrete GPU"]["GPU Name"] = list(hardware.get("GPU").keys())[0]
        hardware_shorc["Network"] = hardware.get("Network")
        hardware_shorc["Bluetooth"] = [device_props.get("Device ID") for device_name, device_props in hardware.get("Bluetooth", {}).items()]
        hardware_shorc["Codec ID"] = next((device_props.get("Codec ID") for device_name, device_props in hardware.get("Audio").items()), None)
        hardware_shorc["SD Controller"] = hardware.get("SD Controller")
        hardware_shorc["Input"] = hardware.get("Input")
        hardware_shorc["Storage Controllers"] = hardware.get("Storage Controllers")
        hardware_shorc["Intel MEI"] = hardware.get("Intel MEI")
        hardware_shorc["Unsupported Devices"] = hardware.get("Compatibility").get("Unsupported Devices")

        forbidden_chars = r'[<>:"/\\|?*]'
        hardware_shorc["Motherboard Name"] = re.sub(forbidden_chars, '_', hardware_shorc["Motherboard Name"])

        efi_option = {}
        efi_option["macOS Version"] = macos_version
        efi_option["Custom CPU Name"] = not (" Core" in hardware_shorc.get("Processor Name") and self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware_shorc.get("CPU Codename"), end=12))
        efi_option["Synchronize the TSC"] = "Laptop" in hardware_shorc["Platform"] and "ASUS" in hardware_shorc["Motherboard Name"] or "AMD" in hardware_shorc["Integrated GPU"].get("Manufacturer", "") or self.config.is_intel_hedt_cpu(hardware_shorc["CPU Codename"])
        efi_option["iGPU Properties"] = self.igpu_properties(
            hardware_shorc["Platform"], 
            hardware_shorc.get("Processor Name"), 
            hardware_shorc["Integrated GPU"].get("GPU Codename", ""), 
            hardware_shorc["Discrete GPU"], 
            hardware_shorc["Integrated GPU"].get("Manufacturer", ""), 
            hardware_shorc["Integrated GPU Name"], 
            efi_option.get("macOS Version"))
        efi_option["SMBIOS"] = self.system_product_info(
            hardware_shorc["Platform"], 
            hardware_shorc["CPU Manufacturer"], 
            hardware_shorc.get("Processor Name"), 
            hardware_shorc["CPU Codename"], 
            hardware_shorc["CPU Cores"],
            hardware_shorc["Discrete GPU"], 
            efi_option["iGPU Properties"],
            efi_option.get("macOS Version"))

        input_devices = ", ".join(list(hardware_shorc.get("Input", {}).keys()))
        hardware_shorc["Touchpad Communication"] = "None" if not "Laptop" in hardware_shorc.get("Platform") else "I2C" if "I2C" in input_devices else "PS2" if "PS2" in input_devices else "None"
        efi_option["ACPI"] = self.acpi.initialize_patches(
            hardware_shorc["Motherboard Name"],
            hardware_shorc["Motherboard Chipset"],
            hardware_shorc["Platform"],
            hardware_shorc["CPU Manufacturer"],
            hardware_shorc["CPU Codename"],
            hardware_shorc["Integrated GPU"],
            hardware_shorc["Discrete GPU"],
            hardware_shorc["Network"],
            hardware_shorc["Touchpad Communication"],
            efi_option.get("SMBIOS"),
            hardware_shorc.get("Intel MEI"),
            hardware_shorc["Unsupported Devices"],
            efi_option.get("macOS Version"),
            os.path.join(efi_directory, "EFI", "OC", "ACPI")
        )
        
        kexts = self.kext.gathering_kexts(
            hardware_shorc["Motherboard Name"], 
            hardware_shorc["Platform"], 
            hardware_shorc["CPU Configuration"], 
            hardware_shorc["CPU Manufacturer"], 
            hardware_shorc["CPU Codename"], 
            hardware_shorc["CPU Cores"], 
            hardware_shorc["Instruction Set"], 
            hardware_shorc["Discrete GPU"].get("GPU Codename", ""), 
            hardware_shorc["Integrated GPU"], 
            hardware_shorc.get("Network"), 
            hardware_shorc.get("Bluetooth"), 
            hardware_shorc.get("Codec ID"), 
            hardware_shorc["Input"], 
            hardware_shorc.get("SD Controller"), 
            hardware_shorc.get("Storage Controllers"), 
            hardware.get("USB Controllers"), 
            efi_option.get("SMBIOS"),
            efi_option.get("Custom CPU Name"),
            efi_option.get("Synchronize the TSC"),
            efi_option.get("ACPI"),
            efi_option.get("macOS Version")
        )

        kexts_directory = os.path.join(efi_directory, "EFI", "OC", "Kexts")
        self.kext.install_kexts_to_efi(kexts, efi_option.get("macOS Version"), kexts_directory)
        efi_option["Kernel_Add"] = self.kext.load_kexts(
            kexts, 
            hardware_shorc["Motherboard Name"], 
            hardware_shorc["Platform"],
            hardware_shorc["CPU Manufacturer"],
            hardware_shorc["Discrete GPU"].get("GPU Codename", ""),
            efi_option["macOS Version"]
        )
        
        config_file = os.path.join(efi_directory, "EFI", "OC", "config.plist")
        config_data = self.utils.read_file(config_file)
        
        if not config_data:
            raise Exception("Error: The file {} does not exist.".format(config_file))
        
        self.config.genarate(hardware_shorc, efi_option, config_data)
        self.utils.write_file(config_file, config_data)

        self.clean_up(config_data, efi_directory)
        hardware_file = os.path.join(efi_directory, hardware_shorc.get("Motherboard Name") + ".json")
        self.utils.write_file(hardware_file, hardware)