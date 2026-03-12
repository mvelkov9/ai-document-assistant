"""add last_login_at to users

Revision ID: 002_add_last_login_at
Revises: 001_initial
Create Date: 2026-03-12
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "002_add_last_login_at"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_login_at")
