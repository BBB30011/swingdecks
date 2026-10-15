"""
Tests for Gate 8 Coverage Matrix and Failure Ledger Export
==========================================================
"""

import os
import tempfile
import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine


def test_gate8_coverage_matrix_and_failure_ledger_export():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    engine.load_canonical_scale_dataset(level=2)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        matrix_path = os.path.join(tmpdir, "coverage_matrix.csv")
        ledger_path = os.path.join(tmpdir, "failure_ledger.csv")
        manifest_path = os.path.join(tmpdir, "manifest.json")
        
        engine.export_coverage_matrix_csv(matrix_path)
        engine.export_failure_ledger_csv(ledger_path)
        engine.export_manifest_json(manifest_path)
        
        assert os.path.exists(matrix_path)
        assert os.path.exists(ledger_path)
        assert os.path.exists(manifest_path)
        
        with open(matrix_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) >= 23  # Header + 11 years + 12 domains
            
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) >= 4
