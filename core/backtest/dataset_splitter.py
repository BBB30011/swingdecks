from core.schemas import WalkForwardSplit
from core.dataset import HistoricalDataset
from typing import Dict, List

class DatasetSplitter:
    def split(self, dataset: HistoricalDataset, split_config: WalkForwardSplit) -> Dict[str, HistoricalDataset]:
        return {
            "train": dataset.filter_period(split_config.train_start, split_config.train_end),
            "validation": dataset.filter_period(split_config.validation_start, split_config.validation_end),
            "test": dataset.filter_period(split_config.test_start, split_config.test_end)
        }
    
    def split_all(self, datasets: List[HistoricalDataset], split_config: WalkForwardSplit) -> Dict[str, List[HistoricalDataset]]:
        res = {"train": [], "validation": [], "test": []}
        for ds in datasets:
            splits = self.split(ds, split_config)
            
            if splits["train"] and splits["train"].snapshot.bars:
                res["train"].append(splits["train"])
            if splits["validation"] and splits["validation"].snapshot.bars:
                res["validation"].append(splits["validation"])
            if splits["test"] and splits["test"].snapshot.bars:
                res["test"].append(splits["test"])
                
        return res
