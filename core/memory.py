class MemoryError(Exception):
    pass

class Memory:
    def __init__(self, limit_kb=64*1024):
        """
        Initialize memory manager.
        
        Args:
            limit_kb (int): Maximum allowed memory usage in kilobytes.
        """
        self.limit_kb = limit_kb
        self.used_kb = 0

    def allocate(self, size_kb):
        """
        Simulate allocation of memory.
        
        Args:
            size_kb (int): Size in kilobytes to allocate.
            
        Raises:
            MemoryError: If allocation exceeds the limit.
        """
        if self.used_kb + size_kb > self.limit_kb:
            raise MemoryError(f"Memory limit exceeded: trying to allocate {size_kb} KB, "
                              f"but {self.used_kb}/{self.limit_kb} KB already used.")
        self.used_kb += size_kb

    def free(self, size_kb):
        """
        Simulate freeing memory.
        
        Args:
            size_kb (int): Size in kilobytes to free.
        """
        self.used_kb = max(0, self.used_kb - size_kb)

    def used_kb(self):
        """Return currently used memory in KB."""
        return self.used_kb

    def get_limit_kb(self):
        """Return memory limit in KB."""
        return self.limit_kb
