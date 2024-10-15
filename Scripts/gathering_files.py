from Scripts import github
from Scripts import resource_fetcher
from Scripts import utils
import os
import tempfile
import shutil
import subprocess

class gatheringFiles:
    def __init__(self):
        self.utils = utils.Utils()
        self.github = github.Github()
        self.fetcher = resource_fetcher.ResourceFetcher()
        self.dortania_builds_url = "https://raw.githubusercontent.com/dortania/build-repo/builds/latest.json"
        self.ocbinarydata_url = "https://github.com/acidanthera/OcBinaryData/archive/refs/heads/master.zip"
        self.amd_vanilla_patches_url = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/beta/patches.plist"
        self.temporary_dir = tempfile.mkdtemp()
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.bootloader_kexts_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "bootloader_kexts_data.json")
        self.download_history_file = os.path.join(self.ock_files_dir, "history.json")

    def get_product_index(self, product_list, target_product_name):
        for index, product in enumerate(product_list):
            if target_product_name == product.get("product_name"):
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
                    if self.github.check_ratelimit():
                        add_product_to_download_urls(self.github.get_latest_release(kext.github_repo.get("owner"), kext.github_repo.get("repo")))

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
        
        if not "OpenCore" in product_name:
            kext_paths = self.utils.find_matching_paths(os.path.join(self.temporary_dir, product_name), extension_filter=".kext")
            for kext_path, type in kext_paths:
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

                ocbinarydata_dir = os.path.join(self.temporary_dir, "OcBinaryData", "OcBinaryData-master")
                background_picker_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "datasets", "background_picker.icns")
                if os.path.exists(ocbinarydata_dir):
                    for name in os.listdir(ocbinarydata_dir):
                        if name.startswith("."):
                            continue
                        shutil.copytree(os.path.join(ocbinarydata_dir, name), os.path.join(destination_efi_path, "OC", name), dirs_exist_ok=True)
                    resources_image_dir = os.path.join(destination_efi_path, "OC", "Resources", "Image")
                    picker_variants = self.utils.find_matching_paths(resources_image_dir, type_filter="dir")
                    for picker_variant, type in picker_variants:
                        if ".icns" in ", ".join(os.listdir(os.path.join(resources_image_dir, picker_variant))):
                            shutil.copy(background_picker_path, os.path.join(resources_image_dir, picker_variant, "Background.icns"))

            macserial_paths = self.utils.find_matching_paths(os.path.join(self.temporary_dir, product_name), name_filter="macserial", type_filter="file")
            if macserial_paths:
                for macserial_path, type in macserial_paths:
                    source_macserial_path = os.path.join(self.temporary_dir, product_name, macserial_path)
                    destination_macserial_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(macserial_path))
                    shutil.move(source_macserial_path, destination_macserial_path)
                    if os.name != "nt":
                        subprocess.run(["chmod", "+x", destination_macserial_path])
            else:
                raise FileNotFoundError("No bootloader or kexts files found in the product directory.")
        
        return True
    
    def gather_bootloader_kexts(self, kexts, macos_version):
        download_history = self.utils.read_file(self.download_history_file)

        if not isinstance(download_history, list):
            download_history = []

        bootloader_kext_urls = self.utils.read_file(self.bootloader_kexts_data_path)

        if not isinstance(bootloader_kext_urls, list):
            bootloader_kext_urls = self.get_bootloader_kexts_data(kexts)
        
        self.utils.create_folder(self.temporary_dir)

        for product in kexts + [{"Name": "OpenCorePkg"}]:
            if not isinstance(product, dict) and not product.checked:
                continue

            product_name = product.name if not isinstance(product, dict) else product.get("Name")
            
            if product_name == "AirportItlwm":
                version = macos_version[:2]
                if self.utils.parse_darwin_version("23.4.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "23.4"
                elif self.utils.parse_darwin_version("23.0.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "23.0"
                product_name += version
            elif "VoodooPS2" in product_name:
                product_name = "VoodooPS2"
            elif product_name == "BlueToolFixup" or product_name.startswith("Brcm"):
                product_name = "BrcmPatchRAM"
            elif product_name.startswith("Intel"):
                product_name = "IntelBluetoothFirmware"
            elif product_name.startswith("VoodooI2C"):
                product_name = "VoodooI2C"
            
            try:
                product_index = self.get_product_index(bootloader_kext_urls, product_name)
                product_download_url = bootloader_kext_urls[product_index].get("url")
                product_id = bootloader_kext_urls[product_index].get("id")
            except:
                continue
            
            history_index = self.get_product_index(download_history, product_name)
            if history_index is not None and product_id == download_history[history_index].get("id"):
                continue

            asset_dir = os.path.join(self.ock_files_dir, product_name)
            self.utils.create_folder(asset_dir, remove_content=True)

            zip_path = os.path.join(self.temporary_dir, product_name) + ".zip"
            self.fetcher.download_and_save_file(product_download_url, zip_path)
            self.utils.extract_zip_file(zip_path)

            if "OpenCore" in product_name:
                ocbinarydata_dir = os.path.join(self.temporary_dir, "OcBinaryData")
                if not os.path.exists(ocbinarydata_dir):
                    zip_path = ocbinarydata_dir + ".zip"
                    self.fetcher.download_and_save_file(self.ocbinarydata_url, zip_path)
                    self.utils.extract_zip_file(zip_path)

            if self.move_bootloader_kexts_to_product_directory(product_name):
                if history_index is None:
                    download_history.append({"product_name": product_name, "id": product_id})
                else:
                    download_history[history_index]["id"] = product_id
                
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
            print("Unable to download AMD Vanilla Patches at this time.")
            print("Please try again later or apply them manually.")
            print("")
            self.utils.request_input()
            return []
        
    def gather_hardware_sniffer(self):
        if os.name != "nt":
            return
        
        self.utils.head("Gathering Files")
        print("")
        print("Please wait for download Hardware Sniffer")
        print("")

        hardware_sniffer_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Hardware-Sniffer-CLI.exe")

        hardware_sniffer_cli = None

        try:            
            download_history = self.utils.read_file(self.download_history_file)

            if not isinstance(download_history, list):
                download_history = []

            for product in self.github.get_latest_release("lzhoang2801", "Hardware-Sniffer"):
                if product.get("product_name") == "Hardware-Sniffer-CLI":
                    hardware_sniffer_cli = product

            history_index = self.get_product_index(download_history, "Hardware-Sniffer-CLI")
            if history_index is not None and hardware_sniffer_cli.get("id") == download_history[history_index].get("id"):
                if os.path.exists(hardware_sniffer_path):
                    return hardware_sniffer_path

            self.fetcher.download_and_save_file(hardware_sniffer_cli.get("url"), hardware_sniffer_path)

            if not os.path.exists(hardware_sniffer_path):
                return
            
            if history_index is None:
                download_history.append({"product_name": "Hardware-Sniffer-CLI", "id": hardware_sniffer_cli.get("id")})
            else:
                download_history[history_index]["id"] = hardware_sniffer_cli.get("id")
            
            self.utils.create_folder(os.path.dirname(self.download_history_file))
            self.utils.write_file(self.download_history_file, download_history)

            return hardware_sniffer_path
        except:
            print("Could not complete download Hardware Sniffer.")
            print("Please download Hardware Sniffer CLI manually and place it in \"Scripts\" folder.")
            if hardware_sniffer_cli:
                print("You can manually download \"Hardware-Sniffer-CLI.exe\" from:\n   {}\n".format(hardware_sniffer_cli.get("url")))
            print("Alternatively, export the hardware report manually to continue.")
            print("")
            self.utils.request_input()
            return