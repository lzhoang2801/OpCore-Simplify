from Scripts.datasets.mac_model_data import mac_devices
from Scripts.datasets import kext_data
from Scripts.datasets import os_data
from Scripts.custom_dialogs import show_smbios_selection_dialog
from Scripts import gathering_files
from Scripts import run
from Scripts import utils
from Scripts import settings
import os
import uuid
import random
import platform

os_name = platform.system()

class SMBIOS:
    def __init__(self, gathering_files_instance=None, run_instance=None, utils_instance=None, settings_instance=None):
        self.g = gathering_files_instance if gathering_files_instance else gathering_files.gatheringFiles()
        self.run = run_instance.run if run_instance else run.Run().run
        self.utils = utils_instance if utils_instance else utils.Utils()
        self.settings = settings_instance if settings_instance else settings.Settings()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

    def check_macserial(self, retry_count=0):
        max_retries = 3

        if os_name == "Windows":
            macserial_binary = ["macserial.exe"]
        elif os_name == "Linux":
            macserial_binary = ["macserial.linux", "macserial"]
        elif os_name == "Darwin":
            macserial_binary = ["macserial"]
        else:
            self.utils.log_message("[SMBIOS] Unknown OS for macserial", level="ERROR")
            raise Exception("Unknown OS for macserial")

        for binary in macserial_binary:
            macserial_path = os.path.join(self.script_dir, binary)
            if os.path.exists(macserial_path):
                return macserial_path

        if retry_count >= max_retries:
            self.utils.log_message("[SMBIOS] Failed to find macserial after {} attempts".format(max_retries), level="ERROR")
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

    def generate_smbios(self, smbios_model):
        macserial = self.check_macserial()

        random_mac_address = self.generate_random_mac()

        output = self.run({
            "args":[macserial, "-g", "--model", smbios_model]
        })
        
        if not output or output[-1] != 0 or not output[0] or " | " not in output[0]:
            serial = []
        else:
            serial = output[0].splitlines()[0].split(" | ")

        smbios_info = {
            "MLB": "A" + "0"*15 + "Z" if not serial else serial[-1],
            "ROM": random_mac_address,
            "SystemProductName": smbios_model,
            "SystemSerialNumber": "A" + "0"*10 + "9" if not serial else serial[0],
            "SystemUUID": str(uuid.uuid4()).upper(),
        }

        self.utils.log_message("[SMBIOS] Generated SMBIOS info: MLB: {}..., ROM: {}..., SystemProductName: {}, SystemSerialNumber: {}..., SystemUUID: {}...".format(
            smbios_info["MLB"][:5],
            smbios_info["ROM"][:5],
            smbios_info["SystemProductName"],
            smbios_info["SystemSerialNumber"][:5],
            smbios_info["SystemUUID"].split("-")[0]), level="INFO")
        return smbios_info
    
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

        self.utils.log_message("[SMBIOS] Suggested SMBIOS model: {}".format(smbios_model), level="INFO")
        return smbios_model

    def customize_smbios_model(self, hardware_report, selected_smbios_model, macos_version, parent=None):
        default_smbios_model = self.select_smbios_model(hardware_report, macos_version)
        is_laptop = "Laptop" == hardware_report.get("Motherboard").get("Platform")
        macos_name = os_data.get_macos_name_by_darwin(macos_version)
        
        items = []
        for index, device in enumerate(mac_devices):
            is_supported = self.utils.parse_darwin_version(device.initial_support) <= self.utils.parse_darwin_version(macos_version) <= self.utils.parse_darwin_version(device.last_supported_version)
            
            platform_match = True
            if is_laptop and not device.name.startswith("MacBook"):
                platform_match = False
            elif not is_laptop and device.name.startswith("MacBook"):
                platform_match = False
                
            is_compatible = is_supported and platform_match
            
            category = ""
            for char in device.name:
                if char.isdigit():
                    break
                category += char
            
            gpu_str = "" if not device.discrete_gpu else " - {}".format(device.discrete_gpu)
            label = "{} - {} ({}){}".format(device.name, device.cpu, device.cpu_generation, gpu_str)

            items.append({
                'name': device.name,
                'label': label,
                'category': category,
                'is_supported': is_supported,
                'is_compatible': is_compatible
            })
            
        content = "Lines in gray indicate mac models that are not officially supported by {}.".format(macos_name)
        
        result = show_smbios_selection_dialog("Customize SMBIOS Model", content, items, selected_smbios_model, default_smbios_model)
        
        return result if result else selected_smbios_model