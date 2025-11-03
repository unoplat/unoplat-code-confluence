;; NOTE: Top-level captures (@type_alias, @interface) drive range + signature detection.
;; Type aliases – only capture the alias node for range + signature extraction.
(type_alias_declaration) @type_alias

;; Interface declarations – capture the full node; consumers derive name/signature from text.
(interface_declaration) @interface
