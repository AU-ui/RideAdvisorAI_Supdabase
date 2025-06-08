from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/admin", tags=["Admin"])
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Admin Login ---
class AdminLogin(BaseModel):
    email: str
    password: str

@router.post("/login")
def admin_login(data: AdminLogin):
    # Demo: check against a hardcoded admin (replace with DB check in production)
    admin_email = "admin@rideadvisor.com"
    admin_password = "admin123"  # In production, use hashed passwords!
    if data.email == admin_email and data.password == admin_password:
        return {"message": "Admin login successful", "token": "demo-admin-token"}
    raise HTTPException(status_code=401, detail="Invalid admin credentials")

# --- User Management ---
class UserEdit(BaseModel):
    fullName: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    blocked: Optional[bool]

@router.get("/users")
def list_users():
    users = supabase.table("users").select("id, email, fullName, avatar_url, blocked").execute()
    return users.data

@router.put("/users/{user_id}")
async def edit_user(user_id: str, request: Request):
    raw_body = await request.body()
    print("Raw request body:", raw_body)
    try:
        data = await request.json()
        print("Parsed JSON:", data)
    except Exception as e:
        print("JSON parse error:", e)
        raise HTTPException(status_code=400, detail=f"JSON parse error: {e}")
    # Now use the parsed data to update the user
    update_data = {k: v for k, v in data.items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = supabase.table("users").update(update_data).eq("id", user_id).execute()
    if hasattr(result, 'error') and result.error:
        raise HTTPException(status_code=500, detail="Failed to update user")
    return {"message": "User updated successfully"}

@router.post("/users/{user_id}/block")
def block_user(user_id: str):
    result = supabase.table("users").update({"blocked": True}).eq("id", user_id).execute()
    if hasattr(result, 'error') and result.error:
        raise HTTPException(status_code=500, detail="Failed to block user")
    return {"message": "User blocked"}

@router.post("/users/{user_id}/unblock")
def unblock_user(user_id: str):
    result = supabase.table("users").update({"blocked": False}).eq("id", user_id).execute()
    if hasattr(result, 'error') and result.error:
        raise HTTPException(status_code=500, detail="Failed to unblock user")
    return {"message": "User unblocked"}

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    result = supabase.table("users").delete().eq("id", user_id).execute()
    if hasattr(result, 'error') and result.error:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    return {"message": "User deleted"} 