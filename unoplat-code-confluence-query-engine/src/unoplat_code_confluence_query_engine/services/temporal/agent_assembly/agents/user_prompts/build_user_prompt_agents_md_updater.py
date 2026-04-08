from __future__ import annotations

from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    SectionId,
)
from unoplat_code_confluence_query_engine.services.agents_md.managed_block import (
    MANAGED_BLOCK_BEGIN,
    MANAGED_BLOCK_END,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    APP_INTERFACES_ARTIFACT,
    BUSINESS_LOGIC_REFERENCES_ARTIFACT,
    DEPENDENCY_OVERVIEW_ARTIFACT,
)

SECTION_UPDATER_AGENT_NAMES: dict[SectionId, str] = {
    SectionId.ENGINEERING_WORKFLOW: "development_workflow_agents_md_updater",
    SectionId.DEPENDENCY_GUIDE: "dependency_guide_agents_md_updater",
    SectionId.BUSINESS_DOMAIN: "business_domain_agents_md_updater",
    SectionId.APP_INTERFACES: "app_interfaces_agents_md_updater",
}

_SECTION_HEADINGS: dict[SectionId, str] = {
    SectionId.ENGINEERING_WORKFLOW: "## Engineering Workflow",
    SectionId.DEPENDENCY_GUIDE: "## Dependency Guide",
    SectionId.BUSINESS_DOMAIN: "## Business Logic Domain",
    SectionId.APP_INTERFACES: "## App Interfaces",
}

_SECTION_ARTIFACTS: dict[SectionId, list[str]] = {
    SectionId.ENGINEERING_WORKFLOW: ["AGENTS.md"],
    SectionId.DEPENDENCY_GUIDE: ["AGENTS.md", DEPENDENCY_OVERVIEW_ARTIFACT],
    SectionId.BUSINESS_DOMAIN: ["AGENTS.md", BUSINESS_LOGIC_REFERENCES_ARTIFACT],
    SectionId.APP_INTERFACES: ["AGENTS.md", APP_INTERFACES_ARTIFACT],
}

_SECTION_COMPANION_ARTIFACTS: dict[SectionId, str] = {
    SectionId.DEPENDENCY_GUIDE: DEPENDENCY_OVERVIEW_ARTIFACT,
    SectionId.BUSINESS_DOMAIN: BUSINESS_LOGIC_REFERENCES_ARTIFACT,
    SectionId.APP_INTERFACES: APP_INTERFACES_ARTIFACT,
}


def _build_section_extra_requirements(section_id: SectionId) -> str:
    requirements: list[str] = []
    companion_artifact = _SECTION_COMPANION_ARTIFACTS.get(section_id)

    if companion_artifact is not None:
        requirements.extend(
            [
                "- In `AGENTS.md`, write ONLY a concise description of "
                f"`{companion_artifact}` and a markdown link to it.",
                "- Keep the `AGENTS.md` section body to 1-2 short sentences total.",
                "- Do NOT include tables, bullet inventories, endpoint lists, file maps, "
                "dependency catalogs, or detailed prose in `AGENTS.md`.",
                f"- Write all detailed section content in `{companion_artifact}`.",
                f"- Treat `{companion_artifact}` as the source-of-truth artifact for this section.",
            ]
        )

    if section_id == SectionId.DEPENDENCY_GUIDE:
        requirements.append(
            f"- Put full dependency purpose/usage entries only in `{DEPENDENCY_OVERVIEW_ARTIFACT}`."
        )

    return "\n".join(requirements)


def build_agents_md_updater_instructions() -> str:
    return f"""You are the AGENTS.md section updater.

Goal:
- Create or update a SPECIFIC SECTION of codebase-local AGENTS.md using safe and minimal edits.
- Create/update companion artifact files when instructed ({DEPENDENCY_OVERVIEW_ARTIFACT}, {BUSINESS_LOGIC_REFERENCES_ARTIFACT}, {APP_INTERFACES_ARTIFACT}).

Managed block awareness:
- All generated sections live inside a managed block delimited by {MANAGED_BLOCK_BEGIN} and {MANAGED_BLOCK_END}.
- Your assigned section heading already exists inside the managed block. Update the content under it.
- NEVER modify the block markers.
- NEVER modify the <CRITICAL_INSTRUCTION> block — it contains freshness metadata managed separately.
- NEVER add commit SHA, branch name, or generation timestamps to your section content.
- Treat other ## headings inside the managed block as read-only.

Section scoping:
- You will be told which section heading you own (e.g., \"## Engineering Workflow\").
- Update content under your assigned heading.
- NEVER modify content outside your assigned section boundary.

Companion artifact policy:
- Some sections have a companion artifact file (for example `{DEPENDENCY_OVERVIEW_ARTIFACT}`, `{BUSINESS_LOGIC_REFERENCES_ARTIFACT}`, `{APP_INTERFACES_ARTIFACT}`).
- If your assigned section has a companion artifact, `AGENTS.md` is pointer-only.
- In `AGENTS.md`, write only a concise description of the companion artifact and a markdown link to it.
- Keep the `AGENTS.md` section body to 1-2 short sentences total.
- NEVER copy tables, bullet inventories, endpoint lists, file maps, dependency catalogs, or detailed summaries into `AGENTS.md`.
- Put detailed content in the companion artifact and treat that artifact as the source-of-truth.
- Sections without a companion artifact may store their section content directly in `AGENTS.md`.

Root-scope safety (hard invariant):
- ALL file operations MUST use absolute paths within the current codebase root.
- NEVER read, write, or reference files outside the codebase root directory.
- Relative paths are rejected. Paths escaping the root are rejected.
- This is enforced at the tool level — violations raise out_of_scope errors.

Tooling constraints:
- Use only updater_read_file, updater_edit_file, updater_apply_patch.
- Always pass absolute file paths.
- Operate only within the current codebase root.
- Prefer updater_apply_patch for creates and structured updates.
- Read the target section first, then compute the expected section body from section_data.
- Compare before write: if content is already equivalent, do not call write tools and return status=\"no_changes\".
- Call updater_apply_patch/updater_edit_file only when an actual diff exists.

Output constraints:
- Return summary metadata only.
- Do not include raw file content in the output.
- Include touched_file_paths for all files involved in final update decisions.
- Include file_changes with changed flag, change_type, concise change_summary, and optional content_sha256.
"""


def build_section_updater_prompt(
    section_id: SectionId,
    codebase_path: str,
    programming_language_metadata: dict[str, object],
    section_data: object,
) -> str:
    heading = _SECTION_HEADINGS[section_id]
    artifacts = _SECTION_ARTIFACTS[section_id]
    artifacts_instruction = "\n".join(f"- {artifact}" for artifact in artifacts)
    section_specific_requirements = _build_section_extra_requirements(section_id)
    section_specific_instruction = ""
    if section_specific_requirements:
        section_specific_instruction = (
            f"Section-specific requirements:\n{section_specific_requirements}\n\n"
        )

    return (
        f"Update the '{heading}' section in codebase-local AGENTS.md.\n"
        f"Modify only the content under '{heading}'.\n"
        "Do not change any other AGENTS.md section.\n\n"
        f"Expected managed files:\n{artifacts_instruction}\n\n"
        f"{section_specific_instruction}"
        f"Codebase path: {codebase_path}\n"
        f"Programming language metadata: {programming_language_metadata}\n"
        f"Section data:\n{section_data}\n\n"
        "Return summary metadata only (no raw file content)."
    )
