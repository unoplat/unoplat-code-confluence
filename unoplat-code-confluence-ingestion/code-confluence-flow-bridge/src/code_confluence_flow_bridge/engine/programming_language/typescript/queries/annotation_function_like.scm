(
  (public_field_definition
    (decorator
      (call_expression
        function: (identifier) @decorator_name
      ) @decorator_call
    ) @decorator
  ) @definition
  {{ANNOTATION_NAME_PREDICATE}}
)

(
  (public_field_definition
    (decorator
      (call_expression
        function: (member_expression
          (_) @decorator_object
          (property_identifier) @decorator_method
        ) @decorator_name
      ) @decorator_call
    ) @decorator
  ) @definition
  {{ANNOTATION_METHOD_PREDICATE}}
)

(
  (class_body
    (decorator
      (call_expression
        function: (identifier) @decorator_name
      ) @decorator_call
    ) @decorator
    .
    (method_definition) @definition
  )
  {{ANNOTATION_NAME_PREDICATE}}
)

(
  (class_body
    (decorator
      (call_expression
        function: (member_expression
          (_) @decorator_object
          (property_identifier) @decorator_method
        ) @decorator_name
      ) @decorator_call
    ) @decorator
    .
    (method_definition) @definition
  )
  {{ANNOTATION_METHOD_PREDICATE}}
)
