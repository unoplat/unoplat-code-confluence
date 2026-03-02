(export_statement
  declaration: (function_declaration
    name: (identifier) @export_name @function_name
  ) @function_definition
  {{EXPORT_NAME_PREDICATE}}
  {{FUNCTION_NAME_PREDICATE}}
) @export_statement
