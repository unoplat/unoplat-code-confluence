(
  (call
    function: (identifier) @callee
    arguments: (argument_list)? @call_args
  ) @call_expression
  {{CALLEE_PREDICATE}}
)

(
  (call
    function: (attribute) @callee
    arguments: (argument_list)? @call_args
  ) @call_expression
  {{CALLEE_PREDICATE}}
)
