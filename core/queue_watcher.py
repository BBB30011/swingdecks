from pathlib import Path
from typing import Callable, List
import time

class QueueWatcher:
    def __init__(self, queue_dir: str = "queue"):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
    def poll(self) -> List[Path]:
        """
        Deterministic polling fallback that safely ignores .tmp files
        and returns only fully written .json files.
        """
        return sorted(self.queue_dir.glob("*.json"))
        
    def watch(self, callback: Callable[[Path], None], interval_sec: float = 1.0):
        """
        Interface for watching queue.
        Uses polling by default.
        """
        seen = set()
        while True:
            current_files = self.poll()
            for file_path in current_files:
                if file_path not in seen:
                    seen.add(file_path)
                    callback(file_path)
            time.sleep(interval_sec)
