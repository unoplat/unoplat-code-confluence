import os
import requests
from tqdm import tqdm
from github import Github
import re  # Import regex module
from loguru import logger
from packaging import version

class Downloader:
    @staticmethod
    def get_latest_release_info(repo_name, github_token=None):
        logger.info(f"Fetching latest release info for repository: {repo_name}")
        g = Github(github_token) if github_token else Github()  # Optionally use a token for higher rate limits: Github("your_github_access_token")
        repo = g.get_repo(repo_name)
        latest_release = repo.get_latest_release()
        logger.info(f"Latest release tag: {latest_release.tag_name}")
        return latest_release.tag_name, latest_release.get_assets()

    @staticmethod
    def download_file(url, download_dir, filename):
        logger.info(f"Downloading file from URL: {url} to directory: {download_dir}")
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
            logger.error("ERROR, something went wrong during file download")
        logger.info(f"File downloaded successfully: {local_filename}")
        return local_filename

    @staticmethod
    def download_latest_jar(repo_name, download_dir, github_token=None):
        logger.info(f"Downloading latest JAR for repository: {repo_name}")
        tag_name, assets = Downloader.get_latest_release_info(repo_name, github_token)
        jar_pattern = re.compile(r"scanner_cli-(.*)-all\.jar")  # Regex to match the jar file
        jar_asset = next((asset for asset in assets if jar_pattern.match(asset.name)), None)
        if not jar_asset:
            logger.error("No matching .jar file found in the latest release assets.")
            raise FileNotFoundError("No matching .jar file found in the latest release assets.")
        
        highest_version_asset_name = jar_asset.name
        highest_version_asset_url = jar_asset.browser_download_url

        existing_jars = [f for f in os.listdir(download_dir) if jar_pattern.match(f)]
        if existing_jars:
            highest_version_local = max(existing_jars, key=lambda x: version.parse(jar_pattern.match(x).group(1)))
            if version.parse(jar_pattern.match(highest_version_local).group(1)) >= version.parse(jar_pattern.match(highest_version_asset_name).group(1)):
                logger.info(f"Using existing JAR: {highest_version_local}")
                return os.path.join(download_dir, highest_version_local)
        
        # If no local JAR is higher version, download the latest
        logger.info(f"JAR found: {highest_version_asset_name}, starting download...")
        return Downloader.download_file(highest_version_asset_url, download_dir, highest_version_asset_name)

        
        

        
        
        
        
        
        highest_version_asset = max(jar_asset, key=lambda asset: version.parse(jar_pattern.match(asset.name).group(1)))
        logger.info(f"JAR found: {jar_asset.name}, starting download...")
        return Downloader.download_file(jar_asset.browser_download_url, download_dir, highest_version_asset.name)
