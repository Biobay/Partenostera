from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserMode(str, Enum):
    TOOL = "tool"
    VEO = "veo"

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    preferred_mode: UserMode = UserMode.TOOL
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        use_enum_values = True

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    preferred_mode: UserMode = UserMode.TOOL

class UserUpdate(BaseModel):
    name: Optional[str] = None
    preferred_mode: Optional[UserMode] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    preferred_mode: UserMode
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
