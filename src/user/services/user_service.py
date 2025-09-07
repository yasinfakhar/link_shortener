from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import UserModel
from src.user.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    async def create_user(
        self, db_session: AsyncSession, username: str = None, password: str = None
    ) -> UserModel:
        """
        Creates a new user

        Args:
            db_session (Session): The database session.
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            UserModel: The created user instance.
        """
        if username:
            username = username.lower()
        _user = UserModel(
            username=username,
            password=password,
        )
        user = await self.repository.create(db_session, _user)

        return user

    async def get_user(self, db_session: AsyncSession, user_id: UUID) -> UserModel:
        """
        Retrieves a user by their ID.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user to retrieve.

        Returns:
            UserModel: The User instance.

        Raises:
            Exception: If the user is not found.
        """
        user = await self.repository.get_by_id(db_session, user_id)
        if not user:
            raise Exception("User not found")
        return user
