(class_definition
  body: (block
    [
      (decorated_definition
        (decorator)* @nested_decorator
        definition: (class_definition
          name: (identifier) @nested_class_name
          superclasses: (_)? @nested_superclasses
          body: (block
            . (expression_statement
                (string) @nested_class_docstring)?
          )
        ) @nested_class_def
      ) @nested_class_with_decorators

      (class_definition
        name: (identifier) @nested_class_name
        superclasses: (_)? @nested_superclasses
        body: (block
          . (expression_statement
              (string) @nested_class_docstring)?
        )
      ) @nested_class_def
    ]
  )
)