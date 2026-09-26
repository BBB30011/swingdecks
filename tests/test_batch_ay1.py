import pytest
import numpy as np

def test_permutation_logic():
    # Mock permutation test logic
    np.random.seed(42)
    sig = np.random.normal(0.01, 0.05, 100)
    ctrl = np.random.normal(0.01, 0.05, 500)
    
    diff = np.mean(sig) - np.mean(ctrl)
    
    # Pool
    pool = np.concatenate([sig, ctrl])
    
    # Permute
    diffs = []
    for _ in range(100):
        np.random.shuffle(pool)
        p_sig = pool[:100]
        p_ctrl = pool[100:]
        diffs.append(np.mean(p_sig) - np.mean(p_ctrl))
        
    p_val = np.mean(np.abs(diffs) >= np.abs(diff))
    assert 0.0 <= p_val <= 1.0

def test_bootstrap_logic():
    np.random.seed(42)
    data = np.random.normal(0.05, 0.1, 100)
    
    means = []
    for _ in range(100):
        sample = np.random.choice(data, size=100, replace=True)
        means.append(np.mean(sample))
        
    ci_lower = np.percentile(means, 2.5)
    ci_upper = np.percentile(means, 97.5)
    assert ci_lower < ci_upper
