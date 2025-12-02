"""
Centralized styling and theming for OpCore Simplify GUI
"""

# Color palette
COLORS = {
    # Primary colors
    'primary': '#007AFF',           # Bright blue
    'primary_dark': '#0051D5',      # Darker blue for hover
    'primary_light': '#4DA3FF',     # Light blue for highlights
    
    # Background colors
    'bg_main': '#FFFFFF',           # Main background
    'bg_sidebar': '#F5F5F7',        # Sidebar background
    'bg_hover': '#E8E8E8',          # Hover background
    'bg_selected': '#007AFF',       # Selected item background
    
    # Text colors
    'text_primary': '#1D1D1F',      # Main text
    'text_secondary': '#6E6E73',    # Secondary text
    'text_sidebar': '#1D1D1F',      # Sidebar text
    'text_sidebar_selected': '#FFFFFF',  # Selected sidebar text
    
    # Status colors
    'success': '#34C759',           # Green for success
    'warning': '#FF9500',           # Orange for warnings
    'error': '#FF3B30',             # Red for errors
    'info': '#5AC8FA',              # Light blue for info
    
    # Border colors
    'border': '#D1D1D6',
    'border_light': '#E5E5EA',
    
    # Accent colors
    'accent': '#5856D6',            # Purple accent
}

# Font configurations
FONTS = {
    'title': ('SF Pro Display', 24, 'bold'),
    'subtitle': ('SF Pro Display', 16, 'bold'),
    'heading': ('SF Pro Display', 14, 'bold'),
    'body': ('SF Pro Text', 11),
    'body_bold': ('SF Pro Text', 11, 'bold'),
    'small': ('SF Pro Text', 10),
    'sidebar': ('SF Pro Text', 12),
    'sidebar_selected': ('SF Pro Text', 12, 'bold'),
}

# Fallback fonts for cross-platform compatibility
FONT_FALLBACKS = {
    'SF Pro Display': ['Segoe UI', 'Helvetica Neue', 'Arial'],
    'SF Pro Text': ['Segoe UI', 'Helvetica', 'Arial'],
}

def get_font(font_name):
    """Get font with fallbacks for cross-platform compatibility"""
    font_config = FONTS.get(font_name, FONTS['body'])
    
    # Try primary font first, then fallbacks
    primary_family = font_config[0]
    fallback_families = FONT_FALLBACKS.get(primary_family, ['Arial'])
    
    # For simplicity, use the first fallback (works on most systems)
    family = fallback_families[0] if fallback_families else 'Arial'
    size = font_config[1] if len(font_config) > 1 else 11
    weight = font_config[2] if len(font_config) > 2 else 'normal'
    
    return (family, size, weight)

# Spacing and sizing
SPACING = {
    'tiny': 4,
    'small': 8,
    'medium': 12,
    'large': 16,
    'xlarge': 24,
    'xxlarge': 32,
}

SIZES = {
    'sidebar_width': 200,
    'sidebar_item_height': 44,
    'button_height': 32,
    'input_height': 28,
    'icon_size': 16,
}

# Border radius
RADIUS = {
    'small': 4,
    'medium': 8,
    'large': 12,
}

# Sidebar configuration
SIDEBAR_CONFIG = {
    'width': SIZES['sidebar_width'],
    'bg': COLORS['bg_sidebar'],
    'item_height': SIZES['sidebar_item_height'],
    'padding': SPACING['medium'],
    'separator_color': COLORS['border_light'],
}

# Button styles
BUTTON_STYLES = {
    'primary': {
        'bg': COLORS['primary'],
        'fg': '#FFFFFF',
        'active_bg': COLORS['primary_dark'],
        'hover_bg': COLORS['primary_light'],
    },
    'secondary': {
        'bg': COLORS['bg_sidebar'],
        'fg': COLORS['text_primary'],
        'active_bg': COLORS['bg_hover'],
        'hover_bg': COLORS['bg_hover'],
    },
}

# Navigation items with emojis
NAVIGATION_ITEMS = [
    {'id': 'config', 'label': '⚙️  Configuration', 'emoji': '⚙️'},
    {'id': 'customize', 'label': '🔧  Customization', 'emoji': '🔧'},
    {'id': 'build', 'label': '🔨  Build EFI', 'emoji': '🔨'},
    {'id': 'console', 'label': '📋  Console Log', 'emoji': '📋'},
]
