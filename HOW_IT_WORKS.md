# How OpCore-Simplify Works

## Overview

OpCore-Simplify is an intelligent automation tool that builds OpenCore EFI configurations for Hackintosh systems. Unlike other tools that use predefined templates, OpCore-Simplify analyzes your complete hardware configuration and creates a custom EFI tailored specifically to your system.

## Architecture

The tool is built with a modular architecture, where each module handles a specific aspect of the EFI building process:

```
OpCore-Simplify.py (Main Entry Point)
    ├── Hardware Analysis
    │   ├── Hardware Sniffer Integration
    │   ├── Compatibility Checker
    │   └── Hardware Customizer
    ├── ACPI Management
    │   ├── ACPI Guru (SSDT Generation)
    │   └── DSDT Parser
    ├── Kext Management
    │   └── Kext Maestro
    ├── Configuration Generation
    │   ├── Config Prodigy
    │   └── SMBIOS Selector
    └── File Assembly
        └── Gathering Files
```

## Core Workflow

### 1. Hardware Detection and Analysis

**Module:** `hardware_customizer.py`, `compatibility_checker.py`

The process begins by gathering comprehensive hardware information:

#### Hardware Report Generation
- **Windows**: Uses Hardware Sniffer to export a complete hardware report including:
  - CPU specifications (model, generation, features)
  - GPU details (vendor, device ID, compatibility)
  - Motherboard information (chipset, platform)
  - Storage controllers, network adapters, audio codecs
  - BIOS/UEFI settings (Secure Boot, Resizable BAR)
  - ACPI tables (DSDT, SSDTs)

- **Manual Import**: Users can provide a pre-generated `Report.json` from Hardware Sniffer

#### Compatibility Analysis
The `CompatibilityChecker` evaluates each hardware component against macOS compatibility databases:
- Checks CPU features (SSE4.1/4.2 support)
- Verifies GPU compatibility across macOS versions
- Identifies network adapters and their driver support
- Determines audio codec compatibility
- Assesses storage controller support

**Output**: A compatibility matrix showing which macOS versions are supported by your hardware.

### 2. macOS Version Selection

**Module:** `OpCore-Simplify.py` (`select_macos_version`)

Based on hardware compatibility:
1. Suggests the latest compatible macOS version
2. Identifies if OpenCore Legacy Patcher (OCLP) is needed for newer versions
3. Allows users to select from available versions
4. Validates the selection against hardware constraints

**Decision Tree:**
- If GPU requires OCLP → Suggests latest OCLP-supported version
- If older hardware → Suggests highest natively supported version
- If modern hardware → Suggests latest macOS release

### 3. Hardware Customization

**Module:** `hardware_customizer.py`

Allows fine-tuning of hardware configuration:
- **GPU Selection**: Choose primary GPU (for multi-GPU systems)
- **iGPU Configuration**: Headless mode vs. display output
- **Device Disabling**: Disable unsupported devices (e.g., NVIDIA GPUs in modern macOS)
- **Firmware Type**: UEFI vs. Legacy boot mode
- **Network Configuration**: Select active network adapters
- **Storage Setup**: Choose boot drive controller

### 4. ACPI Patch Generation

**Module:** `acpi_guru.py`

OpCore-Simplify integrates with SSDTTime and includes custom ACPI patching:

#### Automatic SSDT Generation
- **SSDT-PLUG**: CPU power management
- **SSDT-EC**: Fake embedded controller (required for macOS)
- **SSDT-AWAC**: System clock fixes
- **SSDT-RTC0**: Real-time clock for HEDT systems
- **SSDT-PMC**: Power management controller
- **SSDT-PNLF**: Backlight control for laptops

#### Custom ACPI Patches
- **Device Disabling**: Disables unsupported PCI devices (GPU, Wi-Fi, NVMe)
- **Sleep Fix**: Patches _PRW methods to prevent instant wake
- **CPU Core Routing**: Directs operations to active CPUs on HEDT platforms
- **Device Addition**: Adds missing devices (ALS0, MCHC, PMCR, IMEI, etc.)
- **GPIO/ALSD Enabling**: Enables devices required for proper operation

**Process:**
1. Parses DSDT from ACPI tables
2. Identifies devices and their ACPI paths
3. Generates appropriate SSDT patches
4. Compiles AML files using iasl (Intel ACPI compiler)
5. Places compiled files in `EFI/OC/ACPI/`

### 5. Kext Selection and Management

**Module:** `kext_maestro.py`

Intelligent kext selection based on hardware:

#### Required Kexts (Always Included)
- **Lilu.kext**: Patching framework (foundation for many other kexts)
- **VirtualSMC.kext**: SMC emulator (required for macOS to boot)
- **WhateverGreen.kext**: GPU patching and fixes

#### Hardware-Specific Kexts
Based on detected hardware:

**CPU:**
- `CpuTscSync.kext` - TSC synchronization for multi-socket systems
- `CpuTopologyRebuild.kext` - For Intel 12th gen+ with P/E cores
- `SMCAMDProcessor.kext` - AMD CPU power management
- `AMDRyzenCPUPowerManagement.kext` - Enhanced AMD power management

**GPU:**
- `WEG (WhateverGreen)` - Intel iGPU and AMD GPU patches
- `NootedRed.kext` - AMD APU support
- `RadeonSensor.kext` - AMD GPU monitoring

**Network:**
- `IntelMausi.kext` - Intel ethernet (I217, I218, I219)
- `AtherosE2200Ethernet.kext` - Atheros ethernet
- `RealtekRTL8111.kext` - Realtek ethernet
- `itlwm.kext` - Intel Wi-Fi
- `AirportItlwm.kext` - Intel Wi-Fi with native experience
- `AirportBrcmFixup.kext` - Broadcom Wi-Fi fixes

**Audio:**
- `AppleALC.kext` - Audio codec patching (with layout-id selection)
- `VoodooHDA.kext` - Alternative audio driver

**USB:**
- `USBToolBox.kext` + `UTBMap.kext` - USB port mapping (requires post-install mapping)

**Input:**
- `VoodooPS2Controller.kext` - PS/2 keyboard/trackpad
- `VoodooI2C.kext` - I2C trackpad support
- `VoodooInput.kext` - Input stack for trackpads

**Storage:**
- `NVMeFix.kext` - NVMe power management fixes

#### Kext Matching Algorithm
1. Scans kext Info.plist for IOKit matching keys
2. Extracts PCI IDs, vendor IDs, device IDs
3. Matches against detected hardware PCI IDs
4. Automatically enables matched kexts
5. Allows manual override in customization menu

### 6. SMBIOS Configuration

**Module:** `smbios.py`, `mac_model_data.py`

Selects the most appropriate Mac model identifier:

#### Selection Criteria
1. **CPU Generation Match**: Aligns with your Intel/AMD CPU generation
2. **GPU Configuration**: iGPU-only, dGPU-only, or iGPU+dGPU
3. **Platform Type**: Desktop (iMac, Mac Pro) vs. Laptop (MacBook Pro, MacBook Air)
4. **Form Factor**: Mini-ITX (Mac mini), Standard ATX (iMac), HEDT (iMac Pro, Mac Pro)
5. **macOS Version Support**: Ensures SMBIOS is supported in target macOS version

#### Common SMBIOS Models
- **iMac19,1**: Coffee Lake desktop with iGPU+dGPU
- **iMac20,1**: Comet Lake desktop with iGPU+dGPU
- **MacBookPro16,1**: Coffee Lake laptop with dGPU
- **MacPro7,1**: Cascade Lake-X HEDT (X299 chipset)
- **iMacPro1,1**: Skylake-X/Cascade Lake-X HEDT

#### Generated Serial Info
- **SystemSerialNumber**: Generated using Mac model prefix + random numbers
- **MLB (Board Serial)**: Motherboard serial number
- **SystemUUID**: Unique identifier for the system
- **ROM**: MAC address-based identifier

**Note**: Generic serials are generated - users should generate valid serials for iServices.

### 7. Config.plist Generation

**Module:** `config_prodigy.py`

Creates the comprehensive OpenCore configuration file:

#### Booter Section
- **Quirks**: System-specific boot quirks
  - `DevirtualiseMmio`: Required for some systems
  - `EnableWriteUnprotector`: For older systems
  - `ProtectUefiServices`: Modern firmware protection
  - `RebuildAppleMemoryMap`: Memory map fixes
  - `ResizeAppleGpuBars`: Resizable BAR configuration (if detected)
  - `SyncRuntimePermissions`: Runtime permissions fixes

#### Kernel Section
- **Add**: List of kexts to load
- **Emulate**: CPU ID spoofing for unsupported CPUs
- **Patch**: Kernel patches
  - AMD kernel patches (for AMD CPUs)
  - Aquantia NIC patches
  - CPU topology patches for P/E cores
  - `AppleXcpmCfgLock` patches
  - `IOPlatformPluginFamily` patches for legacy CPUs
- **Quirks**:
  - `AppleXcpmExtraMsrs`: For Pentium/Celeron
  - `DisableIoMapper`: Disables VT-d
  - `PanicNoKextDump`: Prevents kext dumps on panic
  - `PowerTimeoutKernelPanic`: Disables power timeout panics

#### DeviceProperties Section
- **PciRoot devices**: Device-specific properties
  - **iGPU**: Framebuffer patches, connector types, device-id spoofing
  - **dGPU**: Device-id spoofing for AMD GPUs
  - **Audio**: layout-id for AppleALC
  - **Ethernet**: Built-in property for iServices
  - **Storage**: Built-in property to show as internal

#### NVRAM Section
- **7C436110-AB2A-4BBB-A880-FE41995C9F82** (Boot args):
  - `-v`: Verbose mode
  - `debug=0x100`: Debug logging
  - `keepsyms=1`: Keep kernel symbols
  - `-igfxvesa`: Force iGPU to VESA mode (during install)
  - `-radvesa`: Force AMD GPU to VESA mode (during install)
  - `alcid=X`: Audio layout ID
- **4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14** (UI Scale):
  - `UIScale`: HiDPI configuration
- **4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102** (OpenCore variables):
  - `rtc-blacklist`: Blacklisted RTC regions

#### PlatformInfo Section
- **Generic**: SMBIOS information
  - `SystemProductName`: Mac model (e.g., iMac19,1)
  - `SystemSerialNumber`, `MLB`, `SystemUUID`, `ROM`
- **UpdateDataHub**, **UpdateNVRAM**, **UpdateSMBIOS**: Set to True

#### UEFI Section
- **Drivers**: Required UEFI drivers
  - `OpenRuntime.efi`: OpenCore runtime
  - `OpenCanopy.efi`: GUI boot picker
  - `HfsPlus.efi`: HFS+ filesystem driver
  - `ResetNvramEntry.efi`: NVRAM reset tool
- **Quirks**: UEFI-specific quirks
  - `EnableVectorAcceleration`: Vector acceleration
  - `UnblockFsConnect`: Filesystem connection fixes

### 8. Resource Gathering

**Module:** `gathering_files.py`, `github.py`, `resource_fetcher.py`

Downloads and organizes all required files:

#### Bootloader Download
- Fetches latest OpenCorePkg from Dortania builds or GitHub releases
- Extracts base EFI structure
- Copies to build directory

#### Kext Download
- Queries Dortania builds database for latest kext versions
- Downloads directly from GitHub releases for non-Dortania kexts
- Verifies kext integrity
- Extracts to temporary directory

#### Additional Resources
- **OcBinaryData**: OpenCore themes and resources
- **AMD Vanilla Patches**: Kernel patches for AMD CPUs
- **Aquantia Patches**: Network patches for Aquantia NICs
- **HyperThreading Patches**: CPU topology patches

#### Update Mechanism
- Checks `history.json` for previously downloaded versions
- Only downloads if new version is available
- Caches downloads in `OCK_Files/` directory

### 9. EFI Assembly

**Module:** `gathering_files.py` (build process)

Final EFI structure assembly:

```
EFI/
├── BOOT/
│   └── BOOTx64.efi
└── OC/
    ├── ACPI/
    │   ├── SSDT-PLUG.aml
    │   ├── SSDT-EC.aml
    │   └── [Other SSDTs]
    ├── Drivers/
    │   ├── OpenRuntime.efi
    │   ├── OpenCanopy.efi
    │   └── HfsPlus.efi
    ├── Kexts/
    │   ├── Lilu.kext
    │   ├── VirtualSMC.kext
    │   ├── WhateverGreen.kext
    │   └── [Hardware-specific kexts]
    ├── Resources/
    │   ├── Image/ (Boot picker themes)
    │   └── Font/ (Boot picker fonts)
    ├── Tools/
    │   ├── OpenShell.efi
    │   └── [Other tools]
    ├── OpenCore.efi
    └── config.plist
```

**Assembly Process:**
1. Creates result directory structure
2. Copies base OpenCore files
3. Copies generated ACPI files to `ACPI/`
4. Copies selected kexts to `Kexts/`
5. Writes generated `config.plist`
6. Removes unused drivers, resources, and tools
7. Validates file structure

### 10. Post-Build Configuration

**Module:** `OpCore-Simplify.py` (`before_using_efi`)

Provides user guidance for final steps:

#### BIOS/UEFI Settings Check
Analyzes hardware report and suggests required BIOS changes:
- Enable UEFI mode (disable CSM)
- Disable Secure Boot
- Enable Above 4G Decoding (for modern systems)
- Disable Resizable BAR (unless properly configured)

#### USB Mapping Reminder
- Directs users to use USBToolBox for USB port mapping
- Explains how to add UTBMap.kext
- Instructions for removing default UTBDefault.kext
- Reminds to snapshot config.plist after USB mapping

#### Result Presentation
- Opens the built EFI folder for user inspection
- Displays full path to built EFI
- Ready for installation to USB or EFI partition

## Key Algorithms

### Hardware Matching Algorithm

```python
# Pseudocode representation of kext matching logic
for detected_device in hardware_report:
    for kext in kext_database:
        if detected_device.pci_id in kext.pci_ids:
            enable_kext(kext)
        if kext.vendor_id == detected_device.vendor_id:
            if kext.device_id == detected_device.device_id:
                enable_kext(kext)
```

### Compatibility Scoring

```python
# Pseudocode representation of compatibility scoring logic
NATIVE_SUPPORT = "native"
REQUIRES_OCLP = "oclp"
UNSUPPORTED = "unsupported"

compatibility_score = 0
for device in hardware_report:
    device_compat = check_device_compatibility(device, macos_version)
    if device_compat == NATIVE_SUPPORT:
        compatibility_score += 100
    elif device_compat == REQUIRES_OCLP:
        compatibility_score += 50
    elif device_compat == UNSUPPORTED:
        compatibility_score += 0

if compatibility_score > threshold:
    # Suggest native installation
    suggest_installation_type("native")
else:
    # Suggest OCLP installation or lower macOS version
    suggest_installation_type("oclp_or_lower_version")
```

### ACPI Patch Priority

```python
patch_priority = {
    "Essential": ["PLUG", "EC", "AWAC"],  # Applied first
    "System-Specific": ["RTCAWAC", "PMC"],  # Applied second
    "Optional": ["PNLF", "XOSI", "GPRW"],  # Applied last
}
```

## Data Sources

### Hardware Databases

**CPU Data** (`cpu_data.py`):
- Intel CPU generations (Nehalem → Arrow Lake)
- AMD CPU families (Ryzen, Threadripper)
- CPU features (SSE, AVX support)

**GPU Data** (`gpu_data.py`):
- Intel iGPU device IDs and generations
- AMD GPU device IDs and codenames
- NVIDIA GPU device IDs (for legacy support)

**Chipset Data** (`chipset_data.py`):
- Intel chipsets and their generations
- AMD chipsets (AM4, AM5, TRX40)
- Platform detection (Desktop, Mobile, HEDT)

**PCI Data** (`pci_data.py`):
- PCI vendor IDs
- PCI device IDs for various device classes
- Device class codes

### macOS Databases

**OS Data** (`os_data.py`):
- macOS version names and Darwin versions
- Version release dates
- Version support status

**Mac Model Data** (`mac_model_data.py`):
- SMBIOS model identifiers
- Model introduction/discontinuation dates
- Hardware specifications per model
- Compatible macOS versions

### Kext Database

**Kext Data** (`kext_data.py`):
- Kext names and bundle identifiers
- Download sources (Dortania/GitHub)
- PCI ID matching data
- macOS version compatibility
- Dependency information

## Error Handling

The tool includes comprehensive error handling:

1. **File Validation**: Checks for valid JSON hardware reports
2. **ACPI Validation**: Verifies DSDT parsing success
3. **Download Verification**: Validates downloaded files
4. **Path Validation**: Ensures all required paths exist
5. **Configuration Validation**: Checks config.plist structure
6. **Graceful Failures**: Allows continuation on non-critical errors

## Performance Optimizations

- **Caching**: Downloaded kexts and bootloaders are cached
- **Incremental Updates**: Only downloads new versions when available
- **Parallel Processing**: Where possible, operations run concurrently
- **Lazy Loading**: Modules are loaded only when needed

## Security Considerations

1. **No Telemetry**: Tool doesn't send any data externally
2. **Local Processing**: All operations are performed locally
3. **Verified Downloads**: Downloads are from official sources (GitHub, Dortania)
4. **No Credential Storage**: Tool doesn't store any credentials
5. **Serial Generation**: Generic serials prevent iServices conflicts

## Extensibility

The modular design allows for easy extensions:

- **Adding New Kexts**: Update `kext_data.py`
- **Supporting New Hardware**: Update `pci_data.py`, `gpu_data.py`, `cpu_data.py`
- **New macOS Versions**: Update `os_data.py`
- **Custom ACPI Patches**: Extend `acpi_guru.py`
- **New SMBIOS Models**: Update `mac_model_data.py`

## Comparison with Other Tools

| Feature | OpCore-Simplify | Other Tools |
|---------|----------------|-------------|
| Hardware Analysis | Complete system scan | Template-based |
| ACPI Generation | Dynamic based on DSDT | Predefined SSDTs |
| Kext Selection | Automatic matching | Manual selection |
| SMBIOS Selection | Intelligent matching | User choice |
| Customization | Extensive options | Limited options |
| Update Mechanism | Automatic | Manual |

## Future Enhancements

Potential areas for improvement:

1. **GUI Interface**: Graphical interface for easier use
2. **Profile Management**: Save and load configurations
3. **Advanced Diagnostics**: Boot log analysis
4. **Cloud Sync**: Optional configuration backup
5. **Community Database**: Share successful configurations

## Conclusion

OpCore-Simplify works by:
1. Analyzing your complete hardware configuration
2. Determining macOS compatibility for each component
3. Generating custom ACPI patches specific to your hardware
4. Selecting and configuring appropriate kexts
5. Choosing the optimal SMBIOS model
6. Creating a tailored config.plist
7. Assembling all components into a ready-to-use EFI

This approach ensures maximum compatibility and performance for your specific hardware configuration, while maintaining the flexibility to customize as needed.
