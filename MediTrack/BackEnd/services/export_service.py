from typing import Dict, Any, List
import json
import csv
import tempfile
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class ExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    async def generate_pdf_report(self, export_data: Dict[str, Any], user_id: str) -> str:
        """Generate PDF medical report"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            # Create PDF document
            doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("MediTrack Medical Report", title_style))
            story.append(Spacer(1, 20))
            
            # User Profile Section
            if export_data.get("user_profile"):
                story.append(Paragraph("Patient Information", self.styles['Heading2']))
                profile = export_data["user_profile"]
                
                profile_data = [
                    ["Name:", profile.get("full_name", "Not specified")],
                    ["Date of Birth:", profile.get("date_of_birth", "Not specified")],
                    ["Email:", profile.get("email", "Not specified")],
                    ["Phone:", profile.get("phone", "Not specified")],
                    ["Emergency Contact:", profile.get("emergency_contact", "Not specified")]
                ]
                
                profile_table = Table(profile_data, colWidths=[2*inch, 4*inch])
                profile_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ]))
                story.append(profile_table)
                story.append(Spacer(1, 20))
            
            # Medical History Section
            if export_data.get("medical_history"):
                story.append(Paragraph("Medical History", self.styles['Heading2']))
                
                if export_data["medical_history"]:
                    for condition in export_data["medical_history"]:
                        condition_name = condition.get("condition_name") or condition.get("conditions", {}).get("name", "Unknown")
                        diagnosed_date = condition.get("diagnosed_date", "Unknown")
                        notes = condition.get("notes", "No notes")
                        
                        story.append(Paragraph(f"<b>{condition_name}</b>", self.styles['Normal']))
                        story.append(Paragraph(f"Diagnosed: {diagnosed_date}", self.styles['Normal']))
                        if notes != "No notes":
                            story.append(Paragraph(f"Notes: {notes}", self.styles['Normal']))
                        story.append(Spacer(1, 10))
                else:
                    story.append(Paragraph("No medical history recorded.", self.styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Allergies Section
            if export_data.get("allergies"):
                story.append(Paragraph("Allergies", self.styles['Heading2']))
                
                if export_data["allergies"]:
                    allergy_data = [["Allergen", "Reaction", "Severity"]]
                    for allergy in export_data["allergies"]:
                        allergy_data.append([
                            allergy.get("allergen", "Unknown"),
                            allergy.get("reaction", "Not specified"),
                            allergy.get("severity", "Not specified")
                        ])
                    
                    allergy_table = Table(allergy_data, colWidths=[2*inch, 2*inch, 1.5*inch])
                    allergy_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(allergy_table)
                else:
                    story.append(Paragraph("No allergies recorded.", self.styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Current Medications Section
            if export_data.get("medication_schedules"):
                story.append(Paragraph("Current Medications", self.styles['Heading2']))
                
                if export_data["medication_schedules"]:
                    med_data = [["Medication", "Dosage", "Frequency", "Start Date"]]
                    for med in export_data["medication_schedules"]:
                        if med.get("is_active", True):
                            med_data.append([
                                med.get("medication_name", "Unknown"),
                                med.get("dosage", "Not specified"),
                                f"{med.get('frequency_per_day', 'Unknown')} times/day",
                                med.get("start_date", "Not specified")
                            ])
                    
                    med_table = Table(med_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                    med_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(med_table)
                else:
                    story.append(Paragraph("No current medications.", self.styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Export metadata
            if export_data.get("export_metadata"):
                story.append(Paragraph("Report Information", self.styles['Heading2']))
                story.append(Paragraph(f"Generated: {export_data['export_metadata'].get('exported_at', 'Unknown')}", self.styles['Normal']))
                story.append(Paragraph(f"Generated by: {export_data['export_metadata'].get('generated_by', 'MediTrack')}", self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            return temp_file.name
            
        except Exception as e:
            raise Exception(f"Error generating PDF report: {str(e)}")
    
    async def generate_csv_export(self, export_data: Dict[str, Any], user_id: str) -> str:
        """Generate CSV export file"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')
            
            writer = csv.writer(temp_file)
            
            # Write header
            writer.writerow(["MediTrack Data Export"])
            writer.writerow(["Generated:", export_data.get("export_metadata", {}).get("exported_at", "Unknown")])
            writer.writerow([])  # Empty row
            
            # User Profile
            if export_data.get("user_profile"):
                writer.writerow(["PATIENT INFORMATION"])
                profile = export_data["user_profile"]
                for key, value in profile.items():
                    writer.writerow([key.replace("_", " ").title(), value or "Not specified"])
                writer.writerow([])  # Empty row
            
            # Medical History
            if export_data.get("medical_history"):
                writer.writerow(["MEDICAL HISTORY"])
                writer.writerow(["Condition", "Diagnosed Date", "Notes", "Active"])
                for condition in export_data["medical_history"]:
                    condition_name = condition.get("condition_name") or condition.get("conditions", {}).get("name", "Unknown")
                    writer.writerow([
                        condition_name,
                        condition.get("diagnosed_date", "Unknown"),
                        condition.get("notes", ""),
                        "Yes" if condition.get("is_active", True) else "No"
                    ])
                writer.writerow([])  # Empty row
            
            # Allergies
            if export_data.get("allergies"):
                writer.writerow(["ALLERGIES"])
                writer.writerow(["Allergen", "Reaction", "Severity", "Notes"])
                for allergy in export_data["allergies"]:
                    writer.writerow([
                        allergy.get("allergen", "Unknown"),
                        allergy.get("reaction", ""),
                        allergy.get("severity", ""),
                        allergy.get("notes", "")
                    ])
                writer.writerow([])  # Empty row
            
            # Current Medications
            if export_data.get("medication_schedules"):
                writer.writerow(["CURRENT MEDICATIONS"])
                writer.writerow(["Medication", "Dosage", "Frequency per Day", "Times of Day", "Start Date", "End Date", "Active"])
                for med in export_data["medication_schedules"]:
                    writer.writerow([
                        med.get("medication_name", "Unknown"),
                        med.get("dosage", ""),
                        med.get("frequency_per_day", ""),
                        "; ".join(med.get("times_of_day", [])),
                        med.get("start_date", ""),
                        med.get("end_date", ""),
                        "Yes" if med.get("is_active", True) else "No"
                    ])
            
            temp_file.close()
            return temp_file.name
            
        except Exception as e:
            raise Exception(f"Error generating CSV export: {str(e)}")
    
    async def generate_doctor_summary(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate doctor-friendly summary"""
        try:
            user_profile = medical_data.get("user_profile", {})
            medical_history = medical_data.get("medical_history", [])
            allergies = medical_data.get("allergies", [])
            current_medications = medical_data.get("current_medications", [])
            recent_interactions = medical_data.get("recent_drug_interactions", [])
            adherence_data = medical_data.get("adherence_data", {})
            
            # Calculate age
            age = self._calculate_age(user_profile.get("date_of_birth"))
            
            # Active conditions
            active_conditions = [
                h.get("condition_name") or h.get("conditions", {}).get("name")
                for h in medical_history 
                if h.get("is_active", True)
            ]
            
            # High-severity allergies
            critical_allergies = [
                a.get("allergen") 
                for a in allergies 
                if a.get("severity") in ["high", "severe"]
            ]
            
            # Active medications
            active_meds = [
                {
                    "name": med.get("medication_name"),
                    "dosage": med.get("dosage"),
                    "frequency": f"{med.get('frequency_per_day', 'Unknown')} times/day"
                }
                for med in current_medications 
                if med.get("is_active", True)
            ]
            
            # Risk assessment
            risk_factors = []
            if len(active_meds) > 5:
                risk_factors.append("Polypharmacy (>5 medications)")
            if critical_allergies:
                risk_factors.append("Critical allergies present")
            if recent_interactions:
                risk_factors.append("Recent drug interactions detected")
            
            summary = {
                "patient_overview": {
                    "age": age,
                    "active_conditions_count": len(active_conditions),
                    "active_medications_count": len(active_meds),
                    "critical_allergies_count": len(critical_allergies)
                },
                "active_conditions": active_conditions,
                "critical_allergies": critical_allergies,
                "current_medications": active_meds,
                "risk_factors": risk_factors,
                "adherence_summary": adherence_data,
                "recent_drug_interactions": len(recent_interactions),
                "recommendations": self._generate_recommendations(medical_data)
            }
            
            return summary
            
        except Exception as e:
            raise Exception(f"Error generating doctor summary: {str(e)}")
    
    def _calculate_age(self, date_of_birth: str) -> int:
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        
        try:
            birth_date = datetime.fromisoformat(date_of_birth)
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return None
    
    def _generate_recommendations(self, medical_data: Dict[str, Any]) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        medications = medical_data.get("current_medications", [])
        allergies = medical_data.get("allergies", [])
        
        # Medication-related recommendations
        active_meds = [m for m in medications if m.get("is_active", True)]
        if len(active_meds) > 5:
            recommendations.append("Consider medication review for polypharmacy management")
        
        # Allergy-related recommendations
        critical_allergies = [a for a in allergies if a.get("severity") in ["high", "severe"]]
        if critical_allergies:
            recommendations.append("Ensure allergy information is prominently displayed in medical records")
        
        # Adherence-related recommendations
        adherence_data = medical_data.get("adherence_data", {})
        if adherence_data.get("adherence_rate", 100) < 80:
            recommendations.append("Consider adherence counseling and support interventions")
        
        return recommendations
