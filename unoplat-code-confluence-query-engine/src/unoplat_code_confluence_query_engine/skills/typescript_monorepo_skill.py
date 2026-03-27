"""TypeScript monorepo Agent Skill factory using directory-based discovery."""

from pathlib import Path

from pydantic_ai_skills import SkillsToolset

SKILLS_DIR = Path(__file__).parent


def create_typescript_monorepo_toolset(toolset_id: str) -> SkillsToolset:
    """Create a SkillsToolset by discovering the typescript-monorepo SKILL.md."""
    return SkillsToolset(
        directories=[str(SKILLS_DIR)],
        id=toolset_id,
    )
