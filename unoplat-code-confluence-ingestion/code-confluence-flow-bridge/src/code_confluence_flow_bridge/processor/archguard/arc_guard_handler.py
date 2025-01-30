# Standard Library
import os
import subprocess

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
        activity.logger.info(
            "Starting ArchGuard scan",
            extra={
                "language": self.language,
                "codebase": self.codebase_name
            }
        )

        command = [
            "java", "-jar", self.jar_path,
            "--with-function-code",
            f"--language={self.language}",
            "--output=arrow", "--output=json", 
            f"--path={self.codebase_path}",
            f"--output-dir={self.output_path}"
        ]
        activity.logger.debug(
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
                
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            activity.logger.info("ArchGuard scan completed successfully")
            chapi_metadata_path = self.modify_output_filename(
                "0_codes.json", 
                f"{self.codebase_name}_codes.json"
            )
        else:
            activity.logger.error(
                "Error in ArchGuard scanning",
                extra={
                    "error": stderr,
                    "return_code": process.returncode
                }
            )
            raise RuntimeError(f"ArchGuard scan failed: {stderr}")

        activity.logger.info(
            "Scan statistics",
            extra={"output_path": chapi_metadata_path}
        )
        return chapi_metadata_path
        
    def modify_output_filename(self, old_filename: str, new_filename: str) -> str:
        """
        Rename the output file from default name to codebase-specific name.
        
        Args:
            old_filename: Original filename
            new_filename: New filename to use
            
        Returns:
            str: Path to renamed file
            
        Raises:
            OSError: If file rename fails
        """
        current_directory = os.getcwd()
        old_file_path = os.path.join(current_directory, old_filename)
        new_file_path = os.path.join(current_directory, new_filename)
        
        try:
            os.rename(old_file_path, new_file_path)
            activity.logger.debug(
                "Renamed output file",
                extra={
                    "old_path": old_file_path,
                    "new_path": new_file_path
                }
            )
            return new_file_path
        except OSError as e:
            activity.logger.error(
                "Failed to rename output file",
                extra={
                    "error": str(e),
                    "old_path": old_file_path,
                    "new_path": new_file_path
                }
            )
            raise

