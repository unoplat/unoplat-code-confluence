
from src.code_confluence_flow_bridge.parser.linters.linter_strategy import LinterStrategy

import subprocess

from loguru import logger


class RuffStrategy(LinterStrategy):
    def lint_codebase(self, local_workspace_path: str) -> bool:
        """Run Ruff linter on Python codebase.

        Args:
            local_workspace_path (str): Path to Python codebase

        Returns:
            bool: True if linting violations were found, False otherwise
        """
        import json
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                ["ruff", "check", local_workspace_path, "--format=json"],
                capture_output=True,
                text=True,
                check=False,  # Don't raise CalledProcessError on lint violations
            )

            if result.returncode != 0 and result.stdout:
                # Parse JSON output into lint results
                

                json.loads(result.stdout)  # Validate JSON but we don't use it currently
                return True

            return False

        except Exception as e:
            logger.error(f"Error running Ruff linter: {e}")  # str() is unnecessary
            return False
