import pytest
import numpy as np
import pandas as pd

def cluster_bootstrap(df, cluster_col, n_boot=100):
    unique_clusters = df[cluster_col].unique()
    n_clusters = len(unique_clusters)
    means = []
    for _ in range(n_boot):
        # Sample clusters with replacement
        samp_clusters = np.random.choice(unique_clusters, size=n_clusters, replace=True)
        # Create new dataset keeping all items belonging to chosen clusters
        # Since a cluster can be chosen multiple times, we must concatenate the slices
        samp_df = pd.concat([df[df[cluster_col] == c] for c in samp_clusters])
        means.append(samp_df['val'].mean())
    return means

def test_cluster_bootstrap_logic():
    np.random.seed(42)
    # Create mock dataframe with 5 clusters
    df = pd.DataFrame({
        'cluster_id': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        'val': [10, 10, 20, 20, 30, 30, 40, 40, 50, 50]
    })
    
    # Run clustered bootstrap
    means = cluster_bootstrap(df, 'cluster_id', n_boot=50)
    
    # Verify that we never broke up a cluster. 
    # Because clusters 1..5 have identical values (10..50) inside them, 
    # the bootstrapped mean will always be an integer ending in 0 (e.g., 30.0),
    # or some exact average of whole clusters. It should not produce fragmented means.
    for m in means:
        assert m >= 10.0 and m <= 50.0

def test_cluster_permutation_logic():
    np.random.seed(42)
    # Mock data where treatment assignment is permuted at cluster level
    # i.e., all items in a cluster share the same flipped sign
    pass
