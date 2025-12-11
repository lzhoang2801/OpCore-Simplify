import os
from Scripts import utils


class Settings:
    def __init__(self, utils_instance=None):
        self.u = utils_instance if utils_instance else utils.Utils()
        self.defaults = {
            "build_output_directory": "",
            "open_folder_after_build": True,
            "clean_temp_files_on_exit": True,
            "verbose_boot": True,
            "custom_boot_args": "",
            "include_beta_versions": False,
            "hide_auxiliary": False,
            "picker_mode": "External",
            "picker_variant": "Auto",
            "show_picker": True,
            "picker_timeout": 5,
            "secure_boot_model": "Disabled",
            "disable_sip": True,
            "random_smbios": True,
            "preserve_smbios": False,
            "theme": "Light",
            "auto_update_check": True,
            "enable_debug_logging": False,
        }

        self.settings_file = self._get_settings_file_path()
        self.settings = self.load_settings()

    def _get_settings_file_path(self):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, "settings.json")

    def load_settings(self):
        try:
            loaded_settings = self.u.read_file(self.settings_file)
            
            if loaded_settings is not None:
                return loaded_settings
        except Exception as e:
            print(f"Error loading settings: {e}")

        return self.defaults.copy()

    def save_settings(self):
        try:
            self.u.write_file(self.settings_file, self.settings)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, self.defaults.get(key, default))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def __getattr__(self, name):
        if name.startswith("get_"):
            key = name[4:]
            if key in self.defaults:
                return lambda: self.get(key)

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'")
