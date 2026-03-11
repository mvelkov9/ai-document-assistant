from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserPublic, UserRegisterRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def register_user(self, payload: UserRegisterRequest) -> UserPublic:
        existing_user = self.user_repository.get_by_email(payload.email)
        if existing_user:
            raise ValueError("User with this email already exists.")

        user = self.user_repository.create(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
        )
        return UserPublic.model_validate(user)

    def authenticate(self, email: str, password: str) -> UserPublic | None:
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return UserPublic.model_validate(user)

    def get_user_by_email(self, email: str) -> UserPublic | None:
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        return UserPublic.model_validate(user)