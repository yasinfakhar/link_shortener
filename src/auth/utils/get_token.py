from src.util.exceptions import JWTDecodeError
from fastapi import Depends, HTTPException, Request, status
from src.auth.utils.bcrypt_helper import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)
get_credentials = Depends(security)


def get_jwt_token(request: Request):
    """
    Extract the JWT token from the Authorization header of the HTTP request.

    Parameters:
        request (Request): The incoming HTTP request object.

    Returns:
        str: The JWT token extracted from the Authorization header.

    Raises:
        HTTPException: If the Authorization header is missing or invalid.
    """
    authorization: str = request.headers.get("Authorization")
    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer":
            return param
    # Fallback: allow passing token via query param for redirect-based flows
    token_q = request.query_params.get("token")
    if token_q:
        return token_q
    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
    )


def authenticate_user(
    request: Request,
    authorization: HTTPAuthorizationCredentials = get_credentials
):
    """
    Authenticate the user by decoding the JWT token and extracting the user ID.

    Parameters:
        request (Request): The incoming HTTP request object.
        authorization (HTTPAuthorizationCredentials): The bearer token
        credentials, automatically provided by FastAPI dependency injection.

    Returns:
        str: The user ID extracted from the decoded JWT token.

    Raises:
        HTTPException: If the token is missing, invalid, or malformed.
    """
    token: str = ""
    if authorization:
        token = authorization.credentials
    else:
        token = get_jwt_token(request)
    try:
        decode_token = decode_access_token(token)
        return decode_token["user_id"]
    except JWTDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        # Handle any other unexpected errors with a 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
