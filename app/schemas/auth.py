from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "admin"

class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    role: str
    createdAt: Optional[str] = ""

class LoginResponse(BaseModel):
    message: str
    token: str
    user: UserInfo
