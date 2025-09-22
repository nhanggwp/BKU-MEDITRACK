from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.supabase_service import SupabaseService
from services.auth_service import AuthService

router = APIRouter()
supabase_service = SupabaseService()
auth_service = AuthService()

class MedicalConditionRequest(BaseModel):
    condition_id: Optional[str] = None
    condition_name: Optional[str] = None  # For custom conditions
    diagnosed_date: Optional[str] = None
    notes: Optional[str] = None

class AllergyRequest(BaseModel):
    allergen: str
    reaction: Optional[str] = None
    severity: Optional[str] = "moderate"
    notes: Optional[str] = None

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

@router.get("/")
async def get_medical_history(request: Request):
    """Get user's complete medical history"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get medical history
        medical_history = await supabase_service.get_medical_history(user_id)
        
        # Get allergies
        allergies = await supabase_service.get_allergies(user_id)
        
        return {
            "medical_history": medical_history,
            "allergies": allergies,
            "summary": {
                "conditions_count": len(medical_history),
                "allergies_count": len(allergies),
                "last_updated": max(
                    [h.get("updated_at", h.get("created_at", "")) for h in medical_history + allergies]
                ) if medical_history + allergies else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conditions")
async def get_available_conditions(request: Request):
    """Get list of available medical conditions"""
    try:
        await get_current_user_id(request)  # Verify authentication
        
        # Get all conditions from the conditions table
        response = await supabase_service.client.table('conditions').select('*').execute()
        
        return {
            "conditions": response.data,
            "count": len(response.data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conditions")
async def add_medical_condition(request: Request, condition_data: MedicalConditionRequest):
    """Add medical condition to user's history"""
    try:
        user_id = await get_current_user_id(request)
        
        # If condition_name is provided instead of condition_id, we need to find or create the condition
        if condition_data.condition_name and not condition_data.condition_id:
            # First, search for existing condition by name
            try:
                existing_conditions = supabase_service.client.table('conditions').select('id').eq('name', condition_data.condition_name).execute()
                
                if existing_conditions.data:
                    # Use existing condition
                    condition_id = existing_conditions.data[0]['id']
                else:
                    # Create new condition
                    new_condition = {
                        "name": condition_data.condition_name,
                        "description": f"User-added condition: {condition_data.condition_name}",
                        "severity": "moderate"
                    }
                    condition_result = supabase_service.client.table('conditions').insert(new_condition).execute()
                    condition_id = condition_result.data[0]['id']
                
                # Create medical history entry with condition_id
                history_data = {
                    "condition_id": condition_id,
                    "diagnosed_date": condition_data.diagnosed_date,
                    "notes": condition_data.notes
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing condition: {str(e)}")
        else:
            history_data = {
                "condition_id": condition_data.condition_id,
                "diagnosed_date": condition_data.diagnosed_date,
                "notes": condition_data.notes
            }
        
        # Check if this condition already exists for the user
        try:
            existing_history = supabase_service.client.table('medical_histories').select('id').eq('user_id', user_id).eq('condition_id', history_data["condition_id"]).execute()
            
            if existing_history.data:
                # If it exists but is inactive, reactivate it instead of creating a duplicate
                existing_id = existing_history.data[0]['id']
                updated_data = {
                    **history_data,
                    "is_active": True,
                    "updated_at": "NOW()"
                }
                
                result_response = supabase_service.client.table('medical_histories').update(updated_data).eq('id', existing_id).execute()
                result = result_response.data[0] if result_response.data else None
                
                if not result:
                    raise HTTPException(status_code=400, detail="This condition already exists in your medical history")
                
                return {
                    "message": "Medical condition updated successfully (was previously inactive)",
                    "condition": result
                }
            else:
                # Create new entry if it doesn't exist
                result = await supabase_service.add_medical_condition(user_id, history_data)
                
                return {
                    "message": "Medical condition added successfully",
                    "condition": result
                }
        except Exception as e:
            if "duplicate key value violates unique constraint" in str(e):
                raise HTTPException(status_code=400, detail="This medical condition is already in your history")
            raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conditions")
async def list_available_conditions():
    """List available medical conditions"""
    try:
        # Get all conditions from the database
        response = await supabase_service.client.table('conditions').select('*').order('name').execute()
        
        return {
            "conditions": response.data,
            "total": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/allergies")
async def add_allergy(request: Request, allergy_data: AllergyRequest):
    """Add allergy to user's record"""
    try:
        user_id = await get_current_user_id(request)
        
        result = await supabase_service.add_allergy(user_id, allergy_data.dict())
        
        return {
            "message": "Allergy added successfully",
            "allergy": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/allergies")
async def get_allergies(request: Request):
    """Get user's allergies"""
    try:
        user_id = await get_current_user_id(request)
        allergies = await supabase_service.get_allergies(user_id)
        
        return {
            "allergies": allergies,
            "count": len(allergies)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conditions/{condition_history_id}")
async def remove_medical_condition(request: Request, condition_history_id: str):
    """Remove medical condition from history (soft delete)"""
    try:
        user_id = await get_current_user_id(request)
        
        # Soft delete by setting is_active to false
        response = await supabase_service.client.table('medical_histories').update({
            "is_active": False
        }).eq('id', condition_history_id).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Medical condition not found")
        
        return {"message": "Medical condition removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/allergies/{allergy_id}")
async def remove_allergy(request: Request, allergy_id: str):
    """Remove allergy from user's record"""
    try:
        user_id = await get_current_user_id(request)
        
        response = await supabase_service.client.table('allergies').delete().eq(
            'id', allergy_id
        ).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Allergy not found")
        
        return {"message": "Allergy removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/conditions/{condition_history_id}")
async def update_medical_condition(
    request: Request, 
    condition_history_id: str, 
    condition_data: MedicalConditionRequest
):
    """Update medical condition in history"""
    try:
        user_id = await get_current_user_id(request)
        
        # Only include non-None values
        update_data = {k: v for k, v in condition_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        response = await supabase_service.client.table('medical_histories').update(
            update_data
        ).eq('id', condition_history_id).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Medical condition not found")
        
        return {
            "message": "Medical condition updated successfully",
            "condition": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/allergies/{allergy_id}")
async def update_allergy(request: Request, allergy_id: str, allergy_data: AllergyRequest):
    """Update allergy information"""
    try:
        user_id = await get_current_user_id(request)
        
        # Only include non-None values
        update_data = {k: v for k, v in allergy_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        response = await supabase_service.client.table('allergies').update(
            update_data
        ).eq('id', allergy_id).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Allergy not found")
        
        return {
            "message": "Allergy updated successfully",
            "allergy": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
