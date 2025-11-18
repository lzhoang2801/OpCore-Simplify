import os
import json
import hmac
from Scripts import utils

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SECRET_KEY = b'super_secret_key_here'  # Replace with securely stored key

class IntegrityChecker:
    def __init__(self):
        self.utils = utils.Utils()

    def generate_folder_manifest(self, folder_path, manifest_path=None):
        if not os.path.isdir(folder_path):
            return None

        if manifest_path is None:
            manifest_path = os.path.join(folder_path, "manifest.json")

        manifest_files = []
        for root, _, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)

                # Enforce file size limit
                try:
                    if os.path.getsize(file_path) > MAX_FILE_SIZE:
                        print(f"Skipping {file_path}: exceeds 100MB")
                        continue
                except Exception as e:
                    print(f"Error checking size of {file_path}: {e}")
                    continue

                relative_path = os.path.relpath(file_path, folder_path).replace('\\', '/')

                if relative_path == os.path.basename(manifest_path):
                    continue

                manifest_files.append(relative_path)

        # Sign manifest with HMAC
        manifest_bytes = json.dumps(manifest_files, sort_keys=True).encode('utf-8')
        signature = hmac.new(SECRET_KEY, manifest_bytes, digestmod="sha256").hexdigest()

        signed_manifest = {
            "files": manifest_files,
            "signature": signature
        }

        self.utils.write_file(manifest_path, signed_manifest)
        return signed_manifest

    def verify_folder_integrity(self, folder_path, manifest_path=None):
        if not os.path.isdir(folder_path):
            return None, "Folder not found."

        if manifest_path is None:
            manifest_path = os.path.join(folder_path, "manifest.json")

        if not os.path.exists(manifest_path):
            return None, "Manifest file not found."

        manifest_data = self.utils.read_file(manifest_path)
        if not isinstance(manifest_data, dict) or "files" not in manifest_data or "signature" not in manifest_data:
            return None, "Invalid manifest file."

        # Verify HMAC signature
        manifest_bytes = json.dumps(manifest_data["files"], sort_keys=True).encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY, manifest_bytes, digestmod="sha256").hexdigest()
        if not hmac.compare_digest(expected_sig, manifest_data["signature"]):
            return None, "Manifest signature invalid."

        issues = {"missing": [], "untracked": []}
        manifest_files = set(manifest_data["files"])
        actual_files = set()

        for root, _, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)
                relative_path = os.path.relpath(file_path, folder_path).replace('\\', '/')

                if relative_path == os.path.basename(manifest_path):
                    continue

                actual_files.add(relative_path)

                if relative_path not in manifest_files:
                    issues["untracked"].append(relative_path)

        missing_files = manifest_files - actual_files
        issues["missing"] = list(missing_files)

        is_valid = not any(issues.values())
        return is_valid, issues
