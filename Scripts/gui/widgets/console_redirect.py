"""
Console output redirection for GUI
"""

import sys


class ConsoleRedirector:
    """Redirect stdout to a text widget (thread-safe)"""
    
    def __init__(self, text_widget, original_stdout, root):
        """
        Initialize console redirector
        
        Args:
            text_widget: Tkinter Text widget to write to
            original_stdout: Original stdout to preserve
            root: Root Tkinter window for thread-safe operations
        """
        self.text_widget = text_widget
        self.original_stdout = original_stdout
        self.root = root
        
    def write(self, message):
        """Write message to both console and text widget"""
        # Schedule GUI update on main thread for thread safety
        if self.root:
            self.root.after(0, lambda: self._write_to_widget(message))
        # Also write to original stdout
        if self.original_stdout:
            self.original_stdout.write(message)
    
    def _write_to_widget(self, message):
        """Internal method to write to widget (must be called on main thread)"""
        try:
            self.text_widget.insert('end', message)
            self.text_widget.see('end')
            self.text_widget.update_idletasks()
        except (Exception, RuntimeError, AttributeError):
            # Ignore errors if widget is destroyed or no longer accessible
            pass
        
    def flush(self):
        """Flush the output stream"""
        if self.original_stdout:
            self.original_stdout.flush()
