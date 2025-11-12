# app/models/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = Field(..., description="admin | hod | teacher | student")
    department: Optional[str] = None
    semester: Optional[int] = Field(None, description="Applicable only for students")
    section: Optional[str] = Field(None, description="Applicable only for students")

class UserCreate(UserBase):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str
