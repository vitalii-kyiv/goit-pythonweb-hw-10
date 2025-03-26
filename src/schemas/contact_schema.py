from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactCreateSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, description="Ім'я контакту")
    last_name: str = Field(min_length=2, max_length=50, description="Прізвище контакту")
    email: EmailStr = Field(description="Електронна адреса контакту")
    phone_number: str = Field(min_length=5, max_length=20, description="Номер телефону")
    birthday: date = Field(description="День народження контакту")
    additional_info: Optional[str] = Field(
        default=None, max_length=255, description="Додаткова інформація"
    )


class ContactUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    birthday: Optional[date] = None
    additional_info: Optional[str] = Field(None, max_length=255)


class ContactResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
