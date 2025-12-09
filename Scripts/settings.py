import os
from Scripts import utils


class Settings:
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
        self.u = utils.Utils()
        self.defaults = {
            "build_output_directory": "",
            "open_folder_after_build": True,
            "clean_temp_files_on_exit": True,
            "verbose_boot": True,
            "custom_boot_args": "",
            "include_beta_versions": False,
            "show_picker": True,
            "picker_mode": "External",
            "hide_auxiliary": False,
            "picker_variant": "Auto",
            "picker_timeout": 5,
            "disable_sip": True,
            "secure_boot_model": "Disabled",
            "random_smbios": True,
            "preserve_smbios": False,
            "theme": "light",
            "auto_update_check": True,
            "enable_debug_logging": False,
        }

        self.settings_file = self._get_settings_file_path()
        self.settings = self.load_settings()

    def _get_settings_file_path(self):
        script_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, "settings.json")

    def load_settings(self):
        loaded_settings = None

        try:
            loaded_settings = self.u.read_file(self.settings_file)

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
