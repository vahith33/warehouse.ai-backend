from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse
from app.core.database import db
from app.core.security import create_access_token, verify_password, get_password_hash
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: RegisterRequest):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered with this email")

    # Hash the password and save
    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password
    user_data["createdAt"] = datetime.utcnow().isoformat()

    result = await db.users.insert_one(user_data)
    
    return {
        "message": "User registered successfully ✅",
        "id": str(result.inserted_id)
    }

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    # Check against the user database
    user = await db.users.find_one({"email": credentials.email})
    
    # Try to verify against hashed password; fallback to plain text for legacy support
    # (In production, you'd only use hashed verification)
    is_valid = False
    if user:
        try:
            is_valid = verify_password(credentials.password, user["password"])
        except ValueError:
            # Fallback for plain text passwords in transition
            is_valid = (user["password"] == credentials.password)

    if is_valid:
        token_data = {"sub": credentials.email, "role": user.get("role", "admin")}
        token = create_access_token(data=token_data)

        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name", "Admin"),
                "email": user.get("email", credentials.email),
                "role": user.get("role", "admin"),
                "createdAt": user.get("createdAt", "")
            }
        }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")
