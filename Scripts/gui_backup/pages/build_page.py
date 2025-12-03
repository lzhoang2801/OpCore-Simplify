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
        
        # Step indicator
        step_label = tk.Label(
            container,
            text="STEP 4 OF 4",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary']
        )
        step_label.pack(anchor=tk.W, pady=(0, SPACING['tiny']))
        
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
        
        # Build instruction header
        instruction_label = tk.Label(
            content,
            text="Ready to Build Your OpenCore EFI",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        instruction_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        instruction_desc = tk.Label(
            content,
            text="Click the button below to start building your customized OpenCore bootloader. "
                 "This process will download necessary files and configure your EFI.",
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.W,
            wraplength=1000,
            justify=tk.LEFT
        )
        instruction_desc.pack(anchor=tk.W, pady=(0, SPACING['medium']))
        
        # Build button container with centered layout
        button_container = tk.Frame(content, bg=COLORS['bg_secondary'])
        button_container.pack(fill=tk.X, pady=(SPACING['medium'], 0))
        
        # Large prominent build button
        self.controller.build_btn = tk.Button(
            button_container,
            text="🔨  Build OpenCore EFI",
            font=get_font('title'),
            bg=COLORS['success'],
            fg='#FFFFFF',
            activebackground='#28A745',
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xxlarge']*2,
            pady=SPACING['large'],
            command=self.controller.build_efi_gui,
            highlightthickness=0
        )
        self.controller.build_btn.pack()
        
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
        
        # Header with icon
        header_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, SPACING['medium']))
        
        header = tk.Label(
            header_frame,
            text="⏳  Build Progress",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        header.pack(side=tk.LEFT)
        
        # Progress percentage label (moved to header for better visibility)
        self.progress_percent = tk.Label(
            header_frame,
            text="0%",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['primary'],
            anchor=tk.E
        )
        self.progress_percent.pack(side=tk.RIGHT)
        
        # Progress bar container with better styling
        progress_container = tk.Frame(content, bg=COLORS['bg_main'], 
                                      highlightbackground=COLORS['border_light'],
                                      highlightthickness=1)
        progress_container.pack(fill=tk.X, pady=(SPACING['small'], 0))
        
        # Progress bar frame with padding
        progress_frame = tk.Frame(progress_container, bg=COLORS['bg_main'])
        progress_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
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
            thickness=12
        )
        
        self.controller.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.controller.progress_var,
            maximum=100,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.controller.progress_bar.pack(fill=tk.X)
        
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
        
        # Header with icon
        header_container = tk.Frame(header_frame, bg=COLORS['bg_secondary'])
        header_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        header = tk.Label(
            header_container,
            text="📝  Build Log",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Clear log button with macOS styling
        clear_btn = tk.Button(
            header_frame,
            text="🗑️ Clear",
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
            clear_btn.config(bg=COLORS['border_light'])
        def on_clear_leave(e):
            clear_btn.config(bg=COLORS['bg_hover'])
        clear_btn.bind('<Enter>', on_clear_enter)
        clear_btn.bind('<Leave>', on_clear_leave)
        
        # Log text area with better styling
        log_frame = tk.Frame(card, bg=COLORS['bg_main'], 
                            highlightbackground=COLORS['border_light'], 
                            highlightthickness=2)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        self.controller.build_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 10) if os.name == 'nt' else ('Monaco', 11),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['medium'],
            pady=SPACING['medium'],
            insertbackground=COLORS['text_primary']
        )
        self.controller.build_log.pack(fill=tk.BOTH, expand=True)
        
    def create_result_actions(self, parent):
        """Create action buttons for after build with macOS styling"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Title
        title_label = tk.Label(
            content,
            text="Next Steps",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['medium']))
        
        # Buttons container
        buttons_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        buttons_frame.pack(fill=tk.X)
        
        # Open result folder button
        self.controller.open_result_btn = tk.Button(
            buttons_frame,
            text="📁  Open EFI Folder",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['medium'],
            state=tk.DISABLED,
            command=self.controller.open_result_folder,
            highlightthickness=0
        )
        self.controller.open_result_btn.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # View instructions button
        instructions_btn = tk.Button(
            buttons_frame,
            text="📖  View Installation Guide",
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['medium'],
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
            instructions_btn.config(bg=COLORS['border_light'])
            
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
