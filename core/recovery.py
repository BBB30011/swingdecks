from typing import Dict, Any, Optional
import os
import json
import time
from pathlib import Path

class AtomicHelper:
    @staticmethod
    def write_json(path: Path, data: Dict[str, Any]):
        tmp_file = path.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, separators=(',', ':'))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, path)

    @staticmethod
    def load_json(path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
