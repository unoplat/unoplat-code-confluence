(module
  [
    (decorated_definition
      (decorator)* @decorator
      definition: (class_definition
        name: (identifier) @class_name
        superclasses: (_)? @superclasses
        body: (block
          . (expression_statement
              (string) @class_docstring)?
        )
      ) @class_def
    ) @class_with_decorators

    (class_definition
      name: (identifier) @class_name
      superclasses: (_)? @superclasses
      body: (block
        . (expression_statement
            (string) @class_docstring)?
      )
    ) @class_def
  ]
) 