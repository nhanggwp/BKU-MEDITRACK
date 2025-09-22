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
