from Scripts import github
from Scripts import kext_maestro
from Scripts import resource_fetcher
from Scripts import utils
import os
import tempfile
import shutil
import subprocess
import platform

os_name = platform.system()

class gatheringFiles:
    def __init__(self):
        self.utils = utils.Utils()
        self.github = github.Github()
        self.kext = kext_maestro.KextMaestro()
        self.fetcher = resource_fetcher.ResourceFetcher()
        self.dortania_builds_url = "https://raw.githubusercontent.com/dortania/build-repo/builds/latest.json"
        self.ocbinarydata_url = "https://github.com/acidanthera/OcBinaryData/archive/refs/heads/master.zip"
        self.amd_vanilla_patches_url = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/beta/patches.plist"
        self.aquantia_macos_patches_url = "https://raw.githubusercontent.com/CaseySJ/Aquantia-macOS-Patches/refs/heads/main/CaseySJ-Aquantia-Patch-Sets-1-and-2.plist"
        self.hyper_threading_patches_url = "https://github.com/b00t0x/CpuTopologyRebuild/raw/refs/heads/master/patches_ht.plist"
        self.temporary_dir = tempfile.mkdtemp()
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.bootloader_kexts_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "bootloader_kexts_data.json")
        self.download_history_file = os.path.join(self.ock_files_dir, "history.json")

    def get_product_index(self, product_list, product_name_name):
        for index, product in enumerate(product_list):
            if product_name_name == product.get("product_name"):
                return index
        return None
        
    def get_bootloader_kexts_data(self, kexts):
        download_urls = self.utils.read_file(self.bootloader_kexts_data_path)

        if not isinstance(download_urls, list):
            download_urls = []

        dortania_builds_data = self.fetcher.fetch_and_parse_content(self.dortania_builds_url, "json")
        seen_repos = set()

        def add_product_to_download_urls(products):
            if isinstance(products, dict):
                products = [products]

            for product in products:
                product_index = self.get_product_index(download_urls, product.get("product_name"))

                if product_index is None:
                    download_urls.append(product)
                else:
                    download_urls[product_index] = product

        for kext in kexts:
            if not kext.checked:
                continue

            if kext.download_info:
                add_product_to_download_urls({"product_name": kext.name, **kext.download_info})
            elif kext.github_repo and kext.github_repo.get("repo") not in seen_repos:
                name = kext.github_repo.get("repo")
                seen_repos.add(name)
                if name in dortania_builds_data:
                    add_product_to_download_urls({
                        "product_name": name,
                        "id": dortania_builds_data[name]["versions"][0]["release"]["id"], 
                        "url": dortania_builds_data[name]["versions"][0]["links"]["release"]
                    })
                else:
                    latest_release = self.github.get_latest_release(kext.github_repo.get("owner"), kext.github_repo.get("repo")) or {}
                    add_product_to_download_urls(latest_release.get("assets"))

        add_product_to_download_urls({
            "product_name": "OpenCorePkg",
            "id": dortania_builds_data["OpenCorePkg"]["versions"][0]["release"]["id"], 
            "url": dortania_builds_data["OpenCorePkg"]["versions"][0]["links"]["release"]
        })

        sorted_download_urls = sorted(download_urls, key=lambda x:x["product_name"])

        self.utils.create_folder(self.ock_files_dir)
        self.utils.write_file(self.bootloader_kexts_data_path, sorted_download_urls)
    
        return sorted_download_urls
    
    def move_bootloader_kexts_to_product_directory(self, product_name):
        if not os.path.exists(self.temporary_dir):
            raise FileNotFoundError("The directory {} does not exist.".format(self.temporary_dir))
        
        temp_product_dir = os.path.join(self.temporary_dir, product_name)
        
        if not "OpenCore" in product_name:
            kext_paths = self.utils.find_matching_paths(temp_product_dir, extension_filter=".kext")
            for kext_path, type in kext_paths:
                source_kext_path = os.path.join(self.temporary_dir, product_name, kext_path)
                destination_kext_path = os.path.join(self.ock_files_dir, product_name, os.path.basename(kext_path))
                
                if "debug" in kext_path.lower() or "Contents" in kext_path or not self.kext.process_kext(temp_product_dir, kext_path):
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

            ocbinarydata_dir = os.path.join(self.temporary_dir, "OcBinaryData", "OcBinaryData-master")
            if os.path.exists(ocbinarydata_dir):
                background_picker_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "datasets", "background_picker.icns")
                product_dir = os.path.join(self.ock_files_dir, product_name)
                efi_dirs = self.utils.find_matching_paths(product_dir, name_filter="EFI", type_filter="dir")

                for efi_dir, _ in efi_dirs:
                    for dir_name in os.listdir(ocbinarydata_dir):
                        source_dir = os.path.join(ocbinarydata_dir, dir_name)
                        destination_dir = os.path.join(destination_efi_path, "OC", dir_name)
                        if os.path.isdir(destination_dir):
                            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

                    resources_image_dir = os.path.join(product_dir, efi_dir, "OC", "Resources", "Image")
                    picker_variants = self.utils.find_matching_paths(resources_image_dir, type_filter="dir")
                    for picker_variant, _ in picker_variants:
                        if ".icns" in ", ".join(os.listdir(os.path.join(resources_image_dir, picker_variant))):
                            shutil.copy(background_picker_path, os.path.join(resources_image_dir, picker_variant, "Background.icns"))

            macserial_paths = self.utils.find_matching_paths(temp_product_dir, name_filter="macserial", type_filter="file")
            if macserial_paths:
                for macserial_path, _ in macserial_paths:
                    source_macserial_path = os.path.join(self.temporary_dir, product_name, macserial_path)
                    destination_macserial_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(macserial_path))
                    shutil.move(source_macserial_path, destination_macserial_path)
                    if os.name != "nt":
                        subprocess.run(["chmod", "+x", destination_macserial_path])
        
        return True
    
    def gather_bootloader_kexts(self, kexts, macos_version):
        self.utils.head("Gathering Files")
        print("")
        print("Please wait for download OpenCorePkg, kexts and macserial...")

        download_history = self.utils.read_file(self.download_history_file)

        if not isinstance(download_history, list):
            download_history = []

        bootloader_kext_urls = self.get_bootloader_kexts_data(kexts)
        
        self.utils.create_folder(self.temporary_dir)

        seen_download_urls = set()

        for product in kexts + [{"Name": "OpenCorePkg"}]:
            if not isinstance(product, dict) and not product.checked:
                continue

            product_name = product.name if not isinstance(product, dict) else product.get("Name")
            
            if product_name == "AirportItlwm":
                version = macos_version[:2]
                if all((kexts[kext_maestro.kext_data.kext_index_by_name.get("IOSkywalkFamily")].checked, kexts[kext_maestro.kext_data.kext_index_by_name.get("IO80211FamilyLegacy")].checked)) or self.utils.parse_darwin_version("24.0.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "22"
                elif self.utils.parse_darwin_version("23.4.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "23.4"
                elif self.utils.parse_darwin_version("23.0.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "23.0"
                product_name += version
            elif "VoodooPS2" in product_name:
                product_name = "VoodooPS2"
            elif product_name == "BlueToolFixup" or product_name.startswith("Brcm"):
                product_name = "BrcmPatchRAM"
            elif product_name.startswith("Ath3kBT"):
                product_name = "Ath3kBT"
            elif product_name.startswith("IntelB"):
                product_name = "IntelBluetoothFirmware"
            elif product_name.startswith("VoodooI2C"):
                product_name = "VoodooI2C"

            product_download_index = self.get_product_index(bootloader_kext_urls, product_name)
            if product_download_index is None:
                if product.github_repo:
                    product_download_index = self.get_product_index(bootloader_kext_urls, product.github_repo.get("repo"))
            
            if product_download_index is not None:
                _, product_id, product_download_url = bootloader_kext_urls[product_download_index].values()

                if product_download_url in seen_download_urls:
                    continue
                seen_download_urls.add(product_download_url)
            else:
                product_id = product_download_url = None

            product_history_index = self.get_product_index(download_history, product_name)

            print("")
            if product_history_index is None:
                print("Please wait for download {}...".format(product_name))
            else:
                if product_id == download_history[product_history_index].get("id"):
                    print("Latest version of {} already downloaded.".format(product_name))
                    continue
                else:
                    print("Updating {}...".format(product_name))

            if product_download_url is not None:
                print("from " + product_download_url)
            else:
                print("Could not find download URL for {}.".format(product_name))
                print("Please try again later.")
                print("")
                self.utils.request_input()
                shutil.rmtree(self.temporary_dir, ignore_errors=True)
                return False
            print("")

            zip_path = os.path.join(self.temporary_dir, product_name) + ".zip"
            self.fetcher.download_and_save_file(product_download_url, zip_path)

            if not os.path.exists(zip_path):
                if product_history_index is not None:
                    print("Using previously version of {}.".format(product_name))
                    continue
                else:
                    print("")
                    print("Could not download {} at this time.".format(product_name))
                    print("Please try again later.")
                    print("")
                    self.utils.request_input()
                    shutil.rmtree(self.temporary_dir, ignore_errors=True)
                    return False
                
            self.utils.extract_zip_file(zip_path)

            asset_dir = os.path.join(self.ock_files_dir, product_name)
            self.utils.create_folder(asset_dir, remove_content=True)
            
            while True:
                zip_files = self.utils.find_matching_paths(os.path.join(self.temporary_dir, product_name), extension_filter=".zip")

                if not zip_files:
                    break

                for zip_file, file_type in zip_files:
                    full_zip_path = os.path.join(self.temporary_dir, product_name, zip_file)
                    self.utils.extract_zip_file(full_zip_path)
                    os.remove(full_zip_path)

            if "OpenCore" in product_name:
                zip_path = os.path.join(self.temporary_dir, "OcBinaryData.zip")
                print("")
                print("Please wait for download OcBinaryData...")
                print("from " + self.ocbinarydata_url)
                print("")
                self.fetcher.download_and_save_file(self.ocbinarydata_url, zip_path)

                if not os.path.exists(zip_path):
                    print("")
                    print("Could not download OcBinaryData at this time.")
                    print("Please try again later.")
                    print("")
                    self.utils.request_input()
                    shutil.rmtree(self.temporary_dir, ignore_errors=True)
                    return False
                
                self.utils.extract_zip_file(zip_path)

            if self.move_bootloader_kexts_to_product_directory(product_name):
                if product_history_index is None:
                    download_history.append({
                        "product_name": product_name, 
                        "id": product_id
                    })
                else:
                    download_history[product_history_index]["id"] = product_id
                
                self.utils.write_file(self.download_history_file, download_history)

        shutil.rmtree(self.temporary_dir, ignore_errors=True)
        return True
    
    def get_kernel_patches(self, patches_name, patches_url):
        try:
            response = self.fetcher.fetch_and_parse_content(patches_url, "plist")

            return response["Kernel"]["Patch"]
        except: 
            print("")
            print("Unable to download {} at this time".format(patches_name))
            print("from " + patches_url)
            print("")
            print("Please try again later or apply them manually.")
            print("")
            self.utils.request_input()
            return []
        
    def gather_hardware_sniffer(self):
        if os_name != "Windows":
            return
        
        self.utils.head("Gathering Files")
        print("")
        print("Please wait for download Hardware Sniffer")
        print("")

        product_name = "Hardware-Sniffer-CLI.exe"

        hardware_sniffer_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), product_name)

        download_history = self.utils.read_file(self.download_history_file)

        if not isinstance(download_history, list):
            download_history = []

        product_id = product_download_url = None 

        latest_release = self.github.get_latest_release("lzhoang2801", "Hardware-Sniffer") or {}

        for product in latest_release.get("assets"):
            if product.get("product_name") == product_name.split(".")[0]:
                _, product_id, product_download_url = product.values()
        
        product_history_index = self.get_product_index(download_history, product_name)

        print("")
        if product_history_index == None:
            print("Please wait for download {}...".format(product_name))
        else:
            if product_id == download_history[product_history_index].get("id") and os.path.exists(hardware_sniffer_path):
                print("Latest version of {} already downloaded.".format(product_name))
                return hardware_sniffer_path
            else:
                print("Updating {}...".format(product_name))

        if product_download_url:
            print("from " + product_download_url)
        else:
            print("Could not find download URL for {}.".format(product_name))
            print("Please try again later.")
            print("")
            self.utils.request_input()
            return
        print("")

        self.fetcher.download_and_save_file(product_download_url, hardware_sniffer_path)
        
        if product_history_index is None:
            download_history.append({
                "product_name": product_name, 
                "id": product_id
            })
        else:
            download_history[product_history_index]["id"] = product_id
        
        self.utils.create_folder(os.path.dirname(self.download_history_file))
        self.utils.write_file(self.download_history_file, download_history)

        return hardware_sniffer_path