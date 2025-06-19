import time
import random

class API:
    def __init__(self, memory, filesystem, resource_manager, graphics=None):
        self.memory = memory
        self.fs = filesystem
        self.resource_manager = resource_manager
        self.graphics = graphics

    # ========== Filesystem ==========

    def list_dir(self, path):
        self.resource_manager.check_cpu()
        return self.fs.list_dir(path)

    def read_file(self, path):
        self.resource_manager.check_cpu()
        return self.fs.read_file(path)

    def write_file(self, path, content):
        self.resource_manager.check_cpu()
        self.fs.write_file(path, content)

    def file_exists(self, path):
        self.resource_manager.check_cpu()
        return self.fs.file_exists(path)

    # ========== Console I/O ==========

    def print(self, *args, **kwargs):
        print("[VM Output]:", *args, **kwargs)

    def input(self, prompt=""):
        self.resource_manager.check_cpu()
        return input(f"[VM Input] {prompt}")

    # ========== Resource Checks ==========

    def check_cpu(self):
        self.resource_manager.check_cpu()

    def check_memory(self):
        self.resource_manager.check_memory(self.memory.used_kb())

    # ========== Utilities ==========

    def sleep(self, seconds):
        self.resource_manager.check_cpu()
        time.sleep(seconds)

    def rand(self, start=0, end=100):
        self.resource_manager.check_cpu()
        return random.randint(start, end)

    # ========== Memory Info ==========

    def get_memory_used(self):
        return self.memory.used_kb()

    def get_memory_limit(self):
        return self.memory.limit_kb

    # ========== Graphics API ==========

    def set_pixel(self, x, y, r, g, b):
        self.resource_manager.check_cpu()
        if self.graphics:
            self.graphics.fb.set_pixel(x, y, (r, g, b))

    def clear_screen(self, r=0, g=0, b=0):
        self.resource_manager.check_cpu()
        if self.graphics:
            self.graphics.fb.clear((r, g, b))

    def draw_rect(self, x, y, w, h, r, g, b):
        self.resource_manager.check_cpu()
        if self.graphics:
            for dx in range(w):
                for dy in range(h):
                    self.graphics.fb.set_pixel(x + dx, y + dy, (r, g, b))

    # Future: mouse, windows, multitasking...
    def get_events(self):
        self.resource_manager.check_cpu()
        if self.graphics:
            return self.graphics.get_events()
        return []
