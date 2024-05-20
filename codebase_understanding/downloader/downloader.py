import os
import requests
from tqdm import tqdm
from github import Github
import re  # Import regex module

class Downloader:
    @staticmethod
    def get_latest_release_info(repo_name,github_token=None):
        g = Github(github_token) if github_token else Github()  # Optionally use a token for higher rate limits: Github("your_github_access_token")
        repo = g.get_repo(repo_name)
        latest_release = repo.get_latest_release()
        return latest_release.tag_name, latest_release.get_assets()

    @staticmethod
    def download_file(url, download_dir, filename):
        os.makedirs(download_dir, exist_ok=True)  # Ensure the directory exists
        local_filename = os.path.join(download_dir, filename)

        response = requests.get(url, stream=True)
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(local_filename, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")
        return local_filename

    @staticmethod
    def download_latest_jar(repo_name, download_dir,github_token=None):
        tag_name, assets = Downloader.get_latest_release_info(repo_name,github_token)
        jar_pattern = re.compile(r"scanner_cli-.*-all\.jar")  # Regex to match the jar file
        jar_asset = next((asset for asset in assets if jar_pattern.match(asset.name)), None)
        if jar_asset is None:
            raise FileNotFoundError("No matching .jar file found in the latest release assets.")
        return Downloader.download_file(jar_asset.browser_download_url, download_dir, jar_asset.name)
        