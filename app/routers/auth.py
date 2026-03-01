from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    SignUpRequest,
    SignInRequest,
    TokenResponse,
    UserResponse,
    ResetPasswordRequest,
    UpdatePasswordRequest,
    MessageResponse,
)
from app.services.auth import (
    get_user_by_email,
    create_user,
    verify_password,
    create_access_token,
    generate_reset_token,
    validate_reset_token,
    update_user_password,
)
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignUpRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    await create_user(db, body.email, body.password)
    return MessageResponse(message="Account created successfully")


@router.post("/signin", response_model=TokenResponse)
async def signin(body: SignInRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(str(user.id), user.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=str(user.id), email=user.email),
    )


@router.post("/signout", response_model=MessageResponse)
async def signout():
    # JWT is stateless — client simply discards the token.
    # This endpoint exists for API contract compatibility.
    return MessageResponse(message="Signed out")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=str(current_user.id), email=current_user.email)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, body.email)
    if not user:
        # Don't reveal whether email exists
        return MessageResponse(message="If the email exists, a reset link has been sent")
    token = await generate_reset_token(db, user)
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    if settings.mail_mode == "console":
        print(f"\n{'='*50}")
        print(f"PASSWORD RESET LINK for {user.email}:")
        print(f"{reset_url}")
        print(f"{'='*50}\n")
    else:
        # TODO: plug in real SMTP sending
        pass

    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/update-password", response_model=MessageResponse)
async def update_password_with_token(
    body: UpdatePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update password for an authenticated user (e.g. after clicking reset link and re-logging in)."""
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    await update_user_password(db, current_user, body.password)
    return MessageResponse(message="Password updated successfully")


@router.post("/reset-password-confirm", response_model=TokenResponse)
async def reset_password_confirm(
    token: str,
    body: UpdatePasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Confirm password reset using the token from the reset email."""
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user = await validate_reset_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    await update_user_password(db, user, body.password)
    access_token = create_access_token(str(user.id), user.email)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=str(user.id), email=user.email),
    )
