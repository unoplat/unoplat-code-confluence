"""Mermaid Architecture Diagram skill factory using isolated discovery."""

from pathlib import Path

from pydantic_ai_skills import SkillsToolset

ARCHITECTURE_DIAGRAMS_SKILLS_DIR = Path(__file__).parent / "architecture-diagrams"

# Guidance-only skill: no packaged resources/scripts exist under
# architecture-diagrams/. Excluding the unused skill tools prevents the model
# from mistaking console operations (especially write_file) for skill scripts.
_ARCHITECTURE_SKILL_INSTRUCTION_TEMPLATE = """\
You have access to one guidance skill for Mermaid architecture-beta diagrams.

<available_skills>
{skills_list}
</available_skills>

When authoring or reviewing architecture.md:
1. Use `load_skill` with skill_name `architecture-diagrams` to read the full
   diagram guidance before drafting and again during final review.
2. Follow that guidance when writing Mermaid architecture-beta syntax.
3. Do NOT call skill resource or skill script tools for this skill. Repository
   file reads/writes and Mermaid CLI execution use the separate local console
   tools (`read_file`, `write_file`, `edit_file`, `execute`, and related
   inspection tools), not skill scripts.
"""


def create_architecture_diagrams_toolset(toolset_id: str) -> SkillsToolset:
    """Create a toolset that discovers only the architecture-diagrams skill."""
    return SkillsToolset(
        directories=[str(ARCHITECTURE_DIAGRAMS_SKILLS_DIR)],
        id=toolset_id,
        instruction_template=_ARCHITECTURE_SKILL_INSTRUCTION_TEMPLATE,
        exclude_tools=[
            "list_skills",
            "read_skill_resource",
            "run_skill_script",
        ],
    )
