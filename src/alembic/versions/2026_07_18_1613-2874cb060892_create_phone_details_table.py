"""create phone details table

Revision ID: 2874cb060892
Revises:
Create Date: 2026-07-18 16:13:23.159133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2874cb060892"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "BLOCKED", "DELETED", name="userstatus"),
            nullable=False,
        ),
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
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
        sa.ForeignKeyConstraint(["user_uuid"], ["users.uuid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("phone_number"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("phones")
    op.drop_table("users")
