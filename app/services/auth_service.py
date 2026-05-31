from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.models.users import User
from app.models.refresh_token import RefreshToken
from app.repositories.token_repository import TokenRepository


class AuthService:

    @staticmethod
    def register(db, username: str, email: str, password: str):

        # check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email already exists")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    
    @staticmethod
    def login(db, email: str, password: str):

        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        access_token = create_access_token(str(user.id))

        refresh_token = create_refresh_token()

        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        refresh_record = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )

        TokenRepository.create(db, refresh_record)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
    @staticmethod
    def refresh_access_token(db, refresh_token: str):

        token_record = TokenRepository.get_by_token(
            db,
            refresh_token
        )

        if not token_record:
            return None

        if token_record.revoked:
            return None

        if token_record.expires_at < datetime.utcnow():
            return None

        new_access_token = create_access_token(
            str(token_record.user_id)
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    @staticmethod
    def logout(db, refresh_token: str):

        token_record = TokenRepository.get_by_token(
            db,
            refresh_token
        )

        if not token_record:
            return False

        TokenRepository.revoke(
            db,
            token_record
        )

        return True