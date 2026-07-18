"""TypeScript monorepo Agent Skill factory using directory-based discovery."""

from pathlib import Path

from pydantic_ai_skills import SkillsToolset

TYPESCRIPT_MONOREPO_SKILLS_DIR = Path(__file__).parent / "typescript-monorepo"


def create_typescript_monorepo_toolset(toolset_id: str) -> SkillsToolset:
    """Create a toolset that discovers only the typescript-monorepo skill."""
    return SkillsToolset(
        directories=[str(TYPESCRIPT_MONOREPO_SKILLS_DIR)],
        id=toolset_id,
    )
