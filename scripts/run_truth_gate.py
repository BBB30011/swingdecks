import time
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.evidence_truth_gate import EvidenceTruthGate

def main():
    start = time.time()
    gate = EvidenceTruthGate()
    snap = gate.scan()
    end = time.time()
    
    print(f"TRUTH GATE RUNTIME: {end - start:.2f}s")
    print(f"OVERALL STATUS: {snap.overall_status}")
    print(f"FINDINGS: {len(snap.findings)}")
    for f in snap.findings:
        print(f" - [{f.severity}] {f.category} | {f.root_cause} | {f.status}")
        print(f"   Expected: {f.expected_value} | Observed: {f.observed_value}")

if __name__ == "__main__":
    main()
