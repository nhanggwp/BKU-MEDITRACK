# DDI Service - Drug-Drug Interaction Prediction

A deep learning service for predicting drug-drug interactions using molecular fingerprints and neural networks.

## Overview

This service provides:
- **Deep Learning Model**: Multi-label classification with 1317 side effect labels
- **REST API**: FastAPI service running on port 8001
- **Docker Support**: Complete containerized workflows
- **Training Pipeline**: Full model training and evaluation

## Docker Setup

### 1. Start and Play with Trained Model

Start the API service with the pre-trained model:

```bash
# Using Docker Compose
docker-compose up -d ddi-api

# Or using workflow script
./docker/workflow.sh serve

# API available at: http://localhost:8001/docs
# Health check: http://localhost:8001/health
```

Test the API:
```bash
curl -X POST "http://localhost:8001/predict" \
-H "Content-Type: application/json" \
-d '{
  "drug1_smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
  "drug2_smiles": "CC1=CC=C(C=C1)C(=O)C2=CC=CC=C2",
  "top_k": 5
}'
```

### 2. How to Train

Train a new model with your data:

```bash
# Complete training pipeline
./docker/workflow.sh train

# Or with custom parameters
docker-compose run --rm -e DDI_EPOCHS=20 -e DDI_BATCH_SIZE=512 ddi-train
```

### 3. How to Test

Run comprehensive tests:

```bash
# Integration tests
./docker/test-integration.sh

# API tests
docker-compose run --rm ddi-test
```

### 4. How to Evaluate

Evaluate model performance:

```bash
# Full evaluation with plots
./docker/workflow.sh evaluate

# Or direct evaluation
./docker/evaluate.sh --save-plots --output-dir ./results
```

## Traditional Setup

### Prerequisites

- Python 3.11+
- PyTorch
- RDKit
- Required dependencies in `requirements.txt`

### Installation

```bash
# Clone repository
git clone <repository-url>
cd DDIService

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Start API Service
```bash
# Default startup (port 8001)
python run_service.py

# With custom settings
python run_service.py --host 0.0.0.0 --port 8001
```

#### Train Model
```bash
# Basic training
python train_model.py

# With parameters
python train_model.py --epochs 20 --batch-size 512 --learning-rate 0.001
```

#### Evaluate Model
```bash
# Comprehensive evaluation
python evaluate_model.py --save-plots --output-dir ./results

# Quick evaluation
python evaluate_model.py --splits test
```

## Configuration

Key configuration files:
- `.env` - Environment variables
- `src/config.py` - Model and training parameters

Important settings:
- **Port**: 8001
- **Model Labels**: 1317 side effects
- **Model Path**: `./models/best_ddi_model.pt`

## API Endpoints

- `POST /predict` - Single drug pair prediction
- `POST /predict/batch` - Multiple drug pairs
- `GET /health` - Service health check

## Project Structure

```
DDIService/
├── docker/              # Docker workflow scripts
├── src/                # Core source code
│   ├── model.py        # Neural network
│   ├── inference.py    # Prediction logic
│   ├── training.py     # Training pipeline
│   └── config.py       # Configuration
├── models/             # Trained models
├── main.py            # FastAPI application
├── train_model.py     # Training script
├── run_service.py     # Service runner
└── docker-compose.yml # Docker configuration
```