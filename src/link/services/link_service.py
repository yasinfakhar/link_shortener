import random
import string
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import LinkModel
from src.link.repositories.link_repository import LinkRepository


def _generate_code(length: int = 7) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choices(alphabet, k=length))


class LinkService:
    def __init__(self) -> None:
        self.repository = LinkRepository()

    async def create_link(
        self,
        db: AsyncSession,
        original_url: str,
        preferred_code: Optional[str] = None,
    ) -> LinkModel:
        # ensure unique short_code
        code = preferred_code or _generate_code()
        # retry a few times if collision
        for _ in range(10):
            exists = await self.repository.get_by_code(db, code)
            if not exists:
                break
            code = _generate_code()
        if await self.repository.get_by_code(db, code):
            raise ValueError("Could not generate unique short code; please try again")

        link = LinkModel(original_url=original_url, short_code=code)
        return await self.repository.create(db, link)

    async def get_link(self, db: AsyncSession, link_id: int) -> LinkModel:
        link = await self.repository.get_by_id(db, link_id)
        if not link:
            raise ValueError("Link not found")
        return link

    async def get_by_code(self, db: AsyncSession, code: str) -> LinkModel:
        link = await self.repository.get_by_code(db, code)
        if not link:
            raise ValueError("Link not found")
        return link

    async def list_links(self, db: AsyncSession) -> List[LinkModel]:
        return await self.repository.list(db)

    async def update_link(self, db: AsyncSession, link_id: int, original_url: Optional[str] = None, short_code: Optional[str] = None) -> LinkModel:
        new_values = {}
        if original_url is not None:
            new_values["original_url"] = original_url
        if short_code is not None:
            # ensure unique if changing
            exists = await self.repository.get_by_code(db, short_code)
            if exists and exists.id != link_id:
                raise ValueError("Short code already in use")
            new_values["short_code"] = short_code
        updated = await self.repository.update(db, link_id, new_values)
        if not updated:
            raise ValueError("Link not found")
        return updated

    async def delete_link(self, db: AsyncSession, link_id: int) -> None:
        await self.repository.delete(db, link_id)
