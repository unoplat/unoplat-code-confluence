(class_definition
  body: (block
    [
      (decorated_definition
        (decorator)* @decorator
        definition: (function_definition
          name: (identifier) @method_name
          parameters: (_) @params
          body: (block
            . (expression_statement
                (string) @method_docstring)?
          )
        ) @method_def
      ) @method_with_decorators
      
      (function_definition
        name: (identifier) @method_name
        parameters: (_) @params
        body: (block
          . (expression_statement
              (string) @method_docstring)?
        )
      ) @method_def
    ]
  )
) 