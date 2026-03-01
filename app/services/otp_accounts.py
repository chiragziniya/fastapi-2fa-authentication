import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp_account import OtpAccount


async def list_accounts(db: AsyncSession, user_id: str) -> list[OtpAccount]:
    result = await db.execute(
        select(OtpAccount)
        .where(OtpAccount.user_id == uuid.UUID(user_id))
        .order_by(OtpAccount.created_at.asc())
    )
    return list(result.scalars().all())


async def create_account(
    db: AsyncSession,
    user_id: str,
    issuer: str,
    account_name: str,
    encrypted_secret: str,
    algorithm: str,
    digits: int,
    period: int,
) -> OtpAccount:
    account = OtpAccount(
        user_id=uuid.UUID(user_id),
        issuer=issuer,
        account_name=account_name,
        encrypted_secret=encrypted_secret,
        algorithm=algorithm,
        digits=digits,
        period=period,
    )
    db.add(account)
    await db.flush()
    return account


async def get_account(db: AsyncSession, account_id: str, user_id: str) -> OtpAccount | None:
    result = await db.execute(
        select(OtpAccount).where(
            OtpAccount.id == uuid.UUID(account_id),
            OtpAccount.user_id == uuid.UUID(user_id),
        )
    )
    return result.scalar_one_or_none()


async def update_account(
    db: AsyncSession, account: OtpAccount, issuer: str | None, account_name: str | None
) -> OtpAccount:
    if issuer is not None:
        account.issuer = issuer
    if account_name is not None:
        account.account_name = account_name
    await db.flush()
    return account


async def delete_account(db: AsyncSession, account: OtpAccount) -> None:
    await db.delete(account)
    await db.flush()
