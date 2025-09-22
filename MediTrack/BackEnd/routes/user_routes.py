from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from services.supabase_service import SupabaseService
from services.auth_service import AuthService

router = APIRouter()
supabase_service = SupabaseService()
auth_service = AuthService()

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None

async def get_current_user_id(request: Request) -> str:
    """Extract user ID from token"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No valid token provided")
    
    token = auth_header.split(" ")[1]
    try:
        user = await auth_service.verify_token(token)
        
        # Set the authentication token for the supabase service
        supabase_service.set_auth_token(token)
        
        return user["id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/profile")
async def get_profile(request: Request):
    """Get current user's profile"""
    try:
        user_id = await get_current_user_id(request)
        profile = await supabase_service.get_user_by_id(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {"profile": profile}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_profile(request: Request, profile_data: UpdateProfileRequest):
    """Update current user's profile"""
    try:
        user_id = await get_current_user_id(request)
        
        # Only include non-None values
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        updated_profile = await supabase_service.update_user_profile(user_id, update_data)
        
        if not updated_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "message": "Profile updated successfully",
            "profile": updated_profile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_dashboard(request: Request):
    """Get user dashboard data"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get profile
        profile = await supabase_service.get_user_by_id(user_id)
        
        # Get medical history
        medical_history = await supabase_service.get_medical_history(user_id)
        
        # Get allergies
        allergies = await supabase_service.get_allergies(user_id)
        
        # Get medication schedules
        schedules = await supabase_service.get_medication_schedules(user_id)
        
        # Get family group info
        family_group = await supabase_service.get_family_group(user_id)
        
        return {
            "profile": profile,
            "medical_history": medical_history,
            "allergies": allergies,
            "medication_schedules": schedules,
            "family_group": family_group,
            "dashboard_stats": {
                "conditions_count": len(medical_history),
                "allergies_count": len(allergies),
                "active_medications": len(schedules),
                "has_family_group": family_group is not None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/account")
async def delete_account(request: Request):
    """Delete user account (soft delete)"""
    try:
        user_id = await get_current_user_id(request)
        
        # In a real implementation, you might want to:
        # 1. Soft delete by marking account as inactive
        # 2. Anonymize personal data
        # 3. Keep medical data for legal/audit purposes
        
        # For now, just mark as inactive
        await supabase_service.update_user_profile(user_id, {"is_active": False})
        
        return {"message": "Account deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
