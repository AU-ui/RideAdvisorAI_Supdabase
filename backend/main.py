from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from routes import auth, users, recommend
from routes import admin

app = FastAPI(title="RideAdvisor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add both possible frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recommend.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Welcome to RideAdvisor API"}

@app.get("/health")
async def health_check():
    try:
        # Test Supabase connection by getting the current user (this will work even without authentication)
        response = supabase.auth.get_user()
        return {
            "status": "healthy",
            "database": "connected",
            "supabase_url": SUPABASE_URL,
            "message": "Successfully connected to Supabase"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 