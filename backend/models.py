from pydantic import BaseModel, EmailStr, constr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6)  # Minimum password length of 6 characters
    fullName: str  # Changed from full_name to match frontend

    @validator('password')
    def password_strength(cls, v):
        errors = []
        if not re.search(r'[A-Z]', v):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            errors.append('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append('Password must contain at least one special character')
        
        if errors:
            raise ValueError('; '.join(errors))
        return v

    @validator('fullName')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        if not all(x.isalpha() or x.isspace() for x in v):
            raise ValueError('Full name can only contain letters and spaces')
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    fullName: str  # Changed from full_name to match frontend 