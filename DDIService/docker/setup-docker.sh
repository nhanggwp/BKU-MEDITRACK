#!/bin/bash
# Docker Environment Setup Script
# Initialize Docker environment with proper configurations

set -e

echo "🐳 Setting up DDI Service Docker Environment"
echo "============================================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p {models,cache,results,logs,configs,monitoring/grafana,monitoring}

# Create .dockerignore if it doesn't exist
if [ ! -f ".dockerignore" ]; then
    echo "📝 Creating .dockerignore..."
    cat > .dockerignore << 'EOF'
# Cache and results
cache/
results/
logs/
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.pytest_cache/
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/

# Jupyter
.ipynb_checkpoints/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
README_DOCKER.md
docs/

# Development
.env.development
.env.local
EOF
fi

# Create monitoring configs
echo "📊 Creating monitoring configurations..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ddi-api'
    static_configs:
      - targets: ['ddi-api:8000']
    metrics_path: /metrics
    scrape_interval: 10s
    scrape_timeout: 5s
EOF

mkdir -p monitoring/grafana/dashboards monitoring/grafana/datasources

cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create health check script
echo "💚 Creating health check script..."
cat > docker/health-check.sh << 'EOF'
#!/bin/bash
# Health check script for DDI service

SERVICE_URL=${1:-"http://localhost:8000"}

# Check if service is responding
response=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health")

if [ "$response" = "200" ]; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is unhealthy (HTTP $response)"
    exit 1
fi
EOF

chmod +x docker/health-check.sh

# Create default configurations if they don't exist
if [ ! -f "configs/production.yaml" ]; then
    echo "⚙️ Creating default configurations..."
    python3 -c "
try:
    import sys
    sys.path.append('.')
    from src.config import create_default_configs
    create_default_configs()
    print('✅ Configurations created successfully')
except Exception as e:
    print(f'⚠ Could not create configurations: {e}')
    print('💡 Run after installing dependencies: pip install -r requirements.txt')
" 2>/dev/null || echo "⚠ Will create configurations after first run"
fi

# Create example environment files if they don't exist
if [ ! -f ".env.example" ]; then
    echo "📋 Creating example environment file..."
    cat > .env.example << 'EOF'
# DDI Service Configuration Example
# Copy to .env and customize as needed

# Model Configuration
DDI_MODEL_PATH=/app/models/best_ddi_model.pt
DDI_HIDDEN_DIM=1024
DDI_DROPOUT=0.4

# Training Configuration  
DDI_EPOCHS=10
DDI_BATCH_SIZE=256
DDI_LEARNING_RATE=0.001
DDI_DEVICE=auto

# Data Configuration
DDI_DATASET=TWOSIDES
DDI_CACHE_DIR=/app/cache
DDI_USE_CACHE=true

# Server Configuration
DDI_HOST=0.0.0.0
DDI_PORT=8000
DDI_WORKERS=1
DDI_LOG_LEVEL=info

# Environment
DDI_ENVIRONMENT=production
DDI_DEBUG=false

# Optional: Database for results
POSTGRES_DB=ddi_results
POSTGRES_USER=ddi_user
POSTGRES_PASSWORD=ddi_password

# Optional: Monitoring
PROMETHEUS_ENABLED=false
GRAFANA_ADMIN_PASSWORD=admin
EOF
fi

# Test Docker installation
echo "🔧 Testing Docker installation..."
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker is not installed or not in PATH"
    echo "💡 Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed or not in PATH"
    echo "💡 Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Test NVIDIA Docker if available
if command -v nvidia-docker > /dev/null 2>&1; then
    echo "✅ NVIDIA Docker detected - GPU support available"
elif docker info 2>/dev/null | grep -q "nvidia"; then
    echo "✅ NVIDIA Docker runtime detected - GPU support available"
else
    echo "⚠ NVIDIA Docker not detected - GPU training will fall back to CPU"
fi

echo ""
echo "✅ Docker environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy environment file: cp .env.example .env"
echo "2. Run complete pipeline: ./docker/workflow.sh pipeline"
echo "3. Or individual steps:"
echo "   - Setup: ./docker/workflow.sh setup"
echo "   - Train: ./docker/workflow.sh train"  
echo "   - Serve: ./docker/workflow.sh serve"
echo ""
echo "🌐 Service will be available at: http://localhost:8000/docs"
echo "📚 Docker guide: README_DOCKER.md"