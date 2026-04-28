"""Ad-hoc script: dump db_get_data_model_files output for unoplat-code-confluence-commons.

Run from `unoplat-code-confluence-query-engine/`:
    uv run python scripts/dump_commons_data_model_files.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_business_logic_repository import (
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.postgres.db import (
    init_db_connections,
    dispose_db_connections,
)

CODEBASE_PATH: str = (
    "/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons"
)
OUTPUT_PATH: Path = Path(__file__).parent / "commons_data_model_files.json"


async def main() -> None:
    settings = EnvironmentSettings()
    await init_db_connections(settings)
    try:
        result = await db_get_data_model_files(CODEBASE_PATH)
    finally:
        await dispose_db_connections()

    payload: dict[str, object] = {
        "codebase_path": CODEBASE_PATH,
        "file_count": len(result),
        "files": result,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Wrote {len(result)} files to {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
