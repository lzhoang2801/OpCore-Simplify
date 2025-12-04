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

class Utils:
    def __init__(self, script_name = "OpCore Simplify"):
        self.script_name = script_name
        self.gui_callback = None  # Callback for GUI mode interactions

    def clean_temporary_dir(self):
        temporary_dir = tempfile.gettempdir()
        
        for file in os.listdir(temporary_dir):
            if file.startswith("ocs_"):
    
                if not os.path.isdir(os.path.join(temporary_dir, file)):
                    continue

                try:
                    shutil.rmtree(os.path.join(temporary_dir, file))
                except Exception as e:
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

    def request_input(self, prompt="Press Enter to continue...", gui_type=None, gui_options=None):
        """
        Request input from user, using GUI callback if available.
        
        Args:
            prompt: The prompt text
            gui_type: Type of GUI dialog (e.g., 'choice', 'confirm', 'info')
            gui_options: Additional options for GUI dialog
        
        Returns:
            User's response as string
        """
        # If GUI callback is available and gui_type is specified, use GUI
        if self.gui_callback and gui_type:
            return self.gui_callback(gui_type, prompt, gui_options)
        
        # Fall back to CLI
        if sys.version_info[0] < 3:
            user_response = raw_input(prompt)
        else:
            user_response = input(prompt)
        
        if not isinstance(user_response, str):
            user_response = str(user_response)
        
        return user_response

    def progress_bar(self, title, steps, current_step_index, done=False):
        # Check if GUI callback exists for progress updates
        if hasattr(self, 'gui_progress_callback') and self.gui_progress_callback:
            # Calculate progress percentage
            if done:
                progress = 100
            else:
                progress = int((current_step_index / len(steps)) * 100)
            
            # Call GUI progress callback
            self.gui_progress_callback(title, steps, current_step_index, progress, done)
        else:
            # CLI mode - original behavior
            self.head(title)
            print("")
            if done:
                for step in steps:
                    print("  [\033[92m✓\033[0m] {}".format(step))
            else:
                for i, step in enumerate(steps):
                    if i < current_step_index:
                        print("  [\033[92m✓\033[0m] {}".format(step))
                    elif i == current_step_index:
                        print("  [\033[1;93m>\033[0m] {}...".format(step))
                    else:
                        print("  [ ] {}".format(step))
            print("")

    def head(self, text = None, width = 68, resize=True):
        if resize:
            self.adjust_window_size()
        # Skip clear screen in GUI mode or if TERM is not set to prevent issues
        if self.gui_callback is None and os.environ.get('TERM'):
            try:
                os.system('cls' if os.name=='nt' else 'clear')
            except Exception:
                pass  # Silently ignore clear screen errors
        if text == None:
            text = self.script_name
        separator = "═" * (width - 2)
        title = " {} ".format(text)
        if len(title) > width - 2:
            title = title[:width-4] + "..."
        title = title.center(width - 2)
        
        print("╔{}╗\n║{}║\n╚{}╝".format(separator, title, separator))
    
    def adjust_window_size(self, content=""):
        # Skip terminal resizing in GUI mode or if TERM is not set
        if self.gui_callback is not None or not os.environ.get('TERM'):
            return
        lines = content.splitlines()
        rows = len(lines)
        cols = max(len(line) for line in lines) if lines else 0
        try:
            print('\033[8;{};{}t'.format(max(rows+6, 30), max(cols+2, 100)))
        except Exception:
            # Silently ignore any terminal resize errors
            pass

    def exit_program(self):
        self.head()
        width = 68
        print("")
        print("For more information, to report errors, or to contribute to the product:".center(width))
        print("")

        separator = "─" * (width - 4)
        print(f" ┌{separator}┐ ")
        
        contacts = {
            "Facebook": "https://www.facebook.com/macforce2601",
            "Telegram": "https://t.me/lzhoang2601",
            "GitHub": "https://github.com/lzhoang2801/OpCore-Simplify"
        }
        
        for platform, link in contacts.items():
            line = f" * {platform}: {link}"
            print(f" │{line.ljust(width - 4)}│ ")

        print(f" └{separator}┘ ")
        print("")
        print("Thank you for using our program!".center(width))
        print("")
        self.request_input("Press Enter to exit.".center(width))
        sys.exit(0)