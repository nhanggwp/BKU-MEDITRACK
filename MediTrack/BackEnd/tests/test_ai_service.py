#!/usr/bin/env python3
"""
Comprehensive test suite for AIService
"""
import asyncio
import json
from unittest.mock import Mock, patch
from services.ai_service import AIService


class TestAIService:
    """Test class for AIService functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ai_service = AIService()
        
        # Sample test data
        self.sample_medications = ["Lisinopril 10mg", "Metformin 500mg", "Atorvastatin 20mg"]
        
        self.sample_interactions = [
            {
                "drug1_name": "Lisinopril",
                "drug2_name": "Metformin", 
                "severity": "moderate",
                "description": "May increase risk of lactic acidosis"
            },
            {
                "drug1_name": "Atorvastatin",
                "drug2_name": "Lisinopril",
                "severity": "minor", 
                "description": "Minor interaction - monitor liver function"
            }
        ]
        
        self.sample_medical_history = [
            {
                "conditions": {"name": "Diabetes", "severity": "moderate"},
                "is_active": True
            },
            {
                "conditions": {"name": "Hypertension", "severity": "mild"},
                "is_active": True
            }
        ]
        
        self.sample_allergies = [
            {"allergen": "Penicillin", "severity": "high", "reaction": "Rash"},
            {"allergen": "Shellfish", "severity": "moderate", "reaction": "Swelling"}
        ]
        
        self.sample_prescription_text = """PRESCRIPTION

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

    def test_ai_service_initialization(self):
        """Test AI service initialization"""
        ai_service = AIService()
        
        # Check that the service is properly initialized
        assert ai_service.settings is not None
        assert ai_service.model is not None
        assert hasattr(ai_service.model, 'generate_content')
        
        print("✅ AI service initialization test passed")

    def test_build_medical_context(self):
        """Test building medical context for prompts"""
        self.setUp()
        
        context = self.ai_service._build_medical_context(
            medications=self.sample_medications,
            interactions=self.sample_interactions,
            medical_history=self.sample_medical_history,
            allergies=self.sample_allergies
        )
        
        # Verify context structure
        assert "medications" in context
        assert "total_medications" in context
        assert "interactions" in context
        assert "interaction_count" in context
        assert "medical_conditions" in context
        assert "allergies" in context
        
        # Verify content
        assert context["total_medications"] == 3
        assert context["interaction_count"] == 2
        assert len(context["medical_conditions"]) == 2
        assert len(context["allergies"]) == 2
        
        # Check medical conditions extraction
        conditions = [cond["condition"] for cond in context["medical_conditions"]]
        assert "Diabetes" in conditions
        assert "Hypertension" in conditions
        
        # Check allergies extraction
        allergens = [allergy["allergen"] for allergy in context["allergies"]]
        assert "Penicillin" in allergens
        assert "Shellfish" in allergens
        
        print("✅ Build medical context test passed")

    def test_assess_overall_risk(self):
        """Test risk assessment logic"""
        self.setUp()
        
        # Test with no interactions
        risk = self.ai_service._assess_overall_risk([])
        assert risk == "minor"
        
        # Test with minor interactions
        minor_interactions = [{"severity": "minor"}]
        risk = self.ai_service._assess_overall_risk(minor_interactions)
        assert risk == "minor"
        
        # Test with moderate interactions
        moderate_interactions = [{"severity": "moderate"}]
        risk = self.ai_service._assess_overall_risk(moderate_interactions)
        assert risk == "moderate"
        
        # Test with major interactions
        major_interactions = [{"severity": "major"}]
        risk = self.ai_service._assess_overall_risk(major_interactions)
        assert risk == "major"
        
        # Test with mixed interactions (should return highest)
        mixed_interactions = [
            {"severity": "minor"},
            {"severity": "major"},
            {"severity": "moderate"}
        ]
        risk = self.ai_service._assess_overall_risk(mixed_interactions)
        assert risk == "major"
        
        print("✅ Risk assessment test passed")

    def test_create_risk_explanation_prompt(self):
        """Test risk explanation prompt creation"""
        self.setUp()
        
        context = self.ai_service._build_medical_context(
            medications=self.sample_medications,
            interactions=self.sample_interactions,
            medical_history=self.sample_medical_history,
            allergies=self.sample_allergies
        )
        
        prompt = self.ai_service._create_risk_explanation_prompt(context)
        
        # Verify prompt contains key information
        assert "Lisinopril 10mg" in prompt
        assert "Metformin 500mg" in prompt
        assert "Atorvastatin 20mg" in prompt
        assert "Diabetes" in prompt
        assert "Hypertension" in prompt
        assert "Penicillin" in prompt
        assert "**Drug Interactions Found:** 2" in prompt
        assert "Overall Safety Assessment" in prompt
        assert "Key Interactions" in prompt
        assert "Recommendations" in prompt
        
        print("✅ Risk explanation prompt test passed")

    @patch('google.generativeai.GenerativeModel.generate_content')
    async def test_generate_risk_explanation(self, mock_generate):
        """Test generating risk explanation"""
        self.setUp()
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = """
# Overall Safety Assessment
Your medication combination has moderate risk due to potential interactions.

# Key Interactions
- Lisinopril and Metformin may increase risk of lactic acidosis
- Monitor kidney function regularly

# Recommendations
- Take medications as prescribed
- Monitor for signs of kidney problems
- Contact doctor if experiencing unusual symptoms
"""
        mock_generate.return_value = mock_response
        
        result = await self.ai_service.generate_risk_explanation(
            medications=self.sample_medications,
            interactions=self.sample_interactions,
            user_medical_history=self.sample_medical_history,
            user_allergies=self.sample_allergies
        )
        
        # Verify result structure
        assert "explanation" in result
        assert "format" in result
        assert "medications_analyzed" in result
        assert "interactions_found" in result
        assert "risk_level" in result
        assert "prompt_used" in result
        assert "tokens_used" in result
        
        # Verify content
        assert result["format"] == "markdown"
        assert result["medications_analyzed"] == self.sample_medications
        assert result["interactions_found"] == 2
        assert result["risk_level"] == "moderate"
        assert "Overall Safety Assessment" in result["explanation"]
        
        print("✅ Generate risk explanation test passed")

    @patch('google.generativeai.GenerativeModel.generate_content')
    async def test_analyze_prescription_text(self, mock_generate):
        """Test prescription text analysis"""
        self.setUp()
        
        # Mock AI response with JSON
        mock_response = Mock()
        mock_response.text = """{
    "medications": [
        {
            "name": "Lisinopril",
            "dosage": "10mg",
            "frequency": "once daily",
            "duration": null,
            "instructions": "Take 1 tablet for blood pressure"
        },
        {
            "name": "Metformin",
            "dosage": "500mg", 
            "frequency": "twice daily",
            "duration": null,
            "instructions": "Take 1 tablet with meals for diabetes"
        },
        {
            "name": "Atorvastatin",
            "dosage": "20mg",
            "frequency": "at bedtime",
            "duration": null,
            "instructions": "Take 1 tablet for cholesterol"
        }
    ],
    "doctor_info": {
        "name": "Michael Johnson",
        "clinic": "Cardiology Associates"
    },
    "prescription_date": "January 20, 2024",
    "confidence": "high"
}"""
        mock_generate.return_value = mock_response
        
        result = await self.ai_service.analyze_prescription_text(self.sample_prescription_text)
        
        # Verify result structure
        assert "medications" in result
        assert "doctor_info" in result
        assert "prescription_date" in result
        assert "confidence" in result
        
        # Verify content
        assert len(result["medications"]) == 3
        assert result["doctor_info"]["name"] == "Michael Johnson"
        assert result["doctor_info"]["clinic"] == "Cardiology Associates"
        assert result["prescription_date"] == "January 20, 2024"
        assert result["confidence"] == "high"
        
        # Verify first medication
        first_med = result["medications"][0]
        assert first_med["name"] == "Lisinopril"
        assert first_med["dosage"] == "10mg"
        assert first_med["frequency"] == "once daily"
        
        print("✅ Analyze prescription text test passed")

    @patch('google.generativeai.GenerativeModel.generate_content')
    async def test_analyze_prescription_text_with_markdown(self, mock_generate):
        """Test prescription analysis with markdown-wrapped JSON"""
        self.setUp()
        
        # Mock AI response with markdown code block
        mock_response = Mock()
        mock_response.text = """```json
{
    "medications": [
        {
            "name": "Aspirin",
            "dosage": "81mg",
            "frequency": "once daily",
            "duration": null,
            "instructions": "Take with food"
        }
    ],
    "doctor_info": {
        "name": "Dr. Smith",
        "clinic": "Family Medicine"
    },
    "prescription_date": "March 15, 2024",
    "confidence": "medium"
}
```"""
        mock_generate.return_value = mock_response
        
        result = await self.ai_service.analyze_prescription_text("Simple prescription text")
        
        # Verify it properly extracted from markdown
        assert len(result["medications"]) == 1
        assert result["medications"][0]["name"] == "Aspirin"
        assert result["doctor_info"]["name"] == "Dr. Smith"
        assert result["confidence"] == "medium"
        
        print("✅ Analyze prescription with markdown test passed")

    @patch('google.generativeai.GenerativeModel.generate_content')
    async def test_analyze_prescription_text_fallback(self, mock_generate):
        """Test prescription analysis fallback for invalid JSON"""
        self.setUp()
        
        # Mock AI response with invalid JSON
        mock_response = Mock()
        mock_response.text = "This is not valid JSON response from AI"
        mock_generate.return_value = mock_response
        
        result = await self.ai_service.analyze_prescription_text("Some prescription text")
        
        # Verify fallback structure
        assert "medications" in result
        assert "doctor_info" in result
        assert "prescription_date" in result
        assert "confidence" in result
        assert "raw_response" in result
        
        # Verify fallback values
        assert result["medications"] == []
        assert result["confidence"] == "low"
        assert result["raw_response"] == "This is not valid JSON response from AI"
        
        print("✅ Analyze prescription fallback test passed")

    @patch('google.generativeai.GenerativeModel.generate_content')
    async def test_generate_medication_summary(self, mock_generate):
        """Test medication summary generation"""
        self.setUp()
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = """
**Emergency Medication List**

Current Medications:
• Lisinopril 10mg - once daily (blood pressure)
• Metformin 500mg - twice daily (diabetes)
• Atorvastatin 20mg - at bedtime (cholesterol)

**Critical Warnings:**
- Patient has diabetes and hypertension
- Monitor for kidney function changes

**Emergency Contact:** Call primary physician at 555-0123
"""
        mock_generate.return_value = mock_response
        
        medications = [
            {"medication_name": "Lisinopril", "dosage": "10mg", "frequency": "once daily"},
            {"medication_name": "Metformin", "dosage": "500mg", "frequency": "twice daily"},
            {"medication_name": "Atorvastatin", "dosage": "20mg", "frequency": "at bedtime"}
        ]
        
        result = await self.ai_service.generate_medication_summary(medications)
        
        # Verify summary contains key information
        assert "Lisinopril" in result
        assert "Metformin" in result
        assert "Atorvastatin" in result
        assert "Emergency" in result
        
        print("✅ Generate medication summary test passed")

    @patch('google.generativeai.GenerativeModel.generate_content')
    async def test_generate_medication_summary_fallback(self, mock_generate):
        """Test medication summary fallback when AI fails"""
        self.setUp()
        
        # Mock AI exception
        mock_generate.side_effect = Exception("AI service unavailable")
        
        medications = [
            {"medication_name": "Aspirin", "dosage": "81mg", "frequency": "daily"}
        ]
        
        result = await self.ai_service.generate_medication_summary(medications)
        
        # Verify fallback format
        assert "• Aspirin 81mg daily" in result
        
        print("✅ Generate medication summary fallback test passed")

    def test_build_user_context(self):
        """Test building user context for prompts"""
        self.setUp()
        
        user_context = {
            "medical_history": self.sample_medical_history,
            "allergies": self.sample_allergies
        }
        
        context = self.ai_service._build_user_context(user_context)
        
        # Verify context contains medical history and allergies
        assert "Medical History:" in context
        assert "Known Allergies:" in context
        assert "Diabetes" in context
        assert "Hypertension" in context
        assert "Penicillin" in context
        assert "Shellfish" in context
        
        print("✅ Build user context test passed")

    def test_calculate_age(self):
        """Test age calculation"""
        self.setUp()
        
        # Test valid date
        age = self.ai_service._calculate_age("1990-01-01")
        assert isinstance(age, int)
        assert age > 30  # Should be around 34-35 years old
        
        # Test None date
        age = self.ai_service._calculate_age(None)
        assert age is None
        
        # Test invalid date
        age = self.ai_service._calculate_age("invalid-date")
        assert age is None
        
        print("✅ Calculate age test passed")

    def test_extract_risk_assessment(self):
        """Test risk assessment extraction"""
        self.setUp()
        
        summary_text = """
        Patient Overview: The patient shows HIGH RISK factors due to multiple medications.
        There is MODERATE RISK of drug interactions. CAUTION is advised when monitoring.
        Regular monitoring is recommended.
        """
        
        risk_assessment = self.ai_service._extract_risk_assessment(summary_text)
        
        # Verify risk extraction
        assert "identified_risks" in risk_assessment
        assert "overall_risk_level" in risk_assessment
        assert len(risk_assessment["identified_risks"]) > 0
        assert "high risk" in risk_assessment["identified_risks"]
        assert "moderate risk" in risk_assessment["identified_risks"]
        assert "caution" in risk_assessment["identified_risks"]
        
        print("✅ Extract risk assessment test passed")

    def test_extract_recommendations(self):
        """Test recommendations extraction"""
        self.setUp()
        
        summary_text = """
        Patient needs careful monitoring.
        
        RECOMMENDATIONS:
        - Monitor blood pressure daily
        - Check kidney function monthly
        - Avoid alcohol consumption
        
        Additional suggestions:
        - Regular exercise recommended
        - Follow up in 2 weeks
        """
        
        recommendations = self.ai_service._extract_recommendations(summary_text)
        
        # Verify recommendations extraction
        assert len(recommendations) >= 3
        assert any("blood pressure" in rec.lower() for rec in recommendations)
        assert any("kidney function" in rec.lower() for rec in recommendations)
        assert any("alcohol" in rec.lower() for rec in recommendations)
        
        print("✅ Extract recommendations test passed")

    def test_estimate_tokens(self):
        """Test token estimation"""
        self.setUp()
        
        # Test short text
        short_text = "Hello world"
        tokens = self.ai_service._estimate_tokens(short_text)
        assert tokens > 0
        assert tokens < 10
        
        # Test longer text
        long_text = "This is a much longer text that should have more tokens estimated. " * 10
        tokens = self.ai_service._estimate_tokens(long_text)
        assert tokens > 50
        
        print("✅ Token estimation test passed")

    async def test_generate_risk_explanation_error_handling(self):
        """Test error handling in risk explanation generation"""
        self.setUp()
        
        with patch.object(self.ai_service.model, 'generate_content', side_effect=Exception("AI Error")):
            try:
                await self.ai_service.generate_risk_explanation(
                    medications=self.sample_medications,
                    interactions=self.sample_interactions
                )
                assert False, "Should have raised an exception"
            except Exception as e:
                assert "AI explanation generation failed" in str(e)
        
        print("✅ Error handling test passed")

    async def test_analyze_prescription_text_error_handling(self):
        """Test error handling in prescription analysis"""
        self.setUp()
        
        with patch.object(self.ai_service.model, 'generate_content', side_effect=Exception("AI Error")):
            try:
                await self.ai_service.analyze_prescription_text("test prescription")
                assert False, "Should have raised an exception"
            except Exception as e:
                assert "Prescription analysis failed" in str(e)
        
        print("✅ Prescription analysis error handling test passed")


async def run_all_tests():
    """Run all AI service tests"""
    test_suite = TestAIService()
    
    print("🧪 Starting AI Service Test Suite\n")
    
    # Synchronous tests
    test_suite.test_ai_service_initialization()
    test_suite.test_build_medical_context()
    test_suite.test_assess_overall_risk()
    test_suite.test_create_risk_explanation_prompt()
    test_suite.test_build_user_context()
    test_suite.test_calculate_age()
    test_suite.test_extract_risk_assessment()
    test_suite.test_extract_recommendations()
    test_suite.test_estimate_tokens()
    
    # Asynchronous tests
    await test_suite.test_generate_risk_explanation()
    await test_suite.test_analyze_prescription_text()
    await test_suite.test_analyze_prescription_text_with_markdown()
    await test_suite.test_analyze_prescription_text_fallback()
    await test_suite.test_generate_medication_summary()
    await test_suite.test_generate_medication_summary_fallback()
    await test_suite.test_generate_risk_explanation_error_handling()
    await test_suite.test_analyze_prescription_text_error_handling()
    
    print("\n🎉 All AI Service tests completed successfully!")
    print("📊 Test Summary:")
    print("   ✅ Initialization: PASSED")
    print("   ✅ Context Building: PASSED")
    print("   ✅ Risk Assessment: PASSED")
    print("   ✅ Prompt Generation: PASSED")
    print("   ✅ Prescription Analysis: PASSED")
    print("   ✅ Medication Summary: PASSED")
    print("   ✅ Error Handling: PASSED")
    print("   ✅ Utility Functions: PASSED")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
