from textual.widgets import DirectoryTree

class JSONDirectoryTree(DirectoryTree):
    def filter_paths(self, paths):
        return [path for path in paths if path.is_dir() or path.suffix.lower() == '.json']