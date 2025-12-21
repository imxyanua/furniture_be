from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    img: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None


class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = "user"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    img: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    img: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    date_enter: datetime
    status: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
