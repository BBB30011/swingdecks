from typing import List, Dict, Any
from core.dataset import HistoricalDataset
from core.schemas import WalkForwardSplit, MarketSnapshot

class WalkForwardValidator:
    def __init__(
        self,
        backtest_engine,
        splitter,
        performance_validator
    ):
        self.backtest_engine = backtest_engine
        self.splitter = splitter
        self.performance_validator = performance_validator

    def run(self, dataset: List[MarketSnapshot], split_config: WalkForwardSplit) -> Dict[str, Any]:
        
        # 1. Dataset masuk & dibungkus ke HistoricalDataset
        h_datasets = [HistoricalDataset(snap) for snap in dataset]
        
        # 2. Dataset dibagi: TRAIN, VALIDATION, TEST
        splits = self.splitter.split_all(h_datasets, split_config)
        
        train_snaps = [ds.snapshot for ds in splits["train"]]
        val_snaps = [ds.snapshot for ds in splits["validation"]]
        test_snaps = [ds.snapshot for ds in splits["test"]]
        
        # 3. Masing-masing dijalankan menggunakan BacktestEngine existing
        # Jika period test kosong, return INVALID_SPLIT immediately
        if not train_snaps or not test_snaps:
            return {
                "train": None,
                "validation": None,
                "test": None,
                "comparison": {
                    "status": "INVALID_SPLIT", 
                    "degradation": {}, 
                    "warnings": ["Empty test or train period"]
                }
            }
        
        res_train = self.backtest_engine.run(train_snaps)
        res_val = self.backtest_engine.run(val_snaps) if val_snaps else None
        res_test = self.backtest_engine.run(test_snaps)
        
        # 4 & 5. Ambil metrik dan bandingkan hasil
        comp = self.performance_validator.compare(res_train, res_val, res_test)
        
        return {
            "train": res_train,
            "validation": res_val,
            "test": res_test,
            "comparison": comp
        }
