(
  (call_expression
    function: (identifier) @callee
    arguments: (arguments)? @call_args
  ) @call_expression
  {{CALLEE_PREDICATE}}
)

(
  (call_expression
    function: (member_expression) @callee
    arguments: (arguments)? @call_args
  ) @call_expression
  {{CALLEE_PREDICATE}}
)
