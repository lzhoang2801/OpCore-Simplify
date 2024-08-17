from Scripts import resource_fetcher
from Scripts import utils
import os

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
        if response.get("rate").get("remaining") == 0:
            raise Exception("Please try again later, you have exhausted your GitHub REST API request quota")
        
    def get_latest_artifact(self, owner, repo):
        results = []

        self.check_ratelimit()

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
        result = []

        self.check_ratelimit()

        url = "https://api.github.com/repos/{}/{}/releases?per_page=1".format(owner, repo)

        response = self.fetcher.fetch_and_parse_content(url, "json")

        # Iterate over the assets in the release
        for asset in response[0].get("assets"):
            asset_id = asset.get("id")
            download_url = asset.get("browser_download_url")
            asset_name = self.extract_asset_name(asset.get("name"))

            if "tlwm" in download_url or ("tlwm" not in download_url and "DEBUG" not in download_url.upper()):
                result.append({
                    "product_name": asset_name, 
                    "id": asset_id, 
                    "url": download_url
                })

        return result
    
    def extract_asset_name(self, name):
        # Extract the base name from the asset name
        name_parts = name.split("-") if "-" in name else name.split("_")

        asset_name = name_parts[0].split(".")[0]
        if asset_name[-1].isdigit():
            asset_name = asset_name[:-1]
            
        if (len(name_parts) > 1):
            if "uns" in name_parts[1]:
                asset_name += "-" + name_parts[1]
            elif "Sonoma14.4" in name:
                asset_name += "23.4"
            elif "Sonoma" in name:
                asset_name += "23"
            elif "Ventura" in name:
                asset_name += "22"
            elif "Monterey" in name:
                asset_name += "21"
            elif "Catalina" in name:
                asset_name += "19"
            elif "Mojave" in name:
                asset_name += "18"
            elif "HighSierra" in name:
                asset_name += "17"
            elif "BigSur" in name:
                asset_name += "20"

        return asset_name