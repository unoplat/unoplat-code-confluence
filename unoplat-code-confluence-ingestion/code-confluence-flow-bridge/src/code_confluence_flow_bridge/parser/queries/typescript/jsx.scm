;; JSX Elements
(jsx_element
  open_tag: (jsx_opening_element
    name: [
      (identifier) @component_name
      (member_expression) @namespaced_component
    ]
    attribute: (jsx_attribute)* @attributes)
  children: (_)* @children
  close_tag: (jsx_closing_element)?) @jsx_element

;; JSX Self-closing elements
(jsx_self_closing_element
  name: [
    (identifier) @self_closing_component
    (member_expression) @self_closing_namespaced
  ]
  attribute: (jsx_attribute)* @attributes) @jsx_self_closing

;; JSX Attributes
(jsx_attribute
  name: (property_identifier) @attribute_name
  value: [
    (string) @string_value
    (jsx_expression
      expression: (_) @expression_value)
  ]?) @jsx_attribute

;; JSX Spread attributes
(jsx_opening_element
  (jsx_spread_attribute
    argument: (_) @spread_value)) @spread_attribute

;; JSX Text
(jsx_element
  (jsx_text) @text_content)

;; JSX Expression containers
(jsx_expression
  "{" @open_brace
  expression: (_) @jsx_expression_content
  "}" @close_brace) @jsx_expression_container

;; JSX Fragments
(jsx_fragment
  children: (_)* @fragment_children) @fragment
