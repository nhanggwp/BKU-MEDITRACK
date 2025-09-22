#!/usr/bin/env python3
"""
MediTrack OCR Flow Testing Script

This script tests the complete OCR flow:
1. User authentication
2. OCR text upload and AI analysis
3. Prescription data extraction and storage
4. Medicine retrieval and verification

Usage:
    python test_ocr_flow.py [--base-url http://localhost:8000] [--test-user-email test@example.com]
"""

import asyncio
import aiohttp
import json
import argparse
from typing import Dict, Any, List

class OCRFlowTester:
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
    
    def get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if include_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, include_auth: bool = True):
        """Make HTTP request"""
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
            elif method.upper() == "PUT":
                async with self.session.put(url, headers=headers, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
        except Exception as e:
            return {"status": -1, "error": str(e)}
    
    async def test_authentication(self, email: str, password: str = "test123") -> bool:
        """Test authentication flow"""
        print("🔐 Testing authentication...")
        
        # Test signup (might fail if user exists, that's ok)
        signup_data = {
            "email": email,
            "password": password,
            "full_name": "OCR Test User",
            "phone": "+1234567890"
        }
        
        signup_result = await self.make_request("POST", "/api/auth/signup", signup_data, include_auth=False)
        print(f"  📝 Signup status: {signup_result['status']}")
        
        # Test signin
        signin_data = {"email": email, "password": password}
        signin_result = await self.make_request("POST", "/api/auth/signin", signin_data, include_auth=False)
        
        if signin_result["status"] != 200:
            print(f"❌ Authentication failed: {signin_result}")
            return False
        
        # Extract token and user ID
        signin_data = signin_result["data"]
        self.auth_token = signin_data.get("session", {}).get("access_token")
        self.user_id = signin_data.get("user", {}).get("id")
        
        if not self.auth_token:
            print("❌ No access token received")
            return False
        
        print(f"✅ Authentication successful, User ID: {self.user_id}")
        return True
    
    async def test_basic_ocr_upload(self) -> str:
        """Test basic OCR data upload"""
        print("\n📤 Testing basic OCR upload...")
        
        sample_ocr_data = {
            "raw_ocr_text": "Dr. Smith Medical Center\\nPatient: John Doe\\nDate: 2024-01-15\\n\\nPrescription:\\n1. Lisinopril 10mg - Take once daily\\n2. Metformin 500mg - Take twice daily with meals\\n3. Aspirin 81mg - Take once daily\\n\\nDr. Sarah Smith, MD\\nLicense: MD12345",
            "confidence_score": 0.85,
            "source_type": "printed"
        }
        
        result = await self.make_request("POST", "/api/ocr/upload", sample_ocr_data)
        
        if result["status"] not in [200, 201]:
            print(f"❌ OCR upload failed: {result}")
            return None
        
        upload_id = result["data"]["upload_id"]
        print(f"✅ OCR upload successful, Upload ID: {upload_id}")
        return upload_id
    
    async def test_ai_prescription_analysis(self) -> str:
        """Test AI-powered prescription analysis"""
        print("\n🤖 Testing AI prescription analysis...")
        
        # Sample prescription texts to test different scenarios
        test_prescriptions = [
            {
                "name": "Clear typed prescription",
                "text": "PRESCRIPTION\\n\\nPatient: Jane Doe\\nDate: January 20, 2024\\n\\nRx:\\n1. Lisinopril 10mg - Take 1 tablet once daily for blood pressure\\n2. Metformin 500mg - Take 1 tablet twice daily with meals for diabetes\\n3. Atorvastatin 20mg - Take 1 tablet at bedtime for cholesterol\\n\\nDr. Michael Johnson, MD\\nCardiology Associates\\nLicense: 12345\\nRefills: 3 months",
                "confidence": 0.9,
                "source": "printed"
            },
            {
                "name": "Handwritten-style prescription",
                "text": "Dr Sarah Lee\\nInternal Medicine\\n\\nPt: Robert Smith\\nDOB: 03/15/1975\\n\\nRx:\\nAmoxicillin 500mg\\nTake 1 cap TID x 7 days\\n\\nIbuprofen 200mg\\nTake 1-2 tabs q6h PRN pain\\n\\nSignature: Dr. S. Lee\\nDEA: BL1234567",
                "confidence": 0.7,
                "source": "handwritten"
            },
            {
                "name": "Complex multi-drug prescription",
                "text": "VALLEY MEDICAL CENTER\\nPhysician: Dr. Amanda Rodriguez\\nSpecialty: Endocrinology\\n\\nPatient: Maria Garcia\\nMRN: 98765\\nDate: 02/10/2024\\n\\nMEDICATIONS:\\n1. Metformin XR 1000mg - Take 1 tablet twice daily\\n2. Insulin Glargine (Lantus) 25 units - Inject subcutaneously at bedtime\\n3. Lisinopril/HCTZ 10/12.5mg - Take 1 tablet daily\\n4. Simvastatin 40mg - Take 1 tablet at bedtime\\n5. Aspirin 81mg - Take 1 tablet daily\\n\\nNext appointment: 3 months\\nLab work: A1C, lipid panel in 6 weeks",
                "confidence": 0.85,
                "source": "mixed"
            }
        ]
        
        analysis_results = []
        
        for i, prescription in enumerate(test_prescriptions, 1):
            print(f"\\n  📋 Testing prescription {i}: {prescription['name']}")
            
            analysis_data = {
                "raw_ocr_text": prescription["text"],
                "confidence_score": prescription["confidence"],
                "source_type": prescription["source"]
            }
            
            result = await self.make_request("POST", "/api/ocr/analyze-prescription", analysis_data)
            
            if result["status"] not in [200, 201]:
                print(f"    ❌ Analysis failed: {result}")
                continue
            
            analysis_result = result["data"]
            upload_id = analysis_result["upload_id"]
            medicines_count = analysis_result["medicines_count"]
            ai_analysis = analysis_result["ai_analysis"]
            
            print(f"    ✅ Analysis successful:")
            print(f"       - Upload ID: {upload_id}")
            print(f"       - Medicines extracted: {medicines_count}")
            print(f"       - AI confidence: {ai_analysis.get('confidence', 'N/A')}")
            
            if ai_analysis.get("medications"):
                print(f"       - Medications found:")
                for med in ai_analysis["medications"]:
                    print(f"         • {med.get('name', 'Unknown')} {med.get('dosage', '')} - {med.get('frequency', '')}")
            
            analysis_results.append({
                "upload_id": upload_id,
                "prescription_name": prescription["name"],
                "medicines_count": medicines_count,
                "ai_analysis": ai_analysis
            })
        
        print(f"\\n✅ AI prescription analysis completed: {len(analysis_results)} prescriptions processed")
        return analysis_results
    
    async def test_ocr_retrieval(self, upload_ids: List[str]):
        """Test retrieving OCR uploads and extracted medicines"""
        print("\\n📖 Testing OCR data retrieval...")
        
        # Test getting all uploads
        result = await self.make_request("GET", "/api/ocr/uploads?limit=10")
        
        if result["status"] != 200:
            print(f"❌ Failed to retrieve uploads: {result}")
            return False
        
        uploads = result["data"]["uploads"]
        print(f"✅ Retrieved {len(uploads)} OCR uploads")
        
        # Test getting specific uploads with medicines
        for upload_id in upload_ids[:2]:  # Test first 2 uploads
            result = await self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
            
            if result["status"] != 200:
                print(f"❌ Failed to retrieve upload {upload_id}: {result}")
                continue
            
            upload_data = result["data"]["upload"]
            medicines_count = len(upload_data.get("extracted_medicines", []))
            
            print(f"✅ Upload {upload_id}: {medicines_count} medicines extracted")
            
            # Print medicine details
            if upload_data.get("extracted_medicines"):
                print("   Extracted medicines:")
                for med in upload_data["extracted_medicines"]:
                    name = med.get("extracted_name", "Unknown")
                    dosage = med.get("dosage", "")
                    frequency = med.get("frequency", "")
                    print(f"   • {name} {dosage} - {frequency}")
        
        return True
    
    async def test_prescription_review_and_verification(self, upload_id: str):
        """Test reviewing and verifying prescription data"""
        print(f"\\n🔍 Testing prescription review for upload {upload_id}...")
        
        # First, get the current prescription data
        result = await self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if result["status"] != 200:
            print(f"❌ Failed to get prescription data: {result}")
            return False
        
        upload_data = result["data"]["upload"]
        current_medicines = upload_data.get("extracted_medicines", [])
        
        if not current_medicines:
            print("❌ No medicines found to review")
            return False
        
        # Simulate user review - modify the first medicine
        reviewed_medicines = []
        for i, med in enumerate(current_medicines):
            reviewed_med = {
                "extracted_name": med.get("extracted_name"),
                "dosage": med.get("dosage"),
                "frequency": med.get("frequency"),
                "duration": med.get("duration"),
                "confidence_score": 0.95,  # User verification increases confidence
                "medication_id": None
            }
            
            # Simulate user correction on first medicine
            if i == 0:
                reviewed_med["dosage"] = "10mg (corrected by user)"
                reviewed_med["frequency"] = "Once daily (corrected)"
            
            reviewed_medicines.append(reviewed_med)
        
        # Submit review
        review_data = {
            "ocr_upload_id": upload_id,
            "medicines": reviewed_medicines,
            "verified": True
        }
        
        result = await self.make_request("PUT", f"/api/ocr/uploads/{upload_id}/review", review_data)
        
        if result["status"] != 200:
            print(f"❌ Prescription review failed: {result}")
            return False
        
        print("✅ Prescription review and verification successful")
        print(f"   - Reviewed {len(reviewed_medicines)} medicines")
        print(f"   - First medicine corrected: {reviewed_medicines[0]['extracted_name']}")
        
        return True
    
    async def test_drug_interaction_check(self, upload_id: str):
        """Test drug interaction checking with extracted medicines"""
        print(f"\\n⚠️ Testing drug interaction check for upload {upload_id}...")
        
        # Get the prescription data
        result = await self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if result["status"] != 200:
            print(f"❌ Failed to get prescription data: {result}")
            return False
        
        upload_data = result["data"]["upload"]
        medicines = upload_data.get("extracted_medicines", [])
        
        if len(medicines) < 2:
            print("❌ Need at least 2 medicines for interaction check")
            return False
        
        # Extract medicine names for interaction check
        medication_names = [med.get("extracted_name", "") for med in medicines if med.get("extracted_name")]
        
        interaction_data = {
            "medications": medication_names,
            "check_type": "comprehensive"
        }
        
        result = await self.make_request("POST", "/api/interactions/check", interaction_data)
        
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
        
        if interactions_found > 0:
            print("   - Interaction details:")
            for interaction in interaction_result.get("interactions", [])[:3]:  # Show first 3
                drug1 = interaction.get("drug1_name", "Unknown")
                drug2 = interaction.get("drug2_name", "Unknown")
                severity = interaction.get("severity", "unknown")
                print(f"     • {drug1} + {drug2}: {severity} risk")
        
        return True
    
    async def test_ai_explanation_generation(self, upload_id: str):
        """Test AI explanation generation for extracted medicines"""
        print(f"\\n🧠 Testing AI explanation generation for upload {upload_id}...")
        
        # Get the prescription data
        result = await self.make_request("GET", f"/api/ocr/uploads/{upload_id}")
        
        if result["status"] != 200:
            print(f"❌ Failed to get prescription data: {result}")
            return False
        
        upload_data = result["data"]["upload"]
        medicines = upload_data.get("extracted_medicines", [])
        
        if not medicines:
            print("❌ No medicines found for explanation")
            return False
        
        # Extract medicine names
        medication_names = [med.get("extracted_name", "") for med in medicines if med.get("extracted_name")]
        
        explanation_data = {
            "medication_list": medication_names,
            "include_medical_history": True,
            "format": "markdown"
        }
        
        result = await self.make_request("POST", "/api/ai/explain", explanation_data)
        
        if result["status"] != 200:
            print(f"❌ AI explanation generation failed: {result}")
            return False
        
        explanation_result = result["data"]
        explanation_text = explanation_result.get("explanation", "")
        
        print(f"✅ AI explanation generated:")
        print(f"   - Medications: {', '.join(medication_names)}")
        print(f"   - Explanation length: {len(explanation_text)} characters")
        print(f"   - Cached: {explanation_result.get('cached', False)}")
        
        # Show first 200 characters of explanation
        if explanation_text:
            preview = explanation_text[:200] + "..." if len(explanation_text) > 200 else explanation_text
            print(f"   - Preview: {preview}")
        
        return True
    
    async def test_cleanup(self, upload_ids: List[str]):
        """Test deleting OCR uploads (cleanup)"""
        print(f"\\n🗑️ Testing cleanup (deleting {len(upload_ids)} uploads)...")
        
        deleted_count = 0
        for upload_id in upload_ids:
            result = await self.make_request("DELETE", f"/api/ocr/uploads/{upload_id}")
            
            if result["status"] == 200:
                deleted_count += 1
                print(f"   ✅ Deleted upload {upload_id}")
            else:
                print(f"   ❌ Failed to delete upload {upload_id}: {result}")
        
        print(f"✅ Cleanup completed: {deleted_count}/{len(upload_ids)} uploads deleted")
        return deleted_count == len(upload_ids)
    
    async def run_complete_test(self, test_email: str) -> Dict[str, bool]:
        """Run complete OCR flow test"""
        print("🚀 Starting MediTrack OCR Flow Test\\n")
        
        results = {}
        
        # Test authentication
        auth_success = await self.test_authentication(test_email)
        results["authentication"] = auth_success
        
        if not auth_success:
            print("❌ Authentication failed, stopping tests")
            return results
        
        # Test basic OCR upload
        basic_upload_id = await self.test_basic_ocr_upload()
        results["basic_ocr_upload"] = basic_upload_id is not None
        
        # Test AI prescription analysis
        analysis_results = await self.test_ai_prescription_analysis()
        results["ai_prescription_analysis"] = len(analysis_results) > 0
        
        # Collect all upload IDs
        upload_ids = []
        if basic_upload_id:
            upload_ids.append(basic_upload_id)
        
        for analysis in analysis_results:
            upload_ids.append(analysis["upload_id"])
        
        # Test OCR retrieval
        if upload_ids:
            results["ocr_retrieval"] = await self.test_ocr_retrieval(upload_ids)
            
            # Use an AI-analyzed upload (with medicines) for the subsequent tests
            # Skip the basic upload (index 0) and use an AI upload that has medicines
            test_upload_id = upload_ids[1] if len(upload_ids) > 1 else upload_ids[0]
            
            # Test prescription review
            results["prescription_review"] = await self.test_prescription_review_and_verification(test_upload_id)
            
            # Test drug interaction check
            results["drug_interaction_check"] = await self.test_drug_interaction_check(test_upload_id)
            
            # Test AI explanation
            results["ai_explanation"] = await self.test_ai_explanation_generation(test_upload_id)
            
            # Test cleanup (optional - comment out if you want to keep test data)
            # results["cleanup"] = await self.test_cleanup(upload_ids)
        
        return results
    
    def print_test_summary(self, results: Dict[str, bool]):
        """Print test results summary"""
        print("\\n" + "="*50)
        print("📊 MediTrack OCR Flow Test Summary")
        print("="*50)
        
        total_tests = len(results)
        passed_tests = sum(1 for success in results.values() if success)
        
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            test_display = test_name.replace("_", " ").title()
            print(f"{status} - {test_display}")
        
        print(f"\\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! OCR flow is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
        
        print("\\n💡 Next steps:")
        print("- Check your Supabase database for the stored OCR data")
        print("- Test the client app with real image uploads")
        print("- Verify drug interaction detection works with your TWOSIDES data")

async def main():
    parser = argparse.ArgumentParser(description="Test MediTrack OCR flow")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--test-user-email", default="testuser2@gmail.com", help="Test user email")
    
    args = parser.parse_args()
    
    async with OCRFlowTester(args.base_url) as tester:
        results = await tester.run_complete_test(args.test_user_email)
        tester.print_test_summary(results)

if __name__ == "__main__":
    asyncio.run(main())
