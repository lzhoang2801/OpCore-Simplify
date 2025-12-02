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
        
        # Step indicator
        step_label = tk.Label(
            container,
            text="STEP 2 OF 4",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['primary']
        )
        step_label.pack(anchor=tk.W, pady=(0, SPACING['tiny']))
        
        # Title section
        title_label = tk.Label(
            container,
            text="Hardware Compatibility",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Review your hardware compatibility with macOS",
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
        """Create an enhanced status information card with beautiful design"""
        card = tk.Frame(parent, bg='#E3F2FD', relief=tk.FLAT, bd=0,
                       highlightbackground='#2196F3', highlightthickness=2)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        content = tk.Frame(card, bg='#E3F2FD')
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Icon and status
        icon = tk.Label(
            content,
            text="🔍",
            font=('Arial', 24),
            bg='#E3F2FD',
            fg='#1976D2'
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        text_frame = tk.Frame(content, bg='#E3F2FD')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_title = tk.Label(
            text_frame,
            text="Ready to Check Compatibility",
            font=get_font('heading'),
            bg='#E3F2FD',
            fg='#1565C0',
            anchor=tk.W
        )
        self.status_title.pack(anchor=tk.W)
        
        self.status_desc = tk.Label(
            text_frame,
            text="Load a hardware report to begin compatibility checking",
            font=get_font('body'),
            bg='#E3F2FD',
            fg='#1976D2',
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
        """Create an enhanced compatibility summary section with beautiful design"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Summary title with icon
        header_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, SPACING['medium']))
        
        header = tk.Label(
            header_frame,
            text="📊  Compatibility Summary",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Summary stats frame with enhanced styling
        stats_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        stats_frame.pack(fill=tk.X)
        
        # Compatible devices card
        compatible_card = tk.Frame(stats_frame, bg='#E8F5E9',
                                   highlightbackground='#4CAF50',
                                   highlightthickness=2,
                                   relief=tk.FLAT)
        compatible_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                            padx=(0, SPACING['small']))
        
        compat_content = tk.Frame(compatible_card, bg='#E8F5E9')
        compat_content.pack(padx=SPACING['large'], pady=SPACING['large'])
        
        # Icon
        tk.Label(
            compat_content,
            text="✓",
            font=('Arial', 32, 'bold'),
            bg='#E8F5E9',
            fg='#4CAF50'
        ).pack()
        
        # Count
        self.compatible_count = tk.Label(
            compat_content,
            text="0",
            font=('Arial', 28, 'bold'),
            bg='#E8F5E9',
            fg='#2E7D32'
        )
        self.compatible_count.pack()
        
        # Label
        tk.Label(
            compat_content,
            text="Compatible Devices",
            font=get_font('body'),
            bg='#E8F5E9',
            fg='#2E7D32'
        ).pack()
        
        # Incompatible devices card
        incompatible_card = tk.Frame(stats_frame, bg='#FFEBEE',
                                      highlightbackground='#F44336',
                                      highlightthickness=2,
                                      relief=tk.FLAT)
        incompatible_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                               padx=(SPACING['small'], 0))
        
        incompat_content = tk.Frame(incompatible_card, bg='#FFEBEE')
        incompat_content.pack(padx=SPACING['large'], pady=SPACING['large'])
        
        # Icon
        tk.Label(
            incompat_content,
            text="⚠",
            font=('Arial', 32, 'bold'),
            bg='#FFEBEE',
            fg='#F44336'
        ).pack()
        
        # Count
        self.incompatible_count = tk.Label(
            incompat_content,
            text="0",
            font=('Arial', 28, 'bold'),
            bg='#FFEBEE',
            fg='#C62828'
        )
        self.incompatible_count.pack()
        
        # Label
        tk.Label(
            incompat_content,
            text="Needs Attention",
            font=get_font('body'),
            bg='#FFEBEE',
            fg='#C62828'
        ).pack()
        
    def show_compatibility_results(self, hardware_report, native_versions, oclp_versions):
        """Display compatibility check results with amazing visual design"""
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Update status card to success state
        self.status_title.config(
            text="✅  Compatibility Check Complete!",
            fg='#2E7D32'
        )
        self.status_desc.config(
            text="Review the detailed results below for your hardware configuration",
            fg='#388E3C'
        )
        # Update status card background to success color
        self.status_title.master.master.config(bg='#E8F5E9', highlightbackground='#4CAF50')
        self.status_title.master.config(bg='#E8F5E9')
        self.status_desc.master.config(bg='#E8F5E9')
        # Update icon parent
        for child in self.status_title.master.master.winfo_children():
            if isinstance(child, tk.Frame) and child != self.status_title.master:
                child.config(bg='#E8F5E9')
        
        # Store results
        self.compatibility_results = {}
        compatible_count = 0
        incompatible_count = 0
        
        # Device types to check with better display names and emojis
        device_types = [
            ('CPU', 'Processor', '🔧'),
            ('GPU', 'Graphics', '🎮'),
            ('Sound', 'Audio', '🔊'),
            ('Network', 'Network', '🌐'),
            ('Bluetooth', 'Bluetooth', '📶'),
            ('Storage Controllers', 'Storage', '💾'),
            ('Biometric', 'Biometric', '🔐'),
            ('SD Controller', 'SD Card', '💳')
        ]
        
        index = 0
        for device_type, display_name, emoji in device_types:
            if device_type not in hardware_report:
                continue
            
            index += 1
            devices = hardware_report[device_type]
            
            # Create device type section with enhanced header
            section_frame = tk.Frame(self.results_frame, bg=COLORS['bg_main'])
            section_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
            
            # Section header with gradient-like background
            header_frame = tk.Frame(section_frame, bg='#1565C0',
                                   highlightbackground='#0D47A1',
                                   highlightthickness=1,
                                   relief=tk.FLAT)
            header_frame.pack(fill=tk.X, pady=(0, SPACING['small']))
            
            header_content = tk.Frame(header_frame, bg='#1565C0')
            header_content.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['small'])
            
            # Section title with emoji
            tk.Label(
                header_content,
                text=f"{emoji}  {index}. {display_name}",
                font=get_font('heading'),
                bg='#1565C0',
                fg='#FFFFFF',
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            # Device count badge
            count_badge = tk.Frame(header_content, bg='#E3F2FD', relief=tk.FLAT)
            count_badge.pack(side=tk.RIGHT)
            
            tk.Label(
                count_badge,
                text=f"{len(devices)} device(s)",
                font=get_font('small'),
                bg='#E3F2FD',
                fg='#0D47A1',
                padx=SPACING['small'],
                pady=2
            ).pack()
            
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
        """Create an enhanced card for a single device with beautiful design"""
        # Determine compatibility status and colors
        compatibility = device_props.get('Compatibility', (None, None))
        oclp_compat = device_props.get('OCLP Compatibility')
        
        if compatibility[0] and compatibility[1]:
            status_icon = "✓"
            status_color = COLORS['success']
            status_text = "Compatible"
            status_bg = "#E8F5E9"  # Light green background
            border_color = COLORS['success']
        elif oclp_compat:
            status_icon = "⚡"
            status_color = COLORS['warning']
            status_text = "Requires OCLP"
            status_bg = "#FFF3E0"  # Light orange background
            border_color = COLORS['warning']
        else:
            status_icon = "✗"
            status_color = COLORS['error']
            status_text = "Not Supported"
            status_bg = "#FFEBEE"  # Light red background
            border_color = COLORS['error']
        
        # Main card container with colored left border
        card_container = tk.Frame(parent, bg=border_color)
        card_container.pack(fill=tk.X, pady=SPACING['small'])
        
        # Left colored indicator (4px wide)
        indicator = tk.Frame(card_container, bg=border_color, width=4)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        # Card content area
        card = tk.Frame(card_container, bg=COLORS['bg_main'],
                       highlightbackground=COLORS['border_light'],
                       highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        content = tk.Frame(card, bg=COLORS['bg_main'])
        content.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
        # Top section: Device name and status badge
        top_frame = tk.Frame(content, bg=COLORS['bg_main'])
        top_frame.pack(fill=tk.X, pady=(0, SPACING['small']))
        
        # Device name with icon
        name_frame = tk.Frame(top_frame, bg=COLORS['bg_main'])
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Large status icon
        tk.Label(
            name_frame,
            text=status_icon,
            font=('Arial', 16, 'bold'),
            bg=COLORS['bg_main'],
            fg=status_color
        ).pack(side=tk.LEFT, padx=(0, SPACING['small']))
        
        # Device name
        tk.Label(
            name_frame,
            text=device_name,
            font=get_font('body_bold'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        # Status badge
        badge_frame = tk.Frame(top_frame, bg=status_bg, relief=tk.FLAT)
        badge_frame.pack(side=tk.RIGHT, padx=SPACING['tiny'])
        
        tk.Label(
            badge_frame,
            text=status_text,
            font=get_font('small'),
            bg=status_bg,
            fg=status_color,
            padx=SPACING['small'],
            pady=2
        ).pack()
        
        # Device details section
        details_frame = tk.Frame(content, bg=COLORS['bg_secondary'], relief=tk.FLAT)
        details_frame.pack(fill=tk.X, pady=(SPACING['tiny'], 0))
        
        details_content = tk.Frame(details_frame, bg=COLORS['bg_secondary'])
        details_content.pack(fill=tk.X, padx=SPACING['small'], pady=SPACING['small'])
        
        # Create a grid for details
        row = 0
        
        # Device Type
        if device_props.get('Device Type'):
            self._add_detail_row(details_content, "Type:", device_props['Device Type'], row)
            row += 1
        
        # Manufacturer
        if device_props.get('Manufacturer'):
            self._add_detail_row(details_content, "Manufacturer:", device_props['Manufacturer'], row)
            row += 1
        
        # Device ID
        if device_props.get('Device ID'):
            self._add_detail_row(details_content, "Device ID:", device_props['Device ID'], row)
            row += 1
        
        # Codename (for GPUs)
        if device_props.get('Codename'):
            self._add_detail_row(details_content, "Codename:", device_props['Codename'], row)
            row += 1
        
        # Bus Type
        if device_props.get('Bus Type'):
            self._add_detail_row(details_content, "Bus:", device_props['Bus Type'], row)
            row += 1
        
        # macOS version support - with visual styling
        if compatibility[0] and compatibility[1]:
            if os_data:
                min_ver = os_data.get_macos_name_by_darwin(compatibility[1])
                max_ver = os_data.get_macos_name_by_darwin(compatibility[0])
                
                support_frame = tk.Frame(details_content, bg=COLORS['bg_secondary'])
                support_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(SPACING['tiny'], 0))
                
                tk.Label(
                    support_frame,
                    text="🍎 macOS Support:",
                    font=get_font('small'),
                    bg=COLORS['bg_secondary'],
                    fg=COLORS['text_primary']
                ).pack(side=tk.LEFT, padx=(0, SPACING['tiny']))
                
                # Version range in a highlighted box
                version_box = tk.Frame(support_frame, bg='#E3F2FD', relief=tk.FLAT)
                version_box.pack(side=tk.LEFT)
                
                tk.Label(
                    version_box,
                    text=f"{min_ver} → {max_ver}",
                    font=get_font('small'),
                    bg='#E3F2FD',
                    fg='#1976D2',
                    padx=SPACING['small'],
                    pady=2
                ).pack()
                
        elif oclp_compat:
            if os_data:
                min_ver = os_data.get_macos_name_by_darwin(oclp_compat[1])
                max_ver = os_data.get_macos_name_by_darwin(oclp_compat[0])
                
                support_frame = tk.Frame(details_content, bg=COLORS['bg_secondary'])
                support_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(SPACING['tiny'], 0))
                
                tk.Label(
                    support_frame,
                    text="⚡ OCLP Support:",
                    font=get_font('small'),
                    bg=COLORS['bg_secondary'],
                    fg=COLORS['text_primary']
                ).pack(side=tk.LEFT, padx=(0, SPACING['tiny']))
                
                # Version range in a highlighted box
                version_box = tk.Frame(support_frame, bg='#FFF3E0', relief=tk.FLAT)
                version_box.pack(side=tk.LEFT)
                
                tk.Label(
                    version_box,
                    text=f"{min_ver} → {max_ver}",
                    font=get_font('small'),
                    bg='#FFF3E0',
                    fg='#F57C00',
                    padx=SPACING['small'],
                    pady=2
                ).pack()
    
    def _add_detail_row(self, parent, label, value, row):
        """Add a detail row with label and value"""
        label_widget = tk.Label(
            parent,
            text=label,
            font=get_font('small'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        label_widget.grid(row=row, column=0, sticky=tk.W, padx=(0, SPACING['small']), pady=2)
        
        value_widget = tk.Label(
            parent,
            text=value,
            font=get_font('small'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        value_widget.grid(row=row, column=1, sticky=tk.W, pady=2)
        
    def refresh(self):
        """Refresh the page content"""
        # Check if we have hardware report data to display
        if self.controller.hardware_report and not self.is_checking:
            self.show_compatibility_results(
                self.controller.hardware_report,
                self.controller.native_macos_version,
                self.controller.ocl_patched_macos_version
            )
