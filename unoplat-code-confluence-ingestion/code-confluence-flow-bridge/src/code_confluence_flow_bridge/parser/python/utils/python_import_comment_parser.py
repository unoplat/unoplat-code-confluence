# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import ImportType

import re
from typing import Dict, List, Optional


# TODO: does not support comments trailing or in between imports. Should work with ruff and understand python standards regarding the same.
class PythonImportCommentParser:
    """Parser for Python import section comments"""

    # Standard comment patterns for each import type
    SECTION_PATTERNS = {ImportType.STANDARD: [r"#\s*Standard\s+Library\s*"], ImportType.EXTERNAL: [r"#\s*Third\s+Party\s*"], ImportType.INTERNAL: [r"#\s*First\s+Party\s*"], ImportType.LOCAL: [r"#\s*Local\s*"]}

    def __init__(self):
        # Compile all patterns for better performance
        self.compiled_patterns = {import_type: [re.compile(pattern, re.IGNORECASE) for pattern in patterns] for import_type, patterns in self.SECTION_PATTERNS.items()}

    def identify_section(self, comment_line: str) -> Optional[ImportType]:
        """
        Identifies the import section type from a comment line.

        Args:
            comment_line: The comment line to parse

        Returns:
            ImportType if the comment matches a section pattern, None otherwise

        Examples:
            "# Standard Library" -> ImportType.STANDARD
            "# Third Party" -> ImportType.EXTERNAL
            "# First Party" -> ImportType.INTERNAL
            "# Local" -> ImportType.LOCAL
        """
        if not comment_line.strip():
            return None

        for import_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.match(comment_line.strip()):
                    return import_type
        return None

    def _clean_import_line(self, import_str: str) -> str:
        """Clean up an import line by standardizing spaces and removing unnecessary characters.

        Args:
            import_str: Raw import string to clean

        Returns:
            Cleaned import string with standardized spacing
        """
        # Remove parentheses and any trailing/leading whitespace
        cleaned = import_str.replace("(", "").replace(")", "").strip()

        # Standardize spaces around commas
        cleaned = re.sub(r"\s*,\s*", ", ", cleaned)

        # Standardize spaces around 'as' keyword
        cleaned = re.sub(r"\s+as\s+", " as ", cleaned)

        # Standardize spaces after 'import' keyword
        cleaned = re.sub(r"import\s+", "import ", cleaned)

        # Standardize spaces after 'from' keyword
        cleaned = re.sub(r"from\s+", "from ", cleaned)

        return cleaned

    def parse_import_sections(self, file_content: str) -> Dict[ImportType, List[str]]:
        """
        Parses Python code lines into sections based on import comments.

        Args:
            file_content: String containing the Python file content

        Returns:
            Dictionary mapping ImportType to list of import lines in that section
        """
        sections: Dict[ImportType, List[str]] = {ImportType.STANDARD: [], ImportType.EXTERNAL: [], ImportType.INTERNAL: [], ImportType.LOCAL: []}

        current_section: ImportType | None = None
        current_import: List[str] = []
        in_multiline: bool = False

        # Split file content into lines and process each line
        for line in file_content.splitlines():
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if this is a section comment
            if line.startswith("#"):
                # If we were in a multiline import, save it before changing section
                if in_multiline and current_import and current_section is not None:
                    import_str = self._join_multiline_import(current_import)
                    sections[current_section].append(import_str)
                    current_import = []
                    in_multiline = False

                section_type = self.identify_section(line)
                if section_type:
                    current_section = section_type
                continue

            # Handle import lines
            if current_section is not None:
                if line.startswith("import ") or line.startswith("from "):
                    # If we were in a multiline import, save the previous one
                    if in_multiline and current_import:
                        import_str = self._join_multiline_import(current_import)
                        sections[current_section].append(import_str)
                        current_import = []

                    # Start new import
                    current_import = [line]
                    # Check if this is start of a multiline import
                    in_multiline = "(" in line and ")" not in line

                    # If it's a single line import, save it immediately
                    if not in_multiline:
                        cleaned_import = self._clean_import_line(line)
                        sections[current_section].append(cleaned_import)
                        current_import = []

                # Continue multiline import
                elif in_multiline:
                    # Remove trailing comma if present
                    cleaned_line = line.rstrip(",").strip()
                    if cleaned_line:
                        current_import.append(cleaned_line)

                    # Check if multiline import ends
                    if ")" in line:
                        import_str = self._join_multiline_import(current_import)
                        sections[current_section].append(import_str)
                        current_import = []
                        in_multiline = False

        # Handle any remaining multiline import
        if in_multiline and current_import and current_section is not None:
            import_str = self._join_multiline_import(current_import)
            sections[current_section].append(import_str)

        return sections

    def _join_multiline_import(self, import_lines: List[str]) -> str:
        """Join multiline import statements while preserving commas.

        Args:
            import_lines: List of import statement lines

        Returns:
            Single line import statement with proper formatting

        Example:
            Input: [
                'from sqlalchemy import (',
                '    Column,',
                '    Integer as Int,',
                '    String as Str,',
                '    ForeignKey',
                ')'
            ]
            Output: 'from sqlalchemy import Column, Integer as Int, String as Str, ForeignKey'
        """
        # Get the import statement prefix (everything before the first parenthesis)
        prefix = import_lines[0].split("(")[0].strip()

        # Process the imported items
        items = []
        for line in import_lines[1:]:  # Skip the first line as it's the prefix
            # Remove parentheses and extra whitespace
            line = line.replace("(", "").replace(")", "").strip()

            # Skip empty lines
            if not line:
                continue

            # If line ends with comma, remove it but remember we need one
            if line.endswith(","):
                line = line.rstrip(",")
                if line:  # Only add non-empty items
                    items.append(line)
            else:
                if line:  # Only add non-empty items
                    items.append(line)

        # Join items with commas
        joined_items = ", ".join(items)

        # Combine prefix with items
        result = f"{prefix} {joined_items}"

        return result
