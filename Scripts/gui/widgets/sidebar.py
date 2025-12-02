"""
Sidebar navigation widget for OpCore Simplify GUI
"""

import tkinter as tk
from tkinter import ttk

from ..styles import COLORS, FONTS, SIDEBAR_CONFIG, NAVIGATION_ITEMS, SPACING, get_font


class Sidebar(tk.Frame):
    """Modern sidebar navigation component"""
    
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
        
        # Prevent sidebar from shrinking
        self.pack_propagate(False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup sidebar UI components"""
        # Logo/Title section
        logo_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'], height=80)
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
        title_label.pack(anchor=tk.W)
        
        version_label = tk.Label(
            logo_frame,
            text="GUI Mode",
            font=get_font('small'),
            bg=SIDEBAR_CONFIG['bg'],
            fg=COLORS['text_secondary']
        )
        version_label.pack(anchor=tk.W)
        
        # Separator
        separator = tk.Frame(self, bg=COLORS['border_light'], height=1)
        separator.pack(fill=tk.X, padx=SPACING['medium'], pady=SPACING['small'])
        
        # Navigation items
        nav_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'])
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['small'], 
                      pady=SPACING['small'])
        
        for item in NAVIGATION_ITEMS:
            self.create_nav_item(nav_frame, item)
        
        # Footer section
        footer_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'], height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=SPACING['medium'], 
                         pady=SPACING['medium'])
        footer_frame.pack_propagate(False)
        
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
        """Create a navigation item button with macOS styling"""
        item_id = item['id']
        emoji = item.get('emoji', '')
        label = item.get('label', '')
        display_text = f"{emoji}  {label}" if emoji else label
        
        # Create container frame for rounded corners effect
        item_container = tk.Frame(parent, bg=SIDEBAR_CONFIG['bg'])
        item_container.pack(fill=tk.X, pady=3, padx=8)
        
        # Create button with macOS-style appearance
        button = tk.Button(
            item_container,
            text=display_text,
            font=get_font('sidebar'),
            bg=SIDEBAR_CONFIG['bg'],
            fg=COLORS['text_sidebar'],
            activebackground=COLORS['bg_hover'],
            activeforeground=COLORS['text_primary'],
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
        
        # Store button reference
        self.nav_buttons[item_id] = button
        
        # Bind hover effects
        button.bind('<Enter>', lambda e, btn=button: self.on_hover_enter(btn, item_id))
        button.bind('<Leave>', lambda e, btn=button: self.on_hover_leave(btn, item_id))
        
    def on_hover_enter(self, button, item_id):
        """Handle mouse enter event with subtle macOS-style hover"""
        if self.selected_id != item_id:
            button.config(bg=COLORS['bg_hover'])
            
    def on_hover_leave(self, button, item_id):
        """Handle mouse leave event"""
        if self.selected_id != item_id:
            button.config(bg=SIDEBAR_CONFIG['bg'])
            
    def select_item(self, item_id):
        """Select a navigation item"""
        # Deselect previous item
        if self.selected_id and self.selected_id in self.nav_buttons:
            prev_button = self.nav_buttons[self.selected_id]
            prev_button.config(
                bg=SIDEBAR_CONFIG['bg'],
                fg=COLORS['text_sidebar'],
                font=get_font('sidebar')
            )
        
        # Select new item
        self.selected_id = item_id
        if item_id in self.nav_buttons:
            button = self.nav_buttons[item_id]
            button.config(
                bg=COLORS['bg_selected'],
                fg=COLORS['text_sidebar_selected'],
                font=get_font('sidebar_selected')
            )
        
        # Call callback
        if self.on_item_select:
            self.on_item_select(item_id)
            
    def set_selected(self, item_id):
        """Programmatically set selected item"""
        self.select_item(item_id)
