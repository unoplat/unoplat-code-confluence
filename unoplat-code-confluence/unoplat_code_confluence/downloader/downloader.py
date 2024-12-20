# Standard Library
# Standard Library
import os
import re  # Import regex module

# Third Party
import re  # Import regex module

# Third Party
import requests
from github import Github
from loguru import logger
from tqdm import tqdm


class Downloader:
    @staticmethod
    def get_specific_release_info(repo_name, release_tag, github_token=None):
        logger.info(f"Fetching release info for repository: {repo_name} with tag: {release_tag}")
        g = Github(github_token) if github_token else Github()  # Optionally use a token for higher rate limits: Github("your_github_access_token")
        repo = g.get_repo(repo_name)
        specific_release = repo.get_release(release_tag)
        logger.info(f"Specific release tag: {specific_release.tag_name}")
        return specific_release.tag_name, specific_release.get_assets()

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
        #todo: make this dynamic but there are breaking upstream changes as of now so hardcoding for now.
        tag_name, assets = Downloader.get_specific_release_info(repo_name, 'v2.2.8',github_token)
        jar_pattern = re.compile(r"scanner_cli-(.*)-all\.jar")  # Regex to match the jar file
        jar_asset = next((asset for asset in assets if jar_pattern.match(asset.name)), None)
        if not jar_asset:
            logger.error("No matching .jar file found in the latest release assets.")
            raise FileNotFoundError("No matching .jar file found in the latest release assets.")
        
        highest_version_asset_name = jar_asset.name
        highest_version_asset_url = jar_asset.browser_download_url

        existing_jars = [f for f in os.listdir(download_dir) if jar_pattern.match(f)]
        if existing_jars:
            matching_jar = next((jar for jar in existing_jars if tag_name[1:] in jar), None)
            if matching_jar:
                logger.info(f"Using existing JAR for version {tag_name}: {matching_jar}")
                return os.path.join(download_dir, matching_jar)
        
        # If no local JAR is higher version, download the latest
        logger.info(f"JAR found: {highest_version_asset_name}, starting download...")
        return Downloader.download_file(highest_version_asset_url, download_dir, highest_version_asset_name)