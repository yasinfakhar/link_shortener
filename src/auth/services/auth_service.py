from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from src.util.exceptions import *
from src.db.models import UserModel
from src.share.logging import Logging
from src.db.sql_alchemy import Database
from src.user.services.user_service import UserService
from src.auth.utils.bcrypt_helper import hash_password, verify_password


database = Database()
_logger = Logging().get_logger()


class RegisterInput(BaseModel):
    username: Optional[str] = Field(
        None, example="user@example.com", description="The username of the user"
    )
    password: Optional[str] = Field(
        None,
        example="securepassword123",
        description="The password for the user account",
    )


class LoginInput(BaseModel):
    username: str = Field(
        ..., example="user@example.com", description="The username of the user"
    )
    password: str = Field(
        ...,
        example="securepassword123",
        description="The password for the user account",
    )

class AuthService:
    """
    Service class for handling user authentication and registration logic.
    """

    def __init__(self):
        self.user_service = UserService()

    async def register(self, input: RegisterInput, db: AsyncSession) -> str:
        """
        Registers a new user by saving their details into the database.

        Args:
            input (RegisterInput): The registration input .
            db (Session): The database session for executing queries.

        Returns:
            str: Success message indicating the user was registered.

        Raises:
            HTTPException: If a user with the same username already exists.
        """
        # # Create a new user record
        if len(input.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if input.username and input.password:
            res = await db.execute(
                select(UserModel).where(UserModel.username == input.username.lower())
            )
            existing_user = res.scalar_one_or_none()
            if existing_user:
                raise AlreadyExistsError("This username is already exists")

        if input.password:
            hashed_password = hash_password(input.password)

        new_user = await self.user_service.create_user(
            db,
            input.username,
            hashed_password,
        )

        return new_user

    async def authenticate_user(
        self, username: str, password: str, db: AsyncSession, store: str | None = None
    ):
        """
        Authenticates a user by verifying their username and password.

        Args:
            username (str): The user's username.
            password (str): The user's plaintext password.
            db (Session): The database session for executing queries.

        Returns:
            UserModel: The authenticated user object if authentication is successful.
            bool: `False` if authentication fails.
        """
        # Fetch the user from the database using the provided username
        res = await db.execute(select(UserModel).where(UserModel.username == username))
        user = res.scalar_one_or_none()

        if not user:
            raise NotFoundError("User not found with this username")

        # Verify the provided password matches the stored hash
        if not verify_password(password, user.password):
            raise InvalidPasswordError("Incorrect username or password")

        return user