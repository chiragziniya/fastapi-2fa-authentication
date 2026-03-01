from pydantic import BaseModel
from datetime import datetime


class OtpAccountCreate(BaseModel):
    issuer: str = ""
    account_name: str = ""
    encrypted_secret: str
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30


class OtpAccountUpdate(BaseModel):
    issuer: str | None = None
    account_name: str | None = None


class OtpAccountResponse(BaseModel):
    id: str
    user_id: str
    issuer: str
    account_name: str
    encrypted_secret: str
    algorithm: str
    digits: int
    period: int
    created_at: datetime

    model_config = {"from_attributes": True}
