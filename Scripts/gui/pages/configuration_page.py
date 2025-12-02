"""
Configuration page for hardware report and macOS version selection
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from ..styles import COLORS, SPACING, FONTS, get_font


class ConfigurationPage(tk.Frame):
    """Configuration page for hardware report and initial setup"""
    
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
        
        # Title section
        title_label = tk.Label(
            container,
            text="Configuration",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Configure your hardware and preferences to build an OpenCore EFI",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Current Configuration Card
        self.create_config_card(container)
        
        # Actions Card
        self.create_actions_card(container)
        
        # Instructions Card
        self.create_instructions_card(container)
        
    def create_config_card(self, parent):
        """Create current configuration display card with macOS styling"""
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
            ("Hardware Report:", "hardware_report_path"),
            ("macOS Version:", "macos_version"),
            ("SMBIOS Model:", "smbios_model"),
            ("Disabled Devices:", "disabled_devices_text"),
        ]
        
        for label_text, var_name in config_items:
            item_frame = tk.Frame(card, bg=COLORS['bg_secondary'])
            item_frame.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['small'])
            
            label = tk.Label(
                item_frame,
                text=label_text,
                font=get_font('body_bold'),
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_secondary'],
                width=18,
                anchor=tk.W
            )
            label.pack(side=tk.LEFT)
            
            value = tk.Label(
                item_frame,
                textvariable=getattr(self.controller, var_name),
                font=get_font('body'),
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_primary'],
                anchor=tk.W,
                wraplength=500
            )
            value.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add padding at bottom
        tk.Frame(card, bg=COLORS['bg_secondary'], height=SPACING['large']).pack()
        
    def create_actions_card(self, parent):
        """Create action buttons card with macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header
        header = tk.Label(
            card,
            text="Quick Actions",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Button container
        button_container = tk.Frame(card, bg=COLORS['bg_secondary'])
        button_container.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Action buttons with descriptions
        actions = [
            {
                'number': '1',
                'title': 'Select Hardware Report',
                'description': 'Load hardware report and run compatibility checker',
                'command': self.controller.select_hardware_report_gui
            },
            {
                'number': '2',
                'title': 'Select macOS Version',
                'description': 'Choose the macOS version you want to install',
                'command': self.controller.select_macos_version_gui
            },
            {
                'number': '3',
                'title': 'Customize SMBIOS Model',
                'description': 'Select the appropriate Mac model for your hardware',
                'command': self.controller.customize_smbios_gui
            }
        ]
        
        for action in actions:
            self.create_action_button(button_container, action)
            
    def create_action_button(self, parent, action):
        """Create an action button with description and enhanced macOS styling"""
        btn_frame = tk.Frame(parent, bg=COLORS['bg_main'], relief=tk.FLAT, bd=0, 
                            highlightbackground=COLORS['border_light'], highlightthickness=1)
        btn_frame.pack(fill=tk.X, pady=SPACING['small'])
        
        # Inner padding frame
        inner_frame = tk.Frame(btn_frame, bg=COLORS['bg_main'])
        inner_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
        # Number badge with modern macOS styling
        number_frame = tk.Frame(
            inner_frame,
            bg=COLORS['primary'],
            width=36,
            height=36
        )
        number_frame.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        number_frame.pack_propagate(False)
        
        number_label = tk.Label(
            number_frame,
            text=action['number'],
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF'
        )
        number_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Text container
        text_frame = tk.Frame(inner_frame, bg=COLORS['bg_main'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title button
        title_btn = tk.Button(
            text_frame,
            text=action['title'],
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            anchor=tk.W,
            command=action['command'],
            highlightthickness=0
        )
        title_btn.pack(anchor=tk.W)
        
        # Description
        desc_label = tk.Label(
            text_frame,
            text=action['description'],
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        desc_label.pack(anchor=tk.W)
        
        # Enhanced macOS-style hover effects with smooth transition
        def on_enter(e):
            title_btn.config(fg=COLORS['primary_hover'])
            btn_frame.config(highlightbackground=COLORS['primary'], highlightthickness=2)
            number_frame.config(bg=COLORS['primary_hover'])
            number_label.config(bg=COLORS['primary_hover'])
            
        def on_leave(e):
            title_btn.config(fg=COLORS['primary'])
            btn_frame.config(highlightbackground=COLORS['border_light'], highlightthickness=1)
            number_frame.config(bg=COLORS['primary'])
            number_label.config(bg=COLORS['primary'])
            
        # Bind to all interactive elements
        for widget in [title_btn, btn_frame, inner_frame, number_frame, number_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
        
    def create_instructions_card(self, parent):
        """Create instructions card with macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = tk.Label(
            card,
            text="Getting Started",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Instructions text
        instructions = """Welcome to OpCore Simplify!

Follow these simple steps to build your OpenCore EFI:

1. Select Hardware Report
   • Load a hardware report JSON file, or
   • Export one using Hardware Sniffer (Windows only)
   • The tool will automatically validate, load ACPI tables,
     run compatibility checks, and select optimal settings

2. Review Compatibility
   • Check the Compatibility page for device support status
   • Note any devices requiring OpenCore Legacy Patcher

3. Customize (Optional)
   • Adjust macOS version, ACPI patches, kexts, or SMBIOS model
   • Most users can skip this step

4. Build EFI
   • Navigate to Build EFI page and click "Build OpenCore EFI"
   • Follow the USB mapping instructions before use

For detailed guides, visit: https://dortania.github.io/OpenCore-Install-Guide/"""
        
        text_widget = tk.Text(
            card,
            wrap=tk.WORD,
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['large'],
            pady=SPACING['medium'],
            height=18
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        text_widget.insert('1.0', instructions)
        text_widget.config(state=tk.DISABLED)
        
    def refresh(self):
        """Refresh the page content"""
        # This can be called when configuration changes
        pass
