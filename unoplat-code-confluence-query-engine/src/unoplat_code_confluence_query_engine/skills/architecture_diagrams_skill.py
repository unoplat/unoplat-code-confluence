"""Mermaid Architecture Diagram skill factory using isolated discovery."""

from pathlib import Path

from pydantic_ai_skills import SkillsToolset

ARCHITECTURE_DIAGRAMS_SKILLS_DIR = Path(__file__).parent / "architecture-diagrams"

# Guidance skill with one packaged visual-review reference under
# architecture-diagrams/references/. Script execution stays disabled; repository
# I/O and Mermaid CLI remain on the separate local console tools.
_ARCHITECTURE_SKILL_INSTRUCTION_TEMPLATE = """\
You have access to one guidance skill for Mermaid architecture-beta diagrams.

<available_skills>
{skills_list}
</available_skills>

When authoring or reviewing architecture.md:
1. Use `load_skill` with skill_name `architecture-diagrams` to read the full
   diagram guidance before drafting and again during final review.
2. Follow the skill's instructions, including its required visual reference and
   inspection of the validation PNG.
3. Follow that guidance when writing Mermaid architecture-beta syntax.
4. Do NOT call skill script tools for this skill. Repository file reads/writes
   and Mermaid CLI execution use the separate local console tools (`read_file`,
   `write_file`, `edit_file`, `execute`, and related inspection tools), not
   skill scripts.
"""


def create_architecture_diagrams_toolset(toolset_id: str) -> SkillsToolset:
    """Create a toolset that discovers only the architecture-diagrams skill."""
    return SkillsToolset(
        directories=[str(ARCHITECTURE_DIAGRAMS_SKILLS_DIR)],
        id=toolset_id,
        instruction_template=_ARCHITECTURE_SKILL_INSTRUCTION_TEMPLATE,
        exclude_tools=[
            "list_skills",
            "run_skill_script",
        ],
    )
