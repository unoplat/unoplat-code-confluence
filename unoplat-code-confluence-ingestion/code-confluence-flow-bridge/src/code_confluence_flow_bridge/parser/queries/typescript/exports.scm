;; Named exports
(export_statement
  (export_clause
    (export_specifier
      name: (identifier) @export_name
      alias: (identifier)? @export_alias)))

;; Default exports
(export_statement
  "default" @default_export
  declaration: [
    (class_declaration) @exported_class
    (function_declaration) @exported_function
    (expression) @exported_expression
  ])

;; Export declarations
(export_statement
  declaration: [
    (class_declaration
      name: (type_identifier) @exported_class_name)
    (function_declaration
      name: (identifier) @exported_function_name)
    (interface_declaration
      name: (type_identifier) @exported_interface_name)
    (enum_declaration
      name: (identifier) @exported_enum_name)
    (type_alias_declaration
      name: (type_identifier) @exported_type_name)
    (variable_declaration
      (variable_declarator
        name: (identifier) @exported_variable_name))
    (lexical_declaration
      (variable_declarator
        name: (identifier) @exported_variable_name))
  ])

;; Re-exports
(export_statement
  source: (string) @reexport_source)

;; Export all
(export_statement
  "*" @export_all
  source: (string) @export_all_source)

;; Namespace export (export * as name from "source")
(export_statement
  (namespace_export
    "*" @export_all
    (identifier) @export_alias)
  source: (string) @export_all_source)
