import os
import json
import plistlib
import shutil
import re
import binascii
import subprocess
import zipfile
import tempfile
import traceback
import contextlib
import logging

class Utils:
    def __init__(self):
        self.gui_handler = None
        self.logger = logging.getLogger("OpCoreSimplify")

    @contextlib.contextmanager
    def safe_block(self, task_name="Operation", suppress_error=True):
        try:
            yield
        except Exception as e:
            error_details = "".join(traceback.format_exc())
            self.log_message("Error during '{}': {}\n{}".format(task_name, str(e), error_details), level="ERROR")
            if not suppress_error:
                raise

    def log_message(self, message, level="INFO", to_build_log=False):
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        extra = {'to_build_log': to_build_log}
        
        self.logger.log(log_level, message, extra=extra)
        return True

    def clean_temporary_dir(self):
        temporary_dir = tempfile.gettempdir()
        
        for file in os.listdir(temporary_dir):
            if file.startswith("ocs_"):
    
                if not os.path.isdir(os.path.join(temporary_dir, file)):
                    continue

                try:
                    shutil.rmtree(os.path.join(temporary_dir, file))
                except Exception as e:
                    self.log_message("[UTILS] Failed to remove temp directory {}: {}".format(file, e), "Error")
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