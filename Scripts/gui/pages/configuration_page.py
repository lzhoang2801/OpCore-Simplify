"""
Step 3: Review and adjust configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

from ..styles import COLORS, SPACING, get_font
from ..icons import Icons


class ConfigurationPage(tk.Frame):
    """Step 3: Review and adjust auto-configured settings"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize configuration page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the configuration page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Step indicator
        step_label = tk.Label(
            container,
            text="STEP 3 OF 4",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary']
        )
        step_label.pack(anchor=tk.W, pady=(0, SPACING['tiny']))
        
        # Title section
        title_label = tk.Label(
            container,
            text="Review Configuration",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Review automatically selected settings or customize as needed",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Auto-configuration status card
        self.create_status_card(container)
        
        # Current configuration card
        self.create_config_card(container)
        
        # Customization options card
        self.create_customization_card(container)
        
    def create_status_card(self, parent):
        """Create auto-configuration status card"""
        card = tk.Frame(parent, bg='#D1ECF1', relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        content = tk.Frame(card, bg='#D1ECF1')
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['medium'])
        
        # Icon
        icon = tk.Label(
            content,
            text="✅",
            font=('SF Pro Display', 24),
            bg='#D1ECF1',
            fg='#0C5460'
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # Text
        text_frame = tk.Frame(content, bg='#D1ECF1')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(
            text_frame,
            text="Automatic Configuration Complete",
            font=get_font('body_bold'),
            bg='#D1ECF1',
            fg='#0C5460',
            anchor=tk.W
        )
        title_label.pack(anchor=tk.W)
        
        desc_label = tk.Label(
            text_frame,
            text="Settings have been optimally configured based on your hardware. Review below or customize if needed.",
            font=get_font('small'),
            bg='#D1ECF1',
            fg='#0C5460',
            anchor=tk.W,
            wraplength=800
        )
        desc_label.pack(anchor=tk.W)
    
    def create_config_card(self, parent):
        """Create current configuration display card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header
        header = tk.Label(
            card,
            text="Current Configuration",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Configuration items
        config_items = [
            {
                'label': "Hardware Report:",
                'var': "hardware_report_path",
                'icon': "📋"
            },
            {
                'label': "macOS Version:",
                'var': "macos_version",
                'icon': "🍎"
            },
            {
                'label': "SMBIOS Model:",
                'var': "smbios_model",
                'icon': "💻"
            },
            {
                'label': "Disabled Devices:",
                'var': "disabled_devices_text",
                'icon': "⚠️"
            },
        ]
        
        for item in config_items:
            self.create_config_item(card, item)
        
        # Add padding at bottom
        tk.Frame(card, bg=COLORS['bg_secondary'], height=SPACING['large']).pack()
        
    def create_config_item(self, parent, item):
        """Create a configuration item row"""
        item_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        item_frame.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['small'])
        
        # Inner padding
        inner_frame = tk.Frame(item_frame, bg=COLORS['bg_main'])
        inner_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
        # Icon
        icon_label = tk.Label(
            inner_frame,
            text=item['icon'],
            font=('SF Pro Display', 20),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # Text container
        text_frame = tk.Frame(inner_frame, bg=COLORS['bg_main'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Label
        label = tk.Label(
            text_frame,
            text=item['label'],
            font=get_font('caption'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        label.pack(anchor=tk.W)
        
        # Value
        value = tk.Label(
            text_frame,
            textvariable=getattr(self.controller, item['var'], tk.StringVar(value="Not available")),
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            anchor=tk.W,
            wraplength=700
        )
        value.pack(anchor=tk.W)
        
    def create_customization_card(self, parent):
        """Create customization options card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = tk.Label(
            card,
            text="Customization Options (Advanced)",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Note
        note_frame = tk.Frame(card, bg='#FFF3CD', relief=tk.FLAT, bd=0)
        note_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['medium']))
        
        note_content = tk.Frame(note_frame, bg='#FFF3CD')
        note_content.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['small'])
        
        note_label = tk.Label(
            note_content,
            text="💡 Most users don't need to customize these settings. The automatic configuration provides optimal compatibility.",
            font=get_font('small'),
            bg='#FFF3CD',
            fg='#856404',
            anchor=tk.W,
            wraplength=800
        )
        note_label.pack(anchor=tk.W)
        
        # Customization buttons
        button_container = tk.Frame(card, bg=COLORS['bg_secondary'])
        button_container.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        options = [
            {
                'title': 'Change macOS Version',
                'description': 'Select a different macOS version for your system',
                'command': self.controller.select_macos_version_gui
            },
            {
                'title': 'Customize ACPI Patches',
                'description': 'View and modify ACPI patches (for advanced users)',
                'command': self.controller.customize_acpi_gui
            },
            {
                'title': 'Customize Kernel Extensions',
                'description': 'Add or remove kexts (for advanced users)',
                'command': self.controller.customize_kexts_gui
            },
            {
                'title': 'Change SMBIOS Model',
                'description': 'Select a different Mac model identifier',
                'command': self.controller.customize_smbios_gui
            }
        ]
        
        for option in options:
            self.create_option_button(button_container, option)
    
    def create_option_button(self, parent, option):
        """Create a customization option button"""
        btn_frame = tk.Frame(
            parent, 
            bg=COLORS['bg_main'],
            relief=tk.FLAT, 
            bd=0,
            highlightbackground=COLORS['border_light'],
            highlightthickness=1
        )
        btn_frame.pack(fill=tk.X, pady=SPACING['small'])
        
        # Inner padding frame
        inner_frame = tk.Frame(btn_frame, bg=COLORS['bg_main'])
        inner_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
        # Text container
        text_frame = tk.Frame(inner_frame, bg=COLORS['bg_main'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Title button
        title_btn = tk.Button(
            text_frame,
            text=option['title'],
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            anchor=tk.W,
            command=option['command'],
            highlightthickness=0
        )
        title_btn.pack(anchor=tk.W)
        
        # Description
        desc_label = tk.Label(
            text_frame,
            text=option['description'],
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        desc_label.pack(anchor=tk.W)
        
        # Arrow
        arrow_label = tk.Label(
            inner_frame,
            text="→",
            font=('SF Pro Display', 16),
            bg=COLORS['bg_main'],
            fg=COLORS['primary']
        )
        arrow_label.pack(side=tk.RIGHT, padx=(SPACING['medium'], 0))
        
        # Hover effects
        def on_enter(e):
            title_btn.config(fg=COLORS['primary_hover'])
            arrow_label.config(fg=COLORS['primary_hover'])
            btn_frame.config(highlightbackground=COLORS['primary'], highlightthickness=2)
            
        def on_leave(e):
            title_btn.config(fg=COLORS['primary'])
            arrow_label.config(fg=COLORS['primary'])
            btn_frame.config(highlightbackground=COLORS['border_light'], highlightthickness=1)
        
        for widget in [title_btn, btn_frame, inner_frame, text_frame, desc_label, arrow_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
        
    def refresh(self):
        """Refresh the page content"""
        # This can be called when configuration changes
        pass
