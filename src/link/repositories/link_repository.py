from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.db.models import LinkModel


class LinkRepository:
    async def get_by_id(self, db: AsyncSession, link_id: int) -> Optional[LinkModel]:
        res = await db.execute(
            select(LinkModel).where(LinkModel.id == link_id)
        )
        return res.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[LinkModel]:
        res = await db.execute(
            select(LinkModel).where(LinkModel.short_code == code)
        )
        return res.scalar_one_or_none()

    async def list(self, db: AsyncSession, user_id: Optional[str] = None) -> List[LinkModel]:
        stmt = select(LinkModel)
        if user_id:
            stmt = stmt.where(LinkModel.user_id == user_id)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, db: AsyncSession, link: LinkModel) -> LinkModel:
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    async def update(self, db: AsyncSession, link_id: int, new_values: dict) -> Optional[LinkModel]:
        await db.execute(
            update(LinkModel)
            .where(LinkModel.id == link_id)
            .values(**new_values)
        )
        await db.commit()
        # return the updated link
        return await self.get_by_id(db, link_id)

    async def delete(self, db: AsyncSession, link_id: int) -> None:
        await db.execute(delete(LinkModel).where(LinkModel.id == link_id))
        await db.commit()
