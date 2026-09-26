import unittest
import os
import sys
import pandas as pd
from datetime import datetime, timezone
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ingestion.source_registry import SourceRegistry
from core.ingestion.market_ingestor import MarketDataIngestor
from core.ingestion.universe_builder import UniverseBuilder

class TestBatchZZZ1Ingestion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = "data/test_ingestion"
        cls.raw_dir = os.path.join(cls.test_dir, "raw")
        cls.parquet_dir = os.path.join(cls.test_dir, "market")
        cls.ca_dir = os.path.join(cls.test_dir, "corporate_actions")
        
    def setUp(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        self.ingestor = MarketDataIngestor(raw_dir=self.raw_dir, parquet_dir=self.parquet_dir, ca_dir=self.ca_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_source_registry(self):
        registry = SourceRegistry(output_path=os.path.join(self.test_dir, "registry.csv"))
        source = registry.get_source("SRC_YFINANCE_MARKET")
        self.assertIsNotNone(source)
        self.assertEqual(source["data_category"], "MARKET")
        self.assertEqual(source["survivorship_support"], "NO")
        
        registry.export_registry()
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "registry.csv")))

    def test_market_ingestor_idempotency(self):
        # Ingest a small period to be fast
        res1 = self.ingestor.ingest_ticker("BBCA", period="1mo")
        self.assertEqual(res1["status"], "SUCCESS")
        
        parquet_path = os.path.join(self.parquet_dir, "BBCA.parquet")
        self.assertTrue(os.path.exists(parquet_path))
        df1 = pd.read_parquet(parquet_path)
        rows1 = len(df1)
        
        # Run again
        res2 = self.ingestor.ingest_ticker("BBCA", period="1mo")
        self.assertEqual(res2["status"], "SUCCESS")
        
        df2 = pd.read_parquet(parquet_path)
        rows2 = len(df2)
        
        # Idempotency check: Rows should not magically double. 
        # (It might go up by 1 if a new day ticked over, but definitely not double)
        self.assertTrue(rows2 <= rows1 + 2)
        
        # Ensure UTC timezone is preserved
        self.assertTrue(str(df2['timestamp'].dt.tz) == 'UTC')
        
    def test_universe_builder(self):
        uni_path = os.path.join(self.test_dir, "universe.parquet")
        builder = UniverseBuilder(output_path=uni_path)
        builder.build_pilot_universe()
        
        self.assertTrue(os.path.exists(uni_path))
        df = pd.read_parquet(uni_path)
        self.assertTrue(len(df) > 0)
        
        # Ensure survivorship flag is set as required
        self.assertEqual(df.iloc[0]['survivorship_status'], "HIGH_RISK")

if __name__ == '__main__':
    unittest.main()
