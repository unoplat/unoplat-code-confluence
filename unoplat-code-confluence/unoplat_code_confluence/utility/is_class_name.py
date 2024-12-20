from loguru import logger
import re

class IsClassName:
    # Class-level regex pattern for valid Python class names
    _valid_class_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    @staticmethod
    def is_python_class_name(name: str) -> bool:
        """Check if a name follows Python class naming convention (CamelCase).
        
        Args:
            name: Name to check
            
        Returns:
            bool: True if name follows Python class naming convention. 
                 Returns False for invalid inputs after logging error.
        """
        try:
            # Handle None or non-string types
            if not isinstance(name, str):
                logger.error(
                    "Invalid input type for class name check: {}\n"
                    "Expected str, got {}", 
                    name, type(name).__name__
                )
                return False
                
            # Handle empty string
            if not name:
                logger.debug("Empty string provided for class name check")
                return False
                
            # Class names should:
            # 1. Start with uppercase letter
            # 2. Not contain underscores (CamelCase not snake_case)
            # 3. Not be all uppercase (to exclude constants)
            # 4. Allow single uppercase letter (e.g., A, B, T for generics)
            # 5. Not contain special characters
            
            # Handle single character case
            if len(name) == 1:
                return name.isupper()
                
            # Check if name matches valid pattern and is not all uppercase
            return bool(
                IsClassName._valid_class_pattern.match(name) and
                not name.isupper()
            )
            
        except Exception as e:
            logger.error(
                "Unexpected error checking class name: {}\n"
                "Input: {}\n"
                "Error: {}", 
                name, type(name).__name__, str(e)
            )
            return False 