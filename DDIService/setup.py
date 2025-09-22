#!/usr/bin/env python3
"""
Setup DDI Service Script
Creates configuration files and prepares the service for use
"""
import os
import sys

# Add the DDIService directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("Setting up DDI Service...")
    print("=" * 50)
    
    # Create necessary directories
    directories = [
        "./cache",
        "./evaluation_results", 
        "./configs",
        "./models"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create default configuration files
    try:
        from src.config import create_default_configs
        create_default_configs()
        print("✓ Created default configuration files")
    except Exception as e:
        print(f"⚠ Could not create config files: {e}")
    
    # Check if model exists
    model_path = "./models/best_ddi_model.pt"
    if os.path.exists(model_path):
        print(f"✓ Model found: {model_path}")
    else:
        print(f"⚠ Model not found: {model_path}")
        print("  Run 'python train_model.py' to train a new model")
    
    print("\n" + "=" * 50)
    print("DDI Service Setup Complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    if not os.path.exists(model_path):
        print("2. Train model: python train_model.py")
    print("3. Start service: python run_service.py")
    print("4. View API docs: http://localhost:8000/docs")
    print("=" * 50)


if __name__ == "__main__":
    main()