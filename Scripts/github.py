from Scripts import resource_fetcher
from Scripts import utils
import random
import json

class Github:
    def __init__(self, utils_instance=None):
        self.utils = utils_instance if utils_instance is not None else utils.Utils()
        self.fetcher = resource_fetcher.ResourceFetcher(utils_instance=self.utils)

    def extract_payload(self, response):
        for line in response.splitlines():
            if "type=\"application/json\"" in line:
                payload = line.split(">", 1)[1].split("<", 1)[0]

                try:
                    payload = json.loads(payload)
                    payload = payload["payload"]
                except:
                    continue

                return payload
        return None
        
    def get_commits(self, owner, repo, branch="main", start_commit=None, after=-1):
        if after > -1 and not start_commit:
            start_commit = self.get_commits(owner, repo, branch)["currentCommit"]["oid"]

        if after < 0:
            url = "https://github.com/{}/{}/commits/{}".format(owner, repo, branch)
        else:
            url = "https://github.com/{}/{}/commits/{}?after={}+{}".format(owner, repo, branch, start_commit, after)

        response = self.fetcher.fetch_and_parse_content(url)

        if not response:
            raise ValueError("Failed to fetch commit information from GitHub.")

        payload = self.extract_payload(response)

        if not "commitGroups" in payload:
            raise ValueError("Cannot find commit information for repository {} on branch {}.".format(repo, branch))
        
        return payload

    def get_latest_release(self, owner, repo):
        url = "https://github.com/{}/{}/releases".format(owner, repo)
        response = self.fetcher.fetch_and_parse_content(url)

        if not response:
            raise ValueError("Failed to fetch release information from GitHub.")

        tag_name = self._extract_tag_name(response)
        body = self._extract_body_content(response)

        release_tag_url = "https://github.com/{}/{}/releases/expanded_assets/{}".format(owner, repo, tag_name)
        response = self.fetcher.fetch_and_parse_content(release_tag_url)

        if not response:
            raise ValueError("Failed to fetch expanded assets information from GitHub.")

        assets = self._extract_assets(response)

        return {
            "body": body,
            "assets": assets
        }

    def _extract_tag_name(self, response):
        for line in response.splitlines():
            if "<a" in line and "href=\"" in line and "/releases/tag/" in line:
                return line.split("/releases/tag/")[1].split("\"")[0]
        return None

    def _extract_body_content(self, response):
        for line in response.splitlines():
            if "<div" in line and "body-content" in line:
                return response.split(line.split(">", 1)[0], 1)[1].split("</div>", 1)[0][1:]
        return ""

    def _extract_assets(self, response):
        assets = []

        in_li_block = False

        for line in response.splitlines():

            if "<li" in line:
                in_li_block = True
                download_link = None
                sha256 = None
                asset_id = None
            elif in_li_block and "</li" in line:
                if download_link and asset_id:
                    assets.append({
                        "product_name": self.extract_asset_name(download_link.split("/")[-1]), 
                        "id": int(asset_id), 
                        "url": "https://github.com" + download_link,
                        "sha256": sha256
                    })
                in_li_block = False

            if in_li_block:  
                if download_link is None and "<a" in line and "href=\"" in line and "/releases/download" in line:
                    download_link = line.split("href=\"", 1)[1].split("\"", 1)[0]

                    if not ("tlwm" in download_link or ("tlwm" not in download_link and "DEBUG" not in download_link.upper())):
                        in_li_block = False
                        continue

                if sha256 is None and "sha256:" in line:
                    sha256 = line.split("sha256:", 1)[1].split("<", 1)[0]

                if asset_id is None and "<relative-time" in line:
                    asset_id = self._generate_asset_id(line)

        return assets

    def _generate_asset_id(self, line):
        try:
            return "".join(char for char in line.split("datetime=\"")[-1].split("\"")[0][::-1] if char.isdigit())[:9]
        except:
            return "".join(random.choices('0123456789', k=9))

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
        if "unsupported" in file_name:
            asset_name += "-unsupported"
        elif "rtsx" in file_name:
            asset_name += "-rtsx"
        elif "itlwm" in file_name.lower():
            if "Sonoma14.4" in file_name:
                asset_name += "23.4"
            elif "Sonoma14.0" in file_name:
                asset_name += "23.0"
            elif "Ventura" in file_name:
                asset_name += "22"
            elif "Monterey" in file_name:
                asset_name += "21"
            elif "BigSur" in file_name:
                asset_name += "20"
            elif "Catalina" in file_name:
                asset_name += "19"
            elif "Mojave" in file_name:
                asset_name += "18"
            elif "HighSierra" in file_name:
                asset_name += "17"

        return asset_name