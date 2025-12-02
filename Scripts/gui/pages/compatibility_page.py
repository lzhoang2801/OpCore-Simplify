"""
Hardware compatibility checker page
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import time

from ..styles import COLORS, SPACING, get_font
from ..icons import Icons

# Import os_data at module level for efficiency
try:
    from Scripts.datasets import os_data
except ImportError:
    os_data = None


class CompatibilityPage(tk.Frame):
    """Hardware compatibility checking page"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize compatibility page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        self.compatibility_results = {}
        self.is_checking = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the compatibility page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Title section
        title_label = tk.Label(
            container,
            text="Hardware Compatibility Checker",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Verify your hardware compatibility with macOS",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Status card
        self.create_status_card(container)
        
        # Results section
        self.create_results_section(container)
        
        # Summary section
        self.create_summary_section(container)
        
    def create_status_card(self, parent):
        """Create status information card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Icon and status
        icon = tk.Label(
            content,
            text="🔍",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['info']
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        text_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_title = tk.Label(
            text_frame,
            text="Ready to Check Compatibility",
            font=get_font('body_bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        self.status_title.pack(anchor=tk.W)
        
        self.status_desc = tk.Label(
            text_frame,
            text="Load a hardware report to begin compatibility checking",
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        self.status_desc.pack(anchor=tk.W)
        
    def create_results_section(self, parent):
        """Create compatibility results display"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, SPACING['large']))
        
        # Header
        header_frame = tk.Frame(card, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        header = tk.Label(
            header_frame,
            text=Icons.format_with_text("chart", "Compatibility Results"),
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Results container with scrolling
        results_container = tk.Frame(card, bg=COLORS['bg_main'],
                                     highlightbackground=COLORS['border_light'], 
                                     highlightthickness=1)
        results_container.pack(fill=tk.BOTH, expand=True, 
                              padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Create canvas for scrolling
        canvas = tk.Canvas(results_container, bg=COLORS['bg_main'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=canvas.yview)
        self.results_frame = tk.Frame(canvas, bg=COLORS['bg_main'])
        
        self.results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial placeholder
        placeholder = tk.Label(
            self.results_frame,
            text="No compatibility check performed yet.\n\n"
                 "Load a hardware report from the Configuration page to see compatibility results.",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            justify=tk.CENTER
        )
        placeholder.pack(expand=True, pady=SPACING['xxlarge'])
        
    def create_summary_section(self, parent):
        """Create compatibility summary section"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Summary title
        header = tk.Label(
            content,
            text="📝  Summary",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, pady=(0, SPACING['medium']))
        
        # Summary stats frame
        stats_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        stats_frame.pack(fill=tk.X)
        
        # Compatible devices
        compatible_frame = tk.Frame(stats_frame, bg=COLORS['bg_main'],
                                   highlightbackground=COLORS['border_light'],
                                   highlightthickness=1)
        compatible_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                            padx=(0, SPACING['small']))
        
        compat_content = tk.Frame(compatible_frame, bg=COLORS['bg_main'])
        compat_content.pack(padx=SPACING['medium'], pady=SPACING['medium'])
        
        tk.Label(
            compat_content,
            text=Icons.get("check"),
            font=get_font('heading'),
            bg=COLORS['bg_main'],
            fg=COLORS['success']
        ).pack()
        
        self.compatible_count = tk.Label(
            compat_content,
            text="0",
            font=get_font('heading'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        self.compatible_count.pack()
        
        tk.Label(
            compat_content,
            text="Compatible",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        ).pack()
        
        # Incompatible devices
        incompatible_frame = tk.Frame(stats_frame, bg=COLORS['bg_main'],
                                      highlightbackground=COLORS['border_light'],
                                      highlightthickness=1)
        incompatible_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                               padx=(SPACING['small'], 0))
        
        incompat_content = tk.Frame(incompatible_frame, bg=COLORS['bg_main'])
        incompat_content.pack(padx=SPACING['medium'], pady=SPACING['medium'])
        
        tk.Label(
            incompat_content,
            text="⚠",
            font=get_font('heading'),
            bg=COLORS['bg_main'],
            fg=COLORS['warning']
        ).pack()
        
        self.incompatible_count = tk.Label(
            incompat_content,
            text="0",
            font=get_font('heading'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        self.incompatible_count.pack()
        
        tk.Label(
            incompat_content,
            text="Needs Attention",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        ).pack()
        
    def show_compatibility_results(self, hardware_report, native_versions, oclp_versions):
        """Display compatibility check results"""
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Update status
        self.status_title.config(text="Compatibility Check Complete")
        self.status_desc.config(text="Review the results below for detailed information")
        
        # Store results
        self.compatibility_results = {}
        compatible_count = 0
        incompatible_count = 0
        
        # Device types to check
        device_types = [
            ('CPU', 'Processor'),
            ('GPU', 'Graphics'),
            ('Sound', 'Audio'),
            ('Network', 'Network'),
            ('Bluetooth', 'Bluetooth'),
            ('Storage Controllers', 'Storage'),
            ('Biometric', 'Biometric'),
            ('SD Controller', 'SD Card')
        ]
        
        index = 0
        for device_type, display_name in device_types:
            if device_type not in hardware_report:
                continue
            
            index += 1
            devices = hardware_report[device_type]
            
            # Create device type section
            section_frame = tk.Frame(self.results_frame, bg=COLORS['bg_main'])
            section_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['small'])
            
            # Section header
            header_frame = tk.Frame(section_frame, bg=COLORS['bg_secondary'],
                                   highlightbackground=COLORS['border_light'],
                                   highlightthickness=1)
            header_frame.pack(fill=tk.X, pady=(0, SPACING['tiny']))
            
            header_content = tk.Frame(header_frame, bg=COLORS['bg_secondary'])
            header_content.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['small'])
            
            tk.Label(
                header_content,
                text=f"{index}. {display_name}",
                font=get_font('body_bold'),
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_primary'],
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            device_count = tk.Label(
                header_content,
                text=f"{len(devices)} device(s)",
                font=get_font('small'),
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_secondary']
            )
            device_count.pack(side=tk.RIGHT)
            
            # Device list
            for device_name, device_props in devices.items():
                self.create_device_card(section_frame, device_name, device_props)
                
                # Count compatibility
                compatibility = device_props.get('Compatibility', (None, None))
                if compatibility[0] and compatibility[1]:
                    compatible_count += 1
                else:
                    incompatible_count += 1
        
        # Update summary counts
        self.compatible_count.config(text=str(compatible_count))
        self.incompatible_count.config(text=str(incompatible_count))
        
    def create_device_card(self, parent, device_name, device_props):
        """Create a card for a single device"""
        card = tk.Frame(parent, bg=COLORS['bg_main'],
                       highlightbackground=COLORS['border_light'],
                       highlightthickness=1)
        card.pack(fill=tk.X, pady=SPACING['tiny'])
        
        content = tk.Frame(card, bg=COLORS['bg_main'])
        content.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['small'])
        
        # Device name and status
        top_frame = tk.Frame(content, bg=COLORS['bg_main'])
        top_frame.pack(fill=tk.X)
        
        # Status icon
        compatibility = device_props.get('Compatibility', (None, None))
        oclp_compat = device_props.get('OCLP Compatibility')
        
        if compatibility[0] and compatibility[1]:
            status_icon = Icons.get("check")
            status_color = COLORS['success']
            status_text = "Compatible"
        elif oclp_compat:
            status_icon = Icons.get("lightning")
            status_color = COLORS['warning']
            status_text = "Requires OCLP"
        else:
            status_icon = Icons.get("cross")
            status_color = COLORS['error']
            status_text = "Not Supported"
        
        tk.Label(
            top_frame,
            text=status_icon,
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=status_color
        ).pack(side=tk.LEFT, padx=(0, SPACING['small']))
        
        tk.Label(
            top_frame,
            text=device_name,
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            top_frame,
            text=status_text,
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=status_color
        ).pack(side=tk.RIGHT)
        
        # Device details
        details_frame = tk.Frame(content, bg=COLORS['bg_main'])
        details_frame.pack(fill=tk.X, pady=(SPACING['tiny'], 0))
        
        # Device type and ID
        if device_props.get('Device Type'):
            tk.Label(
                details_frame,
                text=f"Type: {device_props['Device Type']}",
                font=get_font('small'),
                bg=COLORS['bg_main'],
                fg=COLORS['text_secondary'],
                anchor=tk.W
            ).pack(anchor=tk.W)
        
        if device_props.get('Device ID'):
            tk.Label(
                details_frame,
                text=f"ID: {device_props['Device ID']}",
                font=get_font('small'),
                bg=COLORS['bg_main'],
                fg=COLORS['text_secondary'],
                anchor=tk.W
            ).pack(anchor=tk.W)
        
        # macOS version support
        if compatibility[0] and compatibility[1]:
            if os_data:
                min_ver = os_data.get_macos_name_by_darwin(compatibility[1])
                max_ver = os_data.get_macos_name_by_darwin(compatibility[0])
                
                tk.Label(
                    details_frame,
                    text=f"macOS Support: {min_ver} to {max_ver}",
                    font=get_font('small'),
                    bg=COLORS['bg_main'],
                    fg=COLORS['text_secondary'],
                    anchor=tk.W
                ).pack(anchor=tk.W)
        elif oclp_compat:
            if os_data:
                min_ver = os_data.get_macos_name_by_darwin(oclp_compat[1])
                max_ver = os_data.get_macos_name_by_darwin(oclp_compat[0])
                
                tk.Label(
                    details_frame,
                    text=f"OCLP Support: {min_ver} to {max_ver}",
                    font=get_font('small'),
                    bg=COLORS['bg_main'],
                    fg=COLORS['warning'],
                    anchor=tk.W
                ).pack(anchor=tk.W)
        
    def refresh(self):
        """Refresh the page content"""
        # Check if we have hardware report data to display
        if self.controller.hardware_report and not self.is_checking:
            self.show_compatibility_results(
                self.controller.hardware_report,
                self.controller.native_macos_version,
                self.controller.ocl_patched_macos_version
            )
