;; Lexical declarations (const, let) - 'kind' field exists but const/let are literals, not capturable node types
(lexical_declaration
  (variable_declarator
    name: [
      (identifier) @const_let_variable_name
      (object_pattern) @const_let_destructured_object
      (array_pattern) @const_let_destructured_array
    ]
    type: (type_annotation)? @const_let_variable_type
    value: (_)? @const_let_variable_value)) @const_let_variable

;; Variable declarations (var) - no fields, positional matching
(variable_declaration
  (variable_declarator
    name: [
      (identifier) @var_variable_name
      (object_pattern) @var_destructured_object
      (array_pattern) @var_destructured_array
    ]
    type: (type_annotation)? @var_variable_type
    value: (_)? @var_variable_value)) @var_variable

;; Class properties - correct node type is public_field_definition
(class_body
  (public_field_definition
    (accessibility_modifier)? @accessibility
    name: (property_identifier) @property_name
    type: (type_annotation)? @property_type
    value: (_)? @property_value) @property)

;; Parameter properties (TypeScript feature)
(formal_parameters
  (required_parameter
    (accessibility_modifier) @param_accessibility
    pattern: (identifier) @param_property_name
    type: (type_annotation)? @param_type))

;; Object property shorthand
(object
  (shorthand_property_identifier) @shorthand_property)

;; Computed property names
(object
  (pair
    key: (computed_property_name
      (expression) @computed_key)
    value: (_) @computed_value))
