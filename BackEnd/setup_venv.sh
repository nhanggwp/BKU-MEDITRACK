#!/bin/bash

# MediTrack Backend Virtual Environment Setup Script for Linux/macOS
echo ""
echo "🚀 MediTrack Backend Virtual Environment Setup"
echo "==============================================="

# Check if running in correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the BackEnd directory"
    exit 1
fi

echo "✅ Setting up MediTrack backend with virtual environment..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
else
    echo "✅ Python found: $(python3 --version)"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Recreate virtual environment? (y/n): " RECREATE
    if [ "$RECREATE" = "y" ]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
        python3 -m venv venv
        echo "✅ Virtual environment recreated"
    else
        echo "✅ Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    echo "Python location: $(which python)"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Some packages failed to install"
        echo "💡 Trying with different options..."
        
        # Try with no cache
        pip install -r requirements.txt --no-cache-dir
        
        if [ $? -ne 0 ]; then
            echo ""
            echo "⚠️  Some packages still failed. Installing core packages individually..."
            
            # Install core packages one by one
            pip install fastapi==0.104.1
            pip install uvicorn==0.24.0
            pip install python-multipart==0.0.6
            pip install supabase==2.3.0
            pip install python-dotenv==1.0.0
            pip install pydantic==2.5.0
            pip install pydantic-settings==2.1.0
            pip install cryptography==41.0.8
            pip install qrcode==7.4.2
            pip install Pillow==10.1.0
            pip install redis==5.0.1
            pip install google-generativeai==0.3.2
            pip install httpx==0.25.2
            pip install "python-jose[cryptography]==3.3.0"
            pip install "passlib[bcrypt]==1.7.4"
            pip install bcrypt==4.1.2
            pip install aiofiles==23.2.1
            pip install reportlab==4.0.6
            pip install pandas==2.1.3
        fi
    else
        echo "✅ All dependencies installed successfully"
    fi
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p uploads/prescriptions
mkdir -p logs
echo "✅ Directories created"

# Setup environment file
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env file with your actual credentials"
    else
        echo "❌ .env.example file not found"
    fi
else
    echo "✅ .env file already exists"
fi

# Test installation
echo ""
echo "🧪 Testing installation..."

python -c "import fastapi, uvicorn; print('✅ Core web framework: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ FastAPI installation test failed"
else
    echo "✅ FastAPI installation test passed"
fi

python -c "import supabase; print('✅ Supabase client: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Supabase installation test failed"
else
    echo "✅ Supabase installation test passed"
fi

python -c "import redis; print('✅ Redis client: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Redis installation test failed"
else
    echo "✅ Redis installation test passed"
fi

python -c "from services.auth_service import AuthService; print('✅ Auth service: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Auth service test failed"
else
    echo "✅ Auth service test passed"
fi

echo ""
echo "🎉 Virtual environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Supabase and other service credentials"
echo "2. Start the development server with: python main.py"
echo "3. Or use: uvicorn main:app --reload"
echo "4. API docs will be available at: http://localhost:8000/docs"
echo ""
echo "💡 To activate this environment in the future:"
echo "   source venv/bin/activate"
echo ""
echo "💡 To deactivate:"
echo "   deactivate"
echo ""
