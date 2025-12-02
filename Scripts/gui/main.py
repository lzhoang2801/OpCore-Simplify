"""
Main GUI application with sidebar navigation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time

from .styles import COLORS, SPACING, SIDEBAR_CONFIG, get_font
from .widgets import Sidebar, StatusBar, ConsoleRedirector
from .pages import UploadPage, CompatibilityPage, ConfigurationPage, BuildPage, ConsolePage, WiFiPage
from .icons import Icons

# Import from Scripts package
import sys
scripts_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
from datasets import os_data


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
        self.pages_initialized = set()  # Track which pages have been created
        self.console_redirected = False  # Track console redirection state
        
        # Placeholder for widgets that will be created by pages
        self.build_btn = None
        self.progress_var = None
        self.progress_bar = None
        self.build_log = None
        self.open_result_btn = None
        self.console_log = None
        
        # Set up GUI callback for ACPI folder selection
        self.ocpe.ac.gui_folder_callback = self.select_acpi_folder_gui
        
        # Set up GUI callback for interactive prompts
        self.ocpe.u.gui_callback = self.handle_gui_prompt
        self.ocpe.h.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.k.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.c.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.o.utils.gui_callback = self.handle_gui_prompt
        self.ocpe.ac.utils.gui_callback = self.handle_gui_prompt
        
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
        
        # Initialize page placeholders (lazy loading for performance)
        self.init_page_placeholders()
        
        # Show initial page
        self.sidebar.set_selected('upload')
        self.show_page('upload')
        
        # Set up console redirection after console page is created
        if self.console_log:
            sys.stdout = ConsoleRedirector(self.console_log, sys.stdout, self.root)
        
        # Set initial status
        self.status_bar.set_ready()
        
    def init_page_placeholders(self):
        """Initialize page placeholders for lazy loading"""
        # Create placeholders but don't build full UI yet
        # Only the upload page is created immediately for fast startup
        self.pages['upload'] = UploadPage(self.content_area, self)
        self.pages_initialized.add('upload')
        
        # Other pages will be created on first access
        self.pages['compatibility'] = None
        self.pages['configuration'] = None
        self.pages['build'] = None
        self.pages['wifi'] = None
        self.pages['console'] = None
        
    def ensure_page_created(self, page_id):
        """Ensure a page is created before showing it (lazy loading)"""
        if page_id in self.pages_initialized:
            return
        
        # Create the page on first access
        if page_id == 'compatibility':
            self.pages['compatibility'] = CompatibilityPage(self.content_area, self)
        elif page_id == 'configuration':
            self.pages['configuration'] = ConfigurationPage(self.content_area, self)
        elif page_id == 'build':
            self.pages['build'] = BuildPage(self.content_area, self)
        elif page_id == 'wifi':
            self.pages['wifi'] = WiFiPage(self.content_area, self)
        elif page_id == 'console':
            self.pages['console'] = ConsolePage(self.content_area, self)
            # Set up console redirection if not already done
            if self.console_log and not self.console_redirected:
                sys.stdout = ConsoleRedirector(self.console_log, sys.stdout, self.root)
                self.console_redirected = True
        
        self.pages_initialized.add(page_id)
            
    def on_nav_select(self, item_id):
        """Handle navigation item selection"""
        self.show_page(item_id)
        
    def show_page(self, page_id):
        """Show a specific page with optimized loading"""
        # Show loading indicator for better UX
        self.status_bar.set_status(f"Loading {page_id}...", 'info')
        
        # Hide current page
        if self.current_page and self.current_page in self.pages:
            current_page_widget = self.pages[self.current_page]
            if current_page_widget:
                current_page_widget.pack_forget()
        
        # Ensure the page is created (lazy loading)
        self.ensure_page_created(page_id)
        
        # Show new page
        if page_id in self.pages and self.pages[page_id]:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_id
            
            # Refresh page content (deferred to improve responsiveness)
            self.root.after(10, lambda: self.pages[page_id].refresh())
            
        # Update status
        self.root.after(50, lambda: self.status_bar.set_ready())
            
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
                
            # Get the Scripts directory and construct report path
            scripts_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            report_dir = os.path.join(scripts_dir, "..", "SysReport")
            
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
            
    def select_acpi_folder_gui(self):
        """GUI method to select ACPI tables folder"""
        folder_path = filedialog.askdirectory(
            title="Select ACPI Tables Folder"
        )
        return folder_path if folder_path else None
    
    def handle_gui_prompt(self, prompt_type, prompt_text, options=None):
        """
        Handle interactive prompts from backend code in GUI mode.
        
        Args:
            prompt_type: Type of prompt ('choice', 'confirm', 'info')
            prompt_text: The prompt message
            options: Additional options dict with keys like 'title', 'choices', 'default', etc.
        
        Returns:
            User's response as string
        """
        if options is None:
            options = {}
        
        # Use root.after to ensure GUI calls happen on main thread
        result_container = [None]
        
        def show_dialog():
            if prompt_type == 'info':
                # Just show info and wait for user to acknowledge
                messagebox.showinfo(
                    options.get('title', 'Information'),
                    prompt_text
                )
                result_container[0] = ""
                
            elif prompt_type == 'confirm':
                # Yes/No confirmation dialog
                title = options.get('title', 'Confirmation')
                message = options.get('message', prompt_text)
                warning = options.get('warning', '')
                
                full_message = message
                if warning:
                    full_message += f"\n\n⚠️ {warning}"
                
                result = messagebox.askyesno(title, full_message)
                result_container[0] = "yes" if result else "no"
                
            elif prompt_type == 'choice':
                # Multiple choice dialog
                self.show_choice_dialog(prompt_text, options, result_container)
        
        # Schedule on main thread and wait
        self.root.after(0, show_dialog)
        
        # Wait for result
        while result_container[0] is None:
            self.root.update()
            time.sleep(0.01)
        
        return result_container[0]
    
    def show_choice_dialog(self, prompt_text, options, result_container):
        """Show a choice dialog with multiple options"""
        dialog = tk.Toplevel(self.root)
        dialog.title(options.get('title', 'Select Option'))
        dialog.geometry("700x600")
        dialog.configure(bg=COLORS['bg_main'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog modal - prevent closing via window manager
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Title
        title_label = tk.Label(
            dialog,
            text=options.get('title', 'Select Option'),
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(pady=SPACING['large'])
        
        # Message
        message_label = tk.Label(
            dialog,
            text=options.get('message', prompt_text),
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            wraplength=650,
            justify=tk.LEFT
        )
        message_label.pack(pady=SPACING['medium'], padx=SPACING['large'])
        
        # Warning if present
        if options.get('warning'):
            warning_frame = tk.Frame(dialog, bg='#FFF3CD', relief=tk.SOLID, bd=1)
            warning_frame.pack(pady=SPACING['small'], padx=SPACING['large'], fill=tk.X)
            
            warning_label = tk.Label(
                warning_frame,
                text=f"⚠️ {options['warning']}",
                font=get_font('body'),
                bg='#FFF3CD',
                fg='#856404',
                wraplength=630,
                justify=tk.LEFT
            )
            warning_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Note if present
        if options.get('note'):
            note_frame = tk.Frame(dialog, bg='#D1ECF1', relief=tk.SOLID, bd=1)
            note_frame.pack(pady=SPACING['small'], padx=SPACING['large'], fill=tk.X)
            
            note_label = tk.Label(
                note_frame,
                text=f"ℹ️ {options['note']}",
                font=get_font('body'),
                bg='#D1ECF1',
                fg='#0C5460',
                wraplength=630,
                justify=tk.LEFT
            )
            note_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Choices
        choices = options.get('choices', [])
        default = options.get('default', '')
        
        selected_var = tk.StringVar(value=default)
        
        # Create scrollable frame for choices
        canvas = tk.Canvas(dialog, bg=COLORS['bg_main'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_main'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add radio buttons for each choice
        for choice in choices:
            choice_value = choice.get('value', '')
            choice_label = choice.get('label', choice_value)
            choice_desc = choice.get('description', '')
            
            # Frame for each choice
            choice_frame = tk.Frame(
                scrollable_frame,
                bg=COLORS['bg_card'],
                relief=tk.SOLID,
                bd=1
            )
            choice_frame.pack(pady=SPACING['small'], padx=SPACING['large'], fill=tk.X)
            
            # Radio button with label
            radio = tk.Radiobutton(
                choice_frame,
                text=choice_label,
                variable=selected_var,
                value=choice_value,
                font=get_font('body_bold'),
                bg=COLORS['bg_card'],
                fg=COLORS['text_primary'],
                selectcolor=COLORS['bg_card'],
                activebackground=COLORS['bg_card'],
                activeforeground=COLORS['primary'],
                bd=0,
                highlightthickness=0,
                padx=SPACING['medium'],
                pady=SPACING['small']
            )
            radio.pack(anchor=tk.W, fill=tk.X)
            
            # Description if present
            if choice_desc:
                desc_label = tk.Label(
                    choice_frame,
                    text=choice_desc,
                    font=get_font('caption'),
                    bg=COLORS['bg_card'],
                    fg=COLORS['text_secondary'],
                    wraplength=600,
                    justify=tk.LEFT
                )
                desc_label.pack(anchor=tk.W, padx=SPACING['xlarge'], pady=(0, SPACING['small']))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(SPACING['large'], 0), pady=SPACING['medium'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, SPACING['large']), pady=SPACING['medium'])
        
        # Button frame
        button_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
        button_frame.pack(pady=SPACING['large'])
        
        def on_select():
            result_container[0] = selected_var.get()
            dialog.destroy()
        
        def on_cancel():
            result_container[0] = default
            dialog.destroy()
        
        # Select button
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
            pady=SPACING['small'],
            command=on_select,
            highlightthickness=0
        )
        select_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['small'],
            command=on_cancel,
            highlightthickness=0
        )
        cancel_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        # Hover effects
        def on_select_enter(e):
            select_btn.config(bg=COLORS['primary_hover'])
        def on_select_leave(e):
            select_btn.config(bg=COLORS['primary'])
        def on_cancel_enter(e):
            cancel_btn.config(bg=COLORS['bg_hover'])
        def on_cancel_leave(e):
            cancel_btn.config(bg=COLORS['bg_hover'])
        
        select_btn.bind('<Enter>', on_select_enter)
        select_btn.bind('<Leave>', on_select_leave)
        cancel_btn.bind('<Enter>', on_cancel_enter)
        cancel_btn.bind('<Leave>', on_cancel_leave)
        
        # Wait for dialog to close
        dialog.wait_window()
            
    def load_hardware_report(self, path, data=None):
        """Load and validate hardware report - follows CLI flow"""
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
                
            # Store report path
            self.hardware_report_path.set(os.path.basename(path))
            self.hardware_report_data = data
            
            # Read ACPI tables if not already loaded
            self.update_status("Loading ACPI tables...", 'info')
            self.log_message("Loading ACPI tables...")
            
            if not self.ocpe.ac.ensure_dsdt():
                acpi_dir = os.path.join(os.path.dirname(path), "ACPI")
                if os.path.exists(acpi_dir):
                    self.ocpe.ac.read_acpi_tables(acpi_dir)
                else:
                    # Prompt for ACPI tables
                    self.ocpe.ac.select_acpi_tables()
            
            # Check compatibility (follows CLI behavior - check_compatibility modifies the data)
            self.update_status("Checking hardware compatibility...", 'info')
            self.log_message("Checking hardware compatibility...")
            self.hardware_report, self.native_macos_version, self.ocl_patched_macos_version = \
                self.ocpe.c.check_compatibility(data)
            
            # Auto-select macOS version (follows CLI behavior)
            self.log_message("Auto-selecting macOS version...")
            self.auto_select_macos_version()
            
            self.log_message("Hardware report loaded successfully!")
            self.update_status("Hardware report loaded", 'success')
            
            # Automatically show compatibility results (like CLI does)
            # Switch to compatibility page to show results
            self.sidebar.set_selected('compatibility')
            self.show_page('compatibility')
            
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
                    # Skip if device_props is not a dictionary (fix for AttributeError)
                    if not isinstance(device_props, dict):
                        continue
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
        
        # Apply this version (without prompting for kexts during initial load)
        self.apply_macos_version(suggested_macos_version, defer_kext_selection=True)
        
    def apply_macos_version(self, version, defer_kext_selection=False):
        """Apply a macOS version selection
        
        Args:
            version: macOS version to apply
            defer_kext_selection: If True, skip kext selection prompts during initial load
        """
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
            
            # Only select kexts and show prompts if not deferring
            # This prevents dialogs from appearing before user sees page 2
            if not defer_kext_selection:
                # Select required kexts (may show interactive prompts)
                self.needs_oclp = self.ocpe.k.select_required_kexts(
                    self.customized_hardware, version, self.needs_oclp, self.ocpe.ac.patches
                )
                
                # SMBIOS specific options
                self.ocpe.s.smbios_specific_options(
                    self.customized_hardware, smbios, version,
                    self.ocpe.ac.patches, self.ocpe.k
                )
            
            self.update_status("Configuration complete", 'success')
            
            if self.needs_oclp and not defer_kext_selection:
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
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground='#FFFFFF',
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['border_light'],
            highlightthickness=1
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
            pady=SPACING['small'],
            command=on_select,
            highlightthickness=0
        )
        select_btn.pack()
        
        # macOS-style hover effect
        def on_hover_enter(e):
            select_btn.config(bg=COLORS['primary_hover'])
        def on_hover_leave(e):
            select_btn.config(bg=COLORS['primary'])
        select_btn.bind('<Enter>', on_hover_enter)
        select_btn.bind('<Leave>', on_hover_leave)
        
    def customize_smbios_gui(self):
        """GUI for customizing SMBIOS with full selection dialog"""
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
        
        # Create SMBIOS selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select SMBIOS Model")
        dialog.geometry("700x600")
        dialog.configure(bg=COLORS['bg_main'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(
            dialog,
            text="Select SMBIOS Model",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(pady=SPACING['large'])
        
        # Current selection info
        current_frame = tk.Frame(dialog, bg='#D1ECF1', relief=tk.SOLID, bd=1)
        current_frame.pack(pady=SPACING['medium'], padx=SPACING['large'], fill=tk.X)
        
        current_label = tk.Label(
            current_frame,
            text=f"Current: {self.smbios_model.get()}",
            font=get_font('body_bold'),
            bg='#D1ECF1',
            fg='#0C5460'
        )
        current_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Platform info
        platform = self.customized_hardware.get("Motherboard", {}).get("Platform", "Unknown")
        info_label = tk.Label(
            dialog,
            text=f"Platform: {platform}",
            font=get_font('body'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        info_label.pack(pady=SPACING['small'])
        
        # SMBIOS options based on platform
        laptop_models = [
            "MacBookPro16,4", "MacBookPro16,3", "MacBookPro16,2", "MacBookPro16,1",
            "MacBookPro15,4", "MacBookPro15,3", "MacBookPro15,2", "MacBookPro15,1",
            "MacBookPro14,3", "MacBookPro14,2", "MacBookPro14,1",
            "MacBookPro13,3", "MacBookPro13,2", "MacBookPro13,1",
            "MacBookAir9,1", "MacBookAir8,2", "MacBookAir8,1"
        ]
        
        desktop_models = [
            "iMacPro1,1", "iMac20,2", "iMac20,1", "iMac19,1", "iMac18,3", "iMac18,2", "iMac18,1",
            "iMac17,1", "iMac16,2", "iMac15,1", "iMac14,4",
            "Macmini8,1", "Macmini7,1",
            "MacPro7,1", "MacPro6,1", "MacPro5,1"
        ]
        
        models = laptop_models if "Laptop" in platform else desktop_models
        
        # Scrollable list
        list_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=SPACING['medium'])
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground='#FFFFFF',
            relief=tk.FLAT,
            bd=1,
            highlightbackground=COLORS['border_light'],
            highlightthickness=1
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate list
        for model in models:
            listbox.insert(tk.END, model)
            if model == self.smbios_model.get():
                listbox.selection_set(listbox.size() - 1)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                new_model = listbox.get(selection[0])
                self.smbios_model.set(new_model)
                
                # Re-apply SMBIOS specific options
                self.ocpe.s.smbios_specific_options(
                    self.customized_hardware, new_model, darwin_version,
                    self.ocpe.ac.patches, self.ocpe.k
                )
                
                dialog.destroy()
                messagebox.showinfo(
                    "Success",
                    f"SMBIOS model changed to {new_model}"
                )
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
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
            pady=SPACING['small'],
            command=on_select,
            highlightthickness=0
        )
        select_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['small'],
            command=dialog.destroy,
            highlightthickness=0
        )
        cancel_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        # Hover effects
        def on_select_enter(e):
            select_btn.config(bg=COLORS['primary_hover'])
        def on_select_leave(e):
            select_btn.config(bg=COLORS['primary'])
        select_btn.bind('<Enter>', on_select_enter)
        select_btn.bind('<Leave>', on_select_leave)
        
    def customize_acpi_gui(self):
        """GUI for customizing ACPI patches with full patch viewer"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
        
        # Create ACPI patches dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("ACPI Patches")
        dialog.geometry("800x600")
        dialog.configure(bg=COLORS['bg_main'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(
            dialog,
            text="ACPI Patches Configuration",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(pady=SPACING['large'])
        
        # Info message
        info_frame = tk.Frame(dialog, bg='#D1ECF1', relief=tk.SOLID, bd=1)
        info_frame.pack(pady=SPACING['small'], padx=SPACING['large'], fill=tk.X)
        
        info_label = tk.Label(
            info_frame,
            text="ℹ️  ACPI patches have been automatically selected based on your hardware configuration",
            font=get_font('body'),
            bg='#D1ECF1',
            fg='#0C5460',
            wraplength=750
        )
        info_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Patches list with scrollbar
        list_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=SPACING['medium'])
        
        from tkinter import scrolledtext
        patches_text = scrolledtext.ScrolledText(
            list_frame,
            wrap=tk.WORD,
            font=get_font('body'),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=1,
            padx=SPACING['medium'],
            pady=SPACING['medium']
        )
        patches_text.pack(fill=tk.BOTH, expand=True)
        
        # Display patches
        if hasattr(self.ocpe.ac, 'patches') and self.ocpe.ac.patches:
            patches_text.insert('1.0', "Applied ACPI Patches:\n\n")
            for i, patch in enumerate(self.ocpe.ac.patches, 1):
                patch_name = patch.get('Comment', 'Unknown Patch')
                patches_text.insert(tk.END, f"{i}. {patch_name}\n")
        else:
            patches_text.insert('1.0', "No ACPI patches have been configured yet.\n\nPatches will be configured after selecting a macOS version.")
        
        patches_text.config(state=tk.DISABLED)
        
        # Note
        note_frame = tk.Frame(dialog, bg='#FFF3CD', relief=tk.SOLID, bd=1)
        note_frame.pack(pady=SPACING['medium'], padx=SPACING['large'], fill=tk.X)
        
        note_label = tk.Label(
            note_frame,
            text="💡 These patches are optimized for your specific hardware. Manual modification is not recommended unless you have advanced knowledge.",
            font=get_font('small'),
            bg='#FFF3CD',
            fg='#856404',
            wraplength=750
        )
        note_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Close button
        button_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
        button_frame.pack(pady=SPACING['large'])
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['small'],
            command=dialog.destroy,
            highlightthickness=0
        )
        close_btn.pack()
        
        # Hover effect
        def on_hover_enter(e):
            close_btn.config(bg=COLORS['primary_hover'])
        def on_hover_leave(e):
            close_btn.config(bg=COLORS['primary'])
        close_btn.bind('<Enter>', on_hover_enter)
        close_btn.bind('<Leave>', on_hover_leave)
        
    def customize_kexts_gui(self):
        """GUI for customizing kexts with full kext viewer and selection"""
        if not self.hardware_report:
            messagebox.showwarning("Warning", "Please select a hardware report first!")
            return
        
        # Ensure kexts have been selected
        self.ensure_kexts_selected()
        
        # Create kexts dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Kernel Extensions")
        dialog.geometry("800x600")
        dialog.configure(bg=COLORS['bg_main'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(
            dialog,
            text="Kernel Extensions Configuration",
            font=get_font('title'),
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        title_label.pack(pady=SPACING['large'])
        
        # Info message
        info_frame = tk.Frame(dialog, bg='#D1ECF1', relief=tk.SOLID, bd=1)
        info_frame.pack(pady=SPACING['small'], padx=SPACING['large'], fill=tk.X)
        
        info_label = tk.Label(
            info_frame,
            text="ℹ️  Kernel extensions have been automatically selected based on your hardware configuration",
            font=get_font('body'),
            bg='#D1ECF1',
            fg='#0C5460',
            wraplength=750
        )
        info_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Kexts list with scrollbar
        list_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['large'], pady=SPACING['medium'])
        
        # Create canvas for scrollable frame
        canvas = tk.Canvas(list_frame, bg=COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_secondary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display kexts with checkboxes
        if hasattr(self.ocpe.k, 'kexts') and self.ocpe.k.kexts:
            # Separate required and optional kexts
            required_kexts = [k for k in self.ocpe.k.kexts if k.checked and k.required]
            optional_kexts = [k for k in self.ocpe.k.kexts if k.checked and not k.required]
            
            if required_kexts:
                req_label = tk.Label(
                    scrollable_frame,
                    text="Required Kexts:",
                    font=get_font('body_bold'),
                    bg=COLORS['bg_secondary'],
                    fg=COLORS['text_primary'],
                    anchor=tk.W
                )
                req_label.pack(anchor=tk.W, pady=(SPACING['small'], SPACING['tiny']), padx=SPACING['medium'])
                
                for kext in required_kexts:
                    kext_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_secondary'])
                    kext_frame.pack(fill=tk.X, padx=SPACING['large'], pady=2)
                    
                    tk.Label(
                        kext_frame,
                        text=f"✓ {kext.name}",
                        font=get_font('body'),
                        bg=COLORS['bg_secondary'],
                        fg=COLORS['success'],
                        anchor=tk.W
                    ).pack(side=tk.LEFT)
            
            if optional_kexts:
                opt_label = tk.Label(
                    scrollable_frame,
                    text="\nOptional Kexts:",
                    font=get_font('body_bold'),
                    bg=COLORS['bg_secondary'],
                    fg=COLORS['text_primary'],
                    anchor=tk.W
                )
                opt_label.pack(anchor=tk.W, pady=(SPACING['medium'], SPACING['tiny']), padx=SPACING['medium'])
                
                for kext in optional_kexts:
                    kext_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_secondary'])
                    kext_frame.pack(fill=tk.X, padx=SPACING['large'], pady=2)
                    
                    tk.Label(
                        kext_frame,
                        text=f"✓ {kext.name}",
                        font=get_font('body'),
                        bg=COLORS['bg_secondary'],
                        fg=COLORS['primary'],
                        anchor=tk.W
                    ).pack(side=tk.LEFT)
        else:
            no_kext_label = tk.Label(
                scrollable_frame,
                text="No kexts have been configured yet.\n\nKexts will be configured after selecting a macOS version.",
                font=get_font('body'),
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_secondary'],
                justify=tk.LEFT
            )
            no_kext_label.pack(pady=SPACING['large'], padx=SPACING['large'])
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Note
        note_frame = tk.Frame(dialog, bg='#FFF3CD', relief=tk.SOLID, bd=1)
        note_frame.pack(pady=SPACING['medium'], padx=SPACING['large'], fill=tk.X)
        
        note_label = tk.Label(
            note_frame,
            text="💡 These kexts are optimized for your specific hardware. All required drivers and patches have been included.",
            font=get_font('small'),
            bg='#FFF3CD',
            fg='#856404',
            wraplength=750
        )
        note_label.pack(pady=SPACING['small'], padx=SPACING['small'])
        
        # Close button
        button_frame = tk.Frame(dialog, bg=COLORS['bg_main'])
        button_frame.pack(pady=SPACING['large'])
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['small'],
            command=dialog.destroy,
            highlightthickness=0
        )
        close_btn.pack()
        
        # Hover effect
        def on_hover_enter(e):
            close_btn.config(bg=COLORS['primary_hover'])
        def on_hover_leave(e):
            close_btn.config(bg=COLORS['primary'])
        close_btn.bind('<Enter>', on_hover_enter)
        close_btn.bind('<Leave>', on_hover_leave)
    
    def ensure_kexts_selected(self):
        """Ensure kexts have been selected (call this before building if kext selection was deferred)"""
        # Check if kexts were already selected by checking if any kext is checked
        if not hasattr(self.ocpe.k, 'kexts') or not any(kext.checked for kext in self.ocpe.k.kexts):
            # Kexts not selected yet, select them now with interactive prompts
            current_version = self.macos_version.get()
            darwin_version = current_version.split("(")[1].split(")")[0] if "(" in current_version else None
            if darwin_version and self.customized_hardware:
                self.needs_oclp = self.ocpe.k.select_required_kexts(
                    self.customized_hardware, darwin_version, self.needs_oclp, self.ocpe.ac.patches
                )
                
                # SMBIOS specific options
                smbios = self.smbios_model.get()
                self.ocpe.s.smbios_specific_options(
                    self.customized_hardware, smbios, darwin_version,
                    self.ocpe.ac.patches, self.ocpe.k
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
        
        # Ensure kexts have been selected (in case they were deferred during initial load)
        self.ensure_kexts_selected()
            
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
            bg=COLORS['bg_main'],
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
            text=Icons.format_with_text("folder", "Open EFI Folder"),
            font=get_font('body_bold'),
            bg=COLORS['primary'],
            fg='#FFFFFF',
            activebackground=COLORS['primary_dark'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['small'],
            command=lambda: [self.open_result_folder(), info_window.destroy()],
            highlightthickness=0
        )
        open_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=get_font('body_bold'),
            bg=COLORS['bg_hover'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_hover'],
            bd=0,
            relief=tk.FLAT,
            cursor='hand2',
            padx=SPACING['xlarge'],
            pady=SPACING['small'],
            command=info_window.destroy,
            highlightthickness=0
        )
        close_btn.pack(side=tk.LEFT, padx=SPACING['small'])
        
        # macOS-style hover effects
        def on_open_enter(e):
            open_btn.config(bg=COLORS['primary_hover'])
        def on_open_leave(e):
            open_btn.config(bg=COLORS['primary'])
        def on_close_enter(e):
            close_btn.config(bg=COLORS['bg_hover'])
        def on_close_leave(e):
            close_btn.config(bg=COLORS['bg_hover'])
        
        open_btn.bind('<Enter>', on_open_enter)
        open_btn.bind('<Leave>', on_open_leave)
        close_btn.bind('<Enter>', on_close_enter)
        close_btn.bind('<Leave>', on_close_leave)
        
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
