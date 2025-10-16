;; Namespace declarations (TypeScript)
(internal_module
  name: [
    (identifier) @namespace_name
    (nested_identifier) @nested_namespace_name
  ]
  body: (statement_block) @namespace_body) @namespace

;; Module declarations
(module
  name: (string) @module_name
  body: (statement_block) @module_body) @module_declaration

;; Ambient declarations - "declare" keyword is part of the node, not capturable
(ambient_declaration
  [
    (variable_declaration) @ambient_variable
    (function_declaration) @ambient_function
    (class_declaration) @ambient_class
    (interface_declaration) @ambient_interface
    (type_alias_declaration) @ambient_type
    (internal_module) @ambient_namespace
  ]) @ambient

;; Global augmentations - Note: "global" is typically the identifier name, not a capturable keyword
(internal_module
  name: (identifier) @global
  body: (statement_block) @global_augmentation)

;; Module augmentations
(internal_module
  name: (string) @augmented_module
  body: (statement_block) @module_augmentation)
