# OpCore Simplify GUI Guide

## Overview

OpCore Simplify now features a modern graphical user interface (GUI) that makes building OpenCore EFI configurations easier and more intuitive than ever before.

## Interface Layout

The GUI consists of four main tabs:

### 1. Configuration Tab (Main)

This is the primary interface where you'll spend most of your time.

**Current Configuration Display:**
- Hardware Report: Shows the path to your loaded hardware report
- macOS Version: Displays the selected macOS version
- SMBIOS Model: Shows the selected SMBIOS model
- Disabled Devices: Lists any hardware that will be disabled

**Action Buttons:**
- **Select Hardware Report**: Opens a file dialog to choose your hardware report JSON file
  - On Windows, offers to export directly using Hardware Sniffer
  - Validates the report automatically
  - Loads ACPI tables if available
  
- **Select macOS Version**: Opens a selection dialog showing:
  - All compatible macOS versions for your hardware
  - Highlights versions requiring OpenCore Legacy Patcher
  - Auto-suggests the best version for stability
  
- **Customize SMBIOS Model**: Lets you choose the appropriate Mac model
  - Shows compatible models based on your hardware
  - Automatically configures model-specific settings

**Instructions Panel:**
- Step-by-step guide for first-time users
- Quick reference for the build process
- Links to official documentation

### 2. Customization Tab

For advanced users who want to fine-tune their configuration.

**ACPI Patches:**
- Button to customize ACPI patches
- Most users can skip this (automatic detection works well)

**Kexts Configuration:**
- Button to customize kernel extensions
- Enable/disable specific kexts
- Force load kexts on unsupported macOS versions

**Information Panel:**
- Explains what each customization option does
- Warnings about when to use advanced features

### 3. Build EFI Tab

Where the magic happens!

**Build Button:**
- Large, prominent "Build OpenCore EFI" button
- Disabled until configuration is complete

**Progress Bar:**
- Shows real-time build progress (0-100%)
- Smooth animation during build process

**Build Log:**
- Scrollable text area showing all build steps
- Real-time updates as each step completes
- Error messages if something goes wrong

**Open Result Folder Button:**
- Appears after successful build
- Opens the folder containing your built EFI
- One-click access to your files

### 4. Console Log Tab

Technical information for troubleshooting.

**Console Output:**
- All system messages and debug information
- Downloadable/copyable for bug reports
- Automatically scrolls to latest messages

## Key Features

### User-Friendly Design

- **No Command Line Required**: Everything is point-and-click
- **Visual Feedback**: Progress bars, status messages, and dialog boxes
- **Error Prevention**: File dialogs prevent typing mistakes
- **Clear Instructions**: Every step is explained

### Smart Automation

- **Auto-Detection**: Automatically detects optimal settings
- **Validation**: Checks hardware reports for errors
- **Suggestions**: Recommends best macOS version
- **Progress Tracking**: Shows exactly what's happening

### Maintains Power

- **Full Feature Set**: All CLI features available in GUI
- **Advanced Options**: Customization tab for experts
- **Console Access**: View all technical details
- **CLI Mode**: Still available with `--cli` flag

## Workflow Example

### First-Time User

1. Launch OpCore-Simplify.bat (Windows) or OpCore-Simplify.command (macOS)
2. GUI opens automatically
3. Click "Select Hardware Report"
   - On Windows: Choose "Export hardware report" option
   - Tool runs Hardware Sniffer automatically
   - Or browse for existing Report.json file
4. Tool automatically:
   - Validates your hardware
   - Selects best macOS version
   - Chooses appropriate SMBIOS model
   - Configures ACPI patches
   - Selects required kexts
5. Switch to "Build EFI" tab
6. Click "Build OpenCore EFI"
7. Watch progress bar and logs
8. When complete, click "Open Result Folder"
9. Follow USB mapping instructions displayed

Total time: 5-10 minutes (mostly waiting for downloads)

### Advanced User

1. Launch with GUI mode
2. Select hardware report
3. Switch to "Customization" tab
4. Fine-tune ACPI patches if needed
5. Customize kexts selection
6. Return to "Configuration" tab
7. Change SMBIOS model if desired
8. Build EFI
9. Review console log for details

## Advantages Over CLI

| Feature | CLI | GUI |
|---------|-----|-----|
| Learning Curve | Steeper | Gentle |
| Visual Feedback | Limited | Extensive |
| Error Prevention | Manual | Automatic |
| Progress Tracking | Text-based | Visual progress bar |
| File Selection | Type paths | File dialog |
| Multi-tasking | Blocks terminal | Non-blocking window |
| Beginner Friendly | No | Yes |
| Advanced Features | Yes | Yes |

## System Requirements

- **Operating System**: Windows 7+, macOS 10.13+, or Linux
- **Python**: 3.6 or higher
- **GUI Library**: tkinter (included with Python)
- **Display**: Any resolution 800x600 or higher

## Troubleshooting

### GUI Won't Start

**Problem**: GUI mode doesn't launch

**Solution**: 
- Check if tkinter is installed: `python3 -c "import tkinter"`
- If missing, install: `sudo apt-get install python3-tk` (Linux)
- Use CLI mode as fallback: `OpCore-Simplify.bat --cli`

### Window Too Small

**Problem**: Can't see all controls

**Solution**:
- Resize window by dragging corners
- All tabs are scrollable
- Minimum recommended: 900x700 pixels

### Build Fails

**Problem**: Build process reports errors

**Solution**:
1. Check Console Log tab for details
2. Verify hardware report is valid
3. Ensure internet connection (downloads required)
4. Try again with different settings
5. Report issue with console log content

## Tips and Tricks

1. **Save Time**: Let the tool auto-configure everything first, then customize if needed
2. **Check Logs**: Console Log tab shows technical details when troubleshooting
3. **Multiple Builds**: You can change settings and rebuild without restarting
4. **Learning Tool**: Watch the Build Log to understand what's happening
5. **CLI Available**: Use `--cli` flag if you prefer command-line interface

## Support

- **GitHub Issues**: Report bugs at the repository
- **Documentation**: README.md for detailed information
- **Community**: Hackintosh community forums
- **Console Log**: Include when reporting issues

## Future Enhancements

Potential features for future versions:
- Dark mode theme option
- Save/load configuration profiles
- Direct USB installer creation
- Built-in USB port mapping
- Configuration comparison tool
- Export build report

## Conclusion

The GUI mode makes OpCore Simplify accessible to everyone, from first-time Hackintosh builders to experienced enthusiasts. The intuitive interface doesn't sacrifice power—all advanced features remain available for those who need them.

Whether you're new to Hackintosh or a veteran, the GUI provides a streamlined, visual workflow that makes building your OpenCore EFI faster and less error-prone.
