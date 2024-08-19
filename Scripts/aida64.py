from Scripts.datasets import pci_data
from Scripts import gpu_identifier
from Scripts import utils

class AIDA64:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        self.encodings = ["utf-8", "latin-1", "ISO-8859-1"]
        self.gpu_identifier = gpu_identifier.GPUIdentifier()
        self.utils = utils.Utils()
    
    def try_open(self, file_path):
        for encoding in self.encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("Unable to decode file {} with given encodings".format(file_path))

    def get_unique_key(self, base_key, dictionary):
        if base_key not in dictionary:
            return base_key
        
        counter = 1
        unique_key = f"{base_key}_#{counter}"
        
        while unique_key in dictionary:
            counter += 1
            unique_key = f"{base_key}_#{counter}"
        
        return unique_key
    
    def parse_hardware_id(self, hardware_id):
        if "VEN" in hardware_id:
            return {
                "Bus Type": hardware_id.split("\\")[0],
                "Device ID": "{}-{}".format(hardware_id.split("VEN_")[-1].split("&")[0], hardware_id.split("DEV_")[-1].split("&")[0]),
                "Subsystem ID": hardware_id.split("SUBSYS_")[-1].split("&")[0],
                "Revision": hardware_id.split("REV_")[-1].split("\\")[0]
            }
        
        if "VID" in hardware_id:
            return {
                "Bus Type": hardware_id.split("\\")[0],
                "Device ID": "{}-{}".format(hardware_id.split("VID_")[-1].split("&")[0], hardware_id.split("PID_")[-1].split("&")[0]),
                "Revision": hardware_id.split("REV_")[-1].split("&")[0].split("\\")[0]
            }
        
        return {
            "Bus Type": hardware_id.split("\\")[0],
            "Device": hardware_id.split("\\")[-1]
        }
 
    def motherboard(self, motherboard_props, dmi):
        motherboard_info = {}

        # Extract motherboard name and chipset from provided properties
        motherboard_info["Motherboard Name"] = motherboard_props.get("Motherboard Name", "Unknown").split("(")[0].strip()
        motherboard_info["Motherboard Chipset"] = motherboard_props.get("Motherboard Chipset", "Unknown").split(", ")[0]

        # If motherboard name is still unknown, attempt to derive it from DMI information
        if "Unknown" in motherboard_info.get("Motherboard Name"):
            motherboard_info["Motherboard Name"] = "Unknown"
            merged_report = dmi.get("System", {}).copy()
            merged_report.update(dmi.get("Motherboard", {}))
            for device_key, device_value in merged_report.items():
                motherboard_name = "{} {}".format(device_value.get("Manufacturer", "O.E.M."), device_value.get("Product", "O.E.M."))
                if "O.E.M." not in motherboard_name and "System Product Name" not in motherboard_name and len(motherboard_name) > len(motherboard_info.get("Motherboard Name")):
                    motherboard_info["Motherboard Name"] = motherboard_name

        # Extract platform type from chassis information
        motherboard_info["Platform"] = dmi.get("Chassis", {}).get("Chassis Properties", {}).get("Chassis Type", "Unknown")
        if any(word in motherboard_info["Platform"].lower() for word in ["convertible", "notebook", "laptop", "docking station"]):
            motherboard_info["Platform"] = "Laptop"
        elif any(word in motherboard_info["Platform"].lower() for word in ["desktop", "mini pc"]):
            motherboard_info["Platform"] = "Desktop"
        elif "NUC" in motherboard_info["Motherboard Name"]:
            motherboard_info["Platform"] = "NUC"

        return motherboard_info
    
    def cpu(self, cpu_table):
        cpu_info = {}

        cpu_info["CPU Manufacturer"] = cpu_table.get("CPU Manufacturer", {}).get("Company Name", "Unknown")

        cpu_props = cpu_table.get("CPU Properties", {})
        cpu_info["Processor Name"] = cpu_props.get("CPU Type", "Unknown").split(",")[0]

        # Determine CPU Manufacturer if still unknown
        if "Intel" in cpu_info["CPU Manufacturer"]:
            cpu_info["CPU Manufacturer"] = "Intel"
        elif "Advanced Micro Devices" in cpu_info["CPU Manufacturer"]:
            cpu_info["CPU Manufacturer"] = "AMD"
        elif cpu_info["CPU Manufacturer"] == "Unknown":
            processor_name = cpu_table.get("Multi CPU", {}).get("CPU #1", "Unknown").split("with")[0].split(",")[0]
            if "Intel" in processor_name:
                cpu_info["CPU Manufacturer"] = "Intel"
            elif "AMD" in processor_name:
                cpu_info["CPU Manufacturer"] = "AMD"
            cpu_info["Processor Name"] += cpu_info["CPU Manufacturer"] + processor_name.split(cpu_info["CPU Manufacturer"])[-1]

        cpu_info["CPU Codename"] = cpu_props.get("CPU Alias", "Unknown")

        cpu_info["CPU Cores"] = str(sum(1 for key in list(cpu_table.get("CPU Utilization", {}).keys()) if not "SMT Unit" in key or "SMT Unit #1" in key)).zfill(2)

        cpu_info["CPU Configuration"] = list(cpu_table.get("CPU Utilization", {}).keys())[-1].split(" / ")[0].split("#")[-1].zfill(2)

        cpu_info["Instruction Set"] = cpu_props.get("Instruction Set", "Unknown")

        return cpu_info

    def storage_controllers(self, ata_controllers, storage_controllers):
        storage_controllers_info = {}

        storage_controllers.update(ata_controllers)
        for controller_name, controller_props in storage_controllers.items():
            bus_type = controller_props.get("Bus Type", "Unknown")
            if "PCI" in bus_type or "VID" in bus_type:
                pci_device = controller_props.get("PCI Device")
                if " SD " in pci_device or "MMC" in pci_device:
                    continue

                storage_controllers_info[self.get_unique_key(controller_props.get("PCI Device", controller_name), storage_controllers_info)] = {
                    "Bus Type": controller_props.get("Bus Type", "Unknown"),
                    "Device ID": controller_props.get("Device ID", "Unknown")
                }

        return storage_controllers_info

    def audio(self, windows_devices):
        audio_devices_info = {}
        audio_device_ids = []

        for device_name, device_props in windows_devices.get("Audio inputs and outputs", {}).items():
            driver_description = device_props.get("Driver Description", "Unknown")

            if " (" not in driver_description:
                continue

            audio_endpoint = driver_description.split(" (")[0]
            audio_controller_name = driver_description.split(" (")[-1].strip(" )").split("- ")[-1]

            audio_controller_props = self.utils.search_dict_iter(windows_devices, audio_controller_name)
            bus_type = audio_controller_props.get("Bus Type", "")
            
            if audio_controller_name not in audio_devices_info and (bus_type.endswith("AUDIO") or bus_type.endswith("USB") or bus_type.endswith("ACP")):
                audio_devices_info[audio_controller_name] = {
                    "Bus Type": bus_type,
                    "{} ID".format("USB" if bus_type.endswith("USB") else "Codec"): audio_controller_props.get("Device ID", "Unknown"),
                    "Audio Endpoints": [audio_endpoint]
                }
                audio_device_ids.append(audio_controller_props.get("Device ID", "Unknown"))
            elif audio_controller_name in audio_devices_info:
                audio_devices_info[audio_controller_name]["Audio Endpoints"].append(audio_endpoint)

        detected_audio_devices = self.utils.search_dict_iter(windows_devices, "AUDIO", equal=False)
        windows_audio_devices = self.utils.search_dict_iter(windows_devices, detected_audio_devices)
        
        for device_name, device_props in windows_audio_devices.items():
            bus_type = device_props.get("Bus Type", "")
            if bus_type.endswith("AUDIO") or bus_type.endswith("USB"):
                if device_props.get("Device ID", "Unknown") not in audio_device_ids:
                    audio_devices_info[self.get_unique_key(device_name, audio_devices_info)] = {
                        "Bus Type": bus_type,
                        "{} ID".format("USB" if bus_type.endswith("USB") else "Codec"): device_props.get("Device ID", "Unknown")
                    }

        return audio_devices_info

    def gpu(self, pci_devices, windows_devices):
        gpu_info = {}

        display_adapters = windows_devices.get("Display adapters", windows_devices.get("Display adaptors", {}))
        gpu_by_class = None
        if not display_adapters:
            gpu_by_class = self.utils.search_dict_iter(pci_devices, "VGA Display Controller", equal=False)
            if gpu_by_class:
                gpu_in_windows_devices = self.utils.search_dict_iter(windows_devices, gpu_by_class.get("Device ID"))
                display_adapters = self.utils.search_dict_iter(windows_devices, gpu_in_windows_devices)

        for adapter_name, adapter_props in display_adapters.items():
            device_id = adapter_props.get("Device ID")
            if not device_id:
                continue
            if gpu_by_class and self.utils.contains_any(["Video Controller", "Video Adapter", "Graphics Controller"], adapter_name + adapter_props.get("PCI Device", "")) is None:
                continue
            gpu_info[adapter_name] = self.gpu_identifier.classify_gpu(device_id)

        return self.utils.sort_dict_by_key(gpu_info, "Device Type")

    def input(self, human_interface_devices, keyboards, pointing_devices, usb_devices):
        input_devices_info = {}

        combined_devices = human_interface_devices.copy()
        combined_devices.update(keyboards)
        combined_devices.update(pointing_devices)
        
        for device_name, device_props in combined_devices.items():
            bus_type = device_props.get("Bus Type", "Unknown")
            device_id = device_props.get("Device ID", "Unknown")
            
            if "ACPI" in bus_type or "ROOT" in bus_type or "USB" in bus_type:
                if "USB" in bus_type:
                    device_name = self.utils.search_dict_iter(usb_devices, device_props["Device ID"]).get("Device Description", device_name)

                input_devices_info[device_name] = {
                    "Bus Type": bus_type,
                    "Device ID": device_id
                }

        return input_devices_info
      
    def usb_controllers(self, usb_controllers):
        return {
            controller_name: {
                "Bus Type": controller_props.get("Bus Type", "Unknown"),
                "Device ID": controller_props.get("Device ID", "Unknown")
            }
            for controller_name, controller_props in usb_controllers.items()
            if controller_props.get("Bus Type", "Unknown").startswith("PCI")
        }

    def usb_devices(self, usb_devices, windows_devices):
        usb_devices_info = {}

        for device_name, device_data in usb_devices.items():
            device_props = device_data.get("Device Properties", {})
            manufacturer = device_props.get("Manufacturer", None)
            product = device_props.get("Product", None)
            device_description = "{} {}".format(manufacturer, product) if manufacturer and product else product if product else None

            if not device_description:
                device_id = device_props.get("Device ID", None)
                revision_id = device_props.get("Revision", None)[:-1] if device_props.get("Revision") else None
                hardware_id = "USB\\VID_{}&PID_{}&REV_{}".format(device_id[:4], device_id[5:], revision_id[:-1]) if device_id and revision_id else None

                if hardware_id:
                    device_description = self.utils.search_dict_iter(windows_devices, hardware_id + "&MI_00").get("Driver Description", None)
                    if not device_description:
                        device_description = self.utils.search_dict_iter(windows_devices, hardware_id).get("Driver Description", device_name)

            device_description = self.get_unique_key(device_description, usb_devices_info)

            if "Hub" not in device_description and "Billboard" not in device_description and not "0000-0000" in device_props.get("Device ID"):
                usb_devices_info[device_description] = {
                    "Device Description": device_description.split("_#")[0],
                    "Device Class": device_props.get("Device Class"),
                    "Device ID": device_props.get("Device ID"),
                    "Revision": device_props.get("Revision")
                }

        return usb_devices_info

    def network(self, windows_devices, pci_devices):
        network_info = {}
        
        for device_name, device_props in pci_devices.items():
            device_class = device_props.get("Device Properties", {}).get("Device Class", "Unknown")[6:-1]

            if self.utils.contains_any(["Network", "Ethernet", "WiFi", "Wi-Fi", "Wireless"], device_class + device_name):
                device_id = device_props.get("Device Properties").get("Device ID")

                network_adapter = self.utils.search_dict_iter(windows_devices, device_id)
                network_adapters = self.utils.search_dict_iter(windows_devices, network_adapter)

                for adapter_name, adapter_props in network_adapters.items():
                    bus_type = adapter_props.get("Bus Type", "Unknown")
                    if bus_type.startswith("PCI") or bus_type.startswith("USB"):
                        device_key = adapter_props.get("PCI Device") if not " - " in adapter_props.get("PCI Device", " - ") else adapter_name
                        network_info[device_key.split(" [")[0]] = {
                            "Bus Type": bus_type,
                            "Device ID": adapter_props.get("Device ID", "Unknown")
                        }

        return network_info
    
    def sd_controller(self, pci_devices, usb_devices, hardware):
        combined_devices = pci_devices.copy()
        combined_devices.update(usb_devices)

        for device_name, device_data in combined_devices.items():
            device_props = device_data.get("Device Properties", device_data)
            device_class = device_props.get("Device Class", "Unknown")

            if self.utils.contains_any(["SD Host Controller", "Card Reader", "SDHC", "SDXC", "SDUC", " SD ", "MMC"], device_name + " " + device_class):
                hardware["SD Controller"] = {
                    "Device Description": device_name,
                    "Bus Type": "PCI" if device_props.get("Bus Type", "Unknown").startswith("PCI") else "USB",
                    "Device ID": device_props.get("Device ID", "Unknown")
                }
                
        return hardware

    def intel_mei(self, cpu_codename, pci_devices, hardware):
        if "Sandy Bridge" in cpu_codename or "Ivy Bridge" in cpu_codename:
            intel_mei_data = self.utils.search_dict_iter(pci_devices, "HECI", equal=False)

            if not intel_mei_data:
                intel_mei_data = self.utils.search_dict_iter(pci_devices, "Management Engine Interface", equal=False)
            
            if intel_mei_data:
                intel_mei_props = intel_mei_data.get("Device Properties", {})
                hardware["Intel MEI"] = {
                    "Bus Type": intel_mei_props.get("Bus Type", "Unknown"),
                    "Device ID": intel_mei_props.get("Device ID", "Unknown")
                }
        
        return hardware

    def bluetooth(self, bluetooth, usb_devices, hardware):
        bluetooth_info = {}

        for device_name, device_props in bluetooth.items():
            bus_type = device_props.get("Bus Type", "Unknown")

            if bus_type.startswith("USB"):
                bluetooth_info[device_name] = {
                    "Device ID": device_props.get("Device ID"),
                    "Revision": device_props.get("Revision")
                }

        if not bluetooth_info:
            for usb_device_name, usb_device_props in usb_devices.items():
                device_class = usb_device_props.get("Device Class", {})
                device_id = usb_device_props.get("Device ID", {})

                if "bluetooth" in (usb_device_name + device_class).lower() or device_id in pci_data.BluetoothIDs:
                    bluetooth_info[usb_device_name] = usb_device_props

        if bluetooth_info:
            hardware["Bluetooth"] = bluetooth_info

        return hardware

    def biometric(self, biometric_devices, usb_devices, hardware):
        biometric_info = {
            device_name: {
                "Bus Type": device_props.get("Bus Type", "Unknown"),
                "Device ID": device_props.get("Device ID", "Unknown")
            }
            for device_name, device_props in biometric_devices.items()
        }

        if not biometric_info:
            for device_name, device_data in usb_devices.items():
                if "fingerprint" in device_name.lower():
                    device_props = device_data.get("Device Properties", {})

                    biometric_info[device_name] = {
                        "Bus Type": device_props.get("Bus Type", "Unknown"),
                        "Device ID": device_props.get("Device ID", "Unknown")
                    }

        if biometric_info:
            hardware["Biometric"] = biometric_info

        return hardware

    def parse_dmi(self, dmi_data):
        parsed_dmi = {}

        for full_key, item_value in dmi_data.items():
            occurrence_suffix = ""
            category_name = None

            if "_#" in full_key:
                suffix_idx = full_key.index("_#")
                occurrence_suffix = full_key[suffix_idx:]
                full_key = full_key[:suffix_idx]

            if " / " in full_key:
                category_idx = full_key.index(" / ")
                category_name = full_key[:category_idx]
                device_name = full_key[category_idx + 3:]

            if not category_name:
                parsed_dmi["{}{}".format(full_key, occurrence_suffix)] = item_value
            else:
                if category_name not in parsed_dmi:
                    parsed_dmi[category_name] = {}
                parsed_dmi[category_name]["{}{}".format(device_name, occurrence_suffix)] = item_value

        return parsed_dmi
     
    def parse_windows_devices(self, windows_devices):
        parsed_windows_devices = {}

        for full_key, item_value in windows_devices.items():
            device_props = item_value.get("Device Properties", {})
            
            if "Hardware ID" in device_props:
                device_props.update(self.parse_hardware_id(device_props.get("Hardware ID")))

            category_name = full_key.split(" / ")[0]

            if category_name not in parsed_windows_devices:
                parsed_windows_devices[category_name] = {}

            device_name = device_props.get("Driver Description")

            parsed_windows_devices[category_name][self.get_unique_key(device_name, parsed_windows_devices[category_name])] = device_props

        return parsed_windows_devices
    
    def get_inner_text(self, html_string):
        text = ""
        inside_tag = False
        for char in html_string:
            if char == "<":
                inside_tag = True
            elif char == ">":
                inside_tag = False
            elif not inside_tag:
                text += char
        return text.strip()

    def parse_html_to_json(self, html_content):
        parsed_data = {}
        table_titles = [
            "Summary",
            "DMI",
            "CPU",
            "Windows Devices",
            "PCI Devices",
            "USB Devices"
        ]

        try:
            start_index = html_content.index("</div>") + len("</div>")
        except:
            raise Exception("Your AIDA64 report is missing some information. Please revise it according to the provided guidelines")
        
        for title in table_titles:
            title_marker = f">{title}<"
            if title_marker not in html_content[start_index:]:
                raise Exception("Your AIDA64 report is missing some information. Please revise it according to the provided guidelines")
            
            title_index = html_content[start_index:].index(title_marker)
            table_start_index = start_index + title_index + html_content[start_index+title_index:].index("\n")
            table_end_index = table_start_index + 1 + html_content[table_start_index:].index("</TABLE>") + len("</TABLE>")
            table_html = html_content[table_start_index:table_end_index].strip()

            parsed_data[title] = {}
            stack = [(parsed_data[title], -1)]

            for line in table_html.splitlines():
                if line.startswith("<TR>"):
                    line = line.replace("<TR>", "")
                    
                    level = (len(line) - len(line.lstrip("<TD>"))) // 3 - 1
                    if level < 1:
                        continue

                    while line.startswith("<TD>"):
                        line = line[line.find(">") + 1:]
                else:
                    continue

                line = line.replace("&nbsp;&nbsp;", "")
                td_elements = line.split("<TD>")
                key = self.get_inner_text(td_elements[0])
                value = None if len(td_elements) < 2 else self.get_inner_text(td_elements[-1])
                
                key = key.rstrip(":").strip("[]").strip()

                while stack and stack[-1][1] >= level:
                    stack.pop()
                
                current_dict = stack[-1][0]
                key = self.get_unique_key(key, current_dict)

                if value is None:
                    new_dict = {}
                    current_dict[key] = new_dict
                    stack.append((new_dict, level))
                else:
                    current_dict[key] = value

            start_index = table_end_index

        return parsed_data

    def dump(self, report_path):
        html_content = self.try_open(report_path)
        report_dict = self.parse_html_to_json(html_content)

        dmi = self.parse_dmi(report_dict.get("DMI", {}))
        windows_devices = self.parse_windows_devices(report_dict.get("Windows Devices", {}))

        hardware = {}
        hardware["Motherboard"] = self.motherboard(report_dict.get("Summary", {}).get("Motherboard", {}), dmi)
        hardware["CPU"] = self.cpu(report_dict.get("CPU", {}))
        hardware["GPU"] = self.gpu(report_dict.get("PCI Devices", {}), windows_devices)
        hardware["Network"] = self.network(windows_devices, report_dict.get("PCI Devices", {}))
        hardware["Storage Controllers"] = self.storage_controllers(windows_devices.get("IDE ATA/ATAPI controllers", {}), windows_devices.get("Storage controllers", {}))
        hardware["Audio"] = self.audio(windows_devices)
        hardware["USB Controllers"] = self.usb_controllers(windows_devices.get("Universal Serial Bus controllers", {}))
        usb_devices = self.usb_devices(report_dict.get("USB Devices", {}), windows_devices)
        hardware["Input"] = self.input(windows_devices.get("Human Interface Devices", {}), windows_devices.get("Keyboards", {}), windows_devices.get("Mice and other pointing devices", {}), usb_devices)
        
        hardware = self.biometric(windows_devices.get("Biometric devices", {}), usb_devices, hardware)
        hardware = self.bluetooth(windows_devices.get("Bluetooth", {}), usb_devices, hardware)
        hardware = self.sd_controller(report_dict.get("PCI Devices", {}), usb_devices, hardware)
        hardware = self.intel_mei(hardware["CPU"].get("CPU Codename"), report_dict.get("PCI Devices", {}), hardware)
        
        return hardware