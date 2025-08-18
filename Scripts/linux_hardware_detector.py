#!/usr/bin/env python3
import json
import subprocess
import os
import re

class LinuxHardwareDetector:
    def __init__(self):
        self.hardware_info = {}
    
    def run_command(self, command):
        """Run a shell command and return output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return ""
    
    def get_cpu_info(self):
        """Get CPU information matching Windows Hardware Sniffer format"""
        cpu_info = {}
        
        # Get CPU model name as "Processor Name"
        cpu_model = self.run_command("lscpu | grep 'Model name' | cut -d':' -f2")
        if cpu_model:
            cpu_info["Processor Name"] = cpu_model.strip()
        
        # Get CPU vendor
        vendor = self.run_command("lscpu | grep 'Vendor ID' | cut -d':' -f2")
        if vendor:
            cpu_info["Manufacturer"] = vendor.strip()
        
        # Get core and thread count
        cores = self.run_command("lscpu | grep '^Core(s) per socket' | cut -d':' -f2")
        sockets = self.run_command("lscpu | grep '^Socket(s)' | cut -d':' -f2")
        threads = self.run_command("lscpu | grep '^Thread(s) per core' | cut -d':' -f2")
        
        if cores and sockets:
            try:
                total_cores = int(cores.strip()) * int(sockets.strip())
                cpu_info["Core Count"] = total_cores
                if threads:
                    total_threads = total_cores * int(threads.strip())
                    cpu_info["Thread Count"] = total_threads
            except:
                pass
        
        # Get CPU features/flags for SIMD detection
        flags = self.run_command("lscpu | grep '^Flags' | cut -d':' -f2")
        if flags:
            simd_features = []
            flag_list = flags.strip().split()
            
            # Map Linux flags to Windows-style SIMD features
            flag_mapping = {
                'sse': 'SSE',
                'sse2': 'SSE2', 
                'sse3': 'SSE3',
                'ssse3': 'SSSE3',
                'sse4_1': 'SSE4.1',
                'sse4_2': 'SSE4.2',
                'avx': 'AVX',
                'avx2': 'AVX2',
                'avx512f': 'AVX512'
            }
            
            for flag, feature in flag_mapping.items():
                if flag in flag_list:
                    simd_features.append(feature)
            
            cpu_info["SIMD Features"] = simd_features
        
        # Try to determine CPU codename (best effort)
        family = self.run_command("cat /proc/cpuinfo | grep 'cpu family' | head -1 | cut -d':' -f2")
        model = self.run_command("cat /proc/cpuinfo | grep '^model' | head -1 | cut -d':' -f2")
        
        if family and model:
            cpu_info["Family"] = int(family.strip())
            cpu_info["Model"] = int(model.strip())
            
            # Basic codename mapping for Intel CPUs
            if vendor and "Intel" in vendor:
                model_num = int(model.strip())
                family_num = int(family.strip())
                if family_num == 6:
                    codename_map = {
                        142: "Kaby Lake",
                        158: "Coffee Lake", 
                        165: "Comet Lake",
                        167: "Rocket Lake",
                        151: "Alder Lake",
                        154: "Alder Lake",
                        183: "Raptor Lake",
                        186: "Raptor Lake"
                    }
                    cpu_info["Codename"] = codename_map.get(model_num, "Unknown")
        
        self.hardware_info["CPU"] = cpu_info
    
    def get_gpu_info(self):
        """Get GPU information matching Windows Hardware Sniffer format"""
        gpus = {}
        
        # Get GPU devices from lspci
        gpu_lines = self.run_command("lspci -nn | grep -E 'VGA|3D|Display'").split('\n')
        
        for idx, line in enumerate(gpu_lines):
            if line:
                # Parse PCI info
                match = re.search(r'(\S+)\s+.*:\s+(.*?)\s+\[([0-9a-f]{4}):([0-9a-f]{4})\]', line)
                if match:
                    pci_path = match.group(1)
                    device_name = match.group(2)
                    vendor_id = match.group(3)
                    device_id = match.group(4)
                    
                    # Create GPU entry with Windows-style naming
                    gpu_key = f"GPU {idx}"
                    gpu_data = {
                        "Name": device_name,
                        "Device ID": f"PCI\\VEN_{vendor_id.upper()}&DEV_{device_id.upper()}",
                        "Vendor ID": f"0x{vendor_id}",
                        "PCI Path": pci_path
                    }
                    
                    # Determine manufacturer
                    if vendor_id == "8086":
                        gpu_data["Manufacturer"] = "Intel Corporation"
                    elif vendor_id == "1002":
                        gpu_data["Manufacturer"] = "Advanced Micro Devices, Inc. [AMD/ATI]"  
                    elif vendor_id == "10de":
                        gpu_data["Manufacturer"] = "NVIDIA Corporation"
                    else:
                        gpu_data["Manufacturer"] = "Unknown"
                    
                    # Try to determine codename for AMD GPUs
                    if vendor_id == "1002":
                        codename_map = {
                            "67df": "Ellesmere",
                            "67ef": "Baffin",
                            "731f": "Navi 10",
                            "7340": "Navi 14",
                            "73bf": "Navi 21",
                            "73df": "Navi 22",
                            "73ff": "Navi 23"
                        }
                        gpu_data["Codename"] = codename_map.get(device_id.lower(), "Unknown")
                    
                    gpus[gpu_key] = gpu_data
        
        self.hardware_info["GPU"] = gpus
    
    def get_motherboard_info(self):
        """Get motherboard information"""
        mobo = {}
        
        # Get board info from DMI
        manufacturer = self.run_command("cat /sys/class/dmi/id/board_vendor 2>/dev/null")
        if manufacturer:
            mobo["Manufacturer"] = manufacturer
        
        model = self.run_command("cat /sys/class/dmi/id/board_name 2>/dev/null")
        if model:
            mobo["Model"] = model
        
        # Determine platform type
        chassis = self.run_command("cat /sys/class/dmi/id/chassis_type 2>/dev/null")
        if chassis:
            laptop_types = ["8", "9", "10", "11", "14", "30", "31", "32"]
            if chassis in laptop_types:
                mobo["Platform"] = "Laptop"
            else:
                mobo["Platform"] = "Desktop"
        else:
            mobo["Platform"] = "Desktop"
        
        self.hardware_info["Motherboard"] = mobo
    
    def get_audio_info(self):
        """Get audio device information"""
        audio = {}
        
        # Get audio devices from lspci
        audio_lines = self.run_command("lspci -nn | grep -i 'audio'").split('\n')
        
        for idx, line in enumerate(audio_lines):
            if line:
                match = re.search(r'(\S+)\s+.*:\s+(.*?)\s+\[([0-9a-f]{4}):([0-9a-f]{4})\]', line)
                if match:
                    pci_path = match.group(1)
                    device_name = match.group(2)
                    vendor_id = match.group(3)
                    device_id = match.group(4)
                    
                    audio_key = f"Audio Device {idx}"
                    audio[audio_key] = {
                        "Name": device_name,
                        "Device ID": f"PCI\\VEN_{vendor_id.upper()}&DEV_{device_id.upper()}",
                        "Vendor ID": f"0x{vendor_id}",
                        "PCI Path": pci_path
                    }
        
        self.hardware_info["Audio"] = audio
    
    def get_network_info(self):
        """Get network adapter information"""
        network = {}
        
        # Get network devices from lspci
        net_lines = self.run_command("lspci -nn | grep -i 'network\\|ethernet'").split('\n')
        
        for idx, line in enumerate(net_lines):
            if line:
                match = re.search(r'(\S+)\s+.*:\s+(.*?)\s+\[([0-9a-f]{4}):([0-9a-f]{4})\]', line)
                if match:
                    pci_path = match.group(1)
                    device_name = match.group(2)
                    vendor_id = match.group(3)
                    device_id = match.group(4)
                    
                    net_key = f"Network Adapter {idx}"
                    network[net_key] = {
                        "Name": device_name,
                        "Device ID": f"PCI\\VEN_{vendor_id.upper()}&DEV_{device_id.upper()}",
                        "Vendor ID": f"0x{vendor_id}",
                        "PCI Path": pci_path
                    }
        
        self.hardware_info["Network Adapters"] = network
    
    def get_storage_controllers(self):
        """Get storage controller information"""
        controllers = {}
        
        # Get storage controllers from lspci
        storage_lines = self.run_command("lspci -nn | grep -E 'SATA|NVMe|AHCI|IDE|RAID'").split('\n')
        
        for idx, line in enumerate(storage_lines):
            if line:
                match = re.search(r'(\S+)\s+.*:\s+(.*?)\s+\[([0-9a-f]{4}):([0-9a-f]{4})\]', line)
                if match:
                    pci_path = match.group(1)
                    device_name = match.group(2)
                    vendor_id = match.group(3)
                    device_id = match.group(4)
                    
                    controller_key = f"Storage Controller {idx}"
                    controllers[controller_key] = {
                        "Name": device_name,
                        "Device ID": f"PCI\\VEN_{vendor_id.upper()}&DEV_{device_id.upper()}",
                        "Vendor ID": f"0x{vendor_id}",
                        "PCI Path": pci_path,
                        "Bus Type": "PCI"
                    }
        
        self.hardware_info["Storage Controllers"] = controllers
    
    def get_bluetooth_info(self):
        """Get Bluetooth device information"""
        bluetooth = {}
        
        # Try to get Bluetooth devices from USB
        usb_bt = self.run_command("lsusb | grep -i bluetooth")
        if usb_bt:
            lines = usb_bt.split('\n')
            for idx, line in enumerate(lines):
                if line:
                    # Parse USB ID
                    match = re.search(r'ID\s+([0-9a-f]{4}):([0-9a-f]{4})\s+(.*)', line)
                    if match:
                        vendor_id = match.group(1)
                        device_id = match.group(2)
                        device_name = match.group(3)
                        
                        bt_key = f"Bluetooth Device {idx}"
                        bluetooth[bt_key] = {
                            "Name": device_name,
                            "Device ID": f"USB\\VID_{vendor_id.upper()}&PID_{device_id.upper()}",
                            "Vendor ID": f"0x{vendor_id}",
                            "Bus Type": "USB"
                        }
        
        self.hardware_info["Bluetooth"] = bluetooth
    
    def export_acpi_tables(self, output_dir):
        """Export ACPI tables"""
        acpi_dir = os.path.join(output_dir, "ACPI")
        os.makedirs(acpi_dir, exist_ok=True)
        
        # List of ACPI tables to export
        tables = ["DSDT", "SSDT", "FADT", "MADT", "HPET", "MCFG", "ECDT", "BGRT", "DMAR"]
        
        for table in tables:
            table_path = f"/sys/firmware/acpi/tables/{table}"
            if os.path.exists(table_path):
                output_file = os.path.join(acpi_dir, f"{table}.aml")
                try:
                    # Use sudo if available, otherwise try without
                    result = self.run_command(f"sudo cat {table_path} 2>/dev/null")
                    if not result:
                        result = self.run_command(f"cat {table_path} 2>/dev/null")
                    
                    if result:
                        with open(output_file, 'wb') as f:
                            f.write(result.encode('latin-1'))
                        print(f"  Exported {table}")
                except:
                    pass
        
        # Export multiple SSDTs if they exist  
        ssdt_index = 1
        while os.path.exists(f"/sys/firmware/acpi/tables/SSDT{ssdt_index}"):
            table_path = f"/sys/firmware/acpi/tables/SSDT{ssdt_index}"
            output_file = os.path.join(acpi_dir, f"SSDT-{ssdt_index}.aml")
            try:
                result = self.run_command(f"sudo cat {table_path} 2>/dev/null")
                if not result:
                    result = self.run_command(f"cat {table_path} 2>/dev/null")
                
                if result:
                    with open(output_file, 'wb') as f:
                        f.write(result.encode('latin-1'))
                    print(f"  Exported SSDT-{ssdt_index}")
                    ssdt_index += 1
                else:
                    break
            except:
                break
    
    def collect_all(self):
        """Collect all hardware information"""
        print("Gathering CPU information...")
        self.get_cpu_info()
        
        print("Gathering GPU information...")
        self.get_gpu_info()
        
        print("Gathering Motherboard information...")
        self.get_motherboard_info()
        
        print("Gathering Audio information...")
        self.get_audio_info()
        
        print("Gathering Network information...")
        self.get_network_info()
        
        print("Gathering Storage Controllers...")
        self.get_storage_controllers()
        
        print("Gathering Bluetooth devices...")
        self.get_bluetooth_info()
        
        return self.hardware_info
    
    def export_report(self, output_dir=None):
        """Export hardware report to JSON file"""
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "SysReport")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Collect hardware info
        report = self.collect_all()
        
        # Save JSON report
        report_path = os.path.join(output_dir, "Report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {report_path}")
        
        # Try to export ACPI tables
        print("\nExporting ACPI tables...")
        self.export_acpi_tables(output_dir)
        
        return report_path

if __name__ == "__main__":
    detector = LinuxHardwareDetector()
    detector.export_report()