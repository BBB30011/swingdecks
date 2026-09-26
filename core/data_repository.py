import os
import json
from pathlib import Path
from datetime import datetime, timezone
from pydantic import ValidationError
from core.schemas import MarketSnapshot

class DataRepository:
    def __init__(self, base_directory: str | Path):
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, snapshot: MarketSnapshot):
        symbol = snapshot.symbol
        target_file = self.base_dir / f"{symbol}.json"
        tmp_file = self.base_dir / f"{symbol}.json.tmp"
        
        data_str = snapshot.model_dump_json()
        
        # Atomic Write
        with open(tmp_file, 'w', encoding='utf-8') as f:
            f.write(data_str)
            f.flush()
            os.fsync(f.fileno())
            
        os.replace(tmp_file, target_file)

    def load_snapshot(self, symbol: str) -> MarketSnapshot:
        target_file = self.base_dir / f"{symbol}.json"
        
        if not target_file.exists():
            raise FileNotFoundError(f"Snapshot file tidak ditemukan: {target_file}")
            
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"File JSON corrupt: {target_file}. Error: {e}")
            
        try:
            return MarketSnapshot.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Data schema invalid untuk {symbol}: {e}")

def check_data_quality(snapshot: MarketSnapshot, max_age_minutes: int) -> str:
    if not snapshot.bars:
        return "INVALID"
        
    try:
        dt = datetime.fromisoformat(snapshot.timestamp)
        if dt.tzinfo is None:
            # Asumsikan local atau system UTC jika naive
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return "INVALID"
    except Exception:
        return "INVALID"
        
    now = datetime.now(timezone.utc)
    
    diff_minutes = (now - dt).total_seconds() / 60.0
    
    if diff_minutes < -5:  # Tolerance untuk sistem dengan clock drift (waktu terdeteksi 'masa depan')
        return "INVALID"
        
    if diff_minutes <= max_age_minutes:
        return "FRESH"
    else:
        return "STALE"
