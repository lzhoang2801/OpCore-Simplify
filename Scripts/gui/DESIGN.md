# OpCore Simplify GUI - Visual Design Mockup

## Overview

This document describes the visual design of the new OpCore Simplify GUI with sidebar navigation.

## Color Scheme

### Primary Colors
- **Primary Blue**: #007AFF - Used for buttons, links, and selections
- **Primary Dark**: #0051D5 - Hover state for primary elements
- **Primary Light**: #4DA3FF - Highlights and accents

### Status Colors
- **Success Green**: #34C759 - Successful operations
- **Warning Orange**: #FF9500 - Warnings and cautions
- **Error Red**: #FF3B30 - Errors and critical issues
- **Info Blue**: #5AC8FA - Information messages

### Background Colors
- **Main Background**: #FFFFFF - Pure white for main content
- **Sidebar Background**: #F5F5F7 - Light gray for sidebar
- **Card Background**: #F5F5F7 - Light gray for content cards
- **Hover Background**: #E8E8E8 - Slightly darker gray for hover states
- **Console Background**: #1E1E1E - Dark background for console

### Text Colors
- **Primary Text**: #1D1D1F - Almost black for main text
- **Secondary Text**: #6E6E73 - Gray for secondary information
- **Link Text**: #007AFF - Blue for clickable elements
- **Console Text**: #D4D4D4 - Light gray for dark console

## Typography

### Font Families
- **Primary**: SF Pro Display / Segoe UI / Helvetica Neue / Arial
- **Body**: SF Pro Text / Segoe UI / Helvetica / Arial
- **Console**: Consolas / Monaco / Courier New (monospace)

### Font Sizes
- **Title**: 24px, bold - Main page titles
- **Subtitle**: 16px, bold - Section headers
- **Heading**: 14px, bold - Card headers
- **Body**: 11px, normal - Regular text
- **Body Bold**: 11px, bold - Emphasized text
- **Small**: 10px, normal - Helper text and notes
- **Console**: 9-10px, monospace - Console output

## Layout Structure

### Window
- **Default Size**: 1200x800 pixels
- **Minimum Size**: 1000x700 pixels
- **Background**: White (#FFFFFF)

### Sidebar
- **Width**: 200px (fixed)
- **Background**: Light gray (#F5F5F7)
- **Position**: Left side, full height

### Content Area
- **Width**: Flexible (window width - sidebar width)
- **Padding**: 32px on all sides
- **Background**: White (#FFFFFF)

### Status Bar
- **Height**: 30px (fixed)
- **Background**: Light gray (#F5F5F7)
- **Position**: Bottom, full width

## Component Designs

### Sidebar Navigation

```
┌──────────────────┐
│                  │
│   OpCore         │ ← Title: 16px bold, #1D1D1F
│   Simplify       │
│   GUI Mode       │ ← Subtitle: 10px, #6E6E73
│                  │
├──────────────────┤ ← Separator: 1px, #E5E5EA
│                  │
│ ⚙️  Configuration│ ← 12px, with emoji
│                  │   Selected: #007AFF bg, white text
│ 🔧  Customization│   Hover: #E8E8E8 bg
│                  │   Default: transparent bg, #1D1D1F text
│ 🔨  Build EFI    │
│                  │
│ 📋  Console Log  │
│                  │
│        ⋮         │
│                  │
│                  │
├──────────────────┤
│ OpenCore EFI     │ ← Footer: 10px, #6E6E73
│ Builder for      │
│ Hackintosh       │
└──────────────────┘
```

### Content Card

```
┌────────────────────────────────────────┐
│                                        │
│  Card Title                    14px bold  ← #1D1D1F on #F5F5F7
│                                        │
│  Description text goes here...         │ ← 11px, #6E6E73
│                                        │
│  ┌──────────────────────────────┐     │
│  │  Card content area           │     │ ← #FFFFFF or #F5F5F7
│  │                              │     │
│  └──────────────────────────────┘     │
│                                        │
│  [Action Button]                       │ ← Button (see below)
│                                        │
└────────────────────────────────────────┘
   ↑ Padding: 16-24px all sides
```

### Primary Button

```
┌────────────────────────┐
│  🔨  Build OpenCore EFI │ ← #34C759 bg (green for build)
└────────────────────────┘   #FFFFFF text, 14px bold
                             Padding: 16px horizontal, 12px vertical
                             Border radius: 8px (conceptual)
                             Hover: #2DA44E (darker green)
                             Cursor: pointer
```

### Secondary Button

```
┌────────────────────────┐
│  Open EFI Folder       │ ← #007AFF bg (blue)
└────────────────────────┘   #FFFFFF text, 11px bold
                             Padding: 16px horizontal, 12px vertical
                             Hover: #0051D5 (darker blue)
```

### Action Link Button

```
┌────────────────────────────────┐
│ 1  Select Hardware Report      │ ← Badge: 3 width, #007AFF bg
│    Choose your hardware...     │   Title: 11px bold, #007AFF
└────────────────────────────────┘   Description: 10px, #6E6E73
                                     Hover: Title becomes #0051D5
```

### Progress Bar

```
┌────────────────────────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░│ ← #34C759 (success green)
└────────────────────────────────────────┘   Background: #E5E5EA
    45%                                       Height: 8px
    ↑ 10px, #6E6E73                          Border radius: 4px
```

### Status Bar

```
┌────────────────────────────────────────┐
│ Ready                              ●   │ ← Text: 11px, #6E6E73
└────────────────────────────────────────┘   Dot: Status color
                                             Green: success
                                             Orange: warning
                                             Red: error
                                             Blue: info
```

### Warning Banner

```
┌────────────────────────────────────────┐
│ ⚠️  Advanced Settings                  │ ← #FF9500 bg (orange)
│                                        │   #FFFFFF text
│ These settings are automatically...   │   12px bold title
│                                        │   10px normal description
└────────────────────────────────────────┘   Padding: 12px all sides
```

## Page Layouts

### Configuration Page

```
┌────────────────────────────────────────────┐
│                                            │
│  Configuration                  24px bold  │
│  Set up your hardware...        11px gray  │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Current Configuration                │ │ ← Card #F5F5F7
│  │                                      │ │
│  │ Hardware Report: [value in blue]    │ │
│  │ macOS Version:   [value in blue]    │ │
│  │ SMBIOS Model:    [value in blue]    │ │
│  │ Disabled:        [value in blue]    │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Quick Actions                        │ │
│  │                                      │ │
│  │ 1  Select Hardware Report           │ │ ← Action buttons
│  │    Choose your hardware...          │ │
│  │                                      │ │
│  │ 2  Select macOS Version             │ │
│  │    Choose the macOS version...      │ │
│  │                                      │ │
│  │ 3  Customize SMBIOS Model           │ │
│  │    Select the appropriate Mac...    │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Getting Started                      │ │
│  │                                      │ │
│  │ Welcome to OpCore Simplify!         │ │
│  │                                      │ │
│  │ Follow these steps...               │ │
│  │ [Instructions text...]              │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

### Build Page

```
┌────────────────────────────────────────────┐
│                                            │
│  Build OpenCore EFI             24px bold  │
│  Create your customized...      11px gray  │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │                                      │ │
│  │  [🔨 Build OpenCore EFI]  Ready...  │ │ ← Large button
│  │                                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Build Progress                       │ │
│  │                                      │ │
│  │ ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │ ← Progress bar
│  │                                 45%  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 📝 Build Log           [Clear]       │ │
│  │                                      │ │
│  │ ┌──────────────────────────────────┐│ │
│  │ │ Starting EFI build process...    ││ │ ← Console-style
│  │ │ Step 1/5: Copying EFI base...    ││ │   Monospace font
│  │ │ Step 2/5: Applying ACPI...       ││ │   Scrollable
│  │ │                                  ││ │
│  │ └──────────────────────────────────┘│ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │                                      │ │
│  │ [📁 Open EFI Folder] [View Instr.] │ │ ← Action buttons
│  │                                      │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

### Console Page

```
┌────────────────────────────────────────────┐
│                                            │
│  Console Log           [🗑️ Clear] [💾 Export]
│  System messages...                        │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │████████████████████████████████████  │ │ ← Dark theme
│  │▓ OpCore Simplify GUI started         │ │   #1E1E1E bg
│  │▓ Welcome to OpCore Simplify!         │ │   #D4D4D4 text
│  │▓                                      │ │   Monaco/Consolas
│  │▓ Loading hardware report...          │ │   Monospace 9-10px
│  │▓ Hardware report loaded successfully!│ │
│  │▓                                      │ │
│  │                                      │ │
│  │                                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  💡 Tip: Export the console log when...   │ ← Helpful tip
└────────────────────────────────────────────┘
```

## Interactive States

### Button States
1. **Normal**: Defined background and text color
2. **Hover**: Slightly darker background (20% darker)
3. **Active**: Same as hover or slightly lighter
4. **Disabled**: 50% opacity, gray background, no cursor change

### Link States
1. **Normal**: Primary blue (#007AFF)
2. **Hover**: Darker blue (#0051D5)
3. **Visited**: Same as normal (no distinction needed)

### Navigation Item States
1. **Normal**: Transparent background, dark text
2. **Hover**: Light gray background (#E8E8E8)
3. **Selected**: Primary blue background (#007AFF), white text, bold font

### Input States
1. **Normal**: Light background, dark text
2. **Focus**: Blue outline (conceptual)
3. **Error**: Red border or background tint
4. **Disabled**: Gray background, gray text

## Spacing Guidelines

### Padding
- **Content Area**: 32px all sides
- **Cards**: 16-24px all sides
- **Buttons**: 16px horizontal, 12px vertical
- **Small elements**: 8-12px

### Margins
- **Between cards**: 16px vertical
- **Between sections**: 24px vertical
- **Between elements**: 8-12px

### Element Heights
- **Sidebar items**: 44px (touch-friendly)
- **Buttons**: 32-40px depending on importance
- **Input fields**: 28px
- **Status bar**: 30px
- **Progress bar**: 8px

## Accessibility Considerations

1. **Color Contrast**: All text meets WCAG AA standards
2. **Font Sizes**: Minimum 10px for readable text
3. **Touch Targets**: Minimum 44px height for interactive elements
4. **Focus Indicators**: Visual indication of focused elements
5. **Error Messages**: Color + text (not color alone)
6. **Status Indicators**: Icon + color + text when possible

## Responsive Behavior

### Window Resize
- Sidebar: Fixed at 200px
- Content: Flexible, adjusts with window width
- Status bar: Full width
- Cards: Full width of content area
- Text: May wrap at smaller widths

### Minimum Dimensions
- **Width**: 1000px (sidebar 200px + content 800px)
- **Height**: 700px
- Below minimum, scrollbars appear

## Animation Concepts

While not implemented in current tkinter version, future enhancements could include:

1. **Page Transitions**: Smooth fade or slide when changing pages
2. **Button Hover**: Subtle background color transition
3. **Progress Bar**: Smooth fill animation
4. **Loading States**: Spinner or pulsing indicator
5. **Status Messages**: Fade in/out for status changes

## Platform Considerations

### Windows
- Uses Segoe UI font
- Native window controls
- Flat design aesthetic

### macOS
- Uses SF Pro font (if available)
- Native window controls
- Follows macOS Human Interface Guidelines

### Linux
- Uses Helvetica or Arial
- GTK or Qt styling
- Adapts to system theme

## Implementation Notes

All designs are implemented using:
- **tkinter**: Standard Python GUI library
- **No custom drawing**: Uses standard widgets
- **Cross-platform**: Works on Windows, macOS, Linux
- **No external dependencies**: Only uses Python standard library

The designs prioritize:
- **Clarity**: Easy to understand at a glance
- **Consistency**: Same patterns throughout
- **Efficiency**: Quick access to common tasks
- **Reliability**: Stable and predictable behavior
