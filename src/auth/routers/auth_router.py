from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.utils.bcrypt_helper import generate_access_token
from src.auth.services.auth_service import (
    AuthService,
    LoginInput,
    RegisterInput,
)
from src.util.exceptions import *
from src.share.logging import Logging
from src.db.sql_alchemy import Database
from src.util.response import global_response, GlobalResponse, ExceptionResponse

router = APIRouter(prefix="/auth")
database = Database()
auth = AuthService()
logger = Logging().get_logger()


async def get_db() -> AsyncSession:
    """
    Dependency to get an async SQLAlchemy database session.
    """
    async for db in database.get_db():
        yield db


class AuthOutput(BaseModel):
    access_token: str


@router.post(
    "/register",
    response_model=GlobalResponse[AuthOutput, dict],
    summary="User Registration",
    description="Register a new user with username and password.",
    responses={
        409: {
            "model": ExceptionResponse,
            "description": "User or username already exists"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request"
        },
    }
)
async def register(input: RegisterInput, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    - **username**: User's username
    - **password**: User's password
    """
    try:
        user = await auth.register(input, db)

        payload = {"id": str(user.id)}
        token = generate_access_token(data=payload)
        return global_response(
            {
                "access_token": token,
            }
        )
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/login",
    response_model=GlobalResponse[AuthOutput, dict],
    summary="User Login",
    description="Authenticate a user with username and password.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "User not found"
        },
        401: {
            "model": ExceptionResponse,
            "description": "Incorrect password"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request"
        },
    }
)
async def login(input: LoginInput, db: AsyncSession = Depends(get_db)):
    """
    Login a user and return an access token.

    - **username**: User's username
    - **password**: User's password
    """
    try:
        user = await auth.authenticate_user(input.username.lower(), input.password, db)

        payload = {"id": str(user.id)}
        token = generate_access_token(data=payload)
        return global_response(
            {
                "access_token": token,
            }
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
