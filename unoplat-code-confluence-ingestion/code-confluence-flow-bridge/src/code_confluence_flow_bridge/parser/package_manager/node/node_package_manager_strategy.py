# Standard Library
import json
from typing import Any, Dict, Optional

# Third Party
from loguru import logger
from unoplat_code_confluence_commons.base_models import ProgrammingLanguageMetadata

# First Party
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatPackageManagerMetadata,
    UnoplatProjectDependency,
    UnoplatVersion,
)
from src.code_confluence_flow_bridge.parser.package_manager.node.package_json_loader import (
    PackageJsonManifest,
    load_package_json,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import (
    PackageManagerStrategy,
)


class NodePackageManagerStrategy(PackageManagerStrategy):
    """Base strategy for Node.js package managers (npm, pnpm, yarn).

    This class provides common functionality for parsing package.json files
    and extracting dependency metadata. Specific package manager implementations
    (NpmStrategy, PnpmStrategy, YarnStrategy) should extend this class.
    """

    def process_metadata(
        self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Process package.json metadata for Node.js projects.

        Loads package.json exactly once and extracts:
        - Dependency groups (default, dev, peer, optional, bundled, override)
        - Project metadata (name, version, description, etc.)
        - Scripts, binaries, and entry points
        - TypeScript version inference

        Args:
            local_workspace_path: Path to the workspace containing package.json
            metadata: Programming language metadata with manifest_path

        Returns:
            UnoplatPackageManagerMetadata with all extracted information

        Raises:
            PackageJsonNotFoundError: If package.json doesn't exist
            PackageJsonParseError: If package.json is malformed
            ValueError: If language/package_manager pair is unexpected
        """
        # Load manifest exactly once
        manifest = load_package_json(local_workspace_path, metadata)

        # Assert expected language/package_manager pair
        expected_language = metadata.language.value if metadata.language else "unknown"
        expected_pm = metadata.package_manager.value if metadata.package_manager else "unknown"

        logger.info(
            "Processing Node.js package manifest",
            extra={
                "language": expected_language,
                "package_manager": expected_pm,
                "manifest_path": metadata.manifest_path,
            },
        )

        # Extract raw dependency buckets
        dependency_groups = self._build_dependency_groups(manifest)

        # Collect supporting metadata fields
        metadata_fields = self._collect_metadata_fields(manifest, dependency_groups)

        # Infer TypeScript version
        typescript_version = self._infer_typescript_version(
            manifest, dependency_groups
        )

        # Convert dependency groups to UnoplatProjectDependency
        dependencies_result: Dict[str, Dict[str, UnoplatProjectDependency]] = {}

        for group_name, group_deps in dependency_groups.items():
            dependencies_result[group_name] = {}

            for pkg_name, version_spec in group_deps.items():
                # Special handling for override group
                if group_name == "override":
                    extracted_version = self._extract_override_version(version_spec)
                    if extracted_version is None:
                        # Complex override without version - skip
                        continue
                    version_spec = extracted_version

                # Parse the dependency spec
                parsed_spec = self._parse_dependency_spec(pkg_name, version_spec)

                # Create UnoplatVersion (specifier can be None for git/file/etc)
                version = (
                    UnoplatVersion(specifier=parsed_spec["specifier"])
                    if parsed_spec["specifier"]
                    else UnoplatVersion()
                )

                # Create UnoplatProjectDependency
                dependencies_result[group_name][pkg_name] = UnoplatProjectDependency(
                    version=version,
                    source=parsed_spec["source"],
                    source_url=parsed_spec["source_url"],
                    source_reference=parsed_spec["source_reference"],
                    subdirectory=parsed_spec["subdirectory"],
                    extras=parsed_spec["extras"],
                )

        # Instantiate UnoplatPackageManagerMetadata
        # Note: manifest_path is already in ProgrammingLanguageMetadata, not duplicated here
        package_manager_value = expected_pm if expected_pm != "unknown" else "unknown"

        return UnoplatPackageManagerMetadata(
            dependencies=dependencies_result,
            programming_language=expected_language,
            package_manager=package_manager_value,
            programming_language_version=typescript_version,
            **metadata_fields,  # Unpack collected metadata
        )

    def _build_dependency_groups(
        self, manifest: PackageJsonManifest
    ) -> Dict[str, Dict[str, str]]:
        """Extract raw dependency buckets from manifest.

        Returns dict mapping group names to package version specs.
        Read-only access, no mutation.

        Args:
            manifest: Parsed package.json manifest

        Returns:
            Dict with keys: default, dev, peer, optional, bundled, override
            Each value is a dict mapping package name to version spec string

        Example:
            {
                "default": {"react": "^18.0.0", "typescript": "^5.0.0"},
                "dev": {"jest": "^29.0.0"},
                "peer": {},
                "optional": {},
                "bundled": {},
                "override": {}
            }
        """
        return manifest.dependencies

    def _parse_dependency_spec(
        self, package_name: str, version_spec: str
    ) -> Dict[str, Any]:
        """Parse dependency spec into structured dict.

        Handles semver, git URLs, HTTP tarballs, file paths, workspace protocol, tags.
        Returns dict with specifier (can be None for non-registry sources).

        Args:
            package_name: Name of the package (e.g., "react")
            version_spec: Version specification string (e.g., "^18.0.0")

        Returns:
            Dict with keys:
                - specifier: Version range string (e.g., "^18.0.0")
                - source: Optional source type ("git", "file", "url", "workspace", "link")
                - source_url: Optional URL for git/http sources
                - source_reference: Optional branch/tag/commit for git sources
                - subdirectory: Optional subdirectory within git repos
                - extras: Optional list of extras/features

        Examples:
            >>> _parse_dependency_spec("react", "^18.0.0")
            {"specifier": "^18.0.0", "source": None, ...}

            >>> _parse_dependency_spec("pkg", "git+https://github.com/user/repo#main")
            {"specifier": None, "source": "git", "source_url": "...", ...}
        """
        # Strip whitespace
        version_spec = version_spec.strip()

        # Git URLs (multiple formats)
        if any(version_spec.startswith(prefix) for prefix in
               ["git+", "git://", "git@", "ssh://", "github:"]):
            return self._parse_git_spec(version_spec)

        # HTTP(S) tarballs
        if version_spec.startswith("http://") or version_spec.startswith("https://"):
            return {
                "specifier": None,
                "source": "url",
                "source_url": version_spec,
                "source_reference": None,
                "subdirectory": None,
                "extras": None,
            }

        # File paths
        if version_spec.startswith("file:") or version_spec.startswith("link:"):
            source_type = "file" if version_spec.startswith("file:") else "link"
            path = version_spec.split(":", 1)[1]
            return {
                "specifier": None,
                "source": source_type,
                "source_url": path,
                "source_reference": None,
                "subdirectory": None,
                "extras": None,
            }

        # Workspace protocol
        if version_spec.startswith("workspace:"):
            workspace_version = version_spec.split(":", 1)[1]
            return {
                "specifier": workspace_version if workspace_version != "*" else None,
                "source": "workspace",
                "source_url": None,
                "source_reference": None,
                "subdirectory": None,
                "extras": None,
            }

        # Default: semver or tag (registry)
        return {
            "specifier": version_spec,
            "source": None,
            "source_url": None,
            "source_reference": None,
            "subdirectory": None,
            "extras": None,
        }

    def _collect_metadata_fields(
        self, manifest: PackageJsonManifest, dependency_groups: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """Extract supporting metadata from manifest for UnoplatPackageManagerMetadata.

        Returns a dict with safe defaults for all metadata fields.

        Args:
            manifest: Parsed package.json manifest
            dependency_groups: Extracted dependency buckets (for context)

        Returns:
            Dict containing:
                - scripts: Dict of npm scripts
                - binaries: Dict of CLI binaries
                - entry_points: Dict of module entry points (from main/module/types/exports)
                - package_name: Package name
                - project_version: Package version
                - description: Package description
                - keywords: List of keywords
                - homepage: Homepage URL
                - repository: Repository URL (extracted from string or object)
                - documentation: Documentation URL
                - authors: List of author strings
                - maintainers: List of maintainer strings
                - license: License info (string or dict)
                - readme: README path/content
        """
        # Safe author handling
        authors = []
        if manifest.author:
            if isinstance(manifest.author, str):
                authors = [manifest.author]
            elif isinstance(manifest.author, dict):
                # Format: {"name": "...", "email": "...", "url": "..."}
                name = manifest.author.get("name", "")
                email = manifest.author.get("email", "")
                if name and email:
                    authors = [f"{name} <{email}>"]
                elif name:
                    authors = [name]
                elif email:
                    authors = [f"<{email}>"]

        # Safe maintainers handling
        maintainers = []
        for maintainer in manifest.maintainers:
            if isinstance(maintainer, str):
                maintainers.append(maintainer)
            elif isinstance(maintainer, dict):
                name = maintainer.get("name", "")
                email = maintainer.get("email", "")
                if name and email:
                    maintainers.append(f"{name} <{email}>")
                elif name:
                    maintainers.append(name)
                elif email:
                    maintainers.append(f"<{email}>")

        # Extract repository URL (no normalization)
        repository_url = None
        if manifest.repository:
            if isinstance(manifest.repository, str):
                repository_url = manifest.repository
            elif isinstance(manifest.repository, dict):
                repository_url = manifest.repository.get("url")

        return {
            "scripts": manifest.scripts,  # Already Dict[str, str]
            "binaries": manifest.bin,  # Already normalized to Dict[str, str]
            "entry_points": self._build_entry_points(manifest),
            "package_name": manifest.name,
            "project_version": manifest.version,
            "description": manifest.description,
            "keywords": manifest.keywords,
            "homepage": manifest.homepage,
            "repository": repository_url,
            "documentation": manifest.documentation,
            "authors": authors,
            "maintainers": maintainers,
            "license": manifest.license,
            "readme": manifest.readme,
        }

    def _infer_typescript_version(
        self, manifest: PackageJsonManifest, dependency_groups: Dict[str, Dict[str, str]]
    ) -> Optional[str]:
        """Infer TypeScript/Node.js version from manifest.

        Preference order:
        1. devDependencies.typescript
        2. peerDependencies.typescript
        3. engines.node (as fallback indicator)

        Args:
            manifest: Parsed package.json manifest
            dependency_groups: Extracted dependency buckets

        Returns:
            Version string or None if not found

        Example:
            "^5.0.0" (from devDependencies.typescript)
        """
        # 1. Check devDependencies for typescript
        dev_deps = dependency_groups.get("dev", {})
        if "typescript" in dev_deps:
            return dev_deps["typescript"].strip()

        # 2. Fall back to peerDependencies
        peer_deps = dependency_groups.get("peer", {})
        if "typescript" in peer_deps:
            return peer_deps["typescript"].strip()

        # 3. Fall back to engines.node
        engines = manifest.engines
        if isinstance(engines, dict) and "node" in engines:
            return engines["node"].strip()

        return None

    def _flatten_exports(self, exports_node: Any) -> Dict[str, str]:
        """Iteratively flatten nested exports structure.

        Uses a stack-based approach to avoid recursion.
        Ignores non-dict/non-string leaves (e.g., booleans).

        Handles deeply nested exports like:
        {
          ".": {
            "import": {
              "types": "./dist/index.d.ts",
              "default": "./dist/index.mjs"
            },
            "require": "./dist/index.cjs"
          }
        }

        Produces keys like: export:.:import:types

        Args:
            exports_node: The exports value from package.json

        Returns:
            Flattened dict with colon-separated keys
        """
        result = {}

        # Stack holds (prefix, node) tuples
        stack = [("export", exports_node)]

        while stack:
            prefix, node = stack.pop()

            if isinstance(node, str):
                # Leaf node - store path
                result[prefix] = node
            elif isinstance(node, dict):
                # Push children onto stack in reverse order to maintain key order
                for key in reversed(list(node.keys())):
                    value = node[key]
                    nested_prefix = f"{prefix}:{key}"
                    stack.append((nested_prefix, value))
            # Ignore other types (booleans, numbers, etc.)

        return result

    def _build_entry_points(self, manifest: PackageJsonManifest) -> Dict[str, str]:
        """Extract entry points from manifest fields.

        Combines simple fields (main, module, types) with flattened exports.

        Args:
            manifest: Parsed package.json manifest

        Returns:
            Dict mapping entry point names to file paths

        Example:
            {
                "main": "dist/index.js",
                "module": "dist/index.mjs",
                "types": "dist/index.d.ts",
                "export:.:import": "./dist/index.mjs",
                "export:.:require": "./dist/index.cjs"
            }
        """
        entry_points = {}

        # Simple fields
        if manifest.main:
            entry_points["main"] = manifest.main
        if manifest.module:
            entry_points["module"] = manifest.module
        if manifest.types:
            entry_points["types"] = manifest.types

        # Flatten exports iteratively
        if manifest.exports:
            if isinstance(manifest.exports, dict):
                flattened = self._flatten_exports(manifest.exports)
                entry_points.update(flattened)
            elif isinstance(manifest.exports, str):
                entry_points["export"] = manifest.exports

        return entry_points

    def _parse_git_spec(self, spec: str) -> Dict[str, Any]:
        """Parse git URL specs comprehensively.

        Captures raw fragment as source_reference (including subdirectory suffix like #main:packages/pkg).
        Future enhancement: split subdirectory from reference.

        Handles:
        - git+https://github.com/user/repo.git
        - git+https://github.com/user/repo.git#commit-sha
        - git+https://github.com/user/repo.git#semver:^1.0.0
        - git+https://github.com/user/repo.git#main:packages/pkg (subdirectory)
        - github:user/repo#branch
        - git://github.com/user/repo.git#main
        - ssh://git@github.com/user/repo.git#main
        - git@github.com:user/repo.git#branch

        Args:
            spec: Git URL specification string

        Returns:
            Dict with parsed git source information
        """
        source_url = None
        source_reference = None

        # GitHub shorthand: github:user/repo#branch
        if spec.startswith("github:"):
            spec = spec[7:]
            if "#" in spec:
                repo, ref = spec.split("#", 1)
                source_reference = ref  # Raw fragment, may include :subdir
            else:
                repo = spec
            source_url = f"https://github.com/{repo}"

        # Git URLs with various schemes
        elif any(spec.startswith(prefix) for prefix in ["git+", "git://", "git@", "ssh://"]):
            url = spec

            # Remove git+ prefix
            if url.startswith("git+"):
                url = url[4:]

            # Extract reference from fragment (raw capture)
            if "#" in url:
                url, source_reference = url.split("#", 1)
                # Keep raw reference (e.g., "main:packages/pkg" or "semver:^1.0.0")
                # Future: parse subdirectory suffix

            # Normalize SSH format: git@github.com:user/repo -> ssh://git@github.com/user/repo
            if url.startswith("git@") and ":" in url and not url.startswith("git@https://"):
                # git@github.com:user/repo.git
                parts = url.split(":", 1)
                url = f"ssh://{parts[0]}/{parts[1]}"

            # Clean .git suffix
            if url.endswith(".git"):
                url = url[:-4]

            source_url = url

        return {
            "specifier": None,
            "source": "git",
            "source_url": source_url,
            "source_reference": source_reference,  # Raw, may include subdirectory
            "subdirectory": None,  # Future: extract from reference
            "extras": None,
        }

    def _extract_override_version(self, version_spec: str) -> Optional[str]:
        """Extract version from npm override entry (may be JSON string).

        npm overrides can be:
        - Simple: "lodash": "^4.17.21"
        - Complex: "lodash": {"version": "^4.17.21", "dependencies": {...}}

        Strips whitespace from version strings.
        Returns the version string or None if complex structure without version.

        Args:
            version_spec: Version specification string or JSON-serialized override

        Returns:
            Clean version string or None

        Examples:
            >>> _extract_override_version("^4.17.21")
            "^4.17.21"

            >>> _extract_override_version('{"version": "  ^4.17.21  ", "dependencies": {...}}')
            "^4.17.21"

            >>> _extract_override_version('{"dependencies": {...}}')
            None
        """
        # Try to parse as JSON
        if version_spec.startswith("{") or version_spec.startswith("["):
            try:
                parsed = json.loads(version_spec)
                if isinstance(parsed, dict) and "version" in parsed:
                    return parsed["version"].strip()
                # Complex override without explicit version - skip
                return None
            except json.JSONDecodeError:
                pass  # Not valid JSON, treat as string

        # Simple string version - strip whitespace
        return version_spec.strip()
