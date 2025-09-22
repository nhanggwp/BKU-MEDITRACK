import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
from config.settings import Settings

class AIService:
    def __init__(self):
        self.settings = Settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate_risk_explanation(
        self, 
        medications: List[str], 
        interactions: List[Dict[str, Any]], 
        user_medical_history: List[Dict[str, Any]] = None,
        user_allergies: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate plain-language explanation of medication risks using Gemini AI"""
        
        # Build context
        context = self._build_medical_context(medications, interactions, user_medical_history, user_allergies)
        
        # Create prompt
        prompt = self._create_risk_explanation_prompt(context)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.settings.ai_temperature,
                    max_output_tokens=self.settings.max_ai_tokens
                )
            )
            
            # Parse the response
            explanation = response.text
            
            return {
                "explanation": explanation,
                "format": "markdown",
                "medications_analyzed": medications,
                "interactions_found": len(interactions),
                "risk_level": self._assess_overall_risk(interactions),
                "prompt_used": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "tokens_used": len(explanation.split()) * 1.3  # Rough estimate
            }
            
        except Exception as e:
            raise Exception(f"AI explanation generation failed: {str(e)}")
    
    def _build_medical_context(
        self, 
        medications: List[str], 
        interactions: List[Dict[str, Any]], 
        medical_history: List[Dict[str, Any]] = None, 
        allergies: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build medical context for AI prompt"""
        
        context = {
            "medications": medications,
            "total_medications": len(medications),
            "interactions": interactions,
            "interaction_count": len(interactions),
            "medical_conditions": [],
            "allergies": []
        }
        
        if medical_history:
            context["medical_conditions"] = [
                {
                    "condition": hist.get("conditions", {}).get("name", "Unknown"),
                    "severity": hist.get("conditions", {}).get("severity", "unknown")
                }
                for hist in medical_history
            ]
        
        if allergies:
            context["allergies"] = [
                {
                    "allergen": allergy.get("allergen", ""),
                    "severity": allergy.get("severity", "unknown"),
                    "reaction": allergy.get("reaction", "")
                }
                for allergy in allergies
            ]
        
        return context
    
    def _create_risk_explanation_prompt(self, context: Dict[str, Any]) -> str:
        """Create detailed prompt for risk explanation"""
        
        medications_list = ", ".join(context["medications"])
        
        prompt = f"""
You are a medical AI assistant specializing in medication safety. Please provide a clear, easy-to-understand explanation about the medications and their potential interactions.

**Patient Information:**
- Medications: {medications_list}
- Number of medications: {context['total_medications']}
"""
        
        if context["medical_conditions"]:
            conditions = ", ".join([cond["condition"] for cond in context["medical_conditions"]])
            prompt += f"- Medical conditions: {conditions}\n"
        
        if context["allergies"]:
            allergies = ", ".join([allergy["allergen"] for allergy in context["allergies"]])
            prompt += f"- Known allergies: {allergies}\n"
        
        prompt += f"\n**Drug Interactions Found:** {context['interaction_count']}\n"
        
        if context["interactions"]:
            prompt += "\nDetailed interactions:\n"
            for interaction in context["interactions"]:
                prompt += f"- {interaction.get('drug1_name', '')} + {interaction.get('drug2_name', '')}: {interaction.get('description', 'No description')}\n"
        
        prompt += """
Please provide:

1. **Overall Safety Assessment**: A brief summary of the medication combination's safety
2. **Key Interactions**: Explain the most important drug interactions in simple terms
3. **Potential Side Effects**: What symptoms to watch for
4. **Recommendations**: 
   - What to discuss with the doctor
   - Any timing considerations for taking medications
   - Warning signs that require immediate medical attention
5. **Allergy Considerations**: If any medications might conflict with known allergies

Please write in a caring, informative tone that a patient can easily understand. Use bullet points and clear headings. Avoid medical jargon where possible, but when technical terms are necessary, explain them briefly.

Remember to emphasize that this is informational only and not a substitute for professional medical advice.
"""
        
        return prompt
    
    def _assess_overall_risk(self, interactions: List[Dict[str, Any]]) -> str:
        """Assess overall risk level based on interactions"""
        if not interactions:
            return "minor"
        
        severity_scores = {
            "minor": 1,
            "moderate": 2, 
            "major": 3
        }
        
        max_severity = 0
        for interaction in interactions:
            severity = interaction.get("severity", "minor")
            score = severity_scores.get(severity, 1)
            max_severity = max(max_severity, score)
        
        if max_severity >= 3:
            return "major"
        elif max_severity >= 2:
            return "moderate"
        else:
            return "minor"
    
    async def generate_medication_summary(self, medications: List[Dict[str, Any]]) -> str:
        """Generate a summary of medications for QR code sharing"""
        
        med_list = []
        for med in medications:
            name = med.get("medication_name", med.get("name", "Unknown"))
            dosage = med.get("dosage", "")
            frequency = med.get("frequency", "")
            med_list.append(f"{name} {dosage} {frequency}".strip())
        
        prompt = f"""
Create a concise medical summary for emergency use. This will be shared via QR code with healthcare providers.

Medications:
{chr(10).join([f"- {med}" for med in med_list])}

Please provide:
1. A brief, clear list of current medications
2. Any critical warnings or interactions
3. Emergency contact information format

Keep it under 200 words and suitable for emergency situations.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback to simple list if AI fails
            return "\n".join([f"• {med}" for med in med_list])
    
    async def analyze_prescription_text(self, ocr_text: str) -> Dict[str, Any]:
        """Analyze OCR text from prescription to extract structured data"""
        
        prompt = f"""
You are a medical AI assistant helping extract structured data from prescription texts.

The input below is a noisy OCR output from a scanned or photographed prescription. It may contain misspellings, missing punctuation, or formatting issues. Your task is to **recover the intended medical meaning** as accurately as possible.

---

**OCR Input**:
\"\"\"{ocr_text}\"\"\"

---

Please extract and return a JSON with this structure:

{{
  "medications": [
    {{
      "name": "Medication name",
      "dosage": "Dosage strength (e.g. 10mg, 500mg)",
      "frequency": "How often to take it (e.g. once a day, twice daily)",
      "duration": "For how long (e.g. 7 days, as needed)",
      "instructions": "Any additional instructions (e.g. take before meal)"
    }}
  ],
  "prescription_date": "Date if present (e.g. 25/07/2025)",
  "doctor_info": {{
    "name": "Doctor's name if found",
    "clinic": "Clinic or hospital name if found"
  }},
  "confidence": "high / medium / low (based on clarity of input)"
}}

**Instructions**:
- If data is not clearly present, set it to `null`
- Be cautious with assumptions. Don't hallucinate.
- Try to recover miswritten drug names if possible (e.g. “Paracelamol” → “Paracetamol”)
- Trim any unnecessary explanation. Only return the JSON.
"""

        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to parse as JSON
            try:
                # Handle markdown code blocks (```json...```)
                if response_text.startswith("```"):
                    # Extract JSON from markdown code block
                    lines = response_text.split('\n')
                    json_lines = []
                    in_json_block = False
                    
                    for line in lines:
                        if line.strip().startswith("```"):
                            if not in_json_block:
                                in_json_block = True
                            else:
                                break
                        elif in_json_block:
                            json_lines.append(line)
                    
                    if json_lines:
                        json_text = '\n'.join(json_lines)
                        return json.loads(json_text)
                
                # Try direct JSON parsing
                return json.loads(response_text)
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return basic structure
                return {
                    "medications": [],
                    "doctor_info": {"name": None, "clinic": None},
                    "prescription_date": None,
                    "confidence": "low",
                    "raw_response": response_text
                }
        except Exception as e:
            raise Exception(f"Prescription analysis failed: {str(e)}")
    
    async def generate_custom_explanation(
        self,
        medications: List[str],
        custom_prompt: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI explanation with custom prompt"""
        try:
            # Build context
            context = ""
            if user_context:
                context = self._build_user_context(user_context)
            
            # Build full prompt
            full_prompt = f"""
            {context}
            
            Medications: {', '.join(medications)}
            
            {custom_prompt}
            
            Please provide a clear, accurate, and helpful response.
            """
            
            # Generate content
            response = self.model.generate_content(full_prompt)
            
            return {
                "explanation": response.text,
                "prompt_used": full_prompt,
                "tokens_used": self._estimate_tokens(response.text)
            }
        except Exception as e:
            raise Exception(f"Error generating custom AI explanation: {str(e)}")
    
    async def generate_profile_summary(
        self,
        user_profile: Dict[str, Any],
        medical_history: List[Dict[str, Any]],
        allergies: List[Dict[str, Any]],
        medication_schedules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive AI summary of user's medical profile"""
        try:
            prompt = self._build_profile_summary_prompt(
                user_profile, medical_history, allergies, medication_schedules
            )
            
            response = self.model.generate_content(prompt)
            
            # Parse response into structured format
            summary_text = response.text
            
            return {
                "summary": summary_text,
                "risk_assessment": self._extract_risk_assessment(summary_text),
                "recommendations": self._extract_recommendations(summary_text),
                "tokens_used": self._estimate_tokens(summary_text)
            }
        except Exception as e:
            raise Exception(f"Error generating profile summary: {str(e)}")

    def _build_user_context(self, user_context: Dict[str, Any]) -> str:
        """Build user context text for prompts"""
        context_parts = []
        
        if user_context.get("medical_history"):
            conditions = [h.get("condition_name") or h.get("conditions", {}).get("name") 
                         for h in user_context["medical_history"] if h.get("is_active", True)]
            if conditions:
                context_parts.append(f"Medical History: {', '.join(filter(None, conditions))}")
        
        if user_context.get("allergies"):
            allergens = [a.get("allergen") for a in user_context["allergies"]]
            if allergens:
                context_parts.append(f"Known Allergies: {', '.join(allergens)}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _build_profile_summary_prompt(
        self,
        user_profile: Dict[str, Any],
        medical_history: List[Dict[str, Any]],
        allergies: List[Dict[str, Any]],
        medication_schedules: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for comprehensive profile summary"""
        
        # Extract information
        age = self._calculate_age(user_profile.get("date_of_birth"))
        conditions = [h.get("condition_name") or h.get("conditions", {}).get("name") 
                     for h in medical_history if h.get("is_active", True)]
        allergens = [a.get("allergen") for a in allergies]
        medications = [s.get("medication_name") for s in medication_schedules if s.get("is_active", True)]
        
        prompt = f"""
        Generate a comprehensive medical profile summary for healthcare providers.
        
        Patient Information:
        - Age: {age if age else "Not specified"}
        - Medical Conditions: {', '.join(filter(None, conditions)) if conditions else "None reported"}
        - Known Allergies: {', '.join(allergens) if allergens else "None reported"}
        - Current Medications: {', '.join(medications) if medications else "None reported"}
        
        Please provide:
        1. PATIENT OVERVIEW: Brief summary of the patient's medical status
        2. RISK ASSESSMENT: Key risk factors and areas of concern
        3. MEDICATION INTERACTIONS: Analysis of current medication regimen
        4. RECOMMENDATIONS: Specific recommendations for monitoring and care
        
        Format as a professional medical summary suitable for healthcare providers.
        """
        
        return prompt
    
    def _calculate_age(self, date_of_birth: Optional[str]) -> Optional[int]:
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        
        try:
            from datetime import datetime
            birth_date = datetime.fromisoformat(date_of_birth)
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return None
    
    def _extract_risk_assessment(self, summary_text: str) -> Dict[str, Any]:
        """Extract risk assessment from summary text"""
        # Simple extraction logic - in practice, you might want more sophisticated parsing
        risk_keywords = ["high risk", "moderate risk", "low risk", "caution", "warning", "monitor"]
        
        risks_found = []
        for keyword in risk_keywords:
            if keyword.lower() in summary_text.lower():
                risks_found.append(keyword)
        
        return {
            "identified_risks": risks_found,
            "overall_risk_level": "moderate" if risks_found else "low"
        }
    
    def _extract_recommendations(self, summary_text: str) -> List[str]:
        """Extract recommendations from summary text"""
        # Simple extraction logic - look for recommendation sections
        lines = summary_text.split('\n')
        recommendations = []
        
        in_recommendations_section = False
        for line in lines:
            if "recommendation" in line.lower() or "suggest" in line.lower():
                in_recommendations_section = True
            
            if in_recommendations_section and line.strip().startswith('-'):
                recommendations.append(line.strip()[1:].strip())
        
        return recommendations
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
