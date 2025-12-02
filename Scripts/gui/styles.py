"""
Centralized styling and theming for OpCore Simplify GUI
"""

# Color palette - macOS Big Sur/Monterey inspired with enhanced gradient support
COLORS = {
    # Primary colors - macOS system blue
    'primary': '#007AFF',           # macOS system blue
    'primary_dark': '#0051D5',      # Darker blue for active state
    'primary_light': '#5AC8FA',     # Light blue for hover
    'primary_hover': '#0062CC',     # Hover state blue
    
    # Background colors - macOS neutral palette
    'bg_main': '#FFFFFF',           # Pure white main background
    'bg_secondary': '#F5F5F7',      # Light gray secondary background
    'bg_sidebar': '#F8F8F8',        # Sidebar background (lighter)
    'bg_sidebar_gradient_start': '#FAFAFA',  # Gradient start
    'bg_sidebar_gradient_end': '#F0F0F0',    # Gradient end
    'bg_hover': '#E8E8ED',          # Hover background (more subtle)
    'bg_selected': '#007AFF',       # Selected item background
    'bg_selected_hover': '#0062CC', # Selected item hover
    'bg_card': '#FAFAFA',           # Card background
    
    # Text colors - macOS text hierarchy
    'text_primary': '#000000',      # Pure black for primary text
    'text_secondary': '#6C6C70',    # Medium gray for secondary text
    'text_tertiary': '#8E8E93',     # Light gray for tertiary text
    'text_sidebar': '#1C1C1E',      # Sidebar text (slightly softer black)
    'text_sidebar_hover': '#000000', # Sidebar text on hover
    'text_sidebar_selected': '#FFFFFF',  # Selected sidebar text
    
    # Status colors - macOS system colors
    'success': '#30D158',           # macOS green
    'warning': '#FF9F0A',           # macOS orange
    'error': '#FF453A',             # macOS red
    'info': '#64D2FF',              # macOS light blue
    
    # Border colors - subtle macOS borders
    'border': '#D1D1D6',
    'border_light': '#E5E5EA',
    'border_focus': '#007AFF',
    'shadow': '#00000015',          # Very subtle shadow
    
    # Accent colors
    'accent': '#5E5CE6',            # macOS purple
    'accent_secondary': '#FF375F',  # macOS pink
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

# Spacing and sizing - macOS Human Interface Guidelines
SPACING = {
    'tiny': 4,
    'small': 8,
    'medium': 12,
    'large': 16,
    'xlarge': 20,
    'xxlarge': 24,
    'xxxlarge': 32,
}

SIZES = {
    'sidebar_width': 220,
    'sidebar_item_height': 40,
    'button_height': 28,
    'button_padding_x': 16,
    'button_padding_y': 6,
    'input_height': 28,
    'icon_size': 16,
}

# Border radius - macOS rounded corners
RADIUS = {
    'small': 4,
    'medium': 6,
    'large': 8,
    'xlarge': 10,
    'button': 6,
    'card': 10,
}

# Sidebar configuration - macOS style
SIDEBAR_CONFIG = {
    'width': SIZES['sidebar_width'],
    'bg': COLORS['bg_sidebar'],
    'item_height': SIZES['sidebar_item_height'],
    'padding': SPACING['medium'],
    'separator_color': COLORS['border_light'],
    'item_padding_x': 12,
    'item_padding_y': 8,
    'item_radius': 6,
}

# Button styles - macOS inspired
BUTTON_STYLES = {
    'primary': {
        'bg': COLORS['primary'],
        'fg': '#FFFFFF',
        'active_bg': COLORS['primary_dark'],
        'hover_bg': COLORS['primary_hover'],
        'border_radius': RADIUS['button'],
    },
    'secondary': {
        'bg': COLORS['bg_secondary'],
        'fg': COLORS['text_primary'],
        'active_bg': COLORS['bg_hover'],
        'hover_bg': COLORS['bg_hover'],
        'border_radius': RADIUS['button'],
    },
    'success': {
        'bg': COLORS['success'],
        'fg': '#FFFFFF',
        'active_bg': '#28A745',
        'hover_bg': '#34C759',
        'border_radius': RADIUS['button'],
    },
}

# Navigation items with emojis
NAVIGATION_ITEMS = [
    {'id': 'config', 'label': 'Configuration', 'emoji': '⚙️', 'section': 'main'},
    {'id': 'compatibility', 'label': 'Compatibility', 'emoji': '🔍', 'section': 'main'},
    {'id': 'customize', 'label': 'Customization', 'emoji': '🔧', 'section': 'main'},
    {'id': 'build', 'label': 'Build EFI', 'emoji': '🔨', 'section': 'main'},
    {'id': 'wifi', 'label': 'WiFi Profiles', 'emoji': '📡', 'section': 'tools'},
    {'id': 'console', 'label': 'Console Log', 'emoji': '📋', 'section': 'tools'},
]

# Animation settings
ANIMATION = {
    'transition_speed': 150,  # milliseconds
    'hover_delay': 50,        # milliseconds
    'fade_steps': 10,         # number of steps in fade animation
}
