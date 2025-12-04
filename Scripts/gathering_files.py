from Scripts import github
from Scripts import kext_maestro
from Scripts import integrity_checker
from Scripts import resource_fetcher
from Scripts import utils
import os
import shutil
import subprocess
import platform

os_name = platform.system()

class gatheringFiles:
    def __init__(self):
        self.utils = utils.Utils()
        self.github = github.Github(utils_instance=self.utils)
        self.kext = kext_maestro.KextMaestro()
        self.fetcher = resource_fetcher.ResourceFetcher(utils_instance=self.utils)
        self.integrity_checker = integrity_checker.IntegrityChecker()
        self.dortania_builds_url = "https://raw.githubusercontent.com/dortania/build-repo/builds/latest.json"
        self.ocbinarydata_url = "https://github.com/acidanthera/OcBinaryData/archive/refs/heads/master.zip"
        self.amd_vanilla_patches_url = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/beta/patches.plist"
        self.aquantia_macos_patches_url = "https://raw.githubusercontent.com/CaseySJ/Aquantia-macOS-Patches/refs/heads/main/CaseySJ-Aquantia-Patch-Sets-1-and-2.plist"
        self.hyper_threading_patches_url = "https://github.com/b00t0x/CpuTopologyRebuild/raw/refs/heads/master/patches_ht.plist"
        self.temporary_dir = self.utils.get_temporary_dir()
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.download_history_file = os.path.join(self.ock_files_dir, "history.json")

    def get_product_index(self, product_list, product_name_name):
        for index, product in enumerate(product_list):
            if product_name_name == product.get("product_name"):
                return index
        return None
        
    def update_download_database(self, kexts, download_history):
        download_database = download_history.copy()
        dortania_builds_data = self.fetcher.fetch_and_parse_content(self.dortania_builds_url, "json")
        seen_repos = set()

        def add_product_to_download_database(products):
            if isinstance(products, dict):
                products = [products]

            for product in products:
                if not product or not product.get("product_name"):
                    continue

                product_index = self.get_product_index(download_database, product.get("product_name"))

                if product_index is None:
                    download_database.append(product)
                else:
                    download_database[product_index].update(product)

        for kext in kexts:
            if not kext.checked:
                continue

            if kext.download_info:
                if not kext.download_info.get("sha256"):
                    kext.download_info["sha256"] = None
                add_product_to_download_database({"product_name": kext.name, **kext.download_info})
            elif kext.github_repo and kext.github_repo.get("repo") not in seen_repos:
                name = kext.github_repo.get("repo")
                seen_repos.add(name)
                if name != "IntelBluetoothFirmware" and name in dortania_builds_data:
                    add_product_to_download_database({
                        "product_name": name,
                        "id": dortania_builds_data[name]["versions"][0]["release"]["id"], 
                        "url": dortania_builds_data[name]["versions"][0]["links"]["release"],
                        "sha256": dortania_builds_data[name]["versions"][0]["hashes"]["release"]["sha256"]
                    })
                else:
                    latest_release = self.github.get_latest_release(kext.github_repo.get("owner"), kext.github_repo.get("repo")) or {}
                    add_product_to_download_database(latest_release.get("assets"))

        add_product_to_download_database({
            "product_name": "OpenCorePkg",
            "id": dortania_builds_data["OpenCorePkg"]["versions"][0]["release"]["id"], 
            "url": dortania_builds_data["OpenCorePkg"]["versions"][0]["links"]["release"],
            "sha256": dortania_builds_data["OpenCorePkg"]["versions"][0]["hashes"]["release"]["sha256"]
        })

        return sorted(download_database, key=lambda x:x["product_name"])
    
    def move_bootloader_kexts_to_product_directory(self, product_name):
        if not os.path.exists(self.temporary_dir):
            raise FileNotFoundError(f"The directory {self.temporary_dir} does not exist.")
        
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

        download_database = self.update_download_database(kexts, download_history)
        
        self.utils.create_folder(self.temporary_dir)

        seen_download_urls = set()
        
        # Calculate total number of products to download for progress tracking
        total_products = 0
        products_to_download = []
        
        # First pass: collect products that need to be downloaded
        all_products = kexts + [{"Name": "OpenCorePkg"}]
        
        for product in all_products:
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
            elif product_name == "UTBDefault":
                product_name = "USBToolBox"

            product_download_index = self.get_product_index(download_database, product_name)
            if product_download_index is None:
                if hasattr(product, 'github_repo') and product.github_repo:
                    product_download_index = self.get_product_index(download_database, product.github_repo.get("repo"))
            
            if product_download_index is None:
                print("\n")
                print(f"Could not find download URL for {product_name}.")
                continue

            product_info = download_database[product_download_index]
            product_id = product_info.get("id")
            product_download_url = product_info.get("url")
            sha256_hash = product_info.get("sha256")

            if product_download_url in seen_download_urls:
                continue
            seen_download_urls.add(product_download_url)

            product_history_index = self.get_product_index(download_history, product_name)
            asset_dir = os.path.join(self.ock_files_dir, product_name)
            manifest_path = os.path.join(asset_dir, "manifest.json")

            if product_history_index is not None:
                history_item = download_history[product_history_index]
                is_latest_id = (product_id == history_item.get("id"))
                folder_is_valid, _ = self.integrity_checker.verify_folder_integrity(asset_dir, manifest_path)
                
                if is_latest_id and folder_is_valid:
                    # Skip this product - already up to date
                    if self.utils.gui_callback:
                        # In GUI mode, just print a brief message
                        print(f"✓ {product_name} already up to date")
                    else:
                        # In CLI mode, show the standard message
                        print(f"\nLatest version of {product_name} already downloaded.")
                    continue
            
            # Add to products to download list
            products_to_download.append({
                'product': product,
                'product_name': product_name,
                'product_id': product_id,
                'product_download_url': product_download_url,
                'sha256_hash': sha256_hash,
                'product_history_index': product_history_index,
                'asset_dir': asset_dir,
                'manifest_path': manifest_path
            })
        
        total_products = len(products_to_download)
        
        # Second pass: actually download the products with progress tracking
        for index, download_item in enumerate(products_to_download):
            product = download_item['product']
            product_name = download_item['product_name']
            product_id = download_item['product_id']
            product_download_url = download_item['product_download_url']
            sha256_hash = download_item['sha256_hash']
            product_history_index = download_item['product_history_index']
            asset_dir = download_item['asset_dir']
            manifest_path = download_item['manifest_path']
            
            # Update progress for GUI mode
            if self.utils.gui_callback and hasattr(self.utils, 'gui_gathering_progress_callback'):
                progress_info = {
                    'current': index + 1,
                    'total': total_products,
                    'product_name': product_name,
                    'status': 'downloading'
                }
                self.utils.gui_gathering_progress_callback(progress_info)

            print("")
            print(f"Downloading {index + 1}/{total_products}: {product_name}")
            if product_download_url:
                print(f"from {product_download_url}")
                print("")
            else:
                print("")
                print(f"Could not find download URL for {product_name}.")
                print("")
                # Only show "Press Enter to continue" prompt in CLI mode
                if not self.utils.gui_callback:
                    self.utils.request_input()
                shutil.rmtree(self.temporary_dir, ignore_errors=True)
                return False

            zip_path = os.path.join(self.temporary_dir, product_name) + ".zip"
            if not self.fetcher.download_and_save_file(product_download_url, zip_path, sha256_hash):
                folder_is_valid, _ = self.integrity_checker.verify_folder_integrity(asset_dir, manifest_path)
                if product_history_index is not None and folder_is_valid:
                    print(f"Using previously downloaded version of {product_name}.")
                    continue
                else:
                    raise Exception(f"Could not download {product_name} at this time. Please try again later.")
            
            print(f"Extracting {product_name}...")
            self.utils.extract_zip_file(zip_path)
            self.utils.create_folder(asset_dir, remove_content=True)
            
            # Extract nested zips
            while True:
                nested_zip_files = self.utils.find_matching_paths(os.path.join(self.temporary_dir, product_name), extension_filter=".zip")
                if not nested_zip_files:
                    break
                for zip_file, _ in nested_zip_files:
                    full_zip_path = os.path.join(self.temporary_dir, product_name, zip_file)
                    self.utils.extract_zip_file(full_zip_path)
                    os.remove(full_zip_path)

            if "OpenCore" in product_name:
                # Update progress for OcBinaryData download
                if self.utils.gui_callback and hasattr(self.utils, 'gui_gathering_progress_callback'):
                    progress_info = {
                        'current': index + 1,
                        'total': total_products,
                        'product_name': 'OcBinaryData (for OpenCore)',
                        'status': 'downloading'
                    }
                    self.utils.gui_gathering_progress_callback(progress_info)
                
                oc_binary_data_zip_path = os.path.join(self.temporary_dir, "OcBinaryData.zip")
                print("")
                print("Downloading OcBinaryData...")
                print(f"from {self.ocbinarydata_url}")
                print("")
                self.fetcher.download_and_save_file(self.ocbinarydata_url, oc_binary_data_zip_path)

                if not os.path.exists(oc_binary_data_zip_path):
                    print("")
                    print("Could not download OcBinaryData at this time.")
                    print("Please try again later.\n")
                    # Only show "Press Enter to continue" prompt in CLI mode
                    if not self.utils.gui_callback:
                        self.utils.request_input()
                    shutil.rmtree(self.temporary_dir, ignore_errors=True)
                    return False
                
                print("Extracting OcBinaryData...")
                self.utils.extract_zip_file(oc_binary_data_zip_path)
            
            # Update progress for processing
            if self.utils.gui_callback and hasattr(self.utils, 'gui_gathering_progress_callback'):
                progress_info = {
                    'current': index + 1,
                    'total': total_products,
                    'product_name': product_name,
                    'status': 'processing'
                }
                self.utils.gui_gathering_progress_callback(progress_info)
            
            print(f"Processing {product_name}...")
            if self.move_bootloader_kexts_to_product_directory(product_name):
                self.integrity_checker.generate_folder_manifest(asset_dir, manifest_path)
                self._update_download_history(download_history, product_name, product_id, product_download_url, sha256_hash)

        shutil.rmtree(self.temporary_dir, ignore_errors=True)
        
        # Final progress update for GUI
        if self.utils.gui_callback and hasattr(self.utils, 'gui_gathering_progress_callback'):
            progress_info = {
                'current': total_products,
                'total': total_products,
                'product_name': 'Complete',
                'status': 'complete'
            }
            self.utils.gui_gathering_progress_callback(progress_info)
        
        print("")
        print("All files gathered successfully!")
        return True
    
    def get_kernel_patches(self, patches_name, patches_url):
        try:
            response = self.fetcher.fetch_and_parse_content(patches_url, "plist")

            return response["Kernel"]["Patch"]
        except: 
            print("")
            print(f"Unable to download {patches_name} at this time")
            print("from " + patches_url)
            print("")
            print("Please try again later or apply them manually.")
            print("")
            # Only show "Press Enter to continue" prompt in CLI mode
            if not self.utils.gui_callback:
                self.utils.request_input()
            return []
        
    def _update_download_history(self, download_history, product_name, product_id, product_url, sha256_hash):
        product_history_index = self.get_product_index(download_history, product_name)
        
        entry = {
            "product_name": product_name, 
            "id": product_id,
            "url": product_url,
            "sha256": sha256_hash
        }

        if product_history_index is None:
            download_history.append(entry)
        else:
            download_history[product_history_index].update(entry)
        
        self.utils.create_folder(os.path.dirname(self.download_history_file))
        self.utils.write_file(self.download_history_file, download_history)
        
    def gather_hardware_sniffer(self):
        if os_name != "Windows":
            return

        self.utils.head("Gathering Hardware Sniffer")

        PRODUCT_NAME = "Hardware-Sniffer-CLI.exe"
        REPO_OWNER = "lzhoang2801"
        REPO_NAME = "Hardware-Sniffer"

        destination_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), PRODUCT_NAME)
        
        latest_release = self.github.get_latest_release(REPO_OWNER, REPO_NAME) or {}
        
        product_id = None
        product_download_url = None
        sha256_hash = None

        asset_name = PRODUCT_NAME.split('.')[0]
        for asset in latest_release.get("assets", []):
            if asset.get("product_name") == asset_name:
                product_id = asset.get("id")
                product_download_url = asset.get("url")
                sha256_hash = asset.get("sha256")
                break

        if not all([product_id, product_download_url, sha256_hash]):
            print("")
            print(f"Could not find release information for {PRODUCT_NAME}.")
            print("Please try again later.")
            print("")
            self.utils.request_input()
            raise Exception(f"Could not find release information for {PRODUCT_NAME}.")

        download_history = self.utils.read_file(self.download_history_file)
        if not isinstance(download_history, list):
            download_history = []

        product_history_index = self.get_product_index(download_history, PRODUCT_NAME)
        
        if product_history_index is not None:
            history_item = download_history[product_history_index]
            is_latest_id = (product_id == history_item.get("id"))
            
            file_is_valid = False
            if os.path.exists(destination_path):
                local_hash = self.integrity_checker.get_sha256(destination_path)
                file_is_valid = (sha256_hash == local_hash)

            if is_latest_id and file_is_valid:
                print("")
                print(f"Latest version of {PRODUCT_NAME} already downloaded.")
                return destination_path

        print("")
        print("Updating" if product_history_index is not None else "Please wait for download", end=" ")
        print(f"{PRODUCT_NAME}...")
        print("")
        print(f"from {product_download_url}")
        print("")
        
        if not self.fetcher.download_and_save_file(product_download_url, destination_path, sha256_hash):
            manual_download_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest"
            print(f"Go to {manual_download_url} to download {PRODUCT_NAME} manually.")
            print("")
            self.utils.request_input()
            raise Exception(f"Failed to download {PRODUCT_NAME}.")

        self._update_download_history(download_history, PRODUCT_NAME, product_id, product_download_url, sha256_hash)
        
        return destination_path