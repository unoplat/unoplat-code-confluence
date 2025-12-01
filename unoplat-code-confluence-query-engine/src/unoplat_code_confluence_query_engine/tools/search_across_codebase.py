"""
Search across codebase using ripgrep for fast pattern matching.

This module provides a Pydantic AI tool that leverages ripgrep to search
for patterns across an entire codebase with support for regex/literal matching,
file filtering, case sensitivity options, and contextual preview.
"""

from __future__ import annotations

import os
import asyncio
import json
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_ai import RunContext
from pydantic_ai.exceptions import ModelRetry

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


class SearchMatch(BaseModel):
    """Represents a single search match with contextual information."""

    file_path: str = Field(..., description="Path relative to the codebase root")
    line: int = Field(..., description="1-based line number of the match")
    text: str = Field(..., description="The line content containing the match")
    preview: Optional[str] = Field(
        None,
        description=(
            "Optional multi-line preview including up to `context` lines "
            "before and after the match. The matched line is included in the preview."
        ),
    )


class SearchResults(BaseModel):
    """Container for search results with metadata."""

    pattern: str = Field(..., description="The search pattern used")
    matches: List[SearchMatch] = Field(
        default_factory=list, description="Matches, capped by max_results"
    )
    total: int = Field(
        ..., description="Total number of matches found across all files"
    )
    truncated: bool = Field(
        ..., description="True if results were capped by max_results"
    )


def _build_ripgrep_command(
    pattern: str,
    codebase_path: str,
    mode: Literal["regex", "literal"],
    glob: Optional[List[str]],
    case: Literal["smart", "sensitive", "insensitive"],
    context: int,
    search_path: str,
) -> List[str]:
    """Build ripgrep command arguments based on search parameters.

    Args:
        pattern: Search pattern to match.
        codebase_path: Base path to search in.
        mode: Search mode (regex or literal).
        glob: File patterns to include/exclude.
        case: Case sensitivity strategy.
        context: Number of context lines.
        search_path: Specific path to search within codebase.

    Returns:
        Command arguments list for ripgrep execution.
    """
    cmd = ["rg", "--json", "--no-heading", "--with-filename"]

    # Pattern mode
    if mode == "literal":
        cmd.append("--fixed-strings")

    # Case sensitivity
    if case == "smart":
        cmd.append("--smart-case")
    elif case == "sensitive":
        cmd.append("--case-sensitive")
    elif case == "insensitive":
        cmd.append("--ignore-case")

    # Context lines
    if context > 0:
        cmd.extend(["--context", str(context)])

    # File filtering
    if glob:
        for pattern_glob in glob:
            cmd.extend(["--glob", pattern_glob])

    # Default behavior
    cmd.extend(
        [
            "--hidden",  # Include hidden files
            "--glob",
            "!.git/*",  # Exclude .git directory
            "--glob",
            "!node_modules/*",  # Exclude node_modules
            "--glob",
            "!__pycache__/*",  # Exclude Python cache
            "--no-messages",  # Suppress error messages for permissions etc
        ]
    )

    # Add pattern and search path (relative to codebase root)
    cmd.append(pattern)
    cmd.append(search_path)

    return cmd


def _parse_ripgrep_json_output(
    output_lines: List[str], max_results: int, context: int
) -> tuple[List[SearchMatch], int, bool]:
    """Parse ripgrep JSON output into SearchMatch objects.

    Args:
        output_lines: Lines of JSON output from ripgrep command.
        max_results: Maximum number of results to return.
        context: Number of context lines requested.

    Returns:
        Tuple of (matches, total_found, truncated) where matches contains SearchMatch objects,
        total_found is the count of all matches, and truncated indicates if results were capped.
    """
    matches: List[SearchMatch] = []
    total_found = 0
    context_buffer: Dict[str, Dict[int, str]] = {}  # file -> {line_num: content}
    match_lines: Dict[str, List[int]] = {}  # file -> [match_line_numbers]

    # Parse all JSON lines first
    for line in output_lines:
        if not line.strip():
            continue

        try:
            data = json.loads(line)
            msg_type = data.get("type")

            if msg_type == "match":
                match_data = data.get("data", {})
                file_path = match_data.get("path", {}).get("text", "")
                line_number = match_data.get("line_number")
                line_text = match_data.get("lines", {}).get("text", "")

                if file_path and line_number and line_text is not None:
                    # Store match info
                    if file_path not in match_lines:
                        match_lines[file_path] = []
                        context_buffer[file_path] = {}

                    match_lines[file_path].append(line_number)
                    context_buffer[file_path][line_number] = line_text
                    total_found += 1

            elif msg_type == "context":
                context_data = data.get("data", {})
                file_path = context_data.get("path", {}).get("text", "")
                line_number = context_data.get("line_number")
                line_text = context_data.get("lines", {}).get("text", "")

                if file_path and line_number and line_text is not None:
                    if file_path not in context_buffer:
                        context_buffer[file_path] = {}
                    context_buffer[file_path][line_number] = line_text

        except (json.JSONDecodeError, KeyError, TypeError):
            # Skip malformed JSON lines
            continue

    # Build SearchMatch objects with previews
    result_count = 0
    for file_path, match_line_nums in match_lines.items():
        for line_num in sorted(match_line_nums):
            if result_count >= max_results:
                break

            line_text = context_buffer[file_path].get(line_num, "")

            # Build preview with context lines
            preview_lines = []
            if context > 0:
                start_line = max(1, line_num - context)
                end_line = line_num + context

                for preview_line_num in range(start_line, end_line + 1):
                    if preview_line_num in context_buffer[file_path]:
                        preview_lines.append(
                            context_buffer[file_path][preview_line_num]
                        )

            preview = "\n".join(preview_lines) if preview_lines else None

            matches.append(
                SearchMatch(
                    file_path=file_path, line=line_num, text=line_text, preview=preview
                )
            )
            result_count += 1

        if result_count >= max_results:
            break

    truncated = total_found > max_results
    return matches, total_found, truncated


async def search_across_codebase(
    ctx: RunContext[AgentDependencies],
    pattern: str,
    mode: Literal["regex", "literal"] = "regex",
    glob: Optional[List[str]] = None,
    case: Literal["smart", "sensitive", "insensitive"] = "smart",
    context: int = 2,
    max_results: int = 50,
    timeout_s: int = 20,
    path: Optional[str] = None,
) -> SearchResults:
    """
    Search for patterns across the entire codebase using ripgrep.
    This tool provides fast, powerful code searching capabilities with support for
    both regex and literal pattern matching, file filtering, and contextual previews.

    Args:
        pattern: The search pattern to find
        mode: Whether to treat pattern as "regex" or "literal" (default: "regex")
        glob: Optional list of glob patterns to filter files (e.g., ["*.py", "**/*.ts"])
        case: Case strategy - "smart" (insensitive unless uppercase), "sensitive", or "insensitive"
        context: Number of lines to include before/after each match (default: 2)
        max_results: Global maximum number of matches to return (default: 50)
        timeout_s: Timeout in seconds for the search operation (default: 20)
        path: Optional search path relative to the codebase root. If provided, search starts in this subdirectory or file; otherwise searches the entire codebase.

    Returns:
        SearchResults containing matches with contextual information

    Examples:
        # Search for function definitions
        results = await search_across_codebase(pattern=r"^def \\w+", mode="regex", glob=["*.py"], context=3
        )

        # Find TODO comments (case insensitive)
        results = await search_across_codebase(pattern="TODO", mode="literal", case="insensitive", max_results=20
        )

        # Search for specific imports
        results = await search_across_codebase(pattern="from unoplat_code_confluence", mode="literal", glob=["**/*.py"])
    """
    # Validate inputs
    if not pattern.strip():
        raise ModelRetry("Search pattern cannot be empty")

    # Get codebase path from dependencies
    codebase_path = ctx.deps.codebase_metadata.codebase_path
    if not codebase_path or not os.path.exists(codebase_path):
        raise ModelRetry(f"Invalid codebase path: {codebase_path}")

    if not os.path.isdir(codebase_path):
        raise ModelRetry(f"Codebase path is not a directory: {codebase_path}")

    # Validate parameters
    if context < 0:
        context = 0
    if max_results < 1:
        max_results = 1
    if timeout_s < 1:
        timeout_s = 1

    # Resolve search path within codebase
    if path is None or not str(path).strip():
        search_root = codebase_path
        rg_path = "."
    else:
        # Support absolute or relative inputs; normalize to absolute then ensure within codebase
        candidate_abs = (
            os.path.abspath(os.path.join(codebase_path, path))
            if not os.path.isabs(path)
            else os.path.abspath(path)
        )
        codebase_abs = os.path.abspath(codebase_path)
        # Ensure candidate is inside codebase
        try:
            common = os.path.commonpath([candidate_abs, codebase_abs])
        except ValueError:
            raise ModelRetry("Invalid search path provided")
        if common != codebase_abs:
            raise ModelRetry("Search path must be inside the codebase root")
        if not os.path.exists(candidate_abs):
            raise ModelRetry(f"Search path does not exist: {path}")
        search_root = candidate_abs
        # Build ripgrep target path relative to codebase cwd for better portability
        rg_path = os.path.relpath(search_root, codebase_abs)
        if rg_path == ".":
            rg_path = "."

    # Build ripgrep command
    cmd = _build_ripgrep_command(
        pattern, codebase_path, mode, glob, case, context, rg_path
    )

    try:
        # Execute ripgrep with timeout
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=codebase_path,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=timeout_s
            )
        except asyncio.TimeoutError:
            # Kill the process and raise error
            process.kill()
            await process.wait()
            raise ModelRetry(f"Search timed out after {timeout_s} seconds")

        # Handle process results
        if process.returncode == 0:
            # Success - parse output
            stdout_str = stdout_bytes.decode("utf-8", errors="replace")
            output_lines = stdout_str.strip().split("\n") if stdout_str.strip() else []

            matches, total_found, truncated = _parse_ripgrep_json_output(
                output_lines, max_results, context
            )

            return SearchResults(
                pattern=pattern, matches=matches, total=total_found, truncated=truncated
            )

        elif process.returncode == 1:
            # No matches found - this is normal
            return SearchResults(pattern=pattern, matches=[], total=0, truncated=False)
        else:
            # Error occurred
            stderr_str = stderr_bytes.decode("utf-8", errors="replace")
            if (
                "No such file or directory" in stderr_str
                or "command not found" in stderr_str
            ):
                raise ModelRetry(
                    "ripgrep not installed. Install via: brew install ripgrep (macOS) "
                    "or apt install ripgrep (Ubuntu)"
                )
            else:
                # Include stderr in error for debugging
                raise ModelRetry(f"Search failed: {stderr_str}")

    except FileNotFoundError:
        raise ModelRetry(
            "ripgrep not installed. Install via: brew install ripgrep (macOS) "
            "or apt install ripgrep (Ubuntu)"
        )
    except Exception as e:
        raise ModelRetry(f"Search failed with unexpected error: {str(e)}")
