
from Scripts.datasets import cpu_data
from Scripts.datasets import pci_data
from Scripts import utils
import os
import shutil

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
        self.kext_loading_sequence = [
            {
                "MainKext": "Lilu",
                "BundlePath": "Lilu.kext",
                "ExecutablePath": "Contents/MacOS/Lilu",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VirtualSMC",
                "BundlePath": "VirtualSMC.kext",
                "ExecutablePath": "Contents/MacOS/VirtualSMC",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "ECEnabler",
                "BundlePath": "ECEnabler.kext",
                "ExecutablePath": "Contents/MacOS/ECEnabler",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VirtualSMC",
                "BundlePath": "SMCBatteryManager.kext",
                "ExecutablePath": "Contents/MacOS/SMCBatteryManager",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VirtualSMC",
                "BundlePath": "SMCDellSensors.kext",
                "ExecutablePath": "Contents/MacOS/SMCDellSensors",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VirtualSMC",
                "BundlePath": "SMCLightSensor.kext",
                "ExecutablePath": "Contents/MacOS/SMCLightSensor",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VirtualSMC",
                "BundlePath": "SMCProcessor.kext",
                "ExecutablePath": "Contents/MacOS/SMCProcessor",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VirtualSMC",
                "BundlePath": "SMCSuperIO.kext",
                "ExecutablePath": "Contents/MacOS/SMCSuperIO",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "WhateverGreen",
                "BundlePath": "WhateverGreen.kext",
                "ExecutablePath": "Contents/MacOS/WhateverGreen",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "NootedRed",
                "BundlePath": "NootedRed.kext",
                "ExecutablePath": "Contents/MacOS/NootedRed",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "NootRX",
                "BundlePath": "NootRX.kext",
                "ExecutablePath": "Contents/MacOS/NootRX",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AppleALC",
                "BundlePath": "AppleALC.kext",
                "ExecutablePath": "Contents/MacOS/AppleALC",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AirportItlwm",
                "BundlePath": "AirportItlwm.kext",
                "ExecutablePath": "Contents/MacOS/AirportItlwm",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "itlwm",
                "BundlePath": "itlwm.kext",
                "ExecutablePath": "Contents/MacOS/itlwm",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IOSkywalkFamily",
                "BundlePath": "IOSkywalkFamily.kext",
                "ExecutablePath": "Contents/MacOS/IOSkywalkFamily",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IO80211FamilyLegacy",
                "BundlePath": "IO80211FamilyLegacy.kext",
                "ExecutablePath": "Contents/MacOS/IO80211FamilyLegacy",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IO80211FamilyLegacy",
                "BundlePath": "IO80211FamilyLegacy.kext/Contents/PlugIns/AirPortBrcmNIC.kext",
                "ExecutablePath": "Contents/MacOS/AirPortBrcmNIC",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AirportBrcmFixup",
                "BundlePath": "AirportBrcmFixup.kext",
                "ExecutablePath": "Contents/MacOS/AirportBrcmFixup",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AirportBrcmFixup",
                "BundlePath": "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcm4360_Injector.kext",
                "ExecutablePath": "",
                "MaxKernel": "19.99.99",
                "MinKernel": ""
            },
            {
                "MainKext": "AirportBrcmFixup",
                "BundlePath": "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext",
                "ExecutablePath": "",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IntelBluetoothFirmware",
                "BundlePath": "IntelBluetoothFirmware.kext",
                "ExecutablePath": "Contents/MacOS/IntelBluetoothFirmware",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IntelBluetoothFirmware",
                "BundlePath": "IntelBTPatcher.kext",
                "ExecutablePath": "Contents/MacOS/IntelBTPatcher",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IntelBluetoothFirmware",
                "BundlePath": "IntelBluetoothInjector.kext",
                "ExecutablePath": "",
                "MaxKernel": "20.99.99",
                "MinKernel": ""
            },
            {
                "MainKext": "BlueToolFixup",
                "BundlePath": "BlueToolFixup.kext",
                "ExecutablePath": "Contents/MacOS/BlueToolFixup",
                "MaxKernel": "",
                "MinKernel": "21.0.0"
            },
            {
                "MainKext": "BrcmPatchRAM",
                "BundlePath": "BrcmBluetoothInjector.kext",
                "ExecutablePath": "",
                "MaxKernel": "20.99.99",
                "MinKernel": ""
            },
            {
                "MainKext": "BrcmPatchRAM",
                "BundlePath": "BrcmFirmwareData.kext",
                "ExecutablePath": "Contents/MacOS/BrcmFirmwareData",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BrcmPatchRAM",
                "BundlePath": "BrcmPatchRAM2.kext",
                "ExecutablePath": "Contents/MacOS/BrcmPatchRAM2",
                "MaxKernel": "18.99.99",
                "MinKernel": ""
            },
            {
                "MainKext": "BrcmPatchRAM",
                "BundlePath": "BrcmPatchRAM3.kext",
                "ExecutablePath": "Contents/MacOS/BrcmPatchRAM3",
                "MaxKernel": "",
                "MinKernel": "19.0.0"
            },
            {
                "MainKext": "AppleIGC",
                "BundlePath": "AppleIGC.kext",
                "ExecutablePath": "Contents/MacOS/AppleIGC",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AtherosE2200Ethernet",
                "BundlePath": "AtherosE2200Ethernet.kext",
                "ExecutablePath": "Contents/MacOS/AtherosE2200Ethernet",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "IntelMausi",
                "BundlePath": "IntelMausi.kext",
                "ExecutablePath": "Contents/MacOS/IntelMausi",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "LucyRTL8125Ethernet",
                "BundlePath": "LucyRTL8125Ethernet.kext",
                "ExecutablePath": "Contents/MacOS/LucyRTL8125Ethernet",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "NullEthernet",
                "BundlePath": "NullEthernet.kext",
                "ExecutablePath": "Contents/MacOS/NullEthernet",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "RealtekRTL8100",
                "BundlePath": "RealtekRTL8100.kext",
                "ExecutablePath": "Contents/MacOS/RealtekRTL8100",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "RealtekRTL8111",
                "BundlePath": "RealtekRTL8111.kext",
                "ExecutablePath": "Contents/MacOS/RealtekRTL8111",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BrightnessKeys",
                "BundlePath": "BrightnessKeys.kext",
                "ExecutablePath": "Contents/MacOS/BrightnessKeys",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AsusSMC",
                "BundlePath": "AsusSMC.kext",
                "ExecutablePath": "Contents/MacOS/AsusSMC",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooInput",
                "BundlePath": "VoodooInput.kext",
                "ExecutablePath": "Contents/MacOS/VoodooInput",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooPS2",
                "BundlePath": "VoodooPS2Controller.kext",
                "ExecutablePath": "Contents/MacOS/VoodooPS2Controller",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooPS2",
                "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Keyboard.kext",
                "ExecutablePath": "Contents/MacOS/VoodooPS2Keyboard",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooPS2",
                "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Mouse.kext",
                "ExecutablePath": "Contents/MacOS/VoodooPS2Mouse",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooPS2",
                "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Trackpad.kext",
                "ExecutablePath": "Contents/MacOS/VoodooPS2Trackpad",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooRMI",
                "BundlePath": "VoodooRMI.kext",
                "ExecutablePath": "Contents/MacOS/VoodooRMI",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooRMI",
                "BundlePath": "VoodooSMBus.kext",
                "ExecutablePath": "Contents/MacOS/VoodooSMBus",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooSMBus",
                "BundlePath": "VoodooSMBus.kext",
                "ExecutablePath": "Contents/MacOS/VoodooSMBus",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooRMI",
                "BundlePath": "VoodooRMI.kext/Contents/PlugIns/RMISMBus.kext",
                "ExecutablePath": "Contents/MacOS/RMISMBus",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooI2C",
                "BundlePath": "VoodooI2C.kext/Contents/PlugIns/VoodooI2CServices.kext",
                "ExecutablePath": "Contents/MacOS/VoodooI2CServices",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooI2C",
                "BundlePath": "VoodooI2C.kext/Contents/PlugIns/VoodooGPIO.kext",
                "ExecutablePath": "Contents/MacOS/VoodooGPIO",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooI2C",
                "BundlePath": "VoodooI2C.kext",
                "ExecutablePath": "Contents/MacOS/VoodooI2C",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BigSurface",
                "BundlePath": "BigSurface.kext/Contents/PlugIns/VoodooInput.kext",
                "ExecutablePath": "Contents/MacOS/VoodooInput",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BigSurface",
                "BundlePath": "BigSurface.kext/Contents/PlugIns/VoodooGPIO.kext",
                "ExecutablePath": "Contents/MacOS/VoodooGPIO",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BigSurface",
                "BundlePath": "BigSurface.kext/Contents/PlugIns/VoodooSerial.kext",
                "ExecutablePath": "Contents/MacOS/VoodooSerial",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BigSurface",
                "BundlePath": "BigSurface.kext",
                "ExecutablePath": "Contents/MacOS/BigSurface",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "BigSurface",
                "BundlePath": "BigSurface.kext/Contents/PlugIns/BigSurfaceHIDDriver.kext",
                "ExecutablePath": "Contents/MacOS/BigSurfaceHIDDriver",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooRMI",
                "BundlePath": "VoodooRMI.kext/Contents/PlugIns/RMII2C.kext",
                "ExecutablePath": "Contents/MacOS/RMII2C",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "lzh",
                "BundlePath": "VoodooI2CELAN.kext",
                "ExecutablePath": "Contents/MacOS/VoodooI2CELAN",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "VoodooI2C",
                "BundlePath": "VoodooI2CHID.kext",
                "ExecutablePath": "Contents/MacOS/VoodooI2CHID",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AlpsHID",
                "BundlePath": "AlpsHID.kext",
                "ExecutablePath": "Contents/MacOS/AlpsHID",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "lzh",
                "BundlePath": "VoodooI2CSynaptics.kext",
                "ExecutablePath": "Contents/MacOS/VoodooI2CSynaptics",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "AppleMCEReporterDisabler",
                "BundlePath": "AppleMCEReporterDisabler.kext",
                "ExecutablePath": "",
                "MaxKernel": "",
                "MinKernel": "21.0.0"
            },
            {
                "MainKext": "AMFIPass",
                "BundlePath": "AMFIPass.kext",
                "ExecutablePath": "Contents/MacOS/AMFIPass",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "CpuTopologyRebuild",
                "BundlePath": "CpuTopologyRebuild.kext",
                "ExecutablePath": "Contents/MacOS/CpuTopologyRebuild",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "CtlnaAHCIPort",
                "BundlePath": "CtlnaAHCIPort.kext",
                "ExecutablePath": "Contents/MacOS/CtlnaAHCIPort",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "RealtekCardReader",
                "BundlePath": "RealtekCardReader.kext",
                "ExecutablePath": "Contents/MacOS/RealtekCardReader",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "RealtekCardReaderFriend",
                "BundlePath": "RealtekCardReaderFriend.kext",
                "ExecutablePath": "Contents/MacOS/RealtekCardReaderFriend",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "ForgedInvariant",
                "BundlePath": "ForgedInvariant.kext",
                "ExecutablePath": "Contents/MacOS/ForgedInvariant",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "RestrictEvents",
                "BundlePath": "RestrictEvents.kext",
                "ExecutablePath": "Contents/MacOS/RestrictEvents",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "HibernationFixup",
                "BundlePath": "HibernationFixup.kext",
                "ExecutablePath": "Contents/MacOS/HibernationFixup",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "RTCMemoryFixup",
                "BundlePath": "RTCMemoryFixup.kext",
                "ExecutablePath": "Contents/MacOS/RTCMemoryFixup",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "NVMeFix",
                "BundlePath": "NVMeFix.kext",
                "ExecutablePath": "Contents/MacOS/NVMeFix",
                "MaxKernel": "",
                "MinKernel": "18.0.0"
            },
            {
                "MainKext": "CryptexFixup",
                "BundlePath": "CryptexFixup.kext",
                "ExecutablePath": "Contents/MacOS/CryptexFixup",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "GenericUSBXHCI",
                "BundlePath": "GenericUSBXHCI.kext",
                "ExecutablePath": "Contents/MacOS/GenericUSBXHCI",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "XHCI-unsupported",
                "BundlePath": "XHCI-unsupported.kext",
                "ExecutablePath": "",
                "MaxKernel": "",
                "MinKernel": ""
            },
            {
                "MainKext": "USBMap",
                "BundlePath": "USBMap.kext",
                "ExecutablePath": "",
                "MaxKernel": "",
                "MinKernel": ""
            }
        ]
        self.latest_macos_version = "24.99.99"

    def extract_pci_id(self, kext_path):
        if not os.path.exists(kext_path):
            return []

        plist_path = os.path.join(kext_path, "Contents", "Info.plist")
        plist_data = self.utils.read_file(plist_path)

        pci_ids = []

        # Iterate through the personalities in the plist
        for personality_name, properties in plist_data.get("IOKitPersonalities", {}).items():
            matching_keys = [key for key in self.matching_keys if key in properties]
            
            if not matching_keys:
                continue
            
            match_key = matching_keys[0]

            if match_key in ["IOPCIMatch", "IOPCIPrimaryMatch"]:
                # Split PCI IDs and format them
                pci_list = properties[match_key].split(" ")
                for pci_id in pci_list:
                    vendor_id = pci_id[-4:]
                    device_id = pci_id[2:6]
                    pci_ids.append("{}-{}".format(vendor_id, device_id).upper())
            elif match_key == "IONameMatch":
                # Process IONameMatch keys
                for pci_id in properties[match_key]:
                    vendor_id = pci_id[3:7]
                    device_id = pci_id[-4:]
                    pci_ids.append("{}-{}".format(vendor_id, device_id).upper())
            elif match_key == "idProduct":
                # Process idProduct and idVendor
                vendor_id = self.utils.int_to_hex(properties["idVendor"]).zfill(4)
                device_id = self.utils.int_to_hex(properties["idProduct"]).zfill(4)
                pci_ids.append("{}-{}".format(vendor_id, device_id).upper())
            elif match_key == "HDAConfigDefault":
                # Handle AppleALC configurations
                for codec_layout in properties[match_key]:
                    codec_id = self.utils.int_to_hex(codec_layout.get("CodecID")).zfill(8)
                    pci_ids.append("{}-{}".format(codec_id[:4], codec_id[-4:]))
                pci_ids = sorted(list(set(pci_ids)))

        return pci_ids

    def gathering_kexts(self, motherboard_name, platform, cpu_configuration, cpu_manufacturer, cpu_codename, discrete_gpu_codename, integrated_gpu, wifi_pci, ethernet_pci, bluetooth, codec_id, input, sd_controller, storage_controllers, usb_controllers, smbios, custom_cpu_name, tsc_sync, battery_status_patch_needed, macos_version):
        kexts = [
            "Lilu", 
            "VirtualSMC", 
            "USBMap"
        ]

        if macos_version > 22 or custom_cpu_name or "MacPro7,1" in smbios:
            kexts.append("RestrictEvents")

        if codec_id in pci_data.CodecIDs and not ("AMD" in cpu_manufacturer and macos_version > 23):
            kexts.append("AppleALC")
        
        if "AMD" in cpu_manufacturer and macos_version > 21 or int(cpu_configuration) > 1 and macos_version > 18:
            kexts.append("AppleMCEReporterDisabler")

        if macos_version > 21 and self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=2):
            kexts.append("CryptexFixup")

        if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=13):
            kexts.append("CpuTopologyRebuild")

        if tsc_sync:
            kexts.append("ForgedInvariant")

        if "AMD" in cpu_manufacturer and integrated_gpu and not discrete_gpu_codename:
            kexts.append("NootedRed")
        else:
            kexts.append("NootRX" if "Navi 2" in discrete_gpu_codename else "WhateverGreen")

        if wifi_pci and wifi_pci in pci_data.NetworkIDs:
            if wifi_pci.startswith("14E4"):
                if wifi_pci in ["14E4-43A0", "14E4-43A3", "14E4-43BA"]:
                    if macos_version > 22:
                        kexts.extend(["AirportBrcmFixup", "IOSkywalkFamily", "IO80211FamilyLegacy", "AMFIPass"])
                elif wifi_pci in pci_data.NetworkIDs:
                    kexts.append("AirportBrcmFixup")
            elif wifi_pci.startswith("8086"):
                kexts.append("AirportItlwm" if macos_version < 23 else "itlwm")

        if not ethernet_pci or not (ethernet_pci[0] in pci_data.NetworkIDs or ethernet_pci[-1] in pci_data.NetworkIDs):
            kexts.append("NullEthernet")
        else:
            for pci_id in ethernet_pci:
                idx = pci_data.NetworkIDs.index(pci_id)

                if 108 <= idx <= 114:
                    kexts.append("AppleIGC")
                elif 115 <= idx <= 121:
                    kexts.append("AtherosE2200Ethernet")
                elif 122 <= idx <= 172:
                    kexts.append("IntelMausi")
                elif 173 <= idx <= 175:
                    kexts.append("LucyRTL8125Ethernet")
                elif idx == 176:
                    kexts.append("RealtekRTL8100")
                elif 177 <= idx <= 180:
                    kexts.append("RealtekRTL8111")

        if bluetooth and macos_version > 20 and not wifi_pci in ["14E4-43A0", "14E4-43A3", "14E4-43BA"]:
            kexts.append("BlueToolFixup")
        for usb_id in bluetooth:
            if usb_id in pci_data.BluetoothIDs:
                idx = pci_data.BluetoothIDs.index(usb_id)
                
                if idx < 99:
                    kexts.append("BrcmPatchRAM")
                else:
                    kexts.append("IntelBluetoothFirmware")

        if "Laptop" in platform:
            if "SURFACE" in motherboard_name:
                kexts.append("BigSurface")
            else:
                if "ASUS" in motherboard_name:
                    kexts.append("AsusSMC")
                kexts.append("BrightnessKeys")

                for device_name, device_props in input.items():
                    if not device_props.get("Bus Type", "").startswith("ACPI"):
                        continue

                    if "PS/2" in device_name:
                        kexts.extend(["VoodooInput", "VoodooPS2"])
                    if "I2C" in device_name:
                        kexts.extend(["VoodooInput", "VoodooI2C"])

                    device_id = device_props.get("Device ID")
                    if device_id in pci_data.InputIDs:
                        idx = pci_data.InputIDs.index(device_id)
                        
                        if idx < 77:
                            kexts.append("AlpsHID")
                        elif 76 < idx < 80:
                            kexts.append("VoodooSMBus")
                        else:
                            kexts.append("VoodooRMI")

        if "Laptop" in platform and "SURFACE" not in motherboard_name and battery_status_patch_needed:
            kexts.append("ECEnabler")

        if sd_controller and sd_controller.get("Device ID") in pci_data.RealtekCardReaderIDs:
            kexts.extend(["RealtekCardReader", "RealtekCardReaderFriend"])
        
        for controller_name, controller_props in storage_controllers.items():
            if "NVMe" in controller_name or "NVM Express" in controller_props.get("Device Description"):
                kexts.append("NVMeFix")
            else:
                if controller_props.get("Device ID") in pci_data.UnsupportedSATAControllerIDs and not "AHCI" in controller_name:
                    kexts.append("CtlnaAHCIPort")

        for pci_id in usb_controllers:
            if pci_id in pci_data.UnsupportedUSBControllerIDs:
                idx = pci_data.UnsupportedUSBControllerIDs.index(pci_id)
                if idx == 0:
                    kexts.append("GenericUSBXHCI")
                else:
                    kexts.append("XHCI-unsupported")

        return list(set(kexts))
    
    def install_kexts_to_efi(self, kexts, macos_version, kexts_directory):
        for kext_name in kexts:
            if "AirportItlwm" in kext_name:
                kext_name = "{}{}".format(kext_name, macos_version)
            elif "BlueToolFixup" in kext_name or "BrcmPatchRAM" in kext_name:
                kext_name = "BrcmPatchRAM"

            source_kext_dir = os.path.join(self.ock_files_dir, kext_name)
            if os.path.exists(source_kext_dir):
                shutil.copytree(source_kext_dir, kexts_directory, dirs_exist_ok=True)
        
    def load_kexts(self, kexts, motherboard_name, platform, cpu_manufacturer, discrete_gpu_codename, macos_version):
        kernel_add = []
        unload_kext = []

        if not "DELL" in motherboard_name:
            unload_kext.append("SMCDellSensors")
        if "Desktop" in platform:
            unload_kext.extend([
                "SMCBatteryManager",
                "SMCLightSensor"
            ])
            if "AMD" in cpu_manufacturer:
                unload_kext.extend(["SMCProcessor", "SMCSuperIO"])
            if "Navi 2" in discrete_gpu_codename:
                unload_kext.append("SMCSuperIO")
        elif "Laptop" in platform and not "SURFACE" in motherboard_name:
            if "AMD" in cpu_manufacturer:
                unload_kext.extend([
                    "SMCProcessor", 
                    "SMCSuperIO"
                ])
            
            if "VoodooSMBus" in kexts:
                unload_kext.append("VoodooPS2Mouse")
            elif "VoodooRMI" in kexts:
                if not "VoodooI2C" in kexts:
                    unload_kext.append("RMII2C")
                else:
                    unload_kext.extend([
                        "VoodooSMBus",
                        "RMISMBus",
                        "VoodooI2CServices",
                        "VoodooGPIO",
                        "VoodooI2CHID"
                    ])

        for kext in self.kext_loading_sequence:
            if not kext.get("MainKext") in kexts or os.path.splitext(os.path.basename(kext.get("BundlePath")))[0] in unload_kext:
                continue
            max_supported_macos_version = kext.get("MaxKernel") or self.latest_macos_version
            min_supported_macos_version = kext.get("MinKernel") or "17.0.0"
            if not min_supported_macos_version[:2] <= str(macos_version) <= max_supported_macos_version[:2]:
                continue

            kernel_add.append({
                "Arch": "x86_64",
                "BundlePath": kext.get("BundlePath"),
                "Comment": "",
                "Enabled": True,
                "ExecutablePath": kext.get("ExecutablePath") or "",
                "MaxKernel": "",
                "MinKernel": "",
                "PlistPath": "Contents/Info.plist"
            })

        return kernel_add