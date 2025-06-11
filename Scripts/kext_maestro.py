from Scripts.datasets import cpu_data
from Scripts.datasets import kext_data
from Scripts.datasets import os_data
from Scripts.datasets import pci_data
from Scripts.datasets import codec_layouts
from Scripts import utils
import os
import shutil

try:
    long
    unicode
except NameError:
    long = int
    unicode = str

class KextMaestro:
    def __init__(self):
        self.utils = utils.Utils()
        self.matching_keys = [
            "IOPCIMatch", 
            "IONameMatch", 
            "IOPCIPrimaryMatch", 
            "idProduct", 
            "idVendor", 
            "HDAConfigDefault"
        ]
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.kexts = kext_data.kexts
        
    def extract_pci_id(self, kext_path):
        if not os.path.exists(kext_path):
            return []

        plist_path = os.path.join(kext_path, "Contents", "Info.plist")
        plist_data = self.utils.read_file(plist_path)

        pci_ids = []

        for personality_name, properties in plist_data.get("IOKitPersonalities", {}).items():
            matching_keys = [key for key in self.matching_keys if key in properties]
            
            if not matching_keys:
                continue
            
            match_key = matching_keys[0]

            if match_key in ["IOPCIMatch", "IOPCIPrimaryMatch"]:
                pci_list = properties[match_key].split(" ")
                for pci_id in pci_list:
                    vendor_id = pci_id[-4:]
                    device_id = pci_id[2:6]
                    pci_ids.append("{}-{}".format(vendor_id, device_id).upper())
            elif match_key == "IONameMatch":
                for pci_id in properties[match_key]:
                    vendor_id = pci_id[3:7]
                    device_id = pci_id.split(",")[1].zfill(4)
                    pci_ids.append("{}-{}".format(vendor_id, device_id).upper())
            elif match_key == "idProduct":
                vendor_id = self.utils.int_to_hex(properties["idVendor"]).zfill(4)
                device_id = self.utils.int_to_hex(properties["idProduct"]).zfill(4)
                pci_ids.append("{}-{}".format(vendor_id, device_id).upper())
            elif match_key == "HDAConfigDefault":
                for codec_layout in properties[match_key]:
                    codec_id = self.utils.int_to_hex(codec_layout.get("CodecID")).zfill(8)
                    pci_ids.append("{}-{}".format(codec_id[:4], codec_id[-4:]))
                pci_ids = sorted(list(set(pci_ids)))

        return pci_ids

    def is_intel_hedt_cpu(self, processor_name, cpu_codename):
        if cpu_codename in cpu_data.IntelCPUGenerations[45:66]:
            return cpu_codename.endswith(("-X", "-P", "-W", "-E", "-EP", "-EX"))
        
        if cpu_codename in cpu_data.IntelCPUGenerations[66:]:
            return "Xeon" in processor_name
        
        return False

    def check_kext(self, index, target_darwin_version, allow_unsupported_kexts=False):
        kext = self.kexts[index]

        if kext.checked or not (allow_unsupported_kexts or self.utils.parse_darwin_version(kext.min_darwin_version) <= self.utils.parse_darwin_version(target_darwin_version) <= self.utils.parse_darwin_version(kext.max_darwin_version)):
            return

        kext.checked = True

        for requires_kext_name in kext.requires_kexts:
            requires_kext_index = kext_data.kext_index_by_name.get(requires_kext_name)
            if requires_kext_index:
                self.check_kext(requires_kext_index, target_darwin_version, allow_unsupported_kexts)

        if kext.conflict_group_id:
            for other_kext in self.kexts:
                if other_kext.conflict_group_id == kext.conflict_group_id and other_kext.name != kext.name:
                    other_kext.checked = False

    def select_required_kexts(self, hardware_report, macos_version, needs_oclp, acpi_patches):
        self.utils.head("Select Required Kernel Extensions")
        print("")
        print("Checking for required kernel extensions...")

        for kext in self.kexts:
            kext.checked = kext.required

        selected_kexts = []

        if "Intel" in hardware_report.get("CPU").get("Manufacturer"):
            selected_kexts.extend(("SMCProcessor", "SMCSuperIO"))

        if "Laptop" in hardware_report.get("Motherboard").get("Platform") and not "SURFACE" in hardware_report.get("Motherboard").get("Name"):
            selected_kexts.append("SMCBatteryManager")
            if "DELL" in hardware_report.get("Motherboard").get("Name"):
                selected_kexts.append("SMCDellSensors")
            selected_kexts.append("SMCLightSensor")

        if  not (" Core" in hardware_report.get("CPU").get("Processor Name") and \
                 hardware_report.get("CPU").get("Codename") in cpu_data.IntelCPUGenerations[28:]) or \
            self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
            selected_kexts.append("RestrictEvents")

        for codec_properties in hardware_report.get("Sound", {}).values():
            if codec_properties.get("Device ID") in codec_layouts.data:
                selected_kexts.append("AppleALC")
        
        if "AMD" in hardware_report.get("CPU").get("Manufacturer") and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("21.4.0") or \
            int(hardware_report.get("CPU").get("CPU Count")) > 1 and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("19.0.0"):
            selected_kexts.append("AppleMCEReporterDisabler")

        if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("22.0.0") and not "AVX2" in hardware_report.get("CPU").get("SIMD Features"):
            selected_kexts.append("CryptexFixup")

        if  "Lunar Lake" not in hardware_report.get("CPU").get("Codename") and \
            "Meteor Lake" not in hardware_report.get("CPU").get("Codename") and \
            hardware_report.get("CPU").get("Codename") in cpu_data.IntelCPUGenerations[:20] and \
            int(hardware_report.get("CPU").get("Core Count")) > 6:
            selected_kexts.append("CpuTopologyRebuild")

        for gpu_name, gpu_props in hardware_report.get("GPU", {}).items():
            if "Integrated GPU" in gpu_props.get("Device Type"):
                if "AMD" in gpu_props.get("Manufacturer"):
                    selected_kexts.append("NootedRed")
            else:
                if "Navi 22" in gpu_props.get("Codename"):
                    selected_kexts.append("NootRX")
                elif gpu_props.get("Codename") in {"Navi 21", "Navi 23"}:
                    print("\n*** Found {} is AMD {} GPU.".format(gpu_name, gpu_props.get("Codename")))
                    print("")
                    print("\033[91mImportant: Black Screen Fix\033[0m")
                    print("If you experience a black screen after verbose mode:")
                    print("    1. Use ProperTree to open config.plist")
                    print("    2. Navigate to NVRAM -> Add -> 7C436110-AB2A-4BBB-A880-FE41995C9F82 -> boot-args")
                    print("    3. Remove \"-v debug=0x100 keepsyms=1\" from boot-args")
                    print("")
                    print("\033[93mNote:\033[0m - AMD {} GPUs have two available kext options:".format(gpu_props.get("Codename")))
                    print("      - You can try different kexts after installation to find the best one for your system")
                    print("")
                    print("1. \033[1mNootRX\033[0m - Uses latest GPU firmware")
                    print("2. \033[1mWhateverGreen\033[0m - Uses original Apple firmware")
                    print("")

                    if any(other_gpu_props.get("Manufacturer") == "Intel" for other_gpu_props in hardware_report.get("GPU", {}).values()):
                        print("\033[91mImportant:\033[0m - NootRX kext is not compatible with Intel GPUs")
                        print("      - Automatically selecting WhateverGreen kext due to Intel GPU compatibility")
                        print("")
                        self.utils.request_input("Press Enter to continue...")
                        continue

                    recommended_option = 2
                    recommended_name = "WhateverGreen"

                    kext_option = self.utils.request_input("Select kext for your AMD {} GPU (default: {}): ".format(gpu_props.get("Codename"), recommended_name)).strip() or str(recommended_option)
                    
                    if kext_option.isdigit() and 0 < int(kext_option) < 3:
                        selected_option = int(kext_option)
                    else:
                        print("\033[91mInvalid selection, using recommended option: {}\033[0m".format(recommended_option))
                        selected_option = recommended_option

                    if selected_option == 2:
                        selected_kexts.append("WhateverGreen")
                    else:
                        selected_kexts.append("NootRX")
                elif gpu_props.get("Codename").startswith("Navi 1"):
                    selected_kexts.append("WhateverGreen")

        if not "NootedRed" in selected_kexts and not "NootRX" in selected_kexts and not "WhateverGreen" in selected_kexts:
            selected_kexts.append("WhateverGreen")

        if "Laptop" in hardware_report.get("Motherboard").get("Platform") and ("ASUS" in hardware_report.get("Motherboard").get("Name") or "NootedRed" in selected_kexts):
            selected_kexts.append("ForgedInvariant")

        if self.is_intel_hedt_cpu(hardware_report.get("CPU").get("Processor Name"), hardware_report.get("CPU").get("Codename")):
            selected_kexts.append("CpuTscSync")

        if needs_oclp:
            selected_kexts.extend(("AMFIPass", "RestrictEvents"))

        for network_name, network_props in hardware_report.get("Network", {}).items():
            device_id = network_props.get("Device ID")

            if device_id in pci_data.BroadcomWiFiIDs and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
                selected_kexts.append("IOSkywalkFamily")

            if device_id in pci_data.BroadcomWiFiIDs[:15]:
                selected_kexts.append("AirportBrcmFixup")
            elif device_id == pci_data.BroadcomWiFiIDs[15] and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("19.0.0"):
                selected_kexts.append("AirportBrcmFixup")
            elif device_id in pci_data.BroadcomWiFiIDs[16:18] and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("20.0.0"):
                selected_kexts.append("AirportBrcmFixup")
            elif device_id in pci_data.IntelWiFiIDs:
                print("\n*** Found {} is Intel WiFi device.".format(network_name))
                print("")
                print("\033[93mNote:\033[0m Intel WiFi devices have two available kext options:")
                print("")
                print("1. \033[1mAirportItlwm\033[0m - Uses native WiFi settings menu")
                print("   • Provides Handoff, Universal Clipboard, Location Services, Instant Hotspot support")
                print("   • Supports enterprise-level security")

                if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("24.0.0"):
                    print("   • \033[91mSince macOS Sequoia 15\033[0m: Can work with OCLP root patch but may cause issues")
                elif self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
                    print("   • \033[91mOn macOS Sonoma 14\033[0m: iServices won't work unless using OCLP root patch")
                
                print("")
                print("2. \033[1mitlwm\033[0m - More stable overall")
                print("   • Works with HeliPort app instead of native WiFi settings menu")
                print("   • No Apple Continuity features and enterprise-level security")
                print("   • Can connect to Hidden Networks")
                print("")

                recommended_option = 2 if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0") else 1
                recommended_name = "itlwm" if recommended_option == 2 else "AirportItlwm"

                if "Beta" in os_data.get_macos_name_by_darwin(macos_version):
                    print("\033[91mImportant:\033[0m For macOS Beta versions, only itlwm kext is supported")
                    print("")
                    self.utils.request_input("Press Enter to continue...")
                    selected_option = recommended_option
                else:
                    kext_option = self.utils.request_input("Select kext for your Intel WiFi device (default: {}): ".format(recommended_name)).strip() or str(recommended_option)
                    
                    if kext_option.isdigit() and 0 < int(kext_option) < 3:
                        selected_option = int(kext_option)
                    else:
                        print("\033[91mInvalid selection, using recommended option: {}\033[0m".format(recommended_option))
                        selected_option = recommended_option
                
                if selected_option == 2:
                    selected_kexts.append("itlwm")
                else:
                    selected_kexts.append("AirportItlwm")
                    
                    if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("24.0.0"):
                        selected_kexts.append("IOSkywalkFamily")
                    elif self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
                        print("")
                        print("\033[93mNote:\033[0m Since macOS Sonoma 14, iServices won't work with AirportItlwm without patches")
                        print("")
                        option = self.utils.request_input("Apply OCLP root patch to fix iServices? (y/N): ").strip().lower() or "n"
                        
                        if option == "y":
                            selected_kexts.append("IOSkywalkFamily")
            elif device_id in pci_data.AtherosWiFiIDs[:8]:
                selected_kexts.append("corecaptureElCap")
                if self.utils.parse_darwin_version(macos_version) > self.utils.parse_darwin_version("20.99.99"):
                    selected_kexts.append("AMFIPass")
            elif device_id in pci_data.IntelI22XIDs:
                selected_kexts.append("AppleIGC")
            elif device_id in pci_data.AtherosE2200IDs:
                selected_kexts.append("AtherosE2200Ethernet")
            elif device_id in pci_data.IntelMausiIDs:
                selected_kexts.append("IntelMausiEthernet")
            elif device_id in pci_data.RealtekRTL8125IDs:
                selected_kexts.append("LucyRTL8125Ethernet")
            elif device_id in pci_data.RealtekRTL8100IDs:
                selected_kexts.append("RealtekRTL8100")
            elif device_id in pci_data.RealtekRTL8111IDs:
                selected_kexts.append("RealtekRTL8111")
            elif device_id in pci_data.AppleIGBIDs:
                selected_kexts.append("AppleIGB")
            elif device_id in pci_data.BroadcomBCM57XXIDs:
                selected_kexts.append("CatalinaBCM5701Ethernet")
            elif device_id in pci_data.IntelX500IDs:
                selected_kexts.append("IntelLucy")

        if not hardware_report.get("Network"):
            selected_kexts.append("NullEthernet")

        for bluetooth_name, bluetooth_props in hardware_report.get("Bluetooth", {}).items():
            usb_id = bluetooth_props.get("Device ID")

            if usb_id in pci_data.AtherosBluetoothIDs:
                selected_kexts.extend(("Ath3kBT", "Ath3kBTInjector"))
            elif usb_id in pci_data.BroadcomBluetoothIDs:               
                selected_kexts.append("BrcmFirmwareData")
            elif usb_id in pci_data.IntelBluetoothIDs:
                selected_kexts.append("IntelBluetoothFirmware")
            elif usb_id in pci_data.BluetoothIDs[-1]:
                selected_kexts.append("BlueToolFixup")

        if "Laptop" in hardware_report.get("Motherboard").get("Platform"):
            if "SURFACE" in hardware_report.get("Motherboard").get("Name"):
                selected_kexts.append("BigSurface")
            else:
                if "ASUS" in hardware_report.get("Motherboard").get("Name"):
                    selected_kexts.append("AsusSMC")
                selected_kexts.append("BrightnessKeys")

                for device_name, device_props in hardware_report.get("Input").items():
                    if not device_props.get("Device"):
                        continue

                    device_id = device_props.get("Device")
                    idx = None
                    if device_id in pci_data.InputIDs:
                        idx = pci_data.InputIDs.index(device_id)

                    if "PS/2" in device_props.get("Device Type", "None"):
                        selected_kexts.append("VoodooPS2Controller")
                        if device_id.startswith("SYN"):
                            selected_kexts.append("VoodooRMI")
                        elif idx and 75 < idx < 79:
                            selected_kexts.append("VoodooSMBus")
                    if "I2C" in device_props.get("Device Type", "None"):
                        selected_kexts.append("VoodooI2CHID")
                        if idx:
                            if idx < 76:
                                selected_kexts.append("AlpsHID")
                            elif 78 < idx:
                                selected_kexts.append("VoodooRMI")
        
        for device_name, device_info in hardware_report.get("System Devices", {}).items():
            if device_info.get("Bus Type") == "ACPI" and device_info.get("Device") in pci_data.YogaHIDs:
                selected_kexts.append("YogaSMC")

        if any(patch.checked for patch in acpi_patches if patch.name == "BATP"):
            selected_kexts.append("ECEnabler")

        for controller_name, controller_props in hardware_report.get("SD Controller", {}).items():
            if controller_props.get("Device ID") in pci_data.RealtekCardReaderIDs:
                if controller_props.get("Device ID") in pci_data.RealtekCardReaderIDs[5:]:
                    selected_kexts.append("Sinetek-rtsx")
                else:
                    selected_kexts.append("RealtekCardReader")
        
        for controller_name, controller_props in hardware_report.get("Storage Controllers", {}).items():
            if "NVMe" in controller_name or "NVM Express" in controller_name:
                selected_kexts.append("NVMeFix")
            elif not "AHCI" in controller_name:
                if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("20.0.0"):
                    if controller_props.get("Device ID") in pci_data.UnsupportedSATAControllerIDs:
                        selected_kexts.append("CtlnaAHCIPort")
                else:
                    if controller_props.get("Device ID") in pci_data.UnsupportedSATAControllerIDs[15:]:
                        selected_kexts.append("SATA-unsupported")

        for controller_name, controller_props in hardware_report.get("USB Controllers").items():
            device_id = controller_props.get("Device ID")
            if device_id in pci_data.UnsupportedUSBControllerIDs:
                idx = pci_data.UnsupportedUSBControllerIDs.index(device_id)
                if idx == 0:
                    if "Laptop" in hardware_report.get("Motherboard").get("Platform"):
                        selected_kexts.append("GenericUSBXHCI")
                else:
                    selected_kexts.append("XHCI-unsupported")

        if "Sandy Bridge" in hardware_report.get("CPU").get("Codename"):
            selected_kexts.append("ASPP-Override")

        if "Sandy Bridge" in hardware_report.get("CPU").get("Codename") or "Ivy Bridge" in hardware_report.get("CPU").get("Codename"):
            selected_kexts.extend(("AppleIntelCPUPowerManagement", "AppleIntelCPUPowerManagementClient"))

        for name in selected_kexts:
            self.check_kext(kext_data.kext_index_by_name.get(name), macos_version, "Beta" in os_data.get_macos_name_by_darwin(macos_version))

    def install_kexts_to_efi(self, macos_version, kexts_directory):
        for kext in self.kexts:
            if kext.checked:
                try:
                    source_kext_path = destination_kext_path = None

                    kext_paths = self.utils.find_matching_paths(self.ock_files_dir, extension_filter=".kext", name_filter=kext.name)
                    for kext_path, type in kext_paths:
                        if "AirportItlwm" == kext.name:
                            version = macos_version[:2]
                            if all((self.kexts[kext_data.kext_index_by_name.get("IOSkywalkFamily")].checked, self.kexts[kext_data.kext_index_by_name.get("IO80211FamilyLegacy")].checked)) or self.utils.parse_darwin_version("24.0.0") <= self.utils.parse_darwin_version(macos_version):
                                version = "22"
                            elif self.utils.parse_darwin_version("23.4.0") <= self.utils.parse_darwin_version(macos_version):
                                version = "23.4"
                            elif self.utils.parse_darwin_version("23.0.0") <= self.utils.parse_darwin_version(macos_version):
                                version = "23.0"
                            
                            if version in kext_path:
                                source_kext_path = os.path.join(self.ock_files_dir, kext_path)
                                destination_kext_path = os.path.join(kexts_directory, os.path.basename(kext_path))
                                break
                        else:
                            main_kext = kext_path.split("/")[0]
                            main_kext_index = kext_data.kext_index_by_name.get(main_kext)
                            if not main_kext_index or self.kexts[main_kext_index].checked:
                                if os.path.splitext(os.path.basename(kext_path))[0] in kext.name:
                                    source_kext_path = os.path.join(self.ock_files_dir, kext_path)
                                    destination_kext_path = os.path.join(kexts_directory, os.path.basename(kext_path))
                    
                    if os.path.exists(source_kext_path):
                        shutil.copytree(source_kext_path, destination_kext_path, dirs_exist_ok=True)
                except:
                    continue

    def process_kext(self, kexts_directory, kext_path):
        try:
            plist_path = self.utils.find_matching_paths(os.path.join(kexts_directory, kext_path), extension_filter=".plist", name_filter="Info")[0][0]
            bundle_info = self.utils.read_file(os.path.join(kexts_directory, kext_path, plist_path))

            if isinstance(bundle_info.get("CFBundleIdentifier", None), (str, unicode)):
                pass
        except:
            return None

        executable_path = os.path.join("Contents", "MacOS", bundle_info.get("CFBundleExecutable", "None"))
        if not os.path.exists(os.path.join(kexts_directory, kext_path, executable_path)):
            executable_path = ""
        
        return {
            "BundlePath": kext_path.replace("\\", "/").lstrip("/"),
            "Enabled": True,
            "ExecutablePath": executable_path.replace("\\", "/").lstrip("/"),
            "PlistPath": plist_path.replace("\\", "/").lstrip("/"),
            "BundleIdentifier": bundle_info.get("CFBundleIdentifier"),
            "BundleVersion": bundle_info.get("CFBundleVersion"),
            "BundleLibraries": {
                bundle_identifier: bundle_version
                for bundle_identifier, bundle_version in bundle_info.get("OSBundleLibraries", {}).items() 
            }
        }

    def modify_kexts(self, plist_path, hardware_report, macos_version):
        try:
            bundle_info = self.utils.read_file(plist_path)

            if bundle_info.get("IOKitPersonalities").get("itlwm").get("WiFiConfig"):
                from Scripts import wifi_profile_extractor
                
                wifi_profiles = wifi_profile_extractor.WifiProfileExtractor().get_profiles()

                if wifi_profiles:
                    bundle_info["IOKitPersonalities"]["itlwm"]["WiFiConfig"] = {
                        "WiFi_{}".format(index): {
                            "password": profile[1],
                            "ssid": profile[0]
                        }
                        for index, profile in enumerate(wifi_profiles, start=1)
                    }
            elif bundle_info.get("IOKitPersonalities").get("VoodooTSCSync"):
                bundle_info["IOKitPersonalities"]["VoodooTSCSync"]["IOPropertyMatch"]["IOCPUNumber"] = 0 if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("21.0.0") else int(hardware_report["CPU"]["Core Count"]) - 1
            elif bundle_info.get("IOKitPersonalities").get("AmdTscSync"):
                bundle_info["IOKitPersonalities"]["AmdTscSync"]["IOPropertyMatch"]["IOCPUNumber"] = 0 if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("21.0.0") else int(hardware_report["CPU"]["Core Count"]) - 1
            else:
                return
            
            self.utils.write_file(plist_path, bundle_info)
        except:
            return            
        
    def load_kexts(self, hardware_report, macos_version, kexts_directory):
        kernel_add = []
        unload_kext = []

        if self.kexts[kext_data.kext_index_by_name.get("IO80211ElCap")].checked:
            unload_kext.extend((
                "AirPortBrcm4331",
                "AppleAirPortBrcm43224"
            ))
        elif self.kexts[kext_data.kext_index_by_name.get("VoodooSMBus")].checked:
            unload_kext.append("VoodooPS2Mouse")
        elif self.kexts[kext_data.kext_index_by_name.get("VoodooRMI")].checked:
            if not self.kexts[kext_data.kext_index_by_name.get("VoodooI2C")].checked:
                unload_kext.append("RMII2C")
            else:
                unload_kext.extend((
                    "VoodooSMBus",
                    "RMISMBus",
                    "VoodooI2CHID"
                ))

        kext_paths = self.utils.find_matching_paths(kexts_directory, extension_filter=".kext")
        bundle_list = []

        for kext_path, type in kext_paths:
            bundle_info = self.process_kext(kexts_directory, kext_path)

            if bundle_info:
                self.modify_kexts(os.path.join(kexts_directory, kext_path, bundle_info.get("PlistPath")), hardware_report, macos_version)

                bundle_list.append(bundle_info)

        bundle_dict = {bundle["BundleIdentifier"]: bundle for bundle in bundle_list}

        sorted_bundles = []
        
        visited = set()
        seen_identifier = set()

        def visit(bundle):
            if os.path.splitext(os.path.basename(bundle.get("BundlePath")))[0] in unload_kext or (bundle.get("BundlePath"), bundle.get("BundleIdentifier")) in visited:
                return
                        
            bundle["MaxKernel"] = os_data.get_latest_darwin_version()
            bundle["MinKernel"] = os_data.get_lowest_darwin_version()

            kext_index = kext_data.kext_index_by_name.get(os.path.splitext(os.path.basename(bundle.get("BundlePath")))[0])

            if kext_index:
                bundle["MaxKernel"] = self.kexts[kext_index].max_darwin_version
                bundle["MinKernel"] = self.kexts[kext_index].min_darwin_version
            
            for dep_identifier in bundle.get("BundleLibraries"):
                if dep_identifier in bundle_dict:
                    visit(bundle_dict[dep_identifier])
                    
                    bundle["MaxKernel"] = bundle["MaxKernel"] if self.utils.parse_darwin_version(bundle["MaxKernel"]) < self.utils.parse_darwin_version(bundle_dict[dep_identifier].get("MaxKernel", "99.99.99")) else bundle_dict[dep_identifier]["MaxKernel"]
                    bundle["MinKernel"] = bundle["MinKernel"] if self.utils.parse_darwin_version(bundle["MinKernel"]) > self.utils.parse_darwin_version(bundle_dict[dep_identifier].get("MinKernel", "0.0.0")) else bundle_dict[dep_identifier]["MinKernel"]

            if os.path.splitext(os.path.basename(bundle.get("BundlePath")))[0] == "AirPortBrcm4360_Injector":
                bundle["MaxKernel"] = "19.99.99"
            elif os.path.splitext(os.path.basename(bundle.get("BundlePath")))[0] == "AirportItlwm":
                bundle["MaxKernel"] = macos_version[:2] + bundle["MaxKernel"][2:]
                bundle["MinKernel"] = macos_version[:2] + bundle["MinKernel"][2:]

            visited.add((bundle.get("BundlePath"), bundle.get("BundleIdentifier")))

            if bundle.get("BundleIdentifier") in seen_identifier:
                bundle["Enabled"] = False
            else:
                seen_identifier.add(bundle.get("BundleIdentifier"))

            sorted_bundles.append(bundle)

        for bundle in bundle_list:
            visit(bundle)

        latest_darwin_version = (os_data.get_latest_darwin_version(), os_data.get_latest_darwin_version(include_beta=False))
        lowest_darwin_version = os_data.get_lowest_darwin_version()

        for bundle in sorted_bundles:
            kernel_add.append({
                "Arch": "x86_64",
                "BundlePath": bundle.get("BundlePath"),
                "Comment": "",
                "Enabled": bundle.get("Enabled"),
                "ExecutablePath": bundle.get("ExecutablePath"),
                "MaxKernel": "" if bundle.get("MaxKernel") in latest_darwin_version else bundle.get("MaxKernel"),
                "MinKernel": "" if bundle.get("MinKernel") == lowest_darwin_version else bundle.get("MinKernel"),
                "PlistPath": bundle.get("PlistPath")
            })

        return kernel_add

    def uncheck_kext(self, index):
        kext = self.kexts[index]
        kext.checked = False

        for other_kext in self.kexts:
            if other_kext.name in kext.requires_kexts and not other_kext.required:
                other_kext.checked = False

    def verify_kext_compatibility(self, selected_kexts, target_darwin_version):
        incompatible_kexts = [
            (self.kexts[index].name, "Lilu" in self.kexts[index].requires_kexts)
            for index in selected_kexts
            if not self.utils.parse_darwin_version(self.kexts[index].min_darwin_version)
            <= self.utils.parse_darwin_version(target_darwin_version)
            <= self.utils.parse_darwin_version(self.kexts[index].max_darwin_version)
        ]

        if not incompatible_kexts:
            return False
        
        while True:
            self.utils.head("Kext Compatibility Check")
            print("\nIncompatible kexts for the current macOS version ({}):\n".format(target_darwin_version))
            
            for index, (kext_name, is_lilu_dependent) in enumerate(incompatible_kexts, start=1):
                print("{:2}. {:25}{}".format(index, kext_name, " - Lilu Plugin" if is_lilu_dependent else ""))
            
            print("\n\033[1;36m")
            print("Note:")
            print("- With Lilu plugins, using the \"-lilubetaall\" boot argument will force them to load.")
            print("- Forcing unsupported kexts can cause system instability. \033[0;31mProceed with caution.\033[0m")
            print("\033[0m")
            
            option = self.utils.request_input("Do you want to force load {} on the unsupported macOS version? (Y/n): ".format("these kexts" if len(incompatible_kexts) > 1 else "this kext"))
            
            if option.lower() == "y":
                return True
            elif option.lower() == "n":
                return False

    def kext_configuration_menu(self, macos_version):
        current_category = None

        while True:
            contents = []
            contents.append("")
            contents.append("List of available kexts:")
            for index, kext in enumerate(self.kexts, start=1):
                if kext.category != current_category:
                    current_category = kext.category
                    category_header = "Category: {}".format(current_category if current_category else "Uncategorized")
                    contents.append(f"\n{category_header}\n" + "=" * len(category_header))
                checkbox = "[*]" if kext.checked else "[ ]"
                
                line = "{} {:2}. {:35} - {:60}".format(checkbox, index, kext.name, kext.description)
                if kext.checked:
                    line = "\033[1;32m{}\033[0m".format(line)
                elif not self.utils.parse_darwin_version(kext.min_darwin_version) <= self.utils.parse_darwin_version(macos_version) <= self.utils.parse_darwin_version(kext.max_darwin_version):
                    line = "\033[90m{}\033[0m".format(line)
                contents.append(line)
            contents.append("\033[1;36m")
            contents.append("Note:")
            contents.append("- Lines in gray indicate kexts that are not supported by the current macOS version ({}).".format(macos_version))
            contents.append("- When a plugin of a kext is selected, the entire kext will be automatically selected.")
            contents.append("- You can select multiple kexts by entering their indices separated by commas (e.g., '1, 2, 3').")
            contents.append("\033[0m")
            contents.append("B. Back")
            contents.append("Q. Quit")
            contents.append("")
            content = "\n".join(contents)

            self.utils.adjust_window_size(content)
            self.utils.head("Configure Kernel Extensions", resize=False)
            print(content)
            option = self.utils.request_input("Select your option: ")
            if option.lower() == "b":
                return
            if option.lower() == "q":
                self.utils.exit_program()
            indices = [int(i.strip()) -1 for i in option.split(",") if i.strip().isdigit()]

            allow_unsupported_kexts = "Beta" in os_data.get_macos_name_by_darwin(macos_version) or self.verify_kext_compatibility(indices, macos_version)
    
            for index in indices:
                if index >= 0 and index < len(self.kexts):
                    kext = self.kexts[index]
                    if kext.checked and not kext.required:
                        self.uncheck_kext(index)
                    else:
                        self.check_kext(index, macos_version, allow_unsupported_kexts)