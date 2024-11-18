# Standard Library
import glob
import os

# Third Party
from loguru import logger


class TotalFileCount:
    def __init__(self, directory, extension):
        self.directory = directory
        self.extension = extension
        logger.info(f"FileCounter initialized with directory: {directory} and extension: {extension}")

    def count_files(self):
        logger.info("Counting files...")
        # Ensure the extension starts with a dot
        if not self.extension.startswith('.'):
            self.extension = '.' + self.extension
        
        # Create a pattern for glob to match all files with the extension
        pattern = os.path.join(self.directory, '**', '*' + self.extension)
        
        # Use glob.glob with recursive=True to find all files matching the pattern
        files = glob.glob(pattern, recursive=True)
        
        logger.info(f"Total files found: {len(files)}")
        
        # Return the count of files
        return len(files)
