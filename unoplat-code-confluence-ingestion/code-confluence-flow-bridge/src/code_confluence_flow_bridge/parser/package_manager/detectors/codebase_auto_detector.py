"""
Python Codebase Auto-Detection System

This module implements automatic detection of Python codebases from GitHub repositories,
including identification of package managers (pip, poetry, uv) and project structure.

Detection is performed by cloning the repository and analyzing its structure using
streaming detection algorithms. Only git URL based detection is supported.

Integrates with the existing unoplat workflow system using Pydantic models and
the existing rules.yaml configuration.
"""

# Import Pydantic models from project settings
from src.code_confluence_flow_bridge.models.configuration.settings import (
    CodebaseConfig,
    FileNode,
    LanguageRules,
    ManagerRule,
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
    Signature,
)

import os
from collections import defaultdict
import fnmatch
import glob
from pathlib import Path
from typing import Dict, List, Literal, Optional, Set, Tuple

# Import Git integration for repository cloning
from git import Repo
import tomlkit
import yaml


class PythonCodebaseDetector:
    """Detector for Python codebases from GitHub repositories using streaming algorithm."""
    
    def __init__(self, rules_path: Optional[str] = None, github_token: Optional[str] = None):
        """
        Initialize the detector.
        
        Args:
            rules_path: Path to rules.yaml file. If None, uses project's rules.yaml.
            github_token: Optional GitHub personal access token for authentication.
        """
        if rules_path is None:
            # Use existing rules.yaml from same directory
            rules_path = os.path.join(os.path.dirname(__file__), "rules.yaml")
        
        self.rules_path = rules_path
        self.github_token = github_token
        self.language_rules = self._load_rules()
        self._file_cache: Dict[str, str] = {}  # Cache for file contents
        self._gitignore_patterns: List[str] = []  # Gitignore patterns
        self._candidate_rules: Dict[str, List[ManagerRule]] = {}  # Filename -> rules mapping
        self._max_weight = max(rule.weight for rule in self.language_rules.managers)
        self._build_candidate_rules()
    
    def _load_rules(self) -> LanguageRules:
        """Load and parse rules from YAML file."""
        if not Path(self.rules_path).exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_path}")
            
        with open(self.rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)
        
        # Extract Python rules
        python_rules = rules_data.get('python', {})
        managers = []
        
        for mgr_data in python_rules.get('managers', []):
            signatures = []
            for sig_data in mgr_data.get('signatures', []):
                if isinstance(sig_data, str):
                    # Simple string signature
                    signatures.append(Signature(file=sig_data))
                elif isinstance(sig_data, dict):
                    # Complex signature
                    signatures.append(Signature(**sig_data))
            
            managers.append(ManagerRule(
                manager=mgr_data['manager'],
                weight=mgr_data.get('weight', 1),
                signatures=signatures,
                workspace_field=mgr_data.get('workspace_field')
            ))
        
        return LanguageRules(
            ignores=python_rules.get('ignores', []),
            managers=managers
        )
    
    def _build_candidate_rules(self) -> None:
        """Build lookup table mapping filenames to applicable rules for O(1) rule matching."""
        self._candidate_rules = defaultdict(list)
        
        for rule in self.language_rules.managers:
            for signature in rule.signatures:
                if signature.file and not signature.contains:
                    # Direct filename match (e.g., 'uv.lock', 'poetry.lock')
                    self._candidate_rules[signature.file].append(rule)
                elif signature.file and signature.contains:
                    # Filename with content check (e.g., 'pyproject.toml' with '[tool.uv]')
                    self._candidate_rules[signature.file].append(rule)
                # Note: glob patterns handled separately in walk_and_detect()
        
        # Convert to regular dict
        self._candidate_rules = dict(self._candidate_rules)
    
    # ──────────────────────────────────────────────────────────────────────────
    # REPOSITORY WALKING
    # ──────────────────────────────────────────────────────────────────────────
    
    def _load_gitignore(self, repo_path: str) -> None:
        """Load .gitignore patterns from repository."""
        gitignore_path = os.path.join(repo_path, '.gitignore')
        self._gitignore_patterns = []
        
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self._gitignore_patterns.append(line)
            except Exception:
                pass
        
        # Add common Python ignore patterns
        default_ignores = [
            '__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python',
            'build/', 'develop-eggs/', 'dist/', 'downloads/', 'eggs/', '.eggs/',
            'lib/', 'lib64/', 'parts/', 'sdist/', 'var/', 'wheels/', 
            '*.egg-info/', '.installed.cfg', '*.egg', 'MANIFEST',
            '.env', '.venv', 'env/', 'venv/', 'ENV/', 'env.bak/', 'venv.bak/',
            '.tox/', '.coverage', '.pytest_cache/', '.mypy_cache/', '.git/'
        ]
        self._gitignore_patterns.extend(default_ignores)
    
    def _is_ignored(self, path: str, repo_path: str) -> bool:
        """Check if path should be ignored based on gitignore patterns."""
        rel_path = os.path.relpath(path, repo_path).replace(os.sep, '/')
        
        for pattern in self._gitignore_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
        return False
    
    def _walk_and_detect(self, repo_path: str) -> Tuple[List[FileNode], Dict[str, ManagerRule]]:
        """
        Walk repository and detect package managers simultaneously.
        
        Returns:
            Tuple of (inventory, hits) where hits maps directory paths to detected package managers.
        """
        self._load_gitignore(repo_path)
        
        # Detection state
        hits: Dict[str, ManagerRule] = {}  # dir_path -> ManagerRule
        done_dirs: Set[str] = set()  # Directories with max-weight matches (stop tracking)
        inventory: List[FileNode] = []  # Complete file inventory for later processing
        workspace_queue: List[Tuple[str, str]] = []  # (parent_dir, workspace_member) pairs
        
        def scan_and_detect(dir_path: str) -> None:
            try:
                with os.scandir(dir_path) as entries:
                    for entry in entries:
                        if self._is_ignored(entry.path, repo_path):
                            continue

                        rel_path = os.path.relpath(entry.path, repo_path).replace(os.sep, '/')

                        if entry.is_dir():
                            inventory.append(FileNode(path=rel_path, kind="dir", size=None))
                            scan_and_detect(entry.path)
                        elif entry.is_file():
                            inventory.append(FileNode(path=rel_path, kind="file", size=None))

                            # Package manager detection logic
                            parent_dir = os.path.dirname(rel_path) or "."
                            filename = os.path.basename(rel_path)

                            # Skip further rule checks only if directory is finished **and**
                            # we are **not** processing a possible uv workspace manifest.
                            skip_due_to_done = (
                                parent_dir in done_dirs
                                and not (
                                    filename == "pyproject.toml"
                                    and hits.get(parent_dir) is not None
                                    and hits[parent_dir].manager == "uv"
                                )
                            )
                            if skip_due_to_done:
                                continue

                            # Check direct filename matches
                            if filename in self._candidate_rules:
                                for rule in self._candidate_rules[filename]:
                                    # Skip if current rule is not better than existing match
                                    if parent_dir in hits and rule.weight <= hits[parent_dir].weight:
                                        continue

                                    # Check signature
                                    match_found = False
                                    for signature in rule.signatures:
                                        if signature.file == filename:
                                            if not signature.contains:
                                                # Direct filename match (e.g., uv.lock, poetry.lock)
                                                match_found = True
                                                break
                                            else:
                                                # Content check required (e.g., pyproject.toml)
                                                content = self._read_local_file(entry.path)
                                                if signature.contains in content:
                                                    match_found = True

                                                    # Handle uv workspace expansion
                                                    if (rule.manager == "uv" and
                                                        signature.contains == "[tool.uv]" and
                                                        "[tool.uv.workspace]" in content):
                                                        try:
                                                            data = tomlkit.loads(content)
                                                            workspace_config = data.get("tool", {}).get("uv", {}).get("workspace", {})
                                                            # Handle exclude and globbed workspace members
                                                            excludes = set(workspace_config.get("exclude", []))
                                                            members = workspace_config.get("members", [])
                                                            for member in members:
                                                                if member in excludes:
                                                                    continue
                                                                # Build member path relative to repo root
                                                                pattern_rel = os.path.join(parent_dir, member) if parent_dir != "." else member
                                                                pattern_rel_posix = pattern_rel.replace(os.sep, "/")
                                                                # Expand globs
                                                                if any(ch in pattern_rel for ch in "*?[]"):
                                                                    abs_pattern = os.path.join(repo_path, pattern_rel_posix)
                                                                    for matched in glob.glob(abs_pattern, recursive=True):
                                                                        if os.path.isdir(matched):
                                                                            rel_matched = os.path.relpath(matched, repo_path).replace(os.sep, "/")
                                                                            if rel_matched not in excludes:
                                                                                workspace_queue.append((parent_dir, rel_matched))
                                                                else:
                                                                    workspace_queue.append((parent_dir, pattern_rel_posix))
                                                        except Exception:
                                                            pass
                                                    break

                                    if match_found:
                                        hits[parent_dir] = rule
                                        # Short-circuit if max weight reached
                                        if rule.weight == self._max_weight:
                                            # For uv, wait until we have inspected pyproject.toml
                                            if not (rule.manager == "uv" and filename == "uv.lock"):
                                                done_dirs.add(parent_dir)
                                        break

                            # Check glob patterns (e.g., requirements-*.txt)
                            if parent_dir not in done_dirs:
                                for rule in self.language_rules.managers:
                                    if parent_dir in hits and rule.weight <= hits[parent_dir].weight:
                                        continue

                                    for signature in rule.signatures:
                                        if signature.glob and fnmatch.fnmatch(filename, signature.glob):
                                            hits[parent_dir] = rule
                                            if rule.weight == self._max_weight:
                                                done_dirs.add(parent_dir)
                                            break
            except PermissionError:
                pass  # Skip directories we can't read
        
        # Start recursive scan
        scan_and_detect(repo_path)
        
        # Process queued workspace members
        for parent_dir, member_path in workspace_queue:
            if member_path not in hits:
                # Find the uv rule
                uv_rule = next((r for r in self.language_rules.managers if r.manager == "uv"), None)
                if uv_rule:
                    hits[member_path] = uv_rule
        
        return inventory, hits
    
    def _read_local_file(self, file_path: str) -> str:
        """Read file contents from local filesystem with caching."""
        if file_path not in self._file_cache:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._file_cache[file_path] = f.read()
            except Exception:
                self._file_cache[file_path] = ""
        return self._file_cache[file_path]
    
    # ──────────────────────────────────────────────────────────────────────────
    # FILTERING
    # ──────────────────────────────────────────────────────────────────────────
    
    def prune_nested_and_ignored(self, hits: Dict[str, ManagerRule], repo_path: Optional[str] = None) -> List[str]:
        """Prune fixture directories and nested packages."""
        ignores = set(self.language_rules.ignores)

        # Filter out paths containing ignored tokens
        keep = []
        for path in hits.keys():
            path_parts = Path(path).parts
            if not any(token in ignores for token in path_parts):
                keep.append(path)

        # Sort shortest->longest so ancestor precedes child
        keep.sort(key=lambda p: len(Path(p).parts))

        # Remove nested duplicates, but keep uv workspace leaves under aggregator
        final: List[str] = []
        for path in keep:
            # Check if this path is nested under any already accepted path
            is_nested = False
            for accepted in final:
                agg_rule = hits[accepted]
                if (
                    path != accepted
                    and path.startswith(accepted + "/")
                    and not (
                        agg_rule.manager == "uv"
                        and self.decide_role(accepted, "uv", repo_path) == "aggregator"
                    )
                ):
                    is_nested = True
                    break

            if not is_nested:
                final.append(path)

        return final
    
    # ──────────────────────────────────────────────────────────────────────────
    # ROLE ASSIGNMENT
    # ──────────────────────────────────────────────────────────────────────────
    
    def decide_role(self, dir_path: str, manager: str, 
                   repo_path: Optional[str] = None) -> Literal["leaf", "aggregator", "NA"]:
        """
        Decide role based on uv workspace semantics.
        - If manager != 'uv' → role = 'NA'
        - If manager == 'uv':
            - manifest has [tool.uv.workspace] → 'aggregator'
            - else → 'leaf'
        """
        if manager != "uv":
            return "NA"
        
        if not repo_path:
            return "leaf"
        
        manifest_path = os.path.join(repo_path, dir_path, "pyproject.toml") if dir_path != "." else os.path.join(repo_path, "pyproject.toml")
        
        try:
            manifest_text = self._read_local_file(manifest_path)
            if "[tool.uv.workspace]" in manifest_text:
                return "aggregator"
        except Exception:
            pass
        
        return "leaf"
    
    # ──────────────────────────────────────────────────────────────────────────
    # CODEBASE BUILDING
    # ──────────────────────────────────────────────────────────────────────────
    
    def _detect_root_packages(self, codebase_dir: str, inventory: List[FileNode]) -> Optional[List[str]]:
        """
        Detect Python root packages by finding directories containing main.py.
        
        Args:
            codebase_dir: The codebase directory path (e.g., "." or "services")
            inventory: List of all files in the repository
            
        Returns:
            List of directories containing main.py relative to codebase_dir,
            or None if no main.py files found
        """
        root_packages = []
        
        # Build prefix for filtering
        if codebase_dir == ".":
            prefix = ""
        else:
            prefix = codebase_dir + "/"
        
        
        # Find all main.py files within this codebase
        main_files = [
            node.path for node in inventory
            if node.kind == "file" 
            and node.path.endswith("/main.py")
            and (node.path.startswith(prefix) if prefix else True)
        ]
        
        # Also check for main.py at codebase root level
        root_main = prefix + "main.py" if prefix else "main.py"
        if any(node.path == root_main for node in inventory):
            main_files.append(root_main)
        
        # Extract package directories from main.py paths
        for main_path in main_files:
            # Remove prefix to get relative path
            rel_path = main_path[len(prefix):] if prefix else main_path
            
            # Get directory containing main.py
            if rel_path == "main.py":
                # main.py at codebase root
                root_packages.append(".")
            else:
                # main.py in subdirectory
                package_dir = os.path.dirname(rel_path)
                if package_dir:
                    root_packages.append(package_dir)
        
        # Remove duplicates and sort
        root_packages = sorted(list(set(root_packages)))
        
        return root_packages if root_packages else None
    
    def _build_codebase_config(self, dir_path: str, mgr_rule: ManagerRule,
                              inventory: List[FileNode], repo_path: Optional[str] = None) -> CodebaseConfig:
        """Build CodebaseConfig object for detected codebase."""
        # Determine role
        role = self.decide_role(dir_path, mgr_rule.manager, repo_path)
        
        # Find manifest path if exists
        manifest_path = None
        if mgr_rule.manager in ["poetry", "uv"]:
            manifest_candidate = os.path.join(dir_path, "pyproject.toml") if dir_path != "." else "pyproject.toml"
            if any(n.path == manifest_candidate for n in inventory):
                manifest_path = manifest_candidate
        
        # Detect root packages based on main.py files
        root_packages = self._detect_root_packages(dir_path, inventory)
        
        # Build programming language metadata
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.PYTHON,
            package_manager=PackageManagerType(mgr_rule.manager),
            language_version=None,
            role=role,
            manifest_path=manifest_path,
            project_name=None
        )
        
        return CodebaseConfig(
            codebase_folder=dir_path,
            root_packages=root_packages,
            programming_language_metadata=programming_language_metadata
        )
    
    # ──────────────────────────────────────────────────────────────────────────
    # MAIN DETECTION INTERFACE
    # ──────────────────────────────────────────────────────────────────────────
    
    def detect_codebases(self, git_url: str) -> List[CodebaseConfig]:
        """
        Main detection method to detect Python codebases from a GitHub repository URL.
        
        Args:
            git_url: GitHub repository URL (supports HTTPS and SSH formats)
            
        Returns:
            List of CodebaseConfig objects for detected codebases
        """
        # Clone repository using similar logic to GithubHelper
        repo_path = self._clone_repository(git_url)
        
        # Walk and detect simultaneously 
        inventory, hits = self._walk_and_detect(repo_path)
        
        # Prune nested and ignored paths
        pruned_paths = self.prune_nested_and_ignored(hits, repo_path)
        
        # Build codebase config objects
        codebase_configs = []
        for path in pruned_paths:
            mgr_rule = hits[path]
            codebase_config = self._build_codebase_config(path, mgr_rule, inventory, repo_path)
            codebase_configs.append(codebase_config)
        
        return codebase_configs
    
    def _clone_repository(self, git_url: str) -> str:
        """
        Clone GitHub repository to local path.
        Uses same logic as GithubHelper for consistency.
        
        Args:
            git_url: GitHub repository URL
            
        Returns:
            Local path to cloned repository
        """
        # Extract repository name from URL (same logic as GithubHelper)
        if git_url.startswith("git@"):
            # Handle SSH format: git@github.com:org/repo.git
            repo_path = git_url.split("github.com:")[-1]
        else:
            # Handle HTTPS format: https://github.com/org/repo[.git]
            repo_path = git_url.split("github.com/")[-1]
        repo_path = repo_path.replace(".git", "")
        repo_name = repo_path.split("/")[-1]
        
        # Create local directory (same as GithubHelper)
        local_base_path = os.path.join(os.path.expanduser("~"), ".unoplat", "repositories")
        os.makedirs(local_base_path, exist_ok=True)
        
        # Set local clone path
        local_repo_path = os.path.join(local_base_path, repo_name)
        
        # Clone repository if not already cloned
        if not os.path.exists(local_repo_path):
            # Add token to URL if provided
            if self.github_token and git_url.startswith("https://"):
                # Insert token into HTTPS URL
                clone_url = git_url.replace("https://", f"https://{self.github_token}@")
            else:
                clone_url = git_url
                
            Repo.clone_from(clone_url, local_repo_path)
        
        return local_repo_path


# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

