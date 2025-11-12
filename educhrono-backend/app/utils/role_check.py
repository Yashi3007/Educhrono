from fastapi import HTTPException, Depends, Request
from jose import jwt, JWTError
from datetime import datetime
from app import db

SECRET_KEY = "educhrono@@secret"
ALGORITHM = "HS256"

# ✅ Core function to verify JWT
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")

        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Optional: check if user still exists
        user = db["users"].find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {"email": email, "role": role.lower(), "name": user.get("name", "")}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ✅ Restrict route by role(s)
def require_roles(allowed_roles: list):
    def wrapper(request: Request):
        user = get_current_user(request)
        if user["role"] not in [r.lower() for r in allowed_roles]:
            raise HTTPException(status_code=403, detail=f"Access denied for role: {user['role']}")
        return user

    return wrapper
