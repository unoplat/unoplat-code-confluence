from typing import Optional

import aiofiles
from aiopath import AsyncPath
from loguru import logger
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


async def read_file_content(
    ctx: RunContext[AgentDependencies],
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
) -> str:
    """Read content from a file with optional line range filtering.

    Args:
        file_path: Absolute path to the file to read
        start_line: Starting line number (1-based, inclusive). If None, starts from beginning
        end_line: Ending line number (1-based, inclusive). If None, reads to end

    Returns:
        The file content as a string, optionally filtered by line range
    """
    # Log the file read attempt
    if start_line is not None or end_line is not None:
        logger.debug(
            "Attempting to read file: {} (lines {}-{})",
            file_path,
            start_line or "start",
            end_line or "end",
        )
    else:
        logger.debug("Attempting to read file: {}", file_path)

    # Validate file path security
    path = AsyncPath(file_path)

    # Check if path is absolute and exists
    if not path.is_absolute():
        logger.debug("File read failed - path is not absolute: {}", file_path)
        raise ModelRetry(
            f"File path must be absolute. Please provide an absolute path instead of: {file_path}"
        )

    if not await path.exists():
        logger.debug("File read failed - file not found: {}", file_path)
        raise ModelRetry(
            f"File not found at path: {file_path}. Please check the file path and try again."
        )

    if not await path.is_file():
        logger.debug("File read failed - path is not a file: {}", file_path)
        raise ModelRetry(
            f"The path '{file_path}' is not a file. Please provide a valid file path."
        )

    # Validate line range parameters
    if start_line is not None and start_line < 1:
        logger.debug(
            "File read failed - invalid start_line {}: must be >= 1", start_line
        )
        raise ModelRetry(
            "start_line must be >= 1. Please provide a valid line number starting from 1."
        )

    if end_line is not None and end_line < 1:
        logger.debug("File read failed - invalid end_line {}: must be >= 1", end_line)
        raise ModelRetry(
            "end_line must be >= 1. Please provide a valid line number starting from 1."
        )

    if start_line is not None and end_line is not None and start_line > end_line:
        logger.debug(
            "File read failed - invalid line range: start_line {} > end_line {}",
            start_line,
            end_line,
        )
        raise ModelRetry(
            "start_line cannot be greater than end_line. Please provide a valid line range."
        )

    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file:
            if start_line is None and end_line is None:
                # Read entire file - simple and efficient
                content = await file.read()
                logger.debug(
                    "Successfully read entire file: {} ({} characters)",
                    file_path,
                    len(content),
                )
                return content
            else:
                # Use async iteration for line range reading
                lines = []
                line_num = 0

                async for line in file:
                    line_num += 1  # 1-based indexing

                    if start_line and line_num < start_line:
                        continue
                    if end_line and line_num > end_line:
                        break

                    # Normalize line endings - strip all variations and use \n consistently
                    lines.append(line.rstrip("\r\n"))

                # Check if start_line is beyond file length
                if start_line and not lines and line_num > 0:
                    logger.debug(
                        "File read failed - start_line {} exceeds file length {} for: {}",
                        start_line,
                        line_num,
                        file_path,
                    )
                    raise ModelRetry(
                        f"The file has only {line_num} lines, but you requested to start from line {start_line}. Please adjust the line range."
                    )

                result = "\n".join(lines)
                logger.debug(
                    "Successfully read lines {}-{} from file: {} ({} lines, {} characters)",
                    start_line or 1,
                    end_line or line_num,
                    file_path,
                    len(lines),
                    len(result),
                )
                return result

    except PermissionError:
        logger.debug("File read failed - permission denied: {}", file_path)
        raise ModelRetry(
            f"Permission denied reading file: {file_path}. Please check file permissions or choose a different file."
        )
    except UnicodeDecodeError as e:
        logger.debug(
            "File read failed - unicode decode error for: {} ({})", file_path, e
        )
        raise ModelRetry(
            f"Unable to decode file as UTF-8: {file_path}. The file might be binary or use a different encoding. Please try a different file."
        )
    except Exception as e:
        logger.debug("File read failed - unexpected error for: {} ({})", file_path, e)
        raise ModelRetry(
            f"Unexpected error reading file {file_path}: {str(e)}. Please try again or choose a different file."
        )
