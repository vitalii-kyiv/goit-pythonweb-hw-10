from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts_repository import ContactRepository
from src.schemas.contact_schema import ContactCreateSchema, ContactUpdateSchema
from src.entity.models import User


class ContactService:
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreateSchema):
        # Прив'язка користувача до контакту
        return await self.contact_repository.create_contact(body, self.current_user.id)

    async def get_contacts(
        self, limit: int = 100, offset: int = 0, search: str | None = None
    ):
        return await self.contact_repository.get_contacts(
            limit, offset, search, self.current_user.id
        )

    async def get_contact(self, contact_id: int):
        contact = await self.contact_repository.get_contact_by_id(contact_id)
        if contact and contact.user_id != self.current_user.id:
            return None  # або піднімай 403
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema):
        contact = await self.get_contact(contact_id)
        if contact is None:
            return None
        return await self.contact_repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        contact = await self.get_contact(contact_id)
        if contact is None:
            return None
        return await self.contact_repository.remove_contact(contact_id)

    async def get_upcoming_birthdays(self):
        return await self.contact_repository.get_upcoming_birthdays(
            self.current_user.id
        )
