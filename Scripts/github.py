from Scripts import resource_fetcher
from Scripts import utils
import re
from urllib.parse import quote


class Github:
    def __init__(self):
        self.utils = utils.Utils()
        self.fetcher = resource_fetcher.ResourceFetcher()

    def get_commits(self, owner, repo, branch="main"):
        """Read branch-head metadata from the GitHub API."""
        url = "https://api.github.com/repos/{}/{}/commits/{}".format(
            quote(owner, safe=""), quote(repo, safe=""), quote(branch, safe="")
        )
        response = self.fetcher.fetch_and_parse_content(url, "json")
        if not isinstance(response, dict):
            raise ValueError(
                "Failed to fetch commit information from GitHub API. "
                "Check the connection errors reported above.")
        if "message" in response and "sha" not in response:
            raise ValueError(
                "GitHub API error for {}/{}: {}".format(owner, repo, response["message"]))

        sha = response.get("sha")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            raise ValueError(
                "Cannot find commit information for repository {} on branch {}.".format(repo, branch))
        return {"sha": sha.lower(), "url": url}

    def get_latest_release(self, owner, repo):
        url = "https://api.github.com/repos/{}/{}/releases/latest".format(
            quote(owner, safe=""), quote(repo, safe="")
        )
        response = self.fetcher.fetch_and_parse_content(url, "json")

        if response is None or (
            isinstance(response, dict) and response.get("message") == "Not Found"
        ):
            releases_url = "https://api.github.com/repos/{}/{}/releases?per_page=1".format(
                quote(owner, safe=""), quote(repo, safe="")
            )
            response = self.fetcher.fetch_and_parse_content(releases_url, "json")

        if isinstance(response, dict):
            if "message" in response and "assets" not in response:
                raise ValueError(
                    "GitHub API error for {}/{}: {}".format(owner, repo, response["message"]))
            release = response
        elif isinstance(response, list) and response and isinstance(response[0], dict):
            release = response[0]
        else:
            raise ValueError(
                "Failed to fetch release information for {}/{} from GitHub API. "
                "Check the connection errors reported above.".format(owner, repo))

        assets = []
        for asset in release.get("assets", []):
            if not isinstance(asset, dict):
                continue

            name = asset.get("name")
            download_url = asset.get("url")
            asset_id = asset.get("id")
            if not isinstance(name, str) or not isinstance(download_url, str) or not asset_id:
                continue
            if name.lower().endswith(".sha256") or "RESEARCH" in name.upper() or "DEBUG" in name.upper():
                continue

            digest = asset.get("digest")
            sha256 = None
            if isinstance(digest, str):
                match = re.fullmatch(r"sha256:([0-9a-fA-F]{64})", digest)
                if match:
                    sha256 = match.group(1).lower()

            assets.append({
                "product_name": self.extract_asset_name(name),
                "id": int(asset_id),
                "url": download_url,
                "sha256": sha256
            })

        return {
            "body": release.get("body") or "",
            "assets": assets
        }

    def extract_asset_name(self, file_name):
        end_idx = len(file_name)
        if "-" in file_name:
            end_idx = min(file_name.index("-"), end_idx)
        if "_" in file_name:
            end_idx = min(file_name.index("_"), end_idx)
        if "." in file_name:
            end_idx = min(file_name.index("."), end_idx)
            if file_name[end_idx] == "." and file_name[end_idx - 1].isdigit():
                end_idx = end_idx - 1
        asset_name = file_name[:end_idx]

        if "Sniffer" in file_name:
            asset_name = file_name.split(".")[0]
        if asset_name == "IntelBluetooth":
            asset_name = "IntelBluetoothFirmware"
        if "unsupported" in file_name:
            asset_name += "-unsupported"
        elif "rtsx" in file_name:
            asset_name += "-rtsx"
        elif "itlwm" in file_name.lower():
            if "Sequoia" in file_name:
                asset_name += "24"
            elif "Tahoe" in file_name:
                asset_name += "25"
            elif "Sonoma14.4" in file_name:
                asset_name += "23.4"
            elif "Sonoma14.0" in file_name:
                asset_name += "23.0"
            elif "Ventura" in file_name:
                asset_name += "22"
            elif "Monterey" in file_name:
                asset_name += "21"
            elif "Big_Sur" in file_name:
                asset_name += "20"
            elif "Catalina" in file_name:
                asset_name += "19"
            elif "Mojave" in file_name:
                asset_name += "18"
            elif "High_Sierra" in file_name:
                asset_name += "17"

        return asset_name
