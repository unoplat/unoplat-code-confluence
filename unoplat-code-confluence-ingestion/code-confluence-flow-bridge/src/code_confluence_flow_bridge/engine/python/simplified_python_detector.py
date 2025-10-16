"""
Simplified Python framework detection using structural signatures.

This module replaces the complex Tree-sitter based detection with direct
analysis of pre-parsed structural signature data.
"""

import re
from typing import Dict, List, Optional, Set

from loguru import logger
from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    Concept,
    Detection,
    FeatureSpec,
    InheritanceInfo,
    LocatorStrategy,
    PythonClassInfo,
    PythonFunctionInfo,
    PythonStructuralSignature,
)


class SimplifiedPythonDetector:
    """Simplified Python framework detector using structural signatures."""

    def detect_from_structural_signature(
        self,
        structural_signature: PythonStructuralSignature,
        feature_specs: List[FeatureSpec],
        import_aliases: Dict[str, str],
    ) -> List[Detection]:
        """
        Detect framework features using pre-parsed structural signature data.

        Args:
            structural_signature: Parsed structure of the file
            feature_specs: Framework features to detect
            import_aliases: Mapping from absolute paths to aliases

        Returns:
            List of Detection objects for found framework features
        """
        all_detections: List[Detection] = []

        for spec in feature_specs:
            try:
                detections = self._detect_feature(
                    structural_signature, spec, import_aliases
                )
                all_detections.extend(detections)

            except Exception as e:
                logger.warning("Failed to detect feature {}: {}", spec.feature_key, e)

        return all_detections

    def _detect_feature(
        self, signature: PythonStructuralSignature, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> List[Detection]:
        """Detect a single feature using the appropriate concept method."""

        if spec.concept == Concept.ANNOTATION_LIKE:
            return self._detect_annotation_like(signature, spec, aliases)
        elif spec.concept == Concept.CALL_EXPRESSION:
            return self._detect_call_expression(signature, spec, aliases)
        elif spec.concept == Concept.INHERITANCE:
            return self._detect_inheritance(signature, spec, aliases)
        else:
            logger.warning("Unsupported concept: {}", spec.concept)
            return []

    def _detect_annotation_like(
        self, signature: PythonStructuralSignature, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> List[Detection]:
        """
        Detect decorator patterns like @app.get("/path") using function signatures.
        """
        detections: List[Detection] = []

        # Get bound variables if using VariableBound strategy
        bound_variables = set()
        if spec.locator_strategy == LocatorStrategy.VARIABLE_BOUND:
            bound_variables = self._find_bound_variables(signature, spec, aliases)
            if not bound_variables:
                return []

        # Check all functions and methods (including nested functions)
        all_functions = signature.functions.copy()

        # Add methods from classes
        for class_info in signature.classes:
            all_functions.extend(class_info.methods)
            # Add nested functions from each method
            for method in class_info.methods:
                all_functions.extend(self._collect_nested_functions_recursively(method))

            for nested_class in class_info.nested_classes:
                all_functions.extend(nested_class.methods)
                # Add nested functions from nested class methods
                for method in nested_class.methods:
                    all_functions.extend(
                        self._collect_nested_functions_recursively(method)
                    )

        for func in all_functions:
            detections.extend(
                self._extract_decorators_from_function(func, spec, bound_variables)
            )

        return detections

    def _collect_nested_functions_recursively(
        self, func: PythonFunctionInfo
    ) -> List[PythonFunctionInfo]:
        """Recursively collect all nested functions within a function."""
        nested_functions = []

        for nested_func in func.nested_functions:
            nested_functions.append(nested_func)
            # Recursively collect nested functions from this nested function
            nested_functions.extend(
                self._collect_nested_functions_recursively(nested_func)
            )

        return nested_functions

    def _extract_decorators_from_function(
        self, func: PythonFunctionInfo, spec: FeatureSpec, bound_variables: Set[str]
    ) -> List[Detection]:
        """Extract decorators from a function signature."""
        detections: List[Detection] = []

        # Pattern to match decorators: @variable.method(...)
        decorator_pattern = r"@(\w+(?:\.\w+)*)\.(\w+)\s*\([^)]*\)"

        for match in re.finditer(decorator_pattern, func.signature, re.MULTILINE):
            obj_path = match.group(1)  # e.g., "app" or "self.app"
            method_name = match.group(2)  # e.g., "get"
            full_decorator = match.group(0)  # e.g., "@app.get('/users')"

            # Apply locator strategy filtering
            if spec.locator_strategy == LocatorStrategy.VARIABLE_BOUND:
                if obj_path not in bound_variables:
                    continue
            elif spec.locator_strategy == LocatorStrategy.DIRECT:
                # For Direct strategy, skip variable-bound patterns
                continue

            # Apply method regex filtering if specified
            if spec.construct_query and spec.construct_query.get("method_regex"):
                method_regex = spec.construct_query["method_regex"]
                if not re.fullmatch(method_regex, method_name):
                    continue

            detection = AnnotationLikeInfo(
                feature_key=spec.feature_key,
                library=spec.library,
                match_text=full_decorator,
                start_line=func.start_line,
                end_line=func.start_line,  # Decorators are usually single line
                object=obj_path,
                annotation_name=method_name,
                metadata={
                    "concept": "AnnotationLike",
                    "source": "structural_signature",
                },
            )
            detections.append(detection)

        return detections

    def _detect_call_expression(
        self, signature: PythonStructuralSignature, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> List[Detection]:
        """
        Detect function call patterns using pre-computed function_calls lists.
        """
        detections: List[Detection] = []

        # Get all functions with their calls
        all_functions = signature.functions.copy()

        # Add methods from classes
        for class_info in signature.classes:
            all_functions.extend(class_info.methods)

        # Look for function calls that match our spec
        for func in all_functions:
            for call in func.function_calls:
                # Check if this call matches any of our absolute paths
                if self._matches_call_pattern(call, spec, aliases):
                    detection = CallExpressionInfo(
                        feature_key=spec.feature_key,
                        library=spec.library,
                        match_text=call,
                        start_line=func.start_line,
                        end_line=func.end_line,
                        callee=call.split("(")[0] if "(" in call else call,
                        args_text=call.split("(", 1)[1] if "(" in call else "",
                        metadata={
                            "concept": "CallExpression",
                            "source": "structural_signature",
                        },
                    )
                    detections.append(detection)

        return detections

    def _matches_call_pattern(
        self, call: str, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> bool:
        """Check if a function call matches the feature spec pattern."""
        # Extract the function name from the call
        func_name = call.split("(")[0].strip()

        # Check against absolute paths and their aliases
        for abs_path in spec.absolute_paths:
            # Check direct match
            if abs_path in func_name:
                return True

            # Check alias match
            if abs_path in aliases:
                alias = aliases[abs_path]
                if alias in func_name:
                    return True

            # Check short name match
            short_name = abs_path.split(".")[-1]
            if short_name in func_name:
                return True

        return False

    def _detect_inheritance(
        self, signature: PythonStructuralSignature, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> List[Detection]:
        """
        Detect class inheritance patterns by parsing class signatures.
        """
        detections: List[Detection] = []

        # Check all classes
        all_classes = signature.classes.copy()

        # Add nested classes
        for class_info in signature.classes:
            all_classes.extend(class_info.nested_classes)

        for class_info in all_classes:
            base_classes = self._extract_base_classes(class_info.signature)

            for base_class in base_classes:
                if self._matches_inheritance_pattern(base_class, spec, aliases):
                    # Extract class name from signature
                    class_name = self._extract_class_name(class_info.signature)

                    detection = InheritanceInfo(
                        feature_key=spec.feature_key,
                        library=spec.library,
                        match_text=class_info.signature,
                        start_line=class_info.start_line,
                        end_line=class_info.end_line,
                        subclass=class_name,
                        superclass=base_class,
                        metadata={
                            "concept": "Inheritance",
                            "source": "structural_signature",
                        },
                    )
                    detections.append(detection)

        return detections

    def _extract_base_classes(self, class_signature: str) -> List[str]:
        """Extract base class names from a class signature."""
        # Pattern to match class inheritance: class MyClass(BaseClass, Mixin):
        pattern = r"class\s+\w+\s*\(([^)]+)\)\s*:"
        match = re.search(pattern, class_signature)

        if not match:
            return []

        # Split by comma and clean up
        base_classes = []
        for base in match.group(1).split(","):
            base = base.strip()
            if base:
                base_classes.append(base)

        return base_classes

    def _extract_class_name(self, class_signature: str) -> str:
        """Extract class name from a class signature."""
        pattern = r"class\s+(\w+)"
        match = re.search(pattern, class_signature)
        return match.group(1) if match else ""

    def _matches_inheritance_pattern(
        self, base_class: str, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> bool:
        """Check if a base class matches the feature spec pattern."""
        for abs_path in spec.absolute_paths:
            # Check direct match with short name
            short_name = abs_path.split(".")[-1]
            if base_class == short_name:
                return True

            # Check alias match
            if abs_path in aliases and base_class == aliases[abs_path]:
                return True

        return False

    def _find_bound_variables(
        self, signature: PythonStructuralSignature, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> Set[str]:
        """
        Find variables that are bound to framework constructors.
        Enhanced version that scans variable declarations and constructor calls in methods.
        """
        bound_vars: Set[str] = set()

        # Check global variables
        for var in signature.global_variables:
            if self._is_constructor_assignment(var.signature, spec, aliases):
                var_name = self._extract_variable_name(var.signature)
                if var_name:
                    bound_vars.add(var_name)

        # Check class variables
        for class_info in signature.classes:
            for var in class_info.vars:
                if self._is_constructor_assignment(var.signature, spec, aliases):
                    var_name = self._extract_variable_name(var.signature)
                    if var_name:
                        bound_vars.add(var_name)

            # Check instance variables from constructor calls in methods
            instance_vars = self._find_instance_variables_from_constructor_calls(
                class_info, spec, aliases
            )
            bound_vars.update(instance_vars)

        return bound_vars

    def _is_constructor_assignment(
        self, var_signature: str, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> bool:
        """Check if a variable signature contains a framework constructor assignment."""
        for abs_path in spec.absolute_paths:
            constructor_name = abs_path.split(".")[-1]

            # Check for direct constructor call: var = Constructor()
            if f" = {constructor_name}(" in var_signature:
                return True

            # Check for alias constructor call
            if abs_path in aliases:
                alias = aliases[abs_path]
                if f" = {alias}(" in var_signature:
                    return True

            # Check for module.constructor pattern
            module_parts = abs_path.split(".")
            if len(module_parts) >= 2:
                module_name = module_parts[0]
                if module_name in aliases:
                    module_alias = aliases[module_name]
                    pattern = f" = {module_alias}.{constructor_name}("
                    if pattern in var_signature:
                        return True

        return False

    def _extract_variable_name(self, var_signature: str) -> Optional[str]:
        """Extract variable name from a variable signature."""
        # Pattern: variable_name = ...
        pattern = r"^(\w+)\s*="
        match = re.search(pattern, var_signature.strip())
        return match.group(1) if match else None

    def _find_instance_variables_from_constructor_calls(
        self, class_info: PythonClassInfo, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> Set[str]:
        """
        Find instance variables created from constructor calls in __init__ methods.

        Scans function_calls in __init__ methods for framework constructor patterns
        and infers instance variable names using naming conventions.
        """
        instance_vars: Set[str] = set()

        # Look for __init__ methods
        for method in class_info.methods:
            if method.signature.strip().startswith("def __init__"):
                # Scan function_calls for constructor patterns
                for call in method.function_calls:
                    if self._is_constructor_call(call, spec, aliases):
                        # Infer instance variable name from constructor call
                        var_name = self._infer_instance_variable_name(
                            call, spec, aliases
                        )
                        if var_name:
                            instance_vars.add(var_name)

        return instance_vars

    def _is_constructor_call(
        self, call: str, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> bool:
        """
        Check if a function call is a framework constructor call.

        Args:
            call: Function call from function_calls list (e.g., "FastAPI()")
            spec: Feature specification with absolute_paths
            aliases: Import aliases mapping

        Returns:
            True if the call matches a framework constructor pattern
        """
        # Extract the function name from the call
        func_name = call.split("(")[0].strip()

        # Check against absolute paths
        for abs_path in spec.absolute_paths:
            constructor_name = abs_path.split(".")[-1]

            # Direct constructor name match: FastAPI()
            if func_name == constructor_name:
                return True

            # Module.constructor pattern: fastapi.FastAPI()
            if func_name.endswith(f".{constructor_name}"):
                return True

            # Check alias matches
            if abs_path in aliases:
                alias = aliases[abs_path]
                if func_name == alias:
                    return True

            # Check module alias patterns
            module_parts = abs_path.split(".")
            if len(module_parts) >= 2:
                module_name = module_parts[0]
                if module_name in aliases:
                    module_alias = aliases[module_name]
                    expected_call = f"{module_alias}.{constructor_name}"
                    if func_name == expected_call:
                        return True

        return False

    def _infer_instance_variable_name(
        self, call: str, spec: FeatureSpec, aliases: Dict[str, str]
    ) -> Optional[str]:
        """
        Infer instance variable name from a constructor call using naming conventions.

        For example:
        - FastAPI() → "app" (assuming self.app = FastAPI())
        - APIRouter() → "router" (assuming self.router = APIRouter())
        - SQLAlchemy() → "db" (assuming self.db = SQLAlchemy())

        Args:
            call: Constructor call from function_calls (e.g., "FastAPI()")
            spec: Feature specification with absolute_paths
            aliases: Import aliases mapping

        Returns:
            Inferred instance variable name (e.g., "self.app")
        """
        func_name = call.split("(")[0].strip()

        # Default naming conventions for common frameworks
        naming_conventions = {
            "FastAPI": "self.app",
            "APIRouter": "self.router",
            "Flask": "self.app",
            "Sanic": "self.app",
            "Tornado": "self.app",
            "SQLAlchemy": "self.db",
            "BaseModel": "self.model",
            "declarative_base": "self.Base",
        }

        # Check against absolute paths for constructor matching
        for abs_path in spec.absolute_paths:
            constructor_name = abs_path.split(".")[-1]

            # Direct match
            if func_name == constructor_name and constructor_name in naming_conventions:
                return naming_conventions[constructor_name]

            # Module.constructor pattern
            if (
                func_name.endswith(f".{constructor_name}")
                and constructor_name in naming_conventions
            ):
                return naming_conventions[constructor_name]

            # Alias matches
            if abs_path in aliases:
                alias = aliases[abs_path]
                if func_name == alias and constructor_name in naming_conventions:
                    return naming_conventions[constructor_name]

            # Module alias patterns
            module_parts = abs_path.split(".")
            if len(module_parts) >= 2:
                module_name = module_parts[0]
                if module_name in aliases:
                    module_alias = aliases[module_name]
                    expected_call = f"{module_alias}.{constructor_name}"
                    if (
                        func_name == expected_call
                        and constructor_name in naming_conventions
                    ):
                        return naming_conventions[constructor_name]

        # Fallback: use lowercase constructor name
        for abs_path in spec.absolute_paths:
            constructor_name = abs_path.split(".")[-1]
            if func_name == constructor_name or func_name.endswith(
                f".{constructor_name}"
            ):
                return f"self.{constructor_name.lower()}"

        return None
