import os
import sys
import json
import plistlib
import shutil
import re
import binascii
import subprocess
import pathlib
import zipfile
import tempfile
import traceback
import contextlib

class Utils:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Utils, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.gui_handler = None  # GUI handler object for direct dialog access
        self.gui_log_callback = None  # Callback for logging to build log/console
        self.gui_callback = None  # Callback for GUI prompts (backward compatibility)
        self.gui_progress_callback = None  # Callback for updating build progress in GUI
        self.gui_gathering_progress_callback = None  # Callback for updating gathering progress in GUI
        
        # Load settings for debug logging
        try:
            from Scripts import settings as settings_module
            self.settings = settings_module.Settings()
            self.debug_logging_enabled = self.settings.get_enable_debug_logging()
        except:
            self.settings = None
            self.debug_logging_enabled = False
    
    def debug_log(self, message):
        """Log debug messages if debug logging is enabled"""
        if self.debug_logging_enabled:
            self.log_gui(f"[DEBUG] {message}", level="Debug")

    def setup_smart_exception_handler(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            error_message = f"Uncaught exception detected:\n{error_details}"
            
            self.log_gui(error_message, level="Error")
            
            try:
                sys.__stderr__.write(f"\n[CRITICAL ERROR] {error_message}\n")
            except:
                pass

        sys.excepthook = handle_exception
        self.debug_log("Smart exception handler installed - unhandled errors will be auto-logged.")

    @contextlib.contextmanager
    def safe_block(self, task_name="Operation", suppress_error=True):
        try:
            yield
        except Exception as e:
            error_details = "".join(traceback.format_exc())
            self.log_gui(f"Error during '{task_name}': {str(e)}\n{error_details}", level="Error")
            if not suppress_error:
                raise

    def log_gui(self, message, level="Info", to_build_log=False):
        if self.gui_log_callback:
            try:
                self.gui_log_callback(message, level, to_build_log=to_build_log)
            except TypeError:
                self.gui_log_callback(message, level)
            return True
        return False

    
    def clean_temporary_dir(self):        
        temporary_dir = tempfile.gettempdir()
        
        for file in os.listdir(temporary_dir):
            if file.startswith("ocs_"):
    
                if not os.path.isdir(os.path.join(temporary_dir, file)):
                    continue

                try:
                    self.debug_log(f"Cleaning temporary directory: {file}")
                    shutil.rmtree(os.path.join(temporary_dir, file))
                except Exception as e:
                    self.debug_log(f"Failed to remove temp directory {file}: {e}")
                    pass
    
    def get_temporary_dir(self):
        return tempfile.mkdtemp(prefix="ocs_")

    def write_file(self, file_path, data):
        file_extension = os.path.splitext(file_path)[1]

        with open(file_path, "w" if file_extension == ".json" else "wb") as file:
            if file_extension == ".json":
                json.dump(data, file, indent=4)
            else:
                if file_extension == ".plist":
                    data = plistlib.dumps(data)

                file.write(data)

    def read_file(self, file_path):
        if not os.path.exists(file_path):
            return None

        file_extension = os.path.splitext(file_path)[1]

        with open(file_path, "r" if file_extension == ".json" else "rb") as file_handle:
            if file_extension == ".plist":
                data = plistlib.load(file_handle)
            elif file_extension == ".json":
                data = json.load(file_handle)
            else:
                data = file_handle.read()
            return data

    def find_matching_paths(self, root_path, extension_filter=None, name_filter=None, type_filter=None):

        def is_valid_item(name):
            if name.startswith("."):
                return False
            if extension_filter and not name.lower().endswith(extension_filter.lower()):
                return False
            if name_filter and name_filter not in name:
                return False
            return True
        
        found_paths = []

        for root, dirs, files in os.walk(root_path):
            relative_root = root.replace(root_path, "")[1:]

            if type_filter in (None, "dir"):
                for d in dirs:
                    if is_valid_item(d):
                        found_paths.append((os.path.join(relative_root, d), "dir"))

            if type_filter in (None, "file"):
                for file in files:
                    if is_valid_item(file):
                        found_paths.append((os.path.join(relative_root, file), "file"))

        return sorted(found_paths, key=lambda path: path[0])

    def create_folder(self, path, remove_content=False):
        if os.path.exists(path):
            if remove_content:
                shutil.rmtree(path)
                os.makedirs(path)
        else:
            os.makedirs(path)

    def hex_to_bytes(self, string):
        try:
            hex_string = re.sub(r'[^0-9a-fA-F]', '', string)

            if len(re.sub(r"\s+", "", string)) != len(hex_string):
                return string
            
            return binascii.unhexlify(hex_string)
        except binascii.Error:
            return string
    
    def int_to_hex(self, number):
        return format(number, '02X')
    
    def to_little_endian_hex(self, hex_string):
        hex_string = hex_string.lower().lstrip("0x")

        return ''.join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)])).upper()
    
    def string_to_hex(self, string):
        return ''.join(format(ord(char), '02X') for char in string)
    
    def extract_zip_file(self, zip_path, extraction_directory=None):
        if extraction_directory is None:
            extraction_directory = os.path.splitext(zip_path)[0]
        
        os.makedirs(extraction_directory, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_directory)

    def contains_any(self, data, search_item, start=0, end=None):
        return next((item for item in data[start:end] if item.lower() in search_item.lower()), None)

    def normalize_path(self, path):
        path = re.sub(r'^[\'"]+|[\'"]+$', '', path)
        
        path = path.strip()
        
        path = os.path.expanduser(path)
        
        if os.name == 'nt':
            path = path.replace('\\', '/')
            path = re.sub(r'/+', '/', path)
        else:
            path = path.replace('\\', '')
        
        path = os.path.normpath(path)
        
        return str(pathlib.Path(path).resolve())
    
    def parse_darwin_version(self, darwin_version):
        major, minor, patch = map(int, darwin_version.split('.'))
        return major, minor, patch
    
    def open_folder(self, folder_path):
        if os.name == 'posix':
            if 'darwin' in os.uname().sysname.lower():
                subprocess.run(['open', folder_path])
            else:
                subprocess.run(['xdg-open', folder_path])
        elif os.name == 'nt':
            os.startfile(folder_path)

    def progress_bar(self, title, steps, current_step_index, done=False):
        if done:
            progress = 100
        else:
            progress = int((current_step_index / len(steps)) * 100)
        
        self.gui_progress_callback(title, steps, current_step_index, progress, done)