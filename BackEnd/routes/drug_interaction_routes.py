
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.supabase_service import SupabaseService
from services.drug_interaction_service import DrugInteractionService
from services.auth_service import AuthService
from routes.medical_history_routes import get_medical_history

router = APIRouter()
supabase_service = SupabaseService()
drug_service = DrugInteractionService()
auth_service = AuthService()

class MedicationListRequest(BaseModel):
    medications: List[str]
    include_user_history: bool = True

class InteractionCheckResponse(BaseModel):
    medications: List[str]
    interactions: List[Dict[str, Any]]
    risk_summary: Dict[str, Any]
    checked_at: str

async def get_current_user_id(request: Request) -> str:
    """Extract user ID from token"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    token = auth_header.split(" ")[1]
    try:
        user = await auth_service.verify_token(token)
        
        # Set the authentication token for the supabase service
        supabase_service.set_auth_token(token)
        
        return user["id"]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


@router.post("/check")
async def check_drug_interactions(request: Request, medication_data: MedicationListRequest):
    """Check medication list for drug interactions"""
    try:
        # Get user ID from authentication token
        user_id = await get_current_user_id(request)
        medical_history = await get_medical_history(request)
        print(f"User ID: {user_id}, Medical History: {medical_history}")


        result = await drug_service.check_drug_interactions(
            medication_data.medications,
            user_id=user_id,
            medical_history=medical_history
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_interaction_history(request: Request, limit: int = 10, offset: int = 0):
    """Get user's drug interaction check history"""
    try:
        user_id = await get_current_user_id(request)
        
        history = await supabase_service.get_interaction_history(user_id, limit, offset)
        
        return {
            "history": history,
            "count": len(history)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medications/search")
async def search_medications(query: str, limit: int = 10):
    """Search medications by name"""
    try:
        medications = await supabase_service.search_medications(query, limit)
        
        return {
            "medications": medications,
            "count": len(medications)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interactions/{drug1}/{drug2}")
async def get_specific_interaction(drug1: str, drug2: str):
    """Get specific interaction between two drugs"""
    try:
        interactions = await supabase_service.get_drug_interactions(drug1, drug2)
        
        return {
            "drug1": drug1,
            "drug2": drug2,
            "interactions": interactions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-check")
async def batch_check_interactions(request: Request, medication_lists: List[MedicationListRequest]):
    """Check multiple medication lists for interactions (for family management)"""
    try:
        user_id = await get_current_user_id(request)
        
        results = []
        for med_list in medication_lists:
            try:
                # Check for drug interactions
                interaction_results = await drug_service.check_interactions(
                    med_list.medications,
                    {} if not med_list.include_user_history else None
                )
                
                results.append({
                    "medications": med_list.medications,
                    "interactions": interaction_results["interactions"],
                    "risk_summary": interaction_results["risk_summary"],
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "medications": med_list.medications,
                    "error": str(e),
                    "status": "error"
                })
        
        return {
            "results": results,
            "total_checks": len(medication_lists)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))