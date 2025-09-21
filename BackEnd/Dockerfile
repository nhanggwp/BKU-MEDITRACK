FROM python:3.11-slim

WORKDIR /app

# Cài các gói hệ thống cần thiết cho OpenCV + Tesseract
RUN apt-get update && apt-get install -y \
    gcc \
    tesseract-ocr \
    libglib2.0-0 \
    tesseract-ocr-vie\
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code source vào container
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
