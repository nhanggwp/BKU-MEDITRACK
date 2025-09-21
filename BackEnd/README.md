# MediTrack Backend API

A comprehensive backend system for MediTrack, a medication safety platform that provides drug interaction checking, prescription parsing, AI-powered explanations, and family medication management.

## 🚀 Features

### Core Features

- **User Management**: Authentication via Supabase with family accounts
- **Medical History Storage**: Comprehensive medical records with conditions and allergies
- **OCR Prescription Parsing**: Process prescription images and extract medication data
- **Drug Interaction Checker**: Uses TWOSIDES database for comprehensive interaction analysis
- **AI-Powered Explanations**: Gemini AI generates plain-language medical risk explanations
- **Encrypted QR Sharing**: Share medical information securely via QR codes
- **Medication Reminders**: Schedule and track medication adherence
- **Family Dashboard**: Manage medications for multiple family members
- **Data Export**: Export medical data in JSON, PDF, or CSV formats

### Technical Features

- **Supabase Integration**: PostgreSQL database with real-time capabilities
- **Redis Caching**: Performance optimization for drug interactions
- **Docker Support**: Containerized deployment
- **Row-Level Security**: Data privacy and access control
- **RESTful API**: Well-documented endpoints
- **Background Tasks**: For long-running operations

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Caching**: Redis
- **AI**: Google Gemini API
- **Authentication**: Supabase Auth
- **File Processing**: aiofiles, Pillow
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode library
- **Encryption**: Cryptography (Fernet)
- **Deployment**: Docker & docker-compose

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Supabase account
- Google Gemini API key
- Redis (included in docker-compose)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

#### Windows:

```cmd
# Navigate to backend directory
cd MediTrack\BackEnd

# Run automated setup script
setup_venv.bat
```

#### Linux/macOS:

```bash
# Navigate to backend directory
cd MediTrack/BackEnd

# Make setup script executable
chmod +x setup_venv.sh

# Run automated setup script
./setup_venv.sh
```

### Option 2: Manual Setup

#### 1. Create Virtual Environment

**Windows:**

```cmd
# Navigate to backend directory
cd MediTrack\BackEnd

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show path with 'venv')
where python
```

**Linux/macOS:**

```bash
# Navigate to backend directory
cd MediTrack/BackEnd

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show path with 'venv')
which python
```

#### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify core installations
python -c "import fastapi, uvicorn, supabase, redis; print('✅ Core dependencies installed')"
```

If you encounter issues with pandas on Windows, try:

```cmd
# Install pandas with pre-compiled wheels
pip install pandas --only-binary=all --no-build-isolation

# Or use conda if available
conda install pandas
```

#### 3. Setup Environment Configuration

**Copy environment template:**

```bash
# Copy the example environment file
cp .env.example .env
```

**Edit `.env` file with your credentials:**

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your_secret_key_here_generate_a_secure_random_string

# Redis Configuration
REDIS_URL=redis://redis:6379

# Environment
ENVIRONMENT=development

# QR Code Encryption
QR_ENCRYPTION_KEY=your_32_character_encryption_key
```

### 3. Setup Database

1. Create a new Supabase project
2. Run the SQL schema from `database_schema.sql` in your Supabase SQL editor
3. Enable Row Level Security (RLS) policies

### 4. Deploy with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 5. Alternative: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run Redis separately
docker run -d -p 6379:6379 redis:7-alpine

# Start the API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Create Necessary Directories

```bash
# Create required directories
mkdir -p uploads/prescriptions
mkdir -p logs

# On Windows
mkdir uploads\prescriptions
mkdir logs
```

#### 5. Start the Development Server

```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal prompt

# Start the server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Virtual Environment Management

### Daily Development Workflow

**Activate virtual environment:**

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**Deactivate virtual environment:**

```bash
deactivate
```

**Verify environment is active:**

```bash
# Should show path containing 'venv'
which python    # Linux/macOS
where python    # Windows

# Should show installed packages
pip list
```

### Managing Dependencies

**Add new dependencies:**

```bash
# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

**Update existing dependencies:**

```bash
# Update a specific package
pip install --upgrade package_name

# Update all packages (use with caution)
pip install --upgrade -r requirements.txt
```

**Clean virtual environment:**

```bash
# Deactivate first
deactivate

# Remove virtual environment
rm -rf venv        # Linux/macOS
rmdir /s venv      # Windows

# Recreate
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 📖 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

The API uses Supabase authentication with JWT tokens. Include the token in requests:

```bash
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/signout` - Logout user

## 📚 API Endpoints Overview

### User Management

- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/dashboard` - Dashboard data

### Medical History

- `GET /api/medical-history/` - Get medical history
- `POST /api/medical-history/conditions` - Add condition
- `POST /api/medical-history/allergies` - Add allergy

### OCR & Prescriptions

- `POST /api/ocr/upload` - Upload prescription image
- `POST /api/ocr/process-ocr` - Process OCR text
- `GET /api/ocr/uploads` - Get user uploads

### Drug Interactions

- `POST /api/interactions/check` - Check drug interactions
- `GET /api/interactions/current-medications` - Check user's medications
- `GET /api/interactions/history` - Interaction history

### AI Explanations

- `POST /api/ai/explain-risks` - Get AI risk explanation
- `POST /api/ai/analyze-prescription` - AI prescription analysis

### QR Sharing

- `POST /api/qr/create` - Create encrypted QR code
- `GET /api/qr/access/{token}` - Access QR data
- `GET /api/qr/tokens` - List user's QR tokens

### Medication Reminders

- `GET /api/reminders/schedules` - Get medication schedules
- `POST /api/reminders/schedules` - Create schedule
- `GET /api/reminders/upcoming` - Upcoming reminders

### Family Management

- `GET /api/family/group` - Get family group
- `POST /api/family/group` - Create family group
- `POST /api/family/members` - Add family member

### Data Export

- `POST /api/export/medical-data` - Export medical data
- `GET /api/export/emergency-summary` - Emergency summary
- `POST /api/export/family-overview` - Family overview

## 🔄 Drug Interaction Risk Levels

The system uses three risk levels for drug interactions:

- **Minor**: Low-risk interactions, monitoring recommended
- **Moderate**: Moderate-risk interactions, discuss with doctor
- **Major**: High-risk interactions, requires immediate medical attention

## 🧪 TWOSIDES Database Integration

The system integrates with the TWOSIDES database for drug interaction data:

1. Place `TWOSIDES.csv` in `db-twosides/` directory
2. Use the populate endpoint to import data:
   ```bash
   POST /api/interactions/populate-twosides
   ```

## 🔒 Security Features

- **Row-Level Security (RLS)**: Database-level access control
- **JWT Authentication**: Secure API access
- **Data Encryption**: QR codes use AES-256 encryption
- **Input Validation**: Pydantic models for request validation
- **CORS Protection**: Configurable CORS policies

## 📊 Monitoring & Health Checks

- `GET /health` - System health check
- Monitor database connectivity
- Redis connection status
- API service status

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest tests/

# Test specific endpoints
curl -X GET "http://localhost:8000/health"
```

## 🚀 Production Deployment

### Environment Configuration

- Set `ENVIRONMENT=production`
- Use strong secret keys
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Use managed Redis service
- Monitor logs and metrics

### Database Setup

- Enable connection pooling
- Configure backup strategies
- Set up database monitoring
- Optimize queries for performance

### Scaling Considerations

- Use load balancers
- Implement caching strategies
- Monitor API rate limits
- Set up horizontal scaling

## 🔧 Configuration

Key configuration options in `config/settings.py`:

- `MAX_FILE_SIZE`: Maximum upload file size
- `CACHE_EXPIRE_MINUTES`: Cache expiration time
- `MAX_AI_TOKENS`: AI response token limit
- `DRUG_INTERACTION_CACHE_HOURS`: Drug interaction cache duration

## 📝 Logging

The application logs important events:

- Authentication attempts
- Drug interaction checks
- QR code access
- Export operations
- Error conditions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure code quality
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the API documentation
2. Review error logs
3. Test with health check endpoint
4. Verify environment configuration

## 🔄 API Flow Examples

### Complete Drug Interaction Check Flow

```bash
# 1. Sign in
POST /api/auth/signin
{
  "email": "user@example.com",
  "password": "password"
}

# 2. Check drug interactions
POST /api/interactions/check
Authorization: Bearer <token>
{
  "medications": ["aspirin", "warfarin", "ibuprofen"],
  "include_user_history": true
}

# 3. Get AI explanation
POST /api/ai/explain-risks
Authorization: Bearer <token>
{
  "medications": ["aspirin", "warfarin", "ibuprofen"],
  "interactions": [...],  // from step 2
  "include_medical_context": true
}
```

### OCR Prescription Processing Flow

```bash
# 1. Upload prescription image
POST /api/ocr/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
file: prescription.jpg
ocr_data: {
  "raw_ocr_text": "...",
  "confidence_score": 0.85,
  "source_type": "printed"
}

# 2. Review extracted medications
GET /api/ocr/uploads/{upload_id}
Authorization: Bearer <token>

# 3. Verify extracted medicines
POST /api/ocr/uploads/{upload_id}/verify
Authorization: Bearer <token>
```

This backend provides a robust foundation for the MediTrack medication safety platform with comprehensive features for medication management, interaction checking, and family care coordination.
