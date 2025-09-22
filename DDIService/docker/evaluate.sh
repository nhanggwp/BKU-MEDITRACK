#!/bin/bash
# Docker Evaluation Script
# Evaluates a trained DDI model using Docker container

set -e

# Default values
MODEL_PATH="./models/best_ddi_model.pt"
OUTPUT_DIR="./results"
SPLITS="train valid test"
SAVE_PLOTS="false"
BATCH_SIZE=256

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --model-path)
      MODEL_PATH="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --splits)
      SPLITS="$2"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --save-plots)
      SAVE_PLOTS="true"
      shift
      ;;
    --test-only)
      SPLITS="test"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --model-path PATH   Path to model file (default: ./models/best_ddi_model.pt)"
      echo "  --output-dir DIR    Output directory (default: ./results)"
      echo "  --splits SPLITS     Data splits to evaluate (default: 'train valid test')"
      echo "  --batch-size N      Batch size (default: 256)"
      echo "  --save-plots        Save evaluation plots"
      echo "  --test-only         Evaluate only test split"
      echo "  -h, --help          Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

echo "📊 Starting DDI Model Evaluation with Docker"
echo "============================================="
echo "Configuration:"
echo "  Model Path: $MODEL_PATH"
echo "  Output Directory: $OUTPUT_DIR"
echo "  Data Splits: $SPLITS"
echo "  Batch Size: $BATCH_SIZE"
echo "  Save Plots: $SAVE_PLOTS"
echo "============================================="

# Check if model file exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Error: Model file not found at $MODEL_PATH"
    echo "💡 Tip: Train a model first using: ./docker/train.sh"
    exit 1
fi

# Create necessary directories
mkdir -p "$OUTPUT_DIR" cache

# Build the evaluation image if it doesn't exist
echo "📦 Building evaluation image..."
docker build --target evaluate -t ddi-service:evaluate .

# Run evaluation
echo "🔍 Starting evaluation..."
docker run \
    --rm \
    --name ddi-evaluate \
    -e DDI_MODEL_PATH="/app/models/$(basename $MODEL_PATH)" \
    -e DDI_BATCH_SIZE=$BATCH_SIZE \
    -v $(pwd)/models:/app/models:ro \
    -v $(pwd)/$OUTPUT_DIR:/app/results \
    -v $(pwd)/cache:/app/cache:ro \
    -v $(pwd)/configs:/app/configs:ro \
    ddi-service:evaluate \
    python evaluate_model.py \
    --model-path "/app/models/$(basename $MODEL_PATH)" \
    --output-dir /app/results \
    --splits $SPLITS \
    --batch-size $BATCH_SIZE \
    $(if [[ "$SAVE_PLOTS" == "true" ]]; then echo "--save-plots"; fi)

echo "✅ Evaluation completed!"
echo "📁 Results saved to: $OUTPUT_DIR"
echo ""
echo "📋 Quick Results Summary:"
if [ -f "$OUTPUT_DIR/evaluation_report.json" ]; then
    python3 -c "
import json
try:
    with open('$OUTPUT_DIR/evaluation_report.json', 'r') as f:
        results = json.load(f)
    for split, data in results.items():
        if 'metrics' in data:
            metrics = data['metrics']
            print(f'{split.upper()}:')
            print(f'  AUROC (macro): {metrics.get(\"auroc_macro\", \"N/A\"):.4f}')
            print(f'  AUPRC (macro): {metrics.get(\"auprc_macro\", \"N/A\"):.4f}')
            print(f'  Sample F1:     {metrics.get(\"sample_f1_mean\", \"N/A\"):.4f}')
            print()
except Exception as e:
    print(f'Could not parse results: {e}')
" 2>/dev/null || echo "Results saved to $OUTPUT_DIR/evaluation_report.json"
fi