
import os
import glob

class FileCounter:
    def __init__(self, directory, extension):
        self.directory = directory
        self.extension = extension

    def count_files(self):
        """Counts files with a given extension in a directory."""
        # Ensure the extension starts with a dot
        if not self.extension.startswith('.'):
            self.extension = '.' + self.extension
        
        # Create a pattern for glob to match all files with the extension
        pattern = os.path.join(self.directory, '**', '*' + self.extension)
        
        # Use glob.glob with recursive=True to find all files matching the pattern
        files = glob.glob(pattern, recursive=True)
        
        # Return the count of files
        return len(files)
