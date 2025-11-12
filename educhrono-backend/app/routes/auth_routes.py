from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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

    # 🔹 Check if already exists
    existing = db["users"].find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists with this email")

    # 🔹 Hash password
    hashed_pw = get_password_hash(request.password)

    # 🔹 Common user data
    new_user = {
        "name": request.name,
        "email": request.email,
        "password": hashed_pw,
        "role": request.role.upper(),
        "department": request.department,
        "createdAt": datetime.utcnow(),
    }

    # 🔹 Add semester & section if student
    if request.role.lower() == "student":
        if not request.semester or not request.section:
            raise HTTPException(
                status_code=400,
                detail="Semester and Section are required for student registration."
            )
        new_user["semester"] = request.semester
        new_user["section"] = request.section

    db["users"].insert_one(new_user)

    # 🔹 Generate access token with extra info
    token_data = {
        "sub": new_user["email"],
        "role": new_user["role"],
        "semester": new_user.get("semester"),
        "section": new_user.get("section"),
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": new_user["email"],
            "role": new_user["role"],
            "name": new_user["name"],
            "semester": new_user.get("semester"),
            "section": new_user.get("section"),
            "token": access_token,
        },
    }


# ==============================
# 🔐 LOGIN ROUTE
# ==============================
@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
def login(request: LoginRequest):
    ensure_admin_user()

    user = db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

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
