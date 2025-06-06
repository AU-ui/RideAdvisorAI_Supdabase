from fastapi import APIRouter, HTTPException, Depends
from supabase import create_client, Client
from models import UserCreate, UserLogin, UserResponse
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    try:
        print("Received registration request:", user.dict())
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Register user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "fullName": user.fullName
                }
            }
        })
        
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        # Store additional user data in the users table
        user_data = {
            "id": auth_response.user.id,
            "email": user.email,
            "fullName": user.fullName
        }
        
        # Insert user data into the users table
        data = supabase.table("users").insert(user_data).execute()
        
        return UserResponse(
            id=auth_response.user.id,
            email=user.email,
            fullName=user.fullName
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print("Registration error:", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_user(user: UserLogin):
    try:
        # Login user with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        
        if auth_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check if email is verified
        if not auth_response.user.email_confirmed_at:
            raise HTTPException(
                status_code=401,
                detail="Please verify your email before logging in"
            )
        
        # Get user data from the users table
        user_data = supabase.table("users").select("*").eq("id", auth_response.user.id).single().execute()
        
        return {
            "access_token": auth_response.session.access_token,
            "user": UserResponse(
                id=auth_response.user.id,
                email=user_data.data["email"],
                fullName=user_data.data["fullName"]
            )
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/verify-email")
async def verify_email(token: str):
    try:
        # Verify email using the token
        response = supabase.auth.verify_otp({
            "token_hash": token,
            "type": "email"
        })
        return {"message": "Email verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/resend-verification")
async def resend_verification(email: str):
    try:
        # Resend verification email
        response = supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        return {"message": "Verification email sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 