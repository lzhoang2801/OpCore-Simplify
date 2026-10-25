from Scripts import github
from Scripts import kext_maestro
from Scripts import integrity_checker
from Scripts import resource_fetcher
from Scripts import utils
import os
import shutil
import subprocess
import platform
import tempfile

os_name = platform.system()

class gatheringFiles:
    def __init__(self):
        self.utils = utils.Utils()
        self.github = github.Github()
        self.kext = kext_maestro.KextMaestro()
        self.fetcher = resource_fetcher.ResourceFetcher()
        self.integrity_checker = integrity_checker.IntegrityChecker()
        self.dortania_builds_url = "https://raw.githubusercontent.com/dortania/build-repo/builds/latest.json"
        self.ocbinarydata_url = "https://github.com/acidanthera/OcBinaryData/archive/refs/heads/master.zip"
        self.amd_vanilla_patches_url = "https://raw.githubusercontent.com/laobamac/AMD_Vanilla/refs/heads/master/patches.plist"
        self.aquantia_macos_patches_url = "https://raw.githubusercontent.com/CaseySJ/Aquantia-macOS-Patches/refs/heads/main/CaseySJ-Aquantia-Patch-Sets-1-and-2.plist"
        self.hyper_threading_patches_url = "https://github.com/b00t0x/CpuTopologyRebuild/raw/refs/heads/master/patches_ht.plist"
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.download_history_file = os.path.join(self.ock_files_dir, "history.json")

    def _load_download_history(self):
        history_data = self.utils.read_file(self.download_history_file)
        return {item["product_name"]: item for item in history_data if item.get("product_name")} if isinstance(history_data, list) else {}
    
    def _save_download_history(self, local_download_history, product_name, product_id, product_url, sha256_hash):
        history_item = {
            "product_name": product_name, 
            "id": product_id,
            "url": product_url,
            "sha256": sha256_hash
        }
        
        self.utils.create_folder(os.path.dirname(self.download_history_file))
        updated_history = {**local_download_history, product_name: history_item}
        sorted_history = sorted(updated_history.values(), key=lambda x: x.get("product_name", ""))
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(self.download_history_file), suffix=".json", delete=False) as history_file:
            temporary_history_path = history_file.name
        try:
            self.utils.write_file(temporary_history_path, sorted_history)
            os.replace(temporary_history_path, self.download_history_file)
        except OSError as error:
            raise OSError("Could not save download history for {} to {}: {}".format(product_name, self.download_history_file, error)) from error
        finally:
            if os.path.exists(temporary_history_path):
                os.remove(temporary_history_path)
        local_download_history[product_name] = history_item

    def fetch_latest_products_info(self, kexts):
        latest_products = {}
        dortania_builds_data = self.fetcher.fetch_and_parse_content(self.dortania_builds_url, "json")
        if not isinstance(dortania_builds_data, dict) or not dortania_builds_data.get("OpenCorePkg", {}).get("versions"):
            raise ValueError("Could not find download information for OpenCorePkg.")
        seen_repos = set()

        def add_product_info(products):
            if isinstance(products, dict):
                products = [products]

            for product in products or []:
                if not product:
                    continue
                name = product.get("product_name")
                if not name:
                    continue

                latest_products[name] = product.copy()

        for kext in kexts:
            if not kext.checked:
                continue

            if kext.download_info:
                add_product_info({"product_name": kext.name, **kext.download_info})
            elif kext.name == "AirportItlwm-laobamac":
                release = self.github.get_latest_release(kext.github_repo["owner"], kext.github_repo["repo"]) or {}
                for asset in release.get("assets", []):
                    if "-RELEASE" in asset["url"] and asset["product_name"] in ("AirportItlwm24", "AirportItlwm25"):
                        add_product_info({**asset, "product_name": kext.name + asset["product_name"][-2:]})
            elif kext.github_repo:
                repository = (kext.github_repo["owner"], kext.github_repo["repo"])
                if repository in seen_repos:
                    continue
                name = kext.github_repo.get("repo")
                seen_repos.add(repository)
                if name in dortania_builds_data:
                    add_product_info({
                        "product_name": name,
                        "id": dortania_builds_data[name]["versions"][0]["release"]["id"], 
                        "url": dortania_builds_data[name]["versions"][0]["links"]["release"],
                        "sha256": dortania_builds_data[name]["versions"][0]["hashes"]["release"]["sha256"]
                    })
                else:
                    latest_release = self.github.get_latest_release(kext.github_repo.get("owner"), kext.github_repo.get("repo")) or {}
                    add_product_info(latest_release.get("assets"))

        add_product_info({
            "product_name": "OpenCorePkg",
            "id": dortania_builds_data["OpenCorePkg"]["versions"][0]["release"]["id"], 
            "url": dortania_builds_data["OpenCorePkg"]["versions"][0]["links"]["release"],
            "sha256": dortania_builds_data["OpenCorePkg"]["versions"][0]["hashes"]["release"]["sha256"]
        })

        return latest_products
    
    def move_bootloader_kexts_to_product_directory(self, product_name, working_dir):
        temp_product_dir = os.path.join(working_dir, "extracted")
        if not os.path.isdir(temp_product_dir):
            raise FileNotFoundError("Extracted files for {} are missing: {}".format(product_name, temp_product_dir))

        product_dir = os.path.join(working_dir, "ready")
        backup_dir = os.path.join(working_dir, "previous")
        asset_dir = os.path.join(self.ock_files_dir, product_name)
        try:
            self.utils.create_folder(product_dir)
            if "OpenCore" not in product_name:
                kext_paths = self.utils.find_matching_paths(temp_product_dir, extension_filter=".kext", type_filter="dir")
                for kext_path, _ in kext_paths:
                    if "research" in kext_path.lower() or "debug" in kext_path.lower() or "Contents" in kext_path or not self.kext.process_kext(temp_product_dir, kext_path):
                        continue

                    source_kext_path = os.path.join(temp_product_dir, kext_path)
                    destination_kext_path = os.path.join(product_dir, os.path.basename(kext_path))
                    os.rename(source_kext_path, destination_kext_path)
                if not os.listdir(product_dir):
                    raise ValueError("No usable kext bundles found for {}.".format(product_name))
            else:
                source_bootloader_path = os.path.join(temp_product_dir, "X64", "EFI")
                source_config_path = os.path.join(temp_product_dir, "Docs", "Sample.plist")
                if not os.path.isdir(source_bootloader_path) or not os.path.isfile(source_config_path):
                    raise ValueError("Missing EFI or Docs/Sample.plist for {}.".format(product_name))
                destination_efi_path = os.path.join(product_dir, "EFI")
                os.rename(source_bootloader_path, destination_efi_path)
                os.replace(source_config_path, os.path.join(destination_efi_path, "OC", "config.plist"))

                ocbinarydata_dir = os.path.join(working_dir, "OcBinaryData", "OcBinaryData-master")
                if os.path.exists(ocbinarydata_dir):
                    background_picker_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "datasets", "background_picker.icns")
                    for dir_name in os.listdir(ocbinarydata_dir):
                        source_dir = os.path.join(ocbinarydata_dir, dir_name)
                        destination_dir = os.path.join(destination_efi_path, "OC", dir_name)
                        if os.path.isdir(destination_dir):
                            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

                    resources_image_dir = os.path.join(destination_efi_path, "OC", "Resources", "Image")
                    picker_variants = self.utils.find_matching_paths(resources_image_dir, type_filter="dir")
                    for picker_variant, _ in picker_variants:
                        if ".icns" in ", ".join(os.listdir(os.path.join(resources_image_dir, picker_variant))):
                            shutil.copy(background_picker_path, os.path.join(resources_image_dir, picker_variant, "Background.icns"))

                macserial_paths = self.utils.find_matching_paths(temp_product_dir, name_filter="macserial", type_filter="file")
                for macserial_path, _ in macserial_paths:
                    source_macserial_path = os.path.join(temp_product_dir, macserial_path)
                    destination_macserial_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(macserial_path))
                    shutil.move(source_macserial_path, destination_macserial_path)
                    if os.name != "nt":
                        subprocess.run(["chmod", "+x", destination_macserial_path], check=True)

            self.integrity_checker.generate_folder_manifest(product_dir)
            if os.path.exists(asset_dir):
                os.replace(asset_dir, backup_dir)
            try:
                os.replace(product_dir, asset_dir)
            except OSError:
                if os.path.exists(backup_dir):
                    os.replace(backup_dir, asset_dir)
                raise
        except (OSError, shutil.Error) as error:
            raise OSError("Could not save {} to {} (staging: {}): {}".format(product_name, asset_dir, working_dir, error)) from error

        return True
    
    def gather_bootloader_kexts(self, kexts, macos_version):
        self.utils.head("Gathering Files")
        print("")
        print("Please wait for download OpenCorePkg, kexts and macserial...")
        local_download_history = self._load_download_history()

        latest_products = self.fetch_latest_products_info(kexts)
        
        self.utils.create_folder(self.ock_files_dir)

        seen_products = set()

        for product in kexts + [{"Name": "OpenCorePkg"}]:
            if not isinstance(product, dict) and not product.checked:
                continue

            product_name = product.name if not isinstance(product, dict) else product.get("Name")
            
            if product_name == "AirportItlwm":
                version = macos_version[:2]
                if all((self.utils.parse_darwin_version("24.0.0") <= self.utils.parse_darwin_version(macos_version), kexts[kext_maestro.kext_data.kext_index_by_name.get("IOSkywalkFamily")].checked, kexts[kext_maestro.kext_data.kext_index_by_name.get("IO80211FamilyLegacy")].checked)):
                    version = "22"
                elif self.utils.parse_darwin_version("23.4.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "23.4"
                elif self.utils.parse_darwin_version("23.0.0") <= self.utils.parse_darwin_version(macos_version):
                    version = "23.0"
                product_name += version
            elif product_name == "AirportItlwm-laobamac":
                product_name += macos_version[:2]
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

            product_info = latest_products.get(product_name)
            if product_info is None:
                if hasattr(product, 'github_repo') and product.github_repo and product.name not in ("AirportItlwm", "AirportItlwm-laobamac"):
                    product_info = latest_products.get(product.github_repo.get("repo"))
            
            if product_info is None:
                raise ValueError("Could not find download information for {}.".format(product_name))

            product_id = product_info.get("id")
            product_download_url = product_info.get("url")
            sha256_hash = product_info.get("sha256")

            if not product_download_url:
                raise ValueError("Could not find download URL for {}.".format(product_name))

            if product_name in seen_products:
                continue
            seen_products.add(product_name)

            history_item = local_download_history.get(product_name)
            asset_dir = os.path.join(self.ock_files_dir, product_name)
            manifest_path = os.path.join(asset_dir, "manifest.json")

            if history_item is not None and all(product_info.get(key) == history_item.get(key) for key in ("id", "url", "sha256")):
                folder_is_valid, _ = self.integrity_checker.verify_folder_integrity(asset_dir, manifest_path)
                
                if folder_is_valid and self.utils.read_file(manifest_path):
                    print(f"\nLatest version of {product_name} already downloaded.")
                    continue

            print("")
            print("Updating" if history_item is not None else "Please wait for download", end=" ")
            print("{}...".format(product_name))
            print("from {}".format(product_download_url))
            print("")

            working_dir = tempfile.mkdtemp(prefix=".ocs-", dir=self.ock_files_dir)
            saved = False
            try:
                zip_path = os.path.join(working_dir, "download.zip")
                if not self.fetcher.download_and_save_file(product_download_url, zip_path, sha256_hash):
                    raise RuntimeError("Could not download {} from {}. The existing cache was kept.".format(product_name, product_download_url))

                extracted_dir = os.path.join(working_dir, "extracted")
                self.utils.extract_zip_file(zip_path, extracted_dir)

                dirs_to_scan = [extracted_dir]
                while dirs_to_scan:
                    current_dir = dirs_to_scan.pop()
                    if not os.path.isdir(current_dir):
                        continue

                    for item in os.listdir(current_dir):
                        item_path = os.path.join(current_dir, item)
                        if os.path.isdir(item_path):
                            dirs_to_scan.append(item_path)
                        elif item.lower().endswith(".zip"):
                            self.utils.extract_zip_file(item_path)
                            os.remove(item_path)
                            dirs_to_scan.append(os.path.splitext(item_path)[0])

                if "OpenCore" in product_name:
                    oc_binary_data_zip_path = os.path.join(working_dir, "OcBinaryData.zip")
                    print("")
                    print("Please wait for download OcBinaryData...")
                    print("from {}".format(self.ocbinarydata_url))
                    print("")
                    if not self.fetcher.download_and_save_file(self.ocbinarydata_url, oc_binary_data_zip_path):
                        raise RuntimeError("Could not download OcBinaryData for {} from {}.".format(product_name, self.ocbinarydata_url))

                    self.utils.extract_zip_file(oc_binary_data_zip_path)

                saved = self.move_bootloader_kexts_to_product_directory(product_name, working_dir)
                self._save_download_history(local_download_history, product_name, product_id, product_download_url, sha256_hash)
            finally:
                if saved or not os.path.exists(os.path.join(working_dir, "previous")):
                    shutil.rmtree(working_dir, ignore_errors=True)

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
            print("Could not find release information for {}.".format(PRODUCT_NAME))
            print("Please try again later.")
            print("")
            self.utils.request_input()
            raise Exception("Could not find release information for {}.".format(PRODUCT_NAME))
        local_download_history = self._load_download_history()

        history_item = local_download_history.get(PRODUCT_NAME)
        
        if history_item is not None:
            is_latest_id = (product_id == history_item.get("id"))
            
            file_is_valid = False
            if os.path.exists(destination_path):
                local_hash = self.integrity_checker.get_sha256(destination_path)
                file_is_valid = (sha256_hash == local_hash)

            if is_latest_id and file_is_valid:
                print("")
                print("Latest version of {} already downloaded.".format(PRODUCT_NAME))
                return destination_path

        print("")
        print("Updating" if history_item is not None else "Please wait for download", end=" ")
        print("{}...".format(PRODUCT_NAME))
        print("")
        print("from {}".format(product_download_url))
        print("")
        
        if not self.fetcher.download_and_save_file(product_download_url, destination_path, sha256_hash):
            manual_download_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest"
            print("Go to {} to download {} manually.".format(manual_download_url, PRODUCT_NAME))
            print("")
            self.utils.request_input()
            raise Exception("Failed to download {}.".format(PRODUCT_NAME))

        self._save_download_history(local_download_history, PRODUCT_NAME, product_id, product_download_url, sha256_hash)
        
        return destination_path
