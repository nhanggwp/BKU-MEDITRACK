"""
Feature Extraction for Drug Molecules
Extracted from the UIT challenge notebook
"""
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors


def smiles_to_features(smiles, radius=2, n_bits=512):
    """
    Convert SMILES string to molecular features
    
    Args:
        smiles: SMILES string representation of molecule
        radius: Radius for Morgan fingerprint (default: 2)
        n_bits: Number of bits for fingerprint (default: 512)
    
    Returns:
        np.array: Combined features [fingerprint, molecular_weight, logp, tpsa]
    """
    mol = Chem.MolFromSmiles(smiles)
    fp = np.zeros((n_bits,), dtype=np.float32)
    
    if mol is not None:
        # Morgan fingerprint
        bitvec = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        AllChem.DataStructs.ConvertToNumpyArray(bitvec, fp)
        
        # Molecular descriptors
        mw = Descriptors.MolWt(mol)      # Molecular weight
        logp = Descriptors.MolLogP(mol)  # LogP (lipophilicity)
        tpsa = Descriptors.TPSA(mol)     # Topological polar surface area
    else:
        mw = logp = tpsa = 0.0
    
    return np.concatenate([fp, np.array([mw, logp, tpsa], dtype=np.float32)])


def precompute_drug_features(drug_smiles_dict, radius=2, n_bits=512):
    """
    Precompute features for multiple drugs
    
    Args:
        drug_smiles_dict: Dictionary mapping drug names/IDs to SMILES
        radius: Radius for Morgan fingerprint
        n_bits: Number of bits for fingerprint
    
    Returns:
        dict: Dictionary mapping drug names/IDs to feature vectors
    """
    drug_features = {}
    
    for drug_id, smiles in drug_smiles_dict.items():
        drug_features[drug_id] = smiles_to_features(smiles, radius, n_bits)
    
    return drug_features