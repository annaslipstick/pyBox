# Virtual file system for the OS
filesystem = {}

def read_file(path):
    return filesystem.get(path, "[file not found]")

def write_file(path, content):
    filesystem[path] = content
