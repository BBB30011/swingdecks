import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.real_backtest import RealBacktestEngine

def main():
    engine = RealBacktestEngine("data/raw/historical")
    result = engine.execute()
    
    print("=== REAL IDX BACKTEST ===")
    
    status = result["dataset_status"]
    print(f"Status: {status}")
    print(f"Predictive Value: {result['predictive_value']}")
    
    if status == "REAL_DATA_NOT_PROVISIONED":
        print("REAL_DATA_NOT_PROVISIONED")
        sys.exit(3)
    elif status == "REAL_DATA_INVALID":
        sys.exit(2)
    elif status == "ACCEPTED_WITH_WARNINGS":
        sys.exit(1)
    elif status == "ACCEPTED":
        sys.exit(0)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
