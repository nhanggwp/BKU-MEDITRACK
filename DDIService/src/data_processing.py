"""
Data Processing Utilities for DDI Service
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any, Optional
from tqdm import tqdm

from .feature_extraction import smiles_to_features


def save_drug_embeddings(drug2emb: Dict[str, np.ndarray], filepath: str):
    """
    Save precomputed drug embeddings to disk
    
    Args:
        drug2emb: Dictionary mapping SMILES to feature vectors
        filepath: Path to save the embeddings
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(drug2emb, f)
    print(f"Saved {len(drug2emb)} drug embeddings to {filepath}")


def load_drug_embeddings(filepath: str) -> Dict[str, np.ndarray]:
    """
    Load precomputed drug embeddings from disk
    
    Args:
        filepath: Path to the saved embeddings
        
    Returns:
        Dictionary mapping SMILES to feature vectors
    """
    with open(filepath, 'rb') as f:
        drug2emb = pickle.load(f)
    print(f"Loaded {len(drug2emb)} drug embeddings from {filepath}")
    return drug2emb


def save_dataset_split(split: Dict[str, pd.DataFrame], filepath: str):
    """
    Save dataset split to disk
    
    Args:
        split: Dictionary containing train/valid/test DataFrames
        filepath: Path to save the split
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(split, f)
    print(f"Saved dataset split to {filepath}")


def load_dataset_split(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    Load dataset split from disk
    
    Args:
        filepath: Path to the saved split
        
    Returns:
        Dictionary containing train/valid/test DataFrames
    """
    with open(filepath, 'rb') as f:
        split = pickle.load(f)
    print(f"Loaded dataset split from {filepath}")
    return split


def cache_processed_data(
    split: Dict[str, pd.DataFrame],
    drug2emb: Dict[str, np.ndarray],
    num_labels: int,
    multilabel_mode: bool,
    emb_dim: int,
    cache_dir: str = "./cache"
):
    """
    Cache all processed data for faster subsequent runs
    
    Args:
        split: Dataset split
        drug2emb: Drug embeddings
        num_labels: Number of side effect labels
        multilabel_mode: Whether using multilabel format
        emb_dim: Embedding dimension
        cache_dir: Directory to save cached data
    """
    os.makedirs(cache_dir, exist_ok=True)
    
    # Save split and embeddings
    save_dataset_split(split, os.path.join(cache_dir, "dataset_split.pkl"))
    save_drug_embeddings(drug2emb, os.path.join(cache_dir, "drug_embeddings.pkl"))
    
    # Save metadata
    metadata = {
        "num_labels": num_labels,
        "multilabel_mode": multilabel_mode,
        "emb_dim": emb_dim
    }
    
    with open(os.path.join(cache_dir, "metadata.pkl"), 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"Cached all processed data to {cache_dir}")


def load_cached_data(cache_dir: str = "./cache") -> Tuple[Dict[str, pd.DataFrame], Dict[str, np.ndarray], Dict[str, Any]]:
    """
    Load all cached processed data
    
    Args:
        cache_dir: Directory containing cached data
        
    Returns:
        Tuple of (split, drug2emb, metadata)
    """
    split = load_dataset_split(os.path.join(cache_dir, "dataset_split.pkl"))
    drug2emb = load_drug_embeddings(os.path.join(cache_dir, "drug_embeddings.pkl"))
    
    with open(os.path.join(cache_dir, "metadata.pkl"), 'rb') as f:
        metadata = pickle.load(f)
    
    print(f"Loaded all cached data from {cache_dir}")
    return split, drug2emb, metadata


def check_cache_exists(cache_dir: str = "./cache") -> bool:
    """
    Check if cached data exists and is complete
    
    Args:
        cache_dir: Directory to check
        
    Returns:
        True if all required cache files exist
    """
    required_files = [
        "dataset_split.pkl",
        "drug_embeddings.pkl",
        "metadata.pkl"
    ]
    
    return all(os.path.exists(os.path.join(cache_dir, f)) for f in required_files)


def process_drug_pair_batch(
    drug_pairs: list,
    drug2emb: Dict[str, np.ndarray],
    n_bits: int = 512,
    verbose: bool = True
) -> Dict[str, np.ndarray]:
    """
    Process a batch of drug SMILES that might not be in the precomputed embeddings
    
    Args:
        drug_pairs: List of (drug1_smiles, drug2_smiles) tuples
        drug2emb: Existing drug embeddings
        n_bits: Number of bits for fingerprint
        verbose: Whether to show progress
        
    Returns:
        Updated drug2emb dictionary with new drugs
    """
    # Find unique drugs that need processing
    all_drugs = set()
    for d1, d2 in drug_pairs:
        all_drugs.add(d1)
        all_drugs.add(d2)
    
    new_drugs = all_drugs - set(drug2emb.keys())
    
    if new_drugs:
        if verbose:
            print(f"Processing {len(new_drugs)} new drugs...")
        
        # Process new drugs
        iterator = tqdm(new_drugs, desc="Computing features") if verbose else new_drugs
        for drug in iterator:
            drug2emb[drug] = smiles_to_features(drug, n_bits=n_bits)
    
    return drug2emb


def validate_drug_embeddings(drug2emb: Dict[str, np.ndarray], expected_dim: int) -> bool:
    """
    Validate that all drug embeddings have the expected dimension
    
    Args:
        drug2emb: Drug embeddings dictionary
        expected_dim: Expected embedding dimension
        
    Returns:
        True if all embeddings are valid
    """
    for drug, emb in drug2emb.items():
        if emb.shape[0] != expected_dim:
            print(f"Invalid embedding dimension for drug {drug}: {emb.shape[0]} != {expected_dim}")
            return False
        
        if np.any(np.isnan(emb)) or np.any(np.isinf(emb)):
            print(f"Invalid values in embedding for drug {drug}")
            return False
    
    print(f"All {len(drug2emb)} drug embeddings are valid (dim={expected_dim})")
    return True


def get_dataset_statistics(split: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Get statistics about the dataset
    
    Args:
        split: Dataset split
        
    Returns:
        Dictionary with dataset statistics
    """
    stats = {}
    
    for split_name, df in split.items():
        stats[split_name] = {
            "num_samples": len(df),
            "num_unique_drug1": df['Drug1'].nunique(),
            "num_unique_drug2": df['Drug2'].nunique(),
            "num_unique_drugs_total": len(set(df['Drug1']).union(set(df['Drug2'])))
        }
        
        # Analyze Y column
        first_y = df['Y'].iloc[0]
        if isinstance(first_y, (list, tuple, np.ndarray)):
            stats[split_name]["y_format"] = "multilabel"
            stats[split_name]["num_labels"] = len(first_y)
            # Count positive labels per sample
            y_matrix = np.stack(df['Y'].values)
            stats[split_name]["avg_positive_labels"] = y_matrix.sum(axis=1).mean()
            stats[split_name]["positive_rate_per_label"] = y_matrix.mean(axis=0)
        else:
            stats[split_name]["y_format"] = "integer"
            stats[split_name]["num_unique_labels"] = df['Y'].nunique()
            stats[split_name]["label_distribution"] = df['Y'].value_counts().to_dict()
    
    return stats


def print_dataset_info(split: Dict[str, pd.DataFrame], drug2emb: Dict[str, np.ndarray]):
    """
    Print comprehensive dataset information
    
    Args:
        split: Dataset split
        drug2emb: Drug embeddings
    """
    print("=== Dataset Information ===")
    
    stats = get_dataset_statistics(split)
    
    for split_name, split_stats in stats.items():
        print(f"\n{split_name.upper()} SET:")
        print(f"  Samples: {split_stats['num_samples']:,}")
        print(f"  Unique drugs: {split_stats['num_unique_drugs_total']:,}")
        print(f"  Drug1 unique: {split_stats['num_unique_drug1']:,}")
        print(f"  Drug2 unique: {split_stats['num_unique_drug2']:,}")
        
        if split_stats["y_format"] == "multilabel":
            print(f"  Labels format: Multi-label ({split_stats['num_labels']} labels)")
            print(f"  Avg positive labels per sample: {split_stats['avg_positive_labels']:.2f}")
        else:
            print(f"  Labels format: Integer ({split_stats['num_unique_labels']} unique)")
    
    print(f"\nDRUG EMBEDDINGS:")
    print(f"  Total drugs with embeddings: {len(drug2emb):,}")
    
    if drug2emb:
        emb_dim = len(next(iter(drug2emb.values())))
        print(f"  Embedding dimension: {emb_dim}")
        
        # Check coverage
        all_drugs = set()
        for df in split.values():
            all_drugs.update(df['Drug1'])
            all_drugs.update(df['Drug2'])
        
        coverage = len(set(drug2emb.keys()) & all_drugs) / len(all_drugs)
        print(f"  Coverage of dataset drugs: {coverage:.1%}")


def create_inference_cache(
    model_path: str,
    drug2emb: Dict[str, np.ndarray],
    metadata: Dict[str, Any],
    cache_path: str = "./models/inference_cache.pkl"
):
    """
    Create a complete inference cache with model metadata and drug embeddings
    
    Args:
        model_path: Path to the trained model
        drug2emb: Drug embeddings dictionary
        metadata: Dataset metadata (num_labels, etc.)
        cache_path: Path to save the inference cache
    """
    inference_data = {
        "model_path": model_path,
        "drug2emb": drug2emb,
        "metadata": metadata
    }
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'wb') as f:
        pickle.dump(inference_data, f)
    
    print(f"Created inference cache at {cache_path}")
    print(f"  Model: {model_path}")
    print(f"  Drug embeddings: {len(drug2emb)}")
    print(f"  Metadata: {metadata}")