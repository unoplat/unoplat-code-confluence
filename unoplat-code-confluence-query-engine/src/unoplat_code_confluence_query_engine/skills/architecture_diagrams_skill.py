"""D2 architecture-diagram skill factory using isolated discovery."""

from pathlib import Path

from pydantic_ai_skills import SkillsToolset

ARCHITECTURE_DIAGRAMS_SKILLS_DIR = Path(__file__).parent / "architecture-diagrams"

# Guidance and URL-only icon catalogs are loaded on demand. Skill script
# execution stays disabled; the validator owns D2/ELK rendering.
_ARCHITECTURE_SKILL_INSTRUCTION_TEMPLATE = """\
You have access to one guidance skill for D2 architecture diagrams.

<available_skills>
{skills_list}
</available_skills>

Runtime artifact ownership and tools are defined by the agent instructions.
For authoring and visual review:
1. Use `load_skill` with skill_name `architecture-diagrams` before drafting and
   again at final review; follow the loaded skill.
2. Before using a hosted icon, call `read_skill_resource` with skill_name
   `architecture-diagrams` and an exact resource name listed by `load_skill`
   (icon catalogs or `icons/README.md`).
3. Do not call skill script tools.
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
