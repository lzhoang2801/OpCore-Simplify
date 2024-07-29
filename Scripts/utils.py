import os
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

    def search_dict_iter(self, dictionary, search_term, equal=True, reverse=False):
        dictionary_copy = dictionary.copy()

        if reverse:
            dictionary_copy = dict(list(dictionary_copy.items())[::-1])

        stack = [(dictionary_copy, None)]

        while stack:
            current_dict, parent_dict = stack.pop()
            for key, value in current_dict.items():
                if equal and value == search_term or not equal and search_term in value:
                    return current_dict
                if isinstance(value, dict):
                    stack.append((value, current_dict))
                if equal and key == search_term or not equal and search_term in key:
                    return value

        return {}

    def find_matching_paths(self, directory, target_file_extension=None, target_name_pattern=None):
        found_paths = []

        if not os.path.exists(directory):
            print("Error: The directory {} does not exist.".format(directory))
            return found_paths
        
        for root, dirs, files in os.walk(directory):
            if "MACOSX" in root:
                continue

            if target_file_extension and root.endswith(target_file_extension) or target_name_pattern and target_name_pattern in root:
                if not os.path.exists(os.path.join(root, os.path.basename(root))):
                    found_paths.append(root.replace(directory, "")[1:])

            for file in files:
                file_name, file_extension = os.path.splitext(file)

                if target_file_extension and file_extension.endswith(target_file_extension) or target_name_pattern and target_name_pattern in file_name:
                    found_paths.append(os.path.join(root, file).replace(directory, "")[1:])

        return found_paths

    def sort_dict_by_key(self, input_dict, sort_key):
        return dict(sorted(input_dict.items(), key=lambda item: item[1].get(sort_key, "")))

    def mkdirs(self, *directories):
        for directory in directories:
            if not os.path.exists(os.path.dirname(directory)):
                os.makedirs(os.path.dirname(directory))
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
    
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
        try:
            return format(number, '02X')
        except:
            return number

    def hex_to_int(self, hex_string):
        return int(hex_string, 16)
    
    def to_little_endian_hex(self, hex_str):
        hex_str = hex_str.lower().lstrip("0x")
                
        hex_str = hex_str.zfill(8)

        little_endian_hex = ''.join(reversed([hex_str[i:i+2] for i in range(0, len(hex_str), 2)]))
        
        return little_endian_hex.upper()

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

    @staticmethod
    def message(text, msg_type="attention"):
        # ANSI escape codes for different colors and bold font
        RED_BOLD = "\033[1;31m"
        YELLOW_BOLD = "\033[1;33m"
        CYAN_BOLD = "\033[1;36m"
        RESET = "\033[0m"
        
        if msg_type == "attention":
            color_code = RED_BOLD
        elif msg_type == "warning":
            color_code = YELLOW_BOLD
        elif msg_type == "reminder":
            color_code = CYAN_BOLD
        else:
            color_code = RESET

        return "{}{}{}".format(color_code, text, RESET)

    def exit_program(self, custom_content=""):
        self.head()
        print(custom_content)
        print("For more information, to report errors, or to contribute to the product:")
        print("* Facebook: https://www.facebook.com/macforce2601")
        print("* Telegram: https://t.me/lzhoang2601")
        print("* GitHub: https://github.com/lzhoang2801/OpCore-Simplify")
        print("")

        print("Thank you for using our program!\n")
        exit(0)