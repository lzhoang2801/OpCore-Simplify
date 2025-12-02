"""
Build page for OpenCore EFI building
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os

from ..styles import COLORS, SPACING, get_font
from ..icons import Icons


class BuildPage(tk.Frame):
    """Build page for creating OpenCore EFI"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize build page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the build page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Title section
        title_label = tk.Label(
            container,
            text="Build OpenCore EFI",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Create your customized OpenCore bootloader",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Build controls card
        self.create_build_controls(container)
        
        # Progress section
        self.create_progress_section(container)
        
        # Build log section
        self.create_log_section(container)
        
        # Result actions
        self.create_result_actions(container)
        
    def create_build_controls(self, parent):
        """Create build control buttons with enhanced macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        # Card content with padding
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Build button (large and prominent with enhanced macOS styling)
        button_container = tk.Frame(content, bg=COLORS['bg_secondary'])
        button_container.pack(side=tk.LEFT)
        
        self.controller.build_btn = tk.Button(
            button_container,
            text="🔨  Build OpenCore EFI",
            font=get_font('heading'),
            bg=COLORS['success'],
            fg='#FFFFFF',
            activebackground='#28A745',
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xxlarge'],
            pady=SPACING['medium'],
            command=self.controller.build_efi_gui,
            highlightthickness=0
        )
        self.controller.build_btn.pack()
        
        # Status text next to button with improved layout
        status_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        status_frame.pack(side=tk.LEFT, padx=SPACING['large'], fill=tk.X, expand=True)
        
        status_title = tk.Label(
            status_frame,
            text="Ready to Build",
            font=get_font('body_bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        status_title.pack(anchor=tk.W)
        
        status_text = tk.Label(
            status_frame,
            text="Ensure your hardware report and configuration are complete before building.",
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.W,
            wraplength=400
        )
        status_text.pack(anchor=tk.W)
        
        # Enhanced macOS-style hover effect for build button
        def on_enter(e):
            if self.controller.build_btn['state'] != tk.DISABLED:
                self.controller.build_btn.config(bg='#34C759')
            
        def on_leave(e):
            if self.controller.build_btn['state'] != tk.DISABLED:
                self.controller.build_btn.config(bg=COLORS['success'])
            
        self.controller.build_btn.bind('<Enter>', on_enter)
        self.controller.build_btn.bind('<Leave>', on_leave)
        
    def create_progress_section(self, parent):
        """Create progress bar and status with macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Progress label
        progress_label = tk.Label(
            content,
            text="Build Progress",
            font=get_font('body_bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        progress_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        # Progress bar
        self.controller.progress_var = tk.DoubleVar()
        
        # Custom styled progress bar with macOS appearance
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS['border_light'],
            background=COLORS['primary'],
            bordercolor=COLORS['border_light'],
            lightcolor=COLORS['primary'],
            darkcolor=COLORS['primary'],
            thickness=8
        )
        
        self.controller.progress_bar = ttk.Progressbar(
            content,
            variable=self.controller.progress_var,
            maximum=100,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.controller.progress_bar.pack(fill=tk.X, pady=(0, SPACING['small']))
        
        # Progress percentage label
        self.progress_percent = tk.Label(
            content,
            text="0%",
            font=get_font('small'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.E
        )
        self.progress_percent.pack(anchor=tk.E)
        
        # Update percentage when progress changes
        def update_percent(*args):
            value = self.controller.progress_var.get()
            self.progress_percent.config(text=f"{int(value)}%")
        
        self.controller.progress_var.trace('w', update_percent)
        
    def create_log_section(self, parent):
        """Create build log viewer with macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, SPACING['large']))
        
        # Header
        header_frame = tk.Frame(card, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        header = tk.Label(
            header_frame,
            text="📝  Build Log",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Clear log button with macOS styling
        clear_btn = tk.Button(
            header_frame,
            text="Clear",
            font=get_font('body'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['medium'],
            pady=SPACING['small'],
            command=self.clear_log,
            highlightthickness=0
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # Hover effect for clear button
        def on_clear_enter(e):
            clear_btn.config(bg=COLORS['bg_hover'])
        def on_clear_leave(e):
            clear_btn.config(bg=COLORS['bg_secondary'])
        clear_btn.bind('<Enter>', on_clear_enter)
        clear_btn.bind('<Leave>', on_clear_leave)
        
        # Log text area
        log_frame = tk.Frame(card, bg=COLORS['bg_main'], highlightbackground=COLORS['border_light'], highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        self.controller.build_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9) if os.name == 'nt' else ('Monaco', 10),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['medium'],
            pady=SPACING['medium']
        )
        self.controller.build_log.pack(fill=tk.BOTH, expand=True)
        
    def create_result_actions(self, parent):
        """Create action buttons for after build with macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Open result folder button
        self.controller.open_result_btn = tk.Button(
            content,
            text=Icons.format_with_text("folder", "Open EFI Folder"),
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            state=tk.DISABLED,
            command=self.controller.open_result_folder,
            highlightthickness=0
        )
        self.controller.open_result_btn.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # View instructions button
        instructions_btn = tk.Button(
            content,
            text=Icons.format_with_text("book", "View Instructions"),
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            command=self.show_instructions,
            highlightthickness=0
        )
        instructions_btn.pack(side=tk.LEFT)
        
        # macOS-style hover effects
        def on_result_enter(e):
            if self.controller.open_result_btn['state'] != tk.DISABLED:
                self.controller.open_result_btn.config(bg=COLORS['primary_hover'])
            
        def on_result_leave(e):
            if self.controller.open_result_btn['state'] != tk.DISABLED:
                self.controller.open_result_btn.config(bg=COLORS['primary'])
                
        def on_inst_enter(e):
            instructions_btn.config(bg=COLORS['bg_hover'])
            
        def on_inst_leave(e):
            instructions_btn.config(bg=COLORS['bg_hover'])
            
        self.controller.open_result_btn.bind('<Enter>', on_result_enter)
        self.controller.open_result_btn.bind('<Leave>', on_result_leave)
        instructions_btn.bind('<Enter>', on_inst_enter)
        instructions_btn.bind('<Leave>', on_inst_leave)
        
    def clear_log(self):
        """Clear the build log"""
        self.controller.build_log.delete('1.0', tk.END)
        
    def show_instructions(self):
        """Show build instructions"""
        instructions = """OpenCore EFI Build Instructions

After building your EFI, follow these steps:

1. USB Mapping (Required):
   • Download USBToolBox from GitHub
   • Run the tool and map your USB ports
   • Place the generated UTBMap.kext in EFI/OC/Kexts
   • Delete UTBDefault.kext from EFI/OC/Kexts
   • Use ProperTree to snapshot your config.plist (Cmd/Ctrl+R)

2. BIOS/UEFI Settings:
   • Enable UEFI boot mode
   • Disable Secure Boot
   • Disable CSM/Legacy
   • Enable Above 4G Decoding (if available)
   • Disable Resizable BAR (if available)

3. Create macOS Installer:
   • Windows: Use UnPlugged or gibMacOS
   • macOS: Use diskutil and createinstallmedia
   • Copy your EFI folder to the installer's EFI partition

4. Installation:
   • Boot from USB installer
   • Install macOS
   • Copy EFI to system drive after installation

For detailed troubleshooting:
https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/"""

        # Create info window
        info_window = tk.Toplevel(self.controller.root)
        info_window.title("Build Instructions")
        info_window.geometry("700x600")
        info_window.configure(bg=COLORS['bg_main'])
        
        # Title
        title = tk.Label(
            info_window,
            text=Icons.format_with_text("book", "Build Instructions"),
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title.pack(pady=SPACING['large'])
        
        # Text widget
        text_widget = scrolledtext.ScrolledText(
            info_window,
            wrap=tk.WORD,
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['large'],
            pady=SPACING['medium']
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        text_widget.insert('1.0', instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(
            info_window,
            text="Close",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['medium'],
            command=info_window.destroy
        )
        close_btn.pack(pady=SPACING['large'])
        
    def refresh(self):
        """Refresh the page content"""
        pass
