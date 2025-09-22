from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, time, date
from services.supabase_service import SupabaseService
from services.auth_service import AuthService

router = APIRouter()
supabase_service = SupabaseService()
auth_service = AuthService()

class MedicationScheduleRequest(BaseModel):
    medication_name: str
    medication_id: Optional[str] = None
    dosage: str
    frequency_per_day: int
    times_of_day: List[str]  # List of time strings like ["08:00", "20:00"]
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None
    notes: Optional[str] = None

class ReminderLogRequest(BaseModel):
    schedule_id: str
    status: str  # 'taken', 'missed', 'skipped'
    actual_time: Optional[str] = None  # ISO format
    notes: Optional[str] = None

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

@router.post("/schedules")
async def create_medication_schedule(request: Request, schedule_data: MedicationScheduleRequest):
    """Create a new medication schedule"""
    try:
        user_id = await get_current_user_id(request)
        
        # Convert times_of_day strings to time objects
        try:
            times = [time.fromisoformat(t) for t in schedule_data.times_of_day]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM format.")
        
        # Prepare schedule data
        schedule_dict = {
            "medication_name": schedule_data.medication_name,
            "medication_id": schedule_data.medication_id,
            "dosage": schedule_data.dosage,
            "frequency_per_day": schedule_data.frequency_per_day,
            "times_of_day": schedule_data.times_of_day,
            "start_date": schedule_data.start_date or datetime.now().date().isoformat(),
            "end_date": schedule_data.end_date,
            "notes": schedule_data.notes,
            "is_active": True
        }
        
        result = await supabase_service.create_medication_schedule(user_id, schedule_dict)
        
        return {
            "message": "Medication schedule created successfully",
            "schedule": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedules")
async def get_medication_schedules(request: Request, active_only: bool = True):
    """Get user's medication schedules"""
    try:
        user_id = await get_current_user_id(request)
        
        schedules = await supabase_service.get_medication_schedules(user_id, active_only)
        
        return {
            "schedules": schedules,
            "count": len(schedules)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedules/{schedule_id}")
async def get_medication_schedule(request: Request, schedule_id: str):
    """Get specific medication schedule"""
    try:
        user_id = await get_current_user_id(request)
        
        schedule = await supabase_service.get_medication_schedule_by_id(schedule_id)
        if not schedule or schedule["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Medication schedule not found")
        
        return {
            "schedule": schedule
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/schedules/{schedule_id}")
async def update_medication_schedule(
    request: Request, 
    schedule_id: str, 
    schedule_data: MedicationScheduleRequest
):
    """Update medication schedule"""
    try:
        user_id = await get_current_user_id(request)
        
        # Verify schedule belongs to user
        schedule = await supabase_service.get_medication_schedule_by_id(schedule_id)
        if not schedule or schedule["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Medication schedule not found")
        
        # Prepare update data
        update_data = {k: v for k, v in schedule_data.dict().items() if v is not None}
        
        result = await supabase_service.update_medication_schedule(schedule_id, update_data)
        
        return {
            "message": "Medication schedule updated successfully",
            "schedule": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/schedules/{schedule_id}")
async def delete_medication_schedule(request: Request, schedule_id: str):
    """Delete medication schedule"""
    try:
        user_id = await get_current_user_id(request)
        
        # Verify schedule belongs to user
        schedule = await supabase_service.get_medication_schedule_by_id(schedule_id)
        if not schedule or schedule["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Medication schedule not found")
        
        await supabase_service.delete_medication_schedule(schedule_id)
        
        return {
            "message": "Medication schedule deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming")
async def get_upcoming_reminders(request: Request, hours_ahead: int = 24):
    """Get upcoming medication reminders"""
    try:
        user_id = await get_current_user_id(request)
        
        upcoming_reminders = await supabase_service.get_upcoming_reminders(user_id, hours_ahead)
        
        return {
            "reminders": upcoming_reminders,
            "count": len(upcoming_reminders),
            "hours_ahead": hours_ahead
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log")
async def log_reminder_action(request: Request, log_data: ReminderLogRequest):
    """Log reminder action (taken, missed, skipped)"""
    try:
        user_id = await get_current_user_id(request)
        
        # Verify schedule belongs to user
        schedule = await supabase_service.get_medication_schedule_by_id(log_data.schedule_id)
        if not schedule or schedule["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Medication schedule not found")
        
        # Prepare log data
        log_dict = {
            "schedule_id": log_data.schedule_id,
            "status": log_data.status,
            "actual_time": log_data.actual_time or datetime.now().isoformat(),
            "notes": log_data.notes
        }
        
        result = await supabase_service.create_reminder_log(log_dict)
        
        return {
            "message": "Reminder action logged successfully",
            "log": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adherence")
async def get_medication_adherence(request: Request, days: int = 30):
    """Get medication adherence statistics"""
    try:
        user_id = await get_current_user_id(request)
        
        adherence_stats = await supabase_service.get_medication_adherence(user_id, days)
        
        return {
            "adherence_stats": adherence_stats,
            "period_days": days
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_reminder_logs(
    request: Request, 
    schedule_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get reminder logs"""
    try:
        user_id = await get_current_user_id(request)
        
        logs = await supabase_service.get_reminder_logs(user_id, schedule_id, limit, offset)
        
        return {
            "logs": logs,
            "count": len(logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedules/{schedule_id}/toggle")
async def toggle_schedule_status(request: Request, schedule_id: str):
    """Toggle medication schedule active status"""
    try:
        user_id = await get_current_user_id(request)
        
        # Verify schedule belongs to user
        schedule = await supabase_service.get_medication_schedule_by_id(schedule_id)
        if not schedule or schedule["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Medication schedule not found")
        
        new_status = not schedule["is_active"]
        result = await supabase_service.update_medication_schedule(
            schedule_id, 
            {"is_active": new_status}
        )
        
        return {
            "message": f"Schedule {'activated' if new_status else 'deactivated'} successfully",
            "schedule": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
