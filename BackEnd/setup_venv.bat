@echo off
setlocal enabledelayedexpansion

REM MediTrack Backend Virtual Environment Setup Script for Windows
echo.
echo 🚀 MediTrack Backend Virtual Environment Setup
echo ===============================================

REM Check if running in correct directory
if not exist "main.py" (
    echo ❌ Please run this script from the BackEnd directory
    pause
    exit /b 1
)

echo ✅ Setting up MediTrack backend with virtual environment...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not found
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✅ Python found: %%i
)

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
if exist "venv" (
    echo ⚠️  Virtual environment already exists
    set /p RECREATE="Recreate virtual environment? (y/n): "
    if "!RECREATE!"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
        python -m venv venv
        echo ✅ Virtual environment recreated
    ) else (
        echo ✅ Using existing virtual environment
    )
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify activation
where python | findstr venv >nul
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
) else (
    echo ✅ Virtual environment activated
    python --version
)

REM Upgrade pip
echo.
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo 📥 Installing dependencies from requirements.txt...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ Some packages failed to install
        echo 💡 Trying with different options...
        
        REM Try with no cache and no build isolation
        pip install -r requirements.txt --no-cache-dir --no-build-isolation
        
        if errorlevel 1 (
            echo.
            echo ⚠️  Some packages still failed. Installing core packages individually...
            
            REM Install core packages one by one
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
            
            REM Try pandas last (might need special handling on Windows)
            echo Installing pandas...
            pip install pandas==2.1.3 --only-binary=all
            if errorlevel 1 (
                echo ⚠️  Pandas installation failed. Trying alternative...
                pip install pandas --only-binary=all --no-build-isolation
                if errorlevel 1 (
                    echo ❌ Pandas installation failed. Backend will run without pandas-dependent features.
                    echo 💡 Consider installing Visual Studio Build Tools or using conda for pandas
                )
            )
        )
    ) else (
        echo ✅ All dependencies installed successfully
    )
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo 📁 Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "uploads\prescriptions" mkdir uploads\prescriptions
if not exist "logs" mkdir logs
echo ✅ Directories created

REM Setup environment file
echo.
echo ⚙️  Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ Created .env file from .env.example
        echo ⚠️  Please edit .env file with your actual credentials
    ) else (
        echo ❌ .env.example file not found
    )
) else (
    echo ✅ .env file already exists
)

REM Test installation
echo.
echo 🧪 Testing installation...
python -c "import fastapi, uvicorn; print('✅ Core web framework: OK')" 2>nul
if errorlevel 1 (
    echo ❌ FastAPI installation test failed
) else (
    echo ✅ FastAPI installation test passed
)

python -c "import supabase; print('✅ Supabase client: OK')" 2>nul
if errorlevel 1 (
    echo ❌ Supabase installation test failed
) else (
    echo ✅ Supabase installation test passed
)

python -c "import redis; print('✅ Redis client: OK')" 2>nul
if errorlevel 1 (
    echo ❌ Redis installation test failed
) else (
    echo ✅ Redis installation test passed
)

python -c "from services.auth_service import AuthService; print('✅ Auth service: OK')" 2>nul
if errorlevel 1 (
    echo ❌ Auth service test failed
) else (
    echo ✅ Auth service test passed
)

echo.
echo 🎉 Virtual environment setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your Supabase and other service credentials
echo 2. Start the development server with: python main.py
echo 3. Or use: uvicorn main:app --reload
echo 4. API docs will be available at: http://localhost:8000/docs
echo.
echo 💡 To activate this environment in the future:
echo    venv\Scripts\activate.bat
echo.
echo 💡 To deactivate:
echo    deactivate
echo.

pause
