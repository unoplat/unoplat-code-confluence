# Standard Library
import os
import subprocess
from typing import Optional

# Third Party
from loguru import logger


class ArchGuardHandler:
    def __init__(
        self, 
        jar_path: str, 
        language: str, 
        codebase_path: str,
        codebase_name: str, 
        output_path: str,
        extension: str
    ) -> None:
        self.jar_path = jar_path
        self.language = language
        self.codebase_path = codebase_path
        self.output_path = output_path
        self.codebase_name = codebase_name
        self.extension = extension
        # Create a contextualized logger for this instance
        self.log = logger.bind(
            codebase=codebase_name,
            language=language,
            jar_path=jar_path
        )
        self.log.debug("Initialized ArchGuardHandler with output path: {}", self.output_path)

    def run_scan(self) -> str:
        """
        Run ArchGuard scan on the codebase.
        
        Returns:
            str: Path to the generated JSON file
        """
        # Expand the jar path if it contains tilde
        expanded_jar_path: str = os.path.expanduser(self.jar_path)
        self.log.debug("Expanded jar path: {}", expanded_jar_path)
        
        self.log.info("Starting ArchGuard scan")

        # Store current directory before changing it
        original_dir: str = os.getcwd()
        
        try:
            # Change to output directory before running command
            self.log.debug("Changing working directory from {} to {}", os.getcwd(), self.output_path)
            os.chdir(self.output_path)

            self.log.debug("Using output path for ArchGuard command: {}", os.path.abspath(self.output_path))
            
            command = [
                "java", "-jar", expanded_jar_path,
                "--with-function-code",
                f"--language={self.language}",
                "--output=arrow", "--output=json", 
                f"--path={self.codebase_path}",
                f"--output-dir={self.output_path}",
                f"--depth=30"
            ]
            self.log.info("Executing command: {}", ' '.join(command))
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1
            )
            
            if process.stdout is None:
                self.log.error("Failed to open subprocess stdout")
                raise RuntimeError("Failed to open subprocess stdout")
                
            _stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.log.info("ArchGuard scan completed successfully")
                
                # Use absolute path for output file
                output_file: str = os.path.join(self.output_path, "0_codes.json")
                sanitized_name: str = self.codebase_name.replace('/', '_').replace('\\', '_').replace('//', '_')
                new_file: str = os.path.join(self.output_path, f"{sanitized_name}_codes.json")
                
                try:
                    os.rename(output_file, new_file)
                    self.log.debug("Renamed output file from {} to {}", output_file, new_file)
                    return new_file
                except OSError as e:
                    self.log.error("Failed to rename output file from {} to {}: {}", output_file, new_file, str(e))
                    raise
            else:
                self.log.error("Error in ArchGuard scanning: {} (return code: {})", stderr, process.returncode)
                raise RuntimeError(f"ArchGuard scan failed: {command} with error {stderr}")
        finally:
            # Always restore original directory
            os.chdir(original_dir)
            self.log.info("Restored working directory: {}", original_dir)
