import uuid
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User

settings = get_settings()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.flush()
    return user


async def generate_reset_token(db: AsyncSession, user: User) -> str:
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    await db.flush()
    return token


async def validate_reset_token(db: AsyncSession, token: str) -> User | None:
    result = await db.execute(
        select(User).where(
            User.reset_token == token,
            User.reset_token_expires > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def update_user_password(db: AsyncSession, user: User, new_password: str) -> None:
    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.flush()
