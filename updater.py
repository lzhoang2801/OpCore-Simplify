from Scripts import resource_fetcher
from Scripts import github
from Scripts import run
from Scripts import utils
import os
import tempfile
import shutil

class Updater:
    def __init__(self):
        self.github = github.Github()
        self.fetcher = resource_fetcher.ResourceFetcher({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        self.run = run.Run().run
        self.utils = utils.Utils()
        self.sha_version = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sha_version.txt")
        self.download_repo_url = "https://github.com/lzhoang2801/OpCore-Simplify/archive/refs/heads/main.zip"
        self.temporary_dir = tempfile.mkdtemp()

    def get_current_sha_version(self):
        current_sha_version = self.utils.read_file(self.sha_version)

        if not current_sha_version:
            print("SHA version information is missing in the sha_version.txt file.\n")
            return "0506fb67111d5c5230bf59b826c318ea4251dfc4"

        return current_sha_version.decode()

    def get_latest_sha_version(self):
        latest_commit = self.github.get_latest_commit("lzhoang2801", "OpCore-Simplify")

        return latest_commit.get("sha") or "0506fb67111d5c5230bf59b826c318ea4251dfc4"

    def download_update(self):
        self.utils.create_folder(self.temporary_dir)
        file_path = os.path.join(self.temporary_dir, os.path.basename(self.download_repo_url))
        self.fetcher.download_and_save_file(self.download_repo_url, file_path)
        self.utils.extract_zip_file(file_path)

    def update_files(self):
        target_dir = os.path.join(self.temporary_dir, "main", "OpCore-Simplify-main")
        file_paths = self.utils.find_matching_paths(target_dir, type_filter="file")

        for path, type in file_paths:
            source = os.path.join(target_dir, path)
            destination = source.replace(target_dir, os.path.dirname(os.path.realpath(__file__)))
            self.utils.create_folder(os.path.dirname(destination))
            shutil.move(source, destination)
            if ".command" in os.path.splitext(path)[-1] and os.name != "nt":
                self.run({
                    "args":["chmod", "+x", destination]
                })
        shutil.rmtree(self.temporary_dir)

    def save_latest_sha_version(self, latest_sha):
        self.utils.write_file(self.sha_version, latest_sha.encode())

    def run_update(self):
        self.utils.head("Check for Updates")
        print("")
        current_sha_version = self.get_current_sha_version()

        if not self.github.check_ratelimit():
            print("GitHub REST API request quota has been exhausted. Automatic update check is unavailable now.")
            print("Please check for updates manually if needed.")
            print("")
            self.utils.request_input()
            return False

        latest_sha_version = self.get_latest_sha_version()
        print("Current script SHA version: {}".format(current_sha_version))
        print("Latest script SHA version: {}".format(latest_sha_version))
        print("")
        if latest_sha_version != current_sha_version:
            print("Updating from version {} to {}".format(current_sha_version, latest_sha_version))
            print("")
            self.download_update()
            self.update_files()
            self.save_latest_sha_version(latest_sha_version)
            print("\n")
            print("The program needs to restart to complete the update process.")
            print("\n")
            self.utils.request_input()
        else:
            print("You are already using the latest version")
        
        return latest_sha_version != current_sha_version