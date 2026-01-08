;; Detect dataclasses decorated with @dataclass (including qualified names and calls)
;; Captures:
;;   @dataclass_definition - class_definition node for the dataclass
;;   @dataclass_name       - identifier of the dataclass
(decorated_definition
  (decorator
    (_) @decorator_target
  )+
  definition: (class_definition
    name: (identifier) @dataclass_name
  ) @dataclass_definition
  (#match? @decorator_target "(?i)dataclass")
)
