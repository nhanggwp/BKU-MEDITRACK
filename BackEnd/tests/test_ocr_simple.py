#!/usr/bin/env python3
"""
Simple MediTrack OCR Test Script using requests
"""

import requests
import json
import sys

class SimpleMediTrackOCRTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.auth_token = None
        self.user_id = None
    
    def make_request(self, method: str, endpoint: str, data: dict = None, include_auth: bool = True):
        """Make HTTP request using requests library"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if include_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {"status": -1, "error": f"Unsupported method: {method}"}
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return {
                "status": response.status_code,
                "data": response_data
            }
        except Exception as e:
            return {"status": -1, "error": str(e)}
    
    def authenticate(self, email: str, password: str = "test123"):
        """Authenticate user"""
        print("🔐 Authenticating...")
        
        # Try signup first (might fail if user exists)
        signup_data = {
            "email": email,
            "password": password,
            "full_name": "OCR Test User",
            "phone": "+1234567890"
        }
        
        signup_result = self.make_request("POST", "/api/auth/signup", signup_data, include_auth=False)
        print(f"  📝 Signup status: {signup_result['status']}")
        
        # Sign in
        signin_data = {"email": email, "password": password}
        signin_result = self.make_request("POST", "/api/auth/signin", signin_data, include_auth=False)
        
        if signin_result["status"] != 200:
            print(f"❌ Authentication failed: {signin_result}")
            return False
        
        # Extract token
        signin_data = signin_result["data"]
        self.auth_token = signin_data.get("session", {}).get("access_token")
        self.user_id = signin_data.get("user", {}).get("id")
        
        if not self.auth_token:
            print("❌ No access token received")
            return False
        
        print(f"✅ Authentication successful")
        return True
    
    def test_prescription_analysis(self):
        """Test prescription analysis with sample data"""
        print("\\n🤖 Testing prescription analysis...")
        
        # Sample prescription text
        sample_prescription = """
MEDICAL CENTER PRESCRIPTION

Patient: John Smith
Date: January 25, 2024
DOB: 05/15/1980

MEDICATIONS:
1. Lisinopril 10mg - Take 1 tablet once daily for blood pressure
2. Metformin 500mg - Take 1 tablet twice daily with meals
3. Atorvastatin 20mg - Take 1 tablet at bedtime
4. Aspirin 81mg - Take 1 tablet daily for heart protection

Dr. Sarah Johnson, MD
Internal Medicine
License: MD98765
Refills: 90 days

Notes: Monitor blood pressure and blood sugar
Next appointment: 3 months
"""
        
        analysis_data = {
            "raw_ocr_text": sample_prescription.strip(),
            "confidence_score": 0.85,
            "source_type": "printed"
        }
        
        result = self.make_request("POST", "/api/ocr/analyze-prescription", analysis_data)
        
        if result["status"] not in [200, 201]:
            print(f"❌ Prescription analysis failed: {result}")
            return None
        
        analysis_result = result["data"]
        upload_id = analysis_result["upload_id"]
        medicines_count = analysis_result["medicines_count"]
        ai_analysis = analysis_result["ai_analysis"]
        
        print(f"✅ Prescription analysis successful:")
        print(f"   - Upload ID: {upload_id}")
        print(f"   - Medicines extracted: {medicines_count}")
        print(f"   - AI confidence: {ai_analysis.get('confidence', 'N/A')}")
        
        if ai_analysis.get("medications"):
            print(f"   - Medications found:")
            for med in ai_analysis["medications"]:
                name = med.get("name", "Unknown")
                dosage = med.get("dosage", "")
                frequency = med.get("frequency", "")
                print(f"     • {name} {dosage} - {frequency}")
        
        return upload_id
    
    def test_upload_retrieval(self, upload_id: str):
        """Test retrieving uploaded prescription data"""
        print(f"\\n📖 Testing upload retrieval for {upload_id}...")
        
        result = self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if result["status"] != 200:
            print(f"❌ Failed to retrieve upload: {result}")
            return False
        
        upload_data = result["data"]["upload"]
        medicines = upload_data.get("extracted_medicines", [])
        
        print(f"✅ Upload retrieved successfully:")
        print(f"   - Raw OCR text length: {len(upload_data.get('raw_ocr_text', ''))}")
        print(f"   - Confidence score: {upload_data.get('confidence_score', 'N/A')}")
        print(f"   - Extracted medicines: {len(medicines)}")
        print(f"   - Processed: {upload_data.get('processed', False)}")
        
        if medicines:
            print("   - Medicine details:")
            for med in medicines:
                name = med.get("extracted_name", "Unknown")
                dosage = med.get("dosage", "")
                frequency = med.get("frequency", "")
                confidence = med.get("confidence_score", 0)
                print(f"     • {name} {dosage} - {frequency} (confidence: {confidence})")
        
        return True
    
    def test_drug_interactions(self, upload_id: str):
        """Test drug interaction checking"""
        print(f"\\n⚠️ Testing drug interaction check...")
        
        # Get prescription data first
        result = self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if result["status"] != 200:
            print(f"❌ Failed to get prescription data")
            return False
        
        upload_data = result["data"]["upload"]
        medicines = upload_data.get("extracted_medicines", [])
        
        if len(medicines) < 2:
            print("❌ Need at least 2 medicines for interaction check")
            return False
        
        medication_names = [med.get("extracted_name", "") for med in medicines if med.get("extracted_name")]
        
        interaction_data = {
            "medications": medication_names,
            "check_type": "comprehensive"
        }
        
        result = self.make_request("POST", "/api/interactions/check", interaction_data)
        
        if result["status"] != 200:
            print(f"❌ Drug interaction check failed: {result}")
            return False
        
        interaction_result = result["data"]
        interactions_found = len(interaction_result.get("interactions", []))
        overall_risk = interaction_result.get("overall_risk", "unknown")
        
        print(f"✅ Drug interaction check completed:")
        print(f"   - Medications checked: {len(medication_names)}")
        print(f"   - Interactions found: {interactions_found}")
        print(f"   - Overall risk level: {overall_risk}")
        
        return True
    
    def test_ai_explanation(self, upload_id: str):
        """Test AI explanation generation"""
        print(f"\\n🧠 Testing AI explanation generation...")
        
        # Get prescription data
        result = self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if result["status"] != 200:
            print(f"❌ Failed to get prescription data")
            return False
        
        upload_data = result["data"]["upload"]
        medicines = upload_data.get("extracted_medicines", [])
        
        if not medicines:
            print("❌ No medicines found for explanation")
            return False
        
        medication_names = [med.get("extracted_name", "") for med in medicines if med.get("extracted_name")]
        
        explanation_data = {
            "medication_list": medication_names,
            "include_medical_history": True,
            "format": "markdown"
        }
        
        result = self.make_request("POST", "/api/ai/explain", explanation_data)
        
        if result["status"] != 200:
            print(f"❌ AI explanation generation failed: {result}")
            return False
        
        explanation_result = result["data"]
        explanation_text = explanation_result.get("explanation", "")
        
        print(f"✅ AI explanation generated:")
        print(f"   - Medications: {', '.join(medication_names)}")
        print(f"   - Explanation length: {len(explanation_text)} characters")
        print(f"   - Cached: {explanation_result.get('cached', False)}")
        
        return True
    
    def run_test(self, email: str):
        """Run the complete test"""
        print("🚀 Starting MediTrack OCR Test\\n")
        
        # Authenticate
        if not self.authenticate(email):
            print("❌ Test failed at authentication")
            return False
        
        # Test prescription analysis
        upload_id = self.test_prescription_analysis()
        if not upload_id:
            print("❌ Test failed at prescription analysis")
            return False
        
        # Test upload retrieval
        if not self.test_upload_retrieval(upload_id):
            print("❌ Test failed at upload retrieval")
            return False
        
        # Test drug interactions
        if not self.test_drug_interactions(upload_id):
            print("⚠️ Drug interaction test failed (this might be expected if TWOSIDES data isn't loaded)")
        
        # Test AI explanation
        if not self.test_ai_explanation(upload_id):
            print("⚠️ AI explanation test failed (check if Gemini API is configured)")
        
        print("\\n✅ Core OCR functionality test completed successfully!")
        print(f"\\n💡 Your OCR upload ID: {upload_id}")
        print("Check your Supabase database 'ocr_uploads' and 'extracted_medicines' tables")
        
        return True

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    if len(sys.argv) > 2:
        email = sys.argv[2]
    else:
        email = "testuser2@gmail.com"
    
    print(f"Testing OCR flow at: {base_url}")
    print(f"Using test email: {email}")
    
    tester = SimpleMediTrackOCRTester(base_url)
    success = tester.run_test(email)
    
    if success:
        print("\\n🎉 Test completed successfully!")
    else:
        print("\\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
