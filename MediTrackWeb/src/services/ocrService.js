import apiService from './api';

class OCRService {
  // Analyze prescription text with AI
  async analyzePrescription(ocrText, confidenceScore = 0.8, sourceType = 'mixed') {
    try {
      const response = await apiService.post('/api/ocr/analyze-prescription', {
        raw_ocr_text: ocrText,
        confidence_score: confidenceScore,
        source_type: sourceType
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to analyze prescription');
    }
  }

  // Upload OCR data
  async uploadOCRData(ocrData) {
    try {
      const response = await apiService.post('/api/ocr/upload', ocrData);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to upload OCR data');
    }
  }

  // Recognize text from base64 image
  async recognizeText(imageBase64) {
    try {
      const response = await apiService.post('/api/ocr/recognize', {
        image_base64: imageBase64
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to recognize text');
    }
  }

  // Get OCR uploads history
  async getUploads(limit = 10, offset = 0) {
    try {
      const response = await apiService.get(`/api/ocr/uploads?limit=${limit}&offset=${offset}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to get uploads');
    }
  }

  // Get specific OCR upload
  async getUpload(uploadId) {
    try {
      const response = await apiService.get(`/api/ocr/uploads/${uploadId}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to get upload');
    }
  }

  // Save extracted medicines
  async saveExtractedMedicines(uploadId, medicines) {
    try {
      const response = await apiService.post(`/api/ocr/upload/${uploadId}/medicines`, medicines);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to save extracted medicines');
    }
  }

  // Review prescription
  async reviewPrescription(uploadId, reviewData) {
    try {
      const response = await apiService.put(`/api/ocr/uploads/${uploadId}/review`, reviewData);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to review prescription');
    }
  }

  // Delete OCR upload
  async deleteUpload(uploadId) {
    try {
      const response = await apiService.delete(`/api/ocr/uploads/${uploadId}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete upload');
    }
  }

  // Convert image file to base64
  async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove the data:image/...;base64, prefix
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }

  // Process prescription image (complete flow)
  async processPrescriptionImage(imageFile) {
    try {
      // Convert image to base64
      const base64Image = await this.fileToBase64(imageFile);
      
      // Recognize text from image
      const ocrResult = await this.recognizeText(base64Image);
      
      if (!ocrResult.text) {
        throw new Error('No text detected in image');
      }

      // Analyze the recognized text
      const analysisResult = await this.analyzePrescription(
        ocrResult.text,
        ocrResult.confidence || 0.8,
        'mixed'
      );

      return {
        ocrResult,
        analysisResult,
        extractedMedicines: analysisResult.extracted_medicines || []
      };
    } catch (error) {
      throw new Error(error.message || 'Failed to process prescription image');
    }
  }

  // Validate image file
  validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!allowedTypes.includes(file.type)) {
      throw new Error('Please upload a valid image file (JPEG, PNG, or GIF)');
    }

    if (file.size > maxSize) {
      throw new Error('Image file is too large. Please upload a file smaller than 5MB');
    }

    return true;
  }

  // Format medicine data for display
  formatMedicineData(medicines) {
    if (!medicines || !Array.isArray(medicines)) return [];

    return medicines.map(med => ({
      name: med.extracted_name || med.name || 'Unknown',
      dosage: med.dosage || 'Not specified',
      frequency: med.frequency || 'Not specified',
      duration: med.duration || 'Not specified',
      confidence: med.confidence_score || 0
    }));
  }
}

export default new OCRService();
