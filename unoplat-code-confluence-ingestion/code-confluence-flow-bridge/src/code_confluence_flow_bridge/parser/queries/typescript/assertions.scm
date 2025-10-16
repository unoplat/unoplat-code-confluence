;; Type assertions (as keyword)
(as_expression
  expression: (_) @expression
  type: (_) @asserted_type) @type_assertion

;; Type assertions (angle bracket)
(type_assertion
  type: (_) @assertion_type
  expression: (_) @asserted_expression) @angle_assertion

;; Non-null assertions
(non_null_expression
  expression: (_) @nullable_expression
  "!" @non_null_operator) @non_null_assertion

;; Type predicates
(function_declaration
  return_type: (type_predicate
    name: (identifier) @predicate_param
    type: (_) @predicate_type)) @type_guard_function

;; Const assertions
(as_expression
  expression: (_) @const_expression
  type: (literal_type
    "const" @const_keyword)) @const_assertion

;; Satisfies operator
(satisfies_expression
  expression: (_) @expression
  type: (_) @satisfies_type) @satisfies_assertion
