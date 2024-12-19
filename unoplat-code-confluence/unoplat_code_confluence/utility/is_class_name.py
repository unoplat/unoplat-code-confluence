class IsClassName:
    @staticmethod
    def is_python_class_name(name: str) -> bool:
        """Check if a name follows Python class naming convention (CamelCase).
        
        Args:
            name: Name to check
            
        Returns:
            bool: True if name follows Python class naming convention
        """
        # Class names should:
        # 1. Start with uppercase letter
        # 2. Not contain underscores (CamelCase not snake_case)
        # 3. Not be all uppercase (to exclude constants)
        return (
            name[0].isupper() and  # Starts with uppercase
            '_' not in name and    # No underscores
            not name.isupper()     # Not all uppercase
        ) 