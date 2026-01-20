"""Tree-sitter Debug CLI - A tool for debugging tree-sitter parsing and AST analysis."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
from tree_sitter import Language, Node, Parser
from tree_sitter_language_pack import get_language

app = typer.Typer(
    name="ts-debug",
    help="CLI tool for debugging tree-sitter parsing and AST analysis",
    add_completion=False,
)
console = Console()


def serialize_node(node: Node, code_bytes: bytes) -> dict[str, Any]:
    """
    Serialize a tree-sitter Node into a JSON-serializable dictionary.

    Args:
        node: The tree-sitter Node.
        code_bytes: The original source code bytes.

    Returns:
        A dictionary with node type, start/end points, and the extracted text.
    """
    start_byte: int = node.start_byte
    end_byte: int = node.end_byte
    return {
        "type": node.type,
        "start_point": {"row": node.start_point[0], "column": node.start_point[1]},
        "end_point": {"row": node.end_point[0], "column": node.end_point[1]},
        "text": code_bytes[start_byte:end_byte].decode("utf8", errors="replace").strip(),
    }


def process_from_import_statement(
    node: Node, code_bytes: bytes, internal_prefix: str
) -> Optional[dict[str, Any]]:
    """
    Process a from-import statement AST node using next_named_sibling to walk through imports.

    Args:
        node: The from-import statement node (dotted_name node captured as @module).
        code_bytes: The original source code bytes.
        internal_prefix: Prefix to identify internal imports.

    Returns:
        A dict matching UnoplatImport structure or None if parsing fails.
    """
    source: str = code_bytes[node.start_byte : node.end_byte].decode("utf8").strip()

    usage_names: list[dict[str, Optional[str]]] = []

    current = node.next_named_sibling

    while current:
        if current.type == "aliased_import":
            name_node = current.child(0)
            alias_node = current.child(2)

            if name_node and name_node.text:
                name_text: str = name_node.text.decode("utf8").strip()
                alias_text: Optional[str] = None

                if alias_node and alias_node.text:
                    alias_text = alias_node.text.decode("utf8").strip()

                usage_names.append({"original_name": name_text, "alias": alias_text})
        elif current.type == "dotted_name":
            first_child = current.child(0)
            if first_child and first_child.text:
                name_text = first_child.text.decode("utf8").strip()
                usage_names.append({"original_name": name_text, "alias": None})

        current = current.next_named_sibling

    if not usage_names:
        return None

    return {
        "Source": source,
        "UsageName": usage_names,
        "ImportType": "internal" if source.startswith(internal_prefix) else "external",
    }


def build_ast_tree(node: Node, code_bytes: bytes, tree: Tree, max_depth: int, current_depth: int = 0) -> None:
    """Recursively build a Rich Tree from a tree-sitter AST node."""
    if max_depth > 0 and current_depth >= max_depth:
        return

    text_preview = code_bytes[node.start_byte : node.end_byte].decode("utf8", errors="replace")
    if len(text_preview) > 50:
        text_preview = text_preview[:47] + "..."
    text_preview = text_preview.replace("\n", "\\n")

    label = f"[bold cyan]{node.type}[/] [dim]({node.start_point[0]}:{node.start_point[1]})[/]"
    if node.child_count == 0:
        label += f" [green]'{text_preview}'[/]"

    branch = tree.add(label)

    for child in node.children:
        build_ast_tree(child, code_bytes, branch, max_depth, current_depth + 1)


@app.command()
def analyze_imports(
    file_path: Path = typer.Argument(..., help="Path to the Python file to analyze"),
    internal_prefix: str = typer.Option(
        "src.", help="Prefix to identify internal imports (e.g., 'src.mypackage')"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path"),
) -> None:
    """Analyze Python imports from a file and extract import information."""
    if not file_path.exists():
        rprint(f"[red]Error: File not found: {file_path}[/]")
        raise typer.Exit(1)

    code_bytes = file_path.read_bytes()

    parser: Parser = Parser()
    py_language: Language = get_language("python")
    parser.language = py_language

    tree = parser.parse(code_bytes)

    escaped_prefix = internal_prefix.replace(".", "\\\\.")
    query = py_language.query(
        f"""
        (
          import_from_statement
             module_name: (dotted_name) @module
             (#match? @module "^{escaped_prefix}")
        )
        """
    )

    matches = query.matches(tree.root_node)

    unoplat_imports: list[dict[str, Any]] = []
    for _, captures in matches:
        module_nodes = captures.get("module", [])
        for module_node in module_nodes:
            result = process_from_import_statement(module_node, code_bytes, internal_prefix)
            if result:
                unoplat_imports.append(result)

    if output:
        output.write_text(json.dumps(unoplat_imports, indent=2))
        rprint(f"[green]Import analysis written to: {output}[/]")
    else:
        rprint(Panel.fit(json.dumps(unoplat_imports, indent=2), title="Import Analysis", border_style="green"))

    rprint(f"\n[bold]Found {len(unoplat_imports)} internal imports[/]")


@app.command()
def dump_ast(
    file_path: Path = typer.Argument(..., help="Path to the source file to parse"),
    language: str = typer.Option("python", "--lang", "-l", help="Language to use for parsing"),
    max_depth: int = typer.Option(0, "--depth", "-d", help="Maximum depth to display (0 = unlimited)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path"),
) -> None:
    """Dump the full AST of a source file as a tree visualization or JSON."""
    if not file_path.exists():
        rprint(f"[red]Error: File not found: {file_path}[/]")
        raise typer.Exit(1)

    code_bytes = file_path.read_bytes()

    parser: Parser = Parser()
    lang: Language = get_language(language)
    parser.language = lang

    parsed_tree = parser.parse(code_bytes)

    if output:
        ast_dict = serialize_node_recursive(parsed_tree.root_node, code_bytes)
        output.write_text(json.dumps(ast_dict, indent=2))
        rprint(f"[green]AST written to: {output}[/]")
    else:
        tree = Tree(f"[bold magenta]AST: {file_path.name}[/]")
        build_ast_tree(parsed_tree.root_node, code_bytes, tree, max_depth)
        console.print(tree)


def serialize_node_recursive(node: Node, code_bytes: bytes) -> dict[str, Any]:
    """Recursively serialize a tree-sitter node and its children."""
    result = serialize_node(node, code_bytes)
    if node.child_count > 0:
        result["children"] = [serialize_node_recursive(child, code_bytes) for child in node.children]
    return result


@app.command()
def test_sample() -> None:
    """Run a test with sample Python code demonstrating import analysis."""
    sample_code = '''
# First Party (internal imports) - single line
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode as Node, Program as pm
from src.code_confluence_flow_bridge.models.code import Function, Class as cs
from src.code_confluence_flow_bridge.models.utils import get_all_utils
# First Party (internal imports) - multi-line using parentheses
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
    ImportedName,
    UnoplatImport as Import
)
'''
    code_bytes = sample_code.encode("utf8")

    rprint(Panel(Syntax(sample_code, "python", theme="monokai"), title="Sample Code", border_style="blue"))

    parser: Parser = Parser()
    py_language: Language = get_language("python")
    parser.language = py_language

    tree = parser.parse(code_bytes)

    internal_prefix = "src.code_confluence_flow_bridge"
    escaped_prefix = internal_prefix.replace(".", "\\\\.")
    query = py_language.query(
        f"""
        (
          import_from_statement
             module_name: (dotted_name) @module
             (#match? @module "^{escaped_prefix}")
        )
        """
    )

    matches = query.matches(tree.root_node)

    unoplat_imports: list[dict[str, Any]] = []
    for _, captures in matches:
        module_nodes = captures.get("module", [])
        for module_node in module_nodes:
            result = process_from_import_statement(module_node, code_bytes, internal_prefix)
            if result:
                unoplat_imports.append(result)

    debug_dir = Path("debug_output")
    debug_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = debug_dir / f"unoplat_imports_{timestamp}.json"
    output_file.write_text(json.dumps(unoplat_imports, indent=2))

    rprint(Panel.fit(json.dumps(unoplat_imports, indent=2), title="Parsed Imports", border_style="green"))
    rprint(f"\n[green]Output written to: {output_file}[/]")


@app.command()
def query(
    file_path: Path = typer.Argument(..., help="Path to the source file to query"),
    query_string: str = typer.Argument(..., help="Tree-sitter query pattern"),
    language: str = typer.Option("python", "--lang", "-l", help="Language to use for parsing"),
) -> None:
    """Run a custom tree-sitter query against a source file."""
    if not file_path.exists():
        rprint(f"[red]Error: File not found: {file_path}[/]")
        raise typer.Exit(1)

    code_bytes = file_path.read_bytes()

    parser: Parser = Parser()
    lang: Language = get_language(language)
    parser.language = lang

    tree = parser.parse(code_bytes)

    ts_query = lang.query(query_string)
    matches = ts_query.matches(tree.root_node)

    rprint(f"\n[bold]Found {len(matches)} matches[/]\n")

    for i, (pattern_idx, captures) in enumerate(matches):
        rprint(f"[bold cyan]Match {i + 1}[/] (pattern {pattern_idx}):")
        for name, nodes in captures.items():
            for node in nodes:
                text = code_bytes[node.start_byte : node.end_byte].decode("utf8", errors="replace")
                rprint(f"  [yellow]@{name}[/]: [green]{node.type}[/] = '{text}'")
        rprint()


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
