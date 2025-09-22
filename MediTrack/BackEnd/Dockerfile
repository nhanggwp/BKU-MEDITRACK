FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV, Tesseract OCR and other tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    tesseract-ocr \
    tesseract-ocr-vie \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libgomp1 \
    libgdal-dev \
    libgtk-3-0 \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Copy requirements and install Python packages
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Add user's local bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy source code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p db-twosides temp uploads

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
