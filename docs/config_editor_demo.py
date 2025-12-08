#!/usr/bin/env python3
"""
Demo script showing the config editor functionality
This demonstrates the tree population and basic operations without GUI
"""

import plistlib
import os
from collections import OrderedDict

# Simulate the tree operations
class SimpleTreeNode:
    def __init__(self, key="", value_type="", value=""):
        self.key = key
        self.value_type = value_type
        self.value = value
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
    
    def print_tree(self, indent=0):
        prefix = "  " * indent
        if self.key:
            print(f"{prefix}{self.key} [{self.value_type}]: {self.value}")
        for child in self.children:
            child.print_tree(indent + 1)

def populate_tree(data, parent=None):
    """Simulate tree population"""
    if parent is None:
        parent = SimpleTreeNode("Root", "Dictionary", "")
    
    if isinstance(data, dict):
        for key, value in data.items():
            node = SimpleTreeNode(key, "", "")
            set_node_value(node, value)
            parent.add_child(node)
            
            if isinstance(value, (dict, list)):
                populate_tree(value, node)
    
    elif isinstance(data, list):
        for i, value in enumerate(data):
            node = SimpleTreeNode(f"Item {i}", "", "")
            set_node_value(node, value)
            parent.add_child(node)
            
            if isinstance(value, (dict, list)):
                populate_tree(value, node)
    
    return parent

def set_node_value(node, value):
    """Set node type and value"""
    if isinstance(value, bool):
        node.value_type = "Boolean"
        node.value = "true" if value else "false"
    elif isinstance(value, int):
        node.value_type = "Number"
        node.value = str(value)
    elif isinstance(value, str):
        node.value_type = "String"
        node.value = value
    elif isinstance(value, bytes):
        node.value_type = "Data"
        node.value = value.hex()[:20] + "..." if len(value) > 10 else value.hex()
    elif isinstance(value, dict):
        node.value_type = "Dictionary"
        node.value = f"{len(value)} items"
    elif isinstance(value, list):
        node.value_type = "Array"
        node.value = f"{len(value)} items"

# Demo config.plist structure
demo_config = OrderedDict([
    ("ACPI", OrderedDict([
        ("Add", [
            OrderedDict([
                ("Comment", "SSDT-EC"),
                ("Enabled", True),
                ("Path", "SSDT-EC.aml")
            ]),
            OrderedDict([
                ("Comment", "SSDT-PLUG"),
                ("Enabled", True),
                ("Path", "SSDT-PLUG.aml")
            ])
        ])
    ])),
    ("Kernel", OrderedDict([
        ("Add", [
            OrderedDict([
                ("BundlePath", "Lilu.kext"),
                ("Comment", "Lilu.kext"),
                ("Enabled", True),
                ("ExecutablePath", "Contents/MacOS/Lilu"),
                ("PlistPath", "Contents/Info.plist")
            ]),
            OrderedDict([
                ("BundlePath", "VirtualSMC.kext"),
                ("Comment", "VirtualSMC.kext"),
                ("Enabled", True),
                ("ExecutablePath", "Contents/MacOS/VirtualSMC"),
                ("PlistPath", "Contents/Info.plist")
            ])
        ])
    ])),
    ("Misc", OrderedDict([
        ("Boot", OrderedDict([
            ("HideAuxiliary", False),
            ("Timeout", 5)
        ]))
    ]))
])

print("=" * 70)
print("Config.plist Editor - Demo")
print("=" * 70)
print()

print("1. Tree Population Demo")
print("-" * 70)
tree = populate_tree(demo_config)
tree.print_tree()
print()

print("2. Validation Demo")
print("-" * 70)

# Check path lengths
def check_path_length(path, max_len=128):
    return len(path) <= max_len

acpi_paths = [entry["Path"] for entry in demo_config["ACPI"]["Add"]]
print(f"ACPI Paths: {len(acpi_paths)}")
for path in acpi_paths:
    status = "✓" if check_path_length(path) else "✗"
    print(f"  {status} {path} ({len(path)} chars)")

kext_paths = [entry["BundlePath"] for entry in demo_config["Kernel"]["Add"]]
print(f"\nKext Paths: {len(kext_paths)}")
for path in kext_paths:
    status = "✓" if check_path_length(path) else "✗"
    print(f"  {status} {path} ({len(path)} chars)")

# Check for duplicates
print(f"\nDuplicate Check:")
if len(acpi_paths) == len(set(acpi_paths)):
    print("  ✓ No duplicate ACPI paths")
else:
    print("  ✗ Duplicate ACPI paths found")

if len(kext_paths) == len(set(kext_paths)):
    print("  ✓ No duplicate Kext paths")
else:
    print("  ✗ Duplicate Kext paths found")

# Check kext order
print(f"\nKext Load Order Check:")
if kext_paths[0] == "Lilu.kext":
    print("  ✓ Lilu.kext is loaded first (correct)")
else:
    print("  ⚠ Lilu.kext should be loaded before its dependencies")

print()
print("3. OC Snapshot Simulation")
print("-" * 70)

# Simulate finding new files
new_acpi_files = ["SSDT-AWAC.aml", "SSDT-USB.aml"]
new_kexts = ["WhateverGreen.kext", "AppleALC.kext"]

print(f"Found {len(new_acpi_files)} new ACPI files:")
for f in new_acpi_files:
    print(f"  + {f}")

print(f"\nFound {len(new_kexts)} new Kexts:")
for k in new_kexts:
    print(f"  + {k}")

print("\nAfter OC Snapshot, these would be added to config.plist")
print()

print("=" * 70)
print("Demo Complete!")
print()
print("The actual GUI provides:")
print("  • Interactive TreeView for browsing/editing")
print("  • Double-click to edit values")
print("  • OC Snapshot with folder selection")
print("  • Comprehensive validation with detailed reports")
print("  • Save/Load functionality")
print("=" * 70)
