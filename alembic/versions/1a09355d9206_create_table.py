"""create table

Revision ID: 1a09355d9206
Revises: 51aa99c8741f
Create Date: 2024-06-07 12:01:27.134673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a09355d9206'
down_revision: Union[str, None] = '51aa99c8741f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
