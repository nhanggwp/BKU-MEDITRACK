#!/usr/bin/env python3
"""
Simple test script to verify Gemini API connection
"""
import os
import google.generativeai as genai
from config.settings import Settings

def test_gemini_api():
    """Test Gemini API configuration"""
    try:
        settings = Settings()
        
        print("🔍 Checking Gemini API configuration...")
        print(f"   API Key: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-5:] if len(settings.gemini_api_key) > 15 else 'TOO SHORT'}")
        print(f"   Length: {len(settings.gemini_api_key)} characters")
        
        if len(settings.gemini_api_key) < 30:
            print("❌ API key appears to be incomplete (too short)")
            return False
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        
        # Test with a simple model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("🤖 Testing AI response...")
        test_prompt = """
Extract medications from this prescription text:

PRESCRIPTION
Patient: John Doe
Date: 2024-01-15

Medications:
1. Lisinopril 10mg - Take once daily
2. Metformin 500mg - Take twice daily

Return JSON format:
{
    "medications": [
        {"name": "medication name", "dosage": "dosage"}
    ]
}
"""
        
        response = model.generate_content(test_prompt)
        
        print("✅ AI Response received:")
        print(f"   Response length: {len(response.text)} characters")
        print(f"   First 100 chars: {response.text[:100]}...")
        
        # Try to parse for medications
        if "Lisinopril" in response.text and "Metformin" in response.text:
            print("✅ AI correctly identified medications!")
            return True
        else:
            print("⚠️ AI response doesn't contain expected medications")
            print(f"   Full response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n🎉 Gemini API is working correctly!")
        print("You can now run the OCR tests again.")
    else:
        print("\n❌ Gemini API test failed!")
        print("Please check your API key configuration.")
