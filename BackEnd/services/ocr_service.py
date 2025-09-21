import base64
import os
import platform
import cv2
import numpy as np
import pytesseract
from services.ai_service import AIService

# --- Cross-platform Tesseract binary path ---
# Windows: default install path
# macOS: check Homebrew locations first; otherwise rely on PATH
# Linux: usually already in PATH (/usr/bin/tesseract)
_system = platform.system().lower()
if _system == "windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif _system == "darwin":  # macOS
    if os.path.exists("/opt/homebrew/bin/tesseract"):
        pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
    elif os.path.exists("/usr/local/bin/tesseract"):
        pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"
# else: Linux → leave default (in PATH)

# --- Optional: tessdata directory (language data) ---
# If TESSDATA_PREFIX is set, Tesseract will look for *.traineddata there.
# Example (macOS Homebrew):
#   export TESSDATA_PREFIX="/opt/homebrew/Cellar/tesseract/5.x.x/share/tessdata"
_tessdata_dir = os.getenv("TESSDATA_PREFIX")
_tess_config = {}
if _tessdata_dir and os.path.isdir(_tessdata_dir):
    _tess_config["config"] = f'--tessdata-dir "{_tessdata_dir}"'


class OCRService:
    def __init__(self):
        self.ai_service = AIService()

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess an image before OCR:
        - Resize if larger than 1500px (better speed and memory)
        - Convert to grayscale
        - Apply adaptive thresholding to improve text visibility
        """
        if max(image.shape[:2]) > 1500:
            scale = 1500 / max(image.shape[:2])
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 10
        )
        return processed

    async def recognize_text(self, base64_str: str):
        """
        Full OCR pipeline:
        1) Decode base64 string (strip data URI if present)
        2) Convert to OpenCV image
        3) Preprocess image
        4) Run Tesseract with Vietnamese + English
        5) Analyze extracted text with AIService
        """
        try:
            # Strip "data:image/...;base64," prefix if exists
            if "," in base64_str:
                _, base64_str = base64_str.split(",", 1)

            # Decode base64 to bytes
            image_data = base64.b64decode(base64_str)
            np_array = np.frombuffer(image_data, np.uint8)

            # Convert bytes → OpenCV image (BGR format)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Failed to decode image from base64.")

            # Preprocess for OCR
            processed = self.preprocess_image(image)

            # OCR using both Vietnamese + English languages
            text = pytesseract.image_to_string(
                processed, lang="vie+eng", **_tess_config
            ).strip()

            # Post-process with AI service
            ai_result = await self.ai_service.analyze_prescription_text(text)

            return {
                "raw_text": text,
                "analysis": ai_result
            }

        except Exception as e:
            raise RuntimeError(f"OCR failed: {e}")
