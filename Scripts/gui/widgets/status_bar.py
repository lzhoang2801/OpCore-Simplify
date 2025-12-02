"""
Status bar widget for OpCore Simplify GUI
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from styles import COLORS, SPACING, get_font


class StatusBar(tk.Frame):
    """Modern status bar component at bottom of window"""
    
    def __init__(self, parent, **kwargs):
        """Initialize status bar"""
        super().__init__(parent, bg=COLORS['bg_sidebar'], height=30, **kwargs)
        
        self.pack_propagate(False)
        
        # Status message label
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=SPACING['medium'], fill=tk.X, expand=True)
        
        # Status indicator (optional dot)
        self.indicator = tk.Label(
            self,
            text="●",
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['success']
        )
        self.indicator.pack(side=tk.RIGHT, padx=SPACING['medium'])
        
    def set_status(self, message, status_type='info'):
        """
        Update status bar message and color
        
        Args:
            message: Status message to display
            status_type: Type of status ('info', 'success', 'warning', 'error')
        """
        self.status_label.config(text=message)
        
        # Update indicator color based on status type
        color_map = {
            'info': COLORS['info'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'error': COLORS['error'],
        }
        
        self.indicator.config(fg=color_map.get(status_type, COLORS['info']))
        
    def set_loading(self, message="Loading..."):
        """Set status bar to loading state"""
        self.set_status(message, 'info')
        # Could add animation here in future
        
    def set_ready(self):
        """Set status bar to ready state"""
        self.set_status("Ready", 'success')
