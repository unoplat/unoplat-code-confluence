;; Immediate-child nested functions – plain definition

(
  ; Parent function (we run the query against this node)
  function_definition
    body: (
      block
        ; Immediate *child* function inside the block
        (function_definition
          name: (identifier) @nested_func_name
          parameters: (_) @params
          body: (block
            . (expression_statement (string) @nested_docstring)?
          )
        ) @nested_func_def
    )
)

;; Immediate-child nested functions – decorated definition

(
  function_definition
    body: (
      block
        (decorated_definition
          (decorator)* @decorator
          definition: (
            function_definition
              name: (identifier) @nested_func_name
              parameters: (_) @params
              body: (block
                . (expression_statement (string) @nested_docstring)?
              )
          ) @nested_func_def
        ) @nested_func_with_decorators
    )
) 