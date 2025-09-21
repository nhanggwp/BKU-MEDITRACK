from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from services.supabase_service import SupabaseService
from services.qr_service import QRService
from services.auth_service import AuthService
from datetime import datetime, timedelta

router = APIRouter()
supabase_service = SupabaseService()
auth_service = AuthService()

class QRGenerationRequest(BaseModel):
    include_medical_history: bool = True
    include_medications: bool = True
    include_allergies: bool = True
    expires_hours: int = 24
    max_uses: int = 1

class QRAccessRequest(BaseModel):
    token: str
    decryption_key: Optional[str] = None

async def get_current_user_id(request: Request) -> str:
    """Extract user ID from token"""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = auth_header.replace("Bearer ", "")
    user = await auth_service.verify_token(token)
    return user["id"]

@router.post("/generate")
async def generate_qr_code(request: Request, qr_request: QRGenerationRequest):
    """Generate encrypted QR code with user medical data"""
    try:
        user_id = await get_current_user_id(request)
        
        # Set auth token for the supabase service
        auth_header = request.headers.get("authorization")
        if auth_header:
            token = auth_header.replace("Bearer ", "")
            supabase_service.set_auth_token(token)
        
        # Create QR service with authenticated supabase service
        qr_service = QRService(supabase_service)
        
        # Generate encrypted QR token using the service method
        qr_result = await qr_service.generate_encrypted_qr(
            user_id=user_id,
            options={
                "include_medical_history": qr_request.include_medical_history,
                "include_allergies": qr_request.include_allergies,
                "include_current_medications": qr_request.include_medications,
                "expires_hours": qr_request.expires_hours,
                "max_uses": qr_request.max_uses
            }
        )
        
        return {
            "qr_code_base64": qr_result["qr_code_base64"],
            "token": qr_result["token"],
            "expires_at": qr_result["expires_at"],
            "max_uses": qr_result["max_uses"],
            "access_url": qr_result["access_url"],
            "medical_summary": qr_result["medical_summary"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/access/{token}")
async def access_qr_data(token: str, key: Optional[str] = None):
    """Access QR code data with decryption"""
    try:
        # Create QR service instance
        qr_service = QRService()
        
        # Use the QR service's access method
        result = await qr_service.access_qr_data(token)
        
        return {
            "data": result["medical_data"],
            "accessed_at": datetime.utcnow().isoformat(),
            "remaining_uses": result["max_uses"] - result["access_count"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens")
async def get_user_qr_tokens(request: Request, active_only: bool = True):
    """Get user's QR tokens"""
    try:
        user_id = await get_current_user_id(request)
        
        tokens = await supabase_service.get_user_qr_tokens(user_id, active_only)
        
        return {
            "tokens": tokens,
            "count": len(tokens)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tokens/{token_id}")
async def revoke_qr_token(request: Request, token_id: str):
    """Revoke/delete QR token"""
    try:
        user_id = await get_current_user_id(request)
        
        # Verify token belongs to user
        qr_token = await supabase_service.get_qr_token_by_id(token_id)
        if not qr_token or qr_token["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="QR token not found")
        
        await supabase_service.delete_qr_token(token_id)
        
        return {
            "message": "QR token revoked successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{token_id}/access-logs")
async def get_qr_access_logs(request: Request, token_id: str):
    """Get access logs for QR token"""
    try:
        user_id = await get_current_user_id(request)
        
        # Verify token belongs to user
        qr_token = await supabase_service.get_qr_token_by_id(token_id)
        if not qr_token or qr_token["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="QR token not found")
        
        access_logs = await supabase_service.get_qr_access_logs(token_id)
        
        return {
            "access_logs": access_logs,
            "count": len(access_logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_qr_token(validation_request: QRAccessRequest):
    """Validate QR token without accessing data"""
    try:
        qr_token = await supabase_service.get_qr_token(validation_request.token)
        if not qr_token:
            return {"valid": False, "reason": "Token not found"}
        
        # Check expiration
        if qr_token["expires_at"] and datetime.fromisoformat(qr_token["expires_at"]) < datetime.utcnow():
            return {"valid": False, "reason": "Token expired"}
        
        # Check usage limits
        if qr_token["current_uses"] >= qr_token["max_uses"]:
            return {"valid": False, "reason": "Usage limit exceeded"}
        
        return {
            "valid": True,
            "expires_at": qr_token["expires_at"],
            "remaining_uses": qr_token["max_uses"] - qr_token["current_uses"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
