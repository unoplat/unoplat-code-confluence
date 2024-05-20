import subprocess
from pytermgui import tim
from utility.total_file_count import FileCounter
from loguru import logger

class ArchGuardHandler:
    def __init__(self, jar_path, language, codebase_path, output_path):
        self.jar_path = jar_path
        self.language = language
        self.codebase_path = codebase_path
        self.output_path = output_path
        self.total_files = 0
        self.current_file_count = 0
        # Initialize FileCounter in the constructor
        self.file_counter = FileCounter(self.codebase_path, f'.{self.language}')

    def run_scan(self):
        # Get total number of files in run_scan
        self.total_files = self.file_counter.count_files()

        logger.info("Starting scan...")
        tim.print("[bold lightblue]Starting scan...[/]")

        command = [
            "java", "-jar", self.jar_path,
            "--with-function-code",
            f"--language={self.language}",
            "--output=arrow", "--output=json",
            f"--path={self.codebase_path}",
            f"--output-dir={self.output_path}"
        ]
        logger.info(f"Command: {' '.join(command)}")
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            #todo: print output below using logger of loguru
            logger.debug(output)
            if output == '' and process.poll() is not None:
                break
            if output:
                tim.print(output.strip())
                progress_value = self.parse_progress(output, total_files=self.total_files)
                tim.print(f"Progress: {progress_value}%")

        stdout, stderr = process.communicate()
        if process.returncode == 0:
            logger.info("Scan completed successfully")
            tim.print("Scan completed successfully")
        else:
            logger.error(f"Error in scanning: {stderr}")
            tim.print(f"Error in scanning: {stderr}")

        logger.info(f"Total files scanned: {self.total_files}")
        print(f"Total files scanned: {self.total_files}")

    def parse_progress(self, output, total_files):
        if total_files == 0:
            return 0
        else:
            if "analysis file" in output:
                self.current_file_count += 1
            progress_percentage = (self.current_file_count / total_files) * 100
            
            return int(progress_percentage)

