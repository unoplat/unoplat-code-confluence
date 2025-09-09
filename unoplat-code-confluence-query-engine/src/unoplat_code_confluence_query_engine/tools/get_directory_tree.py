import asyncio
from typing import Optional

from aiopath import AsyncPath
from pydantic import BaseModel, Field
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


# class DirectoryTree(BaseModel):
#     """Directory tree structure returned by the eza utility.
    
#     This model represents the formatted output from the eza command-line tool,
#     which provides a tree-like view of directory structure with files and folders.
#     """

#     tree: str = Field(..., description="Formatted directory tree produced by eza")


async def get_directory_tree(
    ctx: RunContext[AgentDependencies],
    depth: int,
    path: Optional[str] = None,
) -> str:
    """Get a text-based directory tree for a given directory.

    Args:
        depth: Maximum directory depth to traverse (must be >= 1).
        path: Absolute path to directory to traverse; defaults to codebase root if not provided.

    Returns:
        DirectoryTree: The formatted tree structure.
    """
    # Use the provided path or fall back to codebase root
    target_path = path if path is not None else ctx.deps.codebase_metadata.codebase_path
    # Validate file path security
    async_path = AsyncPath(target_path)

    # Check if path is absolute
    if not async_path.is_absolute():
        raise ModelRetry(
            f"Directory path must be absolute. Please provide an absolute path instead of: {target_path}"
        )

    # Check if path exists
    if not await async_path.exists():
        raise ModelRetry(
            f"Directory not found at path: {target_path}. Please check the directory path and try again."
        )

    # Check if path is a directory
    if not await async_path.is_dir():
        raise ModelRetry(
            f"Provided path is not a directory: {target_path}. Please provide a valid directory path."
        )

    # Build eza command arguments
    cmd_args = ["eza", "-T", "--group-directories-first"]

    # Validate and add depth limit
    if depth < 1:
        raise ModelRetry(
            f"Depth must be >= 1. Please provide a valid depth value instead of: {depth}"
        )
    cmd_args.extend(["--level", str(depth)])

    # Add the target path as the final argument
    cmd_args.append(target_path)

    try:
        # Execute eza command using subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Check if process succeeded
        if process.returncode != 0:
            error_msg = (
                stderr.decode("utf-8").strip()
                if stderr
                else f"eza exited with code {process.returncode}"
            )
            raise ModelRetry(
                f"eza failed: {error_msg}. Please check the directory path and permissions."
            )

        # Return the directory tree
        tree_output = stdout.decode("utf-8")
        #return DirectoryTree(tree=tree_output)
        return tree_output

    except FileNotFoundError:
        raise ModelRetry(
            "eza not installed. Install via: brew install eza (macOS) or "
            "apt install eza (Ubuntu) or visit https://github.com/eza-community/eza for other platforms."
        )
    except PermissionError:
        raise ModelRetry(
            f"Permission denied accessing directory: {target_path}. Please check directory permissions."
        )
    except Exception as e:
        raise ModelRetry(
            f"Unexpected error generating directory tree for {target_path}: {str(e)}. Please try again or choose a different directory."
        )
