"""
Customization page for ACPI patches and Kexts configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..styles import COLORS, SPACING, get_font


class CustomizationPage(tk.Frame):
    """Customization page for advanced ACPI and Kext settings"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize customization page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the customization page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Title section
        title_label = tk.Label(
            container,
            text="Advanced Customization",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Fine-tune ACPI patches and kernel extensions for your system",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Warning banner
        self.create_warning_banner(container)
        
        # ACPI Patches Card
        self.create_acpi_card(container)
        
        # Kexts Card
        self.create_kexts_card(container)
        
        # Information Card
        self.create_info_card(container)
        
    def create_warning_banner(self, parent):
        """Create warning banner for advanced users"""
        banner = tk.Frame(parent, bg=COLORS['warning'], relief=tk.FLAT, bd=0)
        banner.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        icon_label = tk.Label(
            banner,
            text="⚠️",
            font=get_font('heading'),
            bg=COLORS['warning'],
            fg='#FFFFFF'
        )
        icon_label.pack(side=tk.LEFT, padx=SPACING['medium'], pady=SPACING['medium'])
        
        text_frame = tk.Frame(banner, bg=COLORS['warning'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=SPACING['medium'])
        
        title = tk.Label(
            text_frame,
            text="Advanced Settings",
            font=get_font('body_bold'),
            bg=COLORS['warning'],
            fg='#FFFFFF',
            anchor=tk.W
        )
        title.pack(anchor=tk.W)
        
        description = tk.Label(
            text_frame,
            text="These settings are automatically configured. Only modify if you know what you're doing.",
            font=get_font('small'),
            bg=COLORS['warning'],
            fg='#FFFFFF',
            anchor=tk.W,
            wraplength=600
        )
        description.pack(anchor=tk.W, pady=(2, 0))
        
        # Padding on right
        tk.Frame(banner, bg=COLORS['warning'], width=SPACING['medium']).pack(side=tk.RIGHT)
        
    def create_acpi_card(self, parent):
        """Create ACPI patches customization card"""
        card = tk.Frame(parent, bg=COLORS['bg_sidebar'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header with icon
        header_frame = tk.Frame(card, bg=COLORS['bg_sidebar'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        icon = tk.Label(
            header_frame,
            text="⚡",
            font=get_font('heading'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['primary']
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['small']))
        
        header = tk.Label(
            header_frame,
            text="ACPI Patches",
            font=get_font('heading'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Description
        desc = tk.Label(
            card,
            text="ACPI patches are automatically selected based on your hardware configuration.\nThese patches fix compatibility issues and enable proper hardware support.",
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_secondary'],
            justify=tk.LEFT,
            anchor=tk.W
        )
        desc.pack(anchor=tk.W, padx=SPACING['large'], pady=(0, SPACING['medium']))
        
        # Button frame
        button_frame = tk.Frame(card, bg=COLORS['bg_sidebar'])
        button_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Customize button
        customize_btn = tk.Button(
            button_frame,
            text="Customize ACPI Patches",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['medium'],
            command=self.controller.customize_acpi_gui
        )
        customize_btn.pack(side=tk.LEFT)
        
        # Hover effect
        def on_enter(e):
            customize_btn.config(bg=COLORS['primary_dark'])
            
        def on_leave(e):
            customize_btn.config(bg=COLORS['primary'])
            
        customize_btn.bind('<Enter>', on_enter)
        customize_btn.bind('<Leave>', on_leave)
        
    def create_kexts_card(self, parent):
        """Create Kexts customization card"""
        card = tk.Frame(parent, bg=COLORS['bg_sidebar'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header with icon
        header_frame = tk.Frame(card, bg=COLORS['bg_sidebar'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        icon = tk.Label(
            header_frame,
            text="🔌",
            font=get_font('heading'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['primary']
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['small']))
        
        header = tk.Label(
            header_frame,
            text="Kernel Extensions (Kexts)",
            font=get_font('heading'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Description
        desc = tk.Label(
            card,
            text="Kexts provide essential drivers for your hardware.\nThe tool automatically selects required kexts based on your configuration.",
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_secondary'],
            justify=tk.LEFT,
            anchor=tk.W
        )
        desc.pack(anchor=tk.W, padx=SPACING['large'], pady=(0, SPACING['medium']))
        
        # Button frame
        button_frame = tk.Frame(card, bg=COLORS['bg_sidebar'])
        button_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Customize button
        customize_btn = tk.Button(
            button_frame,
            text="Customize Kexts",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['medium'],
            command=self.controller.customize_kexts_gui
        )
        customize_btn.pack(side=tk.LEFT)
        
        # Hover effect
        def on_enter(e):
            customize_btn.config(bg=COLORS['primary_dark'])
            
        def on_leave(e):
            customize_btn.config(bg=COLORS['primary'])
            
        customize_btn.bind('<Enter>', on_enter)
        customize_btn.bind('<Leave>', on_leave)
        
    def create_info_card(self, parent):
        """Create information card"""
        card = tk.Frame(parent, bg=COLORS['bg_sidebar'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header_frame = tk.Frame(card, bg=COLORS['bg_sidebar'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        icon = tk.Label(
            header_frame,
            text="ℹ️",
            font=get_font('heading'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['info']
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['small']))
        
        header = tk.Label(
            header_frame,
            text="About Customization",
            font=get_font('heading'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Information text
        info_text = """What are ACPI Patches?

ACPI (Advanced Configuration and Power Interface) patches modify your system's 
firmware tables to fix compatibility issues with macOS. Common patches include:

• Fake EC: Creates a fake embedded controller for systems without one
• PLUG: Enables CPU power management
• Fix HPET: Resolves timer conflicts
• RTC AWAC: Fixes real-time clock issues on 300+ series motherboards

What are Kexts?

Kernel Extensions (kexts) are macOS drivers that enable hardware support:

• Lilu: Patching framework required by most other kexts
• WhateverGreen: GPU support and fixes
• AppleALC: Audio support
• IntelMausi/RealtekRTL8111: Ethernet support
• VirtualSMC: System monitoring and SMC emulation

Should You Customize?

Most users should stick with automatic configuration. Only customize if:
• You have specific hardware requirements
• You're troubleshooting issues
• You're an advanced user testing different configurations

The CLI version offers more detailed customization options for expert users."""
        
        text_widget = tk.Text(
            card,
            wrap=tk.WORD,
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['large'],
            pady=SPACING['medium']
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        text_widget.insert('1.0', info_text)
        text_widget.config(state=tk.DISABLED)
        
    def refresh(self):
        """Refresh the page content"""
        pass
