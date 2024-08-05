from Scripts.datasets import pci_data
from Scripts import gpu_identifier
from Scripts import utils
from bs4 import BeautifulSoup

class AIDA64:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        self.encodings = ['utf-8', 'latin-1', 'ISO-8859-1']
        self.gpu_identifier = gpu_identifier.GPUIdentifier()
        self.utils = utils.Utils()
    
    def try_open(self, file_path):
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
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
    
    def hardware_id(self, hardware_id):
        if "VEN" in hardware_id:
            return {
                "Bus Type": hardware_id.split("\\")[0],
                "Device ID": "{}-{}".format(hardware_id.split("VEN_")[-1].split("&")[0], hardware_id.split("DEV_")[-1].split("&")[0])
            }
        
        if "VID" in hardware_id:
            return {
                "Bus Type": hardware_id.split("\\")[0],
                "Device ID": "{}-{}".format(hardware_id.split("VID_")[-1].split("&")[0], hardware_id.split("PID_")[-1].split("&")[0]),
                "Revision": hardware_id.split("REV_")[-1].split("&")[0]
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

        # Count and format CPU configuration
        motherboard_info["CPU Configuration"] = str(len(dmi.get("Processors", {}))).zfill(2)

        return motherboard_info
    
    def cpu(self, cpu_table):
        cpu_info = {}

        # Extract CPU Manufacturer
        cpu_info["CPU Manufacturer"] = cpu_table.get("CPU Manufacturer", {}).get("Company Name", "Unknown")

        # Extract Processor Name
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

        # Extract CPU Codename
        cpu_info["CPU Codename"] = cpu_props.get("CPU Alias", "Unknown")

        # Extract CPU Cores count
        core_indices = []
        for key in list(cpu_table.get("CPU Utilization", {}).keys()):
            core_index = key.split("#")[2].split(" ")[0]
            if "CPU #1" in key and core_index not in core_indices:
                core_indices.append(core_index)
        cpu_info["CPU Cores"] = str(len(core_indices)).zfill(2)

        # Extract Instruction Set
        cpu_info["Instruction Set"] = cpu_props.get("Instruction Set", "Unknown")

        return cpu_info

    def memory(self, memory_arrays, memory_devices):
        return {
            "Memory Arrays": [
                memory_array.get("Memory Array Properties", {})
                for function, memory_array in memory_arrays.items()
            ],
            "Memory Devices": [
                memory_device.get("Memory Device Properties", {})
                for device_locator, memory_device in memory_devices.items()
            ]
        }
    
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
    
    def monitor(self, monitor):
        return {
            monitor_data["Monitor Properties"].get("Monitor Name", monitor_name): {
                "Monitor Type": monitor_data["Monitor Properties"].get("Monitor Type", "Unknown"),
                "Maximum Resolution": monitor_data["Monitor Properties"].get("Maximum Resolution", list(monitor_data.get("Supported Video Modes", {}).keys())[-1].split("_")[0] if "Supported Video Modes" in monitor_data else "Unknown")
            }
            for monitor_name, monitor_data in monitor.items()
            if "Monitor Properties" in monitor_data
        }
       
    def acpi(self, acpi_tables):
        return [
            {
                "ACPI Signature": acpi_table["ACPI Table Properties"].get("ACPI Signature", "Unknown"),
                "Table Description": acpi_table["ACPI Table Properties"].get("Table Description", "Unknown"),
                "Table Length": acpi_table["ACPI Table Properties"].get("Table Length", "Unknown"),
                "OEM Table ID": acpi_table["ACPI Table Properties"].get("OEM Table ID", "Unknown")
            }
            for table_key, acpi_table in acpi_tables.items()
            if "ACPI Table Properties" in acpi_table
        ]

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
                hardware_id = 'USB\\VID_{}&PID_{}&REV_{}'.format(device_id[:4], device_id[5:], revision_id[:-1]) if device_id and revision_id else None

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
                    "Revision ID": device_props.get("Revision")
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
                    device_description = adapter_name + adapter_props.get("PCI Device", "Unknown")
                    connection_name = "WiFi" if "WiFi" in device_description or "Wi-Fi" in device_description or "Wireless" in device_description else \
                        "Ethernet" if "Network" in device_description or "Ethernet" in device_description else None
                    bus_type = adapter_props.get("Bus Type", "Unknown")
                    if (bus_type.startswith("PCI") or bus_type.startswith("USB")) and connection_name:
                        device_key = adapter_props.get("PCI Device") if not " - " in adapter_props.get("PCI Device", " - ") else adapter_name
                        network_info[device_key.split(" [")[0]] = {
                            "Connection Name": connection_name,
                            "Bus Type": bus_type,
                            "Device ID": adapter_props.get("Device ID", "Unknown")
                        }

        return self.utils.sort_dict_by_key(network_info, "Connection Name")
    
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
            occurrence_suffix = ''
            category_name = None

            if '_#' in full_key:
                suffix_idx = full_key.index('_#')
                occurrence_suffix = full_key[suffix_idx:]
                full_key = full_key[:suffix_idx]

            if ' / ' in full_key:
                category_idx = full_key.index(' / ')
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
            
            # Update device properties with hardware ID if available
            if "Hardware ID" in device_props:
                device_props.update(self.hardware_id(device_props.get("Hardware ID")))

            # Extract category name from the full key
            category_name = full_key.split(" / ")[0]

            # Initialize category dictionary if not already present
            if category_name not in parsed_windows_devices:
                parsed_windows_devices[category_name] = {}

            # Extract device name from device properties
            device_name = device_props.get("Driver Description")

            # Add device to category dictionary
            parsed_windows_devices[category_name][self.get_unique_key(device_name, parsed_windows_devices[category_name])] = device_props

        return parsed_windows_devices

    def html_to_dict(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all('table')

        if not tables:
            return {}

        root = {}
        table_names = [
            "Summary",
            "DMI",
            "CPU",
            "Windows Devices",
            "PCI Devices",
            "USB Devices"
        ]
        table = None

        for table_content in tables:
            # Find the table header to identify the table
            pt_element = table_content.find("td", class_="pt")
            if pt_element:
                table = pt_element.text.strip()
            elif table in table_names:
                root[table] = {}
                stack = [(root[table], -1)]  # Stack holds (current_dict, current_level)

                lines = str(table_content).strip().splitlines()

                for line in lines:
                    if line.startswith('<tr>'):
                        # Remove <tr> tag
                        line = line.replace('<tr>', '')

                        # Calculate the current level based on the number of <td> tags
                        level = (len(line) - len(line.lstrip('<td>'))) // 3 - 1
                        if level < 1:
                            continue

                        # Remove all <td> tags from the left
                        while line.startswith("<td>"):
                            line = line[line.find(">") + 1:]

                        if not line.startswith('<td') and '<td' in line:
                            idx = line.index('<td')
                            line = '{}{}{}{}'.format('<td>', line[:idx], '</td>', line[idx:])
                    else:
                        continue

                    soup_line = BeautifulSoup(line, "html.parser")
                    td_elements = soup_line.find_all('td')
                    key = td_elements[0].text.strip()
                    value = None if len(td_elements) < 2 else td_elements[-1].text.strip()

                    # Clean the key
                    key = key.rstrip(":").strip("[]").strip()

                    # Pop from stack to find the correct parent dictionary
                    while stack and stack[-1][1] >= level:
                        stack.pop()

                    # Add the new key-value pair
                    current_dict = stack[-1][0]
                    key = self.get_unique_key(key, current_dict)

                    if value is None:
                        new_dict = {}
                        current_dict[key] = new_dict
                        stack.append((new_dict, level))
                    else:
                        if '<td class="cc">' not in line:
                            current_dict[key] = value
                        else:
                            if not current_dict.items():
                                current_dict[key] = []
                                current_dict[value] = []
                            else:
                                current_dict[list(current_dict.keys())[0]].append(key)
                                current_dict[list(current_dict.keys())[1]].append(value)

        if len(table_names) != len(root):
            raise Exception("Your AIDA64 report is missing some information. Please revise it according to the provided guidelines")
        return root

    def dump(self, report_path):
        html_content = self.try_open(report_path)
        report_dict = self.html_to_dict(html_content)

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