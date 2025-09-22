#!/usr/bin/env python3
"""
Train DDI Model Script
Convenient script to train the DDI model
"""
import argparse
import os
import sys

# Add the DDIService directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.training import main as train_main
from src.data_processing import check_cache_exists, load_cached_data, cache_processed_data
from src.training import load_and_prepare_data


def main():
    parser = argparse.ArgumentParser(description='Train DDI Model')
    
    # Training parameters
    parser.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=256, help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--hidden-dim', type=int, default=1024, help='Hidden dimension')
    parser.add_argument('--dropout', type=float, default=0.4, help='Dropout rate')
    
    # Data parameters
    parser.add_argument('--dataset', type=str, default='TWOSIDES', help='Dataset name')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--n-bits', type=int, default=512, help='Number of bits for fingerprint')
    
    # Loss parameters
    parser.add_argument('--focal-alpha', type=float, default=2, help='Focal loss alpha')
    parser.add_argument('--focal-gamma', type=float, default=2, help='Focal loss gamma')
    
    # Output parameters
    parser.add_argument('--model-path', type=str, default='./models/best_ddi_model.pt', 
                       help='Path to save the trained model')
    parser.add_argument('--cache-dir', type=str, default='./cache', 
                       help='Directory to cache processed data')
    parser.add_argument('--use-cache', action='store_true', 
                       help='Use cached data if available')
    
    # System parameters
    parser.add_argument('--num-workers', type=int, default=2, help='Number of data loader workers')
    parser.add_argument('--device', type=str, default=None, help='Device to use (cuda/cpu)')
    
    args = parser.parse_args()
    
    print("DDI Model Training")
    print("=" * 50)
    print(f"Configuration:")
    for key, value in vars(args).items():
        print(f"  {key.replace('_', '-')}: {value}")
    print("=" * 50)
    
    # Check if we should use cached data
    if args.use_cache and check_cache_exists(args.cache_dir):
        print("Loading cached data...")
        split, drug2emb, metadata = load_cached_data(args.cache_dir)
        num_labels = metadata['num_labels']
        multilabel_mode = metadata['multilabel_mode']
        emb_dim = metadata['emb_dim']
    else:
        print("Loading and processing data...")
        split, drug2emb, num_labels, multilabel_mode, emb_dim = load_and_prepare_data(
            dataset_name=args.dataset,
            random_seed=args.seed,
            n_bits=args.n_bits
        )
        
        # Cache the data for future use
        if args.cache_dir:
            cache_processed_data(split, drug2emb, num_labels, multilabel_mode, emb_dim, args.cache_dir)
    
    # Import training functions after setting up the path
    from src.training import create_data_loaders, train_model, evaluate_final_model
    
    # Create data loaders
    train_loader, valid_loader, test_loader, train_dataset = create_data_loaders(
        split, drug2emb, num_labels, multilabel_mode,
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )
    
    # Train model
    model, best_val = train_model(
        emb_dim=emb_dim,
        num_labels=num_labels,
        train_loader=train_loader,
        valid_loader=valid_loader,
        train_dataset=train_dataset,
        model_save_path=args.model_path,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        hidden_dim=args.hidden_dim,
        dropout=args.dropout,
        focal_alpha=args.focal_alpha,
        focal_gamma=args.focal_gamma,
        device=args.device
    )
    
    # Final evaluation
    print("\nFinal Evaluation:")
    evaluate_final_model(
        args.model_path,
        emb_dim,
        num_labels,
        train_loader,
        valid_loader,
        test_loader,
        device=args.device
    )
    
    print(f"\nTraining completed successfully!")
    print(f"Best validation AUROC: {best_val:.4f}")
    print(f"Model saved to: {args.model_path}")


if __name__ == "__main__":
    main()