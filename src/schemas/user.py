from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=50, description="Username")
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=12, description="Password")


class UserResponse(UserBase):
    id: int
    avatar: str | None
    model_config = ConfigDict(from_attributes=True)