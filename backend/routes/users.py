from fastapi import APIRouter, HTTPException, Request
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/users", tags=["Users"])
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/avatar")
async def set_avatar(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    avatar_url = data.get("avatar_url")
    if not user_id or not avatar_url:
        raise HTTPException(status_code=400, detail="Missing user_id or avatar_url")
    # Update the user's avatar in the users table
    result = supabase.table("users").update({"avatar_url": avatar_url}).eq("id", user_id).execute()
    if hasattr(result, 'error') and result.error:
        raise HTTPException(status_code=500, detail="Failed to update avatar")
    return {"message": "Avatar updated successfully"} 