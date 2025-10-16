;; Enum declarations
(enum_declaration
  "const"? @const_modifier
  name: (identifier) @enum_name
  body: (enum_body) @enum_body) @enum

;; Enum members
(enum_body
  (enum_assignment
    name: (property_identifier) @enum_member_name
    value: (_)? @enum_member_value) @enum_member)

;; Exported enums
(export_statement
  declaration: (enum_declaration
    "const"? @const_modifier
    name: (identifier) @exported_enum_name
    body: (enum_body) @enum_body) @exported_enum)

;; String enum members
(enum_body
  (enum_assignment
    name: (property_identifier) @string_enum_member
    value: (string) @string_value))

;; Numeric enum members
(enum_body
  (enum_assignment
    name: (property_identifier) @numeric_enum_member
    value: (number) @numeric_value))

;; Computed enum members
(enum_body
  (enum_assignment
    name: (property_identifier) @computed_enum_member
    value: (binary_expression) @computed_value))
