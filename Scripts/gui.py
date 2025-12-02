import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from Scripts import utils
from Scripts.datasets import os_data


class OpCoreGUI:
    def __init__(self, ocpe_instance):
        self.ocpe = ocpe_instance
        self.root = tk.Tk()
        self.root.title("OpCore Simplify - GUI")
        self.root.geometry("900x700")
        
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
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Title section
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="OpCore Simplify", 
                               font=("Arial", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                   text="OpenCore EFI Builder with GUI",
                                   font=("Arial", 12))
        subtitle_label.pack()
        
        # Main content notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tabs
        self.create_main_tab()
        self.create_customization_tab()
        self.create_build_tab()
        self.create_log_tab()
        
        # Status bar at bottom
        self.status_bar = ttk.Label(main_container, text="Ready", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
    def create_main_tab(self):
        """Create the main configuration tab"""
        main_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_tab, text="Configuration")
        
        # Configure grid
        main_tab.columnconfigure(1, weight=1)
        
        # Current Configuration Section
        config_label = ttk.Label(main_tab, text="Current Configuration:", 
                                font=("Arial", 12, "bold"))
        config_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Hardware Report
        ttk.Label(main_tab, text="Hardware Report:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_tab, textvariable=self.hardware_report_path, 
                 foreground="blue").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # macOS Version
        ttk.Label(main_tab, text="macOS Version:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_tab, textvariable=self.macos_version,
                 foreground="blue").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # SMBIOS Model
        ttk.Label(main_tab, text="SMBIOS Model:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_tab, textvariable=self.smbios_model,
                 foreground="blue").grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Disabled Devices
        ttk.Label(main_tab, text="Disabled Devices:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_tab, textvariable=self.disabled_devices_text,
                 foreground="blue").grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Separator
        ttk.Separator(main_tab, orient=tk.HORIZONTAL).grid(row=5, column=0, 
                                                           columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        # Action Buttons Section
        actions_label = ttk.Label(main_tab, text="Actions:", 
                                 font=("Arial", 12, "bold"))
        actions_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Button frame for better layout
        button_frame = ttk.Frame(main_tab)
        button_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Select Hardware Report button
        select_hw_btn = ttk.Button(button_frame, text="1. Select Hardware Report",
                                   command=self.select_hardware_report_gui,
                                   width=30)
        select_hw_btn.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        
        # Select macOS Version button
        select_macos_btn = ttk.Button(button_frame, text="2. Select macOS Version",
                                      command=self.select_macos_version_gui,
                                      width=30)
        select_macos_btn.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        
        # Customize SMBIOS button
        customize_smbios_btn = ttk.Button(button_frame, text="3. Customize SMBIOS Model",
                                         command=self.customize_smbios_gui,
                                         width=30)
        customize_smbios_btn.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_tab, text="Instructions", padding="10")
        instructions_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_tab.rowconfigure(8, weight=1)
        
        instructions_text = tk.Text(instructions_frame, wrap=tk.WORD, height=10)
        instructions_text.pack(fill=tk.BOTH, expand=True)
        
        instructions = """Welcome to OpCore Simplify GUI!

Follow these steps to build your OpenCore EFI:

1. Select Hardware Report: Choose a hardware report JSON file or export one using Hardware Sniffer
2. Select macOS Version: Choose the macOS version you want to use
3. Customize SMBIOS: Select the appropriate SMBIOS model for your hardware
4. (Optional) Customize ACPI patches and Kexts in the Customization tab
5. Build OpenCore EFI in the Build tab

For more information, visit: https://github.com/lzhoang2801/OpCore-Simplify"""
        
        instructions_text.insert(1.0, instructions)
        instructions_text.config(state=tk.DISABLED)
        
    def create_customization_tab(self):
        """Create the customization tab for ACPI and Kexts"""
        custom_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(custom_tab, text="Customization")
        
        custom_tab.columnconfigure(0, weight=1)
        custom_tab.rowconfigure(2, weight=1)
        
        # ACPI Patches Section
        acpi_label = ttk.Label(custom_tab, text="ACPI Patches", 
                              font=("Arial", 12, "bold"))
        acpi_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        acpi_btn = ttk.Button(custom_tab, text="Customize ACPI Patches",
                             command=self.customize_acpi_gui,
                             width=30)
        acpi_btn.grid(row=1, column=0, pady=5, sticky=tk.W)
        
        # Kexts Section
        kext_label = ttk.Label(custom_tab, text="Kexts Configuration", 
                              font=("Arial", 12, "bold"))
        kext_label.grid(row=2, column=0, sticky=tk.W, pady=(20, 10))
        
        kext_btn = ttk.Button(custom_tab, text="Customize Kexts",
                             command=self.customize_kexts_gui,
                             width=30)
        kext_btn.grid(row=3, column=0, pady=5, sticky=tk.W)
        
        # Info text
        info_frame = ttk.LabelFrame(custom_tab, text="Information", padding="10")
        info_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        custom_tab.rowconfigure(4, weight=1)
        
        info_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info = """Customization Options:

ACPI Patches: Customize the ACPI patches that will be applied to your system. 
OpCore Simplify automatically detects and applies necessary patches, but you can 
review and modify them here if needed.

Kexts: Customize kernel extensions (kexts) for your system. The tool automatically 
selects required kexts based on your hardware, but you can enable or disable specific 
kexts or force load them on unsupported macOS versions.

Note: Most users should use the automatic detection. Only customize if you know 
what you're doing."""
        
        info_text.insert(1.0, info)
        info_text.config(state=tk.DISABLED)
        
    def create_build_tab(self):
        """Create the build tab"""
        build_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(build_tab, text="Build EFI")
        
        build_tab.columnconfigure(0, weight=1)
        build_tab.rowconfigure(3, weight=1)
        
        # Build button
        build_label = ttk.Label(build_tab, text="Build OpenCore EFI", 
                               font=("Arial", 14, "bold"))
        build_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))
        
        self.build_btn = ttk.Button(build_tab, text="Build OpenCore EFI",
                                    command=self.build_efi_gui,
                                    width=30)
        self.build_btn.grid(row=1, column=0, pady=10, sticky=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(build_tab, variable=self.progress_var,
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Build log
        log_frame = ttk.LabelFrame(build_tab, text="Build Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.build_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.build_log.pack(fill=tk.BOTH, expand=True)
        
        # Result folder button (initially hidden)
        self.open_result_btn = ttk.Button(build_tab, text="Open Result Folder",
                                         command=self.open_result_folder,
                                         state=tk.DISABLED,
                                         width=30)
        self.open_result_btn.grid(row=4, column=0, pady=10, sticky=tk.W)
        
    def create_log_tab(self):
        """Create the log/console tab"""
        log_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(log_tab, text="Console Log")
        
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)
        
        # Console log
        self.console_log = scrolledtext.ScrolledText(log_tab, wrap=tk.WORD)
        self.console_log.pack(fill=tk.BOTH, expand=True)
        
        # Redirect stdout to console log
        sys.stdout = ConsoleRedirector(self.console_log, sys.stdout)
        
    def log_message(self, message):
        """Log a message to both console and build log"""
        print(message)
        if hasattr(self, 'build_log'):
            self.build_log.insert(tk.END, message + "\n")
            self.build_log.see(tk.END)
            
    def update_status(self, message):
        """Update the status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
        
    def select_hardware_report_gui(self):
        """GUI version of hardware report selection"""
        self.update_status("Selecting hardware report...")
        
        # Option to export or select file
        choice = messagebox.askquestion("Select Hardware Report",
                                       "Do you want to export a hardware report?\n\n" +
                                       "Select 'Yes' to export using Hardware Sniffer\n" +
                                       "Select 'No' to choose an existing report file")
        
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
                return
                
            report_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "SysReport")
            
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
                messagebox.showerror("Export Error", 
                                   f"Could not export the hardware report.\n{error_message}\n" +
                                   "Please try again or use Hardware Sniffer manually.")
                return
            else:
                report_path = os.path.join(report_dir, "Report.json")
                acpitables_dir = os.path.join(report_dir, "ACPI")
                
                report_data = self.ocpe.u.read_file(report_path)
                self.ocpe.ac.read_acpi_tables(acpitables_dir)
                
                self.load_hardware_report(report_path, report_data)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export hardware report: {str(e)}")
            
    def load_hardware_report(self, path, data=None):
        """Load and validate hardware report"""
        try:
            self.log_message(f"Loading hardware report from: {path}")
            
            # Validate report
            is_valid, errors, warnings, data = self.ocpe.v.validate_report(path)
            
            if not is_valid or errors:
                error_msg = "Hardware report validation failed:\n\n"
                if errors:
                    error_msg += "Errors:\n" + "\n".join(f"- {e}" for e in errors)
                if warnings:
                    error_msg += "\n\nWarnings:\n" + "\n".join(f"- {w}" for w in warnings)
                
                messagebox.showerror("Validation Error", error_msg + 
                                   "\n\nPlease re-export the hardware report and try again.")
                return
                
            # Store report
            self.hardware_report_path.set(path)
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
            self.update_status("Hardware report loaded")
            
            messagebox.showinfo("Success", "Hardware report loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hardware report: {str(e)}")
            
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
                            device_id = device_props.get("Device ID", "0"*8)[5:]
                            
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
            
            if self.needs_oclp:
                messagebox.showwarning("OpenCore Legacy Patcher Required",
                                     "Your hardware requires OpenCore Legacy Patcher.\n\n" +
                                     "This will be configured during the build process.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply macOS version: {str(e)}")
            
    def select_macos_version_gui(self):
        """GUI for selecting macOS version"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
            
        # Create selection window
        version_window = tk.Toplevel(self.root)
        version_window.title("Select macOS Version")
        version_window.geometry("600x400")
        
        ttk.Label(version_window, text="Select macOS Version", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create listbox for versions
        listbox_frame = ttk.Frame(version_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        version_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set,
                                     font=("Arial", 10))
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
                messagebox.showinfo("Success", f"macOS version set to {os_data.get_macos_name_by_darwin(version)}")
        
        ttk.Button(version_window, text="Select", command=on_select).pack(pady=10)
        
    def customize_smbios_gui(self):
        """GUI for customizing SMBIOS"""
        if not self.customized_hardware:
            messagebox.showwarning("Warning", "Please select a hardware report and macOS version first!")
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
            
        # Create SMBIOS selection window
        smbios_window = tk.Toplevel(self.root)
        smbios_window.title("Select SMBIOS Model")
        smbios_window.geometry("500x400")
        
        ttk.Label(smbios_window, text="Select SMBIOS Model", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create listbox
        listbox_frame = ttk.Frame(smbios_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        smbios_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set,
                                    font=("Arial", 10))
        smbios_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=smbios_listbox.yview)
        
        # Get available SMBIOS models (simplified)
        # In real implementation, would use the same logic as the CLI version
        available_models = ["iMac19,1", "iMac20,1", "MacBookPro15,1", "MacBookPro16,1", 
                          "MacPro7,1", "iMacPro1,1"]
        
        for model in available_models:
            smbios_listbox.insert(tk.END, model)
        
        def on_select():
            selection = smbios_listbox.curselection()
            if selection:
                selected_model = available_models[selection[0]]
                self.smbios_model.set(selected_model)
                
                # Apply SMBIOS specific options
                self.ocpe.s.smbios_specific_options(
                    self.customized_hardware, selected_model, darwin_version,
                    self.ocpe.ac.patches, self.ocpe.k
                )
                
                smbios_window.destroy()
                messagebox.showinfo("Success", f"SMBIOS model set to {selected_model}")
        
        ttk.Button(smbios_window, text="Select", command=on_select).pack(pady=10)
        
    def customize_acpi_gui(self):
        """GUI for customizing ACPI patches"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
            
        messagebox.showinfo("ACPI Customization", 
                          "ACPI patches have been automatically configured.\n\n" +
                          "Advanced customization is available through the CLI version.")
        
    def customize_kexts_gui(self):
        """GUI for customizing kexts"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
            
        messagebox.showinfo("Kext Customization",
                          "Kexts have been automatically configured.\n\n" +
                          "Advanced customization is available through the CLI version.")
        
    def build_efi_gui(self):
        """Build the EFI in GUI mode"""
        if not self.customized_hardware:
            messagebox.showwarning("Warning", 
                                 "Please complete the configuration first:\n" +
                                 "1. Select hardware report\n" +
                                 "2. Select macOS version\n" +
                                 "3. Select SMBIOS model")
            return
            
        # Check OCLP requirement
        if self.needs_oclp:
            result = messagebox.askyesno("OpenCore Legacy Patcher Warning",
                                        "Your configuration requires OpenCore Legacy Patcher.\n\n" +
                                        "Important:\n" +
                                        "- OpenCore Legacy Patcher disables macOS security features\n" +
                                        "- It may lead to system instability\n" +
                                        "- It is not officially supported for Hackintosh\n\n" +
                                        "Do you want to continue?")
            if not result:
                return
        
        # Disable build button during build
        self.build_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.build_log.delete(1.0, tk.END)
        
        # Get darwin version
        current_version = self.macos_version.get()
        darwin_version = current_version.split("(")[1].split(")")[0] if "(" in current_version else None
        smbios = self.smbios_model.get()
        
        # Run build in a separate thread
        thread = threading.Thread(target=self.run_build_process,
                                 args=(darwin_version, smbios))
        thread.daemon = True
        thread.start()
        
    def run_build_process(self, macos_version, smbios_model):
        """Run the actual build process"""
        try:
            self.log_message("Starting EFI build process...")
            self.root.after(0, lambda: self.update_status("Building EFI..."))
            
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
            self.root.after(0, lambda: self.open_result_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_status("Build completed!"))
            
            # Show success message on main thread
            self.root.after(0, lambda: messagebox.showinfo("Build Complete",
                              f"OpenCore EFI has been built successfully!\n\n" +
                              f"Location: {self.ocpe.result_dir}\n\n" +
                              "Please follow the USB mapping instructions."))
            
        except Exception as e:
            self.log_message(f"\nError during build: {str(e)}")
            # Schedule error dialog on main thread
            self.root.after(0, lambda: messagebox.showerror("Build Error", 
                              f"Failed to build EFI:\n\n{str(e)}"))
            self.root.after(0, lambda: self.update_status("Build failed"))
        finally:
            self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL))
            
    def show_before_using_efi(self):
        """Show instructions before using the EFI"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Before Using EFI")
        info_window.geometry("700x500")
        
        ttk.Label(info_window, text="Before Using Your EFI", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get BIOS requirements
        bios_reqs = self.ocpe.check_bios_requirements(
            self.hardware_report_data, self.customized_hardware
        )
        
        instructions = "Please complete the following steps:\n\n"
        
        if bios_reqs:
            instructions += "BIOS/UEFI Settings Required:\n"
            for req in bios_reqs:
                instructions += f"  - {req}\n"
            instructions += "\n"
        
        instructions += """USB Mapping:
  - Use USBToolBox tool to map USB ports
  - Add created UTBMap.kext into the EFI/OC/Kexts folder
  - Remove UTBDefault.kext in the EFI/OC/Kexts folder
  - Edit config.plist:
      - Use ProperTree to open your config.plist
      - Run OC Snapshot by pressing Command/Ctrl + R
      - If you have more than 15 ports on a single controller, enable the XhciPortLimit patch
      - Save the file when finished

Next Steps:
  - Create a macOS USB installer using UnPlugged (Windows) or diskutil (macOS)
  - Copy the EFI folder to your USB installer's EFI partition
  - Boot from the USB and install macOS
  - After installation, copy the EFI folder to your system drive's EFI partition

For troubleshooting, refer to: https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/
"""
        
        text_widget.insert(1.0, instructions)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(info_window, text="Open EFI Folder",
                  command=self.open_result_folder).pack(pady=10)
        
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
        self.root.mainloop()


class ConsoleRedirector:
    """Redirect stdout to a text widget"""
    def __init__(self, text_widget, original_stdout):
        self.text_widget = text_widget
        self.original_stdout = original_stdout
        
    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()
        # Also write to original stdout
        self.original_stdout.write(message)
        
    def flush(self):
        self.original_stdout.flush()
