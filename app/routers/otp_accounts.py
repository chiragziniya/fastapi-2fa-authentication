from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.otp_account import OtpAccountCreate, OtpAccountUpdate, OtpAccountResponse
from app.services.otp_accounts import (
    list_accounts,
    create_account,
    get_account,
    update_account,
    delete_account,
)

router = APIRouter(prefix="/otp-accounts", tags=["otp_accounts"])


def _to_response(account) -> OtpAccountResponse:
    return OtpAccountResponse(
        id=str(account.id),
        user_id=str(account.user_id),
        issuer=account.issuer,
        account_name=account.account_name,
        encrypted_secret=account.encrypted_secret,
        algorithm=account.algorithm,
        digits=account.digits,
        period=account.period,
        created_at=account.created_at,
    )


@router.get("/", response_model=list[OtpAccountResponse])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    accounts = await list_accounts(db, str(current_user.id))
    return [_to_response(a) for a in accounts]


@router.post("/", response_model=OtpAccountResponse, status_code=status.HTTP_201_CREATED)
async def add_account(
    body: OtpAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await create_account(
        db,
        user_id=str(current_user.id),
        issuer=body.issuer,
        account_name=body.account_name,
        encrypted_secret=body.encrypted_secret,
        algorithm=body.algorithm,
        digits=body.digits,
        period=body.period,
    )
    return _to_response(account)


@router.patch("/{account_id}", response_model=OtpAccountResponse)
async def edit_account(
    account_id: str,
    body: OtpAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await get_account(db, account_id, str(current_user.id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    updated = await update_account(db, account, body.issuer, body.account_name)
    return _to_response(updated)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await get_account(db, account_id, str(current_user.id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    await delete_account(db, account)
