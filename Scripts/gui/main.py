"""
Main GUI application with sidebar navigation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading

# Add Scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.styles import COLORS, SPACING, SIDEBAR_CONFIG, get_font
from gui.widgets import Sidebar, StatusBar, ConsoleRedirector
from gui.pages import ConfigurationPage, CustomizationPage, BuildPage, ConsolePage
from Scripts.datasets import os_data


class OpCoreGUI:
    """Main GUI application with modern sidebar layout"""
    
    def __init__(self, ocpe_instance):
        """
        Initialize the GUI application
        
        Args:
            ocpe_instance: Instance of OCPE class from OpCore-Simplify.py
        """
        self.ocpe = ocpe_instance
        self.root = tk.Tk()
        self.root.title("OpCore Simplify")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure root background
        self.root.configure(bg=COLORS['bg_main'])
        
        # Variables for tracking state
        self.hardware_report_path = tk.StringVar(value="Not selected")
        self.macos_version = tk.StringVar(value="Not selected")
        self.smbios_model = tk.StringVar(value="Not selected")
        self.disabled_devices_text = tk.StringVar(value="None")
        
        # Data storage
        self.hardware_report = None
        self.hardware_report_data = None
        self.customized_hardware = None
        self.disabled_devices = None
        self.native_macos_version = None
        self.ocl_patched_macos_version = None
        self.needs_oclp = False
        
        # Current page
        self.current_page = None
        self.pages = {}
        
        # Placeholder for widgets that will be created by pages
        self.build_btn = None
        self.progress_var = None
        self.progress_bar = None
        self.build_log = None
        self.open_result_btn = None
        self.console_log = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI layout with sidebar"""
        # Create main container
        main_container = tk.Frame(self.root, bg=COLORS['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.sidebar = Sidebar(main_container, on_item_select=self.on_nav_select)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create right side container (content + status bar)
        right_container = tk.Frame(main_container, bg=COLORS['bg_main'])
        right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create content area (for pages)
        self.content_area = tk.Frame(right_container, bg=COLORS['bg_main'])
        self.content_area.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_bar = StatusBar(right_container)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Create all pages
        self.create_pages()
        
        # Show initial page
        self.sidebar.set_selected('config')
        self.show_page('config')
        
        # Set up console redirection after console page is created
        if self.console_log:
            sys.stdout = ConsoleRedirector(self.console_log, sys.stdout, self.root)
        
        # Set initial status
        self.status_bar.set_ready()
        
    def create_pages(self):
        """Create all page instances"""
        self.pages['config'] = ConfigurationPage(self.content_area, self)
        self.pages['customize'] = CustomizationPage(self.content_area, self)
        self.pages['build'] = BuildPage(self.content_area, self)
        self.pages['console'] = ConsolePage(self.content_area, self)
        
        # Hide all pages initially
        for page in self.pages.values():
            page.pack_forget()
            
    def on_nav_select(self, item_id):
        """Handle navigation item selection"""
        self.show_page(item_id)
        
    def show_page(self, page_id):
        """Show a specific page"""
        # Hide current page
        if self.current_page:
            self.pages[self.current_page].pack_forget()
        
        # Show new page
        if page_id in self.pages:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_id
            
            # Refresh page content
            self.pages[page_id].refresh()
            
    def log_message(self, message):
        """Log a message to both console and build log"""
        print(message)
        if self.build_log:
            self.build_log.insert(tk.END, message + "\n")
            self.build_log.see(tk.END)
            
    def update_status(self, message, status_type='info'):
        """Update the status bar"""
        self.status_bar.set_status(message, status_type)
        self.root.update_idletasks()
        
    def select_hardware_report_gui(self):
        """GUI version of hardware report selection"""
        self.update_status("Selecting hardware report...", 'info')
        
        # Option to export or select file
        choice = messagebox.askquestion(
            "Select Hardware Report",
            "Do you want to export a hardware report?\n\n" +
            "Select 'Yes' to export using Hardware Sniffer\n" +
            "Select 'No' to choose an existing report file"
        )
        
        if choice == 'yes' and os.name == 'nt':
            # Export hardware report
            self.export_hardware_report()
        else:
            # Select existing file
            filename = filedialog.askopenfilename(
                title="Select Hardware Report",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                self.load_hardware_report(filename)
                
    def export_hardware_report(self):
        """Export hardware report using Hardware Sniffer"""
        try:
            self.log_message("Exporting hardware report...")
            hardware_sniffer = self.ocpe.o.gather_hardware_sniffer()
            
            if not hardware_sniffer:
                messagebox.showerror("Error", "Hardware Sniffer not found")
                self.update_status("Hardware Sniffer not found", 'error')
                return
                
            report_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                "SysReport"
            )
            
            output = self.ocpe.r.run({
                "args": [hardware_sniffer, "-e", "-o", report_dir]
            })
            
            if output[-1] != 0:
                error_messages = {
                    3: "Error collecting hardware.",
                    4: "Error generating hardware report.",
                    5: "Error dumping ACPI tables."
                }
                error_message = error_messages.get(output[-1], "Unknown error.")
                messagebox.showerror(
                    "Export Error",
                    f"Could not export the hardware report.\n{error_message}\n" +
                    "Please try again or use Hardware Sniffer manually."
                )
                self.update_status("Export failed", 'error')
                return
            else:
                report_path = os.path.join(report_dir, "Report.json")
                acpitables_dir = os.path.join(report_dir, "ACPI")
                
                report_data = self.ocpe.u.read_file(report_path)
                self.ocpe.ac.read_acpi_tables(acpitables_dir)
                
                self.load_hardware_report(report_path, report_data)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export hardware report: {str(e)}")
            self.update_status("Export failed", 'error')
            
    def load_hardware_report(self, path, data=None):
        """Load and validate hardware report"""
        try:
            self.log_message(f"Loading hardware report from: {path}")
            self.update_status("Validating hardware report...", 'info')
            
            # Validate report
            is_valid, errors, warnings, data = self.ocpe.v.validate_report(path)
            
            if not is_valid or errors:
                error_msg = "Hardware report validation failed:\n\n"
                if errors:
                    error_msg += "Errors:\n" + "\n".join(f"- {e}" for e in errors)
                if warnings:
                    error_msg += "\n\nWarnings:\n" + "\n".join(f"- {w}" for w in warnings)
                
                messagebox.showerror(
                    "Validation Error",
                    error_msg + "\n\nPlease re-export the hardware report and try again."
                )
                self.update_status("Validation failed", 'error')
                return
                
            # Store report
            self.hardware_report_path.set(os.path.basename(path))
            self.hardware_report_data = data
            
            # Check compatibility
            self.hardware_report, self.native_macos_version, self.ocl_patched_macos_version = \
                self.ocpe.c.check_compatibility(data)
            
            # Auto-select macOS version
            self.auto_select_macos_version()
            
            # Read ACPI tables if not already loaded
            if not self.ocpe.ac.ensure_dsdt():
                acpi_dir = os.path.join(os.path.dirname(path), "ACPI")
                if os.path.exists(acpi_dir):
                    self.ocpe.ac.read_acpi_tables(acpi_dir)
                else:
                    # Prompt for ACPI tables
                    self.ocpe.ac.select_acpi_tables()
            
            self.log_message("Hardware report loaded successfully!")
            self.update_status("Hardware report loaded", 'success')
            
            messagebox.showinfo("Success", "Hardware report loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hardware report: {str(e)}")
            self.update_status("Failed to load report", 'error')
            
    def auto_select_macos_version(self):
        """Automatically select the best macOS version"""
        if not self.hardware_report:
            return
            
        # Use the same logic as CLI version to determine suggested version
        suggested_macos_version = self.native_macos_version[1]
        
        # Apply hardware-specific version constraints
        for device_type in ("GPU", "Network", "Bluetooth", "SD Controller"):
            if device_type in self.hardware_report:
                for device_name, device_props in self.hardware_report[device_type].items():
                    if device_props.get("Compatibility", (None, None)) != (None, None):
                        if device_type == "GPU" and device_props.get("Device Type") == "Integrated GPU":
                            full_device_id = device_props.get("Device ID", "0"*8)
                            device_id = full_device_id[5:] if len(full_device_id) >= 6 else full_device_id
                            
                            if device_props.get("Manufacturer") == "AMD" or device_id.startswith(("59", "87C0")):
                                suggested_macos_version = "22.99.99"
                            elif device_id.startswith(("09", "19")):
                                suggested_macos_version = "21.99.99"
                        
                        if self.ocpe.u.parse_darwin_version(suggested_macos_version) > \
                           self.ocpe.u.parse_darwin_version(device_props.get("Compatibility")[0]):
                            suggested_macos_version = device_props.get("Compatibility")[0]
        
        # Avoid beta versions
        while "Beta" in os_data.get_macos_name_by_darwin(suggested_macos_version):
            suggested_macos_version = "{}{}".format(
                int(suggested_macos_version[:2]) - 1,
                suggested_macos_version[2:]
            )
        
        # Apply this version
        self.apply_macos_version(suggested_macos_version)
        
    def apply_macos_version(self, version):
        """Apply a macOS version selection"""
        try:
            self.update_status("Configuring for macOS version...", 'info')
            
            macos_name = os_data.get_macos_name_by_darwin(version)
            self.macos_version.set(f"{macos_name} ({version})")
            
            # Perform hardware customization
            self.customized_hardware, self.disabled_devices, self.needs_oclp = \
                self.ocpe.h.hardware_customization(self.hardware_report, version)
            
            # Update disabled devices display
            if self.disabled_devices:
                disabled_list = ", ".join(self.disabled_devices.keys())
                self.disabled_devices_text.set(disabled_list)
            else:
                self.disabled_devices_text.set("None")
            
            # Auto-select SMBIOS
            smbios = self.ocpe.s.select_smbios_model(self.customized_hardware, version)
            self.smbios_model.set(smbios)
            
            # Select ACPI patches
            self.ocpe.ac.select_acpi_patches(self.customized_hardware, self.disabled_devices)
            
            # Select required kexts
            self.needs_oclp = self.ocpe.k.select_required_kexts(
                self.customized_hardware, version, self.needs_oclp, self.ocpe.ac.patches
            )
            
            # SMBIOS specific options
            self.ocpe.s.smbios_specific_options(
                self.customized_hardware, smbios, version,
                self.ocpe.ac.patches, self.ocpe.k
            )
            
            self.update_status("Configuration complete", 'success')
            
            if self.needs_oclp:
                messagebox.showwarning(
                    "OpenCore Legacy Patcher Required",
                    "Your hardware requires OpenCore Legacy Patcher.\n\n" +
                    "This will be configured during the build process."
                )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply macOS version: {str(e)}")
            self.update_status("Configuration failed", 'error')
            
    def select_macos_version_gui(self):
        """GUI for selecting macOS version"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
            
        # Create selection window
        version_window = tk.Toplevel(self.root)
        version_window.title("Select macOS Version")
        version_window.geometry("600x500")
        version_window.configure(bg=COLORS['bg_main'])
        
        # Title
        title = tk.Label(
            version_window,
            text="Select macOS Version",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title.pack(pady=SPACING['large'])
        
        # Create listbox for versions
        listbox_frame = tk.Frame(version_window, bg=COLORS['bg_main'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=SPACING['medium'])
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        version_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground='#FFFFFF',
            relief=tk.FLAT,
            bd=0
        )
        version_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=version_listbox.yview)
        
        # Populate versions
        oclp_min = int(self.ocl_patched_macos_version[-1][:2]) if self.ocl_patched_macos_version else 99
        oclp_max = int(self.ocl_patched_macos_version[0][:2]) if self.ocl_patched_macos_version else 0
        min_version = min(int(self.native_macos_version[0][:2]), oclp_min)
        max_version = max(int(self.native_macos_version[-1][:2]), oclp_max)
        
        version_map = {}
        for darwin_version in range(min_version, max_version + 1):
            name = os_data.get_macos_name_by_darwin(str(darwin_version))
            label = f"{darwin_version}. {name}"
            if oclp_min <= darwin_version <= oclp_max:
                label += " (Requires OpenCore Legacy Patcher)"
            version_listbox.insert(tk.END, label)
            version_map[darwin_version] = f"{darwin_version}.99.99"
        
        def on_select():
            selection = version_listbox.curselection()
            if selection:
                darwin_ver = min_version + selection[0]
                version = version_map[darwin_ver]
                self.apply_macos_version(version)
                version_window.destroy()
                messagebox.showinfo(
                    "Success",
                    f"macOS version set to {os_data.get_macos_name_by_darwin(version)}"
                )
        
        # Button frame
        button_frame = tk.Frame(version_window, bg=COLORS['bg_main'])
        button_frame.pack(pady=SPACING['large'])
        
        select_btn = tk.Button(
            button_frame,
            text="Select",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['medium'],
            command=on_select
        )
        select_btn.pack()
        
    def customize_smbios_gui(self):
        """GUI for customizing SMBIOS"""
        if not self.customized_hardware:
            messagebox.showwarning(
                "Warning",
                "Please select a hardware report and macOS version first!"
            )
            return
            
        # Get current version from the stored value
        current_version = self.macos_version.get()
        if "Not selected" in current_version:
            messagebox.showwarning("Warning", "Please select macOS version first!")
            return
            
        # Extract darwin version from display string
        darwin_version = current_version.split("(")[1].split(")")[0] if "(" in current_version else None
        if not darwin_version:
            return
            
        # For now, show info that SMBIOS is auto-selected
        messagebox.showinfo(
            "SMBIOS Selection",
            f"The optimal SMBIOS model has been automatically selected: {self.smbios_model.get()}\n\n" +
            "This model provides the best compatibility for your hardware configuration.\n\n" +
            "Advanced SMBIOS customization is available through the CLI version."
        )
        
    def customize_acpi_gui(self):
        """GUI for customizing ACPI patches"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
            
        messagebox.showinfo(
            "ACPI Customization",
            "ACPI patches have been automatically configured based on your hardware.\n\n" +
            "The tool has selected the optimal patches for compatibility and stability.\n\n" +
            "Advanced ACPI customization is available through the CLI version."
        )
        
    def customize_kexts_gui(self):
        """GUI for customizing kexts"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
            
        messagebox.showinfo(
            "Kext Customization",
            "Kernel extensions have been automatically configured for your hardware.\n\n" +
            "All required kexts for your system have been selected.\n\n" +
            "Advanced kext customization is available through the CLI version."
        )
        
    def build_efi_gui(self):
        """Build the EFI in GUI mode"""
        if not self.customized_hardware:
            messagebox.showwarning(
                "Warning",
                "Please complete the configuration first:\n" +
                "1. Select hardware report\n" +
                "2. Select macOS version\n" +
                "3. Select SMBIOS model"
            )
            return
            
        # Check OCLP requirement
        if self.needs_oclp:
            result = messagebox.askyesno(
                "OpenCore Legacy Patcher Warning",
                "Your configuration requires OpenCore Legacy Patcher.\n\n" +
                "Important:\n" +
                "- OpenCore Legacy Patcher disables macOS security features\n" +
                "- It may lead to system instability\n" +
                "- It is not officially supported for Hackintosh\n\n" +
                "Do you want to continue?"
            )
            if not result:
                return
        
        # Disable build button during build
        if self.build_btn:
            self.build_btn.config(state=tk.DISABLED)
        if self.progress_var:
            self.progress_var.set(0)
        if self.build_log:
            self.build_log.delete('1.0', tk.END)
        
        # Get darwin version
        current_version = self.macos_version.get()
        darwin_version = current_version.split("(")[1].split(")")[0] if "(" in current_version else None
        smbios = self.smbios_model.get()
        
        # Run build in a separate thread
        thread = threading.Thread(
            target=self.run_build_process,
            args=(darwin_version, smbios)
        )
        thread.daemon = True
        thread.start()
        
    def run_build_process(self, macos_version, smbios_model):
        """Run the actual build process"""
        try:
            self.log_message("Starting EFI build process...")
            self.root.after(0, lambda: self.update_status("Building EFI...", 'info'))
            
            # Gather bootloader and kexts
            self.log_message("Gathering bootloader and kexts...")
            self.root.after(0, lambda: self.progress_var.set(10))
            self.ocpe.o.gather_bootloader_kexts(self.ocpe.k.kexts, macos_version)
            
            self.root.after(0, lambda: self.progress_var.set(30))
            
            # Build OpenCore EFI
            self.log_message("Building OpenCore EFI...")
            
            # Update progress during build
            steps = [
                "Copying EFI base to results folder",
                "Applying ACPI patches",
                "Copying kexts and snapshotting to config.plist",
                "Generating config.plist",
                "Cleaning up unused drivers, resources, and tools"
            ]
            
            for i, step in enumerate(steps):
                self.log_message(f"Step {i+1}/{len(steps)}: {step}")
                progress = 30 + ((i + 1) / len(steps)) * 60
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
            
            # Actually build the EFI
            self.ocpe.build_opencore_efi(
                self.customized_hardware,
                self.disabled_devices,
                smbios_model,
                macos_version,
                self.needs_oclp
            )
            
            self.root.after(0, lambda: self.progress_var.set(100))
            self.log_message("\nBuild completed successfully!")
            self.log_message(f"\nEFI has been built at: {self.ocpe.result_dir}")
            
            # Schedule GUI updates on main thread
            self.root.after(0, self.show_before_using_efi)
            if self.open_result_btn:
                self.root.after(0, lambda: self.open_result_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_status("Build completed!", 'success'))
            
            # Show success message on main thread
            self.root.after(0, lambda: messagebox.showinfo(
                "Build Complete",
                f"OpenCore EFI has been built successfully!\n\n" +
                f"Location: {self.ocpe.result_dir}\n\n" +
                "Please follow the USB mapping instructions."
            ))
            
        except Exception as e:
            self.log_message(f"\nError during build: {str(e)}")
            # Schedule error dialog on main thread
            self.root.after(0, lambda: messagebox.showerror(
                "Build Error",
                f"Failed to build EFI:\n\n{str(e)}"
            ))
            self.root.after(0, lambda: self.update_status("Build failed", 'error'))
        finally:
            if self.build_btn:
                self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL))
            
    def show_before_using_efi(self):
        """Show instructions before using the EFI"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Before Using EFI")
        info_window.geometry("800x600")
        info_window.configure(bg=COLORS['bg_main'])
        
        # Title
        title = tk.Label(
            info_window,
            text="⚠️  Before Using Your EFI",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title.pack(pady=SPACING['large'])
        
        # Text widget
        from tkinter import scrolledtext
        text_widget = scrolledtext.ScrolledText(
            info_window,
            wrap=tk.WORD,
            font=get_font('body'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING['large'],
            pady=SPACING['medium']
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=(0, SPACING['large']))
        
        # Get BIOS requirements
        bios_reqs = self.ocpe.check_bios_requirements(
            self.hardware_report_data, self.customized_hardware
        )
        
        instructions = "Please complete the following steps before using your EFI:\n\n"
        
        if bios_reqs:
            instructions += "🔧 BIOS/UEFI Settings Required:\n"
            for req in bios_reqs:
                instructions += f"  • {req}\n"
            instructions += "\n"
        
        instructions += """🔌 USB Mapping (Required):
  • Download USBToolBox from GitHub
  • Run the tool and map your USB ports
  • Add created UTBMap.kext into the EFI/OC/Kexts folder
  • Remove UTBDefault.kext from EFI/OC/Kexts folder
  • Edit config.plist:
      - Use ProperTree to open your config.plist
      - Run OC Snapshot by pressing Command/Ctrl + R
      - If you have more than 15 ports on a single controller,
        enable the XhciPortLimit patch
      - Save the file when finished

💿 Next Steps:
  • Create a macOS USB installer using UnPlugged (Windows) or diskutil (macOS)
  • Copy the EFI folder to your USB installer's EFI partition
  • Boot from the USB and install macOS
  • After installation, copy the EFI folder to your system drive's EFI partition

📚 For troubleshooting:
  https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/
"""
        
        text_widget.insert('1.0', instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(info_window, bg=COLORS['bg_main'])
        button_frame.pack(pady=SPACING['large'])
        
        # Open EFI folder button
        open_btn = tk.Button(
            button_frame,
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
            command=lambda: [self.open_result_folder(), info_window.destroy()]
        )
        open_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=get_font('body_bold'),
            bg=COLORS['bg_sidebar'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['medium'],
            command=info_window.destroy
        )
        close_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
    def open_result_folder(self):
        """Open the result folder"""
        if self.ocpe.result_dir and os.path.exists(self.ocpe.result_dir):
            self.ocpe.u.open_folder(self.ocpe.result_dir)
        else:
            messagebox.showwarning("Warning", "Result folder not found!")
            
    def run(self):
        """Start the GUI"""
        self.log_message("OpCore Simplify GUI started")
        self.log_message("Welcome to OpCore Simplify!")
        self.log_message("")
        self.root.mainloop()
