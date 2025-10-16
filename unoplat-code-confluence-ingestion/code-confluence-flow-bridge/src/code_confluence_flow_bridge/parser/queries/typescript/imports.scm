
;; Import statements - captures full import statement text
(import_statement) @import

;; Dynamic imports - captures import() call expressions
(call_expression
  function: (import)
  arguments: (arguments (string) @dynamic_import))
