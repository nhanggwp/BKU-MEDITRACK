#!/usr/bin/env python3
"""
Evaluate DDI Model Script
Comprehensive model evaluation with detailed metrics
"""
import argparse
import os
import sys

# Add the DDIService directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(description='Evaluate DDI Model')
    
    # Model parameters
    parser.add_argument('--model-path', type=str, default='./models/best_ddi_model.pt',
                       help='Path to the trained model')
    parser.add_argument('--device', type=str, default=None,
                       help='Device to use (cuda/cpu)')
    
    # Data parameters
    parser.add_argument('--dataset', type=str, default='TWOSIDES', help='Dataset name')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--n-bits', type=int, default=512, help='Number of bits for fingerprint')
    parser.add_argument('--batch-size', type=int, default=256, help='Batch size for evaluation')
    parser.add_argument('--num-workers', type=int, default=2, help='Number of data loader workers')
    
    # Cache parameters
    parser.add_argument('--cache-dir', type=str, default='./cache',
                       help='Directory with cached processed data')
    parser.add_argument('--use-cache', action='store_true',
                       help='Use cached data if available')
    
    # Output parameters
    parser.add_argument('--output-dir', type=str, default='./evaluation_results',
                       help='Directory to save evaluation results')
    parser.add_argument('--save-plots', action='store_true',
                       help='Save evaluation plots')
    
    # Evaluation options
    parser.add_argument('--splits', nargs='+', default=['train', 'valid', 'test'],
                       choices=['train', 'valid', 'test'],
                       help='Which data splits to evaluate')
    
    args = parser.parse_args()
    
    print("DDI Model Evaluation")
    print("=" * 50)
    print(f"Configuration:")
    for key, value in vars(args).items():
        print(f"  {key.replace('_', '-')}: {value}")
    print("=" * 50)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    from src.data_processing import check_cache_exists, load_cached_data
    from src.training import load_and_prepare_data, create_data_loaders
    
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
    
    # Create data loaders
    train_loader, valid_loader, test_loader, _ = create_data_loaders(
        split, drug2emb, num_labels, multilabel_mode,
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )
    
    # Set up loaders based on requested splits
    loaders = {}
    if 'train' in args.splits:
        loaders['train'] = train_loader
    if 'valid' in args.splits:
        loaders['valid'] = valid_loader
    if 'test' in args.splits:
        loaders['test'] = test_loader
    
    # Initialize evaluator
    from src.evaluation import DDIEvaluator
    evaluator = DDIEvaluator(args.model_path, emb_dim, num_labels, device=args.device)
    
    # Get label names if possible
    label_names = None
    try:
        from tdc.utils import get_label_map
        label_map = get_label_map(name=args.dataset, task="DDI", name_column="Side Effect Name")
        label_names = [label_map[i] for i in range(num_labels)]
        print(f"Loaded {len(label_names)} label names")
    except Exception as e:
        print(f"Could not load label names: {e}")
    
    # Run comprehensive evaluation
    report_path = os.path.join(args.output_dir, "evaluation_report.json")
    results = evaluator.generate_report(
        train_loader=loaders.get('train'),
        valid_loader=loaders.get('valid'),
        test_loader=loaders.get('test'),
        label_names=label_names,
        save_path=report_path
    )
    
    # Save plots if requested
    if args.save_plots and len(results) > 1:
        plot_path = os.path.join(args.output_dir, "metrics_comparison.png")
        evaluator.plot_metrics_comparison(results, save_path=plot_path)
    
    # Print summary
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    
    for split_name, split_results in results.items():
        metrics = split_results['metrics']
        print(f"\n{split_name.upper()} SET:")
        print(f"  AUROC (macro):        {metrics['auroc_macro']:.4f}")
        print(f"  AUPRC (macro):        {metrics['auprc_macro']:.4f}")
        print(f"  Hamming Loss:         {metrics['hamming_loss']:.4f}")
        print(f"  Jaccard (macro):      {metrics['jaccard_macro']:.4f}")
        print(f"  Jaccard (micro):      {metrics['jaccard_micro']:.4f}")
        print(f"  Sample F1 (mean):     {metrics['sample_f1_mean']:.4f}")
        print(f"  Sample Precision:     {metrics['sample_precision_mean']:.4f}")
        print(f"  Sample Recall:        {metrics['sample_recall_mean']:.4f}")
        print(f"  Coverage Error:       {metrics['coverage_error']:.4f}")
        print(f"  Label Ranking AP:     {metrics['label_ranking_average_precision']:.4f}")
    
    print(f"\nDetailed results saved to: {args.output_dir}")
    print(f"Report file: {report_path}")
    
    if args.save_plots and len(results) > 1:
        print(f"Comparison plots: {plot_path}")


if __name__ == "__main__":
    main()