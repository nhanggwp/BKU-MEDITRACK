# Multi-stage Docker build for DDI Service
# Supports training, evaluation, testing, and serving workflows

# Base image with common dependencies
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DDI_MODEL_PATH=/app/models/best_ddi_model.pt
ENV DDI_CACHE_DIR=/app/cache
ENV DDI_OUTPUT_DIR=/app/results

# Install system dependencies (including CUDA support)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    wget \
    git \
    libgomp1 \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/models /app/cache /app/results /app/configs /app/logs

# Production serving image
FROM base as serve

# Copy application code
COPY src/ ./src/
COPY main.py .
COPY run_service.py .

# Copy pre-trained model if available
COPY models/ ./models/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash ddi_user && \
    chown -R ddi_user:ddi_user /app

# Switch to non-root user
USER ddi_user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose the port
EXPOSE 8001

# Run the application
CMD ["python", "run_service.py"]

# Training image with additional development tools
FROM base as train

# Install additional training dependencies
RUN pip install --no-cache-dir jupyter tensorboard

# Copy all application code including training scripts
COPY src/ ./src/
COPY *.py ./

# Set up training environment
ENV DDI_ENVIRONMENT=training
ENV DDI_DEVICE=auto
ENV DDI_EPOCHS=10
ENV DDI_BATCH_SIZE=256

# Create directories with proper permissions
RUN mkdir -p /app/models /app/cache /app/results /app/logs && \
    chmod 755 /app/models /app/cache /app/results /app/logs

# Default command for training
CMD ["python", "train_model.py", "--use-cache", "--epochs", "10"]

# Evaluation image optimized for model analysis
FROM base as evaluate

# Copy application code
COPY src/ ./src/
COPY evaluate_model.py .
COPY configs/ ./configs/

# Copy pre-trained models
COPY models/ ./models/

# Set evaluation environment
ENV DDI_ENVIRONMENT=evaluation

# Create evaluation directories
RUN mkdir -p /app/results /app/plots /app/reports

# Default command for evaluation
CMD ["python", "evaluate_model.py", "--save-plots", "--output-dir", "/app/results"]

# Development image with all tools
FROM base as development

# Install development tools
RUN pip install --no-cache-dir \
    jupyter \
    jupyterlab \
    tensorboard \
    pytest-cov \
    pre-commit

# Copy all code
COPY . .

# Set development environment
ENV DDI_ENVIRONMENT=development
ENV DDI_DEBUG=true

# Expose additional ports for development
EXPOSE 8000 8888 6006

# Default command opens a shell
CMD ["/bin/bash"]