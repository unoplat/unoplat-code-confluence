from unoplat_code_confluence_cli.config.settings import AppSettings
from unoplat_code_confluence_cli.connector.api_client import CodeConfluenceConnector

import os
import asyncio

import click
from loguru import logger


async def start_ingestion_process(config_path: str, github_token: str) -> None:
    """
    Initialize the connector and start the ingestion process
    """
    try:
        # Load settings
        app_settings = AppSettings(config_path=config_path)

        # Get base URL from environment variable or use default
        base_url = os.getenv("CODE_CONFLUENCE_SERVER", "http://localhost:8000")

        # Initialize connector
        connector = CodeConfluenceConnector(base_url=base_url, github_token=github_token)

        logger.info(f"Connecting to Code Confluence server at: {base_url}")

        # Start ingestion
        result = await connector.start_ingestion(app_settings.config)
        logger.info(f"Ingestion started successfully: {result}")

    except Exception as e:
        logger.error(f"Failed to start ingestion: {e}")
        raise


@click.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Path to the code confluence query engine configuration file.")
@click.option(
    "--github-token", "github_token", prompt="Enter your GitHub token", envvar="UNOPLAT_GITHUB_TOKEN", help="GitHub token for authentication"
)
def main(config, github_token):
    """Code Confluence CLI tool."""
    if click.confirm("Do you want to proceed with ingestion?", default=True):
        click.echo(f"Config file: {config}")
        click.echo(f"GitHub token: {github_token[:4]}...")

        # Run the async function
        asyncio.run(start_ingestion_process(config, github_token))
    else:
        click.echo("Operation cancelled")


if __name__ == "__main__":
    main()
