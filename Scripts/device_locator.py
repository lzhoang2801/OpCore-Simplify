import run
import os
import re

class DeviceLocator:
    def __init__(self):
        self.run = run.Run().run
    
    def convert_pci_path(self, path):
        components = path.split("#")
        result = []
        
        for component in components:
            if component.startswith("PCIROOT"):
                match = re.match(r"PCIROOT\((\d+)\)", component)
                if match:
                    result.append("PciRoot(0x{:x})".format(int(match.group(1))))
            elif component.startswith("PCI"):
                match = re.match(r"PCI\((\w+)\)", component)
                if match:
                    values = match.group(1)
                    if len(values) == 4:
                        bus = int(values[:2], 16)
                        device = int(values[2:], 16)
                        result.append("Pci(0x{:x},0x{:x})".format(bus, device))
                    else:
                        result.append("Pci(0x{:x})".format(int(values, 16)))
                        
        return "/".join(result)
    
    def convert_acpi_path(self, path):
        components = path.split("#")
        result = []
        
        for component in components:
            match = re.match(r'ACPI\((\w+)\)', component)
            if match:
                if result:
                    result.append(match.group(1))
                else:
                    result.append("\\{}".format(match.group(1)[:-1]))
                
        return '.'.join(result)
    
    def get_device_location_paths(self, bus_type, pci_id, subsystem_id=None, revision_id=None):
        if os.name != 'nt':
            return None
    
        vendor_id = pci_id[:4]
        device_id = pci_id[5:]
        hardware_id = "{}\\VEN_{}&DEV_{}".format(bus_type, vendor_id, device_id)
        if subsystem_id:
            hardware_id += "&SUBSYS_{}".format(subsystem_id)
        if revision_id:
            hardware_id += "&REV_{}".format(revision_id)
        
        query_device_command = '''
        $searchPattern = "{}"
        Get-PnpDevice | Where-Object {{ $_.InstanceId -like "$searchPattern*" }} | Select-Object InstanceId
        '''

        output = self.run({
            "args":["powershell", "-Command", query_device_command.format(hardware_id)]
        })
        
        if output[-1] != 0 or not output[0]:
            return None
        
        lines = output[0].splitlines()
        if len(lines) < 4:
            return None

        device_instance_id_with_topology = lines[3].strip()
        if not hardware_id in device_instance_id_with_topology:
            return None
                    
        get_location_paths_command = (
            'Get-PnpDeviceProperty -InstanceId "{}" '
            '-KeyName DEVPKEY_Device_LocationPaths | Select-Object -ExpandProperty Data'
        )
        
        output = self.run({
            "args":["powershell", "-Command", get_location_paths_command.format(device_instance_id_with_topology)]
        })
        
        if output[-1] != 0 or not output[0]:
            return None

        location_paths = output[0].strip().splitlines()
        return {
            "PCI Path": self.convert_pci_path(location_paths[0]),
            "APCI Path": self.convert_acpi_path(location_paths[-1])
        }