from typing import Dict, List, Optional, Iterator
import os
import requirements
from loguru import logger
from unoplat_code_confluence.data_models.unoplat_project_dependency import UnoplatProjectDependency
from unoplat_code_confluence.data_models.unoplat_version import UnoplatVersion

class RequirementsUtils:
    """Utility class for parsing requirements files using requirements-parser library."""
    
    # Add constants for unsupported options that we want to skip
    _SKIP_OPTIONS = {
        '-c', '--constraint',  # Constraint files
        '-r', '--requirement', # Recursive requirements 
        '--no-binary', '--only-binary', '--prefer-binary',
        '--require-hashes',
        '--pre',
        '--trusted-host',
        '--use-feature',
        '-Z', '--always-unzip'
    }
    
    @staticmethod
    def parse_requirements_folder(workspace_path: str) -> List[UnoplatProjectDependency]:
        """Parse requirements files from the requirements folder.
        
        Args:
            workspace_path: Path to project workspace
            
        Returns:
            List of parsed dependencies
            
        Note:
            Looks for requirements files in this order:
            1. requirements/default.txt
            2. requirements/requirements.txt  
            3. requirements/*.txt
            4. requirements.txt (in workspace root)
        """
        requirements_paths = []
        dependencies = []
        
        # Check requirements folder first
        req_folder = os.path.join(workspace_path, "requirements")
        if os.path.exists(req_folder):
            # Priority 1: default.txt
            default_path = os.path.join(req_folder, "default.txt")
            if os.path.exists(default_path):
                requirements_paths.append(default_path)
                
            # Priority 2: requirements.txt in requirements folder    
            req_txt_path = os.path.join(req_folder, "requirements.txt")
            if os.path.exists(req_txt_path):
                requirements_paths.append(req_txt_path)
                
            # Priority 3: All .txt files in requirements folder
            if not requirements_paths:
                requirements_paths.extend([
                    os.path.join(req_folder, f) 
                    for f in os.listdir(req_folder) 
                    if f.endswith('.txt')
                ])
        
        # Priority 4: requirements.txt in workspace root
        root_req_txt = os.path.join(workspace_path, "requirements.txt")
        if os.path.exists(root_req_txt):
            requirements_paths.append(root_req_txt)
            
        if not requirements_paths:
            logger.warning(f"No requirements files found in {workspace_path}")
            return []
            
        # Parse all found requirement files using requirements-parser
        for req_file in requirements_paths:
            try:
                with open(req_file, 'r') as f:
                    for req in requirements.parse(f):
                        dep = RequirementsUtils._convert_requirement_to_dependency(req)
                        if dep:
                            dependencies.append(dep)
            except Exception as e:
                logger.error(f"Error parsing {req_file}: {str(e)}")
                
        return dependencies
    
    @staticmethod 
    def parse_requirements_file(file_path: str) -> Iterator[UnoplatProjectDependency]:
        """Parse a single requirements file.
        
        Args:
            file_path: Path to requirements file
            
        Yields:
            Parsed dependencies
            
        Raises:
            OSError: If file cannot be read
            ValueError: If requirements are invalid
        """
        try:
            with open(file_path, 'r') as f:
                for req in requirements.parse(f):
                    dep = RequirementsUtils._convert_requirement_to_dependency(req)
                    if dep:
                        yield dep
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {str(e)}")
            raise

    @staticmethod
    def _convert_requirement_to_dependency(req) -> Optional[UnoplatProjectDependency]:
        """Convert requirements-parser Requirement to UnoplatProjectDependency."""
        try:
            # Get package name, handling both VCS and regular requirements
            name = req.name
            if not name and req.uri:
                # Try to get name from URI fragment
                if hasattr(req, 'fragment') and req.fragment:
                    name = req.fragment.get('egg')
            
            if not name:
                logger.warning(f"Could not determine package name from: {req.line}")
                return None

            # Handle version specs
            version = UnoplatVersion()
            if req.specs:
                # Sort specs for consistent output
                sorted_specs = sorted(req.specs, key=lambda x: (x[0], x[1]))
                
                # Parse version constraints into min/max versions
                for op, ver in sorted_specs:
                    if op in ('>=', '>'):
                        version.minimum_version = ver
                    elif op in ('<=', '<'):
                        version.maximum_version = ver
                    elif op == '==':
                        version.current_version = ver
                        
                    elif op == '~=':  # Compatible release operator
                        version.minimum_version = ver
                        # Calculate compatible release max version
                        parts = ver.split('.')
                        if len(parts) >= 2:
                            parts[-1] = '0'  # Zero out patch version
                            parts[-2] = str(int(parts[-2]) + 1)  # Increment minor version
                            version.maximum_version = '.'.join(parts)
            
            # Determine source info
            source = None
            source_url = None
            if req.vcs:
                source = req.vcs
                source_url = req.uri
            elif req.uri:
                source = "url" 
                source_url = req.uri
            elif req.local_file:
                source = "path"
                source_url = req.path

            # Get hash info if present
            hash_info = None
            if hasattr(req, 'hash_name') and req.hash_name:
                hash_info = f"{req.hash_name}:{req.hash}"

            return UnoplatProjectDependency(
                name=name,
                version=version,  # Now passing UnoplatVersion object directly
                extras=sorted(req.extras) if req.extras else None,
                source=source,
                source_url=source_url,
                source_reference=req.revision if req.vcs else None,
                subdirectory=req.subdirectory if hasattr(req, 'subdirectory') else None,
                hash_info=hash_info
            )
        except Exception as e:
            logger.error(f"Error converting requirement {req.line}: {str(e)}")
            return None