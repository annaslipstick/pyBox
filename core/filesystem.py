class File:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content

class Directory:
    def __init__(self, name):
        self.name = name
        self.entries = {}  # name -> File or Directory

class FileSystem:
    def __init__(self):
        self.root = Directory("/")

    def _resolve_path(self, path):
        """
        Resolve path into (parent_dir, final_name).
        Raises FileNotFoundError if intermediate dirs don't exist.
        """
        if not path.startswith("/"):
            raise ValueError("Only absolute paths allowed")
        parts = [p for p in path.strip("/").split("/") if p]
        current = self.root
        for part in parts[:-1]:
            if part not in current.entries or not isinstance(current.entries[part], Directory):
                raise FileNotFoundError(f"Directory '{part}' not found in path '{path}'")
            current = current.entries[part]
        return current, parts[-1] if parts else ""

    def list_dir(self, path):
        if path == "/":
            dir = self.root
        else:
            parent, name = self._resolve_path(path)
            if name not in parent.entries or not isinstance(parent.entries[name], Directory):
                raise FileNotFoundError(f"Directory '{name}' not found at '{path}'")
            dir = parent.entries[name]
        return list(dir.entries.keys())

    def read_file(self, path):
        parent, name = self._resolve_path(path)
        if name not in parent.entries or not isinstance(parent.entries[name], File):
            raise FileNotFoundError(f"File '{name}' not found at '{path}'")
        return parent.entries[name].content

    def write_file(self, path, content):
        parent, name = self._resolve_path(path)
        if name in parent.entries:
            if not isinstance(parent.entries[name], File):
                raise IsADirectoryError(f"Path '{path}' is a directory")
            parent.entries[name].content = content
        else:
            parent.entries[name] = File(name, content)

    def make_dir(self, path):
        if path == "/":
            return  # root exists
        parent, name = self._resolve_path(path)
        if name in parent.entries:
            if not isinstance(parent.entries[name], Directory):
                raise FileExistsError(f"File exists at '{path}'")
            # Directory already exists - no op
        else:
            parent.entries[name] = Directory(name)

    def file_exists(self, path):
        try:
            parent, name = self._resolve_path(path)
            return name in parent.entries
        except FileNotFoundError:
            return False

    def delete(self, path):
        parent, name = self._resolve_path(path)
        if name not in parent.entries:
            raise FileNotFoundError(f"Path '{path}' does not exist")
        del parent.entries[name]
