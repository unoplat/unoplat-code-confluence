(module
  [
    (decorated_definition
      (decorator)* @decorator
      definition: (function_definition
        name: (identifier) @func_name
        parameters: (_) @params
        body: (block
          . (expression_statement
              (string) @docstring)?
        )
      ) @function
    ) @func_with_decorators

    (function_definition
      name: (identifier) @func_name
      parameters: (_) @params
      body: (block
        . (expression_statement
            (string) @docstring)?
      )
    ) @function
  ]
) 