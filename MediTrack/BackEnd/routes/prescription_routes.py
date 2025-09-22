# routes/prescription_routes.py
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import List
from services.supabase_service import SupabaseService

router = APIRouter()
sb = SupabaseService()

class SaveMedsBody(BaseModel):
    medications: List[str]

@router.post("/prescriptions/save")
async def save_prescription_items(body: SaveMedsBody, request: Request):
    print("✅ Route save_prescription_items CALLED")
    user = getattr(request.state, "user", None)
    token = getattr(request.state, "token", None)
    if not user or not user.get("id") or not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 🔑 RẤT QUAN TRỌNG: set token cho đúng instance `sb` dùng trong route này
    sb.set_auth_token(token)

    try:
        uniq = list(dict.fromkeys([(n or "").strip() for n in body.medications if n and n.strip()]))
        rows = [{"user_id": user["id"], "medication_name": n} for n in uniq]
        print("📝 Rows to upsert:", rows)

        resp = (
            sb.client.table("prescription_items")
            .upsert(rows, on_conflict="user_id,medication_name")
            .execute()
        )
        print("📦 Supabase upsert resp:", resp)
        return {"ok": True, "inserted": len(resp.data or []), "data": resp.data or []}
    except Exception as e:
        print("❌ save_prescription_items error:", e)
        raise HTTPException(status_code=500, detail="Failed to save prescriptions")

@router.get("/prescriptions/list")
async def list_prescriptions(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    user = getattr(request.state, "user", None)
    token = getattr(request.state, "token", None)
    if not user or not user.get("id") or not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 🔑 Set token cho instance `sb` trong route này
    sb.set_auth_token(token)

    try:
        print("🔑 list_prescriptions user_id =", user["id"])
        resp = (
            sb.client.table("prescription_items")
            .select("medication_name, created_at")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        items = [row["medication_name"] for row in (resp.data or []) if row.get("medication_name")]
        return {"items": items, "count": len(items), "offset": offset, "limit": limit}
    except Exception as e:
        print("❌ list_prescriptions error:", e)
        raise HTTPException(status_code=500, detail="Failed to list prescriptions")
