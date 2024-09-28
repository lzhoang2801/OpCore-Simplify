from Scripts.datasets.kext_data import kexts
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
        self.fetcher = resource_fetcher.ResourceFetcher()
        self.dortania_builds_url = "https://raw.githubusercontent.com/dortania/build-repo/builds/latest.json"
        self.amd_vanilla_patches_url = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/beta/patches.plist"
        self.temporary_dir = tempfile.mkdtemp()
        self.ock_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "OCK_Files")
        self.bootloader_kexts_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "bootloader_kexts_data.json")
        self.download_history_file = os.path.join(self.ock_files_dir, "history.json")
        
    def get_bootloader_kexts_data(self):
        last_updated_str = (self.utils.read_file(self.bootloader_kexts_data_path) or {}).get("last_updated", "2024-07-25T12:00:00")
        last_updated = datetime.fromisoformat(last_updated_str)

        current_time = datetime.now()
        if current_time - last_updated < timedelta(minutes=15):
            return
        download_urls = []

        dortania_builds_data = self.fetcher.fetch_and_parse_content(self.dortania_builds_url, "json")
        seen_repos = set()

        for kext in kexts:
            if kext.download_info:
                download_urls.append({"product_name": kext.name, **kext.download_info})
            elif kext.github_repo and kext.github_repo.get("repo") not in seen_repos:
                name = kext.github_repo.get("repo")
                seen_repos.add(name)
                if name in dortania_builds_data:
                    download_urls.append({
                        "product_name": name,
                        "id": dortania_builds_data[name]["versions"][0]["release"]["id"], 
                        "url": dortania_builds_data[name]["versions"][0]["links"]["release"]
                    })
                else:
                    if self.github.check_ratelimit():
                        download_urls.extend(self.github.get_latest_release(kext.github_repo.get("owner"), kext.github_repo.get("repo")))

        if self.github.check_ratelimit():
            download_urls.extend(self.github.get_latest_release("wjz304", "OpenCore_Patch_Build"))

        sorted_data = sorted(download_urls, key=lambda x:x["product_name"])

        self.utils.create_folder(self.ock_files_dir)
        self.utils.write_file(self.bootloader_kexts_data_path, {
            "download_urls": sorted_data,
            "last_updated": current_time.isoformat()
        })
    
        return sorted_data
    
    def product_index_in_history(self, product_name, download_history):
        for index, item in enumerate(download_history):
            if product_name in item["product_name"]:
                return index
        return None
    
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

    def gathering_bootloader_kexts(self):
        download_history = self.utils.read_file(self.download_history_file) or []
        
        self.utils.create_folder(self.temporary_dir)

        for product_data in (self.utils.read_file(self.bootloader_kexts_data_path) or {}).get("download_urls", []):
            product_index = self.product_index_in_history(product_data.get("product_name"), download_history)
            if not product_index is None and product_data.get("id") == download_history[product_index].get("id"):
                continue

            asset_dir = os.path.join(self.ock_files_dir, product_data.get("product_name"))
            self.utils.create_folder(asset_dir, remove_content=True)

            zip_path = os.path.join(self.temporary_dir, product_data.get("product_name")) + ".zip"
            self.fetcher.download_and_save_file(product_data.get("url"), zip_path)
            self.utils.extract_zip_file(zip_path)

            if self.move_bootloader_kexts_to_product_directory(product_data.get("product_name")):
                if product_index is None:
                    download_history.append({
                        "product_name": product_data.get("product_name"),
                        "id": product_data.get("id")
                    })
                else:
                    download_history[product_index]["id"] = product_data.get("id")
                
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