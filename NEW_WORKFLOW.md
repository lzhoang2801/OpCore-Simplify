# OpCore Simplify - New GUI Workflow

## Overview

The GUI has been completely reorganized into a **clear, chronological 4-step workflow** that eliminates the need for CLI interaction and provides an intuitive user experience.

## The New 4-Step Workflow

### Step 1: Upload Report
**File**: `Scripts/gui/pages/upload_page.py`

**Purpose**: Upload hardware report and ACPI tables

**Features**:
- Two upload methods:
  1. **Select Existing Report** (Primary) - Choose a previously exported Report.json
  2. **Export New Report** (Windows only) - Use Hardware Sniffer to scan the current system

- Real-time status indicator showing:
  - ⏳ Waiting state
  - ⏳ Loading/processing state  
  - ✅ Success state

- Comprehensive instructions card explaining:
  - How to get a hardware report
  - Platform-specific instructions (Windows vs macOS/Linux)
  - What happens after upload

**What Happens Automatically After Upload**:
1. Hardware report validation
2. ACPI tables loaded automatically
3. Compatibility check runs automatically
4. Optimal macOS version is auto-selected
5. Required kexts are auto-configured
6. SMBIOS model is auto-selected
7. ACPI patches are auto-selected
8. User is automatically redirected to Compatibility page

### Step 2: Compatibility
**File**: `Scripts/gui/pages/compatibility_page.py`

**Purpose**: Review hardware compatibility results

**Features**:
- Displays compatibility checker results
- Shows supported macOS versions for each device
- Highlights any devices requiring OpenCore Legacy Patcher
- Clear visual indicators for:
  - ✅ Fully compatible devices
  - ⚠️ Limited compatibility
  - ❌ Unsupported devices

**Auto-Display**:
- This page automatically shows after Step 1 completes
- Results are populated from the automatic compatibility check
- No user interaction required unless reviewing details

### Step 3: Configuration  
**File**: `Scripts/gui/pages/configuration_page.py`

**Purpose**: Review and optionally customize auto-selected settings

**Features**:
- **Auto-Configuration Status Banner**:
  - ✅ Shows that automatic configuration is complete
  - Explains settings have been optimally configured

- **Current Configuration Display**:
  - 📋 Hardware Report (filename)
  - 🍎 macOS Version (auto-selected)
  - 💻 SMBIOS Model (auto-selected)
  - ⚠️ Disabled Devices (if any)

- **Customization Options** (Advanced Users):
  - Change macOS Version
  - Customize ACPI Patches
  - Customize Kernel Extensions
  - Change SMBIOS Model
  
- **User Guidance**:
  - 💡 Note explaining most users don't need to customize
  - Automatic configuration provides optimal compatibility

**Philosophy**:
- Configuration is done automatically
- This page is for review and optional tweaking
- Most users can skip customization entirely

### Step 4: Build EFI
**File**: `Scripts/gui/pages/build_page.py`

**Purpose**: Build the OpenCore EFI

**Features**:
- Large, prominent "Build OpenCore EFI" button
- Real-time progress bar during build
- Build log showing all steps
- Success message with next steps
- "Open EFI Folder" button after completion

**Build Process Shows**:
1. Copying EFI base to results folder
2. Applying ACPI patches
3. Copying kexts and snapshotting to config.plist
4. Generating config.plist
5. Cleaning up unused drivers, resources, and tools

## Navigation Structure

The sidebar now shows a clear numbered progression:

```
MAIN WORKFLOW
├── 1. Upload Report     📤
├── 2. Compatibility     🔍
├── 3. Configuration     ⚙
└── 4. Build EFI         🔨

TOOLS
├── WiFi Profiles        📡
└── Console Log          📋
```

## User Journey

### Happy Path (No Customization Needed)
1. User opens GUI → sees Step 1 (Upload Report)
2. User clicks "Select Existing Hardware Report" → chooses Report.json
3. **Automatic processing**:
   - Report loads
   - ACPI tables load
   - Compatibility check runs
   - Settings auto-configured
   - GUI shows Step 2 (Compatibility)
4. User reviews compatibility → clicks Step 3 (Configuration)
5. User sees ✅ "Automatic Configuration Complete" → clicks Step 4 (Build EFI)
6. User clicks "Build OpenCore EFI" → progress shows → build completes
7. User sees "Before Using EFI" instructions → clicks "Open EFI Folder"
8. ✅ Done!

### Advanced Path (With Customization)
1-4. Same as Happy Path
5. In Step 3 (Configuration), user customizes:
   - Clicks "Change macOS Version" → GUI dialog appears
   - Clicks "Customize Kexts" → Shows kext options
   - Makes selections via GUI dialogs (NO CLI!)
6-8. Same as Happy Path

## Key Improvements

### 1. Clear Workflow
- Numbered steps (1-4) show exact progress
- Each step has a clear purpose
- Linear progression is obvious

### 2. No CLI Required
- **All prompts now use GUI dialogs**:
  - WiFi kext selection (AirportItlwm vs itlwm)
  - Audio kext selection (AppleALC vs VoodooHDA)
  - AMD GPU kext selection (NootRX vs WhateverGreen)
  - Kext compatibility warnings
  - Firmware type selection
  - OCLP patch confirmations

- **Dialog Types Implemented**:
  - ℹ️ Info dialogs (Press Enter → GUI notification)
  - ✓/✗ Confirmation dialogs (Yes/No → GUI yes/no dialog)
  - 📋 Choice dialogs (Multiple options → GUI radio button dialog)

### 3. Automatic Configuration
- Everything is configured automatically after upload
- Users only customize if they want to
- "Smart defaults" approach reduces complexity

### 4. Better Visual Hierarchy
- Step indicators at top of each page
- Color-coded status indicators
- Card-based layout for grouped information
- Consistent spacing and typography

### 5. Contextual Help
- Instructions on every page
- Tooltips and descriptions for all options
- Warning/info banners where appropriate

## Technical Implementation

### Page Organization
```
Scripts/gui/pages/
├── upload_page.py          # Step 1: Upload
├── compatibility_page.py   # Step 2: Compatibility  
├── configuration_page.py   # Step 3: Configuration
├── build_page.py          # Step 4: Build
├── wifi_page.py           # Tool: WiFi profiles
└── console_page.py        # Tool: Console log
```

### Main GUI Controller
**File**: `Scripts/gui/main.py`

**Key Methods**:
- `load_hardware_report()` - Handles upload and triggers auto-configuration
- `handle_gui_prompt()` - Routes all CLI prompts to appropriate GUI dialogs
- `show_choice_dialog()` - Shows multi-option selection dialogs
- `auto_select_macos_version()` - Automatically selects optimal macOS version
- `apply_macos_version()` - Applies version and configures all settings

### Callback System
**Files**: `Scripts/utils.py`, `Scripts/kext_maestro.py`, `Scripts/hardware_customizer.py`

**How It Works**:
1. Backend code calls `self.utils.request_input()` with GUI parameters
2. If GUI callback is set, it routes to `handle_gui_prompt()`
3. Appropriate GUI dialog is shown
4. User's choice is returned to backend
5. Backend continues processing

**Backward Compatibility**:
- If no GUI callback is set → uses CLI input
- `--cli` flag still works for terminal users
- No breaking changes to existing code

## Benefits

### For End Users
- ✅ **No terminal switching** - everything in one window
- ✅ **Clear progress tracking** - always know what step you're on
- ✅ **Smart defaults** - works with minimal interaction
- ✅ **Visual feedback** - see what's happening in real-time
- ✅ **Contextual help** - guidance at every step

### For Developers
- ✅ **Consistent code patterns** - reusable dialog system
- ✅ **Easy to extend** - add new prompts via callback system
- ✅ **Maintainable** - clear separation of concerns
- ✅ **Well documented** - comments and docstrings throughout

## Future Enhancements

Potential improvements for future versions:

1. **Progress Persistence**
   - Save progress between sessions
   - Resume from last completed step

2. **Configuration Presets**
   - Save/load configuration profiles
   - Share configurations with others

3. **Built-in Tutorials**
   - Interactive walkthrough for first-time users
   - Video guides embedded in GUI

4. **Hardware Database**
   - Community-sourced compatibility data
   - Success rate statistics

5. **One-Click Updates**
   - Update OpenCore components in GUI
   - Automatic backup before updates

## Conclusion

The new 4-step workflow transforms OpCore Simplify from a CLI-heavy tool into a modern, user-friendly GUI application while maintaining all the power and flexibility of the original design.
