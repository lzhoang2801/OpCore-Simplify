
from Scripts.datasets import cpu_data
from Scripts.datasets import kext_data
from Scripts.datasets import mac_model_data
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
                    device_id = pci_id[-4:]
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

    def is_intel_hedt_cpu(self, cpu_codename):
        return not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=21) is None and cpu_codename.endswith(("-X", "-P", "-W", "-E", "-EP", "-EX"))
    
    def get_kext_index(self, name):
        for index, kext in enumerate(self.kexts):
            if kext.name == name:
                return index
        return None

    def check_kext(self, index, target_darwin_version, allow_unsupported_kexts=False):
        kext = self.kexts[index]

        if kext.checked or not (allow_unsupported_kexts or self.utils.parse_darwin_version(kext.min_darwin_version) <= self.utils.parse_darwin_version(target_darwin_version) <= self.utils.parse_darwin_version(kext.max_darwin_version)):
            return

        kext.checked = True

        for requires_kext_name in kext.requires_kexts:
            requires_kext_index = self.get_kext_index(requires_kext_name)
            if requires_kext_index:
                self.check_kext(requires_kext_index, target_darwin_version, allow_unsupported_kexts)

        if kext.conflict_group_id:
            for other_kext in self.kexts:
                if other_kext.conflict_group_id == kext.conflict_group_id and other_kext.name != kext.name:
                    other_kext.checked = False

    def select_required_kexts(self, hardware_report, smbios_model, macos_version, needs_oclp, acpi_patches):
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
                 self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware_report.get("CPU").get("Codename"), start=4)) or \
            self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0") or "MacPro7,1" in smbios_model:
            selected_kexts.append("RestrictEvents")

        if hardware_report.get("Sound"):
            if list(hardware_report.get("Sound").items())[0][-1].get("Device ID") in codec_layouts.data:
                selected_kexts.append("AppleALC")
        
        if "AMD" in hardware_report.get("CPU").get("Manufacturer") and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("21.4.0") or \
            int(hardware_report.get("CPU").get("CPU Count")) > 1 and self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("19.0.0"):
            selected_kexts.append("AppleMCEReporterDisabler")

        if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("22.0.0") and not "AVX2" in hardware_report.get("CPU").get("SIMD Features"):
            selected_kexts.append("CryptexFixup")

        if self.utils.contains_any(cpu_data.IntelCPUGenerations, hardware_report.get("CPU").get("Codename"), end=2) and \
            int(hardware_report.get("CPU").get("Core Count")) > 6:
            selected_kexts.append("CpuTopologyRebuild")

        if  "AMD" in hardware_report.get("CPU").get("Manufacturer") and \
            "Integrated GPU" in list(hardware_report.get("GPU").items())[0][-1].get("Device Type") and \
            "Integrated GPU" in list(hardware_report.get("GPU").items())[-1][-1].get("Device Type"):
            selected_kexts.append("NootedRed")
        else:
            selected_kexts.append("NootRX" if "Navi 22" in list(hardware_report.get("GPU").items())[0][-1].get("Codename") else "WhateverGreen")

        if "Laptop" in hardware_report.get("Motherboard").get("Platform") and "ASUS" in hardware_report.get("Motherboard").get("Name") or \
            "NootedRed" in selected_kexts or \
            self.is_intel_hedt_cpu(hardware_report.get("CPU").get("Codename")):
            selected_kexts.append("ForgedInvariant")

        if needs_oclp:
            selected_kexts.extend(("AMFIPass", "RestrictEvents"))

        ethernet_pci = None
        for network_name, network_props in hardware_report.get("Network", {}).items():
            device_id = network_props.get("Device ID")

            if self.utils.contains_any(pci_data.NetworkIDs, device_id, end=21):
                if device_id in ["14E4-43A0", "14E4-43A3", "14E4-43BA"]:
                    if self.utils.parse_darwin_version(macos_version) >= self.utils.parse_darwin_version("23.0.0"):
                        selected_kexts.extend(("AirportBrcmFixup", "IOSkywalkFamily"))
                elif device_id in pci_data.NetworkIDs:
                    selected_kexts.append("AirportBrcmFixup")
            elif self.utils.contains_any(pci_data.NetworkIDs, device_id, start=21, end=108):
                selected_kexts.append("AirportItlwm" if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("23.0.0") else "itlwm")
            elif self.utils.contains_any(pci_data.NetworkIDs, device_id, start=108, end=219):
                ethernet_pci = pci_data.NetworkIDs.index(device_id)
                if 107 < ethernet_pci < 115:
                    selected_kexts.append("AppleIGC")
                elif 114 < ethernet_pci < 122:
                    selected_kexts.append("AtherosE2200Ethernet")
                elif 121 < ethernet_pci < 173:
                    selected_kexts.append("IntelMausi")
                elif 172 < ethernet_pci < 176:
                    selected_kexts.append("LucyRTL8125Ethernet")
                elif 175 < ethernet_pci < 177:
                    selected_kexts.append("RealtekRTL8100")
                elif 176 < ethernet_pci < 181:
                    selected_kexts.append("RealtekRTL8111")
                elif 180 < ethernet_pci < 219:
                    selected_kexts.append("AppleIGB")

        if not ethernet_pci:
            selected_kexts.append("NullEthernet")

        for bluetooth_name, bluetooth_props in hardware_report.get("Bluetooth", {}).items():
            usb_id = bluetooth_props.get("Device ID")

            if usb_id in pci_data.BluetoothIDs:               
                if pci_data.BluetoothIDs.index(usb_id) < 99:
                    selected_kexts.append("BrcmFirmwareData")
                if pci_data.BluetoothIDs[-1] == usb_id:
                    selected_kexts.append("BlueToolFixup")
                else:
                    selected_kexts.append("IntelBluetoothFirmware")

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

        if any(patch.checked for patch in acpi_patches if patch.name == "BATP"):
            selected_kexts.append("ECEnabler")

        for controller_name, controller_props in hardware_report.get("SD Controller", {}).items():
            if controller_props.get("Device ID") in pci_data.RealtekCardReaderIDs:
                selected_kexts.append("RealtekCardReader")
        
        for controller_name, controller_props in hardware_report.get("Storage Controllers").items():
            if "NVMe" in controller_name or "NVM Express" in controller_name:
                selected_kexts.append("NVMeFix")
            else:
                if controller_props.get("Device ID") in pci_data.UnsupportedSATAControllerIDs and not "AHCI" in controller_name:
                    selected_kexts.append("CtlnaAHCIPort")

        for controller_name, controller_props in hardware_report.get("USB Controllers").items():
            device_id = controller_props.get("Device ID")
            if device_id in pci_data.UnsupportedUSBControllerIDs:
                idx = pci_data.UnsupportedUSBControllerIDs.index(device_id)
                if idx == 0:
                    selected_kexts.append("GenericUSBXHCI")
                else:
                    selected_kexts.append("XHCI-unsupported")

        if smbios_model in (device.name for device in mac_model_data.mac_devices[31:34] + mac_model_data.mac_devices[48:50] + mac_model_data.mac_devices[51:61]):
            selected_kexts.append("NoTouchID")

        for name in selected_kexts:
            self.check_kext(self.get_kext_index(name), macos_version, "Beta" in os_data.get_macos_name_by_darwin(macos_version))

    def install_kexts_to_efi(self, macos_version, kexts_directory):
        for kext in self.kexts:
            if kext.checked:
                try:
                    source_kext_path = destination_kext_path = None

                    kext_paths = self.utils.find_matching_paths(self.ock_files_dir, extension_filter=".kext", name_filter=kext.name)
                    for kext_path, type in kext_paths:
                        if "AirportItlwm" == kext.name:
                            version = macos_version[:2]
                            if self.utils.parse_darwin_version("24.0.0") <= self.utils.parse_darwin_version(macos_version):
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
                            main_kext_index = self.get_kext_index(main_kext)
                            if not main_kext_index or self.kexts[main_kext_index].checked:
                                if os.path.splitext(os.path.basename(kext_path))[0] in kext.name:
                                    source_kext_path = os.path.join(self.ock_files_dir, kext_path)
                                    destination_kext_path = os.path.join(kexts_directory, os.path.basename(kext_path))
                                    break
                    
                    if os.path.exists(source_kext_path):
                        shutil.copytree(source_kext_path, destination_kext_path, dirs_exist_ok=True)
                except:
                    continue
        
    def load_kexts(self, macos_version, kexts_directory):
        kernel_add = []
        unload_kext = []

        if self.kexts[self.get_kext_index("AirportBrcmFixup")].checked and self.utils.parse_darwin_version(macos_version) > self.utils.parse_darwin_version("20.0.0"):
            unload_kext.append("AirPortBrcm4360_Injector")

        if self.kexts[self.get_kext_index("VoodooSMBus")].checked:
            unload_kext.append("VoodooPS2Mouse")
        elif self.kexts[self.get_kext_index("VoodooRMI")].checked:
            if not self.kexts[self.get_kext_index("VoodooI2C")].checked:
                unload_kext.append("RMII2C")
            else:
                unload_kext.extend((
                    "VoodooSMBus",
                    "RMISMBus",
                    "VoodooI2CServices",
                    "VoodooGPIO",
                    "VoodooI2CHID"
                ))

        kext_paths = self.utils.find_matching_paths(kexts_directory, extension_filter=".kext")
        bundle_list = []

        for kext_path, type in kext_paths:        
            try:
                plist_path = self.utils.find_matching_paths(os.path.join(kexts_directory, kext_path), extension_filter=".plist", name_filter="Info")[0][0]
                bundle_info = self.utils.read_file(os.path.join(kexts_directory, kext_path, plist_path))
            except:
                bundle_info = {}

            if not isinstance(bundle_info.get("CFBundleIdentifier", None), (str, unicode)):
                continue

            executable_path = os.path.join("Contents", "MacOS", bundle_info.get("CFBundleExecutable", "None"))
            if not os.path.exists(os.path.join(kexts_directory, kext_path, executable_path)):
                executable_path = ""

            if bundle_info.get("CFBundleExecutable", "None") == "AirportItlwm" and self.utils.parse_darwin_version("24.0.0") <= self.utils.parse_darwin_version(macos_version):
                bundle_info["IOKitPersonalities"]["itlwm"]["IOPCIMatch"] += " 0x43A014E4"
                self.utils.write_file(os.path.join(kexts_directory, kext_path, plist_path), bundle_info)
            
            bundle_list.append({
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
            })

        bundle_dict = {bundle["BundleIdentifier"]: bundle for bundle in bundle_list}

        sorted_bundles = []
        
        visited = set()
        seen_identifier = set()

        def visit(bundle):
            if os.path.splitext(os.path.basename(bundle.get("BundlePath")))[0] in unload_kext or (bundle.get("BundlePath"), bundle.get("BundleIdentifier")) in visited:
                return
            
            for dep_identifier in bundle.get("BundleLibraries"):
                if dep_identifier in bundle_dict:
                    visit(bundle_dict[dep_identifier])

            visited.add((bundle.get("BundlePath"), bundle.get("BundleIdentifier")))

            if bundle.get("BundleIdentifier") in seen_identifier:
                bundle["Enabled"] = False
            else:
                seen_identifier.add(bundle.get("BundleIdentifier"))

            sorted_bundles.append(bundle)

        for bundle in bundle_list:
            visit(bundle)

        for bundle in sorted_bundles:
            kernel_add.append({
                "Arch": "x86_64",
                "BundlePath": bundle.get("BundlePath"),
                "Comment": "",
                "Enabled": bundle.get("Enabled"),
                "ExecutablePath": bundle.get("ExecutablePath"),
                "MaxKernel": "",
                "MinKernel": "",
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

    def kext_configuration_menu(self, hardware_report, smbios_model, macos_version, acpi_patches):
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
                
                line = "{} {:2}. {:25} - {:60}".format(checkbox, index, kext.name, kext.description)
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
            contents.append("R. Restore defaults")
            contents.append("")
            contents.append("B. Back")
            contents.append("Q. Quit")
            contents.append("")
            content = "\n".join(contents)

            self.utils.adjust_window_size(content)
            self.utils.head("Configure Kernel Extensions", resize=False)
            print(content)
            option = self.utils.request_input("Select your option: ")
            if option.lower() == "r":
                self.select_required_kexts(hardware_report, smbios_model, macos_version, acpi_patches)
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