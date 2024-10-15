from Scripts import resource_fetcher
from Scripts import utils

class Github:
    def __init__(self):
        self.utils = utils.Utils()
        # Set the headers for GitHub API requests
        self.headers = {
            "Accept": "application/vnd.github+json",
            "#Authorization": "token GITHUB_TOKEN",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.fetcher = resource_fetcher.ResourceFetcher(self.headers)

    def check_ratelimit(self):
        url = "https://api.github.com/rate_limit"

        response = self.fetcher.fetch_and_parse_content(url, "json")

        return response.get("rate").get("remaining") != 0
        
    def get_latest_commit(self, owner, repo):
        url = "https://api.github.com/repos/{}/{}/commits".format(owner, repo)

        response = self.fetcher.fetch_and_parse_content(url, "json")

        return response[0]
        
    def get_latest_artifact(self, owner, repo):
        results = []

        url = "https://api.github.com/repos/{}/{}/actions/artifacts?per_page=1".format(owner, repo)

        response = self.fetcher.fetch_and_parse_content(url, "json")

        latest_artifact_id = response.get("artifacts")[0].get("id")
        
        results.append({
            "product_name": repo,
            "id": latest_artifact_id,
            "url": "https://api.github.com/repos/{}/{}/actions/artifacts/{}/{}".format(owner, repo, latest_artifact_id, "zip")
        })

        return results

    def get_latest_release(self, owner, repo):
        results = []

        url = "https://api.github.com/repos/{}/{}/releases?per_page=1".format(owner, repo)

        response = self.fetcher.fetch_and_parse_content(url, "json")

        for asset in response[0].get("assets"):
            asset_id = asset.get("id")
            download_url = asset.get("browser_download_url")
            asset_name = self.extract_asset_name(asset.get("name"))

            if "tlwm" in download_url or ("tlwm" not in download_url and "DEBUG" not in download_url.upper()):
                results.append({
                    "product_name": asset_name, 
                    "id": asset_id, 
                    "url": download_url
                })

        return results
    
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