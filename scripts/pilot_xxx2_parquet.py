import json
import pyarrow as pa
import pyarrow.parquet as pq
import os
from pathlib import Path

def run_parquet_pilot():
    # 1. Find an existing JSON snapshot
    data_dir = Path("data/processed")
    if not data_dir.exists():
        print("No processed data dir found. Skipping Parquet conversion.")
        return

    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print("No JSON files found in data/processed. Skipping Parquet conversion.")
        return
        
    source_file = json_files[0]
    print(f"Reading source JSON: {source_file}")
    
    with open(source_file, "r") as f:
        data = json.load(f)
        manifest = data.get("manifest", data)
        
    # JSON has "symbols", etc. We just want to extract a symbol's raw data for the pilot
    if "symbols" not in manifest or not manifest["symbols"]:
        print("Invalid manifest format. Cannot extract bars.")
        return
        
    symbol = list(manifest["symbols"].keys())[0]
    raw_filepath = manifest["symbols"][symbol]["filepath"]
    print(f"Extracting OHLCV for {symbol} from {raw_filepath}")
    
    with open(raw_filepath, "r") as f:
        bars = json.load(f)
        
    if not bars:
        print("No bars found.")
        return
        
    # 2. Convert to PyArrow Table
    # Extract columns
    timestamps = [b["timestamp"] for b in bars]
    opens = [b.get("open", 0.0) for b in bars]
    highs = [b.get("high", 0.0) for b in bars]
    lows = [b.get("low", 0.0) for b in bars]
    closes = [b.get("close", 0.0) for b in bars]
    volumes = [b.get("volume", 0) for b in bars]
    
    table = pa.Table.from_arrays([
        pa.array(timestamps),
        pa.array(opens),
        pa.array(highs),
        pa.array(lows),
        pa.array(closes),
        pa.array(volumes)
    ], names=["timestamp", "open", "high", "low", "close", "volume"])
    
    # 3. Write to Parquet
    out_dir = Path("data/parquet")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{symbol}_pilot.parquet"
    
    pq.write_table(table, out_path)
    print(f"Successfully wrote {out_path}")
    
    # 4. Read back and validate
    read_table = pq.read_table(out_path)
    
    print("\n[PARQUET VALIDATION]")
    print(f"Source JSON bars: {len(bars)}")
    print(f"Parquet table rows: {read_table.num_rows}")
    print(f"Parquet table columns: {read_table.schema.names}")
    
    assert len(bars) == read_table.num_rows, "Row count mismatch"
    assert "timestamp" in read_table.schema.names, "Schema mismatch"
    print("Validation SUCCESS: Parquet format preserves OHLCV fidelity.")

if __name__ == "__main__":
    run_parquet_pilot()
