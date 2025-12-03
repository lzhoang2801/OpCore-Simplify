"""
Step 1: Upload hardware report and ACPI tables
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from ..styles import COLORS, SPACING, FONTS, get_font
from ..icons import Icons


class UploadPage(tk.Frame):
    """Step 1: Upload hardware report and ACPI tables"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize upload page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the upload page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Step indicator
        step_label = tk.Label(
            container,
            text="STEP 1 OF 4",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary']
        )
        step_label.pack(anchor=tk.W, pady=(0, SPACING['tiny']))
        
        # Title section
        title_label = tk.Label(
            container,
            text="Upload Hardware Report",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Start by loading your system hardware information",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Upload methods card
        self.create_upload_card(container)
        
        # Current status card
        self.create_status_card(container)
        
        # Instructions card
        self.create_instructions_card(container)
        
    def create_upload_card(self, parent):
        """Create upload methods card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header
        header = tk.Label(
            card,
            text="Choose Upload Method",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Button container
        button_container = tk.Frame(card, bg=COLORS['bg_secondary'])
        button_container.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Upload options
        self.create_upload_option(
            button_container,
            icon="📂",
            title="Select Existing Hardware Report",
            description="Choose a Report.json file that was previously exported",
            command=self.select_existing_report,
            primary=True
        )
        
        # Only show export option on Windows
        if os.name == 'nt':
            self.create_upload_option(
                button_container,
                icon="🔍",
                title="Export New Hardware Report",
                description="Use Hardware Sniffer to scan this computer and create a new report",
                command=self.export_new_report,
                primary=False
            )
        
    def create_upload_option(self, parent, icon, title, description, command, primary=False):
        """Create an upload option button"""
        btn_frame = tk.Frame(
            parent, 
            bg=COLORS['primary'] if primary else COLORS['bg_main'],
            relief=tk.FLAT, 
            bd=0,
            highlightbackground=COLORS['primary'] if primary else COLORS['border_light'],
            highlightthickness=2 if primary else 1
        )
        btn_frame.pack(fill=tk.X, pady=SPACING['small'])
        
        # Make entire frame clickable
        btn_frame.bind('<Button-1>', lambda e: command())
        btn_frame.config(cursor='hand2')
        
        # Inner padding frame
        inner_frame = tk.Frame(btn_frame, bg=COLORS['primary'] if primary else COLORS['bg_main'])
        inner_frame.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        inner_frame.bind('<Button-1>', lambda e: command())
        inner_frame.config(cursor='hand2')
        
        # Icon
        icon_label = tk.Label(
            inner_frame,
            text=icon,
            font=('SF Pro Display', 32),
            bg=COLORS['primary'] if primary else COLORS['bg_main'],
            fg='#FFFFFF' if primary else COLORS['text_primary']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, SPACING['large']))
        icon_label.bind('<Button-1>', lambda e: command())
        icon_label.config(cursor='hand2')
        
        # Text container
        text_frame = tk.Frame(inner_frame, bg=COLORS['primary'] if primary else COLORS['bg_main'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_frame.bind('<Button-1>', lambda e: command())
        text_frame.config(cursor='hand2')
        
        # Title
        title_label = tk.Label(
            text_frame,
            text=title,
            font=get_font('body_bold'),
            bg=COLORS['primary'] if primary else COLORS['bg_main'],
            fg='#FFFFFF' if primary else COLORS['text_primary'],
            anchor=tk.W
        )
        title_label.pack(anchor=tk.W)
        title_label.bind('<Button-1>', lambda e: command())
        title_label.config(cursor='hand2')
        
        # Description
        desc_label = tk.Label(
            text_frame,
            text=description,
            font=get_font('small'),
            bg=COLORS['primary'] if primary else COLORS['bg_main'],
            fg='#FFFFFF' if primary else COLORS['text_secondary'],
            anchor=tk.W,
            wraplength=500
        )
        desc_label.pack(anchor=tk.W)
        desc_label.bind('<Button-1>', lambda e: command())
        desc_label.config(cursor='hand2')
        
        # Hover effects
        def on_enter(e):
            if primary:
                btn_frame.config(bg=COLORS['primary_hover'], highlightbackground=COLORS['primary_dark'])
                inner_frame.config(bg=COLORS['primary_hover'])
                icon_label.config(bg=COLORS['primary_hover'])
                text_frame.config(bg=COLORS['primary_hover'])
                title_label.config(bg=COLORS['primary_hover'])
                desc_label.config(bg=COLORS['primary_hover'])
            else:
                btn_frame.config(highlightbackground=COLORS['primary'], highlightthickness=2)
            
        def on_leave(e):
            if primary:
                btn_frame.config(bg=COLORS['primary'], highlightbackground=COLORS['primary'])
                inner_frame.config(bg=COLORS['primary'])
                icon_label.config(bg=COLORS['primary'])
                text_frame.config(bg=COLORS['primary'])
                title_label.config(bg=COLORS['primary'])
                desc_label.config(bg=COLORS['primary'])
            else:
                btn_frame.config(highlightbackground=COLORS['border_light'], highlightthickness=1)
        
        for widget in [btn_frame, inner_frame, icon_label, text_frame, title_label, desc_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
    
    def create_status_card(self, parent):
        """Create current status card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card header
        header = tk.Label(
            card,
            text="Current Status",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Status row
        status_frame = tk.Frame(card, bg=COLORS['bg_secondary'])
        status_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Status icon and text
        self.status_icon = tk.Label(
            status_frame,
            text="⏳",
            font=('SF Pro Display', 24),
            bg=COLORS['bg_secondary']
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        text_container = tk.Frame(status_frame, bg=COLORS['bg_secondary'])
        text_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_label = tk.Label(
            text_container,
            text="Waiting for hardware report",
            font=get_font('body_bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        self.status_label.pack(anchor=tk.W)
        
        self.status_detail = tk.Label(
            text_container,
            textvariable=self.controller.hardware_report_path,
            font=get_font('small'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        self.status_detail.pack(anchor=tk.W)
    
    def create_instructions_card(self, parent):
        """Create instructions card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = tk.Label(
            card,
            text="How to Get Hardware Report",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        # Instructions
        instructions = """📋 For Windows Users:

1. Download Hardware Sniffer from the GitHub releases page
2. Run Hardware Sniffer as Administrator
3. Click "Export Hardware Report"
4. Find Report.json in the SysReport folder
5. Upload the Report.json file here

OR use the "Export New Hardware Report" button above


🍎 For macOS/Linux Users:

1. Use a Windows machine or Windows PE environment
2. Run Hardware Sniffer to generate the report
3. Transfer the Report.json file to this machine
4. Upload it using the button above


💡 What Happens Next:

After uploading your hardware report:
• ACPI tables will be automatically loaded
• Compatibility checker will analyze your hardware
• Optimal macOS version will be selected
• Required kexts and patches will be configured
• You'll be guided through any necessary choices"""
        
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
            height=22
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        text_widget.insert('1.0', instructions)
        text_widget.config(state=tk.DISABLED)
    
    def select_existing_report(self):
        """Handle selecting existing hardware report"""
        filename = filedialog.askopenfilename(
            title="Select Hardware Report",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            # Update status
            self.status_icon.config(text="⏳")
            self.status_label.config(text="Loading hardware report...")
            self.status_detail.config(text=os.path.basename(filename))
            
            # Load the report (this will trigger compatibility check and auto-configuration)
            self.controller.load_hardware_report(filename)
    
    def export_new_report(self):
        """Handle exporting new hardware report"""
        self.status_icon.config(text="⏳")
        self.status_label.config(text="Exporting hardware report...")
        self.status_detail.config(text="Running Hardware Sniffer...")
        
        # Export the report
        self.controller.export_hardware_report()
    
    def update_status(self, success=False, message="", detail=""):
        """Update the status display"""
        if success:
            self.status_icon.config(text="✅")
            self.status_label.config(text=message or "Hardware report loaded successfully")
        else:
            self.status_icon.config(text="⏳")
            self.status_label.config(text=message or "Waiting for hardware report")
        
        if detail:
            self.status_detail.config(text=detail)
        
    def refresh(self):
        """Refresh the page content"""
        # Update status based on current state
        if self.controller.hardware_report:
            self.update_status(
                success=True,
                message="Hardware report loaded",
                detail=self.controller.hardware_report_path.get()
            )
        else:
            self.update_status(
                success=False,
                message="Waiting for hardware report",
                detail="Not selected"
            )
