import os
import csv
from datetime import datetime, timedelta
import random

# Fixed seed for deterministic behavior
random.seed(42)

symbols = ["BBCA", "BMRI", "BBNI", "TLKM", "ASII", "IHSG"]

start_date = datetime(2020, 1, 1)

def generate_regime_price(i, current_price, regime):
    if regime == "BULL":
        return current_price * (1 + random.uniform(-0.01, 0.015))
    elif regime == "SIDEWAYS":
        return current_price * (1 + random.uniform(-0.01, 0.01))
    elif regime == "BEAR":
        return current_price * (1 + random.uniform(-0.015, 0.01))
    else: # RECOVERY
        return current_price * (1 + random.uniform(-0.01, 0.02))

def generate_csv(symbol, filename, bars=250, drop_idx=None, dup_idx=None, nan_idx=None, future_idx=None, negative_price=None):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        
        current_price = 1000.0 if symbol != "IHSG" else 5000.0
        current_date = start_date
        
        for i in range(bars):
            # Deterministic regime: 
            # 0-60 BULL, 61-120 SIDEWAYS, 121-180 BEAR, 181+ RECOVERY
            regime = "BULL"
            if 60 <= i < 120: regime = "SIDEWAYS"
            elif 120 <= i < 180: regime = "BEAR"
            elif i >= 180: regime = "RECOVERY"
            
            # Skip weekend
            while current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                
            open_p = current_price
            close_p = generate_regime_price(i, current_price, regime)
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
            vol = random.randint(1000, 100000)
            
            if negative_price == i:
                close_p = -100.0
                
            row_date = current_date.strftime("%Y-%m-%d")
            if future_idx == i:
                row_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
                
            row = [row_date, round(open_p, 2), round(high_p, 2), round(low_p, 2), round(close_p, 2), vol]
            
            if nan_idx == i:
                row[4] = ""
                
            if drop_idx != i:
                writer.writerow(row)
                
            if dup_idx == i:
                writer.writerow(row)
                
            current_price = close_p
            current_date += timedelta(days=1)

os.makedirs("tests/fixtures/historical", exist_ok=True)
for sym in symbols:
    generate_csv(sym, f"tests/fixtures/historical/{sym}.csv")

# Create edge case files
generate_csv("BBCA_MISSING_ROW", "tests/fixtures/historical/BBCA_MISSING_ROW.csv", drop_idx=100)
generate_csv("BBCA_DUP_ROW", "tests/fixtures/historical/BBCA_DUP_ROW.csv", dup_idx=100)
generate_csv("BBCA_NAN", "tests/fixtures/historical/BBCA_NAN.csv", nan_idx=100)
generate_csv("BBCA_FUTURE", "tests/fixtures/historical/BBCA_FUTURE.csv", future_idx=100)
generate_csv("BBCA_NEGATIVE", "tests/fixtures/historical/BBCA_NEGATIVE.csv", negative_price=100)
generate_csv("BBCA_SHORT", "tests/fixtures/historical/BBCA_SHORT.csv", bars=150)
