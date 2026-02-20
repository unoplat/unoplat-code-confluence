"""OpenCode-style file tools for AGENTS updater agent.

Credit: semantics are adapted from OpenCode read/edit/patch tool behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiofiles
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)

READ_MAX_LIMIT = 2000
READ_MAX_LINE_LENGTH = 2000


@dataclass(frozen=True)
class ReplacementChunk:
    """Replacement chunk parsed from update patch hunks."""

    old_text: str
    new_text: str
    hint: str = ""


@dataclass(frozen=True)
class PatchOperation:
    """Parsed patch operation."""

    operation_type: str
    file_path: str
    chunks: tuple[ReplacementChunk, ...] = ()
    add_content: str = ""


def _codebase_root(ctx: RunContext[AgentDependencies]) -> Path:
    return Path(ctx.deps.codebase_metadata.codebase_path).resolve()


def _normalize_scoped_path(
    ctx: RunContext[AgentDependencies],
    *,
    file_path: str,
    allow_missing: bool,
) -> Path:
    candidate = Path(file_path)
    if not candidate.is_absolute():
        raise ModelRetry(f"out_of_scope: file_path must be absolute, got '{file_path}'")

    normalized = candidate.resolve(strict=False)
    root = _codebase_root(ctx)
    if normalized != root and root not in normalized.parents:
        raise ModelRetry(
            "out_of_scope: file_path is outside current codebase root "
            f"'{root.as_posix()}'"
        )

    if not allow_missing and not normalized.exists():
        raise ModelRetry(f"not_found: file does not exist at '{normalized.as_posix()}'")

    return normalized


def _validate_read_bounds(offset: int, limit: int) -> int:
    if offset < 0:
        raise ModelRetry("invalid_patch: offset must be >= 0")
    if limit < 1:
        raise ModelRetry("invalid_patch: limit must be >= 1")
    return min(limit, READ_MAX_LIMIT)


def _format_numbered_line(line_number: int, content: str) -> str:
    truncated = content
    if len(truncated) > READ_MAX_LINE_LENGTH:
        truncated = truncated[:READ_MAX_LINE_LENGTH] + "..."
    return f"{line_number:05d}| {truncated}"


def _parse_patch_operations(patch_text: str) -> list[PatchOperation]:
    lines = patch_text.splitlines()
    if len(lines) < 2 or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        raise ModelRetry(
            "invalid_patch: patch must start with '*** Begin Patch' and end with '*** End Patch'"
        )

    operations: list[PatchOperation] = []
    index = 1
    while index < len(lines) - 1:
        header = lines[index]
        if header.startswith("*** Add File: "):
            operation, index = _parse_add_operation(lines, index)
            operations.append(operation)
            continue
        if header.startswith("*** Delete File: "):
            file_path = header.removeprefix("*** Delete File: ").strip()
            if not file_path:
                raise ModelRetry("invalid_patch: delete operation missing file path")
            operations.append(
                PatchOperation(operation_type="delete", file_path=file_path)
            )
            index += 1
            continue
        if header.startswith("*** Update File: "):
            operation, index = _parse_update_operation(lines, index)
            operations.append(operation)
            continue
        if header == "*** End of File":
            index += 1
            continue
        raise ModelRetry(f"invalid_patch: unknown operation header '{header}'")

    if not operations:
        raise ModelRetry("invalid_patch: patch contains no operations")
    return operations


def _parse_add_operation(lines: list[str], index: int) -> tuple[PatchOperation, int]:
    header = lines[index]
    file_path = header.removeprefix("*** Add File: ").strip()
    if not file_path:
        raise ModelRetry("invalid_patch: add operation missing file path")

    index += 1
    content_lines: list[str] = []
    while index < len(lines) - 1 and not lines[index].startswith("*** "):
        line = lines[index]
        if not line.startswith("+"):
            raise ModelRetry("invalid_patch: add operation lines must start with '+'")
        content_lines.append(line[1:])
        index += 1

    return (
        PatchOperation(
            operation_type="add",
            file_path=file_path,
            add_content="\n".join(content_lines),
        ),
        index,
    )


def _parse_update_operation(lines: list[str], index: int) -> tuple[PatchOperation, int]:
    header = lines[index]
    file_path = header.removeprefix("*** Update File: ").strip()
    if not file_path:
        raise ModelRetry("invalid_patch: update operation missing file path")

    index += 1
    chunks: list[ReplacementChunk] = []

    while index < len(lines) - 1 and not lines[index].startswith("*** "):
        if not lines[index].startswith("@@"):
            raise ModelRetry("invalid_patch: update chunks must start with '@@'")
        hint = lines[index][2:].strip()
        index += 1
        old_lines: list[str] = []
        new_lines: list[str] = []
        while (
            index < len(lines) - 1
            and not lines[index].startswith("*** ")
            and not lines[index].startswith("@@")
        ):
            line = lines[index]
            if line.startswith("-"):
                old_lines.append(line[1:])
            elif line.startswith("+"):
                new_lines.append(line[1:])
            elif line.startswith(" ") or line == "":
                # Context line — present in both old and new text for anchoring
                context_content = line[1:] if line.startswith(" ") else ""
                old_lines.append(context_content)
                new_lines.append(context_content)
            else:
                raise ModelRetry(
                    "invalid_patch: update chunk lines must start with '-', '+', or ' ' (context)"
                )
            index += 1

        if not old_lines:
            raise ModelRetry("invalid_patch: update chunk missing old text")
        chunk = ReplacementChunk(
            old_text="\n".join(old_lines),
            new_text="\n".join(new_lines),
            hint=hint,
        )
        chunks.append(chunk)

    if not chunks:
        raise ModelRetry("invalid_patch: update operation contains no chunks")

    return (
        PatchOperation(
            operation_type="update",
            file_path=file_path,
            chunks=tuple(chunks),
        ),
        index,
    )


def _apply_replacement_chunks(
    file_content: str,
    *,
    chunks: tuple[ReplacementChunk, ...],
) -> str:
    updated = file_content
    for chunk in chunks:
        occurrences = updated.count(chunk.old_text)
        if occurrences == 0:
            raise ModelRetry("not_found: update chunk target text not found")
        if occurrences > 1:
            raise ModelRetry(
                "ambiguous_match: update chunk target appears multiple times"
            )
        updated = updated.replace(chunk.old_text, chunk.new_text, 1)
    return updated


async def updater_read_file(
    ctx: RunContext[AgentDependencies],
    file_path: str,
    offset: int = 0,
    limit: int = READ_MAX_LIMIT,
) -> str:
    """Read file content with absolute path guard and truncation."""
    effective_limit = _validate_read_bounds(offset, limit)
    target = _normalize_scoped_path(ctx, file_path=file_path, allow_missing=False)
    if target.is_dir():
        raise ModelRetry(f"not_found: path is a directory '{target.as_posix()}'")

    output_lines: list[str] = []
    total_lines = 0
    async with aiofiles.open(target, mode="r", encoding="utf-8") as handle:
        async for raw_line in handle:
            total_lines += 1
            if total_lines <= offset:
                continue
            if len(output_lines) >= effective_limit:
                break
            output_lines.append(
                _format_numbered_line(total_lines, raw_line.rstrip("\r\n"))
            )

    is_truncated = total_lines > offset + len(output_lines)
    suffix = (
        f"\n[truncated] showing {len(output_lines)} lines from offset {offset}; "
        f"use a higher offset to continue"
        if is_truncated
        else ""
    )
    return "\n".join(output_lines) + suffix


async def updater_edit_file(
    ctx: RunContext[AgentDependencies],
    file_path: str,
    old_string: str,
    new_string: str,
    expected_replacements: int | None = None,
) -> dict[str, str | int | bool]:
    """Edit file via exact replacement with deterministic error outcomes."""
    if old_string == new_string:
        raise ModelRetry("invalid_patch: old_string and new_string are identical")

    target = _normalize_scoped_path(ctx, file_path=file_path, allow_missing=False)
    if target.is_dir():
        raise ModelRetry(f"not_found: path is a directory '{target.as_posix()}'")

    async with aiofiles.open(target, mode="r", encoding="utf-8") as handle:
        existing_content = await handle.read()

    occurrences = existing_content.count(old_string)
    if occurrences == 0:
        raise ModelRetry("not_found: old_string was not found in target file")

    if expected_replacements is not None and expected_replacements < 1:
        raise ModelRetry("invalid_patch: expected_replacements must be >= 1")

    if expected_replacements is None and occurrences > 1:
        raise ModelRetry(
            "ambiguous_match: old_string appears multiple times; set expected_replacements"
        )

    if expected_replacements is not None and occurrences != expected_replacements:
        raise ModelRetry(
            "ambiguous_match: expected_replacements does not match occurrence count"
        )

    replace_count = expected_replacements if expected_replacements is not None else 1
    updated_content = existing_content.replace(old_string, new_string, replace_count)
    changed = updated_content != existing_content

    if changed:
        async with aiofiles.open(target, mode="w", encoding="utf-8") as handle:
            await handle.write(updated_content)

    return {
        "file_path": target.as_posix(),
        "changed": changed,
        "replacements": replace_count,
        "status": "updated" if changed else "unchanged",
    }


async def updater_apply_patch(
    ctx: RunContext[AgentDependencies],
    patch_text: str,
) -> dict[str, str | int]:
    """Apply OpenCode-style patch with full validation before writes."""
    operations = _parse_patch_operations(patch_text)

    planned_writes: dict[Path, str | None] = {}
    skipped_noop_files = 0
    for operation in operations:
        scoped = _normalize_scoped_path(
            ctx,
            file_path=operation.file_path,
            allow_missing=operation.operation_type == "add",
        )

        if operation.operation_type == "delete":
            if not scoped.exists() or scoped.is_dir():
                raise ModelRetry(
                    f"not_found: delete target missing '{scoped.as_posix()}'"
                )
            planned_writes[scoped] = None
            continue

        if operation.operation_type == "add":
            if scoped.exists() and scoped.is_dir():
                raise ModelRetry(
                    f"not_found: add target is a directory '{scoped.as_posix()}'"
                )
            if scoped.exists():
                async with aiofiles.open(scoped, mode="r", encoding="utf-8") as handle:
                    existing_content = await handle.read()
                if existing_content == operation.add_content:
                    skipped_noop_files += 1
                    continue
            planned_writes[scoped] = operation.add_content
            continue

        if operation.operation_type == "update":
            if not scoped.exists() or scoped.is_dir():
                raise ModelRetry(
                    f"not_found: update target missing '{scoped.as_posix()}'"
                )
            async with aiofiles.open(scoped, mode="r", encoding="utf-8") as handle:
                existing_content = await handle.read()
            updated_content = _apply_replacement_chunks(
                existing_content,
                chunks=operation.chunks,
            )
            if updated_content == existing_content:
                skipped_noop_files += 1
                continue
            planned_writes[scoped] = updated_content
            continue

        raise ModelRetry("invalid_patch: unsupported operation type")

    changed_files = 0
    for target, content in planned_writes.items():
        if content is None:
            target.unlink()
            changed_files += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(target, mode="w", encoding="utf-8") as handle:
            await handle.write(content)
        changed_files += 1

    return {
        "status": "applied",
        "operations": len(operations),
        "changed_files": changed_files,
        "skipped_noop_files": skipped_noop_files,
    }
