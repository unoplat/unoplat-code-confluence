"""Demo module to show local variable filtering."""

# Global variables (captured at module level, not class level)
GLOBAL_VAR = "global"


class DemoClass:
    """Class to demonstrate variable capture behavior."""

    # Class variable (CAPTURED)
    CLASS_VAR = "class_level"

    def __init__(self):
        """Method with both instance vars and local vars."""

        # Instance variables (CAPTURED - these are part of class structure)
        self.instance_var = "captured"
        self.app = SomeApp()

        # Local variables (NOT CAPTURED - these are implementation details)
        local_var = "not_captured"
        temp_config = {"temporary": True}
        helper_obj = HelperClass()

        # Assignment to other objects (NOT CAPTURED)
        helper_obj.config = "not_captured"

    def regular_method(self):
        """Regular method with local variables."""

        # Instance variable (CAPTURED)
        self.method_instance_var = "captured"

        # Local variables (NOT CAPTURED)
        local_data = "not_captured"
        temp_result = process_data(local_data)
        cache = {}

        # More complex local assignments (NOT CAPTURED)
        items = [1, 2, 3]
        processed_items = [x * 2 for x in items]

        return temp_result

    @staticmethod
    def static_method():
        """Static method - no instance variables possible."""

        # Local variables in static method (NOT CAPTURED)
        static_local = "not_captured"
        config = {"static": True}

        return static_local

    def method_with_nested_function(self):
        """Method containing a nested function."""

        # Instance variable (CAPTURED)
        self.outer_instance_var = "captured"

        # Local variable in method (NOT CAPTURED)
        outer_local = "not_captured"

        def nested_function():
            # Local variables in nested function (NOT CAPTURED)
            nested_local = "not_captured"
            nested_config = {"nested": True}

            # Even fake self assignments in nested functions (NOT CAPTURED)
            fake_self = MockObject()
            fake_self.attribute = "definitely_not_captured"

            return nested_local

        # Instance variable after nested function (CAPTURED)
        self.after_nested = "captured"

        return nested_function()


def module_function():
    """Module-level function."""

    # Local variables in module function (NOT CAPTURED as class vars)
    func_local = "not_captured"
    temp_obj = TempClass()
    temp_obj.attr = "not_captured"

    return func_local
