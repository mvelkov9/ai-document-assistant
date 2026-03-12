"""add tags column to documents

Revision ID: 003_add_document_tags
Revises: 002_add_last_login_at
Create Date: 2026-03-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

from alembic import op

revision: str = "003_add_document_tags"
down_revision: Union[str, None] = "002_add_last_login_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("tags", JSON, nullable=True, server_default="[]"))


def downgrade() -> None:
    op.drop_column("documents", "tags")
