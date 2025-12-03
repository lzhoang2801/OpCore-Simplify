# GUI Dependencies

OpCore Simplify now uses **qfluentwidgets** (PyQt6-Fluent-Widgets) for its graphical user interface.

## Installation

To use the GUI mode, you need to install the required dependencies:

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install PyQt6 PyQt6-Fluent-Widgets
```

## Requirements

- **PyQt6** >= 6.6.0 - Qt6 framework for Python
- **PyQt6-Fluent-Widgets** >= 1.5.0 - Fluent Design System components

## Platform Support

The GUI works on:
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (with Qt6 dependencies)

## CLI Mode

If you don't want to use the GUI or don't have the dependencies installed, you can run OpCore Simplify in CLI mode:

```bash
python OpCore-Simplify.py --cli
```

The application will also automatically fall back to CLI mode if the GUI dependencies are not available.

## About qfluentwidgets

qfluentwidgets is a modern UI component library based on PyQt6/PySide6 that implements Microsoft's Fluent Design System. It provides:

- Beautiful, modern UI components
- Smooth animations and transitions
- Light/dark theme support
- Cross-platform compatibility
- Active development and maintenance

More information: https://qfluentwidgets.com
