"""
WiFi profile extraction page
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import json
import platform
import threading

from ..styles import COLORS, SPACING, get_font


class WiFiPage(tk.Frame):
    """WiFi profile extraction page"""
    
    def __init__(self, parent, app_controller, **kwargs):
        """
        Initialize WiFi page
        
        Args:
            parent: Parent widget
            app_controller: Reference to main application controller
        """
        super().__init__(parent, bg=COLORS['bg_main'], **kwargs)
        self.controller = app_controller
        self.os_name = platform.system()
        
        # Import WiFi extractor
        try:
            from Scripts import wifi_profile_extractor
            self.wifi_extractor = wifi_profile_extractor.WifiProfileExtractor()
        except (ImportError, AttributeError, ModuleNotFoundError) as e:
            # WiFi extractor module not available - will show error when used
            self.wifi_extractor = None
            print(f"Warning: WiFi extractor not available: {e}")
        
        self.extracted_networks = []
        self.is_extracting = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the WiFi page UI"""
        # Main container with padding
        container = tk.Frame(self, bg=COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxlarge'], 
                      pady=SPACING['xlarge'])
        
        # Title section
        title_label = tk.Label(
            container,
            text="WiFi Profile Extractor",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, SPACING['small']))
        
        subtitle_label = tk.Label(
            container,
            text="Extract saved WiFi network credentials for easy transfer to macOS",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, SPACING['xlarge']))
        
        # Platform info card
        self.create_platform_info(container)
        
        # Extraction controls
        self.create_extraction_controls(container)
        
        # Results section
        self.create_results_section(container)
        
    def create_platform_info(self, parent):
        """Create platform information card"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Icon
        icon = tk.Label(
            content,
            text="💻",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['info']
        )
        icon.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # Info text
        text_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        os_display = {
            'Windows': 'Windows',
            'Darwin': 'macOS',
            'Linux': 'Linux'
        }.get(self.os_name, self.os_name)
        
        title = tk.Label(
            text_frame,
            text=f"Platform: {os_display}",
            font=get_font('body_bold'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor=tk.W
        )
        title.pack(anchor=tk.W)
        
        if self.os_name == 'Darwin':
            desc_text = "macOS: Will prompt for administrator credentials to access keychain"
        elif self.os_name == 'Windows':
            desc_text = "Windows: Uses netsh to retrieve saved WiFi profiles"
        elif self.os_name == 'Linux':
            desc_text = "Linux: Uses NetworkManager to retrieve WiFi profiles"
        else:
            desc_text = "Platform not fully supported"
        
        desc = tk.Label(
            text_frame,
            text=desc_text,
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            anchor=tk.W,
            wraplength=500
        )
        desc.pack(anchor=tk.W)
        
    def create_extraction_controls(self, parent):
        """Create WiFi extraction control buttons"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, pady=(0, SPACING['large']))
        
        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=SPACING['large'], pady=SPACING['large'])
        
        # Title
        header = tk.Label(
            content,
            text="Extract WiFi Profiles",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(anchor=tk.W, pady=(0, SPACING['medium']))
        
        # Description
        desc = tk.Label(
            content,
            text="This tool extracts saved WiFi network credentials from your system.\n" +
                 "Perfect for transferring your WiFi settings to your Hackintosh installation.",
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            justify=tk.LEFT,
            anchor=tk.W
        )
        desc.pack(anchor=tk.W, pady=(0, SPACING['medium']))
        
        # Button frame
        button_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, pady=(0, 0))
        
        # Extract button
        self.extract_btn = tk.Button(
            button_frame,
            text="📡  Extract WiFi Profiles",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            command=self.start_extraction,
            highlightthickness=0
        )
        self.extract_btn.pack(side=tk.LEFT, padx=(0, SPACING['medium']))
        
        # Export button
        self.export_btn = tk.Button(
            button_frame,
            text="💾  Export to File",
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['large'],
            pady=SPACING['small'],
            state=tk.DISABLED,
            command=self.export_to_file,
            highlightthickness=0
        )
        self.export_btn.pack(side=tk.LEFT)
        
        # Hover effects
        def on_extract_enter(e):
            if self.extract_btn['state'] != tk.DISABLED:
                self.extract_btn.config(bg=COLORS['primary_hover'])
        def on_extract_leave(e):
            if self.extract_btn['state'] != tk.DISABLED:
                self.extract_btn.config(bg=COLORS['primary'])
        def on_export_enter(e):
            if self.export_btn['state'] != tk.DISABLED:
                self.export_btn.config(bg=COLORS['bg_hover'])
        def on_export_leave(e):
            if self.export_btn['state'] != tk.DISABLED:
                self.export_btn.config(bg=COLORS['bg_hover'])
        
        self.extract_btn.bind('<Enter>', on_extract_enter)
        self.extract_btn.bind('<Leave>', on_extract_leave)
        self.export_btn.bind('<Enter>', on_export_enter)
        self.export_btn.bind('<Leave>', on_export_leave)
        
    def create_results_section(self, parent):
        """Create WiFi extraction results display"""
        card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(card, bg=COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=SPACING['large'], pady=(SPACING['large'], SPACING['medium']))
        
        header = tk.Label(
            header_frame,
            text="📋  Extracted Networks",
            font=get_font('heading'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        header.pack(side=tk.LEFT)
        
        # Networks count label
        self.count_label = tk.Label(
            header_frame,
            text="0 networks",
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary']
        )
        self.count_label.pack(side=tk.RIGHT)
        
        # Results text area
        log_frame = tk.Frame(card, bg=COLORS['bg_main'], 
                           highlightbackground=COLORS['border_light'], highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        self.results_text = scrolledtext.ScrolledText(
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
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.insert('1.0', 'No WiFi profiles extracted yet.\n\nClick "Extract WiFi Profiles" to begin.')
        self.results_text.config(state=tk.DISABLED)
        
    def start_extraction(self):
        """Start WiFi profile extraction in a separate thread"""
        if self.is_extracting:
            return
            
        if not self.wifi_extractor:
            messagebox.showerror(
                "Error",
                "WiFi extractor module not available.\nPlease ensure all dependencies are installed."
            )
            return
        
        # Disable button during extraction
        self.extract_btn.config(state=tk.DISABLED)
        self.is_extracting = True
        
        # Clear previous results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', 'Starting WiFi profile extraction...\n\n')
        self.results_text.config(state=tk.DISABLED)
        
        # Run extraction in thread
        thread = threading.Thread(target=self.run_extraction)
        thread.daemon = True
        thread.start()
        
    def run_extraction(self):
        """Run the actual WiFi extraction process"""
        try:
            self.log_message("Detecting WiFi profiles...")
            
            # Get WiFi profiles based on OS
            if self.os_name == 'Windows':
                ssid_list = self.get_windows_profiles()
                get_password_func = self.wifi_extractor.get_wifi_password_windows
            elif self.os_name == 'Darwin':
                ssid_list = self.get_macos_profiles()
                get_password_func = self.wifi_extractor.get_wifi_password_macos
            elif self.os_name == 'Linux':
                ssid_list = self.get_linux_profiles()
                get_password_func = self.wifi_extractor.get_wifi_password_linux
            else:
                self.log_message(f"Error: Platform {self.os_name} is not supported.")
                return
            
            if not ssid_list:
                self.log_message("No WiFi profiles found on this system.")
                return
            
            self.log_message(f"Found {len(ssid_list)} WiFi profile(s).\n")
            
            # Process all networks
            self.extracted_networks = []
            for i, ssid in enumerate(ssid_list):
                self.log_message(f"Processing ({i+1}/{len(ssid_list)}): {ssid}")
                
                if self.os_name == 'Darwin':
                    self.log_message("  → Requesting keychain access...")
                
                try:
                    password = get_password_func(ssid)
                except Exception as pwd_error:
                    self.log_message(f"  ✗ Error retrieving password: {type(pwd_error).__name__}")
                    password = None
                
                if password is not None:
                    self.extracted_networks.append((ssid, password))
                    pwd_display = '(no password)' if password == '' else '***'
                    self.log_message(f"  ✓ Successfully retrieved: {pwd_display}\n")
                else:
                    self.log_message(f"  ✗ Could not retrieve password\n")
            
            # Show summary
            self.log_message("\n" + "="*50)
            self.log_message(f"Extraction complete!")
            self.log_message(f"Successfully extracted {len(self.extracted_networks)} of {len(ssid_list)} network(s).\n")
            
            if self.extracted_networks:
                self.log_message("Extracted networks:")
                for ssid, password in self.extracted_networks:
                    pwd_display = '(open network)' if password == '' else '(password saved)'
                    self.log_message(f"  • {ssid} {pwd_display}")
                
                # Enable export button
                self.controller.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL))
            
            # Update count
            self.controller.root.after(0, lambda: self.count_label.config(
                text=f"{len(self.extracted_networks)} network(s)"
            ))
            
        except Exception as e:
            import traceback
            error_type = type(e).__name__
            error_details = traceback.format_exc()
            
            self.log_message(f"\nError during extraction: {error_type}")
            print(f"WiFi extraction error details:\n{error_details}")
            
            messagebox.showerror(
                "Extraction Error", 
                f"Failed to extract WiFi profiles ({error_type}).\n\n"
                "This may be due to:\n"
                "• Insufficient permissions\n"
                "• System network utilities not available\n"
                "• Platform not fully supported\n\n"
                "Please check the console log for detailed error information."
            )
        finally:
            self.is_extracting = False
            self.controller.root.after(0, lambda: self.extract_btn.config(state=tk.NORMAL))
    
    def get_windows_profiles(self):
        """Get WiFi profiles on Windows"""
        from Scripts import run
        r = run.Run()
        output = r.run({"args": ["netsh", "wlan", "show", "profiles"]})
        
        if output[-1] != 0:
            return []
        
        profiles = []
        for line in output[0].splitlines():
            if "All User Profile" in line or "User Profile" in line:
                ssid = line.split(":")[1].strip()
                if ssid:
                    profiles.append(ssid)
        
        return profiles
    
    def get_macos_profiles(self):
        """Get WiFi profiles on macOS"""
        from Scripts import run
        r = run.Run()
        
        # Get WiFi interface
        output = r.run({"args": ["networksetup", "-listallhardwareports"]})
        if output[-1] != 0:
            return []
        
        interface = None
        lines = output[0].splitlines()
        for i, line in enumerate(lines):
            if "Wi-Fi" in line and i + 1 < len(lines):
                device_line = lines[i + 1]
                if "Device:" in device_line:
                    interface = device_line.split(":")[1].strip()
                    break
        
        if not interface:
            return []
        
        # Get preferred networks
        output = r.run({"args": ["networksetup", "-listpreferredwirelessnetworks", interface]})
        if output[-1] != 0:
            return []
        
        networks = []
        for line in output[0].splitlines()[1:]:
            ssid = line.strip()
            if ssid:
                networks.append(ssid)
        
        return networks
    
    def get_linux_profiles(self):
        """Get WiFi profiles on Linux"""
        from Scripts import run
        r = run.Run()
        output = r.run({"args": ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"]})
        
        if output[-1] != 0:
            return []
        
        profiles = []
        for line in output[0].splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and "802-11-wireless" in parts[1]:
                profiles.append(parts[0])
        
        return profiles
    
    def log_message(self, message):
        """Log a message to the results text area"""
        def update():
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, message + "\n")
            self.results_text.see(tk.END)
            self.results_text.config(state=tk.DISABLED)
        
        self.controller.root.after(0, update)
    
    def export_to_file(self):
        """Export extracted networks to a JSON file"""
        if not self.extracted_networks:
            messagebox.showwarning("No Data", "No WiFi profiles to export.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            title="Export WiFi Profiles",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="wifi_profiles.json"
        )
        
        if not filename:
            return
        
        try:
            # Create export data
            export_data = {
                "platform": self.os_name,
                "networks": [
                    {"ssid": ssid, "password": password}
                    for ssid, password in self.extracted_networks
                ]
            }
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            messagebox.showinfo(
                "Export Successful",
                f"WiFi profiles exported successfully to:\n{filename}\n\n" +
                f"Exported {len(self.extracted_networks)} network(s)."
            )
            self.log_message(f"\n✓ Exported to: {filename}")
            
        except Exception as e:
            import traceback
            print(f"WiFi export error details: {traceback.format_exc()}")
            messagebox.showerror(
                "Export Error", 
                "Failed to export WiFi profiles.\n\n"
                "This may be due to:\n"
                "• Insufficient file write permissions\n"
                "• Invalid file path\n"
                "• Disk space issue\n\n"
                "Please try a different location or check permissions."
            )
    
    def refresh(self):
        """Refresh the page content"""
        pass
