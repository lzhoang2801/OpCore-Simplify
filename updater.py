from Scripts import github
from Scripts import resource_fetcher
from Scripts import utils
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import ssl
import zipfile


class UpdateRecoveryError(RuntimeError):
    """The application must stop because restoration was incomplete."""


class Updater:
    update_steps = (
        "Download update package",
        "Validate and extract files",
        "Back up application files",
        "Install application files",
    )

    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.github = github.Github()
        self.fetcher = resource_fetcher.ResourceFetcher()
        self.utils = utils.Utils()

    def is_git_checkout(self):
        return any(os.path.lexists(parent / ".git") for parent in (self.root, *self.root.parents))

    def get_current_sha_version(self):
        path = self.root / "sha_version.txt"
        if not path.exists():
            return None
        sha = path.read_text(encoding="utf-8").strip()
        return sha.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", sha) else None

    @staticmethod
    def _application_path(name):
        parts = PurePosixPath(name).parts
        if (not parts or "/".join(parts) != name or re.search(r'[<>:"\\|?*\x00-\x1f]', name)
                or any(part in (".", "..")
                       or part.endswith((".", " "))
                       or re.match(r"(?i)^(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(\.|$)", part)
                       for part in parts)):
            raise ValueError("Unsafe update path: {}".format(name))
        return (len(parts) > 1 and parts[0] == "Scripts"
                and not any(part.startswith(".") or part in ("__pycache__", "OCK_Files", "Results") for part in parts)
                or name in ("OpCore-Simplify.py", "OpCore-Simplify.bat", "OpCore-Simplify.command",
                            "updater.py", "README.md", "LICENSE"))

    def _destination(self, name):
        path = self.root / name
        for part in (path, *path.parents):
            if part == self.root:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError("Linked update destination: {}".format(name))
        if self.root not in path.resolve().parents:
            raise ValueError("External update destination: {}".format(name))
        if path.exists() and not path.is_file():
            raise ValueError(
                "Update destination is not a file: {}".format(name))
        return path

    @staticmethod
    def _hash(path):
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(65536), b""):
                digest.update(block)
        return digest.hexdigest()

    def download_update(self, sha, workspace):
        archive_path = workspace / "update.zip"
        url = "https://github.com/lzhoang2801/OpCore-Simplify/archive/{}.zip".format(
            sha)
        self.utils.progress_bar("Update OpCore Simplify", self.update_steps, 0)
        if not self.fetcher.download_and_save_file(url, str(archive_path)):
            raise RuntimeError("Could not download the update package.")
        staged = workspace / "staged"
        files = {}
        seen = set()
        prefix = "OpCore-Simplify-{}/".format(sha)
        self.utils.progress_bar("Update OpCore Simplify", self.update_steps, 1)
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            if len(entries) > 10000 or sum(entry.file_size for entry in entries) > 512 * 1024 * 1024:
                raise ValueError("Update archive exceeds the supported size.")
            for entry in entries:
                if entry.orig_filename != entry.filename:
                    raise ValueError("Non-canonical update archive path.")
                if not entry.filename.startswith(prefix):
                    raise ValueError("Unexpected update archive root.")
                if entry.is_dir():
                    continue
                name = entry.filename[len(prefix):]
                if not self._application_path(name):
                    continue
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(
                        "Update archive contains a symbolic link.")
                if name.casefold() in seen:
                    raise ValueError("Duplicate update path: {}".format(name))
                seen.add(name.casefold())
                target = staged / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
                if name.endswith(".command"):
                    target.chmod(0o755)
                files[name] = self._hash(target)
        for required in ("OpCore-Simplify.py", "updater.py", "Scripts/github.py", "Scripts/utils.py"):
            if required not in files:
                raise ValueError(
                    "Incomplete update archive: missing {}".format(required))
        return files

    def update_files(self, workspace, sha, files):
        if self.is_git_checkout():
            raise RuntimeError(
                "Git checkout detected. Use Git to update this installation.")
        manifest_name = "update_manifest.json"
        manifest_path = self._destination(manifest_name)
        previous = json.loads(manifest_path.read_text(
            encoding="utf-8")) if manifest_path.exists() else {}
        if not isinstance(previous, dict):
            raise ValueError("Invalid installed-file manifest.")
        for name, digest in previous.items():
            if not self._application_path(name) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("Invalid installed-file manifest entry.")
            path = self._destination(name)
            if not path.exists() or self._hash(path) != digest:
                raise ValueError(
                    "Locally changed application file: {}. Update manually.".format(name))

        staged = workspace / "staged"
        (staged / manifest_name).write_text(json.dumps(files, indent=2), encoding="utf-8")
        (staged / "sha_version.txt").write_text(sha + "\n", encoding="utf-8")
        names = sorted(set(previous) | set(files)) + \
            [manifest_name, "sha_version.txt"]
        backup = workspace / "backup"
        existed = {}
        self.utils.progress_bar("Update OpCore Simplify", self.update_steps, 2)
        for name in names:
            path = self._destination(name)
            if manifest_path.exists() and name in files and name not in previous and path.exists():
                raise ValueError(
                    "Unmanaged file would be overwritten: {}. Update manually.".format(name))
            existed[name] = path.exists()
            if path.exists():
                saved = backup / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, saved)
        (workspace / "original_files.json").write_text(json.dumps(existed,
                                                                  indent=2), encoding="utf-8")
        changed = []
        try:
            self.utils.progress_bar(
                "Update OpCore Simplify", self.update_steps, 3)
            for name in names:
                destination = self._destination(name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = staged / name
                changed.append(name)
                if source.exists():
                    os.replace(source, destination)
                else:
                    destination.unlink()
        except (Exception, KeyboardInterrupt) as error:
            failures = []
            for name in reversed(changed):
                try:
                    destination = self._destination(name)
                    if existed[name]:
                        if not destination.exists() or self._hash(destination) != self._hash(backup / name):
                            shutil.copy2(backup / name, destination)
                    else:
                        destination.unlink(missing_ok=True)
                except (Exception, KeyboardInterrupt) as restore_error:
                    failures.append("{}: {}".format(name, restore_error))
            if failures:
                raise UpdateRecoveryError("Rollback incomplete. Backups and original-file list kept at {}. {}".format(
                    workspace, "; ".join(failures))) from error
            raise RuntimeError(
                "Update failed; original files restored: {}".format(error)) from error

    def run_update(self):
        if self.is_git_checkout():
            return "skipped"
        self.utils.head("Check for Updates")
        print("")
        workspace = self.root / ".opcore-update"
        if os.path.lexists(workspace):
            print(
                "\033[91mAn unfinished update needs recovery before the program can continue.\033[0m")
            print("  Recovery files: {}".format(workspace))
            print("")
            self.utils.request_input("Press Enter to exit...")
            return "recovery_required"
        try:
            context = ssl.create_default_context()
            self.github.fetcher.ssl_context = context
            self.fetcher.ssl_context = context
            current = self.get_current_sha_version()
            print("Checking for updates...")
            latest = self.github.get_commits("lzhoang2801", "OpCore-Simplify")
        except Exception as error:
            print(
                "\033[1;93mCould not check for updates. You can continue using the installed version.\033[0m")
            print("  {}".format(error))
            print("")
            self.utils.request_input()
            return "failed"
        sha = latest["sha"]
        print("")
        print("  Current Version: {}".format(
            current[:7] if current else "Unknown"))
        print("  Latest Version:  {}".format(sha[:7]))
        print("")
        if current == sha:
            print("You are already using the latest version.")
            return "unchanged"
        print("\033[1;96mAn update is available.\033[0m" if current else
              "\033[1;93mThe installed version could not be identified.\033[0m")
        if not (self.root / "update_manifest.json").exists():
            print("Updating will replace application files, including any local edits.")
        print("")
        created = False
        keep_backup = False
        try:
            workspace.mkdir()
            created = True
            files = self.download_update(sha, workspace)
            self.update_files(workspace, sha, files)
        except UpdateRecoveryError as error:
            keep_backup = True
            self.utils.head("Update Failed")
            print("")
            print("\033[91m{}\033[0m".format(error))
            print("")
            self.utils.request_input("Press Enter to exit...")
            return "recovery_required"
        except (Exception, KeyboardInterrupt) as error:
            self.utils.head("Update Failed")
            print("")
            print("\033[91mUpdate not installed: {}\033[0m".format(error))
            print("")
            if not created and os.path.lexists(workspace):
                self.utils.request_input("Press Enter to exit...")
                return "recovery_required"
            print("You can continue using the installed version.")
            print("")
            self.utils.request_input()
            return "failed"
        finally:
            if created and not keep_backup:
                try:
                    shutil.rmtree(workspace)
                except OSError as error:
                    print("Could not remove update workspace {}: {}".format(
                        workspace, error))
        self.utils.progress_bar(
            "Update OpCore Simplify", self.update_steps, len(self.update_steps), done=True)
        print("\033[92mUpdate completed successfully!\033[0m")
        print("")
        print("  Previous Version: {}".format(
            current[:7] if current else "Unknown"))
        print("  Installed Version: {}".format(sha[:7]))
        if workspace.exists():
            print("\033[1;93mTemporary update files could not be removed: {}\033[0m".format(
                workspace))
        print("")
        self.utils.request_input("Press Enter to restart...")
        return "updated"
