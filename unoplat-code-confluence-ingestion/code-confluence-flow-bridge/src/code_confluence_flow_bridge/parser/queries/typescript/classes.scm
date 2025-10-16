;; ============================================================================
;; TypeScript Class Signature Component Captures
;;
;; This query extracts individual class signature components:
;; - decorators, export/default keywords, class name, type parameters, heritage
;; - Captures components (NOT whole nodes) for signature reconstruction
;; - Supports: regular classes, exported, export default, abstract, decorated
;; ============================================================================

;; ----------------------------------------------------------------------------
;; REGULAR CLASS DECLARATION
;; Pattern: [decorator]* class Name<T> extends Base implements I1, I2 { }
;; ----------------------------------------------------------------------------
(class_declaration
  (decorator)* @class_decorator
  "class" @class_keyword
  name: (type_identifier) @class_name
  (type_parameters)? @type_params
  (class_heritage)? @heritage)

;; ----------------------------------------------------------------------------
;; EXPORTED CLASS
;; Pattern: export class Name<T> extends Base implements I1, I2 { }
;; ----------------------------------------------------------------------------
(export_statement
  "export" @export_keyword
  declaration: (class_declaration
    (decorator)* @class_decorator
    "class" @class_keyword
    name: (type_identifier) @exported_class_name
    (type_parameters)? @type_params
    (class_heritage)? @heritage))

;; ----------------------------------------------------------------------------
;; EXPORT DEFAULT CLASS
;; Pattern: export default class [Name] { }
;; Note: name is optional for anonymous default classes
;; ----------------------------------------------------------------------------
(export_statement
  "export" @export_keyword
  "default" @default_keyword
  declaration: (class_declaration
    (decorator)* @class_decorator
    "class" @class_keyword
    name: (type_identifier)? @default_class_name
    (type_parameters)? @type_params
    (class_heritage)? @heritage))

;; ----------------------------------------------------------------------------
;; ABSTRACT CLASS DECLARATION
;; Pattern: [decorator]* abstract class Name<T> extends Base implements I { }
;; ----------------------------------------------------------------------------
(abstract_class_declaration
  (decorator)* @class_decorator
  "abstract" @abstract_keyword
  "class" @class_keyword
  name: (type_identifier) @abstract_class_name
  (type_parameters)? @type_params
  (class_heritage)? @heritage)

;; ----------------------------------------------------------------------------
;; HERITAGE COMPONENTS
;; ----------------------------------------------------------------------------

;; Extends clause: capture keyword and target
(class_heritage
  (extends_clause
    "extends" @extends_keyword
    value: [
      (identifier) @extends_target
      (member_expression) @extends_target
    ]))

;; Implements clause: capture keyword and each interface separately
(class_heritage
  (implements_clause
    "implements" @implements_keyword
    (type_identifier) @implements_interface))
