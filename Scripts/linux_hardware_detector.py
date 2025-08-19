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
            # Use list of args instead of shell=True for security
            if isinstance(command, str):
                import shlex
                command = shlex.split(command)
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return ""
        except Exception:
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
    
    def get_input_devices(self):
        """Get input device information (touchpad, touchscreen, keyboard, mouse)"""
        input_devices = {}
        
        # Parse /proc/bus/input/devices for detailed input device info
        try:
            with open('/proc/bus/input/devices', 'r') as f:
                devices_content = f.read()
            
            # Split into individual device entries
            device_entries = devices_content.split('\n\n')
            
            for entry in device_entries:
                if not entry.strip():
                    continue
                
                # Parse device information
                name = ""
                phys = ""
                sysfs = ""
                handlers = ""
                
                for line in entry.split('\n'):
                    if line.startswith('N: Name='):
                        name = line.split('Name=')[1].strip('"')
                    elif line.startswith('P: Phys='):
                        phys = line.split('Phys=')[1].strip()
                    elif line.startswith('S: Sysfs='):
                        sysfs = line.split('Sysfs=')[1].strip()
                    elif line.startswith('H: Handlers='):
                        handlers = line.split('Handlers=')[1].strip()
                
                # Determine device type and connection
                device_type = None
                connection_type = "Unknown"
                
                # Check device type based on name and handlers
                name_lower = name.lower()
                if 'touchpad' in name_lower or 'trackpad' in name_lower:
                    device_type = "Touchpad"
                elif 'touchscreen' in name_lower or 'touch' in name_lower and 'screen' in name_lower:
                    device_type = "Touchscreen"
                elif 'keyboard' in name_lower:
                    device_type = "Keyboard"
                elif 'mouse' in name_lower:
                    device_type = "Mouse"
                elif 'pen' in name_lower or 'stylus' in name_lower:
                    device_type = "Pen/Stylus"
                elif 'trackpoint' in name_lower or 'pointing stick' in name_lower:
                    device_type = "TrackPoint"
                
                # Determine connection type from physical path
                if phys:
                    if 'usb' in phys.lower():
                        connection_type = "USB"
                    elif 'i2c' in phys.lower():
                        connection_type = "I2C"
                    elif 'serio' in phys.lower() or 'isa' in phys.lower():
                        connection_type = "PS/2"
                    elif 'bluetooth' in phys.lower():
                        connection_type = "Bluetooth"
                    elif 'spi' in phys.lower():
                        connection_type = "SPI"
                
                # Also check sysfs path for connection hints
                if sysfs and connection_type == "Unknown":
                    if '/i2c-' in sysfs or '/i2c/' in sysfs:
                        connection_type = "I2C"
                    elif '/usb' in sysfs:
                        connection_type = "USB"
                    elif '/serio' in sysfs:
                        connection_type = "PS/2"
                    elif '/platform/' in sysfs:
                        # Platform devices could be I2C or other
                        if 'i2c' in name_lower:
                            connection_type = "I2C"
                        else:
                            connection_type = "Platform"
                
                # Add to devices if it's an input device we care about
                if device_type and name:
                    device_key = f"{device_type}_{len([k for k in input_devices if k.startswith(device_type)])}"
                    
                    input_devices[device_key] = {
                        "Name": name,
                        "Type": device_type,
                        "Connection": connection_type,
                        "Physical": phys if phys else "N/A",
                        "Handlers": handlers if handlers else "N/A"
                    }
                    
                    # Try to get vendor and product IDs from sysfs
                    if sysfs:
                        # Extract IDs from path if available
                        id_match = re.search(r'/([0-9a-f]{4}):([0-9a-f]{4})', sysfs)
                        if id_match:
                            input_devices[device_key]["Vendor ID"] = f"0x{id_match.group(1)}"
                            input_devices[device_key]["Product ID"] = f"0x{id_match.group(2)}"
        
        except (IOError, OSError):
            # Fallback to xinput if /proc not available
            xinput_output = self.run_command("xinput list")
            if xinput_output:
                for line in xinput_output.split('\n'):
                    if '↳' in line or '⎜' in line:  # Slave devices
                        # Parse xinput device
                        match = re.search(r'[↳⎜]\s+(.*?)\s+id=(\d+)', line)
                        if match:
                            device_name = match.group(1).strip()
                            device_id = match.group(2)
                            
                            # Determine type from name
                            name_lower = device_name.lower()
                            device_type = None
                            
                            if 'touchpad' in name_lower:
                                device_type = "Touchpad"
                            elif 'touchscreen' in name_lower:
                                device_type = "Touchscreen"
                            elif 'keyboard' in name_lower:
                                device_type = "Keyboard"
                            elif 'mouse' in name_lower:
                                device_type = "Mouse"
                            
                            if device_type:
                                device_key = f"{device_type}_{device_id}"
                                input_devices[device_key] = {
                                    "Name": device_name,
                                    "Type": device_type,
                                    "Connection": "Unknown",
                                    "X11 ID": device_id
                                }
        
        self.hardware_info["Input Devices"] = input_devices
    
    def get_biometric_devices(self):
        """Get biometric device information (fingerprint readers, face recognition, etc.)"""
        biometric = {}
        
        # Check for fingerprint readers via USB
        fingerprint_vendors = {
            "138a": "Validity Sensors",
            "147e": "Upek",
            "1c7a": "LighTuning/EgisTec",
            "27c6": "Shenzhen Goodix",
            "06cb": "Synaptics",
            "04f3": "Elan",
            "298d": "Realtek",
            "0483": "STMicroelectronics",
            "1c7e": "SecuGen",
            "0a5c": "Broadcom Corp",
            "045e": "Microsoft Corp",
            "05ba": "DigitalPersona"
        }
        
        # Security key vendors (FIDO/U2F)
        security_key_vendors = {
            "18d1": "Google Inc.",
            "1050": "Yubico",
            "096e": "Feitian Technologies"
        }
        
        # Get all USB devices
        lsusb_output = self.run_command("lsusb")
        if lsusb_output:
            for line in lsusb_output.split('\n'):
                if line:
                    match = re.search(r'ID\s+([0-9a-f]{4}):([0-9a-f]{4})\s+(.*)', line)
                    if match:
                        vendor_id = match.group(1).lower()
                        device_id = match.group(2)
                        device_desc = match.group(3)
                        
                        # Check if it's a known fingerprint vendor
                        if vendor_id in fingerprint_vendors:
                            bio_key = f"Fingerprint Reader {len(biometric)}"
                            biometric[bio_key] = {
                                "Name": device_desc,
                                "Type": "Fingerprint Reader",
                                "Manufacturer": fingerprint_vendors[vendor_id],
                                "Device ID": f"USB\\VID_{vendor_id.upper()}&PID_{device_id.upper()}",
                                "Vendor ID": f"0x{vendor_id}",
                                "Connection": "USB"
                            }
                        # Also check for generic fingerprint/biometric keywords
                        elif any(keyword in device_desc.lower() for keyword in ['fingerprint', 'biometric', 'fpr']):
                            bio_key = f"Fingerprint Reader {len(biometric)}"
                            biometric[bio_key] = {
                                "Name": device_desc,
                                "Type": "Fingerprint Reader",
                                "Device ID": f"USB\\VID_{vendor_id.upper()}&PID_{device_id.upper()}",
                                "Vendor ID": f"0x{vendor_id}",
                                "Connection": "USB"
                            }
                        # Check for security keys
                        elif vendor_id in security_key_vendors:
                            bio_key = f"Security Key {len([k for k in biometric if 'Security Key' in k])}"
                            biometric[bio_key] = {
                                "Name": device_desc,
                                "Type": "Security Key (FIDO/U2F)",
                                "Manufacturer": security_key_vendors[vendor_id],
                                "Device ID": f"USB\\VID_{vendor_id.upper()}&PID_{device_id.upper()}",
                                "Vendor ID": f"0x{vendor_id}",
                                "Connection": "USB"
                            }
                        # Check for security key keywords
                        elif any(keyword in device_desc.lower() for keyword in ['security key', 'yubikey', 'fido', 'u2f', 'titan']):
                            bio_key = f"Security Key {len([k for k in biometric if 'Security Key' in k])}"
                            biometric[bio_key] = {
                                "Name": device_desc,
                                "Type": "Security Key (FIDO/U2F)",
                                "Device ID": f"USB\\VID_{vendor_id.upper()}&PID_{device_id.upper()}",
                                "Vendor ID": f"0x{vendor_id}",
                                "Connection": "USB"
                            }
        
        # Check for TPM (Trusted Platform Module) - often used with biometrics
        tpm_info = self.run_command("ls /dev/tpm* 2>/dev/null")
        if tpm_info:
            bio_key = f"TPM Device"
            biometric[bio_key] = {
                "Name": "Trusted Platform Module",
                "Type": "Security Chip",
                "Device": tpm_info.strip()
            }
        
        # Check if fprintd service is available (fingerprint daemon)
        fprintd = self.run_command("systemctl status fprintd 2>/dev/null | head -1")
        if fprintd and "fprintd.service" in fprintd:
            # Try to list enrolled fingerprints
            enrolled = self.run_command("fprintd-list $USER 2>/dev/null")
            if enrolled and "enrolled" in enrolled.lower():
                if not biometric:  # Only add if we haven't detected hardware already
                    bio_key = "Fingerprint Reader 0"
                    biometric[bio_key] = {
                        "Name": "Generic Fingerprint Reader",
                        "Type": "Fingerprint Reader",
                        "Status": "Configured",
                        "Connection": "Unknown"
                    }
        
        # Check for camera devices that might be used for face recognition
        camera_devices = self.run_command("ls /dev/video* 2>/dev/null")
        if camera_devices:
            # Check if it's an IR camera (often used for Windows Hello-style face recognition)
            for device in camera_devices.split():
                device_name = self.run_command(f"v4l2-ctl -d {device} --info 2>/dev/null | grep 'Card type' | cut -d: -f2")
                if device_name:
                    device_name = device_name.strip()
                    # Check for IR or depth camera indicators
                    if any(keyword in device_name.lower() for keyword in ['ir', 'depth', 'infrared', '3d']):
                        bio_key = f"IR Camera {len([k for k in biometric if 'Camera' in k])}"
                        biometric[bio_key] = {
                            "Name": device_name,
                            "Type": "IR Camera (Face Recognition)",
                            "Device": device,
                            "Connection": "Platform"
                        }
        
        self.hardware_info["Biometric Devices"] = biometric
    
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
                    # Read binary ACPI data properly
                    try:
                        # Try with sudo first
                        result = subprocess.run(['sudo', 'cat', table_path], 
                                              capture_output=True, timeout=5)
                        if result.returncode != 0:
                            # Fall back to non-sudo
                            result = subprocess.run(['cat', table_path], 
                                                  capture_output=True, timeout=5)
                        
                        if result.returncode == 0 and result.stdout:
                            with open(output_file, 'wb') as f:
                                f.write(result.stdout)  # Already binary data
                            print(f"  Exported {table}")
                    except subprocess.TimeoutExpired:
                        print(f"  Timeout reading {table}")
                except (IOError, OSError) as e:
                    print(f"  Failed to export {table}: {e}")
        
        # Export multiple SSDTs if they exist  
        ssdt_index = 1
        while os.path.exists(f"/sys/firmware/acpi/tables/SSDT{ssdt_index}"):
            table_path = f"/sys/firmware/acpi/tables/SSDT{ssdt_index}"
            output_file = os.path.join(acpi_dir, f"SSDT-{ssdt_index}.aml")
            try:
                # Read binary ACPI data properly
                result = subprocess.run(['sudo', 'cat', table_path], 
                                      capture_output=True, timeout=5)
                if result.returncode != 0:
                    result = subprocess.run(['cat', table_path], 
                                          capture_output=True, timeout=5)
                
                if result.returncode == 0 and result.stdout:
                    with open(output_file, 'wb') as f:
                        f.write(result.stdout)  # Already binary data
                    print(f"  Exported SSDT-{ssdt_index}")
                    ssdt_index += 1
                else:
                    break
            except (subprocess.TimeoutExpired, IOError, OSError):
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
        
        print("Gathering Input devices...")
        self.get_input_devices()
        
        print("Gathering Biometric devices...")
        self.get_biometric_devices()
        
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