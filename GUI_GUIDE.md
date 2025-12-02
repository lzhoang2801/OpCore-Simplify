# OpCore Simplify GUI Guide

## Overview

OpCore Simplify now features a modern graphical user interface (GUI) with a sleek sidebar navigation that makes building OpenCore EFI configurations easier and more intuitive than ever before.

## New in This Version

### 🎨 Modern Sidebar Design
- Clean, icon-based navigation on the left side
- Visual feedback with hover effects and selection highlighting
- Better use of screen space with persistent navigation
- Apple-inspired color scheme and typography

### 📁 Modular Code Structure
- Organized into separate files for easy maintenance
- `gui/pages/` - Individual pages for each section
- `gui/widgets/` - Reusable components (sidebar, status bar)
- `gui/styles.py` - Centralized theming and colors
- Easier for developers to contribute and extend

### ✨ Enhanced User Experience
- Card-based layout for better visual organization
- Improved color-coded status indicators
- Better progress visualization
- More intuitive workflow with clear action buttons
- Built-in instructions and helpful tips

## Interface Layout

The GUI features a sidebar navigation with four main sections:

### 1. ⚙️ Configuration Page

This is the primary interface where you'll spend most of your time.

**Current Configuration Display:**
- Shows your hardware report, macOS version, SMBIOS model, and disabled devices
- Information displayed in a clean card layout
- Real-time updates as you make changes

**Quick Actions:**
1. **Select Hardware Report**: Choose your hardware report JSON file
   - On Windows, offers to export directly using Hardware Sniffer
   - Validates the report automatically
   - Loads ACPI tables if available
   
2. **Select macOS Version**: Opens a selection dialog showing:
   - All compatible macOS versions for your hardware
   - Highlights versions requiring OpenCore Legacy Patcher
   - Auto-suggests the best version for stability
   
3. **Customize SMBIOS Model**: Choose the appropriate Mac model
   - Automatically selects the best model for your hardware
   - Configures model-specific settings

**Getting Started Guide:**
- Step-by-step instructions for first-time users
- Quick reference for the build process
- Links to official documentation

### 2. 🔧 Customization Page

For advanced users who want to fine-tune their configuration.

**Features:**
- Warning banner for advanced settings
- Card-based layout for ACPI patches and Kexts
- Clear descriptions of what each option does
- Information panel explaining customization concepts

**ACPI Patches:**
- Automatically selected based on your hardware
- Advanced customization available through CLI version
- Fixes compatibility issues and enables proper hardware support

**Kexts Configuration:**
- Kernel extensions automatically configured
- Enable/disable specific kexts if needed
- Force load kexts on unsupported macOS versions (CLI version)

**Information Panel:**
- Explains what ACPI patches and kexts are
- Lists common patches and their purposes
- Guidance on when to customize vs. use automatic configuration

### 3. 🔨 Build EFI Page

Where the magic happens!

**Build Controls:**
- Large, prominent "Build OpenCore EFI" button
- Status message showing readiness
- Disabled state when configuration is incomplete

**Progress Section:**
- Real-time progress bar (0-100%)
- Percentage display
- Visual feedback during build process

**Build Log:**
- Scrollable console-style log viewer
- Real-time updates as each step completes
- Clear button to reset the log
- Monospace font for better readability
- Error messages if something goes wrong

**Result Actions:**
- "Open EFI Folder" button (enabled after successful build)
- "View Instructions" button for post-build steps
- Quick access to your built EFI

### 4. 📋 Console Log Page

Technical information for troubleshooting.

**Features:**
- Dark theme console for better readability
- All system messages and debug information
- Clear log button
- Export log button (saves to .txt file)
- Downloadable/copyable for bug reports
- Automatically scrolls to latest messages
- Helpful tip about exporting logs for troubleshooting

## Key Features

### Modern Sidebar Navigation

- **Icon-Based Menu**: Each section has a clear icon and label
- **Visual Feedback**: Hover effects and selection highlighting
- **Always Visible**: Quick navigation without switching contexts
- **Compact Design**: Doesn't waste screen space

### User-Friendly Design

- **No Command Line Required**: Everything is point-and-click
- **Visual Feedback**: Progress bars, status messages, and color-coded indicators
- **Error Prevention**: File dialogs prevent typing mistakes
- **Clear Instructions**: Every step is explained with helpful tips
- **Card-Based Layout**: Information organized in visually distinct sections

### Smart Automation

- **Auto-Detection**: Automatically detects optimal settings
- **Validation**: Checks hardware reports for errors before processing
- **Suggestions**: Recommends best macOS version for your hardware
- **Progress Tracking**: Shows exactly what's happening at each step
- **Status Indicators**: Color-coded status (success/warning/error)

### Maintains Power

- **Full Feature Set**: All CLI features available in GUI
- **Advanced Options**: Customization page for experts
- **Console Access**: View all technical details
- **CLI Mode**: Still available with `--cli` flag
- **Export Logs**: Save console output for troubleshooting

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

| Feature | CLI | GUI (New) |
|---------|-----|-----------|
| Learning Curve | Steeper | Gentle |
| Visual Feedback | Limited | Extensive with colors |
| Error Prevention | Manual | Automatic with validation |
| Progress Tracking | Text-based | Visual progress bar & status |
| File Selection | Type paths | File dialog |
| Navigation | Sequential menu | Sidebar navigation |
| Multi-tasking | Blocks terminal | Non-blocking window |
| Status Indicators | Text only | Color-coded status bar |
| Layout | Text-based | Modern card-based design |
| Beginner Friendly | No | Yes |
| Advanced Features | Yes | Yes |

## Technical Architecture

### Modular Structure

The new GUI is built with a modular architecture for better maintainability:

```
Scripts/gui/
├── __init__.py              # Package exports
├── main.py                  # Main application (OpCoreGUI)
├── styles.py                # Centralized theming
├── widgets/                 # Reusable components
│   ├── sidebar.py          # Navigation sidebar
│   ├── status_bar.py       # Bottom status bar
│   └── console_redirect.py # Console output handler
└── pages/                   # Individual pages
    ├── configuration_page.py
    ├── customization_page.py
    ├── build_page.py
    └── console_page.py
```

### Design System

- **Colors**: Apple-inspired palette with primary blue (#007AFF)
- **Typography**: SF Pro Display/Text with cross-platform fallbacks
- **Spacing**: Consistent 4/8/12/16/24/32px spacing scale
- **Components**: Reusable sidebar and status bar widgets

### Benefits

- **Easy to Maintain**: Each page in its own file
- **Consistent Styling**: Centralized theme configuration
- **Extensible**: Easy to add new pages or features
- **Testable**: Modular components can be tested independently
- **Readable**: Clear separation of concerns

## System Requirements

- **Operating System**: Windows 7+, macOS 10.13+, or Linux
- **Python**: 3.6 or higher
- **GUI Library**: tkinter (included with Python)
- **Display**: Any resolution 1000x700 or higher (recommended: 1200x800)
- **Memory**: 4GB RAM minimum

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
- Minimum recommended: 1000x700 pixels (works at 900x700)
- All pages are scrollable if needed
- Sidebar is fixed width for consistency

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
2. **Check Logs**: Console Log page shows technical details when troubleshooting
3. **Multiple Builds**: You can change settings and rebuild without restarting
4. **Learning Tool**: Watch the Build Log to understand what's happening
5. **CLI Available**: Use `--cli` flag if you prefer command-line interface
6. **Export Logs**: Use the export button to save logs for bug reports
7. **Status Bar**: Watch the bottom status bar for current operation status
8. **Color Codes**: Green = success, Orange = warning, Red = error, Blue = info
9. **Sidebar Navigation**: Click any section in the sidebar to jump there instantly
10. **Instructions**: Click "View Instructions" on Build page anytime you need help

## Support

- **GitHub Issues**: Report bugs at the repository
- **Documentation**: README.md for detailed information
- **Community**: Hackintosh community forums
- **Console Log**: Include when reporting issues

## Future Enhancements

Potential features for future versions:

- **Themes**: Dark mode toggle and custom color schemes
- **Profiles**: Save/load configuration profiles
- **USB Mapping**: Built-in USB port mapping tool
- **Direct Installer**: Create macOS USB installer directly from GUI
- **Hardware Detection**: Real-time hardware detection without external tools
- **Configuration Comparison**: Compare different configurations side-by-side
- **Export Build Report**: Generate detailed report of build process
- **Keyboard Shortcuts**: Quick navigation with keyboard
- **Drag & Drop**: Drag hardware report files directly into window
- **Build History**: Track and restore previous builds
- **Notifications**: Desktop notifications for completed builds
- **Multi-language**: Internationalization support

## Contributing

The modular structure makes it easy to contribute:

1. **Adding Pages**: Create new file in `gui/pages/`
2. **Adding Widgets**: Create new file in `gui/widgets/`
3. **Styling**: Modify `gui/styles.py` for theme changes
4. **Documentation**: Update this guide with new features

See `Scripts/gui/README.md` for detailed development guidelines.

## Conclusion

The GUI mode makes OpCore Simplify accessible to everyone, from first-time Hackintosh builders to experienced enthusiasts. The intuitive interface doesn't sacrifice power—all advanced features remain available for those who need them.

Whether you're new to Hackintosh or a veteran, the GUI provides a streamlined, visual workflow that makes building your OpenCore EFI faster and less error-prone.
