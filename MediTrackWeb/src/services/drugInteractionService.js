import apiService from './api';

class DrugInteractionService {
  // Check drug interactions
  async checkInteractions(medications, includeUserHistory = true) {
    try {
      const response = await apiService.post('/api/interactions/check', {
        medications,
        include_user_history: includeUserHistory
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to check drug interactions');
    }
  }

  // Search medications
  async searchMedications(query, limit = 10) {
    try {
      const response = await apiService.get(`/api/interactions/medications/search?query=${encodeURIComponent(query)}&limit=${limit}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to search medications');
    }
  }

  // Get interaction history
  async getInteractionHistory(limit = 10, offset = 0) {
    try {
      const response = await apiService.get(`/api/interactions/history?limit=${limit}&offset=${offset}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to get interaction history');
    }
  }

  // Get specific interaction between two drugs
  async getSpecificInteraction(drug1, drug2) {
    try {
      const response = await apiService.get(`/api/interactions/${encodeURIComponent(drug1)}/${encodeURIComponent(drug2)}`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to get specific interaction');
    }
  }

  // Batch check interactions (for multiple patients/lists)
  async batchCheckInteractions(medicationLists) {
    try {
      const response = await apiService.post('/api/interactions/batch-check', medicationLists);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to batch check interactions');
    }
  }

  // Parse interaction severity
  getRiskLevel(interactions) {
    if (!interactions || interactions.length === 0) return 'low';
    
    const severities = interactions.map(interaction => interaction.severity?.toLowerCase() || 'low');
    
    if (severities.includes('high') || severities.includes('severe')) return 'high';
    if (severities.includes('moderate') || severities.includes('medium')) return 'medium';
    return 'low';
  }

  // Format interaction message
  formatInteractionMessage(interactions) {
    if (!interactions || interactions.length === 0) {
      return 'No significant drug interactions found.';
    }

    const highRisk = interactions.filter(i => 
      ['high', 'severe'].includes(i.severity?.toLowerCase())
    );
    
    const mediumRisk = interactions.filter(i => 
      ['moderate', 'medium'].includes(i.severity?.toLowerCase())
    );

    let message = '';
    if (highRisk.length > 0) {
      message += `⚠️ ${highRisk.length} high-risk interaction(s) detected. `;
    }
    if (mediumRisk.length > 0) {
      message += `⚡ ${mediumRisk.length} moderate-risk interaction(s) found. `;
    }

    return message || 'Some interactions detected. Please review carefully.';
  }

  // Get risk color for UI
  getRiskColor(riskLevel) {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
      case 'severe':
        return '#ff4444';
      case 'medium':
      case 'moderate':
        return '#ff8800';
      case 'low':
      case 'minor':
        return '#44ff44';
      default:
        return '#cccccc';
    }
  }
}

export default new DrugInteractionService();
