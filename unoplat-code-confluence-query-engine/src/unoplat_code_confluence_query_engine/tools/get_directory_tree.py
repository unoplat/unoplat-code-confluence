import asyncio
from typing import Optional

from aiopath import AsyncPath
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


async def get_directory_tree(
    ctx: RunContext[AgentDependencies],
    depth: int,
    path: Optional[str] = None,
) -> str:
    """Get a text-based directory tree for a given directory. REQUIRED: You must provide the depth parameter.

    IMPORTANT: This tool will FAIL if called without the depth argument.
    Always provide depth when calling this tool.

    Args:
        depth: REQUIRED - Maximum directory depth to traverse (must be >= 1). You MUST provide
            this parameter. Do NOT call this tool without depth. Valid examples: depth=2 or depth=3.
            INVALID calls: get_directory_tree() or get_directory_tree({}) without depth.
        path: Optional absolute filesystem path starting with /. Defaults to codebase root if not
            provided. Valid examples: /opt/unoplat/repositories/my-repo/src or
            /opt/unoplat/repositories/my-repo/config. INVALID: relative paths like 'src' or './config'.

    Returns:
        The formatted directory tree structure as text.
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
            f"Depth should be >= 1. Please provide a valid depth value instead of: {depth}"
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
        # return DirectoryTree(tree=tree_output)
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
