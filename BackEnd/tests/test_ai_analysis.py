#!/usr/bin/env python3
"""
Debug script to test AI prescription analysis directly
"""
import asyncio
import json
from services.ai_service import AIService

async def test_ai_prescription_analysis():
    """Test the AI prescription analysis directly"""
    try:
        ai_service = AIService()
        
        # Test with one of the prescriptions from the test script
        test_prescription = """PRESCRIPTION

Patient: Jane Doe
Date: January 20, 2024

Rx:
1. Lisinopril 10mg - Take 1 tablet once daily for blood pressure
2. Metformin 500mg - Take 1 tablet twice daily with meals for diabetes
3. Atorvastatin 20mg - Take 1 tablet at bedtime for cholesterol

Dr. Michael Johnson, MD
Cardiology Associates
License: 12345
Refills: 3 months"""
        
        print("🧪 Testing AI prescription analysis...")
        print(f"Input text:\n{test_prescription}\n")
        
        result = await ai_service.analyze_prescription_text(test_prescription)
        
        print("✅ AI Analysis Result:")
        print(json.dumps(result, indent=2))
        
        # Check if medications were extracted
        medications = result.get("medications", [])
        print(f"\n📊 Extracted {len(medications)} medications:")
        for i, med in enumerate(medications, 1):
            print(f"  {i}. {med.get('name', 'Unknown')} - {med.get('dosage', '')} - {med.get('frequency', '')}")
        
        return len(medications) > 0
        
    except Exception as e:
        print(f"❌ Error in AI analysis: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_prescription_analysis())
    if success:
        print("\n🎉 AI prescription analysis is working!")
    else:
        print("\n❌ AI prescription analysis failed!")
