"""
Settings management for OpCore Simplify
Handles loading, saving, and accessing user preferences
"""

import os
import json

class Settings:
    """Singleton settings manager"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Default settings
        self.defaults = {
            # Build Settings
            "build_output_directory": "",  # Empty means use temporary directory
            "open_folder_after_build": True,  # Auto-open result folder after build
            "clean_temp_files_on_exit": True,  # Clean temporary files when exiting
            
            # Boot Arguments
            "verbose_boot": True,  # Include -v debug=0x100 keepsyms=1 in boot-args
            "custom_boot_args": "",  # Additional boot arguments
            
            # Appearance
            "theme": "light",  # light or dark
            
            # Updates & Downloads
            "auto_update_check": True,  # Check for updates on startup
            "verify_download_integrity": True,  # Verify SHA256 of downloaded files
            "force_redownload": False,  # Force re-download even if file exists
            
            # macOS Version Settings
            "include_beta_versions": False,  # Show beta macOS versions in selection
            "preferred_macos_version": "",  # Preferred macOS version (empty = auto-select)
            
            # OpenCore Boot Picker
            "show_picker": True,  # Show OpenCore boot picker
            "picker_mode": "Auto",  # "Auto", "Builtin", "External"
            "hide_auxiliary": False,  # Hide auxiliary entries in picker
            "picker_timeout": 5,  # Boot picker timeout in seconds (0 = no timeout)
            "picker_variant": "Auto",  # "Auto", "Acidanthera/GoldenGate", etc.
            
            # Security Settings
            "disable_sip": True,  # Disable System Integrity Protection
            "secure_boot_model": "Default",  # "Default", "Disabled", "j137", etc.
            "vault": "Optional",  # "Optional", "Basic", "Secure"
            
            # SMBIOS Settings
            "random_smbios": True,  # Generate random serial numbers
            "preserve_smbios": False,  # Preserve SMBIOS between builds
            "custom_serial_number": "",  # Custom serial number (if not random)
            "custom_mlb": "",  # Custom MLB (if not random)
            "custom_rom": "",  # Custom ROM (if not random)
            
            # Advanced Settings
            "enable_debug_logging": False,  # Enable detailed debug logging
            "skip_acpi_validation": False,  # Skip ACPI validation warnings
            "force_load_incompatible_kexts": False,  # Force load kexts on unsupported macOS
        }
        
        # Get settings file path
        self.settings_file = self._get_settings_file_path()
        
        # Load settings
        self.settings = self.load()
    
    def _get_settings_file_path(self):
        """Get the path to the settings file"""
        # Store settings in the same directory as the script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, "settings.json")
    
    def load(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.defaults.copy()
                    settings.update(loaded_settings)
                    return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save()
    
    # Build Settings
    def get_build_output_directory(self):
        """Get the build output directory, returns None if using temporary"""
        output_dir = self.get("build_output_directory", "")
        if output_dir and os.path.isdir(output_dir):
            return output_dir
        return None
    
    def get_open_folder_after_build(self):
        """Get auto-open folder setting"""
        return self.get("open_folder_after_build", True)
    
    def get_clean_temp_files_on_exit(self):
        """Get clean temp files setting"""
        return self.get("clean_temp_files_on_exit", True)
    
    # Boot Arguments
    def get_verbose_boot(self):
        """Get verbose boot setting"""
        return self.get("verbose_boot", True)
    
    def get_custom_boot_args(self):
        """Get custom boot arguments"""
        return self.get("custom_boot_args", "")
    
    # Appearance
    def get_theme(self):
        """Get theme preference"""
        return self.get("theme", "light")
    
    # Updates & Downloads
    def get_auto_update_check(self):
        """Get auto-update check setting"""
        return self.get("auto_update_check", True)
    
    def get_verify_download_integrity(self):
        """Get download integrity verification setting"""
        return self.get("verify_download_integrity", True)
    
    def get_force_redownload(self):
        """Get force redownload setting"""
        return self.get("force_redownload", False)
    
    # macOS Version Settings
    def get_include_beta_versions(self):
        """Get beta versions inclusion setting"""
        return self.get("include_beta_versions", False)
    
    def get_preferred_macos_version(self):
        """Get preferred macOS version"""
        return self.get("preferred_macos_version", "")
    
    # OpenCore Boot Picker
    def get_show_picker(self):
        """Get show picker setting"""
        return self.get("show_picker", True)
    
    def get_picker_mode(self):
        """Get picker mode"""
        return self.get("picker_mode", "Auto")
    
    def get_hide_auxiliary(self):
        """Get hide auxiliary setting"""
        return self.get("hide_auxiliary", False)
    
    def get_picker_timeout(self):
        """Get picker timeout"""
        return self.get("picker_timeout", 5)
    
    def get_picker_variant(self):
        """Get picker variant"""
        return self.get("picker_variant", "Auto")
    
    # Security Settings
    def get_disable_sip(self):
        """Get disable SIP setting"""
        return self.get("disable_sip", True)
    
    def get_secure_boot_model(self):
        """Get secure boot model"""
        return self.get("secure_boot_model", "Default")
    
    def get_vault(self):
        """Get vault setting"""
        return self.get("vault", "Optional")
    
    # SMBIOS Settings
    def get_random_smbios(self):
        """Get random SMBIOS setting"""
        return self.get("random_smbios", True)
    
    def get_preserve_smbios(self):
        """Get preserve SMBIOS setting"""
        return self.get("preserve_smbios", False)
    
    def get_custom_serial_number(self):
        """Get custom serial number"""
        return self.get("custom_serial_number", "")
    
    def get_custom_mlb(self):
        """Get custom MLB"""
        return self.get("custom_mlb", "")
    
    def get_custom_rom(self):
        """Get custom ROM"""
        return self.get("custom_rom", "")
    
    # Advanced Settings
    def get_enable_debug_logging(self):
        """Get debug logging setting"""
        return self.get("enable_debug_logging", False)
    
    def get_skip_acpi_validation(self):
        """Get skip ACPI validation setting"""
        return self.get("skip_acpi_validation", False)
    
    def get_force_load_incompatible_kexts(self):
        """Get force load incompatible kexts setting"""
        return self.get("force_load_incompatible_kexts", False)
