import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts_services import ContactService
from src.schemas.contact_schema import (
    ContactCreateSchema,
    ContactResponseSchema,
    ContactUpdateSchema,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponseSchema])
async def get_contacts(
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Пошук за ім'ям, прізвищем або email"),
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    return await contact_service.get_contacts(limit, offset, search)


@router.get(
    "/birthdays/upcoming",
    response_model=list[ContactResponseSchema],
    description="Контакти з днями народження на наступні 7 днів",
)
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays()


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_contact(body: ContactCreateSchema, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body)


@router.put("/{contact_id}", response_model=ContactResponseSchema)
async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    await contact_service.remove_contact(contact_id)
    return None