"""Unit tests for OpenCode-style patch parser and applier.

Covers context line support (space-prefixed lines), @@ hint metadata retention,
*** End of File sentinel handling, multi-chunk parsing, and full patch application
with file I/O.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from pydantic_ai import ModelRetry
import pytest

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.agents_md_updater_tools import (
    READ_MAX_LIMIT,
    _apply_replacement_chunks,
    _parse_patch_operations,
    updater_apply_patch,
    updater_edit_file,
    updater_read_file,
)

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────


def _build_patch(*body_lines: str) -> str:
    """Wrap body lines in Begin/End Patch envelope."""
    return "\n".join(["*** Begin Patch", *body_lines, "*** End Patch"])


def _make_run_context(codebase_path: str) -> MagicMock:
    """Create a minimal RunContext mock wired to AgentDependencies."""
    metadata = CodebaseMetadata(
        codebase_name="test-codebase",
        codebase_path=codebase_path,
        codebase_programming_language="python",
        codebase_package_manager="uv",
    )
    deps = AgentDependencies(
        repository_qualified_name="owner/repo",
        codebase_metadata=metadata,
        repository_workflow_run_id="wf-run-001",
        agent_name="test-agent",
    )
    ctx = MagicMock()
    ctx.deps = deps
    return ctx


# ──────────────────────────────────────────────────────────────────────────────
# 1. Context lines (space-prefixed) parsed into both old and new
# ──────────────────────────────────────────────────────────────────────────────


class TestParseUpdateWithContextLines:
    """Space-prefixed lines parsed into both old_lines and new_lines."""

    def test_context_lines_appear_in_both_old_and_new(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            " # Header",
            "-old line",
            "+new line",
            " # Footer",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 1
        assert ops[0].operation_type == "update"
        assert len(ops[0].chunks) == 1

        chunk = ops[0].chunks[0]
        assert chunk.old_text == "# Header\nold line\n# Footer"
        assert chunk.new_text == "# Header\nnew line\n# Footer"


# ──────────────────────────────────────────────────────────────────────────────
# 2. Empty context lines treated as blank context
# ──────────────────────────────────────────────────────────────────────────────


class TestParseUpdateWithEmptyContextLines:
    """Bare empty lines treated as blank context lines."""

    def test_empty_line_becomes_blank_context(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            "-old",
            "",
            "+new",
        )
        ops = _parse_patch_operations(patch)
        chunk = ops[0].chunks[0]

        # Empty line adds "" to both old and new
        assert chunk.old_text == "old\n"
        assert chunk.new_text == "\nnew"


# ──────────────────────────────────────────────────────────────────────────────
# 3. @@ context hint accepted AND hint metadata retained
# ──────────────────────────────────────────────────────────────────────────────


class TestParseUpdateWithContextHintAfterAt:
    """'@@ some_hint' accepted and hint stored on ReplacementChunk."""

    def test_function_hint_retained(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@ def my_function",
            "-old line",
            "+new line",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 1
        chunk = ops[0].chunks[0]
        assert chunk.hint == "def my_function"
        assert chunk.old_text == "old line"
        assert chunk.new_text == "new line"

    def test_class_hint_retained(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@ class MyClass",
            "-removed",
            "+added",
        )
        ops = _parse_patch_operations(patch)
        assert ops[0].chunks[0].hint == "class MyClass"

    def test_bare_at_has_empty_hint(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            "-old",
            "+new",
        )
        ops = _parse_patch_operations(patch)
        assert ops[0].chunks[0].hint == ""

    def test_multi_chunk_hints_independent(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@ section_one",
            "-alpha",
            "+beta",
            "@@ section_two",
            "-gamma",
            "+delta",
        )
        ops = _parse_patch_operations(patch)
        assert ops[0].chunks[0].hint == "section_one"
        assert ops[0].chunks[1].hint == "section_two"


# ──────────────────────────────────────────────────────────────────────────────
# 4. Existing -/+ only patches still work (regression guard)
# ──────────────────────────────────────────────────────────────────────────────


class TestParseUpdatePureMinusPlusRegression:
    """Existing -/+ only patches still work (no regression)."""

    def test_simple_minus_plus_patch(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            "-old content",
            "+new content",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 1
        chunk = ops[0].chunks[0]
        assert chunk.old_text == "old content"
        assert chunk.new_text == "new content"

    def test_multiline_minus_plus_patch(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            "-line one",
            "-line two",
            "+replaced one",
            "+replaced two",
        )
        ops = _parse_patch_operations(patch)
        chunk = ops[0].chunks[0]

        assert chunk.old_text == "line one\nline two"
        assert chunk.new_text == "replaced one\nreplaced two"


# ──────────────────────────────────────────────────────────────────────────────
# 5. Multiple @@ chunks with context lines
# ──────────────────────────────────────────────────────────────────────────────


class TestParseUpdateMultiChunkWithContext:
    """Multiple @@ chunks with context lines."""

    def test_two_chunks_with_context(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            " # Section A",
            "-old A",
            "+new A",
            "@@",
            " # Section B",
            "-old B",
            "+new B",
            " # End B",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 1
        assert len(ops[0].chunks) == 2

        chunk_a = ops[0].chunks[0]
        assert chunk_a.old_text == "# Section A\nold A"
        assert chunk_a.new_text == "# Section A\nnew A"

        chunk_b = ops[0].chunks[1]
        assert chunk_b.old_text == "# Section B\nold B\n# End B"
        assert chunk_b.new_text == "# Section B\nnew B\n# End B"

    def test_multi_chunk_with_hints_and_context(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@ first_section",
            "-alpha",
            "+beta",
            "@@ second_section",
            " context",
            "-gamma",
            "+delta",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops[0].chunks) == 2
        assert ops[0].chunks[0].hint == "first_section"
        assert ops[0].chunks[1].hint == "second_section"
        assert ops[0].chunks[1].old_text == "context\ngamma"
        assert ops[0].chunks[1].new_text == "context\ndelta"


# ──────────────────────────────────────────────────────────────────────────────
# 6. *** End of File sentinel handled gracefully
# ──────────────────────────────────────────────────────────────────────────────


class TestEndOfFileMarkerNoCrash:
    """'*** End of File' is accepted as a valid sentinel between operations."""

    def test_end_of_file_between_two_updates(self) -> None:
        """*** End of File between two update operations is skipped cleanly."""
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            " context",
            "-old",
            "+new",
            "*** End of File",
            "*** Update File: /repo/README.md",
            "@@",
            "-readme old",
            "+readme new",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 2
        assert ops[0].file_path == "/repo/AGENTS.md"
        assert ops[0].chunks[0].old_text == "context\nold"
        assert ops[0].chunks[0].new_text == "context\nnew"
        assert ops[1].file_path == "/repo/README.md"
        assert ops[1].chunks[0].old_text == "readme old"
        assert ops[1].chunks[0].new_text == "readme new"

    def test_end_of_file_after_last_operation(self) -> None:
        """*** End of File after the final update operation is skipped cleanly."""
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            " context line",
            "-old line",
            "+new line",
            "*** End of File",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 1
        chunk = ops[0].chunks[0]
        assert chunk.old_text == "context line\nold line"
        assert chunk.new_text == "context line\nnew line"

    def test_end_of_file_after_add_operation(self) -> None:
        """*** End of File after an add operation is skipped cleanly."""
        patch = _build_patch(
            "*** Add File: /repo/NEW.md",
            "+# New File",
            "+content",
            "*** End of File",
        )
        ops = _parse_patch_operations(patch)

        assert len(ops) == 1
        assert ops[0].operation_type == "add"
        assert ops[0].add_content == "# New File\ncontent"


# ──────────────────────────────────────────────────────────────────────────────
# 7. _apply_replacement_chunks with context-expanded old/new text
# ──────────────────────────────────────────────────────────────────────────────


class TestApplyReplacementChunksWithContext:
    """Full string replacement with context-expanded old/new text."""

    def test_context_anchored_replacement(self) -> None:
        original = "# Header\nold line\n# Footer\n"
        ops = _parse_patch_operations(
            _build_patch(
                "*** Update File: /repo/AGENTS.md",
                "@@",
                " # Header",
                "-old line",
                "+new line",
                " # Footer",
            )
        )
        chunks = ops[0].chunks

        result = _apply_replacement_chunks(original, chunks=chunks)
        assert result == "# Header\nnew line\n# Footer\n"

    def test_context_prevents_ambiguous_match(self) -> None:
        """Context lines disambiguate when the same line appears multiple times."""
        original = "# A\nshared line\n# B\nshared line\n"

        ops = _parse_patch_operations(
            _build_patch(
                "*** Update File: /repo/file.md",
                "@@",
                " # A",
                "-shared line",
                "+replaced line",
            )
        )
        chunks = ops[0].chunks

        result = _apply_replacement_chunks(original, chunks=chunks)
        assert result == "# A\nreplaced line\n# B\nshared line\n"


# ──────────────────────────────────────────────────────────────────────────────
# 8. Full integration: temp file → apply patch with context → verify output
# ──────────────────────────────────────────────────────────────────────────────


class TestFullApplyPatchWithContextLines:
    """Integration: create temp file, apply patch with context, verify output."""

    @pytest.mark.asyncio
    async def test_apply_patch_updates_file_with_context(self, tmp_path: Path) -> None:
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("# Title\n\nold content here\n\n# End\n")

        ctx = _make_run_context(str(tmp_path))

        patch = _build_patch(
            f"*** Update File: {agents_md}",
            "@@",
            " # Title",
            " ",
            "-old content here",
            "+new content here",
            " ",
            " # End",
        )

        result = await updater_apply_patch(ctx, patch)

        assert result["status"] == "applied"
        assert result["changed_files"] == 1

        updated = agents_md.read_text()
        assert updated == "# Title\n\nnew content here\n\n# End\n"

    @pytest.mark.asyncio
    async def test_apply_patch_without_context_still_works(
        self, tmp_path: Path
    ) -> None:
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("line one\nline two\nline three\n")

        ctx = _make_run_context(str(tmp_path))

        patch = _build_patch(
            f"*** Update File: {agents_md}",
            "@@",
            "-line two",
            "+line TWO",
        )

        result = await updater_apply_patch(ctx, patch)

        assert result["status"] == "applied"
        updated = agents_md.read_text()
        assert updated == "line one\nline TWO\nline three\n"

    @pytest.mark.asyncio
    async def test_apply_patch_with_end_of_file_sentinel(self, tmp_path: Path) -> None:
        """Full round-trip: patch with *** End of File applied to real file."""
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("# Title\nold content\n# End\n")

        ctx = _make_run_context(str(tmp_path))

        patch = _build_patch(
            f"*** Update File: {agents_md}",
            "@@",
            " # Title",
            "-old content",
            "+new content",
            " # End",
            "*** End of File",
        )

        result = await updater_apply_patch(ctx, patch)

        assert result["status"] == "applied"
        assert result["changed_files"] == 1
        assert agents_md.read_text() == "# Title\nnew content\n# End\n"


# ──────────────────────────────────────────────────────────────────────────────
# 9. Invalid lines still rejected
# ──────────────────────────────────────────────────────────────────────────────


class TestInvalidLinesStillRejected:
    """Lines not starting with -, +, or space are rejected."""

    def test_tab_prefixed_line_rejected(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            "-old",
            "\tinvalid tab line",
            "+new",
        )
        with pytest.raises(ModelRetry, match="must start with"):
            _parse_patch_operations(patch)

    def test_bare_text_rejected(self) -> None:
        patch = _build_patch(
            "*** Update File: /repo/AGENTS.md",
            "@@",
            "no prefix at all",
        )
        with pytest.raises(ModelRetry, match="must start with"):
            _parse_patch_operations(patch)


# ──────────────────────────────────────────────────────────────────────────────
# 10. Root-scope enforcement regression tests
# ──────────────────────────────────────────────────────────────────────────────


class TestRootScopeEnforcement:
    """Regression tests for codebase-root-only file operation enforcement."""

    @pytest.mark.asyncio
    async def test_relative_path_rejected_with_out_of_scope(
        self, tmp_path: Path
    ) -> None:
        """Relative paths must raise ModelRetry with 'out_of_scope' prefix."""
        ctx = _make_run_context(str(tmp_path))
        patch = _build_patch(
            "*** Update File: relative/path/AGENTS.md",
            "@@",
            "-old",
            "+new",
        )
        with pytest.raises(ModelRetry, match="out_of_scope"):
            await updater_apply_patch(ctx, patch)

    @pytest.mark.asyncio
    async def test_path_outside_codebase_root_rejected(self, tmp_path: Path) -> None:
        """Absolute path outside codebase root must raise out_of_scope."""
        codebase_root = tmp_path / "my_codebase"
        codebase_root.mkdir()
        ctx = _make_run_context(str(codebase_root))

        # Path exists but is outside codebase root
        outside_file = tmp_path / "outside.md"
        outside_file.write_text("should not be readable")

        patch = _build_patch(
            f"*** Update File: {outside_file}",
            "@@",
            "-should not be readable",
            "+hacked",
        )
        with pytest.raises(ModelRetry, match="out_of_scope"):
            await updater_apply_patch(ctx, patch)

    @pytest.mark.asyncio
    async def test_path_traversal_via_dotdot_rejected(self, tmp_path: Path) -> None:
        """Path traversal via .. segments must be caught after resolve()."""
        codebase_root = tmp_path / "my_codebase"
        codebase_root.mkdir()
        ctx = _make_run_context(str(codebase_root))

        # Construct a path that uses .. to escape
        traversal_path = str(codebase_root / ".." / "outside.md")

        patch = _build_patch(
            f"*** Add File: {traversal_path}",
            "+malicious content",
        )
        with pytest.raises(ModelRetry, match="out_of_scope"):
            await updater_apply_patch(ctx, patch)

    @pytest.mark.asyncio
    async def test_read_outside_codebase_root_rejected(self, tmp_path: Path) -> None:
        """updater_read_file must reject paths outside codebase root."""
        codebase_root = tmp_path / "my_codebase"
        codebase_root.mkdir()
        ctx = _make_run_context(str(codebase_root))

        outside_file = tmp_path / "secret.md"
        outside_file.write_text("secret data")

        with pytest.raises(ModelRetry, match="out_of_scope"):
            await updater_read_file(ctx, str(outside_file))

    @pytest.mark.asyncio
    async def test_edit_outside_codebase_root_rejected(self, tmp_path: Path) -> None:
        """updater_edit_file must reject paths outside codebase root."""
        codebase_root = tmp_path / "my_codebase"
        codebase_root.mkdir()
        ctx = _make_run_context(str(codebase_root))

        outside_file = tmp_path / "target.md"
        outside_file.write_text("original")

        with pytest.raises(ModelRetry, match="out_of_scope"):
            await updater_edit_file(ctx, str(outside_file), "original", "hacked")

    @pytest.mark.asyncio
    async def test_valid_path_within_root_succeeds(self, tmp_path: Path) -> None:
        """Absolute path within codebase root must succeed (positive control)."""
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("# Title\nold line\n")
        ctx = _make_run_context(str(tmp_path))

        patch = _build_patch(
            f"*** Update File: {agents_md}",
            "@@",
            "-old line",
            "+new line",
        )
        result = await updater_apply_patch(ctx, patch)
        assert result["status"] == "applied"
        assert agents_md.read_text() == "# Title\nnew line\n"


class TestUpdaterReadFileLimits:
    """Validate read bound handling for updater_read_file."""

    @pytest.mark.asyncio
    async def test_limit_above_max_is_clamped(self, tmp_path: Path) -> None:
        """Oversized limit must clamp to READ_MAX_LIMIT instead of failing."""
        target = tmp_path / "AGENTS.md"
        target.write_text("\n".join(f"line-{index}" for index in range(1, 2105)) + "\n")
        ctx = _make_run_context(str(tmp_path))

        result = await updater_read_file(ctx, str(target), offset=0, limit=4000)
        numbered_lines = [
            line for line in result.splitlines() if len(line) > 7 and line[5:7] == "| "
        ]

        assert len(numbered_lines) == READ_MAX_LIMIT
        assert "[truncated]" in result

    @pytest.mark.asyncio
    async def test_limit_below_one_still_rejected(self, tmp_path: Path) -> None:
        """Limit less than one must still fail with invalid_patch."""
        target = tmp_path / "AGENTS.md"
        target.write_text("content\n")
        ctx = _make_run_context(str(tmp_path))

        with pytest.raises(ModelRetry, match="limit must be >= 1"):
            await updater_read_file(ctx, str(target), limit=0)


class TestUpdaterApplyPatchNoopSemantics:
    """Ensure no-op updates do not write or count as changed files."""

    @pytest.mark.asyncio
    async def test_update_noop_does_not_count_as_change(self, tmp_path: Path) -> None:
        """Update patch yielding identical content should be treated as no-op."""
        target = tmp_path / "AGENTS.md"
        target.write_text("line one\nline two\n")
        ctx = _make_run_context(str(tmp_path))

        patch = _build_patch(
            f"*** Update File: {target}",
            "@@",
            "-line two",
            "+line two",
        )

        result = await updater_apply_patch(ctx, patch)

        assert result["operations"] == 1
        assert result["changed_files"] == 0
        assert result["skipped_noop_files"] == 1
        assert target.read_text() == "line one\nline two\n"

    @pytest.mark.asyncio
    async def test_mixed_operations_track_requested_vs_actual_changes(
        self, tmp_path: Path
    ) -> None:
        """Operations count should include no-op intents; changed_files should not."""
        update_target = tmp_path / "AGENTS.md"
        update_target.write_text("alpha\nbeta\n")

        noop_target = tmp_path / "README.md"
        noop_target.write_text("same\n")

        add_target = tmp_path / "business_logic_references.md"
        ctx = _make_run_context(str(tmp_path))

        patch = _build_patch(
            f"*** Update File: {update_target}",
            "@@",
            "-beta",
            "+BETA",
            f"*** Update File: {noop_target}",
            "@@",
            "-same",
            "+same",
            f"*** Add File: {add_target}",
            "+# Business Logic",
            "+artifact content",
        )

        result = await updater_apply_patch(ctx, patch)

        assert result["operations"] == 3
        assert result["changed_files"] == 2
        assert result["skipped_noop_files"] == 1
        assert update_target.read_text() == "alpha\nBETA\n"
        assert noop_target.read_text() == "same\n"
        assert add_target.read_text() == "# Business Logic\nartifact content"
