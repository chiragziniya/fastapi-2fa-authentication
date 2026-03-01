"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("reset_token", sa.String, nullable=True),
        sa.Column("reset_token_expires", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "otp_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("issuer", sa.String, nullable=False, server_default=""),
        sa.Column("account_name", sa.String, nullable=False, server_default=""),
        sa.Column("encrypted_secret", sa.Text, nullable=False),
        sa.Column("algorithm", sa.String, nullable=False, server_default="SHA1"),
        sa.Column("digits", sa.Integer, nullable=False, server_default="6"),
        sa.Column("period", sa.Integer, nullable=False, server_default="30"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("otp_accounts")
    op.drop_table("users")
