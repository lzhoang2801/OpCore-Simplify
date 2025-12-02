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
        
        # Kext status card (new)
        self.create_kext_status_card(container)
        
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
        
    def create_kext_status_card(self, parent):
        """Create kext status card showing how many kexts will be applied"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header
        header_frame = tk.Frame(card, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        header = tk.Label(
            header_frame,
            text="🔧  Kernel Extensions (Kexts)",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Card content
        content_frame = tk.Frame(card, bg=COLORS['bg_main'])
        content_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        inner_frame = tk.Frame(content_frame, bg=COLORS['bg_main'])
        inner_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
        # Status icon and text
        status_container = tk.Frame(inner_frame, bg=COLORS['bg_main'])
        status_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Icon
        icon_label = tk.Label(
            status_container,
            text="📦",
            font=('SF Pro Display', 24),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # Text container
        text_frame = tk.Frame(status_container, bg=COLORS['bg_main'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Kext status label
        self.kext_status_label = tk.Label(
            text_frame,
            text="Kexts will be automatically selected before build",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        self.kext_status_label.pack(anchor=tk.W)
        
        # Kext count label (initially hidden)
        self.kext_count_label = tk.Label(
            text_frame,
            text="",
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary'],
            anchor=tk.W
        )
        self.kext_count_label.pack(anchor=tk.W)
        
        # Check kexts button
        check_btn = tk.Button(
            inner_frame,
            text="Check Kexts",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            command=self.check_kexts,
            highlightthickness=0
        )
        check_btn.pack(side=tk.RIGHT, padx=SPACING['small'])
        
        # View kexts button (initially hidden)
        self.view_kexts_btn = tk.Button(
            inner_frame,
            text="View Details",
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            command=self.controller.customize_kexts_gui,
            highlightthickness=0
        )
        # Don't pack yet, will be shown after check
        
        # Hover effects
        def on_check_enter(e):
            check_btn.config(bg=COLORS['primary_hover'])
        def on_check_leave(e):
            check_btn.config(bg=COLORS['primary'])
        def on_view_enter(e):
            self.view_kexts_btn.config(bg=COLORS['border_light'])
        def on_view_leave(e):
            self.view_kexts_btn.config(bg=COLORS['bg_hover'])
        
        check_btn.bind('<Enter>', on_check_enter)
        check_btn.bind('<Leave>', on_check_leave)
        self.view_kexts_btn.bind('<Enter>', on_view_enter)
        self.view_kexts_btn.bind('<Leave>', on_view_leave)
    
    def check_kexts(self):
        """Check how many kexts will be applied"""
        if not self.controller.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
        
        try:
            # Ensure kexts have been selected
            self.controller.ensure_kexts_selected()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select kexts: {str(e)}")
            return
        
        try:
            # Count the kexts
            required_kexts = []
            optional_kexts = []
            
            if hasattr(self.controller.ocpe.k, 'kexts') and self.controller.ocpe.k.kexts:
                required_kexts = [k for k in self.controller.ocpe.k.kexts if k.checked and k.required]
                optional_kexts = [k for k in self.controller.ocpe.k.kexts if k.checked and not k.required]
            
            total_kexts = len(required_kexts) + len(optional_kexts)
            
            # Update the status labels
            if total_kexts > 0:
                self.kext_status_label.config(
                    text=f"✅  Kexts have been analyzed and selected",
                    fg=COLORS['success']
                )
                self.kext_count_label.config(
                    text=f"Total: {total_kexts} kexts ({len(required_kexts)} required, {len(optional_kexts)} optional)"
                )
                
                # Show the view button
                if not self.view_kexts_btn.winfo_ismapped():
                    self.view_kexts_btn.pack(side=tk.RIGHT, padx=SPACING['small'])
            else:
                self.kext_status_label.config(
                    text="⚠️  No kexts were selected",
                    fg=COLORS['warning']
                )
                self.kext_count_label.config(text="")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to count kexts: {str(e)}")
        
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
                'icon': '🍎',
                'title': 'Change macOS Version',
                'description': 'Select a different macOS version for your system',
                'command': self.controller.select_macos_version_gui
            },
            {
                'icon': '📝',
                'title': 'Customize ACPI Patches',
                'description': 'View and modify ACPI patches (for advanced users)',
                'command': self.controller.customize_acpi_gui
            },
            {
                'icon': '🔧',
                'title': 'Customize Kernel Extensions',
                'description': 'Add or remove kexts (for advanced users)',
                'command': self.controller.customize_kexts_gui
            },
            {
                'icon': '💻',
                'title': 'Change SMBIOS Model',
                'description': 'Select a different Mac model identifier',
                'command': self.controller.customize_smbios_gui
            }
        ]
        
        for option in options:
            self.create_option_button(button_container, option)
    
    def create_option_button(self, parent, option):
        """Create a customization option button matching upload page style"""
        btn_frame = tk.Frame(
            parent, 
            bg=COLORS['bg_main'],
            relief=tk.FLAT, 
            bd=0,
            highlightbackground=COLORS['border_light'],
            highlightthickness=1
        )
        btn_frame.pack(fill=tk.X, pady=SPACING['small'])
        
        # Make entire frame clickable
        btn_frame.bind('<Button-1>', lambda e: option['command']())
        btn_frame.config(cursor='hand2')
        
        # Inner padding frame
        inner_frame = tk.Frame(btn_frame, bg=COLORS['bg_main'])
        inner_frame.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        inner_frame.bind('<Button-1>', lambda e: option['command']())
        inner_frame.config(cursor='hand2')
        
        # Icon (using emoji)
        icon_label = tk.Label(
            inner_frame,
            text=option.get('icon', '⚙️'),
            font=('SF Pro Display', 32),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, SPACING['large']))
        icon_label.bind('<Button-1>', lambda e: option['command']())
        icon_label.config(cursor='hand2')
        
        # Text container
        text_frame = tk.Frame(inner_frame, bg=COLORS['bg_main'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_frame.bind('<Button-1>', lambda e: option['command']())
        text_frame.config(cursor='hand2')
        
        # Title
        title_label = tk.Label(
            text_frame,
            text=option['title'],
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        title_label.pack(anchor=tk.W)
        title_label.bind('<Button-1>', lambda e: option['command']())
        title_label.config(cursor='hand2')
        
        # Description
        desc_label = tk.Label(
            text_frame,
            text=option['description'],
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            anchor=tk.W,
            wraplength=500
        )
        desc_label.pack(anchor=tk.W)
        desc_label.bind('<Button-1>', lambda e: option['command']())
        desc_label.config(cursor='hand2')
        
        # Hover effects
        def on_enter(e):
            btn_frame.config(highlightbackground=COLORS['primary'], highlightthickness=2)
            
        def on_leave(e):
            btn_frame.config(highlightbackground=COLORS['border_light'], highlightthickness=1)
        
        for widget in [btn_frame, inner_frame, icon_label, text_frame, title_label, desc_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
        
    def refresh(self):
        """Refresh the page content"""
        # This can be called when configuration changes
        pass
