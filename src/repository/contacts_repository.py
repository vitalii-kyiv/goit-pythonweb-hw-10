import logging
from typing import Sequence

from sqlalchemy import select, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from src.entity.models import Contact
from src.schemas.contact_schema import ContactCreateSchema, ContactUpdateSchema

logger = logging.getLogger("uvicorn.error")


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, limit: int, offset: int, search: str | None = None) -> Sequence[Contact]:
        stmt = select(Contact).offset(offset).limit(limit)
        if search:
            stmt = stmt.where(
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                )
            )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreateSchema) -> Contact:
        contact = Contact(**body.model_dump())
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            update_data = body.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_upcoming_birthdays(self) -> Sequence[Contact]:
        today = date.today()
        next_week = today + timedelta(days=7)
        stmt = select(Contact).where(
            or_(
                (extract('month', Contact.birthday) == today.month) & (extract('day', Contact.birthday) >= today.day),
                (extract('month', Contact.birthday) == next_week.month) & (extract('day', Contact.birthday) <= next_week.day),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()