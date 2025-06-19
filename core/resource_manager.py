import time
import threading

class TimeoutError(Exception):
    """Raised when the CPU time limit is exceeded."""
    pass

class MemoryError(Exception):
    """Raised when the memory usage limit is exceeded."""
    pass

class ResourceManager:
    """
    Context manager enforcing CPU time and memory limits for PyBox VMs.
    
    Usage:
        resource_manager = ResourceManager(cpu_time_sec=2, memory_limit_kb=64*1024)
        with resource_manager:
            # run your VM code here
            
        Inside your guest code, call periodically:
            api.resource_manager.check_cpu()
            api.resource_manager.check_memory(api.memory.used_kb())
    """
    def __init__(self, cpu_time_sec=2, memory_limit_kb=64*1024):
        self.cpu_time_sec = cpu_time_sec
        self.memory_limit_kb = memory_limit_kb
        self._start_time = None
        self._stop_event = threading.Event()

    def __enter__(self):
        self._start_time = time.time()
        self._stop_event.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_event.set()

    def check_cpu(self):
        """
        Call this periodically from guest code to enforce CPU time limit.
        Raises TimeoutError if limit exceeded.
        """
        elapsed = time.time() - self._start_time
        if elapsed > self.cpu_time_sec:
            raise TimeoutError("CPU time limit exceeded")

    def check_memory(self, memory_used_kb):
        """
        Call this after any memory allocation attempt.
        Raises MemoryError if memory usage exceeds limit.
        """
        if memory_used_kb > self.memory_limit_kb:
            raise MemoryError(f"Memory limit exceeded: {memory_used_kb} KB used")

    # Stub hooks for future expansion:
    def check_io(self):
        pass

    def check_network(self):
        pass
