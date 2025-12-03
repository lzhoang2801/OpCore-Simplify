from Scripts import utils
import json
import os
import re

class ReportValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.u = utils.Utils()
        
        self.PATTERNS = {
            "not_empty": r".+",
            "platform": r"^(Desktop|Laptop)$",
            "firmware_type": r"^(UEFI|BIOS)$",
            "bus_type": r"^(PCI|USB|ACPI|ROOT)$",
            "cpu_manufacturer": r"^(Intel|AMD)$",
            "gpu_manufacturer": r"^(Intel|AMD|NVIDIA)$",
            "gpu_device_type": r"^(Integrated GPU|Discrete GPU|Unknown)$",
            "hex_id": r"^(?:0x)?[0-9a-fA-F]+$",
            "device_id": r"^[0-9A-F]{4}(?:-[0-9A-F]{4})?$",
            "resolution": r"^\d+x\d+$",
            "pci_path": r"^PciRoot\(0x[0-9a-fA-F]+\)(?:/Pci\(0x[0-9a-fA-F]+,0x[0-9a-fA-F]+\))+$",
            "acpi_path": r"^[\\]?_SB(\.[A-Z0-9_]+)+$",
            "core_count": r"^\d+$",
            "connector_type": r"^(VGA|DVI|HDMI|LVDS|DP|eDP|Internal|Uninitialized)$",
            "enabled_disabled": r"^(Enabled|Disabled)$"
        }
        
        self.SCHEMA = {
            "type": dict,
            "schema": {
                "Motherboard": {
                    "type": dict,
                    "required": True,
                    "schema": {
                        "Name": {"type": str},
                        "Chipset": {"type": str},
                        "Platform": {"type": str, "pattern": self.PATTERNS["platform"]}
                    }
                },
                "BIOS": {
                    "type": dict,
                    "required": True,
                    "schema": {
                        "Version": {"type": str, "required": False},
                        "Release Date": {"type": str, "required": False},
                        "System Type": {"type": str, "required": False},
                        "Firmware Type": {"type": str, "pattern": self.PATTERNS["firmware_type"]},
                        "Secure Boot": {"type": str, "pattern": self.PATTERNS["enabled_disabled"]}
                    }
                },
                "CPU": {
                    "type": dict,
                    "required": True,
                    "schema": {
                        "Manufacturer": {"type": str, "pattern": self.PATTERNS["cpu_manufacturer"]},
                        "Processor Name": {"type": str},
                        "Codename": {"type": str},
                        "Core Count": {"type": str, "pattern": self.PATTERNS["core_count"]},
                        "CPU Count": {"type": str, "pattern": self.PATTERNS["core_count"]},
                        "SIMD Features": {"type": str}
                    }
                },
                "GPU": {
                    "type": dict,
                    "required": True,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Manufacturer": {"type": str, "pattern": self.PATTERNS["gpu_manufacturer"]},
                            "Codename": {"type": str},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]},
                            "Device Type": {"type": str, "pattern": self.PATTERNS["gpu_device_type"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "PCI Path": {"type": str, "required": False, "pattern": self.PATTERNS["pci_path"]},
                            "ACPI Path": {"type": str, "required": False, "pattern": self.PATTERNS["acpi_path"]},
                            "Resizable BAR": {"type": str, "required": False, "pattern": self.PATTERNS["enabled_disabled"]}
                        }
                    }
                },
                "Monitor": {
                    "type": dict,
                    "required": False,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Connector Type": {"type": str, "pattern": self.PATTERNS["connector_type"]},
                            "Resolution": {"type": str, "pattern": self.PATTERNS["resolution"]},
                            "Connected GPU": {"type": str, "required": False}
                        }
                    }
                },
                "Network": {
                    "type": dict,
                    "required": True,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "PCI Path": {"type": str, "required": False, "pattern": self.PATTERNS["pci_path"]},
                            "ACPI Path": {"type": str, "required": False, "pattern": self.PATTERNS["acpi_path"]}
                        }
                    }
                },
                "Sound": {
                    "type": dict,
                    "required": False,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "Audio Endpoints": {"type": list, "required": False, "item_rule": {"type": str}},
                            "Controller Device ID": {"type": str, "required": False, "pattern": self.PATTERNS["device_id"]}
                        }
                    }
                },
                "USB Controllers": {
                    "type": dict,
                    "required": True,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "PCI Path": {"type": str, "required": False, "pattern": self.PATTERNS["pci_path"]},
                            "ACPI Path": {"type": str, "required": False, "pattern": self.PATTERNS["acpi_path"]}
                        }
                    }
                },
                "Input": {
                    "type": dict,
                    "required": True,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device": {"type": str, "required": False},
                            "Device ID": {"type": str, "required": False, "pattern": self.PATTERNS["device_id"]},
                            "Device Type": {"type": str, "required": False}
                        }
                    }
                },
                "Storage Controllers": {
                    "type": dict,
                    "required": True,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "PCI Path": {"type": str, "required": False, "pattern": self.PATTERNS["pci_path"]},
                            "ACPI Path": {"type": str, "required": False, "pattern": self.PATTERNS["acpi_path"]},
                            "Disk Drives": {"type": list, "required": False, "item_rule": {"type": str}}
                        }
                    }
                },
                "Biometric": {
                    "type": dict,
                    "required": False,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device": {"type": str, "required": False},
                            "Device ID": {"type": str, "required": False, "pattern": self.PATTERNS["device_id"]}
                        }
                    }
                },
                "Bluetooth": {
                    "type": dict,
                    "required": False,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]}
                        }
                    }
                },
                "SD Controller": {
                    "type": dict,
                    "required": False,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str, "pattern": self.PATTERNS["bus_type"]},
                            "Device ID": {"type": str, "pattern": self.PATTERNS["device_id"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "PCI Path": {"type": str, "required": False, "pattern": self.PATTERNS["pci_path"]},
                            "ACPI Path": {"type": str, "required": False, "pattern": self.PATTERNS["acpi_path"]}
                        }
                    }
                },
                "System Devices": {
                    "type": dict,
                    "required": False,
                    "values_rule": {
                        "type": dict,
                        "schema": {
                            "Bus Type": {"type": str},
                            "Device": {"type": str, "required": False},
                            "Device ID": {"type": str, "required": False, "pattern": self.PATTERNS["device_id"]},
                            "Subsystem ID": {"type": str, "required": False, "pattern": self.PATTERNS["hex_id"]},
                            "PCI Path": {"type": str, "required": False, "pattern": self.PATTERNS["pci_path"]},
                            "ACPI Path": {"type": str, "required": False, "pattern": self.PATTERNS["acpi_path"]}
                        }
                    }
                }
            }
        }
    
    def validate_report(self, report_path):
        self.errors = []
        self.warnings = []
        data = None
        
        if not os.path.exists(report_path):
            self.errors.append("File does not exist: {}".format(report_path))
            return False, self.errors, self.warnings, None
            
        try:
            data = self.u.read_file(report_path)
        except json.JSONDecodeError as e:
            self.errors.append("Invalid JSON format: {}".format(str(e)))
            return False, self.errors, self.warnings, None
        except Exception as e:
            self.errors.append("Error reading file: {}".format(str(e)))
            return False, self.errors, self.warnings, None
            
        cleaned_data = self._validate_node(data, self.SCHEMA, "Root")
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings, cleaned_data
    
    def _validate_node(self, data, rule, path):
        expected_type = rule.get("type")
        if expected_type:
            if not isinstance(data, expected_type):
                type_name = expected_type.__name__ if hasattr(expected_type, "__name__") else str(expected_type)
                self.errors.append(f"{path}: Expected type {type_name}, got {type(data).__name__}")
                return None

        if isinstance(data, str):
            pattern = rule.get("pattern")
            if pattern is not None:
                if not re.match(pattern, data):
                    self.errors.append(f"{path}: Value '{data}' does not match pattern '{pattern}'")
                    return None
            elif not re.match(self.PATTERNS["not_empty"], data):
                 self.errors.append(f"{path}: Value '{data}' does not match pattern '{self.PATTERNS['not_empty']}'")
                 return None

        cleaned_data = data

        if isinstance(data, dict):
            cleaned_data = {}
            schema_keys = rule.get("schema", {})
            
            for key, value in data.items():
                if key in schema_keys:
                    cleaned_val = self._validate_node(value, schema_keys[key], f"{path}.{key}")
                    if cleaned_val is not None:
                        cleaned_data[key] = cleaned_val
                elif "values_rule" in rule:
                    cleaned_val = self._validate_node(value, rule["values_rule"], f"{path}.{key}")
                    if cleaned_val is not None:
                        cleaned_data[key] = cleaned_val
                else:
                    if schema_keys:
                        self.warnings.append(f"{path}: Unknown key '{key}'")
            
            for key, key_rule in schema_keys.items():
                if key_rule.get("required", True) and key not in cleaned_data:
                    self.errors.append(f"{path}: Missing required key '{key}'")

        elif isinstance(data, list):
            item_rule = rule.get("item_rule")
            if item_rule:
                cleaned_data = []
                for i, item in enumerate(data):
                    cleaned_val = self._validate_node(item, item_rule, f"{path}[{i}]")
                    if cleaned_val is not None:
                        cleaned_data.append(cleaned_val)
            else:
                cleaned_data = list(data)

        return cleaned_data

    def show_validation_report(self, report_path, is_valid, errors, warnings):
        self.u.head("Validation Report")
        print("")
        print("Validation report for: {}".format(report_path))
        print("")

        if is_valid:
            print("Hardware report is valid!")
        else:
            print("Hardware report is not valid! Please check the errors and warnings below.")
        
        if errors:
            print("")
            print("\033[31mErrors ({}):\033[0m".format(len(errors)))
            for i, error in enumerate(errors, 1):
                print("    {}. {}".format(i, error))
        
        if warnings:
            print("")
            print("\033[33mWarnings ({}):\033[0m".format(len(warnings)))
            for i, warning in enumerate(warnings, 1):
                print("    {}. {}".format(i, warning))