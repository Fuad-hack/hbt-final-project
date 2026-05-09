"""
User Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Schema for user response"""
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """Schema for list of users with pagination"""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
