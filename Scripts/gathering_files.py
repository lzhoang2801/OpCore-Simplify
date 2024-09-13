from Scripts import github
from Scripts import resource_fetcher
from Scripts import utils
import os
import tempfile
import shutil
import subprocess
from datetime import datetime, timedelta

class gatheringFiles:
    def __init__(self):
        self.utils = utils.Utils()
        self.github = github.Github()
        self.fetcher = resource_fetcher.ResourceFetcher(self.github.headers)
        self.dortania_builds_url = "https://raw.githubusercontent.com/dortania/build-repo/builds/latest.json"
        self.amd_vanilla_patches_url = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/beta/patches.plist"
        self.temporary_dir = tempfile.mkdtemp()
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.download_history_file = os.path.join(self.ock_files_dir, "history.json")
        self.builds = [
            "AirportBrcmFixup",
            "BrcmPatchRAM",
            "BrightnessKeys",
            "CryptexFixup",
            "ECEnabler",
            "HibernationFixup",
            "IntelBluetoothFirmware",
            "IntelMausi", 
            "Lilu", 
            "NVMeFix", 
            "RTCMemoryFixup", 
            "RealtekRTL8111", 
            "RestrictEvents", 
            "VirtualSMC", 
            "VoodooI2C", 
            "VoodooInput", 
            "VoodooPS2", 
            "VoodooSMBus", 
            "WhateverGreen"
        ]
        self.releases = [
            {
                "owner": "blankmac",
                "repo": "AlpsHID"
            },
            {
                "owner": "SongXiaoXi",
                "repo": "AppleIGC"
            },
            {
                "owner": "hieplpvip",
                "repo": "AsusSMC"
            },
            {
                "owner": "Xiashangning",
                "repo": "BigSurface"
            },
            {
                "owner": "b00t0x",
                "repo": "CpuTopologyRebuild"
            },
            {
                "owner": "0xFireWolf",
                "repo": "RealtekCardReader"
            },
            {
                "owner": "0xFireWolf",
                "repo": "RealtekCardReaderFriend"
            },
            {
                "owner": "VoodooSMBus",
                "repo": "VoodooRMI"
            },
            {
                "owner": "OpenIntelWireless",
                "repo": "itlwm"
            },
            {
                "owner": "ChefKissInc",
                "repo": "NootRX"
            },
            {
                "owner": "ChefKissInc",
                "repo": "NootedRed"
            },
            {
                "owner": "ChefKissInc",
                "repo": "ForgedInvariant"
            },
            {
                "owner": "wjz304",
                "repo": "OpenCore_Patch_Build"
            }
        ][-5:]
        self.actions = []
        
    def get_bootloader_kexts_data(self):
        results = [
            {
                "product_name": "AlpsHID", 
                "id": 69228327, 
                "url": "https://github.com/blankmac/AlpsHID/releases/download/v1.2/AlpsHID1.2_release.zip"
            },
            {
                "product_name": "AMFIPass", 
                "id": 926491527, 
                "url": "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Acidanthera/AMFIPass-v1.4.1-RELEASE.zip"
            },
            {
                "product_name": "AppleALC", 
                "id": 223994507, 
                "url": "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/AppleALC-1.9.2-RELEASE.zip"
            },
            {
                "product_name": "AppleIGB", 
                "id": 736194363, 
                "url": "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/AppleIGB-v5.11.4.zip"
            },
            {
                "product_name": "AppleIGC", 
                "id": 138279923, 
                "url": "https://github.com/SongXiaoXi/AppleIGC/releases/download/v1.5/AppleIGC.kext.zip"
            },
            {
                "product_name": "AppleMCEReporterDisabler", 
                "id": 738162736, 
                "url": "https://github.com/acidanthera/bugtracker/files/3703498/AppleMCEReporterDisabler.kext.zip"
            },
            {
                "product_name": "AsusSMC", 
                "id": 41898282, 
                "url": "https://github.com/hieplpvip/AsusSMC/releases/download/1.4.1/AsusSMC-1.4.1-RELEASE.zip"
            },
            {
                "product_name": "AtherosE2200Ethernet", 
                "id": 9746382, 
                "url": "https://github.com/Mieze/AtherosE2200Ethernet/releases/download/2.2.2/AtherosE2200Ethernet-V2.2.2.zip"
            },
            {
                "product_name": "BigSurface", 
                "id": 18528518, 
                "url": "https://github.com/Xiashangning/BigSurface/releases/download/v6.5/BigSurface.zip"
            },
            {
                "product_name": "CtlnaAHCIPort", 
                "id": 10460478, 
                "url": "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/CtlnaAHCIPort-v3.4.1.zip"
            },
            {
                "product_name": "CpuTopologyRebuild", 
                "id": 13190749, 
                "url": "https://github.com/b00t0x/CpuTopologyRebuild/releases/download/1.1.0/CpuTopologyRebuild-1.1.0-RELEASE.zip"
            },
            {
                "product_name": "IO80211FamilyLegacy", 
                "id": 817294638, 
                "url": "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Wifi/IO80211FamilyLegacy-v1.0.0.zip"
            },
            {
                "product_name": "IOSkywalkFamily", 
                "id": 926584761, 
                "url": "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Wifi/IOSkywalkFamily-v1.2.0.zip"
            },
            {
                "product_name": "LucyRTL8125Ethernet", 
                "id": 159470181, 
                "url": "https://github.com/Mieze/LucyRTL8125Ethernet/releases/download/v1.2.0d5/LucyRTL8125Ethernet-V1.2.0d5.zip"
            },
            {
                "product_name": "NullEthernet", 
                "id": 182736492, 
                "url": "https://bitbucket.org/RehabMan/os-x-null-ethernet/downloads/RehabMan-NullEthernet-2016-1220.zip"
            },
            {
                "product_name": "VoodooRMI", 
                "id": 13190749, 
                "url": "https://github.com/VoodooSMBus/VoodooRMI/releases/download/1.3.5/VoodooRMI-1.3.5-Release.zip"
            },
            {
                "product_name": "RealtekRTL8100", 
                "id": 10460478, 
                "url": "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/RealtekRTL8100-v2.0.1.zip"
            },
            {
                "product_name": "RealtekCardReader", 
                "id": 10460478, 
                "url": "https://github.com/0xFireWolf/RealtekCardReader/releases/download/v0.9.7/RealtekCardReader_0.9.7_006a845_RELEASE.zip"
            },
            {
                "product_name": "RealtekCardReaderFriend", 
                "id": 10460478, 
                "url": "https://github.com/0xFireWolf/RealtekCardReaderFriend/releases/download/v1.0.4/RealtekCardReaderFriend_1.0.4_e1e3301_RELEASE.zip"
            },
            {
                "product_name": "GenericUSBXHCI", 
                "id": 120325166, 
                "url": "https://github.com/RattletraPM/GUX-RyzenXHCIFix/releases/download/v1.3.0b1-ryzenxhcifix/GenericUSBXHCI.kext.zip"
            },
            {
                "product_name": "XHCI-unsupported", 
                "id": 185465401, 
                "url": "https://github.com/daliansky/OS-X-USB-Inject-All/releases/download/v0.8.0/XHCI-unsupported.kext.zip"
            }
        ]

        dortania_builds_data = self.fetcher.fetch_and_parse_content(self.dortania_builds_url, "json")

        for product_name, product_data in dortania_builds_data.items():
            if product_name in self.builds:
                results.append({
                    "product_name": product_name, 
                    "id": product_data["versions"][0]["release"]["id"], 
                    "url": product_data["versions"][0]["links"]["release"]
                })

        for product in self.releases:
            results.extend(self.github.get_latest_release(product["owner"], product["repo"]))
        # [self.github.get_latest_artifact_id(product["owner"], product["repo"]) for product in self.actions]
        
        sorted_results = sorted(results, key=lambda x:x["product_name"])
    
        return sorted_results
    
    def product_index_in_history(self, product_name, versions):
        for index, item in enumerate(versions):
            if product_name in item["product_name"]:
                return index
        return None
    
    def move_bootloader_kexts_to_product_directory(self, product_name):
        if not os.path.exists(self.temporary_dir):
            raise FileNotFoundError("The directory {} does not exist.".format(self.temporary_dir))
        
        if not "OpenCore" in product_name:
            kext_paths = self.utils.find_matching_paths(os.path.join(self.temporary_dir, product_name), ".kext")
            for kext_path in kext_paths:
                source_kext_path = os.path.join(self.temporary_dir, product_name, kext_path)
                destination_kext_path = os.path.join(self.ock_files_dir, product_name, os.path.basename(kext_path))
                
                if "Contents" in kext_path or "Debug".lower() in kext_path.lower():
                    continue
                
                shutil.move(source_kext_path, destination_kext_path)
        else:
            source_bootloader_path = os.path.join(self.temporary_dir, product_name, "X64", "EFI")
            if os.path.exists(source_bootloader_path):
                destination_efi_path = os.path.join(self.ock_files_dir, product_name, os.path.basename(source_bootloader_path))
                shutil.move(source_bootloader_path, destination_efi_path)
                source_config_path = os.path.join(os.path.dirname(os.path.dirname(source_bootloader_path)), "Docs", "Sample.plist")
                destination_config_path = os.path.join(destination_efi_path, "OC", "config.plist")
                shutil.move(source_config_path, destination_config_path)
            macserial_paths = self.utils.find_matching_paths(os.path.join(self.temporary_dir, product_name), target_name_pattern="macserial")
            if macserial_paths:
                for macserial_path in macserial_paths:
                    source_macserial_path = os.path.join(self.temporary_dir, product_name, macserial_path)
                    destination_macserial_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(macserial_path))
                    shutil.move(source_macserial_path, destination_macserial_path)
                    if os.name != "nt":
                        subprocess.run(["chmod", "+x", destination_macserial_path])
            else:
                raise FileNotFoundError("No bootloader or kexts files found in the product directory.")
        
        return True

    def gathering_bootloader_kexts(self):
        download_history = self.utils.read_file(self.download_history_file) or {
            "versions": [],
            "last_updated": "2024-07-25T12:00:00"
        }

        if not download_history.get("versions"):
            download_history["versions"] = []
        last_updated = datetime.fromisoformat(download_history.get("last_updated", "2024-07-25T12:00:00"))

        current_time = datetime.now()
        if current_time - last_updated < timedelta(minutes=10):
            return
        
        ock_data = self.get_bootloader_kexts_data()

        self.utils.create_folder(self.temporary_dir)

        for product_data in ock_data:
        
            product_index = self.product_index_in_history(product_data.get("product_name"), download_history.get("versions"))
            if not product_index is None and product_data.get("id") == download_history.get("versions")[product_index].get("id"):
                continue

            asset_dir = os.path.join(self.ock_files_dir, product_data.get("product_name"))
            self.utils.create_folder(asset_dir, remove_content=True)

            zip_path = os.path.join(self.temporary_dir, product_data.get("product_name")) + ".zip"
            self.fetcher.download_and_save_file(product_data.get("url"), zip_path)
            self.utils.extract_zip_file(zip_path)

            if self.move_bootloader_kexts_to_product_directory(product_data.get("product_name")):
                if product_index is None:
                    download_history["versions"].append({
                        "product_name": product_data.get("product_name"),
                        "id": product_data.get("id")
                    })
                else:
                    download_history["versions"][product_index]["id"] = product_data.get("id")
                
                self.utils.write_file(self.download_history_file, download_history)

        current_time = datetime.now().isoformat()
        download_history["last_updated"] = current_time

        self.utils.write_file(self.download_history_file, download_history)

        shutil.rmtree(self.temporary_dir, ignore_errors=True)
    
    def get_amd_kernel_patches(self):
        self.utils.head("Gathering Files")
        print("")
        print("Please wait for download AMD Vanilla Patches")
        print("from " + self.amd_vanilla_patches_url)
        print("")
        
        try:
            response = self.fetcher.fetch_and_parse_content(self.amd_vanilla_patches_url, "plist")

            return response["Kernel"]["Patch"]
        except: 
            print(self.utils.message("Unable to download AMD Vanilla Patches at this time.\nPlease try again later or apply them manually", "warning"))
            print("")
            self.utils.request_input()
            return []