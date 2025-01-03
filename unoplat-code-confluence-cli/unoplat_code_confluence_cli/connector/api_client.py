from typing import Optional, List, Dict
import asyncio
import httpx
from loguru import logger
from unoplat_code_confluence_cli.config.settings import AppConfig, RepositorySettings

class CodeConfluenceConnector:
    def __init__(self, base_url: str, github_token: str):
        self.base_url = base_url.rstrip('/')
        self.github_token = github_token.strip()
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.github_token}'
        }

    async def _ingest_single_repository(self, repository: RepositorySettings) -> Dict:
        """
        Send POST request to start ingestion for a single repository
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/start-ingestion",
                    json=repository.model_dump(),
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Started ingestion for repository: {repository.git_url}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error for repository {repository.git_url}:\n"
                f"Status code: {e.response.status_code}\n"
                f"Error message: {e.response.text}\n"
                f"Request URL: {e.request.url}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(
                f"Request failed for repository {repository.git_url}:\n"
                f"Error: {str(e)}\n"
                f"Request URL: {e.request.url}"
            )
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred for repository {repository.git_url}: {str(e)}")
            raise

    async def start_ingestion(self, config: AppConfig) -> List[Dict]:
        """
        Send parallel POST requests to start ingestion for each repository
        """
        tasks = []
        for repository in config.repositories:
            task = asyncio.create_task(self._ingest_single_repository(repository))
            tasks.append(task)
        
        logger.info(f"Starting ingestion for {len(tasks)} repositories")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and log any errors
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process repository {config.repositories[i].git_url}: {result}")
            else:
                processed_results.append(result)
        
        return processed_results #type: ignore