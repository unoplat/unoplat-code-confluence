# Standard Library
from pathlib import Path
import traceback
from typing import Any, Dict, List, Optional, Union

# Third Party
from loguru import logger
import yaml

# Load rules from YAML file
try:
    RULES: Dict[str, List[Dict[str, Any]]] = yaml.safe_load(
        (Path(__file__).parent / "rules.yaml").read_text()
    )
except Exception as e:
    logger.error(f"Failed to load package manager detection rules: {str(e)}")
    RULES = {}

def _matches(repo: Path, sig: Union[Dict[str, Any], str]) -> bool:
    """Return True as soon as one signature matches."""
    try:
        paths: List[Path] = []
        if isinstance(sig, str):  # Handle simple string case
            paths.append(repo / sig)
        else:  # Handle dictionary case
            if name := sig.get("file"):
                paths.append(repo / name)
            if pattern := sig.get("glob"):
                paths.extend(repo.glob(pattern))

        for p in paths:
            if not p.exists():
                continue
            if isinstance(sig, dict) and "contains" in sig:
                try:
                    if sig["contains"] not in p.read_text(errors="ignore"):
                        continue
                except Exception:
                    continue
            return True
        return False
    except Exception as e:
        logger.error(f"Error in signature matching: {str(e)}")
        return False

def detect_manager(repo: Path, language: str = "python") -> Optional[str]:
    """Return the first matching manager name, or None."""
    try:
        logger.debug(f"Detecting package manager for {repo} with language {language}")
        
        for rule in RULES.get(language, []):
            if any(_matches(repo, sig) for sig in rule["signatures"]):
                detected = rule["manager"]
                logger.info(f"Detected package manager: {detected} for {repo}")
                return detected
        
        logger.warning(f"No package manager detected for {repo} with language {language}")
        return None
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"Error detecting package manager: {str(e)} | traceback={tb_str}")
        return None
