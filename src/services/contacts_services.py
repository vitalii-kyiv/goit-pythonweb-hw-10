from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts_repository import ContactRepository
from src.schemas.contact_schema import (
    ContactCreateSchema,
    ContactUpdateSchema
)


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreateSchema):
        return await self.contact_repository.create_contact(body)

    async def get_contacts(self, limit: int = 100, offset: int = 0, search: str | None = None):
        return await self.contact_repository.get_contacts(limit, offset, search)

    async def get_contact(self, contact_id: int):
        return await self.contact_repository.get_contact_by_id(contact_id)

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema):
        return await self.contact_repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        return await self.contact_repository.remove_contact(contact_id)

    async def get_upcoming_birthdays(self):
        return await self.contact_repository.get_upcoming_birthdays()