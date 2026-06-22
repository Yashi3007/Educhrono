from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from pymongo import ReturnDocument
from app import db

router = APIRouter()

# ==============================
# 🔐 CONFIG
# ==============================
SECRET_KEY = "educhrono@@secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==============================
# 🧩 MODELS
# ==============================
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    department: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Amit Verma",
                "email": "amit.verma@educhrono.in",
                "password": "Student@123",
                "role": "student",
                "department": "Computer Science",
                "semester": 3,
                "section": "B"
            }
        }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


# ==============================
# ⚙️ HELPERS
# ==============================
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    try:
        # ✅ Normal secure verification
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # ✅ SAFETY FALLBACK:
        # Agar DB me password plain text ho
        return plain_password == hashed_password



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==============================
# 👑 AUTO CREATE ADMIN
# ==============================
def ensure_admin_user():
    existing = db["users"].find_one({"email": "admin@educhrono.in"})
    if not existing:
        db["users"].insert_one({
            "name": "System Admin",
            "email": "admin@educhrono.in",
            "password": get_password_hash("Admin@123"),
            "role": "ADMIN",
            "createdAt": datetime.utcnow(),
        })
        print("✅ Default admin created: admin@educhrono.in / Admin@123")


# ==============================
# 🧾 REGISTER ROUTE
# ==============================
@router.post("/register", response_model=TokenResponse, tags=["Authentication"])
def register_user(request: RegisterRequest):
    ensure_admin_user()

    # 🔹 Hash password
    hashed_pw = get_password_hash(request.password)

    # 🔹 MongoDB Atomic Upsert: Update if exists, insert if not
    user_data = {
        "name": request.name,
        "password": hashed_pw,
        "role": request.role.upper(),
        "department": request.department,
        "updatedAt": datetime.utcnow()
    }
    
    # Add semester & section if student
    if request.role.lower() == "student":
        user_data["semester"] = request.semester
        user_data["section"] = request.section

    # Execute atomic upsert in MongoDB
    user_to_return = db["users"].find_one_and_update(
        {"email": request.email},
        {
            "$set": user_data,
            "$setOnInsert": {"email": request.email, "createdAt": datetime.utcnow()}
        },
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    # 🔹 Generate access token with extra info
    token_data = {
        "sub": user_to_return["email"],
        "role": user_to_return["role"],
        "semester": user_to_return.get("semester"),
        "section": user_to_return.get("section"),
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user_to_return["email"],
            "role": user_to_return["role"],
            "name": user_to_return["name"],
            "semester": user_to_return.get("semester"),
            "section": user_to_return.get("section"),
            "token": access_token,
        },
    }


# ==============================
# 🔐 LOGIN ROUTE
# ==============================
@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
def login(request: LoginRequest):
    ensure_admin_user()

    # 🔹 Safety Check: Check if multiple accounts exist for this email
    user_docs = list(db["users"].find({"email": request.email}))
    
    if len(user_docs) > 1:
        raise HTTPException(
            status_code=500, 
            detail="Database integrity error: Multiple accounts found with this email. Please contact admin."
        )
    
    if not user_docs:
        raise HTTPException(status_code=401, detail="User not found")

    user = user_docs[0]

    if not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 🔹 Include semester/section in token if available
    token_data = {
        "sub": user["email"],
        "role": user["role"],
        "semester": user.get("semester"),
        "section": user.get("section"),
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "role": user["role"],
            "name": user.get("name", ""),
            "semester": user.get("semester"),
            "section": user.get("section"),
            "token": access_token,
        },
    }
