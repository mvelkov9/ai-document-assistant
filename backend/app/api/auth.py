from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from slowapi import Limiter
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import get_client_ip
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserPublic,
    UserRegisterRequest,
)
from app.services.auth_service import AuthService

_settings = get_settings()
router = APIRouter(prefix="/auth")
bearer_scheme = HTTPBearer()
limiter = Limiter(key_func=get_client_ip, enabled=_settings.app_env != "test")


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Returns 409 if email is already registered.",
)
@limiter.limit("5/minute")
def register(request: Request, payload: UserRegisterRequest, db: Session = Depends(get_db)) -> UserPublic:
    auth_service = AuthService(db)
    try:
        return auth_service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain JWT",
    description="Validate credentials and return a bearer access token.",
)
@limiter.limit("5/minute")
def login(request: Request, payload: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    auth_service = AuthService(db)
    user = auth_service.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return TokenResponse(access_token=create_access_token(user.email))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserPublic:
    settings = get_settings()
    auth_service = AuthService(db)
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing subject.",
        )

    user = auth_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist anymore.",
        )
    return user


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user profile",
    description="Return the profile of the currently authenticated user.",
)
def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return current_user
