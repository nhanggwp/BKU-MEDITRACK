from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from services.auth_service import AuthService
from services.supabase_service import SupabaseService

router = APIRouter()
auth_service = AuthService()
supabase_service = SupabaseService()

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    new_password: str
    refresh_token: str

@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """Sign up new user"""
    try:
        # Create user with Supabase Auth
        auth_result = await auth_service.sign_up(
            email=request.email,
            password=request.password,
            user_data={
                "full_name": request.full_name,
                "phone": request.phone,
                "date_of_birth": request.date_of_birth,
                "emergency_contact": request.emergency_contact
            }
        )
        
        # Create user profile in our database
        if auth_result.get("user"):
            user_profile_data = {
                "id": auth_result["user"]["id"],
                "email": request.email,
                "full_name": request.full_name,
                "phone": request.phone,
                "date_of_birth": request.date_of_birth,
                "emergency_contact": request.emergency_contact,
                "role": "patient"
            }
            
            profile = await supabase_service.create_user_profile(user_profile_data)
        
        return {
            "message": "User created successfully",
            "user": auth_result.get("user"),
            "session": auth_result.get("session"),
            "requires_email_confirmation": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin")
async def sign_in(request: SignInRequest):
    """Sign in user"""
    try:
        result = await auth_service.sign_in(request.email, request.password)
        
        # Get additional user profile data
        user_profile = await supabase_service.get_user_by_id(result["user"]["id"])
        
        # If user profile doesn't exist, create it
        if not user_profile:
            user_profile_data = {
                "id": result["user"]["id"],
                "email": request.email,
                "full_name": result["user"].get("user_metadata", {}).get("full_name", ""),
                "phone": result["user"].get("user_metadata", {}).get("phone", ""),
                "date_of_birth": result["user"].get("user_metadata", {}).get("date_of_birth"),
                "emergency_contact": result["user"].get("user_metadata", {}).get("emergency_contact"),
                "role": "patient"
            }
            user_profile = await supabase_service.create_user_profile(user_profile_data)
        
        return {
            "message": "Sign in successful",
            "user": result["user"],
            "profile": user_profile,
            "session": result["session"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        return {
            "message": "Token refreshed successfully",
            "session": result
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/signout")
async def sign_out(request: Request):
    """Sign out user"""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No valid token provided")
        
        token = auth_header.split(" ")[1]
        success = await auth_service.sign_out(token)
        
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Send password reset email"""
    try:
        success = await auth_service.reset_password(request.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-password")
async def update_password(request: UpdatePasswordRequest, http_request: Request):
    """Update user password"""
    try:
        # Extract token from Authorization header
        #auth_header = http_request.headers.get("authorization")
        #if not auth_header or not auth_header.startswith("Bearer "):
        #    raise HTTPException(status_code=401, detail="No valid token provided")
        session = auth_service.client.auth.refresh_session(request.refresh_token) #new


        #token = auth_header.split(" ")[1]
        #success = await auth_service.update_password(token, request.new_password)
        response = auth_service.client.auth.update_user({"password": request.new_password})#new

        if response.user:#new
        #if success:
            return {"message": "Password updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Password update failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/verify")
async def verify_token(request: Request):
    """Verify if current token is valid"""
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No token provided")
        
        token = auth_header.split(" ")[1]
        user = await auth_service.verify_token(token)
        
        # Get full user profile
        user_profile = await supabase_service.get_user_by_id(user["id"])
        
        return {
            "valid": True,
            "user": user,
            "profile": user_profile
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")