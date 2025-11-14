import os
import hashlib
import json
from Scripts import utils

class IntegrityChecker:
    def __init__(self):
        self.utils = utils.Utils()

    def get_sha256(self, file_path, block_size=65536):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return None

        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()

    def generate_folder_manifest(self, folder_path, manifest_path=None):
        if not os.path.isdir(folder_path):
            return None

        if manifest_path is None:
            manifest_path = os.path.join(folder_path, "manifest.json")

        manifest_data = {}
        for root, _, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)
                relative_path = os.path.relpath(file_path, folder_path).replace('\\', '/')
                
                if relative_path == os.path.basename(manifest_path):
                    continue

                manifest_data[relative_path] = self.get_sha256(file_path)
        
        self.utils.write_file(manifest_path, manifest_data)
        return manifest_data

    def verify_folder_integrity(self, folder_path, manifest_path=None):
        if not os.path.isdir(folder_path):
            return None, "Folder not found."

        if manifest_path is None:
            manifest_path = os.path.join(folder_path, "manifest.json")

        if not os.path.exists(manifest_path):
            return None, "Manifest file not found."

        manifest_data = self.utils.read_file(manifest_path)
        if not isinstance(manifest_data, dict):
            return None, "Invalid manifest file."
            
        issues = {
            "modified": [],
            "missing": [],
            "untracked": []
        }

        manifest_files = set(manifest_data.keys())
        actual_files = set()

        for root, _, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)
                relative_path = os.path.relpath(file_path, folder_path).replace('\\', '/')

                if relative_path == os.path.basename(manifest_path):
                    continue
                
                actual_files.add(relative_path)

                if relative_path not in manifest_data:
                    issues["untracked"].append(relative_path)
                else:
                    current_hash = self.get_sha256(file_path)
                    if current_hash != manifest_data.get(relative_path):
                        issues["modified"].append(relative_path)

        missing_files = manifest_files - actual_files
        issues["missing"] = list(missing_files)

        is_valid = not any(issues.values())
        
        return is_valid, issues
