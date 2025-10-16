;; ============================================================================
;; TypeScript Function Signature Component Captures
;;
;; This query extracts individual signature components for all function types:
;; - async keyword, function name, type parameters, parameters, return type
;; - Supports: function declarations, arrow functions, function expressions, generators
;; ============================================================================

;; ----------------------------------------------------------------------------
;; FUNCTION DECLARATIONS
;; Pattern: [async] function name<T>(params): ReturnType { }
;; ----------------------------------------------------------------------------
(function_declaration
  "async"? @async
  (identifier) @function_name
  (type_parameters)? @type_params
  (formal_parameters) @params
  (type_annotation)? @return_type)

;; ----------------------------------------------------------------------------
;; ARROW FUNCTIONS (const/let)
;; Pattern: const name [: Type] = [async] <T>(params) [: ReturnType] => body
;; ----------------------------------------------------------------------------
(lexical_declaration
  ["const" "let"] @binding_keyword
  (variable_declarator
    name: (identifier) @arrow_name
    (type_annotation)? @binding_type
    value: (arrow_function
      "async"? @async
      (type_parameters)? @type_params
      (formal_parameters) @params
      (type_annotation)? @return_type)))

;; ----------------------------------------------------------------------------
;; ARROW FUNCTIONS (var)
;; Pattern: var name [: Type] = [async] <T>(params) [: ReturnType] => body
;; ----------------------------------------------------------------------------
(variable_declaration
  "var" @binding_keyword
  (variable_declarator
    name: (identifier) @arrow_name
    (type_annotation)? @binding_type
    value: (arrow_function
      "async"? @async
      (type_parameters)? @type_params
      (formal_parameters) @params
      (type_annotation)? @return_type)))

;; ----------------------------------------------------------------------------
;; FUNCTION EXPRESSIONS (const/let)
;; Pattern: const name [: Type] = [async] function [innerName]<T>(params): ReturnType { }
;; ----------------------------------------------------------------------------
(lexical_declaration
  ["const" "let"] @binding_keyword
  (variable_declarator
    name: (identifier) @func_expr_name
    (type_annotation)? @binding_type
    value: (function_expression
      "async"? @async
      name: (identifier)? @inner_function_name
      (type_parameters)? @type_params
      (formal_parameters) @params
      (type_annotation)? @return_type)))

;; ----------------------------------------------------------------------------
;; FUNCTION EXPRESSIONS (var)
;; Pattern: var name [: Type] = [async] function [innerName]<T>(params): ReturnType { }
;; ----------------------------------------------------------------------------
(variable_declaration
  "var" @binding_keyword
  (variable_declarator
    name: (identifier) @func_expr_name
    (type_annotation)? @binding_type
    value: (function_expression
      "async"? @async
      name: (identifier)? @inner_function_name
      (type_parameters)? @type_params
      (formal_parameters) @params
      (type_annotation)? @return_type)))

;; ----------------------------------------------------------------------------
;; GENERATOR FUNCTIONS
;; Pattern: [async] function * name<T>(params): ReturnType { }
;; Note: The "*" token is captured as generator marker
;; ----------------------------------------------------------------------------
(generator_function_declaration
  "async"? @async
  "*" @generator
  (identifier) @generator_name
  (type_parameters)? @type_params
  (formal_parameters) @params
  (type_annotation)? @return_type)
