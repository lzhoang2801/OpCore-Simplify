"""
Console log page for viewing system messages and debug information
"""

import tkinter as tk
from tkinter import scrolledtext
import os

from ..styles import COLORS, SPACING, get_font


class ConsolePage(tk.Frame):
    """Console log page for technical output"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize console page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the console page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Title section
        header_frame = tk.Frame(container, bg=COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        title_label = tk.Label(
            header_frame,
            text="Console Log",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = tk.Frame(header_frame, bg=COLORS['bg_main'])
        button_frame.pack(side=tk.RIGHT)
        
        # Clear button with macOS styling
        clear_btn = tk.Button(
            button_frame,
            text="🗑️  Clear",
            font=get_font('body'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            command=self.clear_console,
            highlightthickness=0
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, SPACING['small']))
        
        # Export button with macOS styling
        export_btn = tk.Button(
            button_frame,
            text="💾  Export",
            font=get_font('body'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            command=self.export_console,
            highlightthickness=0
        )
        export_btn.pack(side=tk.LEFT)
        
        # macOS-style hover effects
        def on_clear_enter(e):
            clear_btn.config(bg=COLORS['bg_hover'])
            
        def on_clear_leave(e):
            clear_btn.config(bg=COLORS['bg_hover'])
            
        def on_export_enter(e):
            export_btn.config(bg=COLORS['bg_hover'])
            
        def on_export_leave(e):
            export_btn.config(bg=COLORS['bg_hover'])
            
        clear_btn.bind('<Enter>', on_clear_enter)
        clear_btn.bind('<Leave>', on_clear_leave)
        export_btn.bind('<Enter>', on_export_enter)
        export_btn.bind('<Leave>', on_export_leave)
        
        # Subtitle
        subtitle_label = tk.Label(
            container,
            text="System messages, debug information, and application logs",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['large']))
        
        # Console log area in a card with macOS styling
        card = tk.Frame(container, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Log text area with dark theme (macOS Terminal style)
        log_frame = tk.Frame(card, bg='#1E1E1E', highlightbackground=COLORS['border_light'], highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['medium'], pady=SPACING['medium'])
        
        self.controller.console_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9) if os.name == 'nt' else ('Monaco', 10),
            bg='#1E1E1E',  # Dark background
            fg='#D4D4D4',  # Light text
            insertbackground='#FFFFFF',  # Cursor color
            selectbackground='#264F78',  # Selection color
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['medium'],
            pady=SPACING['medium']
        )
        self.controller.console_log.pack(fill=tk.BOTH, expand=True)
        
        # Info footer
        footer = tk.Frame(container, bg=COLORS['bg_main'])
        footer.pack(fill=tk.X, pady=(SPACING['medium'], 0))
        
        info_label = tk.Label(
            footer,
            text="💡 Tip: Export the console log when reporting issues to help with troubleshooting",
            font=get_font('small'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            anchor=tk.W
        )
        info_label.pack(anchor=tk.W)
        
    def clear_console(self):
        """Clear the console log"""
        self.controller.console_log.delete('1.0', tk.END)
        self.controller.console_log.insert('1.0', "Console log cleared.\n\n")
        
    def export_console(self):
        """Export console log to file"""
        from tkinter import filedialog
        import datetime
        
        # Get log content
        log_content = self.controller.console_log.get('1.0', tk.END)
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"opcore_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                from tkinter import messagebox
                messagebox.showinfo("Export Successful", 
                                  f"Console log exported to:\n{filename}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Export Failed", 
                                   f"Failed to export console log:\n{str(e)}")
        
    def refresh(self):
        """Refresh the page content"""
        pass
