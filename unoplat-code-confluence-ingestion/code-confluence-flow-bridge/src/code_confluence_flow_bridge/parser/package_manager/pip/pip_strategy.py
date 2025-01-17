# Standard Library
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlsplit, parse_qs

# Third Party
from loguru import logger
from packaging.markers import Marker
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_version import UnoplatVersion

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import PackageManagerStrategy
from src.code_confluence_flow_bridge.parser.package_manager.utils.setup_parser import SetupParser


class PipStrategy(PackageManagerStrategy):
    # Common requirement file patterns with priority order
    REQUIREMENT_PATTERNS: List[str] = [
        "requirements.txt",           # Base requirements
        "requirements/*.txt",         # Modular requirements
        "requirements-*.txt",         # Environment-specific requirements
        "constraints.txt",            # Version constraints
        "constraints-*.txt"           # Environment-specific constraints
    ]

    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Process pip specific metadata from requirements files and setup.py."""
        try:
            # Parse all requirement files with constraints
            dependencies: Dict[str, UnoplatProjectDependency] = self._parse_all_requirements(local_workspace_path)
            
            # Create initial metadata with dependencies
            package_metadata: UnoplatPackageManagerMetadata = UnoplatPackageManagerMetadata(
                dependencies=dependencies,
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager,
                programming_language_version=metadata.language_version
            )
            
            try:
                # Parse setup.py for additional metadata and merge dependencies
                package_metadata = SetupParser.parse_setup_file(
                    local_workspace_path, 
                    package_metadata
                )
            except FileNotFoundError:
                logger.warning("setup.py not found, using only requirements data")
            except Exception as e:
                logger.error(f"Error parsing setup.py: {str(e)}")
                
            return package_metadata
            
        except Exception as e:
            logger.error(f"Error processing pip metadata: {str(e)}")
            return self._create_empty_metadata(metadata)

    def _parse_all_requirements(self, workspace_path: str) -> Dict[str, UnoplatProjectDependency]:
        """Parse all requirement files in the workspace with constraint merging."""
        all_dependencies: Dict[str, UnoplatProjectDependency] = {}
        constraints: Dict[str, Set[str]] = {}  # Package name to set of constraints
        workspace: Path = Path(workspace_path)

        # First pass: collect all constraints
        constraint_files: List[Path] = [
            f for f in self._find_requirement_files(workspace)
            if "constraints" in f.name
        ]
        for file in constraint_files:
            self._collect_constraints(file, constraints)

        # Second pass: parse requirements with constraints
        requirement_files: List[Path] = [
            f for f in self._find_requirement_files(workspace)
            if "constraints" not in f.name
        ]
        
        for req_file in requirement_files:
            try:
                file_deps: Dict[str, UnoplatProjectDependency] = self._parse_requirement_file(
                    req_file,
                    constraints
                )
                all_dependencies.update(file_deps)
            except Exception as e:
                logger.warning(f"Error parsing {req_file}: {str(e)}")

        return all_dependencies

    def _collect_constraints(self, file_path: Path, constraints: Dict[str, Set[str]]) -> None:
        """Collect version constraints from a constraints file."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        req: Requirement = Requirement(line)
                        if req.specifier:
                            constraints.setdefault(req.name, set()).add(str(req.specifier))
                    except Exception as e:
                        logger.warning(f"Error parsing constraint '{line}': {str(e)}")
        except Exception as e:
            logger.error(f"Error reading constraints file {file_path}: {str(e)}")

    def _parse_requirement_file(
        self, 
        file_path: Path, 
        constraints: Optional[Dict[str, Set[str]]] = None
    ) -> Dict[str, UnoplatProjectDependency]:
        """Parse a single requirement file with optional constraints."""
        dependencies: Dict[str, UnoplatProjectDependency] = {}
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        # Check for VCS URLs first
                        is_vcs = False
                        if any(line.startswith(f"{vcs}+") for vcs in ('git', 'hg', 'svn', 'bzr')):
                            vcs_type = line.split('+', 1)[0]
                            url = line.split('+', 1)[1]
                            
                            # Use urlsplit to properly parse URL components
                            parsed = urlsplit(url)
                            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                            
                            # Get reference from path if present
                            source_reference = None
                            if '@' in parsed.path:
                                base_url, source_reference = base_url.rsplit('@', 1)
                            
                            # Parse fragment for egg and other parameters
                            if parsed.fragment:
                                params = parse_qs(parsed.fragment)
                                if 'egg' in params:
                                    name = params['egg'][0]
                                    dep = UnoplatProjectDependency(
                                        version=UnoplatVersion(),
                                        source=vcs_type,
                                        source_url=base_url,
                                        source_reference=source_reference,
                                        subdirectory=params.get('subdirectory', [None])[0]
                                    )
                                    # Only add VCS dependency if no version constraint exists
                                    if name not in dependencies:
                                        dependencies[name] = dep
                                    is_vcs = True
                        
                        if is_vcs:
                            continue
                        
                        # Handle regular requirements
                        req = Requirement(line)
                        marker_str = str(req.marker) if req.marker else None
                        
                        # Create appropriate dependency
                        if req.url:
                            dep = self._create_url_dependency(req)
                        else:
                            dep = self._create_version_dependency(req, constraints)
                        
                        dep.environment_marker = marker_str
                        
                        # Preserve version constraints over URL/VCS dependencies
                        if req.name not in dependencies or not (req.url or is_vcs):
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
            if '#egg=' not in line:
                return None
            
            url, egg_part = line.split('#', 1)
            params = dict(p.split('=') for p in egg_part.split('&'))
            name = params.get('egg')
            if not name:
                return None
            
            # Extract VCS type and URL
            vcs_type, repo_url = url.split('+', 1)
            
            # Extract reference if present (@branch, @tag, @commit)
            reference = None
            if '@' in repo_url:
                repo_url, reference = repo_url.rsplit('@', 1)
            
            dependency = UnoplatProjectDependency(
                version=UnoplatVersion(),  # VCS deps don't have version constraints
                source=vcs_type,
                source_url=repo_url,
                source_reference=reference,
                subdirectory=params.get('subdirectory')
            )
            return name, dependency
        except Exception as e:
            logger.warning(f"Error parsing VCS line '{line}': {str(e)}")
            return None

    def _evaluate_marker(self, marker: Marker) -> bool:
        """Evaluate an environment marker."""
        try:
            return marker.evaluate()
        except Exception as e:
            logger.warning(f"Error evaluating marker {marker}: {str(e)}")
            return True  # Include by default if evaluation fails

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
               source_reference="2.0.0", version.current_version="==2.0.0"
        """
        source = "url"
        source_url = str(req.url)
        source_reference = None
        subdirectory = None
        version = UnoplatVersion()

        # Check for VCS prefixes (git+, hg+, etc.)
        for vcs in ("git", "hg", "svn", "bzr"):
            prefix = vcs + "+"
            if source_url.startswith(prefix):
                source = vcs
                source_url = source_url[len(prefix):]  # remove "git+" etc.
                break

        # If there's an @, assume it indicates a branch/tag/commit
        if "@" in source_url:
            source_url, source_reference = source_url.rsplit("@", 1)
            # If it looks like a version number, set it as current_version
            if source_reference and any(c.isdigit() for c in source_reference):
                version = UnoplatVersion(current_version=f"=={source_reference}")

        # Handle any version specifiers from the requirement
        if req.specifier:
            version = UnoplatVersion(
                current_version=str(req.specifier) if len(req.specifier) == 1 else None,
                minimum_version=next((str(s) for s in req.specifier if s.operator in (">=", ">")), None),
                maximum_version=next((str(s) for s in req.specifier if s.operator in ("<=", "<")), None)
            )

        return UnoplatProjectDependency(
            version=version,
            source=source,
            source_url=source_url,
            source_reference=source_reference,
            extras=list(req.extras) if req.extras else None,
            environment_marker=str(req.marker) if req.marker else None,
            subdirectory=subdirectory
        )

    def _create_version_dependency(
        self, 
        req: Requirement,
        constraints: Optional[Dict[str, Set[str]]] = None
    ) -> UnoplatProjectDependency:
        """Create dependency object for version-based requirements."""
        version: UnoplatVersion = UnoplatVersion()
        
        # Combine requirement specifier with constraints
        spec_set: SpecifierSet = req.specifier
        if constraints and req.name in constraints:
            for constraint in constraints[req.name]:
                spec_set &= SpecifierSet(constraint)
        
        if spec_set:
            min_ver: Optional[str] = None
            max_ver: Optional[str] = None
            current_ver: Optional[str] = None
            
            # Sort specs by version for consistent processing
            sorted_specs = sorted(
                spec_set,
                key=lambda s: Version(s.version) if s.version else Version("0")
            )
            
            for spec in sorted_specs:
                if spec.operator in (">=", ">"):
                    min_ver = str(spec)
                elif spec.operator in ("<=", "<"):
                    max_ver = str(spec)
                elif spec.operator == "==":
                    current_ver = str(spec)
                    
            version = UnoplatVersion(
                minimum_version=min_ver,
                maximum_version=max_ver,
                current_version=current_ver
            )
            
        return UnoplatProjectDependency(
            version=version,
            extras=list(req.extras) if req.extras else None
        )

    def _create_empty_metadata(self, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with basic information."""
        return UnoplatPackageManagerMetadata(
            dependencies={},
            programming_language=metadata.language.value,
            package_manager=metadata.package_manager,
            programming_language_version=metadata.language_version
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