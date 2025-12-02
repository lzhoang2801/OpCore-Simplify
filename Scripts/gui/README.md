# OpCore Simplify GUI Module

This directory contains the modular GUI implementation for OpCore Simplify, featuring a modern sidebar navigation and organized page structure.

## Structure

```
gui/
├── __init__.py              # Package initialization, exports OpCoreGUI
├── main.py                  # Main application window with sidebar layout
├── styles.py                # Centralized styling and theming
│
├── widgets/                 # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py          # Navigation sidebar widget
│   ├── status_bar.py       # Bottom status bar widget
│   └── console_redirect.py # Console output redirection
│
└── pages/                   # Individual page implementations
    ├── __init__.py
    ├── configuration_page.py    # Hardware report & macOS selection
    ├── customization_page.py    # ACPI patches & Kexts configuration
    ├── build_page.py            # EFI build interface
    └── console_page.py          # Console log viewer
```

## Features

### Modern Design
- **Sidebar Navigation**: Clean, icon-based navigation with visual feedback
- **Card-based Layout**: Content organized in visually distinct cards
- **Color-coded Status**: Visual indicators for success, warnings, and errors
- **Responsive Design**: Adapts to different window sizes

### User Experience
- **Intuitive Workflow**: Step-by-step process with clear guidance
- **Visual Progress**: Real-time progress bars and status updates
- **Smart Defaults**: Automatic configuration with manual override options
- **Helpful Instructions**: Built-in guides and tips for each step

### Code Organization
- **Modular Structure**: Each page and widget in its own file
- **Centralized Styling**: Single source of truth for colors and fonts
- **Reusable Components**: Sidebar and status bar used across the app
- **Easy Maintenance**: Clear separation of concerns

## Design System

### Colors
- **Primary**: #007AFF (Apple-style blue)
- **Success**: #34C759 (Green)
- **Warning**: #FF9500 (Orange)
- **Error**: #FF3B30 (Red)
- **Background**: #FFFFFF / #F5F5F7

### Typography
- **Fonts**: SF Pro Display/Text with fallbacks (Segoe UI, Helvetica, Arial)
- **Sizes**: Title (24px), Heading (14px), Body (11px), Small (10px)

### Spacing
- Consistent spacing scale: 4, 8, 12, 16, 24, 32px
- Card padding: 16-24px
- Button padding: 12-16px

## Components

### Sidebar (widgets/sidebar.py)
- Navigation between main pages
- Visual feedback on hover and selection
- Logo/branding area
- Footer with version info

### Status Bar (widgets/status_bar.py)
- Bottom-aligned status messages
- Color-coded status indicator
- Update methods for different states

### Console Redirect (widgets/console_redirect.py)
- Thread-safe stdout redirection
- Captures print statements to GUI
- Maintains original stdout functionality

### Configuration Page (pages/configuration_page.py)
- Current configuration display
- Hardware report selection
- macOS version selection
- SMBIOS customization
- Getting started guide

### Customization Page (pages/customization_page.py)
- ACPI patches configuration
- Kexts management
- Advanced settings with warnings
- Information about customization options

### Build Page (pages/build_page.py)
- Build EFI button with prominent styling
- Real-time progress bar
- Build log viewer
- Result folder access
- Instructions dialog

### Console Page (pages/console_page.py)
- System messages and logs
- Export functionality
- Clear log option
- Dark theme for better readability

## Usage

```python
from Scripts.gui import OpCoreGUI

# Create GUI instance with OCPE backend
app = OpCoreGUI(ocpe_instance)

# Run the application
app.run()
```

## Extending the GUI

### Adding a New Page

1. Create a new file in `pages/` (e.g., `my_page.py`)
2. Inherit from `tk.Frame` and implement the page
3. Add the page to `pages/__init__.py`
4. Create the page instance in `main.py`
5. Add navigation item to `styles.py` NAVIGATION_ITEMS
6. Update sidebar selection logic in `main.py`

### Adding a New Widget

1. Create a new file in `widgets/` (e.g., `my_widget.py`)
2. Inherit from appropriate Tkinter widget
3. Add the widget to `widgets/__init__.py`
4. Import and use in pages as needed

### Customizing Styles

1. Edit `styles.py` to change colors, fonts, or spacing
2. Changes automatically apply throughout the application
3. Use `get_font()` helper for cross-platform font compatibility

## Development Guidelines

### Code Style
- Use descriptive variable and function names
- Add docstrings to classes and methods
- Keep methods focused and concise
- Group related functionality together

### UI/UX Principles
- Maintain consistent spacing and alignment
- Use appropriate colors for status indicators
- Provide visual feedback for user actions
- Include helpful instructions and tooltips
- Ensure responsive layout behavior

### Threading
- Run long operations in separate threads
- Use `root.after()` for thread-safe GUI updates
- Never block the main GUI thread
- Handle exceptions gracefully

## Dependencies

- **Python 3.6+**: Core language
- **tkinter**: Standard GUI library (included with Python)
- **threading**: For background operations
- **OpCore-Simplify backend**: Business logic and EFI building

## Future Enhancements

Potential improvements for future versions:
- [ ] Dark mode theme toggle
- [ ] Configuration profiles (save/load)
- [ ] Animated progress indicators
- [ ] Drag-and-drop file support
- [ ] Keyboard shortcuts
- [ ] Integrated USB mapping tool
- [ ] Real-time hardware detection
- [ ] Build history tracking
- [ ] Custom themes support

## Troubleshooting

### GUI Won't Start
- Ensure tkinter is installed: `python3 -c "import tkinter"`
- Check Python version: `python3 --version` (3.6+ required)
- Verify module structure is intact
- Check for syntax errors: `python3 -m py_compile gui/*.py`

### Import Errors
- Ensure `__init__.py` files exist in all directories
- Check sys.path includes parent directory
- Verify file permissions

### Layout Issues
- Check window size constraints
- Verify pack/grid geometry managers
- Test on different screen resolutions
- Review widget packing order

## License

This GUI module is part of OpCore Simplify and shares the same license as the main project.
