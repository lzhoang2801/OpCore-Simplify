# GUI Migration - Moving CLI Logic to GUI

## Overview

This document describes the changes made to move interactive CLI prompts to the GUI interface, eliminating the need for terminal interaction after uploading the hardware report and ACPI tables.

## Changes Made

### 1. Core Infrastructure (`Scripts/utils.py`)

#### Added GUI Callback Support
- Added `gui_callback` attribute to the `Utils` class
- Modified `request_input()` method to support three interaction modes:
  - **CLI mode**: Traditional command-line input (default when no GUI callback is set)
  - **GUI mode**: Interactive dialogs when GUI callback is available
  - **Hybrid mode**: Automatically chooses based on callback availability

```python
def request_input(self, prompt="Press Enter to continue...", gui_type=None, gui_options=None):
    """
    Request input from user, using GUI callback if available.
    
    Args:
        prompt: The prompt text
        gui_type: Type of GUI dialog ('choice', 'confirm', 'info')
        gui_options: Additional options for GUI dialog (title, choices, warnings, etc.)
    
    Returns:
        User's response as string
    """
```

### 2. GUI Handler (`Scripts/gui/main.py`)

#### Implemented Comprehensive Dialog System
Added `handle_gui_prompt()` method that handles three types of dialogs:

1. **Info Dialogs** (`gui_type='info'`)
   - Simple information messages
   - Used for "Press Enter to continue" prompts
   - Shows as `messagebox.showinfo()`

2. **Confirmation Dialogs** (`gui_type='confirm'`)
   - Yes/No questions
   - Used for firmware type selection, OCLP patches, kext compatibility warnings
   - Shows as `messagebox.askyesno()`
   - Supports warning messages

3. **Choice Dialogs** (`gui_type='choice'`)
   - Multiple choice selections
   - Used for WiFi kext selection, audio kext selection, GPU kext selection
   - Custom scrollable dialog with radio buttons
   - Supports:
     - Rich descriptions for each choice
     - Warning banners
     - Info notes
     - Default selections

#### Dialog Features
- Modern, clean UI design matching the application style
- Color-coded warnings (yellow) and notes (blue)
- Scrollable content for long lists
- Keyboard-friendly navigation
- Modal dialogs that block interaction with parent window
- Thread-safe execution on GUI main thread

### 3. Kext Maestro (`Scripts/kext_maestro.py`)

#### WiFi Kext Selection
Converted Intel WiFi kext selection (AirportItlwm vs itlwm) to GUI dialog:
- Two clearly labeled options with descriptions
- Shows compatibility notes for different macOS versions
- Automatic selection for Beta/Tahoe versions
- Default recommendation based on macOS version

#### Audio Kext Selection (macOS Tahoe 26+)
Converted audio kext selection (AppleALC vs VoodooHDA) to GUI dialog:
- Explains AppleHDA removal in macOS Tahoe 26
- Shows OCLP requirement for AppleALC
- Warning about VoodooHDA quality

#### AMD GPU Kext Selection
Converted AMD GPU kext selection (NootRX vs WhateverGreen) to GUI dialog:
- Options depend on macOS version
- Shows black screen fix warning
- Explains firmware differences
- Automatic selection when Intel GPU present

#### iServices OCLP Patch
Converted iServices patch prompt to GUI dialog:
- Yes/No confirmation
- Explains impact on iServices
- Only shown for AirportItlwm + macOS Sonoma 14

#### Kext Compatibility Check
Converted incompatible kext warning to GUI dialog:
- Lists all incompatible kexts
- Shows which are Lilu plugins
- Explains force-load risks
- Warning about system instability

### 4. Hardware Customizer (`Scripts/hardware_customizer.py`)

#### UEFI Firmware Type Selection
Converted BIOS firmware type selection to GUI dialog:
- Prompts when Legacy BIOS detected
- Explains UEFI requirement
- Reminds user to update BIOS settings
- Yes/No confirmation

#### Device Selection Summary
Converted "Press Enter to continue" to GUI info dialog:
- Shows selected devices
- Displays disabled devices
- No longer requires terminal interaction

### 5. Compatibility Checker (`Scripts/compatibility_checker.py`)

#### Error Messages
Converted all error exit prompts to GUI info dialogs:
- Missing SSE4.x instruction set error
- No GPU found error
- No storage controller found error
- Intel VMD controller error
- No compatible storage controller error

All error messages now show as GUI dialogs before exiting the program.

## Usage

### For Users
When running in GUI mode, all interactive prompts now appear as native dialog boxes:
- No need to switch between GUI and terminal
- All configuration happens within the application window
- Better visual presentation of options
- Easier to understand choices with descriptions

### For Developers
To add new GUI-compatible prompts:

1. **Info Dialog** (Press Enter to continue):
```python
self.utils.request_input(
    "Your message here",
    gui_type='info'
)
```

2. **Confirmation Dialog** (Yes/No):
```python
gui_options = {
    'title': 'Dialog Title',
    'message': 'Your question here',
    'default': 'yes',  # or 'no'
    'warning': 'Optional warning text'
}
response = self.utils.request_input(
    "Prompt text",
    gui_type='confirm',
    gui_options=gui_options
)
# response will be 'yes' or 'no'
```

3. **Choice Dialog** (Multiple options):
```python
gui_options = {
    'title': 'Select Option',
    'message': 'Choose one of the following:',
    'choices': [
        {
            'value': '1',
            'label': 'Option 1 Label',
            'description': 'Detailed description of option 1'
        },
        {
            'value': '2',
            'label': 'Option 2 Label',
            'description': 'Detailed description of option 2'
        }
    ],
    'default': '1',
    'warning': 'Optional warning text',
    'note': 'Optional informational note'
}
response = self.utils.request_input(
    "Select your option: ",
    gui_type='choice',
    gui_options=gui_options
)
# response will be the 'value' of selected choice
```

## Testing

### Manual Testing Scenarios

1. **WiFi Kext Selection**
   - Load hardware report with Intel WiFi
   - Verify GUI dialog appears with two options
   - Test selection and cancellation
   - Verify automatic selection for Tahoe 26

2. **Audio Kext Selection**
   - Test with macOS Tahoe 26 version
   - Verify AppleALC vs VoodooHDA dialog
   - Check OCLP warning is shown

3. **AMD GPU Kext Selection**
   - Test with Navi 21/23 GPU
   - Verify NootRX vs WhateverGreen options
   - Check black screen warning is displayed

4. **Kext Compatibility**
   - Select incompatible macOS version
   - Verify warning dialog with kext list
   - Test force-load option

5. **Firmware Type**
   - Load report with Legacy BIOS
   - Verify UEFI selection dialog
   - Test both Yes and No options

### CLI Mode Testing
All changes are backward compatible:
- Running with `--cli` flag uses traditional prompts
- No GUI callback means CLI mode is used
- Existing CLI behavior is preserved

## Benefits

1. **Better User Experience**
   - Single-window workflow
   - No terminal switching required
   - Visual feedback and progress
   - Consistent interface throughout

2. **Improved Clarity**
   - Rich text formatting in dialogs
   - Color-coded warnings and notes
   - Detailed option descriptions
   - Better organization of information

3. **Easier Maintenance**
   - Centralized dialog logic
   - Reusable dialog types
   - Consistent styling
   - Easier to add new prompts

4. **Cross-Platform**
   - Works on Windows, macOS, and Linux
   - Native dialog appearance
   - Proper modal behavior
   - Keyboard navigation support

## Migration Status

### ✅ Completed
- WiFi kext selection (AirportItlwm vs itlwm)
- Audio kext selection (AppleALC vs VoodooHDA)
- AMD GPU kext selection (NootRX vs WhateverGreen)
- iServices OCLP patch confirmation
- Kext compatibility warnings
- UEFI firmware type selection
- All "Press Enter to continue" prompts
- Error message dialogs

### 🔄 Future Enhancements
- Device selection (GPU/WiFi/Bluetooth when multiple found)
- ACPI patch customization
- Kext configuration menu
- SMBIOS customization

## Backward Compatibility

All changes maintain full backward compatibility:
- CLI mode still works with `--cli` flag
- GUI callback is optional
- Default behavior unchanged when no callback set
- Existing scripts and automation unaffected

## Technical Details

### Thread Safety
- GUI dialogs execute on main thread using `root.after()`
- Blocking behavior implemented with event loop
- Result container pattern for thread communication

### Dialog Styling
- Matches application color scheme (COLORS)
- Uses application fonts (get_font)
- Consistent spacing (SPACING)
- Hover effects on buttons

### Error Handling
- Graceful fallback to CLI if GUI unavailable
- Invalid input handling in dialogs
- Default values for all prompts
- Cancel button support
