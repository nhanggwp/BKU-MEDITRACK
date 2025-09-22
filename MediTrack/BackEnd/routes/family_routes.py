from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.supabase_service import SupabaseService
from services.auth_service import AuthService

router = APIRouter()
supabase_service = SupabaseService()
auth_service = AuthService()

class FamilyGroupRequest(BaseModel):
    name: str

class FamilyMemberRequest(BaseModel):
    user_id: str
    relationship: str  # 'parent', 'child', 'spouse', 'sibling', etc.
    can_manage: bool = False

class FamilyMemberInviteRequest(BaseModel):
    email: str
    relationship: str
    can_manage: bool = False

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

@router.post("/groups")
async def create_family_group(request: Request, group_data: FamilyGroupRequest):
    """Create a new family group"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user is already in a family group
        existing_group = await supabase_service.get_family_group(user_id)
        if existing_group:
            raise HTTPException(status_code=400, detail="User is already part of a family group")
        
        # Create family group
        group_dict = {
            "name": group_data.name,
            "admin_user_id": user_id
        }
        
        family_group = await supabase_service.create_family_group(user_id, group_dict)
        
        # Add creator as family member
        member_data = {
            "family_group_id": family_group["id"],
            "user_id": user_id,
            "relationship": "self",
            "can_manage": True
        }
        
        await supabase_service.add_family_member(member_data)
        
        # Update user as family admin
        await supabase_service.update_user_profile(user_id, {"is_family_admin": True})
        
        return {
            "message": "Family group created successfully",
            "family_group": family_group
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/groups")
async def get_family_group(request: Request):
    """Get user's family group information"""
    try:
        user_id = await get_current_user_id(request)
        
        family_group_info = await supabase_service.get_family_group_with_members(user_id)
        if not family_group_info:
            return {"family_group": None, "members": []}
        
        return {
            "family_group": family_group_info["family_group"],
            "members": family_group_info["members"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/members")
async def add_family_member(request: Request, member_data: FamilyMemberRequest):
    """Add a member to family group"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user has permission to manage family
        family_member = await supabase_service.get_family_member_by_user_id(user_id)
        if not family_member or not family_member.get("can_manage"):
            raise HTTPException(status_code=403, detail="Not authorized to manage family members")
        
        # Add new family member
        new_member_data = {
            "family_group_id": family_member["family_group_id"],
            "user_id": member_data.user_id,
            "relationship": member_data.relationship,
            "can_manage": member_data.can_manage
        }
        
        result = await supabase_service.add_family_member(new_member_data)
        
        return {
            "message": "Family member added successfully",
            "member": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/members")
async def get_family_members(request: Request):
    """Get all family group members"""
    try:
        user_id = await get_current_user_id(request)
        
        family_members = await supabase_service.get_family_members(user_id)
        
        return {
            "members": family_members,
            "count": len(family_members)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/members/{member_user_id}/medical-overview")
async def get_family_member_medical_overview(request: Request, member_user_id: str):
    """Get medical overview for family member"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user has permission to view this member's data
        can_access = await supabase_service.can_access_family_member_data(user_id, member_user_id)
        if not can_access:
            raise HTTPException(status_code=403, detail="Not authorized to view this member's data")
        
        # Get medical overview
        medical_history = await supabase_service.get_medical_history(member_user_id)
        allergies = await supabase_service.get_allergies(member_user_id)
        medication_schedules = await supabase_service.get_medication_schedules(member_user_id)
        recent_reminders = await supabase_service.get_upcoming_reminders(member_user_id, 24)
        
        # Get member profile
        member_profile = await supabase_service.get_user_by_id(member_user_id)
        
        return {
            "member_profile": {
                "id": member_profile["id"],
                "full_name": member_profile.get("full_name"),
                "date_of_birth": member_profile.get("date_of_birth")
            },
            "medical_history": medical_history,
            "allergies": allergies,
            "current_medications": medication_schedules,
            "upcoming_reminders": recent_reminders
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/members/{member_id}")
async def update_family_member(request: Request, member_id: str, member_data: FamilyMemberRequest):
    """Update family member information"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user has permission to manage family
        family_member = await supabase_service.get_family_member_by_user_id(user_id)
        if not family_member or not family_member.get("can_manage"):
            raise HTTPException(status_code=403, detail="Not authorized to manage family members")
        
        # Update family member
        update_data = {
            "relationship": member_data.relationship,
            "can_manage": member_data.can_manage
        }
        
        result = await supabase_service.update_family_member(member_id, update_data)
        
        return {
            "message": "Family member updated successfully",
            "member": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/members/{member_id}")
async def remove_family_member(request: Request, member_id: str):
    """Remove family member from group"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user has permission to manage family
        family_member = await supabase_service.get_family_member_by_user_id(user_id)
        if not family_member or not family_member.get("can_manage"):
            raise HTTPException(status_code=403, detail="Not authorized to manage family members")
        
        await supabase_service.remove_family_member(member_id)
        
        return {
            "message": "Family member removed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invite")
async def invite_family_member(request: Request, invite_data: FamilyMemberInviteRequest):
    """Send invitation to join family group"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user has permission to manage family
        family_member = await supabase_service.get_family_member_by_user_id(user_id)
        if not family_member or not family_member.get("can_manage"):
            raise HTTPException(status_code=403, detail="Not authorized to invite family members")
        
        # Create invitation
        invitation_result = await supabase_service.create_family_invitation(
            family_group_id=family_member["family_group_id"],
            invited_email=invite_data.email,
            relationship=invite_data.relationship,
            can_manage=invite_data.can_manage,
            invited_by_user_id=user_id
        )
        
        return {
            "message": "Family invitation sent successfully",
            "invitation": invitation_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_family_dashboard(request: Request):
    """Get family dashboard with overview of all members"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get family group
        family_group_info = await supabase_service.get_family_group_with_members(user_id)
        if not family_group_info:
            raise HTTPException(status_code=404, detail="User is not part of a family group")
        
        # Get overview for each member
        dashboard_data = []
        for member in family_group_info["members"]:
            member_user_id = member["user_id"]
            
            # Check if current user can access this member's data
            can_access = await supabase_service.can_access_family_member_data(user_id, member_user_id)
            if not can_access:
                continue
            
            # Get basic medical info
            medication_count = await supabase_service.count_active_medications(member_user_id)
            allergy_count = await supabase_service.count_allergies(member_user_id)
            upcoming_reminders_count = await supabase_service.count_upcoming_reminders(member_user_id, 24)
            
            member_overview = {
                "user_id": member_user_id,
                "full_name": member.get("users", {}).get("full_name", "Unknown"),
                "relationship": member["relationship"],
                "active_medications": medication_count,
                "allergies": allergy_count,
                "upcoming_reminders": upcoming_reminders_count,
                "can_manage": member.get("can_manage", False)
            }
            
            dashboard_data.append(member_overview)
        
        return {
            "family_group": family_group_info["family_group"],
            "members_overview": dashboard_data,
            "total_members": len(dashboard_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
