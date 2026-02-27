from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '55a338e1c800'
down_revision: Union[str, None] = 'e0fc02378fbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_subscriptions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('language', sa.String(length=50), nullable=True),
    sa.Column('labels', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('notify_on_new_match', sa.Boolean(), nullable=False),
    sa.Column('notify_on_inactive', sa.Boolean(), nullable=False),
    sa.Column('only_actively_merging', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_subscriptions_email'), 'user_subscriptions', ['email'], unique=False)
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('subscription_id', sa.Integer(), nullable=False),
    sa.Column('repo_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('repo_full_name', sa.String(length=255), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('repositories', sa.Column('last_merged_pr_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('repositories', sa.Column('pr_merge_rate', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('repositories', sa.Column('recent_commit_count_30d', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('repositories', sa.Column('recent_merged_pr_count_30d', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('repositories', sa.Column('is_actively_merging', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('repositories', 'is_actively_merging')
    op.drop_column('repositories', 'recent_merged_pr_count_30d')
    op.drop_column('repositories', 'recent_commit_count_30d')
    op.drop_column('repositories', 'pr_merge_rate')
    op.drop_column('repositories', 'last_merged_pr_at')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_user_subscriptions_email'), table_name='user_subscriptions')
    op.drop_table('user_subscriptions')
