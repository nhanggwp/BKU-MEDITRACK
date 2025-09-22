#!/bin/bash
# Docker Compose Workflow Manager
# Manages different DDI service workflows using docker-compose

set -e

WORKFLOW=${1:-"help"}
EXTRA_ARGS=${@:2}

case $WORKFLOW in
  setup)
    echo "🔧 Setting up DDI Service environment..."
    
    # Create necessary directories
    mkdir -p models cache results logs configs monitoring/grafana monitoring
    
    # Create default configurations if they don't exist
    if [ ! -f "./configs/production.yaml" ]; then
        echo "📝 Creating default configurations..."
        python3 -c "
from src.config import create_default_configs
create_default_configs()
" 2>/dev/null || echo "⚠ Could not create configs automatically"
    fi
    
    # Create monitoring configs
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ddi-api'
    static_configs:
      - targets: ['ddi-api:8001']
    metrics_path: /metrics
    scrape_interval: 10s
EOF
    
    echo "✅ Setup completed!"
    echo "📁 Created directories: models, cache, results, logs, configs"
    echo "💡 Next: Run a workflow (train, serve, develop)"
    ;;
    
  train)
    echo "🔥 Starting training workflow..."
    docker-compose --profile training up --build ddi-train $EXTRA_ARGS
    ;;
    
  evaluate)
    echo "📊 Starting evaluation workflow..."
    if [ ! -f "./models/best_ddi_model.pt" ]; then
        echo "❌ No model found. Train first with: $0 train"
        exit 1
    fi
    docker-compose --profile evaluation up --build ddi-evaluate $EXTRA_ARGS
    ;;
    
  serve)
    echo "🚀 Starting production API service..."
    if [ ! -f "./models/best_ddi_model.pt" ]; then
        echo "❌ No model found. Train first with: $0 train"
        exit 1
    fi
    docker-compose up -d ddi-api $EXTRA_ARGS
    echo "✅ Service started at http://localhost:8001"
    echo "📚 API docs: http://localhost:8001/docs"
    ;;
    
  develop)
    echo "🛠 Starting development environment..."
    docker-compose --profile development up -d ddi-dev $EXTRA_ARGS
    echo "✅ Development environment started!"
    echo "🚀 API: http://localhost:8001"
    echo "📓 Jupyter: http://localhost:8888"
    echo "📊 TensorBoard: http://localhost:6006"
    ;;
    
  full-stack)
    echo "🏗 Starting full development stack..."
    docker-compose \
        --profile development \
        --profile database \
        --profile cache \
        up -d $EXTRA_ARGS
    echo "✅ Full stack started!"
    echo "🚀 API: http://localhost:8001"
    echo "📓 Jupyter: http://localhost:8888"
    echo "🗄 PostgreSQL: localhost:5432"
    echo "🔴 Redis: localhost:6379"
    ;;
    
  monitor)
    echo "📈 Starting monitoring stack..."
    docker-compose \
        --profile monitoring \
        up -d $EXTRA_ARGS
    echo "✅ Monitoring started!"
    echo "📊 Prometheus: http://localhost:9090"
    echo "📈 Grafana: http://localhost:3000 (admin/admin)"
    ;;
    
  pipeline)
    echo "🔄 Running complete ML pipeline..."
    
    # 1. Setup
    $0 setup
    
    # 2. Train
    echo "Step 1/3: Training model..."
    $0 train
    
    # 3. Evaluate
    echo "Step 2/3: Evaluating model..."
    $0 evaluate
    
    # 4. Serve
    echo "Step 3/3: Starting service..."
    $0 serve
    
    echo "✅ Complete pipeline finished!"
    ;;
    
  stop)
    echo "🛑 Stopping all services..."
    docker-compose down $EXTRA_ARGS
    echo "✅ All services stopped"
    ;;
    
  clean)
    echo "🧹 Cleaning up all resources..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    echo "✅ Cleanup completed"
    ;;
    
  logs)
    SERVICE=${2:-"ddi-api"}
    echo "📋 Showing logs for $SERVICE..."
    docker-compose logs -f $SERVICE
    ;;
    
  status)
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    if docker-compose ps | grep -q "Up"; then
        echo "🔍 Health Checks:"
        curl -s http://localhost:8001/health 2>/dev/null && echo "✅ API service healthy" || echo "❌ API service unhealthy"
    fi
    ;;
    
  shell)
    SERVICE=${2:-"ddi-api"}
    echo "🐚 Opening shell in $SERVICE..."
    docker-compose exec $SERVICE /bin/bash
    ;;
    
  test)
    echo "🧪 Running tests..."
    docker-compose run --rm ddi-train python -m pytest tests/ -v $EXTRA_ARGS
    ;;
    
  help|*)
    echo "DDI Service Docker Compose Workflow Manager"
    echo "==========================================="
    echo ""
    echo "Usage: $0 <workflow> [options]"
    echo ""
    echo "🔧 Setup & Management:"
    echo "  setup           Set up directories and configurations"
    echo "  stop            Stop all services"
    echo "  clean           Clean up all resources"
    echo "  status          Show service status"
    echo "  logs [service]  Show logs (default: ddi-api)"
    echo "  shell [service] Open shell in service"
    echo ""
    echo "🤖 ML Workflows:"
    echo "  train           Train DDI model"
    echo "  evaluate        Evaluate trained model"
    echo "  test            Run unit tests"
    echo "  pipeline        Run complete ML pipeline (train → evaluate → serve)"
    echo ""
    echo "🚀 Service Modes:"
    echo "  serve           Start production API service"
    echo "  develop         Start development environment (API + Jupyter)"
    echo "  full-stack      Start full stack (dev + database + cache)"
    echo "  monitor         Start monitoring stack (Prometheus + Grafana)"
    echo ""
    echo "📋 Examples:"
    echo "  $0 setup"
    echo "  $0 train"
    echo "  $0 serve"
    echo "  $0 develop"
    echo "  $0 pipeline"
    echo "  $0 logs ddi-api"
    echo ""
    echo "🔗 URLs (when running):"
    echo "  API:        http://localhost:8001"
    echo "  API Docs:   http://localhost:8001/docs"
    echo "  Jupyter:    http://localhost:8888"
    echo "  Grafana:    http://localhost:3000"
    echo "  Prometheus: http://localhost:9090"
    ;;
esac