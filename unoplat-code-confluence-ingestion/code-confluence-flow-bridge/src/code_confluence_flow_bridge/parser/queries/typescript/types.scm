;; Type aliases
(type_alias_declaration
  name: (type_identifier) @type_alias_name
  type_parameters: (type_parameters)? @type_params
  value: (_) @type_alias_value) @type_alias

;; Interface declarations - correct node type is extends_type_clause
(interface_declaration
  name: (type_identifier) @interface_name
  type_parameters: (type_parameters)? @type_params
  (extends_type_clause)? @extends
  body: (interface_body) @interface_body) @interface

;; Interface properties
(interface_body
  (property_signature
    "readonly"? @readonly
    name: [
      (property_identifier) @prop_name
      (string) @string_prop_name
      (number) @number_prop_name
    ]
    "?"? @optional
    type: (type_annotation) @prop_type) @interface_property)

;; Interface methods
(interface_body
  (method_signature
    name: (property_identifier) @method_name
    type_parameters: (type_parameters)? @type_params
    parameters: (formal_parameters) @params
    return_type: (type_annotation)? @return_type) @interface_method)

;; Interface index signatures
(interface_body
  (index_signature
    name: (identifier) @index_name
    index_type: (predefined_type) @index_type
    type: (type_annotation) @value_type) @index_signature)

;; Type parameters - corrected node types
(type_parameters
  (type_parameter
    name: (type_identifier) @type_param_name
    constraint: (constraint)? @type_constraint
    value: (default_type)? @default_type) @type_param)
