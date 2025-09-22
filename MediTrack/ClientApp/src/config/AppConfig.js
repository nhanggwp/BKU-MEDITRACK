// Configuration for the MediTrack app

const config = {
  // Backend API configuration
  api: {
    // Update this URL to match your backend server
    baseURL: __DEV__ 
      ? 'http://localhost:8000/api'  // Development (local backend)
      : 'https://your-production-api.com/api', // Production
    
    // Request timeout in milliseconds
    timeout: 30000,
    
    // Retry attempts for failed requests
    retryAttempts: 3,
  },

  // OCR processing configuration
  ocr: {
    // Image quality for camera capture (0.1 to 1.0)
    imageQuality: 0.8,
    
    // Maximum image size for processing (in pixels)
    maxImageSize: 2048,
    
    // Supported image formats
    supportedFormats: ['jpg', 'jpeg', 'png'],
    
    // OCR language settings
    languages: ['en'], // Can add more languages like ['en', 'es', 'fr']
    
    // Confidence thresholds
    confidenceThresholds: {
      high: 0.8,
      medium: 0.6,
      low: 0.4,
    },
  },

  // Drug interaction settings
  drugInteractions: {
    // Minimum number of medications to check interactions
    minMedicationsForCheck: 2,
    
    // Risk level colors
    riskColors: {
      high: '#F44336',
      medium: '#FF9800',
      low: '#4CAF50',
      unknown: '#9E9E9E',
    },
  },

  // Camera settings
  camera: {
    // Default camera type
    defaultType: 'back',
    
    // Auto-focus settings
    autoFocus: true,
    
    // Flash mode
    flashMode: 'auto',
    
    // White balance
    whiteBalance: 'auto',
  },

  // Debug settings
  debug: {
    // Enable console logging
    enableLogging: __DEV__,
    
    // Log levels: 'error', 'warn', 'info', 'debug'
    logLevel: __DEV__ ? 'debug' : 'error',
    
    // Enable OCR mock data for testing
    useMockOCR: false,
  },
};

export default config;
