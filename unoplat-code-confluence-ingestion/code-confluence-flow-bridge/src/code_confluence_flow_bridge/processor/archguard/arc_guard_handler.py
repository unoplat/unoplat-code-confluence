# Standard Library
import os
import subprocess
from typing import Optional

# Third Party
from temporalio import activity


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
        

    def run_scan(self) -> str:
        """
        Run ArchGuard scan on the codebase.
        
        Returns:
            str: Path to the generated JSON file
        """
        # Expand the jar path if it contains tilde
        expanded_jar_path: str = os.path.expanduser(self.jar_path)
        
        activity.logger.info(
            "Starting ArchGuard scan",
            extra={
                "language": self.language,
                "codebase": self.codebase_name
            }
        )

        # Store current directory before changing it
        original_dir: str = os.getcwd()
        
        try:
            # Change to output directory before running command
            os.chdir(self.output_path)
            activity.logger.info(f"Changed working directory to: {self.output_path}")

            command = [
                "java", "-jar", expanded_jar_path,
                "--with-function-code",
                f"--language={self.language}",
                "--output=arrow", "--output=json", 
                f"--path={self.codebase_path}",
                f"--output-dir={self.output_path}",
                f"--depth=30"
            ]
            activity.logger.info(
                "Executing command",
                extra={"command": ' '.join(command)}
            )
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1
            )
            
            if process.stdout is None:
                activity.logger.error("Failed to open subprocess stdout")
                raise RuntimeError("Failed to open subprocess stdout")
                
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    activity.logger.debug(output.strip())
                    
            _stdout, stderr = process.communicate()
            if process.returncode == 0:
                activity.logger.info("ArchGuard scan completed successfully")
                
                # Use absolute path for output file
                output_file: str = os.path.join(self.output_path, "0_codes.json")
                sanitized_name: str = self.codebase_name.replace('/', '_').replace('\\', '_').replace('//', '_')
                new_file: str = os.path.join(self.output_path, f"{sanitized_name}_codes.json")
                
                try:
                    os.rename(output_file, new_file)
                    activity.logger.debug(
                        "Renamed output file",
                        extra={
                            "old_path": output_file,
                            "new_path": new_file
                        }
                    )
                    return new_file
                except OSError as e:
                    activity.logger.error(
                        "Failed to rename output file",
                        extra={
                            "error": str(e),
                            "old_path": output_file,
                            "new_path": new_file
                        }
                    )
                    raise
            else:
                activity.logger.error(
                    "Error in ArchGuard scanning",
                    extra={
                        "error": stderr,
                        "return_code": process.returncode
                    }
                )
                raise RuntimeError(f"ArchGuard scan failed: {command} with error {stderr}")
        finally:
            # Always restore original directory
            os.chdir(original_dir)
            activity.logger.info(f"Restored working directory to: {original_dir}")

