# Changelog

## GUI Version Update

### What's New

**GUI Mode (Default)**
- Added a modern graphical user interface using tkinter
- Intuitive tab-based navigation:
  - **Configuration Tab**: Select hardware report, macOS version, and SMBIOS model
  - **Customization Tab**: Advanced ACPI and Kext configuration
  - **Build EFI Tab**: Build process with real-time progress bar and logging
  - **Console Log Tab**: View all system output in one place
- Visual feedback for all operations with progress indicators
- File dialogs for selecting hardware reports
- Dialog-based user prompts replacing CLI text input
- Real-time build progress with percentage completion
- One-click folder opening for built EFI

**CLI Mode (Still Available)**
- Preserved full CLI functionality for advanced users
- Access CLI mode by adding `--cli` argument when launching
- All existing features work exactly as before

### How to Use

**GUI Mode (Default)**:
```bash
# Windows
OpCore-Simplify.bat

# macOS/Linux
./OpCore-Simplify.command
python3 OpCore-Simplify.py
```

**CLI Mode**:
```bash
# Windows
OpCore-Simplify.bat --cli

# macOS/Linux
./OpCore-Simplify.command --cli
python3 OpCore-Simplify.py --cli
```

### Technical Details

- GUI built with Python's standard tkinter library (no additional dependencies)
- Backward compatible with all existing functionality
- Automatic fallback to CLI mode if GUI cannot be loaded
- Thread-based build process to prevent GUI freezing
- Console output redirection to maintain visibility of all operations

### Benefits

- **Easier for Beginners**: No need to memorize commands or options
- **Visual Feedback**: See progress in real-time with progress bars
- **Better Organization**: Tab-based interface keeps everything organized
- **Reduced Errors**: File dialogs prevent path typing mistakes
- **Still Powerful**: All advanced features remain accessible
