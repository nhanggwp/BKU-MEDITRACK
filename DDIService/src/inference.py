"""
DDI Model Inference Service
Handles model loading and prediction
"""
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional

# Try to import TDC, fall back to local label mapping if not available
try:
    from tdc.utils import get_label_map
    TDC_AVAILABLE = True
except ImportError:
    TDC_AVAILABLE = False
    print("Warning: TDC not available, using fallback label mapping")

from .model import DeepDDIModel
from .feature_extraction import smiles_to_features


class DDIPredictor:
    """
    Drug-Drug Interaction Predictor
    """
    
    def __init__(self, model_path: str, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.label_map = None
        self.emb_dim = 515  # 512 (fingerprint) + 3 (descriptors)
        self.num_labels = None
        self.model_path = model_path
        
    def _create_fallback_label_map(self, num_labels: int) -> Dict[int, str]:
        """Create a fallback label mapping when TDC is not available"""
        # Common drug side effects - this is a simplified mapping
        common_side_effects = [
            "Nausea", "Headache", "Dizziness", "Fatigue", "Diarrhea",
            "Abdominal Pain", "Vomiting", "Constipation", "Rash", "Fever",
            "Insomnia", "Anxiety", "Depression", "Hypertension", "Hypotension",
            "Tachycardia", "Bradycardia", "Dyspnea", "Cough", "Chest Pain",
            "Muscle Pain", "Joint Pain", "Back Pain", "Tremor", "Confusion",
            "Memory Loss", "Blurred Vision", "Dry Mouth", "Loss of Appetite",
            "Weight Gain", "Weight Loss", "Hair Loss", "Skin Discoloration",
            "Liver Dysfunction", "Kidney Dysfunction", "Anemia", "Thrombosis",
            "Bleeding", "Infection Risk", "Immune Suppression", "Allergic Reaction",
        ]
        
        label_map = {}
        for i in range(num_labels):
            if i < len(common_side_effects):
                label_map[i] = common_side_effects[i]
            else:
                label_map[i] = f"Side Effect {i+1}"
        
        return label_map
        
    def load_model(self, num_labels: int):
        """
        Load the trained DDI model
        
        Args:
            num_labels: Number of side effect labels
        """
        self.num_labels = num_labels
        self.model = DeepDDIModel(self.emb_dim, num_labels).to(self.device)
        
        # Load model weights
        state_dict = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        
        # Load label mapping
        if TDC_AVAILABLE:
            try:
                self.label_map = get_label_map(name="TWOSIDES", task="DDI", name_column="Side Effect Name")
                print("Loaded TDC TWOSIDES label mapping")
            except Exception as e:
                print(f"Warning: Could not load TDC label map: {e}")
                self.label_map = self._create_fallback_label_map(num_labels)
        else:
            self.label_map = self._create_fallback_label_map(num_labels)
    
    def predict(self, drug1_smiles: str, drug2_smiles: str, top_k: int = 5) -> List[Dict]:
        """
        Predict drug-drug interactions for two drugs
        
        Args:
            drug1_smiles: SMILES string for first drug
            drug2_smiles: SMILES string for second drug
            top_k: Number of top predictions to return
            
        Returns:
            List of dictionaries with side effect names and probabilities
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Extract features
        x1_features = smiles_to_features(drug1_smiles)
        x2_features = smiles_to_features(drug2_smiles)
        
        # Convert to tensors
        x1 = torch.tensor(x1_features).unsqueeze(0).to(self.device)
        x2 = torch.tensor(x2_features).unsqueeze(0).to(self.device)
        
        # Make prediction
        with torch.no_grad():
            logits = self.model(x1, x2)
            probs = torch.sigmoid(logits).cpu().numpy().flatten()
        
        # Get top-k predictions
        top_k_idx = probs.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_k_idx:
            side_effect_name = self.label_map.get(idx, f"Unknown Side Effect {idx}")
            results.append({
                "side_effect": side_effect_name,
                "probability": float(probs[idx]),
                "index": int(idx)
            })
        
        return results
    
    def predict_batch(self, drug_pairs: List[Tuple[str, str]], top_k: int = 5) -> List[List[Dict]]:
        """
        Predict DDI for multiple drug pairs
        
        Args:
            drug_pairs: List of tuples (drug1_smiles, drug2_smiles)
            top_k: Number of top predictions per pair
            
        Returns:
            List of prediction results for each pair
        """
        results = []
        for drug1_smiles, drug2_smiles in drug_pairs:
            pair_results = self.predict(drug1_smiles, drug2_smiles, top_k)
            results.append(pair_results)
        
        return results