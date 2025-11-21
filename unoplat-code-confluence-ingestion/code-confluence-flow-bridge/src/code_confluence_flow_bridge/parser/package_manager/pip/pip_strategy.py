# Standard Library
# First Party
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set

# Third Party
from loguru import logger
from packaging.requirements import Requirement
from unoplat_code_confluence_commons.base_models import (
    PackageManagerType,
    ProgrammingLanguageMetadata,
)

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatPackageManagerMetadata,
    UnoplatProjectDependency,
    UnoplatVersion,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import (
    PackageManagerStrategy,
)
from src.code_confluence_flow_bridge.parser.package_manager.utils.setup_parser import (
    SetupParser,
)


class PipStrategy(PackageManagerStrategy):
    # Extended requirement file patterns
    REQUIREMENT_PATTERNS: List[str] = [
        "requirements.txt",  # Base/default requirements
        "requirements-*.txt",  # Environment-specific (dev, test, prod, etc.)
        "requirements/*.txt",  # Organized by subdirectory
        "requirements/*/requirements.txt",  # Nested organization
    ]

    # Standard group name mappings
    GROUP_NAME_MAPPINGS: Dict[str, str] = {
        "requirements.txt": "default",
        "requirements-dev.txt": "dev",
        "requirements-test.txt": "test",
        "requirements-docs.txt": "docs",
        "requirements-prod.txt": "prod",
        "requirements-production.txt": "prod",
    }

    def process_metadata(
        self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Process pip metadata from setup.py and requirements files.

        Follows PEP 621 (pyproject.toml), PEP 735 (dependency-groups),
        and pip requirements file format specification.

        Args:
            local_workspace_path: Path to Python project root
            metadata: Programming language metadata

        Returns:
            Package metadata with grouped dependencies structure
        """
        try:
            package_manager_value = (
                metadata.package_manager.value
                if metadata.package_manager
                else "unknown"
            )

            # Initialize with grouped structure
            package_metadata = UnoplatPackageManagerMetadata(
                dependencies={"default": {}},  # Seed default bucket
                programming_language=metadata.language.value,
                package_manager=package_manager_value,
                programming_language_version=metadata.language_version,
                manifest_path=metadata.manifest_path,
            )

            workspace = Path(local_workspace_path)

            # Step 1: Parse setup.py for core metadata and dependencies
            # SetupParser already handles grouped structure (install_requires → default, extras_require → groups)
            try:
                package_metadata = SetupParser.parse_setup_file(
                    str(workspace), package_metadata
                )
            except FileNotFoundError:
                logger.warning("setup.py not found")
            except Exception as e:
                logger.error("Error parsing setup.py: {}", str(e))

            # Step 2: Parse requirements files and merge with setup.py dependencies
            requirement_files = self._find_requirement_files(workspace)

            if requirement_files:
                for req_file in requirement_files:
                    try:
                        # Parse file with includes
                        parsed_lines = self._parse_requirement_file_recursive(req_file)

                        # Add requirements to appropriate group
                        for parsed in parsed_lines:
                            # Determine group from source file (tracks through includes)
                            source_file = parsed.get("source_file", req_file)
                            group_name = self._determine_group_from_path(
                                source_file, workspace
                            )

                            if parsed["type"] == "requirement" and parsed.get(
                                "requirement"
                            ):
                                self._add_dependency_to_group(
                                    package_metadata.dependencies,
                                    group_name,
                                    parsed["requirement"],
                                    is_editable=False,
                                )
                            elif parsed["type"] == "editable":
                                if parsed.get("vcs_info"):
                                    # Handle VCS editable install
                                    name, dep = parsed["vcs_info"]
                                    bucket = self._ensure_group(
                                        package_metadata.dependencies, group_name
                                    )
                                    normalized_pkg = self._normalize_package_name(name)
                                    bucket[normalized_pkg] = dep
                                elif parsed.get("requirement"):
                                    self._add_dependency_to_group(
                                        package_metadata.dependencies,
                                        group_name,
                                        parsed["requirement"],
                                        is_editable=True,
                                    )
                            elif parsed["type"] == "vcs":
                                # Handle VCS dependency
                                name = parsed["name"]
                                dep = parsed["dependency"]
                                bucket = self._ensure_group(
                                    package_metadata.dependencies, group_name
                                )
                                normalized_pkg = self._normalize_package_name(name)
                                bucket[normalized_pkg] = dep

                    except ValueError:
                        # Re-raise ValueError for circular includes
                        raise
                    except Exception as e:
                        logger.warning("Error parsing {}: {}", req_file, str(e))

            return package_metadata

        except ValueError:
            # Re-raise ValueError for circular includes
            raise
        except Exception as e:
            logger.error("Error processing pip metadata: {}", str(e))
            return self._create_empty_metadata(metadata)

    def _parse_vcs_line(
        self, line: str
    ) -> Optional[tuple[str, UnoplatProjectDependency]]:
        """
        Parse a VCS URL line into a tuple of (package_name, dependency_object).

        Returns:
            Optional[tuple[str, UnoplatProjectDependency]]: Tuple of (name, dependency) or None if parsing fails
        """
        try:
            # Extract package name from egg= parameter
            if "#egg=" not in line:
                return None

            url, egg_part = line.split("#", 1)
            params = dict(p.split("=") for p in egg_part.split("&"))
            name = params.get("egg")
            if not name:
                return None

            # Extract VCS type and URL
            vcs_type, repo_url = url.split("+", 1)

            # Extract reference if present (@branch, @tag, @commit)
            reference = None
            if "@" in repo_url:
                repo_url, reference = repo_url.rsplit("@", 1)

            dependency = UnoplatProjectDependency(
                version=UnoplatVersion(),  # VCS deps don't have version constraints
                source=vcs_type,
                source_url=repo_url,
                source_reference=reference,
                subdirectory=params.get("subdirectory"),
            )
            return name, dependency
        except Exception as e:
            logger.warning(f"Error parsing VCS line '{line}': {str(e)}")
            return None

    def _create_url_dependency(self, req: Requirement) -> UnoplatProjectDependency:
        """
        Create a UnoplatProjectDependency for a URL-based requirement (including VCS).

        Args:
            req: Package requirement with URL

        Returns:
            UnoplatProjectDependency with source, URL and version information

        Example:
            "flask @ git+https://github.com/pallets/flask.git@2.0.0"
            -> source="git", source_url="https://github.com/pallets/flask.git",
               source_reference="2.0.0", specifier="==2.0.0"
        """
        source = "url"
        source_url = str(req.url)
        source_reference = None
        subdirectory = None
        specifier = None  # Initialize specifier

        # Check for VCS prefixes (git+, hg+, etc.)
        for vcs in ("git", "hg", "svn", "bzr"):
            prefix = vcs + "+"
            if source_url.startswith(prefix):
                source = vcs
                source_url = source_url[len(prefix) :]  # remove "git+" etc.
                break

        # If there's an @, assume it indicates a branch/tag/commit
        if "@" in source_url:
            source_url, source_reference = source_url.rsplit("@", 1)
            # If it looks like a version number, set it as specifier
            if source_reference and any(c.isdigit() for c in source_reference):
                specifier = f"=={source_reference}"

        # Only update version from req.specifier if we haven't set it from reference
        if req.specifier and not specifier:
            specifier = str(req.specifier)

        return UnoplatProjectDependency(
            version=UnoplatVersion(specifier=specifier),
            source=source,
            source_url=source_url,
            source_reference=source_reference,
            extras=list(req.extras) if req.extras else None,
            environment_marker=str(req.marker) if req.marker else None,
            subdirectory=subdirectory,
        )

    def _create_version_dependency(self, req: Requirement) -> UnoplatProjectDependency:
        """Create dependency object for version-based requirements.

        Args:
            req: Package requirement with version specifiers

        Returns:
            UnoplatProjectDependency with version specifier as-is

        Example:
            req: "requests>=2.0.0"
            -> version.specifier=">=2.0.0"
            req: "black==22.3.0"
            -> version.specifier="==22.3.0"
        """
        version = UnoplatVersion(
            specifier=str(req.specifier) if req.specifier else None
        )

        return UnoplatProjectDependency(
            version=version, extras=list(req.extras) if req.extras else None
        )

    def _create_empty_metadata(
        self, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with default group initialized.

        Matches poetry_strategy.py:184 and uv_strategy.py:65-69
        """
        return UnoplatPackageManagerMetadata(
            dependencies={"default": {}},  # Initialize default bucket
            programming_language=metadata.language.value,
            package_manager=metadata.package_manager.value
            if metadata.package_manager
            else PackageManagerType.PIP.value,
            programming_language_version=metadata.language_version,
            manifest_path=metadata.manifest_path,
        )

    def _find_requirement_files(self, workspace: Path) -> List[Path]:
        """Find all requirement files in the workspace, matching any of the REQUIREMENT_PATTERNS."""
        requirement_files: List[Path] = []
        for pattern in self.REQUIREMENT_PATTERNS:
            if "*" in pattern:
                requirement_files.extend(workspace.glob(pattern))
            else:
                candidate = workspace / pattern
                if candidate.exists():
                    requirement_files.append(candidate)
        return requirement_files

    def _ensure_group(
        self,
        dependencies: Dict[str, Dict[str, UnoplatProjectDependency]],
        group_name: str,
    ) -> Dict[str, UnoplatProjectDependency]:
        """Get or create dependency bucket for a group.

        Args:
            dependencies: The grouped dependencies structure
            group_name: Name of the group (normalized per PEP 735)

        Returns:
            The dependency dict for this group
        """
        # Normalize group name per PEP 735 (same as PEP 503)
        normalized_name = re.sub(r"[-_.]+", "-", group_name).lower()
        return dependencies.setdefault(normalized_name, {})

    def _normalize_package_name(self, package_name: str) -> str:
        """Normalize package name per PEP 503.

        Args:
            package_name: Raw package name

        Returns:
            Normalized package name (runs of [-_.] collapsed to single -)
        """
        return re.sub(r"[-_.]+", "-", package_name).lower()

    def _parse_requirement_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single requirements file line.

        Returns dict with:
        - 'type': 'requirement' | 'include' | 'editable' | 'skip'
        - 'requirement': Requirement object (if type='requirement' or 'editable')
        - 'path': str (if type='include' or 'editable')

        Args:
            line: Raw line from requirements file

        Returns:
            Parsed line data or None if should skip
        """
        line = line.strip()

        # Skip comments and blank lines
        if not line or line.startswith("#"):
            return None

        # Remove inline comments (but preserve # in URLs)
        if "#" in line:
            parts = line.split()
            cleaned_parts = []
            for part in parts:
                if part.startswith("#") and "://" not in part:
                    break  # Rest is comment
                cleaned_parts.append(part)
            line = " ".join(cleaned_parts).strip()

        if not line:
            return None

        # Check for -r/--requirement includes
        if line.startswith("-r ") or line.startswith("--requirement "):
            include_path = line.split(None, 1)[1] if " " in line else None
            return {"type": "include", "path": include_path}

        # Check for -e/--editable
        if line.startswith("-e ") or line.startswith("--editable "):
            editable_path = line.split(None, 1)[1] if " " in line else None

            # Try to parse as requirement (for VCS URLs with #egg=)
            req = None
            if editable_path:
                # Handle VCS URLs (git+, hg+, etc.)
                if any(
                    editable_path.startswith(f"{vcs}+")
                    for vcs in ("git", "hg", "svn", "bzr")
                ):
                    vcs_result = self._parse_vcs_line(editable_path)
                    if vcs_result:
                        name, dep = vcs_result
                        # Create a simple Requirement-like object for consistency
                        # We'll handle this in _add_dependency_to_group
                        return {
                            "type": "editable",
                            "requirement": None,
                            "path": editable_path,
                            "vcs_info": (name, dep),
                        }

            return {"type": "editable", "requirement": req, "path": editable_path}

        # Check for VCS URLs (not editable)
        if any(line.startswith(f"{vcs}+") for vcs in ("git", "hg", "svn", "bzr")):
            vcs_result = self._parse_vcs_line(line)
            if vcs_result:
                name, dep = vcs_result
                return {"type": "vcs", "name": name, "dependency": dep}

        # Parse as standard PEP 508 requirement
        try:
            req = Requirement(line)
            return {"type": "requirement", "requirement": req}
        except Exception as e:
            logger.warning(f"Failed to parse requirement line '{line}': {e}")
            return None

    def _parse_requirement_file_recursive(
        self, file_path: Path, visited: Optional[Set[Path]] = None
    ) -> List[Dict[str, Any]]:
        """Parse requirements file recursively, following -r includes.

        Args:
            file_path: Path to requirements file
            visited: Set of already-visited files (for cycle detection)

        Returns:
            List of parsed requirement data dicts

        Raises:
            ValueError: If circular include detected
        """
        if visited is None:
            visited = set()

        # Resolve to absolute path for cycle detection
        abs_path = file_path.resolve()

        # Cycle detection
        if abs_path in visited:
            raise ValueError(f"Circular requirement include detected: {abs_path}")

        visited.add(abs_path)

        all_requirements: List[Dict[str, Any]] = []

        if not abs_path.exists():
            logger.warning(f"Requirements file not found: {abs_path}")
            return all_requirements

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Handle line continuations (backslash)
            combined_lines = []
            current_line = ""
            for line in lines:
                stripped = line.rstrip()
                if stripped.endswith("\\"):
                    current_line += stripped[:-1] + " "
                else:
                    current_line += line
                    combined_lines.append(current_line)
                    current_line = ""

            for line in combined_lines:
                parsed = self._parse_requirement_line(line)

                if parsed is None:
                    continue

                if parsed["type"] == "include" and parsed["path"]:
                    # Recursively parse included file
                    include_full_path = (abs_path.parent / parsed["path"]).resolve()
                    try:
                        included_reqs = self._parse_requirement_file_recursive(
                            include_full_path,
                            visited.copy(),  # Use copy to allow sibling includes
                        )
                        all_requirements.extend(included_reqs)
                    except ValueError:
                        # Re-raise ValueError for circular includes
                        raise
                else:
                    # Track source file for group determination
                    parsed["source_file"] = abs_path
                    all_requirements.append(parsed)

        except ValueError:
            # Re-raise ValueError for circular includes
            raise
        except Exception as e:
            logger.error(f"Error parsing requirements file {abs_path}: {e}")

        return all_requirements

    def _determine_group_from_path(self, req_file: Path, workspace: Path) -> str:
        """Determine dependency group from requirements file path.

        Mapping rules:
        - requirements.txt → default
        - requirements-{name}.txt → {name}
        - requirements/{name}.txt → {name}
        - requirements/{name}/requirements.txt → {name}

        Args:
            req_file: Path to requirements file
            workspace: Project workspace root

        Returns:
            Group name (normalized)
        """
        # Check exact mappings first
        file_name = req_file.name
        if file_name in self.GROUP_NAME_MAPPINGS:
            return self.GROUP_NAME_MAPPINGS[file_name]

        # Extract from requirements-{name}.txt pattern
        if file_name.startswith("requirements-") and file_name.endswith(".txt"):
            group_name = file_name.replace("requirements-", "").replace(".txt", "")
            return group_name

        # Extract from requirements/{name}.txt or requirements/{name}/requirements.txt
        try:
            relative_path = req_file.relative_to(workspace)
            parts = relative_path.parts

            if len(parts) >= 2 and parts[0] == "requirements":
                # requirements/{name}.txt or requirements/{name}/requirements.txt
                if parts[1].endswith(".txt"):
                    group_name = parts[1].replace(".txt", "")
                else:
                    group_name = parts[1]
                return group_name
        except ValueError:
            pass

        # Fallback to default
        return "default"

    def _add_dependency_to_group(
        self,
        dependencies: Dict[str, Dict[str, UnoplatProjectDependency]],
        group_name: str,
        requirement: Requirement,
        is_editable: bool = False,
    ) -> None:
        """Add a requirement to the appropriate dependency group.

        Args:
            dependencies: Grouped dependencies structure
            group_name: Target group name
            requirement: Parsed requirement object
            is_editable: Whether this is an editable install
        """
        # Get or create group bucket
        bucket = self._ensure_group(dependencies, group_name)

        # Normalize package name
        normalized_pkg = self._normalize_package_name(requirement.name)

        # Create dependency object
        if requirement.url:
            dep = self._create_url_dependency(requirement)
        else:
            dep = self._create_version_dependency(requirement)

        # Add environment marker if present (PEP 508)
        if requirement.marker:
            dep.environment_marker = str(requirement.marker)

        # Log editable installs
        if is_editable:
            logger.debug(f"Editable install: {requirement.name}")

        # Add or merge into bucket
        if normalized_pkg not in bucket:
            bucket[normalized_pkg] = dep
        else:
            # Merge extras if package already exists in this group
            existing = bucket[normalized_pkg]
            if dep.extras:
                existing_extras = existing.extras or []
                existing.extras = list(set(existing_extras + dep.extras))

            # Update version/marker if new dependency has them
            if dep.version and dep.version.specifier:
                existing.version = dep.version
            if dep.environment_marker:
                existing.environment_marker = dep.environment_marker
