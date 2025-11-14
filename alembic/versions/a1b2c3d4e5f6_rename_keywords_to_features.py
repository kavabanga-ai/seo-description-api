"""rename keywords to features

Revision ID: a1b2c3d4e5f6
Revises: 2537442b0233
Create Date: 2025-11-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "2537442b0233"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename the keywords column to features
    op.alter_column("products", "keywords", new_column_name="features")


def downgrade() -> None:
    """Downgrade schema."""
    # Rename the features column back to keywords
    op.alter_column("products", "features", new_column_name="keywords")
