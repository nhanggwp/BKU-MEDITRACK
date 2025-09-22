#!/usr/bin/env python3
"""
Run DDI Service Script
Convenient script to run the DDI API service
"""
import argparse
import os
import sys
import uvicorn

# Add the DDIService directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='Run DDI API Service')
    
    # Server parameters
    parser.add_argument('--host', type=str, default=os.getenv('DDI_HOST', '0.0.0.0'), 
                       help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.getenv('DDI_PORT', '8000')), 
                       help='Port to bind to')
    parser.add_argument('--workers', type=int, default=1, 
                       help='Number of worker processes')
    parser.add_argument('--reload', action='store_true', 
                       help='Enable auto-reload for development')
    
    # Model parameters
    parser.add_argument('--model-path', type=str, default='./models/best_ddi_model.pt',
                       help='Path to the trained model')
    parser.add_argument('--device', type=str, default=None,
                       help='Device to use (cuda/cpu)')
    
    # Logging
    parser.add_argument('--log-level', type=str, default='info',
                       choices=['debug', 'info', 'warning', 'error'],
                       help='Log level')
    
    args = parser.parse_args()
    
    # Set environment variables for the FastAPI app
    if args.model_path:
        os.environ['DDI_MODEL_PATH'] = args.model_path
    if args.device:
        os.environ['DDI_DEVICE'] = args.device
    
    print("Starting DDI API Service")
    print("=" * 50)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers}")
    print(f"Reload: {args.reload}")
    print(f"Model Path: {args.model_path}")
    print(f"Device: {args.device or 'auto'}")
    print(f"Log Level: {args.log_level}")
    print("=" * 50)
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        workers=args.workers if not args.reload else 1,  # reload doesn't work with multiple workers
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()