from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str

    model_config = {"from_attributes": True}


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class UpdatePasswordRequest(BaseModel):
    password: str


class MessageResponse(BaseModel):
    message: str
