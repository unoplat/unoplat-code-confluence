import subprocess
from pytermgui import WindowManager, Label
from utility.total_file_count import FileCounter

class ArchGuardHandler:
    def __init__(self, jar_path, language, codebase_path, output_path):
        self.jar_path = jar_path
        self.language = language
        self.codebase_path = codebase_path
        self.output_path = output_path
        self.manager = WindowManager()
        self.total_files = 0
        self.progress_label = Label(value="Progress: 0%")
        self.manager.add(self.progress_label)
        # Initialize FileCounter in the constructor
        self.file_counter = FileCounter(self.codebase_path, f'.{self.language}')

    def run_scan(self):
        # Get total number of files in run_scan
        self.total_files = self.file_counter.count_files()

        # Initialize a Label to show progress
        self.progress_label = Label(value="Progress: 0%")
        self.manager.add(self.progress_label)
        self.manager.run(in_thread=True)

        command = [
            "java", "-jar", self.jar_path,
            "--with-function-code",
            f"--language={self.language}",
            "--output=arrow", "--output=json",
            f"--path={self.codebase_path}",
            f"--output-dir={self.output_path}"
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.manager.add(self.progress_bar)
        self.manager.run(in_thread=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                progress_value = self.parse_progress(output,total_files=self.total_files)
                self.update_progress_bar(progress_value)

        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("Scan completed successfully")
        else:
            print(f"Error in scanning: {stderr}")

        self.manager.stop()

    def update_progress_label(self, value):
        self.progress_label.value = f"Progress: {value}%"
        self.manager.render()

    def parse_progress(self, output, total_files):
        # Example parsing logic, needs actual implementation based on output format
        current_file_count = output.count("analysis file:")  # This is just a placeholder
        progress_percentage = (current_file_count / total_files) * 100
        return int(progress_percentage)

    def show_progress(self):
        self.manager.add(self.progress_label)
        self.manager.run()

