"""
Model Evaluation and Metrics Utilities
"""
import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    roc_auc_score, 
    average_precision_score,
    classification_report,
    multilabel_confusion_matrix,
    hamming_loss,
    jaccard_score
)
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from .model import DeepDDIModel


class DDIEvaluator:
    """Comprehensive evaluation utilities for DDI models"""
    
    def __init__(self, model_path: str, emb_dim: int, num_labels: int, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.emb_dim = emb_dim
        self.num_labels = num_labels
        
        # Load model
        self.model = DeepDDIModel(emb_dim, num_labels).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        print(f"Loaded model from {model_path}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def evaluate_loader(self, data_loader) -> Dict[str, np.ndarray]:
        """
        Evaluate model on a data loader and return predictions and labels
        
        Args:
            data_loader: PyTorch DataLoader
            
        Returns:
            Dictionary with 'predictions', 'labels', 'logits'
        """
        all_logits = []
        all_labels = []
        
        with torch.no_grad():
            for x1, x2, y in tqdm(data_loader, desc="Evaluating"):
                x1, x2, y = x1.to(self.device), x2.to(self.device), y.to(self.device)
                logits = self.model(x1, x2)
                
                all_logits.append(logits.cpu().numpy())
                all_labels.append(y.cpu().numpy())
        
        logits = np.concatenate(all_logits, axis=0)
        labels = np.concatenate(all_labels, axis=0)
        predictions = torch.sigmoid(torch.tensor(logits)).numpy()
        
        return {
            'predictions': predictions,
            'labels': labels,
            'logits': logits
        }
    
    def compute_metrics(self, predictions: np.ndarray, labels: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
        """
        Compute comprehensive metrics for multi-label classification
        
        Args:
            predictions: Predicted probabilities (n_samples, n_labels)
            labels: True labels (n_samples, n_labels)
            threshold: Threshold for binary predictions
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # ROC AUC per label
        aucs = []
        for i in range(labels.shape[1]):
            if len(np.unique(labels[:, i])) == 2:  # both 0 and 1 present
                auc = roc_auc_score(labels[:, i], predictions[:, i])
                aucs.append(auc)
        
        metrics['auroc_macro'] = np.mean(aucs) if aucs else float('nan')
        metrics['auroc_per_label'] = aucs
        
        # Average Precision per label
        aps = []
        for i in range(labels.shape[1]):
            if len(np.unique(labels[:, i])) == 2:
                ap = average_precision_score(labels[:, i], predictions[:, i])
                aps.append(ap)
        
        metrics['auprc_macro'] = np.mean(aps) if aps else float('nan')
        metrics['auprc_per_label'] = aps
        
        # Binary predictions for other metrics
        binary_preds = (predictions > threshold).astype(int)
        
        # Hamming Loss
        metrics['hamming_loss'] = hamming_loss(labels, binary_preds)
        
        # Jaccard Score (Intersection over Union)
        metrics['jaccard_macro'] = jaccard_score(labels, binary_preds, average='macro', zero_division=0)
        metrics['jaccard_micro'] = jaccard_score(labels, binary_preds, average='micro', zero_division=0)
        metrics['jaccard_samples'] = jaccard_score(labels, binary_preds, average='samples', zero_division=0)
        
        # Coverage metrics
        metrics['coverage_error'] = self._coverage_error(labels, predictions)
        metrics['label_ranking_average_precision'] = self._label_ranking_ap(labels, predictions)
        
        # Per-sample metrics
        sample_f1_scores = []
        sample_precisions = []
        sample_recalls = []
        
        for i in range(labels.shape[0]):
            true_labels = set(np.where(labels[i] == 1)[0])
            pred_labels = set(np.where(binary_preds[i] == 1)[0])
            
            if len(pred_labels) == 0:
                precision = 1.0 if len(true_labels) == 0 else 0.0
            else:
                precision = len(true_labels & pred_labels) / len(pred_labels)
            
            if len(true_labels) == 0:
                recall = 1.0 if len(pred_labels) == 0 else 0.0
            else:
                recall = len(true_labels & pred_labels) / len(true_labels)
            
            if precision + recall == 0:
                f1 = 0.0
            else:
                f1 = 2 * precision * recall / (precision + recall)
            
            sample_f1_scores.append(f1)
            sample_precisions.append(precision)
            sample_recalls.append(recall)
        
        metrics['sample_f1_mean'] = np.mean(sample_f1_scores)
        metrics['sample_precision_mean'] = np.mean(sample_precisions)
        metrics['sample_recall_mean'] = np.mean(sample_recalls)
        
        return metrics
    
    def _coverage_error(self, y_true: np.ndarray, y_score: np.ndarray) -> float:
        """Coverage error: average number of labels to include to cover all true labels"""
        coverage = 0
        for i in range(y_true.shape[0]):
            true_labels = set(np.where(y_true[i] == 1)[0])
            if len(true_labels) == 0:
                continue
            
            # Sort predictions in descending order
            sorted_indices = np.argsort(y_score[i])[::-1]
            
            # Find how many top predictions we need to cover all true labels
            covered = set()
            for j, idx in enumerate(sorted_indices):
                if idx in true_labels:
                    covered.add(idx)
                if covered == true_labels:
                    coverage += (j + 1) / len(true_labels)
                    break
        
        return coverage / y_true.shape[0]
    
    def _label_ranking_ap(self, y_true: np.ndarray, y_score: np.ndarray) -> float:
        """Label ranking average precision"""
        ap_scores = []
        for i in range(y_true.shape[0]):
            true_labels = np.where(y_true[i] == 1)[0]
            if len(true_labels) == 0:
                continue
            
            # Sort by prediction score (descending)
            sorted_indices = np.argsort(y_score[i])[::-1]
            
            # Calculate average precision for this sample
            hits = 0
            sum_precisions = 0
            for j, idx in enumerate(sorted_indices):
                if idx in true_labels:
                    hits += 1
                    precision_at_j = hits / (j + 1)
                    sum_precisions += precision_at_j
            
            if hits > 0:
                ap_scores.append(sum_precisions / len(true_labels))
        
        return np.mean(ap_scores) if ap_scores else 0.0
    
    def generate_report(
        self, 
        train_loader=None, 
        valid_loader=None, 
        test_loader=None,
        label_names: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Generate comprehensive evaluation report
        
        Args:
            train_loader: Training data loader
            valid_loader: Validation data loader  
            test_loader: Test data loader
            label_names: Names of the labels
            save_path: Path to save the report
            
        Returns:
            Dictionary with evaluation results for each split
        """
        results = {}
        
        loaders = {
            'train': train_loader,
            'valid': valid_loader,
            'test': test_loader
        }
        
        for split_name, loader in loaders.items():
            if loader is None:
                continue
            
            print(f"\nEvaluating {split_name} set...")
            eval_results = self.evaluate_loader(loader)
            metrics = self.compute_metrics(eval_results['predictions'], eval_results['labels'])
            
            results[split_name] = {
                'metrics': metrics,
                'predictions': eval_results['predictions'],
                'labels': eval_results['labels'],
                'logits': eval_results['logits']
            }
            
            # Print key metrics
            print(f"{split_name.upper()} Results:")
            print(f"  AUROC (macro): {metrics['auroc_macro']:.4f}")
            print(f"  AUPRC (macro): {metrics['auprc_macro']:.4f}")
            print(f"  Hamming Loss: {metrics['hamming_loss']:.4f}")
            print(f"  Jaccard (macro): {metrics['jaccard_macro']:.4f}")
            print(f"  Sample F1 (mean): {metrics['sample_f1_mean']:.4f}")
        
        if save_path:
            self.save_evaluation_report(results, save_path, label_names)
        
        return results
    
    def save_evaluation_report(
        self, 
        results: Dict[str, Dict], 
        save_path: str,
        label_names: Optional[List[str]] = None
    ):
        """Save detailed evaluation report to file"""
        import json
        import os
        
        # Prepare serializable results
        serializable_results = {}
        
        for split_name, split_results in results.items():
            serializable_results[split_name] = {
                'metrics': {}
            }
            
            # Convert numpy arrays to lists for JSON serialization
            for metric_name, metric_value in split_results['metrics'].items():
                if isinstance(metric_value, np.ndarray):
                    serializable_results[split_name]['metrics'][metric_name] = metric_value.tolist()
                elif isinstance(metric_value, (np.float32, np.float64)):
                    serializable_results[split_name]['metrics'][metric_name] = float(metric_value)
                else:
                    serializable_results[split_name]['metrics'][metric_name] = metric_value
        
        # Add label names if provided
        if label_names:
            serializable_results['label_names'] = label_names
        
        # Add model info
        serializable_results['model_info'] = {
            'emb_dim': self.emb_dim,
            'num_labels': self.num_labels,
            'device': self.device,
            'total_parameters': sum(p.numel() for p in self.model.parameters())
        }
        
        # Save to JSON
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Evaluation report saved to {save_path}")
    
    def plot_metrics_comparison(
        self, 
        results: Dict[str, Dict],
        save_path: Optional[str] = None
    ):
        """Plot comparison of metrics across splits"""
        if len(results) < 2:
            print("Need at least 2 splits to compare")
            return
        
        # Key metrics to compare
        key_metrics = [
            'auroc_macro',
            'auprc_macro', 
            'hamming_loss',
            'jaccard_macro',
            'sample_f1_mean'
        ]
        
        splits = list(results.keys())
        metric_values = {metric: [] for metric in key_metrics}
        
        for split in splits:
            for metric in key_metrics:
                value = results[split]['metrics'].get(metric, 0.0)
                metric_values[metric].append(value if not np.isnan(value) else 0.0)
        
        # Create comparison plot
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, metric in enumerate(key_metrics):
            ax = axes[i]
            ax.bar(splits, metric_values[metric])
            ax.set_title(f'{metric.replace("_", " ").title()}')
            ax.set_ylabel('Score')
            
            # Add value labels on bars
            for j, v in enumerate(metric_values[metric]):
                ax.text(j, v + max(metric_values[metric]) * 0.01, f'{v:.3f}', 
                       ha='center', va='bottom')
        
        # Remove empty subplot
        axes[-1].remove()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Metrics comparison plot saved to {save_path}")
        
        plt.show()


def compare_models(model_paths: List[str], model_names: List[str], test_loader, emb_dim: int, num_labels: int):
    """
    Compare multiple models on the same test set
    
    Args:
        model_paths: List of paths to model files
        model_names: List of names for the models
        test_loader: Test data loader
        emb_dim: Embedding dimension
        num_labels: Number of labels
    """
    results = {}
    
    for model_path, model_name in zip(model_paths, model_names):
        print(f"\nEvaluating {model_name}...")
        evaluator = DDIEvaluator(model_path, emb_dim, num_labels)
        eval_results = evaluator.evaluate_loader(test_loader)
        metrics = evaluator.compute_metrics(eval_results['predictions'], eval_results['labels'])
        
        results[model_name] = metrics
        
        print(f"{model_name} Results:")
        print(f"  AUROC (macro): {metrics['auroc_macro']:.4f}")
        print(f"  AUPRC (macro): {metrics['auprc_macro']:.4f}")
        print(f"  Sample F1 (mean): {metrics['sample_f1_mean']:.4f}")
    
    # Create comparison DataFrame
    comparison_metrics = ['auroc_macro', 'auprc_macro', 'hamming_loss', 'jaccard_macro', 'sample_f1_mean']
    comparison_df = pd.DataFrame({
        model_name: [results[model_name][metric] for metric in comparison_metrics]
        for model_name in model_names
    }, index=comparison_metrics)
    
    print("\nModel Comparison:")
    print(comparison_df.round(4))
    
    return results, comparison_df