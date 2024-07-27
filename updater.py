from Scripts import resource_fetcher
from Scripts import utils
import os
import tempfile
import shutil

class Updater:
    def __init__(self):
        self.fetcher = resource_fetcher.ResourceFetcher({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        self.utils = utils.Utils()
        self.verion_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "version.json")
        self.download_repo_url = "https://github.com/lzhoang2801/OpCore-Simplify/archive/refs/heads/main.zip"
        self.version_url = "https://raw.githubusercontent.com/lzhoang2801/OpCore-Simplify/main/version.json"
        self.temporary_dir = tempfile.mkdtemp()

    def get_current_version(self):
        version_data = self.utils.read_file(self.verion_file)

        if not version_data or not isinstance(version_data, dict):
            print("Version information is missing in the version.json file.\n")
            return "0.0.0"

        return version_data.get("version", "0.0.0")

    def get_latest_version(self):
        response = self.fetcher.fetch_and_parse_content(self.version_url, "json")

        latest_version = response.get('version')

        return latest_version or "0.0.0"

    def download_update(self):
        self.utils.mkdirs(self.temporary_dir)
        self.fetcher.download_and_save_file(self.download_repo_url, os.path.join(self.temporary_dir, os.path.basename(self.download_repo_url)))

    def update_files(self):
        target_dir = os.path.join(self.temporary_dir, "main", "OpCore-Simplify-main")
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                source = os.path.join(root, file)
                destination = source.replace(target_dir, os.path.dirname(os.path.realpath(__file__)))
                shutil.move(source, destination)
        shutil.rmtree(self.temporary_dir)

    def run_update(self):
        self.utils.head("Check for update")
        print("")
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()
        print(f"Current script version: {current_version}")
        print(f"Latest script version: {latest_version}")
        print("")
        if latest_version > current_version:
            print(f"Updating from version {current_version} to {latest_version}\n")
            self.download_update()
            self.update_files()
            print("\n\n{}\n".format(self.utils.message("The program needs to restart to complete the update process.", "reminder")))
            self.utils.request_input("Press Enter to restart...")
            return True
        else:
            print("You are already using the latest version")
            return False

