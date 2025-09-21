#!/usr/bin/env python3
"""
Debug script to test the full OCR flow step by step
"""
import asyncio
import aiohttp
import json

class OCRDebugTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.auth_token = None
        self.user_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_headers(self, include_auth: bool = True) -> dict:
        headers = {"Content-Type": "application/json"}
        if include_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, include_auth: bool = True):
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers(include_auth)
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
        except Exception as e:
            return {"status": -1, "error": str(e)}
    
    async def authenticate(self):
        """Quick authentication"""
        print("🔐 Authenticating...")
        signin_data = {"email": "testuser2@gmail.com", "password": "test123"}
        result = await self.make_request("POST", "/api/auth/signin", signin_data, include_auth=False)
        
        if result["status"] != 200:
            print(f"❌ Authentication failed: {result}")
            return False
        
        signin_response = result["data"]
        self.auth_token = signin_response.get("session", {}).get("access_token")
        self.user_id = signin_response.get("user", {}).get("id")
        
        print(f"✅ Authenticated as user: {self.user_id}")
        return True
    
    async def test_prescription_analysis_with_debug(self):
        """Test prescription analysis with detailed debugging"""
        print("\n🔍 Testing prescription analysis with debug info...")
        
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

        analysis_data = {
            "raw_ocr_text": test_prescription,
            "confidence_score": 0.9,
            "source_type": "printed"
        }
        
        print("📤 Sending prescription analysis request...")
        result = await self.make_request("POST", "/api/ocr/analyze-prescription", analysis_data)
        
        print(f"📊 Response status: {result['status']}")
        print(f"📄 Response data: {json.dumps(result['data'], indent=2)}")
        
        if result["status"] not in [200, 201]:
            print(f"❌ Analysis failed with status {result['status']}")
            return None
        
        # Extract upload ID from response
        response_data = result["data"]
        upload_id = response_data.get("upload_id")
        medicines_count = response_data.get("medicines_count", 0)
        ai_analysis = response_data.get("ai_analysis", {})
        
        print(f"\n✅ Analysis completed:")
        print(f"   Upload ID: {upload_id}")
        print(f"   Medicines count: {medicines_count}")
        print(f"   AI confidence: {ai_analysis.get('confidence', 'N/A')}")
        
        # Now get the upload details to see what was actually saved
        print(f"\n🔍 Fetching upload details for {upload_id}...")
        upload_result = await self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if upload_result["status"] == 200:
            upload_data = upload_result["data"]["upload"]
            extracted_medicines = upload_data.get("extracted_medicines", [])
            
            print(f"📊 Upload details:")
            print(f"   Extracted medicines in DB: {len(extracted_medicines)}")
            print(f"   Processing status: {upload_data.get('processed', 'Unknown')}")
            
            if extracted_medicines:
                print("   Medicines in database:")
                for i, med in enumerate(extracted_medicines, 1):
                    print(f"      {i}. {med.get('extracted_name', 'Unknown')} - {med.get('dosage', '')} - {med.get('frequency', '')}")
            else:
                print("   ⚠️ No medicines found in database!")
        else:
            print(f"❌ Failed to fetch upload details: {upload_result}")
        
        return {
            "upload_id": upload_id,
            "ai_medicines": len(ai_analysis.get("medications", [])),
            "db_medicines": len(extracted_medicines) if upload_result["status"] == 200 else 0
        }

async def main():
    async with OCRDebugTester() as tester:
        if await tester.authenticate():
            result = await tester.test_prescription_analysis_with_debug()
            
            if result:
                print(f"\n📈 Summary:")
                print(f"   AI extracted: {result['ai_medicines']} medicines")
                print(f"   DB saved: {result['db_medicines']} medicines")
                
                if result['ai_medicines'] > 0 and result['db_medicines'] == 0:
                    print("\n❌ ISSUE FOUND: AI is extracting medicines but they're not being saved to the database!")
                elif result['ai_medicines'] == result['db_medicines']:
                    print("\n✅ SUCCESS: AI extraction and database saving are working correctly!")
                else:
                    print(f"\n⚠️ PARTIAL ISSUE: AI extracted {result['ai_medicines']} but only {result['db_medicines']} were saved")

if __name__ == "__main__":
    asyncio.run(main())
