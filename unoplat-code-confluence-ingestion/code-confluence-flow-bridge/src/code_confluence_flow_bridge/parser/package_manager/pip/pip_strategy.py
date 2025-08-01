# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatPackageManagerMetadata,
    UnoplatProjectDependency,
    UnoplatVersion,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    PackageManagerType,
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import (
    PackageManagerStrategy,
)
from src.code_confluence_flow_bridge.parser.package_manager.utils.setup_parser import (
    SetupParser,
)

from pathlib import Path
from typing import Dict, List, Optional

# Third Party
from loguru import logger
from packaging.requirements import Requirement


class PipStrategy(PackageManagerStrategy):
    # Standard requirement file patterns
    REQUIREMENT_PATTERNS: List[str] = [
        "requirements.txt",  # Base requirements
        "requirements-*.txt",  # Environment-specific requirements
    ]

    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Process pip specific metadata from setup.py and requirements files."""
        try:
            # Create initial metadata
            package_manager_value = metadata.package_manager.value if metadata.package_manager else "unknown"
            package_metadata = UnoplatPackageManagerMetadata(dependencies={}, programming_language=metadata.language.value, package_manager=package_manager_value, programming_language_version=metadata.language_version)

            workspace = Path(local_workspace_path)

            # First parse setup.py for core metadata and dependencies
            try:
                package_metadata = SetupParser.parse_setup_file(str(workspace), package_metadata)
            except FileNotFoundError:
                logger.warning("setup.py not found")
            except Exception as e:
                logger.error("Error parsing setup.py: {}", str(e))

            # Then parse requirements files for additional dependencies
            requirement_files = self._find_requirement_files(workspace)
            if requirement_files:
                requirements = self._parse_all_requirements(str(workspace))
                # Merge with existing dependencies
                for name, req in requirements.items():
                    if name in package_metadata.dependencies:
                        # Update existing dependency
                        existing = package_metadata.dependencies[name]
                        if req.version:
                            existing.version = req.version
                        if req.extras:
                            existing.extras = req.extras
                        if req.environment_marker:
                            existing.environment_marker = req.environment_marker
                        if req.source:
                            existing.source = req.source
                            existing.source_url = req.source_url
                            existing.source_reference = req.source_reference
                            existing.subdirectory = req.subdirectory
                    else:
                        package_metadata.dependencies[name] = req

            return package_metadata

        except Exception as e:
            logger.error("Error processing pip metadata: {}", str(e))
            return self._create_empty_metadata(metadata)

    def _parse_all_requirements(self, workspace_path: str) -> Dict[str, UnoplatProjectDependency]:
        """Parse all requirement files in the workspace."""
        all_dependencies: Dict[str, UnoplatProjectDependency] = {}
        workspace = Path(workspace_path)

        requirement_files = self._find_requirement_files(workspace)
        for req_file in requirement_files:
            try:
                file_deps = self._parse_requirement_file(req_file)
                all_dependencies.update(file_deps)
            except Exception as e:
                logger.warning("Error parsing {}: {}", req_file, str(e))

        return all_dependencies

    def _parse_requirement_file(self, file_path: Path) -> Dict[str, UnoplatProjectDependency]:
        """Parse a single requirement file."""
        dependencies: Dict[str, UnoplatProjectDependency] = {}

        try:
            # Determine group from filename
            group = None
            if "requirements-" in file_path.name:
                group = file_path.name.replace("requirements-", "").replace(".txt", "")

            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if line.startswith("-e") or line.startswith("-r"):
                        continue  # Skip editable installs and requirements includes

                    try:
                        # Check for VCS URLs first
                        if any(line.startswith(f"{vcs}+") for vcs in ("git", "hg", "svn", "bzr")):
                            vcs_result = self._parse_vcs_line(line)
                            if vcs_result:
                                name, dep = vcs_result
                                if group:
                                    dep.group = group
                                dependencies[name] = dep
                            continue

                        # Handle regular requirements
                        req = Requirement(line)

                        # Create appropriate dependency
                        if req.url:
                            dep = self._create_url_dependency(req)
                        else:
                            dep = self._create_version_dependency(req)

                        # Add environment marker if present
                        if req.marker:
                            dep.environment_marker = str(req.marker)

                        # Add group if from a group-specific file
                        if group:
                            dep.group = group

                        dependencies[req.name] = dep

                    except Exception as e:
                        logger.warning(f"Error parsing requirement '{line}': {str(e)}")

        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")

        return dependencies

    def _parse_vcs_line(self, line: str) -> Optional[tuple[str, UnoplatProjectDependency]]:
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

        return UnoplatProjectDependency(version=UnoplatVersion(specifier=specifier), source=source, source_url=source_url, source_reference=source_reference, extras=list(req.extras) if req.extras else None, environment_marker=str(req.marker) if req.marker else None, subdirectory=subdirectory)

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
        version = UnoplatVersion(specifier=str(req.specifier) if req.specifier else None)

        return UnoplatProjectDependency(version=version, extras=list(req.extras) if req.extras else None)

    def _create_empty_metadata(self, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with basic information."""
        return UnoplatPackageManagerMetadata(dependencies={}, programming_language=metadata.language.value, package_manager=metadata.package_manager.value if metadata.package_manager else PackageManagerType.PIP.value, programming_language_version=metadata.language_version)

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
