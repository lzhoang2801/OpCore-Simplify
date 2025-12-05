from Scripts.datasets.mac_model_data import mac_devices
from Scripts.datasets import kext_data
from Scripts.datasets import os_data
from Scripts import gathering_files
from Scripts import run
from Scripts import utils
from Scripts import settings as settings_module
import os
import uuid
import random
import platform
import json

os_name = platform.system()

class SMBIOS:
    def __init__(self):
        self.g = gathering_files.gatheringFiles()
        self.run = run.Run().run
        self.utils = utils.Utils()
        self.settings = settings_module.Settings()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.preserved_smbios_file = os.path.join(os.path.dirname(self.script_dir), "preserved_smbios.json")

    def check_macserial(self, retry_count=0):
        max_retries = 3

        if os_name == "Windows":
            macserial_binary = ["macserial.exe"]
        elif os_name == "Linux":
            macserial_binary = ["macserial.linux", "macserial"]
        elif os_name == "Darwin":
            macserial_binary = ["macserial"]
        else:
            raise Exception("Unknown OS for macserial")

        for binary in macserial_binary:
            macserial_path = os.path.join(self.script_dir, binary)
            if os.path.exists(macserial_path):
                return macserial_path

        if retry_count >= max_retries:
            raise Exception("Failed to find macserial after {} attempts".format(max_retries))
        
        download_history = self.utils.read_file(self.g.download_history_file)

        if download_history:
            product_index = self.g.get_product_index(download_history, "OpenCorePkg")
            
            if product_index is not None:
                download_history.pop(product_index)
                self.utils.write_file(self.g.download_history_file, download_history)

        self.g.gather_bootloader_kexts([], "")
        return self.check_macserial(retry_count + 1)
        
    def generate_random_mac(self):
        random_mac = ''.join([format(random.randint(0, 255), '02X') for _ in range(6)])
        return random_mac
    
    def load_preserved_smbios(self):
        """Load preserved SMBIOS values from file"""
        if os.path.exists(self.preserved_smbios_file):
            try:
                with open(self.preserved_smbios_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def save_preserved_smbios(self, smbios_data):
        """Save SMBIOS values to file for preservation"""
        try:
            with open(self.preserved_smbios_file, 'w') as f:
                json.dump(smbios_data, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save preserved SMBIOS: {e}")

    def generate_smbios(self, smbios_model):
        self.utils.debug_log(f"Generating SMBIOS for model: {smbios_model}")
        
        # Check if we should use preserved SMBIOS
        if self.settings.get_preserve_smbios():
            preserved = self.load_preserved_smbios()
            if preserved and preserved.get("SystemProductName") == smbios_model:
                print("Using preserved SMBIOS values")
                self.utils.debug_log(f"Loaded preserved SMBIOS for {smbios_model}")
                return preserved
        
        # Check if custom SMBIOS values are provided
        if not self.settings.get_random_smbios():
            custom_serial = self.settings.get_custom_serial_number()
            custom_mlb = self.settings.get_custom_mlb()
            custom_rom = self.settings.get_custom_rom()
            
            # If all custom values are provided, use them
            if custom_serial and custom_mlb and custom_rom:
                smbios_data = {
                    "MLB": custom_mlb,
                    "ROM": custom_rom,
                    "SystemProductName": smbios_model,
                    "SystemSerialNumber": custom_serial,
                    "SystemUUID": str(uuid.uuid4()).upper(),
                }
                print("Using custom SMBIOS values")
                self.utils.debug_log(f"Using custom SMBIOS: Serial={custom_serial[:4]}..., MLB={custom_mlb[:4]}...")
                if self.settings.get_preserve_smbios():
                    self.save_preserved_smbios(smbios_data)
                return smbios_data
        
        # Generate random SMBIOS (default behavior)
        self.utils.debug_log("Generating random SMBIOS")
        macserial = self.check_macserial()

        random_mac_address = self.generate_random_mac()

        output = self.run({
            "args":[macserial, "-g", "--model", smbios_model]
        })
        
        if not output or output[-1] != 0 or not output[0] or " | " not in output[0]:
            serial = []
        else:
            serial = output[0].splitlines()[0].split(" | ")

        smbios_data = {
            "MLB": "A" + "0"*15 + "Z" if not serial else serial[-1],
            "ROM": random_mac_address,
            "SystemProductName": smbios_model,
            "SystemSerialNumber": "A" + "0"*10 + "9" if not serial else serial[0],
            "SystemUUID": str(uuid.uuid4()).upper(),
        }
        
        # Save for preservation if enabled
        if self.settings.get_preserve_smbios():
            self.save_preserved_smbios(smbios_data)
        
        return smbios_data
    
    def smbios_specific_options(self, hardware_report, smbios_model, macos_version, acpi_patches, kext_maestro):
        for patch in acpi_patches:
            if patch.name == "MCHC":
                patch.checked = "Intel" in hardware_report.get("CPU").get("Manufacturer") and not "MacPro" in smbios_model

        selected_kexts = []

        if "MacPro7,1" in smbios_model:
            selected_kexts.append("RestrictEvents")

        if smbios_model in (device.name for device in mac_devices[31:34] + mac_devices[48:50] + mac_devices[51:61]):
            selected_kexts.append("NoTouchID")

        for name in selected_kexts:
            kext_maestro.check_kext(kext_data.kext_index_by_name.get(name), macos_version, "Beta" in os_data.get_macos_name_by_darwin(macos_version))
    
    def select_smbios_model(self, hardware_report, macos_version):
        platform = "NUC" if "NUC" in hardware_report.get("Motherboard").get("Name") else hardware_report.get("Motherboard").get("Platform")
        codename = hardware_report.get("CPU").get("Codename")

        smbios_model = "MacBookPro16,2" if "Laptop" in platform else "iMacPro1,1" if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("25.0.0") else "MacPro7,1"

        if codename in ("Lynnfield", "Clarkdale") and "Xeon" not in hardware_report.get("CPU").get("Processor Name") and self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("19.0.0"):
            smbios_model = "iMac11,1" if codename == "Lynnfield" else "iMac11,2"
        elif codename in ("Beckton", "Westmere-EX", "Gulftown", "Westmere-EP", "Clarkdale", "Lynnfield", "Jasper Forest", "Gainestown", "Bloomfield"):
            smbios_model = "MacPro5,1" if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("19.0.0") else "MacPro6,1"
        elif ("Sandy Bridge" in codename or "Ivy Bridge" in codename) and self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("22.0.0"):
            smbios_model = "MacPro6,1"

        if platform != "Laptop" and list(hardware_report.get("GPU").items())[-1][-1].get("Device Type") != "Integrated GPU":
            return smbios_model
        
        if codename in ("Arrandale", "Clarksfield"):
            smbios_model = "MacBookPro6,1"
        elif "Sandy Bridge" in codename:
            if "Desktop" in platform:
                smbios_model = "iMac12,2"
            elif "NUC" in platform:
                smbios_model = "Macmini5,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "Macmini5,3"
            elif "Laptop" in platform:
                smbios_model = "MacBookPro8,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "MacBookPro8,2"
        elif "Ivy Bridge" in codename:
            if "Desktop" in platform:
                smbios_model = "iMac13,1" if "Integrated GPU" in list(hardware_report.get("GPU").items())[0][-1].get("Device Type") else "iMac13,2"
            elif "NUC" in platform:
                smbios_model = "Macmini6,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "Macmini6,2"
            elif "Laptop" in platform:
                smbios_model = "MacBookPro10,2" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "MacBookPro10,1"
        elif "Haswell" in codename:
            if "Desktop" in platform:
                smbios_model = "iMac14,4" if "Integrated GPU" in list(hardware_report.get("GPU").items())[0][-1].get("Device Type") else "iMac15,1"
            elif "NUC" in platform:
                smbios_model = "Macmini7,1"
            elif "Laptop" in platform:
                smbios_model = "MacBookPro11,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "MacBookPro11,5"
        elif "Broadwell" in codename:
            if "Desktop" in platform:
                smbios_model = "iMac16,2" if "Integrated GPU" in list(hardware_report.get("GPU").items())[0][-1].get("Device Type") else "iMac17,1"
            elif "NUC" in platform:
                smbios_model = "iMac16,1"
            elif "Laptop" in platform:
                smbios_model = "MacBookPro12,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "MacBookPro11,5"
        elif "Skylake" in codename:
            smbios_model = "iMac17,1"
            if "Laptop" in platform:
                smbios_model = "MacBookPro13,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "MacBookPro13,3"
        elif "Amber Lake" in codename or "Kaby Lake" in codename:
            smbios_model = "iMac18,1" if "Integrated GPU" in list(hardware_report.get("GPU").items())[0][-1].get("Device Type") else "iMac18,3"
            if "Laptop" in platform:
                smbios_model = "MacBookPro14,1" if int(hardware_report.get("CPU").get("Core Count")) < 4 else "MacBookPro14,3"
        elif "Cannon Lake" in codename or "Whiskey Lake" in codename or "Coffee Lake" in codename or "Comet Lake" in codename:
            smbios_model = "Macmini8,1"
            if "Desktop" in platform:
                smbios_model = "iMac18,3" if self.utils.parse_darwin_version(macos_version) < self.utils.parse_darwin_version("18.0.0") else "iMac19,1"
                if "Comet Lake" in codename:
                    smbios_model = "iMac20,1" if int(hardware_report.get("CPU").get("Core Count")) < 10 else "iMac20,2"
            elif "Laptop" in platform:
                if "-8" in hardware_report.get("CPU").get("Processor Name"):
                    smbios_model = "MacBookPro15,2" if int(hardware_report.get("CPU").get("Core Count")) < 6 else "MacBookPro15,3"
                else:
                    smbios_model = "MacBookPro16,3" if int(hardware_report.get("CPU").get("Core Count")) < 6 else "MacBookPro16,1"
        elif "Ice Lake" in codename:
            smbios_model = "MacBookAir9,1"

        return smbios_model
    
    def customize_smbios_model(self, hardware_report, selected_smbios_model, macos_version):
        current_category = None
        default_smbios_model = self.select_smbios_model(hardware_report, macos_version)
        show_all_models = False
        is_laptop = "Laptop" == hardware_report.get("Motherboard").get("Platform")

        while True:
            incompatible_models_by_index = []
            contents = []
            contents.append("")
            if show_all_models:
                contents.append("List of available SMBIOS:")
            else:
                contents.append("List of compatible SMBIOS:")
            for index, device in enumerate(mac_devices, start=1):
                isSupported = self.utils.parse_darwin_version(device.initial_support) <= self.utils.parse_darwin_version(macos_version) <= self.utils.parse_darwin_version(device.last_supported_version)
                if device.name not in (default_smbios_model, selected_smbios_model) and not show_all_models and (not isSupported or (is_laptop and not device.name.startswith("MacBook")) or (not is_laptop and device.name.startswith("MacBook"))):
                    incompatible_models_by_index.append(index - 1)
                    continue

                category = ""
                for char in device.name:
                    if char.isdigit():
                        break
                    category += char
                if category != current_category:
                    current_category = category
                    category_header = "Category: {}".format(current_category if current_category else "Uncategorized")
                    contents.append(f"\n{category_header}\n" + "=" * len(category_header))
                checkbox = "[*]" if device.name == selected_smbios_model else "[ ]"
                
                line = "{} {:2}. {:15} - {:10} {:20}{}".format(checkbox, index, device.name, device.cpu, "({})".format(device.cpu_generation), "" if not device.discrete_gpu else " - {}".format(device.discrete_gpu))
                if device.name == selected_smbios_model:
                    line = "\033[1;32m{}\033[0m".format(line)
                elif not isSupported:
                    line = "\033[90m{}\033[0m".format(line)
                contents.append(line)
            contents.append("")
            contents.append("\033[1;93mNote:\033[0m")
            contents.append("- Lines in gray indicate mac models that are not officially supported by {}.".format(os_data.get_macos_name_by_darwin(macos_version)))
            contents.append("")
            if not show_all_models:
                contents.append("A. Show all models")
            else:
                contents.append("C. Show compatible models only")
            if selected_smbios_model != default_smbios_model:
                contents.append("R. Restore default SMBIOS model ({})".format(default_smbios_model))
            contents.append("")
            contents.append("B. Back")
            contents.append("Q. Quit")
            contents.append("")
            content = "\n".join(contents)

            self.utils.adjust_window_size(content)
            self.utils.head("Customize SMBIOS Model", resize=False)
            print(content)
            option = self.utils.request_input("Select your option: ")
            if option.lower() == "q":
                self.utils.exit_program()
            if option.lower() == "b":
                return selected_smbios_model
            if option.lower() == "r" and selected_smbios_model != default_smbios_model:
                return default_smbios_model
            if option.lower() in ("a", "c"):
                show_all_models = not show_all_models
                continue

            if option.strip().isdigit():
                index = int(option) - 1
                if index >= 0 and index < len(mac_devices):
                    if not show_all_models and index in incompatible_models_by_index:
                        continue

                    selected_smbios_model = mac_devices[index].name