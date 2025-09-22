#!/bin/bash
# Docker Service Management Script
# Start/stop/manage DDI API service using Docker

set -e

COMMAND=${1:-"start"}
PROFILE=${2:-"production"}

# Configuration
IMAGE_NAME="ddi-service"
CONTAINER_NAME="ddi-api"
HOST_PORT=8000
CONTAINER_PORT=8000

case $COMMAND in
  start)
    echo "🚀 Starting DDI API Service"
    echo "Profile: $PROFILE"
    echo "Port: $HOST_PORT"
    echo "=========================="
    
    # Create necessary directories
    mkdir -p models logs
    
    # Check if model exists for production
    if [[ "$PROFILE" == "production" ]] && [ ! -f "./models/best_ddi_model.pt" ]; then
        echo "❌ Error: No trained model found at ./models/best_ddi_model.pt"
        echo "💡 Run training first: ./docker/train.sh"
        exit 1
    fi
    
    # Build the appropriate image
    echo "📦 Building $PROFILE image..."
    if [[ "$PROFILE" == "development" ]]; then
        docker build --target development -t $IMAGE_NAME:dev .
        IMAGE_TAG="dev"
        EXTRA_PORTS="-p 8888:8888 -p 6006:6006"
        ENVIRONMENT="-e DDI_DEBUG=true -e DDI_ENVIRONMENT=development"
        VOLUMES="-v $(pwd):/app"
        CMD=""
    else
        docker build --target serve -t $IMAGE_NAME:latest .
        IMAGE_TAG="latest"
        EXTRA_PORTS=""
        ENVIRONMENT="-e DDI_ENVIRONMENT=production"
        VOLUMES="-v $(pwd)/models:/app/models:ro -v $(pwd)/logs:/app/logs"
        CMD=""
    fi
    
    # Stop existing container if running
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # Start the container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $HOST_PORT:$CONTAINER_PORT \
        $EXTRA_PORTS \
        $ENVIRONMENT \
        $VOLUMES \
        --restart unless-stopped \
        $IMAGE_NAME:$IMAGE_TAG $CMD
    
    echo "✅ Service started successfully!"
    echo "🌐 API Documentation: http://localhost:$HOST_PORT/docs"
    echo "💚 Health Check: http://localhost:$HOST_PORT/health"
    
    if [[ "$PROFILE" == "development" ]]; then
        echo "📓 Jupyter Lab: http://localhost:8888"
        echo "📊 TensorBoard: http://localhost:6006"
    fi
    
    echo ""
    echo "📋 Container Status:"
    docker ps --filter "name=$CONTAINER_NAME"
    ;;
    
  stop)
    echo "🛑 Stopping DDI API Service..."
    docker stop $CONTAINER_NAME 2>/dev/null || echo "Container not running"
    docker rm $CONTAINER_NAME 2>/dev/null || echo "Container already removed"
    echo "✅ Service stopped"
    ;;
    
  restart)
    echo "🔄 Restarting DDI API Service..."
    $0 stop
    sleep 2
    $0 start $PROFILE
    ;;
    
  logs)
    echo "📋 Showing service logs..."
    docker logs -f $CONTAINER_NAME
    ;;
    
  status)
    echo "📊 Service Status:"
    if docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q $CONTAINER_NAME; then
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "🔍 Health Check:"
        curl -s http://localhost:$HOST_PORT/health | python3 -m json.tool 2>/dev/null || echo "Service not responding"
    else
        echo "❌ Service not running"
    fi
    ;;
    
  shell)
    echo "🐚 Opening shell in service container..."
    if docker ps --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
        docker exec -it $CONTAINER_NAME /bin/bash
    else
        echo "❌ Container not running. Starting temporary shell..."
        docker run --rm -it \
            -v $(pwd):/app \
            $IMAGE_NAME:latest /bin/bash
    fi
    ;;
    
  clean)
    echo "🧹 Cleaning up Docker resources..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    docker rmi $IMAGE_NAME:latest $IMAGE_NAME:dev 2>/dev/null || true
    docker system prune -f
    echo "✅ Cleanup completed"
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|logs|status|shell|clean} [profile]"
    echo ""
    echo "Commands:"
    echo "  start [profile]  Start the service (profiles: production, development)"
    echo "  stop             Stop the service"
    echo "  restart [profile] Restart the service"
    echo "  logs             Show service logs"
    echo "  status           Show service status"
    echo "  shell            Open shell in container"
    echo "  clean            Clean up Docker resources"
    echo ""
    echo "Profiles:"
    echo "  production       Production mode with API only"
    echo "  development      Development mode with Jupyter and debugging"
    echo ""
    echo "Examples:"
    echo "  $0 start production"
    echo "  $0 start development"
    echo "  $0 logs"
    echo "  $0 stop"
    exit 1
    ;;
esac