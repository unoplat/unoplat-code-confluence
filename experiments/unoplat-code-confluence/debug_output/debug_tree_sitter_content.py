
import os
import json
from datetime import datetime

from unoplat_code_confluence.configuration.settings import ProgrammingLanguage
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter


def test():
    """Test to print AST structure for analysis."""
    code = """
def run_scan(self) -> str:        # Get total number of files in run_scan        self.total_files = self.file_counter.count_files()        logger.info("Starting scan...")        command = [            "java", "-jar", self.jar_path,            "--with-function-code",            f"--language={self.language}",            "--output=arrow", "--output=json",            f"--path={self.codebase_path}",            f"--output-dir={self.output_path}"        ]        logger.info(f"Command: {' '.join(command)}")                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)        while True:            output = process.stdout.readline()            logger.debug(output)            if output == '' and process.poll() is not None:                break            if output:                logger.info(output.strip())                progress_value = self.parse_progress(output, total_files=self.total_files)                logger.info(f"Progress: {progress_value}%")        stdout, stderr = process.communicate()        if process.returncode == 0:            logger.info("Scan completed successfully")            chapi_metadata_path = self.modify_output_filename("0_codes.json", f"{self.codebase_name}_codes.json")        else:            logger.error(f"Error in scanning: {stderr}")        logger.info(f"Total files scanned: {self.total_files}")        return chapi_metadata_path
"""
    
    
    parser = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)
    # Parse and get AST
    tree = parser.parser.parse(bytes(code, "utf8"))
    
    # Debug: Save AST to JSON
    debug_dir = "debug_output"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def node_to_dict(node):
        result = {
            "type": node.type,
            "text": node.text.decode('utf8') if node.text else None,
            "start_point": node.start_point,
            "end_point": node.end_point,
        }
        if len(node.children) > 0:
            result["children"] = [node_to_dict(child) for child in node.children]
        return result
        
    ast_dict = node_to_dict(tree.root_node)
    ast_file = f"{debug_dir}/function_ast_{timestamp}.json"
    with open(ast_file, "w") as f:
        json.dump(ast_dict, f, indent=2)


if __name__ == "__main__":
    test()