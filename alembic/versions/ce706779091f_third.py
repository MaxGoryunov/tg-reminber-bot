"""third

Revision ID: ce706779091f
Revises: 1a09355d9206
Create Date: 2024-06-07 12:08:39.589089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce706779091f'
down_revision: Union[str, None] = '1a09355d9206'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
