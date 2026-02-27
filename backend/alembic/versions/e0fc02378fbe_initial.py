from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e0fc02378fbe'
down_revision: Union[str, None] = 'f3c652e38f17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
