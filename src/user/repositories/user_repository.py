from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import load_only

from src.db.models import UserModel
 


class UserRepository:
    """
    Repository class for handling CRUD operations on the UserModel.
    """

    async def get_by_id(
        self, db_session: AsyncSession, user_id: UUID = None
    ) -> Optional[UserModel]:
        """
        Retrieves a user by their ID.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.

        Returns:
            Optional[UserModel]: The user if found, otherwise None.
        """
        stmt = (
            select(UserModel)
            .options(load_only(UserModel.id, UserModel.username))
            .where(UserModel.id == user_id)
        )
        res = await db_session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all(self, db_session: AsyncSession) -> list[UserModel]:
        """
        Retrieves all users.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[UserModel]: A list of all users.
        """
        stmt = select(UserModel).options(load_only(UserModel.id, UserModel.username))
        res = await db_session.execute(stmt)
        return list(res.scalars().all())

    async def create(self, db_session: AsyncSession, user: UserModel) -> UserModel:
        """
        Creates a new user.

        Args:
            db_session (Session): The database session to use.
            user (UserModel): The user instance to add.

        Returns:
            UserModel: The created user instance.
        """
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def update(self, db_session: AsyncSession, new_data: dict) -> UserModel:
        raise NotImplementedError

    async def delete(self, user: UserModel) -> UserModel:
        raise NotImplementedError
