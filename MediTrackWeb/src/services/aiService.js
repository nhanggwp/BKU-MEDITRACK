import apiService from './api';

class AIService {
  // Generate AI explanation for medication risks
  async explainMedicationRisks(medications, options = {}) {
    try {
      const requestData = {
        medication_list: medications,
        risk_factors: options.riskFactors || null,
        include_medical_history: options.includeMedicalHistory !== false,
        format: options.format || 'markdown'
      };

      const response = await apiService.post('/api/ai/explain', requestData);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate AI explanation');
    }
  }

  // Generate custom AI explanation with custom prompt
  async generateCustomExplanation(medications, customPrompt, includeContext = true) {
    try {
      const response = await apiService.post('/api/ai/custom-prompt', {
        medications,
        custom_prompt: customPrompt,
        include_context: includeContext
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate custom explanation');
    }
  }

  // Get AI explanation history
  async getExplanationHistory(limit = 10, offset = 0) {
    try {
      const response = await apiService.get(`/api/ai/history?limit=${limit}&offset=${offset}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to get explanation history');
    }
  }

  // Get specific AI explanation
  async getExplanation(explanationId) {
    try {
      const response = await apiService.get(`/api/ai/explanations/${explanationId}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to get explanation');
    }
  }

  // Delete AI explanation
  async deleteExplanation(explanationId) {
    try {
      const response = await apiService.delete(`/api/ai/explanations/${explanationId}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete explanation');
    }
  }

  // Generate user profile summary
  async summarizeUserProfile() {
    try {
      const response = await apiService.post('/api/ai/summarize-profile', {});
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to summarize user profile');
    }
  }

  // Simple chat interaction for chatbot
  async chatInteraction(message, context = {}) {
    try {
      // If message is about medications, use the medication explanation endpoint
      if (this.isMedicationQuery(message)) {
        const medications = this.extractMedicationsFromMessage(message);
        return await this.generateCustomExplanation(
          medications,
          message,
          true
        );
      }

      // For general medical questions, use custom prompt
      return await this.generateCustomExplanation(
        [],
        message,
        true
      );
    } catch (error) {
      throw new Error(error.message || 'Chat interaction failed');
    }
  }

  // Helper: Check if message is about medications
  isMedicationQuery(message) {
    const medicationKeywords = [
      'medication', 'medicine', 'drug', 'pill', 'tablet',
      'interaction', 'side effect', 'dosage', 'prescription'
    ];
    
    return medicationKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    );
  }

  // Helper: Extract potential medication names from message
  extractMedicationsFromMessage(message) {
    // This is a simple implementation - in a real app, you might want
    // to use NLP or a more sophisticated approach
    const commonMedications = [
      'paracetamol', 'ibuprofen', 'aspirin', 'clopidogrel',
      'metformin', 'lisinopril', 'atorvastatin', 'amlodipine'
    ];

    const foundMedications = [];
    const lowerMessage = message.toLowerCase();

    commonMedications.forEach(med => {
      if (lowerMessage.includes(med)) {
        foundMedications.push(med);
      }
    });

    return foundMedications;
  }

  // Format AI response for display
  formatResponseForDisplay(response) {
    if (!response.explanation) return 'No explanation available.';

    // If it's markdown, you might want to convert it to HTML
    // For now, return as-is
    return response.explanation;
  }

  // Get risk level color for UI
  getRiskLevelColor(riskLevel) {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return '#ff4444';
      case 'medium':
        return '#ff8800';
      case 'low':
        return '#44ff44';
      default:
        return '#cccccc';
    }
  }
}

export default new AIService();
