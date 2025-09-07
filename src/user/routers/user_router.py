from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.sql_alchemy import Database
from src.auth.utils.get_token import authenticate_user
from src.user.services.user_service import UserService
from src.util.response import global_response, GlobalResponse


router = APIRouter(prefix="/user")
database = Database()


async def get_db() -> AsyncSession:
    async for db in database.get_db():
        yield db


def get_user_service() -> UserService:
    return UserService()


class CreateUserInput(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class UserOutput(BaseModel):
    id: UUID
    username: str
    created_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    updated_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    deleted_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")

    class Config:
        from_attributes = True


@router.get("", response_model=GlobalResponse[UserOutput, dict])
async def get_user(
    user_id: str = Depends(authenticate_user),
    db: AsyncSession = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Retrieves a user by their ID.

    Returns:
        UserOutput: The user data
    """
    try:
        user = await service.get_user(db, UUID(user_id))
        return global_response(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
