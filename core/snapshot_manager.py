import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

class SnapshotManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw" / "historical"
        self.processed_dir = self.data_dir / "processed"
        self.synthetic_dir = self.data_dir / "raw" / "synthetic"
        
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.synthetic_dir.mkdir(parents=True, exist_ok=True)

    def _generate_checksum(self, filepath: Path) -> str:
        if not filepath.exists():
            return ""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                sha256.update(block)
        return sha256.hexdigest()

    def save_raw_data(self, symbol: str, data: str, metadata: Dict[str, Any]) -> Path:
        """
        Saves the raw JSON data downloaded from a provider.
        """
        filename = f"{symbol}_{metadata.get('retrieved_at', '').replace(':', '')}.json"
        filepath = self.raw_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
            
        metadata["checksum_sha256"] = self._generate_checksum(filepath)
        
        # Save metadata next to it
        meta_filepath = self.raw_dir / f"{filename}.meta"
        with open(meta_filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        return filepath

    def create_snapshot(self, date_str: str, manifest: Dict[str, Any]) -> str:
        """
        Creates an immutable snapshot descriptor containing all metadata and checksums.
        """
        # Generate a stable hash of the manifest content to form the snapshot ID
        manifest_str = json.dumps(manifest, sort_keys=True)
        snap_hash = hashlib.sha256(manifest_str.encode('utf-8')).hexdigest()[:8]
        
        snapshot_id = f"IDX_DAILY_{date_str}_{snap_hash}"
        snapshot_file = self.processed_dir / f"{snapshot_id}.json"
        
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "manifest": manifest
        }
        
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=4)
            
        return snapshot_id

    def load_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        snapshot_file = self.processed_dir / f"{snapshot_id}.json"
        if not snapshot_file.exists():
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found.")
            
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            return json.load(f)
