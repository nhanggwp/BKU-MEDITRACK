#!/bin/bash
# Docker Training Script
# Trains a DDI model using Docker container

set -e

# Default values
EPOCHS=10
BATCH_SIZE=256
LEARNING_RATE=0.001
DEVICE="auto"
USE_CACHE="true"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --epochs)
      EPOCHS="$2"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --learning-rate)
      LEARNING_RATE="$2"
      shift 2
      ;;
    --device)
      DEVICE="$2"
      shift 2
      ;;
    --no-cache)
      USE_CACHE="false"
      shift
      ;;
    --gpu)
      DEVICE="cuda"
      shift
      ;;
    --cpu)
      DEVICE="cpu"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --epochs N          Number of training epochs (default: 10)"
      echo "  --batch-size N      Batch size (default: 256)"
      echo "  --learning-rate F   Learning rate (default: 0.001)"
      echo "  --device DEVICE     Device (auto|cuda|cpu, default: auto)"
      echo "  --gpu               Use GPU (shorthand for --device cuda)"
      echo "  --cpu               Use CPU (shorthand for --device cpu)"
      echo "  --no-cache          Don't use cached data"
      echo "  -h, --help          Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

echo "🚀 Starting DDI Model Training with Docker"
echo "============================================="
echo "Configuration:"
echo "  Epochs: $EPOCHS"
echo "  Batch Size: $BATCH_SIZE"
echo "  Learning Rate: $LEARNING_RATE"
echo "  Device: $DEVICE"
echo "  Use Cache: $USE_CACHE"
echo "============================================="

# Create necessary directories
mkdir -p models cache results logs

# Check if GPU support is requested and available
if [[ "$DEVICE" == "cuda" ]] || [[ "$DEVICE" == "auto" ]]; then
    if command -v nvidia-docker > /dev/null 2>&1; then
        echo "✓ NVIDIA Docker detected, using GPU support"
        DOCKER_RUNTIME="--runtime=nvidia"
        GPU_ENV="-e NVIDIA_VISIBLE_DEVICES=all"
    elif docker info 2>/dev/null | grep -q "nvidia"; then
        echo "✓ NVIDIA runtime detected, using GPU support"
        DOCKER_RUNTIME="--gpus all"
        GPU_ENV=""
    else
        echo "⚠ GPU requested but NVIDIA Docker not available, falling back to CPU"
        DEVICE="cpu"
        DOCKER_RUNTIME=""
        GPU_ENV=""
    fi
else
    DOCKER_RUNTIME=""
    GPU_ENV=""
fi

# Build the training image if it doesn't exist
echo "📦 Building training image..."
docker build --target train -t ddi-service:train .

# Run training
echo "🔥 Starting training..."
docker run \
    --rm \
    --name ddi-train \
    $DOCKER_RUNTIME \
    $GPU_ENV \
    -e DDI_EPOCHS=$EPOCHS \
    -e DDI_BATCH_SIZE=$BATCH_SIZE \
    -e DDI_LEARNING_RATE=$LEARNING_RATE \
    -e DDI_DEVICE=$DEVICE \
    -e DDI_USE_CACHE=$USE_CACHE \
    -v $(pwd)/models:/app/models \
    -v $(pwd)/cache:/app/cache \
    -v $(pwd)/results:/app/results \
    -v $(pwd)/configs:/app/configs:ro \
    ddi-service:train \
    python train_model.py \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --learning-rate $LEARNING_RATE \
    --device $DEVICE \
    $(if [[ "$USE_CACHE" == "true" ]]; then echo "--use-cache"; fi)

echo "✅ Training completed!"
echo "📁 Results saved to:"
echo "  - Model: ./models/best_ddi_model.pt"
echo "  - Cache: ./cache/"
echo "  - Logs: ./results/"