# OpCore Simplify GUI Architecture

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpCore Simplify                            │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                   │
│   OpCore     │                                                   │
│   Simplify   │           Page Content Area                      │
│   GUI Mode   │                                                   │
│              │       (Configuration/Customization/             │
│──────────────│        Build/Console pages)                      │
│              │                                                   │
│ ⚙️ Config... │                                                   │
│              │                                                   │
│ 🔧 Custom... │                                                   │
│              │                                                   │
│ 🔨 Build EFI │                                                   │
│              │                                                   │
│ 📋 Console   │                                                   │
│              │                                                   │
│              │                                                   │
│              │                                                   │
│──────────────│                                                   │
│              │                                                   │
│ OpenCore EFI │                                                   │
│ Builder for  │                                                   │
│ Hackintosh   │                                                   │
│              │                                                   │
├──────────────┴──────────────────────────────────────────────────┤
│ ● Ready                                                          │
└──────────────────────────────────────────────────────────────────┘
   Sidebar         Content Area                      Status Bar
  (200px)          (Flexible)                        (30px)
```

## Module Hierarchy

```
OpCoreGUI (main.py)
│
├─ Sidebar (widgets/sidebar.py)
│  ├─ Logo/Title section
│  ├─ Navigation items
│  │  ├─ Configuration
│  │  ├─ Customization
│  │  ├─ Build EFI
│  │  └─ Console Log
│  └─ Footer section
│
├─ Content Area
│  └─ Pages (one visible at a time)
│     ├─ ConfigurationPage (pages/configuration_page.py)
│     │  ├─ Current Config Card
│     │  ├─ Quick Actions Card
│     │  └─ Instructions Card
│     │
│     ├─ CustomizationPage (pages/customization_page.py)
│     │  ├─ Warning Banner
│     │  ├─ ACPI Patches Card
│     │  ├─ Kexts Card
│     │  └─ Information Card
│     │
│     ├─ BuildPage (pages/build_page.py)
│     │  ├─ Build Controls Card
│     │  ├─ Progress Section Card
│     │  ├─ Build Log Card
│     │  └─ Result Actions Card
│     │
│     └─ ConsolePage (pages/console_page.py)
│        ├─ Header with controls
│        └─ Console Log Card
│
└─ StatusBar (widgets/status_bar.py)
   ├─ Status message
   └─ Status indicator
```

## Data Flow

```
User Action
    │
    ├─> Sidebar Navigation
    │   └─> main.py: on_nav_select()
    │       └─> show_page(page_id)
    │           └─> Page.refresh()
    │
    ├─> Hardware Report Selection
    │   └─> main.py: select_hardware_report_gui()
    │       ├─> Export or select file
    │       ├─> Validate with OCPE backend
    │       └─> Update UI variables
    │           └─> Pages automatically update via StringVar
    │
    ├─> Build EFI
    │   └─> main.py: build_efi_gui()
    │       ├─> Create background thread
    │       └─> run_build_process()
    │           ├─> Update progress_var
    │           ├─> Log to build_log
    │           ├─> Call OCPE backend methods
    │           └─> root.after() for thread-safe GUI updates
    │
    └─> Status Updates
        └─> main.py: update_status()
            └─> StatusBar.set_status()
                └─> Update color and text
```

## Component Communication

```
┌──────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                      (OpCoreGUI)                             │
│                                                              │
│  Properties:                                                 │
│  - hardware_report_path (StringVar)                         │
│  - macos_version (StringVar)                                │
│  - smbios_model (StringVar)                                 │
│  - disabled_devices_text (StringVar)                        │
│                                                              │
│  Methods:                                                    │
│  - select_hardware_report_gui()                             │
│  - select_macos_version_gui()                               │
│  - customize_smbios_gui()                                   │
│  - customize_acpi_gui()                                     │
│  - customize_kexts_gui()                                    │
│  - build_efi_gui()                                          │
│  - update_status()                                          │
└────────────┬─────────────────────────────────────┬──────────┘
             │                                     │
             │                                     │
    ┌────────▼────────┐                  ┌────────▼────────┐
    │  Pages (views)  │                  │ Widgets (UI)    │
    │                 │                  │                 │
    │ - Configuration │                  │ - Sidebar       │
    │ - Customization │◄─────uses───────►│ - StatusBar     │
    │ - Build         │   StringVars     │ - ConsoleRedir  │
    │ - Console       │                  │                 │
    └────────┬────────┘                  └─────────────────┘
             │
             │
    ┌────────▼────────┐
    │  OCPE Backend   │
    │                 │
    │ Business logic  │
    │ EFI building    │
    │ Hardware checks │
    └─────────────────┘
```

## Threading Model

```
Main Thread (GUI Event Loop)
    │
    ├─ UI Updates
    ├─ Event Handling
    └─ Tkinter operations
    
Background Thread (Build Process)
    │
    ├─ Long-running operations
    ├─ EFI building
    ├─ File downloads
    └─ Hardware processing
    
Communication: root.after() for thread-safe GUI updates
```

## Style System

```
styles.py
    │
    ├─ COLORS
    │  ├─ Primary: #007AFF
    │  ├─ Success: #34C759
    │  ├─ Warning: #FF9500
    │  ├─ Error: #FF3B30
    │  └─ Backgrounds, text, borders
    │
    ├─ FONTS
    │  ├─ Title: 24px bold
    │  ├─ Heading: 14px bold
    │  ├─ Body: 11px
    │  └─ Small: 10px
    │
    ├─ SPACING
    │  ├─ tiny: 4px
    │  ├─ small: 8px
    │  ├─ medium: 12px
    │  ├─ large: 16px
    │  ├─ xlarge: 24px
    │  └─ xxlarge: 32px
    │
    └─ NAVIGATION_ITEMS
       ├─ config
       ├─ customize
       ├─ build
       └─ console
```

## File Dependencies

```
main.py
├─ imports: styles.py
├─ imports: widgets/__init__.py
│  ├─ Sidebar (sidebar.py)
│  ├─ StatusBar (status_bar.py)
│  └─ ConsoleRedirector (console_redirect.py)
├─ imports: pages/__init__.py
│  ├─ ConfigurationPage (configuration_page.py)
│  ├─ CustomizationPage (customization_page.py)
│  ├─ BuildPage (build_page.py)
│  └─ ConsolePage (console_page.py)
└─ imports: Scripts.datasets.os_data

Each Page
├─ imports: styles.py (for theming)
└─ receives: app_controller (main.py instance)

Each Widget
└─ imports: styles.py (for theming)
```

## State Management

```
Application State (in main.py)
│
├─ UI State (Tkinter StringVar/DoubleVar)
│  ├─ hardware_report_path
│  ├─ macos_version
│  ├─ smbios_model
│  ├─ disabled_devices_text
│  └─ progress_var
│
├─ Data State (Python objects)
│  ├─ hardware_report
│  ├─ hardware_report_data
│  ├─ customized_hardware
│  ├─ disabled_devices
│  ├─ native_macos_version
│  ├─ ocl_patched_macos_version
│  └─ needs_oclp
│
└─ Widget References
   ├─ build_btn
   ├─ progress_bar
   ├─ build_log
   ├─ open_result_btn
   └─ console_log

State Updates:
1. User action → Method call
2. Method updates data state
3. Method updates UI state (StringVar.set())
4. Pages observe UI state changes
5. Pages re-render automatically
```

## Key Design Patterns

1. **MVC-like Structure**
   - Model: OCPE backend (business logic)
   - View: Pages (UI components)
   - Controller: main.py (coordinates between model and view)

2. **Observer Pattern**
   - StringVar/DoubleVar notify observers when changed
   - Pages bind to these variables
   - Automatic UI updates

3. **Strategy Pattern**
   - Different pages implement different views
   - Same interface (Frame with refresh method)
   - Swappable at runtime

4. **Singleton Pattern**
   - Single OpCoreGUI instance
   - Single OCPE backend instance
   - Shared state across pages

5. **Template Method**
   - All pages extend tk.Frame
   - All pages implement setup_ui()
   - Consistent initialization pattern
```
