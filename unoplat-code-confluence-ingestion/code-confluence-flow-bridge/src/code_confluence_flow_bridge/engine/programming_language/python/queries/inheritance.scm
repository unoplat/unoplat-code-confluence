(
  (class_definition
    name: (identifier) @class_name
    superclasses: (argument_list
      (identifier) @superclass
    )
  ) @class_definition
  {{SUPERCLASS_PREDICATE}}
)

(
  (class_definition
    name: (identifier) @class_name
    superclasses: (argument_list
      (attribute) @superclass
    )
  ) @class_definition
  {{SUPERCLASS_PREDICATE}}
)
