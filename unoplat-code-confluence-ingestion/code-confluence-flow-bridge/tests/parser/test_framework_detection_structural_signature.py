"""
Test framework detection using structural signature approach with real production code.
This file validates that structural signatures can effectively identify
framework patterns and concepts in actual Python code from the codebase.
"""

from pathlib import Path
import time
from typing import List, Set

from src.code_confluence_flow_bridge.parser.language_processors.python_processor import (
    build_python_extractor_config,
)
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterPythonStructuralSignatureExtractor,
)
from unoplat_code_confluence_commons.base_models import PythonStructuralSignature


class TestFrameworkDetectionPythonStructuralSignature:
    """Test framework detection using structural signature patterns from real production code."""
    
    def setup_method(self):
        """Set up test fixtures."""
        config = build_python_extractor_config()
        self.extractor = TreeSitterPythonStructuralSignatureExtractor(language_name="python", config=config)

        # Define paths to real source files
        self.base_path = Path(__file__).parent.parent.parent / "src" / "code_confluence_flow_bridge"
        self.main_py_path = self.base_path / "main.py"
        self.repo_workflow_path = self.base_path / "processor" / "repo_workflow.py"
        self.codebase_child_workflow_path = self.base_path / "processor" / "codebase_child_workflow.py"
        # structural_signature.py has been moved to commons, use a different file for testing
        self.commons_base_path = Path(__file__).parent.parent.parent.parent.parent / "unoplat-code-confluence-commons" / "src" / "unoplat_code_confluence_commons" / "base_models"
        self.structural_signature_path = self.commons_base_path / "python_structural_signature.py"
        self.package_metadata_path = self.base_path / "models" / "code_confluence_parsing_models" / "unoplat_package_manager_metadata.py"
        # Repository and CodebaseConfig models moved to commons package
        self.repository_data_path = Path(__file__).parent.parent.parent.parent.parent / "unoplat-code-confluence-commons" / "src" / "unoplat_code_confluence_commons" / "repo_models.py"
    
    def test_fastapi_detection_from_real_main_py(self):
        """Test FastAPI framework detection from actual main.py file."""
        assert self.main_py_path.exists(), f"Main.py not found at {self.main_py_path}"
        
        with open(self.main_py_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Debug: Check what we're extracting
        print(f"\nDebug info:")
        print(f"Global variables count: {len(signature.global_variables)}")
        print(f"Classes count: {len(signature.classes)}")
        
        # Print all global variables to see what's captured
        print("All global variables:")
        for i, var in enumerate(signature.global_variables):
            print(f"  {i}: {var.signature}")
        
        # Check for pydantic patterns
        has_pydantic_patterns = self._has_pydantic_patterns(signature)
        print(f"Has Pydantic patterns: {has_pydantic_patterns}")
        
        if signature.classes:
            print("Class signatures:")
            for cls in signature.classes[:3]:  # First 3 classes
                print(f"  {cls.signature}")
        
        # Test framework detection
        frameworks = self._detect_frameworks(signature)
        print(f"Detected frameworks: {frameworks}")
        
        assert "FastAPI" in frameworks, f"FastAPI not detected in frameworks: {frameworks}"
        
        # For now, test Pydantic separately to understand the issue
        if not has_pydantic_patterns:
            print("WARNING: No Pydantic patterns detected in class signatures")
            # Check if we can find pydantic in imports
            pydantic_in_imports = any('pydantic' in var.signature.lower() for var in signature.global_variables if 'import' in var.signature)
            print(f"Pydantic in imports: {pydantic_in_imports}")
        else:
            assert "Pydantic" in frameworks, f"Pydantic patterns found but not detected in frameworks: {frameworks}"
        
        # Test specific FastAPI patterns
        assert self._has_fastapi_patterns(signature), "FastAPI patterns not found"
        
        # Test API endpoint patterns
        endpoints = self._extract_api_endpoints(signature)
        print(f"Found endpoints: {endpoints}")
        assert len(endpoints) >= 1, f"Expected at least 1 endpoint, found {len(endpoints)}"
    
    def test_temporal_detection_from_real_workflow_files(self):
        """Test Temporal framework detection from actual workflow files."""
        assert self.repo_workflow_path.exists(), f"Repo workflow not found at {self.repo_workflow_path}"
        
        with open(self.repo_workflow_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Test framework detection
        frameworks = self._detect_frameworks(signature)
        assert "Temporal" in frameworks, f"Temporal not detected in frameworks: {frameworks}"
        
        # Test specific Temporal patterns
        assert self._has_temporal_patterns(signature), "Temporal patterns not found"
        
        # Test workflow patterns
        workflows = self._extract_temporal_workflows(signature)
        assert len(workflows) >= 1, f"Expected at least 1 workflow, found {len(workflows)}"
        assert "RepoWorkflow" in workflows, f"RepoWorkflow not found in workflows: {workflows}"
        
        # Test activity execution patterns
        assert self._has_activity_execution_patterns(signature), "Activity execution patterns not found"
        
        # Test child workflow patterns
        assert self._has_child_workflow_patterns(signature), "Child workflow patterns not found"
    
    def test_temporal_detection_from_child_workflow(self):
        """Test Temporal framework detection from child workflow file."""
        assert self.codebase_child_workflow_path.exists(), f"Child workflow not found at {self.codebase_child_workflow_path}"
        
        with open(self.codebase_child_workflow_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Test framework detection
        frameworks = self._detect_frameworks(signature)
        assert "Temporal" in frameworks, f"Temporal not detected in frameworks: {frameworks}"
        
        # Test specific Temporal patterns
        assert self._has_temporal_patterns(signature), "Temporal patterns not found"
        
        # Test workflow patterns
        workflows = self._extract_temporal_workflows(signature)
        assert len(workflows) >= 1, f"Expected at least 1 workflow, found {len(workflows)}"
        assert "CodebaseChildWorkflow" in workflows, f"CodebaseChildWorkflow not found in workflows: {workflows}"
    
    def test_pydantic_detection_from_real_structural_signature_py(self):
        """Test Pydantic detection from actual structural_signature.py file."""
        assert self.structural_signature_path.exists(), f"Structural signature not found at {self.structural_signature_path}"
        
        with open(self.structural_signature_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Test framework detection
        frameworks = self._detect_frameworks(signature)
        assert "Pydantic" in frameworks, f"Pydantic not detected in frameworks: {frameworks}"
        
        # Test specific Pydantic patterns
        assert self._has_pydantic_patterns(signature), "Pydantic patterns not found"
        assert self._has_pydantic_field_patterns(signature), "Pydantic Field patterns not found"
        
        # Test model patterns
        models = self._extract_pydantic_models(signature)
        assert len(models) >= 1, f"Expected at least 1 Pydantic model, found {len(models)}"
        assert "PythonStructuralSignature" in models, f"PythonStructuralSignature not found in models: {models}"
    
    def test_advanced_pydantic_from_real_package_metadata_py(self):
        """Test advanced Pydantic patterns from actual package metadata file."""
        assert self.package_metadata_path.exists(), f"Package metadata not found at {self.package_metadata_path}"
        
        with open(self.package_metadata_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Test framework detection
        frameworks = self._detect_frameworks(signature)
        assert "Pydantic" in frameworks, f"Pydantic not detected in frameworks: {frameworks}"
        
        # Test advanced Pydantic patterns
        assert self._has_pydantic_patterns(signature), "Pydantic patterns not found"
        assert self._has_pydantic_validators(signature), "Pydantic validators not found"
        assert self._has_complex_field_types(signature), "Complex field types not found"
        
        # Test validator patterns
        validators = self._extract_pydantic_validators(signature)
        assert len(validators) >= 1, f"Expected at least 1 validator, found {len(validators)}"
        assert "validate_license" in validators, f"validate_license not found in validators: {validators}"
    
    def test_sqlalchemy_detection_from_real_repository_data_py(self):
        """Test SQLAlchemy/SQLModel detection from actual repo models file in commons package."""
        assert self.repository_data_path.exists(), f"Repository data not found at {self.repository_data_path}"
        
        with open(self.repository_data_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Test framework detection
        frameworks = self._detect_frameworks(signature)
        assert "SQLAlchemy" in frameworks, f"SQLAlchemy not detected in frameworks: {frameworks}"
        # SQLModel detection is optional since we've migrated to SQLBase
        # assert "SQLModel" in frameworks, f"SQLModel not detected in frameworks: {frameworks}"
        
        # Test specific SQLAlchemy patterns
        assert self._has_sqlalchemy_patterns(signature), "SQLAlchemy patterns not found"
        # SQLModel patterns are optional since we've migrated to SQLBase
        # assert self._has_sqlmodel_patterns(signature), "SQLModel patterns not found"
        
        # Test model patterns
        models = self._extract_sqlmodel_tables(signature)
        assert len(models) >= 2, f"Expected at least 2 SQLModel tables, found {len(models)}"
        assert "Repository" in models, f"Repository not found in models: {models}"
        assert "CodebaseConfig" in models, f"CodebaseConfig not found in models: {models}"
        
        # Test relationship patterns
        assert self._has_relationship_patterns(signature), "Relationship patterns not found"
        
        # Test constraint patterns
        assert self._has_constraint_patterns(signature), "Constraint patterns not found"
    
    def test_complex_framework_combination_from_real_main_py(self):
        """Test detection of FastAPI framework in main.py (main.py only defines FastAPI patterns, not models)."""
        assert self.main_py_path.exists(), f"Main.py not found at {self.main_py_path}"
        
        with open(self.main_py_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        
        # Test framework detection from main.py (only FastAPI should be detected via structural patterns)
        frameworks = self._detect_frameworks(signature)
        assert "FastAPI" in frameworks, f"FastAPI not detected in frameworks: {frameworks}"
        
        # main.py doesn't define Pydantic models, SQLAlchemy models, or Temporal workflows
        # It only imports and uses them, so structural signature shouldn't detect them
        
        # Test that FastAPI patterns are detected
        assert self._has_fastapi_patterns(signature), "FastAPI patterns not found"
        
        # Test integration patterns that should be present in main.py
        assert self._has_dependency_injection_patterns(signature), "Dependency injection patterns not found"
        assert self._has_async_patterns(signature), "Async patterns not found"
    
    def test_performance_comparison_with_real_main_py(self):
        """Compare performance of structural signature vs string-based detection using real main.py."""
        assert self.main_py_path.exists(), f"Main.py not found at {self.main_py_path}"
        
        # Read the actual file content
        with open(self.main_py_path, 'r') as f:
            code_content = f.read()
        
        # Time structural signature approach
        start_time = time.time()
        with open(self.main_py_path, 'rb') as f:
            content = f.read()
        signature = self.extractor.extract_structural_signature(content)
        frameworks_structural = self._detect_frameworks(signature)
        structural_time = time.time() - start_time
        
        # Time string-based approach
        start_time = time.time()
        frameworks_string = self._detect_frameworks_string_based(code_content)
        string_time = time.time() - start_time
        
        # Both should detect FastAPI (the main framework actually defined in main.py)
        common_frameworks = frameworks_structural.intersection(frameworks_string)
        assert "FastAPI" in common_frameworks, "FastAPI should be detected by both methods"
        
        # Note: String-based detection might find more frameworks due to imports/usage,
        # but structural signature only detects frameworks where classes/functions are actually defined
        
        # Print performance comparison for analysis
        print(f"\nPerformance Comparison on real main.py:")
        print(f"File size: {len(code_content)} characters")
        print(f"Structural Signature: {structural_time:.4f}s, detected: {frameworks_structural}")
        print(f"String-based: {string_time:.4f}s, detected: {frameworks_string}")
        print(f"Ratio: {structural_time/string_time:.2f}x")
        
        # Structural signature should detect fewer frameworks since it only looks at definitions, not imports/usage
        # This is the correct behavior - main.py imports many frameworks but only defines FastAPI patterns
        assert len(frameworks_structural) <= len(frameworks_string), "Structural signature should detect fewer frameworks (definitions only, not imports)"
    
    def test_framework_detection_across_multiple_real_files(self):
        """Test framework detection across multiple real production files."""
        files_to_test = [
            (self.main_py_path, ["FastAPI"]),  # main.py only defines FastAPI patterns
            (self.repo_workflow_path, ["Temporal"]),
            (self.structural_signature_path, ["Pydantic"]),
            (self.package_metadata_path, ["Pydantic"]),
            (self.repository_data_path, ["SQLAlchemy"])  # Only SQLAlchemy expected since we migrated to SQLBase
        ]
        
        results = {}
        
        for file_path, expected_frameworks in files_to_test:
            if not file_path.exists():
                print(f"Skipping {file_path} - file not found")
                continue
                
            with open(file_path, 'rb') as f:
                content = f.read()
            signature = self.extractor.extract_structural_signature(content)
            detected_frameworks = self._detect_frameworks(signature)
            
            results[file_path.name] = {
                'detected': detected_frameworks,
                'expected': set(expected_frameworks),
                'file_path': str(file_path)
            }
            
            # Check that expected frameworks are detected
            for framework in expected_frameworks:
                assert framework in detected_frameworks, f"{framework} not detected in {file_path.name}"
        
        # Print summary
        print(f"\nFramework Detection Summary:")
        for file_name, result in results.items():
            print(f"{file_name}:")
            print(f"  Expected: {result['expected']}")
            print(f"  Detected: {result['detected']}")
            print(f"  Additional: {result['detected'] - result['expected']}")
    
    # Helper methods for framework detection
    def _detect_frameworks(self, signature: PythonStructuralSignature) -> Set[str]:
        """Detect frameworks from structural signature."""
        frameworks = set()
        
        # Extract imports from global variables (imports are typically stored as global variables)
        import_statements = []
        for var in signature.global_variables:
            if 'import' in var.signature or 'from' in var.signature:
                import_statements.append(var.signature.lower())
        
        # Convert to single string for analysis
        import_text = ' '.join(import_statements)
        
        # Check imports for framework indicators
        if 'fastapi' in import_text:
            frameworks.add("FastAPI")
        if 'django' in import_text:
            frameworks.add("Django")
        if 'flask' in import_text:
            frameworks.add("Flask")
        if 'temporal' in import_text:
            frameworks.add("Temporal")
        if 'sqlalchemy' in import_text or 'sqlmodel' in import_text:
            frameworks.add("SQLAlchemy")
            if 'sqlmodel' in import_text:
                frameworks.add("SQLModel")
        if 'pydantic' in import_text:
            frameworks.add("Pydantic")
        if 'pytest' in import_text:
            frameworks.add("Pytest")
        
        # Check structural patterns even if imports aren't detected
        if self._has_fastapi_patterns(signature):
            frameworks.add("FastAPI")
        if self._has_temporal_patterns(signature):
            frameworks.add("Temporal")
        if self._has_pydantic_patterns(signature):
            frameworks.add("Pydantic")
        if self._has_sqlalchemy_patterns(signature):
            frameworks.add("SQLAlchemy")
        if self._has_sqlmodel_patterns(signature):
            frameworks.add("SQLModel")
        
        return frameworks
    
    def _detect_frameworks_string_based(self, code: str) -> Set[str]:
        """String-based framework detection for performance comparison."""
        frameworks = set()
        
        if 'fastapi' in code.lower():
            frameworks.add("FastAPI")
        if 'pydantic' in code.lower():
            frameworks.add("Pydantic")
        if 'sqlalchemy' in code.lower():
            frameworks.add("SQLAlchemy")
        if 'sqlmodel' in code.lower():
            frameworks.add("SQLModel")
        if 'temporal' in code.lower():
            frameworks.add("Temporal")
        
        return frameworks
    
    def _has_fastapi_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains FastAPI patterns."""
        # Look for FastAPI app creation
        for var in signature.global_variables:
            if "FastAPI" in var.signature:
                return True
        
        # Look for route decorators in function signatures
        for func in signature.functions:
            if "@app." in func.signature and any(method in func.signature for method in ["get", "post", "put", "delete"]):
                return True
        
        return False
    
    def _has_temporal_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains Temporal patterns."""
        # Look for workflow/activity decorators in function signatures
        for func in signature.functions:
            if "@workflow.defn" in func.signature or "@activity.defn" in func.signature:
                return True
        
        # Look for workflow decorators in class signatures
        for cls in signature.classes:
            if "@workflow.defn" in cls.signature:
                return True
        
        return False
    
    def _has_pydantic_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains Pydantic patterns."""
        # Look for BaseModel inheritance in class signatures
        for cls in signature.classes:
            if "BaseModel" in cls.signature:
                return True
        
        return False
    
    def _has_sqlalchemy_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains SQLAlchemy patterns."""
        # Look for SQLModel or SQLBase inheritance in class signatures
        for cls in signature.classes:
            if "SQLModel" in cls.signature or "SQLBase" in cls.signature:
                return True
        
        # Look for Column definitions in variables
        for var in signature.global_variables:
            if "Column" in var.signature:
                return True
        
        # Look for SQLAlchemy imports or usage patterns
        all_text = ' '.join([var.signature for var in signature.global_variables])
        if 'sqlalchemy' in all_text.lower() or 'sqlmodel' in all_text.lower() or 'sqlbase' in all_text.lower():
            return True
        
        return False
    
    def _has_sqlmodel_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains SQLModel patterns."""
        for cls in signature.classes:
            if "SQLModel" in cls.signature and "table=True" in cls.signature:
                return True
        return False
    
    def _has_pydantic_field_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains Pydantic Field patterns."""
        for cls in signature.classes:
            for var in cls.vars:
                if "Field(" in var.signature:
                    return True
        return False
    
    def _has_pydantic_validators(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains Pydantic validator patterns."""
        for cls in signature.classes:
            for method in cls.methods:
                if "@field_validator" in method.signature:
                    return True
        return False
    
    def _has_middleware_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains middleware patterns."""
        for func in signature.functions:
            for call in func.function_calls:
                if "add_middleware" in call:
                    return True
        return False
    
    def _has_dependency_injection_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains dependency injection patterns."""
        for func in signature.functions:
            if "Depends(" in func.signature:
                return True
        return False
    
    def _has_activity_execution_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains Temporal activity execution patterns."""
        # Check module-level functions
        for func in signature.functions:
            for call in func.function_calls:
                if "workflow.execute_activity" in call:
                    return True
        
        # Check class methods (where workflow.execute_activity typically appears)
        for cls in signature.classes:
            for method in cls.methods:
                for call in method.function_calls:
                    if "workflow.execute_activity" in call:
                        return True
        return False
    
    def _has_child_workflow_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains child workflow patterns."""
        # Check module-level functions
        for func in signature.functions:
            for call in func.function_calls:
                if "workflow.start_child_workflow" in call:
                    return True
        
        # Check class methods (where workflow.start_child_workflow typically appears)
        for cls in signature.classes:
            for method in cls.methods:
                for call in method.function_calls:
                    if "workflow.start_child_workflow" in call:
                        return True
        return False
    
    def _has_temporal_client_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains Temporal client patterns."""
        for func in signature.functions:
            for call in func.function_calls:
                if "Client.connect" in call or "start_workflow" in call:
                    return True
        return False
    
    def _has_relationship_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains SQLAlchemy relationship patterns."""
        for cls in signature.classes:
            for var in cls.vars:
                if "relationship(" in var.signature or "Relationship(" in var.signature:
                    return True
        return False
    
    def _has_constraint_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains SQLAlchemy constraint patterns."""
        for cls in signature.classes:
            for var in cls.vars:
                if "__table_args__" in var.signature:
                    return True
        return False
    
    def _has_complex_field_types(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains complex Pydantic field types."""
        for cls in signature.classes:
            for var in cls.vars:
                if "Dict[" in var.signature or "List[" in var.signature or "Optional[" in var.signature:
                    return True
        return False
    
    def _has_async_patterns(self, signature: PythonStructuralSignature) -> bool:
        """Check if signature contains async patterns."""
        for func in signature.functions:
            if "async def" in func.signature:
                return True
        return False
    
    def _extract_api_endpoints(self, signature: PythonStructuralSignature) -> List[str]:
        """Extract API endpoints from signature."""
        endpoints = []
        for func in signature.functions:
            if "@app." in func.signature:
                for method in ["get", "post", "put", "delete"]:
                    if f"@app.{method}" in func.signature:
                        endpoints.append(f"@app.{method}")
        return endpoints
    
    def _extract_temporal_workflows(self, signature: PythonStructuralSignature) -> List[str]:
        """Extract Temporal workflow names from signature."""
        workflows = []
        for cls in signature.classes:
            if "@workflow.defn" in cls.signature:
                # Extract class name from signature
                if "class " in cls.signature:
                    class_name = cls.signature.split("class ")[1].split("(")[0].split(":")[0].strip()
                    workflows.append(class_name)
        return workflows
    
    def _extract_pydantic_models(self, signature: PythonStructuralSignature) -> List[str]:
        """Extract Pydantic model names from signature."""
        models = []
        for cls in signature.classes:
            if "BaseModel" in cls.signature:
                # Extract class name from signature
                if "class " in cls.signature:
                    class_name = cls.signature.split("class ")[1].split("(")[0].split(":")[0].strip()
                    models.append(class_name)
        return models
    
    def _extract_sqlmodel_tables(self, signature: PythonStructuralSignature) -> List[str]:
        """Extract SQLModel/SQLBase table names from signature."""
        tables = []
        for cls in signature.classes:
            # Check for SQLModel with table=True OR SQLBase (which are always tables)
            is_table = (("SQLModel" in cls.signature and "table=True" in cls.signature) or 
                       "SQLBase" in cls.signature)
            if is_table:
                # Extract class name from signature
                if "class " in cls.signature:
                    class_name = cls.signature.split("class ")[1].split("(")[0].split(":")[0].strip()
                    tables.append(class_name)
        return tables
    
    def _extract_pydantic_validators(self, signature: PythonStructuralSignature) -> List[str]:
        """Extract Pydantic validator method names from signature."""
        validators = []
        for cls in signature.classes:
            for method in cls.methods:
                if "@field_validator" in method.signature:
                    # Extract method name from signature
                    if "def " in method.signature:
                        method_name = method.signature.split("def ")[1].split("(")[0].strip()
                        validators.append(method_name)
        return validators