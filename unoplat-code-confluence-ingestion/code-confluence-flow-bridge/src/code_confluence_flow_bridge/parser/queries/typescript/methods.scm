;; ============================================================================
;; TypeScript Method Signature Component Captures
;;
;; This query extracts individual method signature components:
;; - decorators, accessibility, static, async, name, parameters, return type
;; - Captures components (NOT whole nodes or bodies) for signature reconstruction
;; - Supports: methods, constructors, getters/setters, abstract methods, fields
;; ============================================================================

;; ----------------------------------------------------------------------------
;; INSTANCE METHOD
;; Pattern: [decorator]* [accessibility] [static] [async] name<T>(params): ReturnType { }
;; Note: Regular methods have NO keyword token (unlike get/set)
;; ----------------------------------------------------------------------------
(class_body
  (decorator)* @method_decorator
  (method_definition
    (accessibility_modifier)? @accessibility
    "static"? @static
    "async"? @async
    name: (property_identifier) @method_name
    (type_parameters)? @type_params
    (formal_parameters) @params
    (type_annotation)? @return_type))

;; ----------------------------------------------------------------------------
;; CONSTRUCTOR
;; Pattern: [accessibility] constructor(params) { }
;; ----------------------------------------------------------------------------
(class_body
  (method_definition
    (accessibility_modifier)? @accessibility
    name: (property_identifier) @constructor_name
    (#eq? @constructor_name "constructor")
    (formal_parameters) @constructor_params))

;; ----------------------------------------------------------------------------
;; GETTER METHOD
;; Pattern: [decorator]* [accessibility] [static] get name(): ReturnType { }
;; Note: "get" is a literal token in AST
;; ----------------------------------------------------------------------------
(class_body
  (decorator)* @method_decorator
  (method_definition
    (accessibility_modifier)? @accessibility
    "static"? @static
    "get" @method_kind
    name: (property_identifier) @getter_name
    (type_annotation)? @return_type))

;; ----------------------------------------------------------------------------
;; SETTER METHOD
;; Pattern: [decorator]* [accessibility] [static] set name(param) { }
;; Note: "set" is a literal token in AST
;; ----------------------------------------------------------------------------
(class_body
  (decorator)* @method_decorator
  (method_definition
    (accessibility_modifier)? @accessibility
    "static"? @static
    "set" @method_kind
    name: (property_identifier) @setter_name
    (formal_parameters) @params))

;; ----------------------------------------------------------------------------
;; ABSTRACT METHOD SIGNATURE
;; Pattern: [accessibility] abstract name<T>(params): ReturnType;
;; ----------------------------------------------------------------------------
(class_body
  (abstract_method_signature
    (accessibility_modifier)? @accessibility
    "abstract" @abstract_keyword
    name: (property_identifier) @abstract_method_name
    (type_parameters)? @type_params
    (formal_parameters) @params
    (type_annotation)? @return_type))

;; ----------------------------------------------------------------------------
;; PARAMETER DECORATORS
;; Pattern: method(@decorator param: Type)
;; ----------------------------------------------------------------------------
(formal_parameters
  (required_parameter
    (decorator)* @param_decorator
    pattern: (identifier) @param_name))
