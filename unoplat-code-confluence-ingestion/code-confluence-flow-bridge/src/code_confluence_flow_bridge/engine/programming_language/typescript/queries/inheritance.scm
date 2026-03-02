(
  (class_declaration
    (type_identifier) @class_name
    (class_heritage
      (extends_clause
        (identifier) @superclass
      )
    )
  ) @class_definition
  {{SUPERCLASS_PREDICATE}}
)

(
  (class_declaration
    (type_identifier) @class_name
    (class_heritage
      (extends_clause
        (member_expression) @superclass
      )
    )
  ) @class_definition
  {{SUPERCLASS_PREDICATE}}
)
