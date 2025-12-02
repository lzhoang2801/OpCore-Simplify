"""
Icon system for OpCore Simplify GUI using Segoe Fluent Icons
Compatible with tkinter and cross-platform
"""

import sys
import platform

# Icon mapping using Unicode characters from Segoe Fluent Icons (Windows 11)
# Falls back to Segoe UI Symbol (Windows 10) and Unicode symbols for other platforms
class Icons:
    """Icon provider using system fonts"""
    
    # Detect platform and available icon fonts
    _os = platform.system()
    
    # Primary icon font based on platform
    if _os == 'Windows':
        # Try Windows 11 Segoe Fluent Icons first, fall back to Segoe MDL2 Assets
        ICON_FONT = 'Segoe Fluent Icons'
        FALLBACK_FONT = 'Segoe MDL2 Assets'
    elif _os == 'Darwin':  # macOS
        ICON_FONT = 'SF Pro Display'
        FALLBACK_FONT = 'Helvetica Neue'
    else:  # Linux and others
        ICON_FONT = 'DejaVu Sans'
        FALLBACK_FONT = 'FreeSans'
    
    # Icon definitions using Unicode code points
    # These work across different icon fonts
    ICONS = {
        # Navigation icons
        'settings': '\u2699',      # ⚙ Settings gear
        'search': '\u2315',        # ⌕ Search/magnifying glass  
        'wrench': '\u1F527',       # 🔧 Wrench/tools
        'hammer': '\u1F528',       # 🔨 Hammer/build
        'wifi': '\u1F4F6',         # 📶 WiFi signal
        'clipboard': '\u1F4CB',    # 📋 Clipboard/document
        
        # Status icons
        'check': '\u2713',         # ✓ Check mark
        'cross': '\u2717',         # ✗ X mark
        'warning': '\u26A0',       # ⚠ Warning triangle
        'info': '\u2139',          # ℹ Info
        'lightning': '\u26A1',     # ⚡ Lightning bolt
        
        # Action icons  
        'folder': '\u1F4C1',       # 📁 Folder
        'save': '\u1F4BE',         # 💾 Save/floppy disk
        'trash': '\u1F5D1',        # 🗑 Trash can
        'document': '\u1F4C4',     # 📄 Document
        'book': '\u1F4D6',         # 📖 Book
        
        # Device icons
        'computer': '\u1F4BB',     # 💻 Computer/laptop
        'chart': '\u1F4CA',        # 📊 Bar chart
        'radio': '\u1F4FB',        # 📻 Radio/broadcast
        
        # Arrow icons
        'arrow_right': '\u2192',   # → Right arrow
        'arrow_left': '\u2190',    # ← Left arrow
        'arrow_up': '\u2191',      # ↑ Up arrow
        'arrow_down': '\u2193',    # ↓ Down arrow
    }
    
    # Alternative text-based icons for better compatibility
    TEXT_ICONS = {
        'settings': '⚙',
        'search': '🔍', 
        'wrench': '🔧',
        'hammer': '🔨',
        'wifi': '📡',
        'clipboard': '📋',
        'check': '✓',
        'cross': '✗',
        'warning': '⚠',
        'info': 'ℹ',
        'lightning': '⚡',
        'folder': '📁',
        'save': '💾',
        'trash': '🗑',
        'document': '📄',
        'book': '📖',
        'computer': '💻',
        'chart': '📊',
        'radio': '📡',
        'arrow_right': '→',
        'arrow_left': '←',
        'arrow_up': '↑',
        'arrow_down': '↓',
    }
    
    @classmethod
    def get(cls, name, use_text=True):
        """
        Get an icon character by name
        
        Args:
            name: Icon name from ICONS dict
            use_text: If True, use TEXT_ICONS for better compatibility
            
        Returns:
            Unicode character for the icon
        """
        if use_text and name in cls.TEXT_ICONS:
            return cls.TEXT_ICONS[name]
        return cls.ICONS.get(name, '')
    
    @classmethod
    def get_font(cls, size=12, weight='normal'):
        """
        Get the appropriate icon font configuration
        
        Args:
            size: Font size in points
            weight: Font weight ('normal', 'bold')
            
        Returns:
            Tuple of (font_family, size, weight)
        """
        return (cls.ICON_FONT, size, weight)
    
    @classmethod
    def get_fallback_font(cls, size=12, weight='normal'):
        """
        Get the fallback font configuration
        
        Args:
            size: Font size in points
            weight: Font weight ('normal', 'bold')
            
        Returns:
            Tuple of (font_family, size, weight)
        """
        return (cls.FALLBACK_FONT, size, weight)
    
    @classmethod
    def format_with_text(cls, icon_name, text, separator='  '):
        """
        Format an icon with text label
        
        Args:
            icon_name: Name of the icon
            text: Text label
            separator: Separator between icon and text
            
        Returns:
            Formatted string with icon and text
        """
        icon = cls.get(icon_name)
        if icon:
            return f"{icon}{separator}{text}"
        return text


# Convenience functions for common use cases
def get_nav_icon(icon_name):
    """Get a navigation icon"""
    return Icons.get(icon_name, use_text=True)


def get_status_icon(icon_name):
    """Get a status icon"""
    return Icons.get(icon_name, use_text=True)


def format_button_text(icon_name, label):
    """Format button text with icon"""
    return Icons.format_with_text(icon_name, label)


# Export main class and convenience functions
__all__ = ['Icons', 'get_nav_icon', 'get_status_icon', 'format_button_text']
