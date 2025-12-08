# Config.plist Editor

A powerful TreeView-based editor for OpenCore config.plist files with OC Snapshot, validation, undo/redo, and advanced editing features. Built with qfluentwidgets for modern Fluent Design UI/UX.

## Features

### 1. Interactive TreeView Editor
- **Fluent Design TreeView**: Modern hierarchical display with smooth animations and Fluent Design styling
- **Auto-Expand**: Tree fully expands on file load for quick overview
- **Modal Dialogs**: Properly modal dialogs that block interaction with main window during editing
- **Fluent Design Dialogs**: Modern, beautiful dialogs for all editing operations with proper validation
- **Type-aware Editing**: Edit values with appropriate Fluent controls:
  - Boolean: Fluent CheckBox
  - Number: Fluent SpinBox with proper range
  - String: Fluent LineEdit with clear button
  - Data: Fluent PlainTextEdit for hexadecimal editing
- **Double-click to Edit**: Quick and intuitive editing workflow with polished dialogs
- **Real-time Updates**: Changes are immediately reflected in the tree
- **Search Functionality**: Quickly find keys in your configuration
- **Fluent Context Menus**: Right-click to add items/keys or remove any child item (including nested dictionaries and arrays) with modern RoundMenu
- **Smart Key Management**: Duplicate key detection and validation in add key dialog
- **Drag-and-Drop**: Reorder items within arrays by dragging
- **Undo/Redo**: Full undo/redo support with 50-level history
- **CommandBar**: Modern command bar with text labels and icons for all major operations

### 2. OC Snapshot
Automatically scan your OpenCore EFI folder and update config.plist with discovered files:

#### What OC Snapshot Does:
- **Scans ACPI folder** for `.aml` and `.bin` files
- **Scans Kexts folder** and parses `Info.plist` files
  - Automatically detects ExecutablePath
  - Handles nested kext structures
  - Validates kext configuration
- **Scans Drivers folder** for `.efi` files
- **Scans Tools folder** for `.efi` files
- **Preserves existing entries** (doesn't delete manually added configurations)
- **Updates paths** if files have been moved or renamed

#### Two Snapshot Modes:
1. **OC Snapshot**: Adds new entries while preserving existing ones
2. **OC Clean Snapshot**: Removes all existing entries and rebuilds from scratch

#### Usage:
1. Load a config.plist file
2. Click "OC Snapshot" or "OC Clean Snapshot"
3. Select your OC folder (the one containing ACPI, Kexts, Drivers, Tools subdirectories)
4. Review the updated configuration
5. Save the file

### 3. Validation
Comprehensive validation checks to ensure your config.plist is properly configured:

#### Validation Checks:

**Path Length Validation**
- Ensures all paths are under 128 characters (OC_STORAGE_SAFE_PATH_MAX)
- Checks ACPI, Kext, Driver, and Tool paths
- Special validation for kext combined paths (BundlePath + ExecutablePath/PlistPath)

**Structure Validation**
- Verifies required sections exist:
  - ACPI, Booter, DeviceProperties, Kernel, Misc, NVRAM, PlatformInfo, UEFI
- Checks for recommended subsections
- Warns about missing or incomplete sections

**Duplicate Detection**
- Identifies duplicate ACPI paths
- Identifies duplicate Kext bundle paths
- Helps prevent conflicts and boot issues

**Kext Dependency Checking**
- Uses comprehensive database of 83+ kexts with dependency information
- Validates load order for all known kexts
- Checks dependencies for:
  - Lilu.kext plugins: WhateverGreen, AppleALC, AirportBrcmFixup, etc.
  - VirtualSMC.kext plugins: SMCProcessor, SMCBatteryManager, SMCSuperIO, etc.
  - Bluetooth kexts: IntelBluetoothFirmware, BrcmPatchRAM, etc.
  - Network kexts: IntelMausi, LucyRTL8125, etc.
  - And many more...
- Warns if dependencies are loaded in wrong order

#### Validation Results:
- **Errors**: Critical issues that may prevent booting
- **Warnings**: Potential issues or improvements
- **Export Reports**: Save validation results to JSON or text file for documentation

### 4. File Operations
- **Load**: Open any config.plist file
- **Save**: Save changes to the current file
- **Save As**: Save to a new file location
- **Undo/Redo**: Revert or reapply changes (50-level history)

### 5. Export Validation Reports
- Export validation results to JSON or text format
- Timestamped reports for tracking configuration health
- Useful for documentation and troubleshooting

## How to Use

### Basic Workflow

1. **Load a config.plist**
   - Click "Load config.plist" button
   - Select your OpenCore config.plist file
   - The tree will populate with your configuration

2. **Edit Values**
   - Double-click any value in the "Value" column
   - Edit using the appropriate dialog
   - Changes are saved to the tree immediately

3. **Run OC Snapshot** (Optional but Recommended)
   - Click "OC Snapshot" button
   - Select your OC folder (typically at `EFI/OC/`)
   - Review the updated entries
   - The snapshot will:
     - Add any missing ACPI files
     - Add any missing Kexts with proper paths
     - Add any missing Drivers
     - Add any missing Tools
     - Remove entries for files that no longer exist

4. **Validate Configuration**
   - Click "Validate" button
   - Review any errors or warnings
   - Fix issues as needed

5. **Save Your Changes**
   - Click "Save" to save to the current file
   - Or "Save As" to save to a new location

### Advanced Usage

#### Clean Snapshot Workflow
Use this when you want to completely rebuild your config from scratch:

1. Load your config.plist
2. Click "OC Clean Snapshot"
3. Select your OC folder
4. All ACPI/Kext/Driver/Tool entries will be cleared and rebuilt
5. Review and save

#### Manual Editing
You can manually edit values in the tree:

1. Navigate to the value you want to edit
2. Double-click in the "Value" column
3. Edit in the dialog that appears
4. Click OK to save changes

## Best Practices

1. **Backup First**: Always backup your config.plist before making changes
2. **Validate Often**: Run validation after making significant changes
3. **Use OC Snapshot**: Let the tool handle file paths to avoid typos
4. **Check Dependencies**: Pay attention to kext dependency warnings
5. **Test Your Changes**: Always test your EFI on the target system

## Tips

- **Search**: Use the search box to quickly find keys in your configuration
- **Right-click Menus**: Right-click on arrays or dictionaries to add items/keys, or right-click on any child item (including nested dictionaries and arrays) to remove it
- **Drag-and-Drop**: Drag items within arrays to reorder them
- **Undo/Redo**: Use Ctrl+Z/Ctrl+Y or the toolbar buttons to undo/redo changes
- **Path Length**: Keep your file and folder names short to avoid exceeding the 128 character limit
- **Kext Order**: The order in the tree matters for kexts with dependencies
- **Clean Snapshot**: Use clean snapshot when reorganizing your EFI folder structure
- **Validation**: Run validation before closing the editor to catch issues early
- **Export Reports**: Export validation results for documentation or sharing

## Limitations

- Undo history limited to 50 actions
- Drag-and-drop only works within the same parent (arrays)
- Cannot rename dictionary keys directly (remove and re-add instead)

## Code Refactoring (Version 5.0)

### Optimizations Made

The code has been refactored for better maintainability and reduced complexity:

**Constants**: All magic numbers moved to constants (`MAX_UNDO_LEVELS`, `OC_STORAGE_SAFE_PATH_MAX`, `TYPE_DEFAULTS`)

**Helper Methods**: Common operations extracted into reusable methods:
- `_get_window()` - Get main window reference
- `_show_info_bar()` - Centralized InfoBar display
- `_create_default_value()` - Generate default values by type
- `_snapshot_folder_generic()` - Unified folder scanning logic

**Consolidated Snapshot Logic**: The 4 separate snapshot methods (`_snapshot_acpi`, `_snapshot_kexts`, `_snapshot_drivers`, `_snapshot_tools`) now use a shared `_snapshot_folder_generic()` method with configuration dictionaries, eliminating ~100 lines of duplicated code.

**Benefits**:
- Easier to maintain (change once, affect all)
- Fewer bugs (less duplication)
- Better organization
- More extensible

## Technical Details

### Based on ProperTree
The OC Snapshot functionality is based on [ProperTree](https://github.com/corpnewt/ProperTree) by CorpNewt, 
the de-facto standard plist editor for OpenCore configurations.

### Path Length Constant
The path length validation uses `OC_STORAGE_SAFE_PATH_MAX = 128` from OpenCorePkg 
(`Include/Acidanthera/Library/OcStorageLib.h`).

### File Format
The editor preserves plist formatting and uses OrderedDict to maintain key order when saving.

### Kext Database
Uses the comprehensive kext database from the OpenCore Simplify project, containing 83+ kexts with full dependency information.

### Dialog Handling
All dialogs follow the standard Qt pattern using `dialog.exec()` which is a blocking call that automatically handles modal behavior and prevents QPainter conflicts. Dialog results are processed immediately after `exec()` returns, following the same pattern used throughout the application in `custom_dialogs.py`. This ensures proper event handling and eliminates the need for deferred operations.

## Troubleshooting

**Q: OC Snapshot doesn't find my files**
- Make sure you selected the correct OC folder (should contain ACPI, Kexts, Drivers subdirectories)
- Try selecting the parent folder if you selected EFI/OC directly

**Q: Validation shows path too long errors**
- Shorten your file names or folder structure
- Consider flattening your kext directory structure

**Q: Kext dependency warnings appear**
- Check the load order in config.plist
- Make sure parent kexts (like Lilu.kext, VirtualSMC.kext) are loaded before their dependencies

**Q: Can't edit certain values**
- Dictionary and Array containers cannot be edited directly
- Edit their child values instead

**Q: How do I undo a mistake?**
- Click the "Undo" action in the CommandBar or press Ctrl+Z
- Up to 50 actions can be undone

## Recent Enhancements

**Version 2.0 Updates:**
- ✅ Search/filter in tree - Use the search box to quickly find keys
- ✅ Add/remove array items - Right-click arrays to add or remove entries
- ✅ Code duplication reduced - Now uses shared utils for file I/O
- ✅ Removed unused dependencies - snapshot.plist no longer required

**Version 3.0 Updates:**
- ✅ Add/remove dictionary keys - Full support for adding and removing keys
- ✅ Drag-and-drop reordering - Reorder array items by dragging
- ✅ Expanded kext dependency database - 83+ kexts with full dependency information
- ✅ Undo/redo functionality - 50-level history with toolbar buttons
- ✅ Export validation reports - Save validation results to JSON or text files

**Version 4.0 Updates:**
- ✅ Fluent Design UI - Migrated to qfluentwidgets TreeWidget for consistent modern UI
- ✅ RoundMenu - Modern context menus with Fluent Design styling
- ✅ CommandBar - Compact command bar with all operations in one place
- ✅ Better visual consistency - Matches the Fluent Design system throughout the app
- ✅ Smoother animations - Enhanced user experience with fluid transitions

**Version 4.1 Updates (Latest):**
- ✅ Fluent Design Dialogs - All dialogs upgraded to MessageBoxBase with modern styling
- ✅ Smart Input Validation - Real-time validation in add key dialog with duplicate detection
- ✅ Enhanced Edit Dialogs - Type-specific Fluent controls (LineEdit, SpinBox, CheckBox, PlainTextEdit)
- ✅ Improved User Feedback - Success notifications for operations like key removal
- ✅ Better UX - Clear buttons, placeholders, and proper dialog sizing
- ✅ Code Cleanup - Removed old PyQt6 dialog components for cleaner codebase

## Future Enhancements

Planned features for future releases:
- OpenCore version-specific validation
- Keyboard shortcuts for common operations
- Advanced search with regex support
- Batch edit operations
- Compare two config.plist files
