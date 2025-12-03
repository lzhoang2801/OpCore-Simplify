"""
Sidebar navigation widget for OpCore Simplify GUI
"""

import tkinter as tk
from tkinter import ttk

from ..styles import COLORS, FONTS, SIDEBAR_CONFIG, NAVIGATION_ITEMS, SPACING, ANIMATION, get_font
from ..icons import get_nav_icon


class Sidebar(tk.Frame):
    """Modern sidebar navigation component with smooth animations"""
    
    def __init__(self, parent, on_item_select=None, **kwargs):
        """
        Initialize sidebar
        
        Args:
            parent: Parent widget
            on_item_select: Callback function when item is selected (receives item_id)
        """
        super().__init__(parent, bg=SIDEBAR_CONFIG['bg'], 
                        width=SIDEBAR_CONFIG['width'], **kwargs)
        
        self.on_item_select = on_item_select
        self.selected_id = None
        self.nav_buttons = {}
        self.nav_containers = {}
        
        # Prevent sidebar from shrinking
        self.pack_propagate(False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup sidebar UI components with modern styling"""
        # Logo/Title section
        logo_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'], height=90)
        logo_frame.pack(fill=tk.X, padx=SPACING['medium'], pady=(SPACING['large'], SPACING['medium']))
        logo_frame.pack_propagate(False)
        
        title_label = tk.Label(
            logo_frame,
            text="OpCore\nSimplify",
            font=get_font('subtitle'),
            bg=SIDEBAR_CONFIG['bg'],
            fg=COLORS['text_primary'],
            justify=tk.LEFT
        )
        title_label.pack(anchor=tk.W, pady=(SPACING['small'], 0))
        
        version_label = tk.Label(
            logo_frame,
            text="GUI Mode",
            font=get_font('small'),
            bg=SIDEBAR_CONFIG['bg'],
            fg=COLORS['text_secondary']
        )
        version_label.pack(anchor=tk.W)
        
        # Separator with subtle styling
        separator = tk.Frame(self, bg=COLORS['border_light'], height=1)
        separator.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['medium'])
        
        # Navigation items container
        nav_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'])
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['small'], 
                      pady=SPACING['small'])
        
        # Group items by section
        sections = {}
        for item in NAVIGATION_ITEMS:
            section = item.get('section', 'main')
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
        
        # Create section headers and items
        first_section = True
        for section_name, items in sections.items():
            if not first_section:
                # Add separator between sections
                section_sep = tk.Frame(nav_frame, bg=COLORS['border_light'], height=1)
                section_sep.pack(fill=tk.X, pady=SPACING['medium'], padx=SPACING['medium'])
            
            # Add section header if not main
            if section_name != 'main':
                section_header = tk.Label(
                    nav_frame,
                    text=section_name.upper(),
                    font=get_font('small'),
                    bg=SIDEBAR_CONFIG['bg'],
                    fg=COLORS['text_tertiary'],
                    anchor=tk.W
                )
                section_header.pack(anchor=tk.W, padx=SPACING['large'], pady=(SPACING['small'], SPACING['tiny']))
            
            for item in items:
                self.create_nav_item(nav_frame, item)
            
            first_section = False
        
        # Footer section
        footer_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'], height=70)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=SPACING['medium'], 
                         pady=SPACING['medium'])
        footer_frame.pack_propagate(False)
        
        # Subtle separator above footer
        footer_sep = tk.Frame(self, bg=COLORS['border_light'], height=1)
        footer_sep.pack(fill=tk.X, side=tk.BOTTOM, padx=SPACING['medium'])
        
        footer_label = tk.Label(
            footer_frame,
            text="OpenCore EFI Builder\nfor Hackintosh",
            font=get_font('small'),
            bg=SIDEBAR_CONFIG['bg'],
            fg=COLORS['text_secondary'],
            justify=tk.LEFT
        )
        footer_label.pack(anchor=tk.W)
        
    def create_nav_item(self, parent, item):
        """Create a navigation item button with enhanced macOS styling and animations"""
        item_id = item['id']
        icon_name = item.get('icon', '')
        label = item.get('label', '')
        
        # Get icon character from icon system
        icon = get_nav_icon(icon_name) if icon_name else ''
        display_text = f"{icon}  {label}" if icon else label
        
        # Create container frame with rounded corners effect
        item_container = tk.Frame(parent, bg=SIDEBAR_CONFIG['bg'])
        item_container.pack(fill=tk.X, pady=2, padx=10)
        
        # Create inner frame for styling (rounded appearance)
        inner_frame = tk.Frame(
            item_container,
            bg=SIDEBAR_CONFIG['bg'],
            highlightthickness=0
        )
        inner_frame.pack(fill=tk.X)
        
        # Create button with enhanced macOS-style appearance
        button = tk.Button(
            inner_frame,
            text=display_text,
            font=get_font('sidebar'),
            bg=SIDEBAR_CONFIG['bg'],
            fg=COLORS['text_sidebar'],
            activebackground=COLORS['bg_hover'],
            activeforeground=COLORS['text_sidebar_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            anchor=tk.W,
            padx=SIDEBAR_CONFIG['item_padding_x'],
            pady=SIDEBAR_CONFIG['item_padding_y'],
            command=lambda: self.select_item(item_id),
            highlightthickness=0
        )
        button.pack(fill=tk.X)
        
        # Store references
        self.nav_buttons[item_id] = button
        self.nav_containers[item_id] = inner_frame
        
        # Bind enhanced hover effects with smooth transitions
        button.bind('<Enter>', lambda e, btn=button, frame=inner_frame: self.on_hover_enter(btn, frame, item_id))
        button.bind('<Leave>', lambda e, btn=button, frame=inner_frame: self.on_hover_leave(btn, frame, item_id))
        
    def on_hover_enter(self, button, frame, item_id):
        """Handle mouse enter event with smooth macOS-style hover transition"""
        if self.selected_id != item_id:
            # Apply smooth hover effect
            button.config(
                bg=COLORS['bg_hover'],
                fg=COLORS['text_sidebar_hover']
            )
            frame.config(bg=COLORS['bg_hover'])
        else:
            # Subtle hover effect on selected item
            button.config(bg=COLORS['bg_selected_hover'])
            frame.config(bg=COLORS['bg_selected_hover'])
            
    def on_hover_leave(self, button, frame, item_id):
        """Handle mouse leave event with smooth transition"""
        if self.selected_id != item_id:
            button.config(
                bg=SIDEBAR_CONFIG['bg'],
                fg=COLORS['text_sidebar']
            )
            frame.config(bg=SIDEBAR_CONFIG['bg'])
        else:
            # Return to selected state
            button.config(bg=COLORS['bg_selected'])
            frame.config(bg=COLORS['bg_selected'])
            
    def select_item(self, item_id):
        """Select a navigation item with smooth visual feedback"""
        # Deselect previous item
        if self.selected_id and self.selected_id in self.nav_buttons:
            prev_button = self.nav_buttons[self.selected_id]
            prev_frame = self.nav_containers[self.selected_id]
            prev_button.config(
                bg=SIDEBAR_CONFIG['bg'],
                fg=COLORS['text_sidebar'],
                font=get_font('sidebar')
            )
            prev_frame.config(bg=SIDEBAR_CONFIG['bg'])
        
        # Select new item with enhanced styling
        self.selected_id = item_id
        if item_id in self.nav_buttons:
            button = self.nav_buttons[item_id]
            frame = self.nav_containers[item_id]
            button.config(
                bg=COLORS['bg_selected'],
                fg=COLORS['text_sidebar_selected'],
                font=get_font('sidebar_selected')
            )
            frame.config(bg=COLORS['bg_selected'])
        
        # Call callback
        if self.on_item_select:
            self.on_item_select(item_id)
            
    def set_selected(self, item_id):
        """Programmatically set selected item"""
        self.select_item(item_id)
