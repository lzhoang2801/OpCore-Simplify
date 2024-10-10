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

class Utils:
    def __init__(self, script_name = "OpCore Simplify"):
        self.script_name = script_name
    
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
            # Remove non-hex characters (e.g., hyphens)
            hex_string = re.sub(r'[^0-9a-fA-F]', '', string)

            if len(re.sub(r"\s+", "", string)) != len(hex_string):
                return string
            
            # Convert hex string to bytes
            bytes_data = binascii.unhexlify(hex_string)
            
            return bytes_data
        except binascii.Error:
            # Handle invalid hex string
            return string
    
    def int_to_hex(self, number):
        return format(number, '02X')
    
    def to_little_endian_hex(self, hex_string):
        hex_string = hex_string.lower().lstrip("0x")

        little_endian_hex = ''.join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)]))
        
        return little_endian_hex.upper()
    
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
        # Remove all surrounding quotes if present
        path = re.sub(r'^[\'"]+|[\'"]+$', '', path)
        
        # Remove trailing spaces
        path = path.strip()
        
        # Expand ~ to the user's home directory
        path = os.path.expanduser(path)
        
        # Normalize path separators for the target operating system
        if os.name == 'nt':  # Windows
            # Replace single backslashes with forward slashes
            path = path.replace('\\', '/')
            # Remove redundant slashes
            path = re.sub(r'/+', '/', path)
        else:
            # Remove backslashes
            path = path.replace('\\', '')
        
        # Normalize the path
        path = os.path.normpath(path)
        
        # Convert the path to an absolute path and normalize it according to the OS
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
        else:
            raise NotImplementedError("This function is only supported on macOS, Windows, and Linux.")

    def request_input(self, prompt="Press Enter to continue..."):
        try:
            user_response = input(prompt)
        except NameError:
            user_response = raw_input(prompt)
        
        if not isinstance(user_response, str):
            user_response = str(user_response)
        
        return user_response

    def clear_screen(self):
    	os.system('cls' if os.name=='nt' else 'clear')

    def head(self, text = None, width = 68, resize=True):
        if resize:
            self.adjust_window_size()
        self.clear_screen()
        if text == None:
            text = self.script_name
        separator = "#" * width
        title = " {} ".format(text)
        if len(title) > width - 2:
            title = title[:width-4] + "..."
        title = title.center(width - 2)  # Center the title within the width minus 2 for the '#' characters
        
        print("{}\n#{}#\n{}".format(separator, title, separator))
    
    def adjust_window_size(self, content=""):
        lines = content.splitlines()
        rows = len(lines)
        cols = max(len(line) for line in lines) if lines else 0
        print('\033[8;{};{}t'.format(max(rows+6, 30), max(cols+2, 100)))

    def exit_program(self):
        self.head()
        print("")
        print("For more information, to report errors, or to contribute to the product:")
        print("* Facebook: https://www.facebook.com/macforce2601")
        print("* Telegram: https://t.me/lzhoang2601")
        print("* GitHub: https://github.com/lzhoang2801/OpCore-Simplify")
        print("")

        print("Thank you for using our program!")
        print("")
        self.request_input("Press Enter to exit.")
        sys.exit(0)