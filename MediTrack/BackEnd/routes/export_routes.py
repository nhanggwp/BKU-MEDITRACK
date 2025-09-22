from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.supabase_service import SupabaseService
from services.auth_service import AuthService
from services.export_service import ExportService
from datetime import datetime
import tempfile
import os

router = APIRouter()
supabase_service = SupabaseService()
auth_service = AuthService()
export_service = ExportService()

class ExportRequest(BaseModel):
    export_type: str  # 'json', 'pdf', 'csv'
    include_medical_history: bool = True
    include_medications: bool = True
    include_allergies: bool = True
    include_ai_explanations: bool = False
    include_ai_summary: bool = False
    include_adherence_data: bool = True
    date_range_days: Optional[int] = None  # Export data from last N days

async def get_current_user_id(request: Request) -> str:
    """Extract user ID from token"""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = auth_header.replace("Bearer ", "")
    user = await auth_service.verify_token(token)
    
    # Set the authentication token for the supabase service
    supabase_service.set_auth_token(token)
    
    return user["id"]

@router.post("/medical-data")
async def export_medical_data(request: Request, export_request: ExportRequest):
    """Export user's medical data in various formats"""
    try:
        user_id = await get_current_user_id(request)
        
        # Collect data based on request
        export_data = {}
        
        # User profile
        user_profile = await supabase_service.get_user_by_id(user_id)
        export_data["user_profile"] = {
            "full_name": user_profile.get("full_name"),
            "date_of_birth": user_profile.get("date_of_birth"),
            "email": user_profile.get("email"),
            "phone": user_profile.get("phone"),
            "emergency_contact": user_profile.get("emergency_contact")
        }
        
        if export_request.include_medical_history:
            medical_history = await supabase_service.get_medical_history(user_id)
            export_data["medical_history"] = medical_history
        
        if export_request.include_medications:
            medication_schedules = await supabase_service.get_medication_schedules(user_id)
            export_data["medication_schedules"] = medication_schedules
        
        if export_request.include_allergies:
            allergies = await supabase_service.get_allergies(user_id)
            export_data["allergies"] = allergies
        
        if export_request.include_ai_explanations:
            ai_explanations = await supabase_service.get_ai_explanation_history(user_id)
            export_data["ai_explanations"] = ai_explanations
        
        if export_request.include_adherence_data:
            adherence_data = await supabase_service.get_medication_adherence(
                user_id, 
                export_request.date_range_days or 30
            )
            export_data["adherence_data"] = adherence_data
        
        # Add export metadata
        export_data["export_metadata"] = {
            "exported_at": datetime.now().isoformat(),
            "export_type": export_request.export_type,
            "generated_by": "MediTrack API v1.0.0"
        }
        
        # Generate export based on type
        if export_request.export_type == "json":
            # Log export
            await supabase_service.log_export(user_id, {
                "export_type": "json",
                "exported_data": export_data,
                "export_reason": "User requested JSON export"
            })
            
            return JSONResponse(
                content=export_data,
                headers={
                    "Content-Disposition": f"attachment; filename=meditrack_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )
        
        elif export_request.export_type == "pdf":
            # Generate PDF
            pdf_file_path = await export_service.generate_pdf_report(export_data, user_id)
            
            # Log export
            await supabase_service.log_export(user_id, {
                "export_type": "pdf",
                "exported_data": {"summary": "PDF report generated"},
                "export_reason": "User requested PDF export"
            })
            
            return FileResponse(
                pdf_file_path,
                media_type="application/pdf",
                filename=f"meditrack_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        
        elif export_request.export_type == "csv":
            # Generate CSV
            csv_file_path = await export_service.generate_csv_export(export_data, user_id)
            
            # Log export
            await supabase_service.log_export(user_id, {
                "export_type": "csv",
                "exported_data": {"summary": "CSV files generated"},
                "export_reason": "User requested CSV export"
            })
            
            return FileResponse(
                csv_file_path,
                media_type="text/csv",
                filename=f"meditrack_data_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export type")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats")
async def get_available_export_formats():
    """Get list of available export formats"""
    return {
        "formats": [
            {
                "type": "json",
                "description": "JSON format with complete data structure",
                "mime_type": "application/json"
            },
            {
                "type": "pdf",
                "description": "PDF report formatted for healthcare providers",
                "mime_type": "application/pdf"
            },
            {
                "type": "csv",
                "description": "CSV format for spreadsheet applications",
                "mime_type": "text/csv"
            }
        ]
    }

@router.get("/history")
async def get_export_history(request: Request, limit: int = 10, offset: int = 0):
    """Get user's export history"""
    try:
        user_id = await get_current_user_id(request)
        
        export_history = await supabase_service.get_export_history(user_id, limit, offset)
        
        return {
            "exports": export_history,
            "count": len(export_history)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctor-summary")
async def generate_doctor_summary(request: Request):
    """Generate comprehensive summary for doctor consultation"""
    try:
        user_id = await get_current_user_id(request)
        
        # Collect comprehensive data
        user_profile = await supabase_service.get_user_by_id(user_id)
        medical_history = await supabase_service.get_medical_history(user_id)
        allergies = await supabase_service.get_allergies(user_id)
        medication_schedules = await supabase_service.get_medication_schedules(user_id)
        recent_interactions = await supabase_service.get_interaction_history(user_id, limit=5)
        adherence_data = await supabase_service.get_medication_adherence(user_id, 30)
        
        # Generate doctor-friendly summary
        doctor_summary = await export_service.generate_doctor_summary({
            "user_profile": user_profile,
            "medical_history": medical_history,
            "allergies": allergies,
            "current_medications": medication_schedules,
            "recent_drug_interactions": recent_interactions,
            "adherence_data": adherence_data
        })
        
        # Log export
        await supabase_service.log_export(user_id, {
            "export_type": "doctor_summary",
            "exported_data": {"summary": "Doctor summary generated"},
            "export_reason": "Doctor consultation preparation"
        })
        
        return {
            "summary": doctor_summary,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-card")
async def generate_emergency_card(request: Request):
    """Generate emergency medical information card"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get essential emergency information
        user_profile = await supabase_service.get_user_by_id(user_id)
        medical_history = await supabase_service.get_medical_history(user_id)
        allergies = await supabase_service.get_allergies(user_id)
        current_medications = await supabase_service.get_medication_schedules(user_id, active_only=True)
        
        # Generate emergency card data
        emergency_card = {
            "personal_info": {
                "name": user_profile.get("full_name"),
                "date_of_birth": user_profile.get("date_of_birth"),
                "emergency_contact": user_profile.get("emergency_contact")
            },
            "critical_allergies": [a for a in allergies if a.get("severity") in ["high", "severe"]],
            "current_medications": [
                {
                    "name": med["medication_name"],
                    "dosage": med["dosage"]
                } for med in current_medications
            ],
            "medical_conditions": [
                {
                    "condition": hist.get("condition_name") or hist.get("conditions", {}).get("name"),
                    "severity": hist.get("conditions", {}).get("severity")
                } for hist in medical_history if hist.get("is_active", True)
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "emergency_card": emergency_card
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
