"""create users table

Revision ID: 7a39e9910b11
Revises:
Create Date: 2026-08-26 15:45:04.354022

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a39e9910b11"
down_revision: Union[str, Sequence[str], None] = "0e3f256d364c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("users")
    op.create_table(
        "users",
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column(
            "phone_sync_status",
            sa.Enum(
                "PENDING",
                "DONE",
                "FAILED",
                "PROCESSING",
                name="phonesyncstatus",
            ),
            nullable=True,
        ),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "phones",
        sa.Column("user_uuid", sa.Uuid(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column(
            "phone_type",
            sa.Enum("MOBILE", "HOME", "WORK", name="phonetype"),
            nullable=False,
        ),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column(
            "operator_type",
            sa.Enum("MTS", "MEGAFON", "BEELINE", name="operatortype"),
            nullable=False,
        ),
        sa.Column(
            "region_type",
            sa.Enum(
                "MOSCOW_CITY",
                "SAINT_PETERSBURG",
                "MOSCOW_OBLAST",
                "KRASNODAR_KRAI",
                "REPUBLIC_OF_TATARSTAN",
                "OTHER",
                name="regiontype",
            ),
            nullable=False,
        ),
        sa.Column("is_spam", sa.Boolean(), nullable=False),
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_uuid"], ["users.uuid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("phone_number"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("phones")
    op.drop_table("users")
