from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f3c652e38f17'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('repositories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('github_id', sa.String(length=20), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('owner', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('primary_language', sa.String(length=50), nullable=True),
    sa.Column('stars', sa.Integer(), nullable=False),
    sa.Column('forks', sa.Integer(), nullable=False),
    sa.Column('open_issues_count', sa.Integer(), nullable=False),
    sa.Column('watchers', sa.Integer(), nullable=False),
    sa.Column('license', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('last_pushed_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('last_commit_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('activity_score', sa.Float(), nullable=False),
    sa.Column('beginner_friendliness_score', sa.Float(), nullable=False),
    sa.Column('combined_score', sa.Float(), nullable=False),
    sa.Column('good_first_issue_count', sa.Integer(), nullable=False),
    sa.Column('contributor_count', sa.Integer(), nullable=False),
    sa.Column('avg_pr_merge_hours', sa.Float(), nullable=True),
    sa.Column('avg_issue_response_hours', sa.Float(), nullable=True),
    sa.Column('open_pr_count', sa.Integer(), nullable=False),
    sa.Column('closed_pr_count', sa.Integer(), nullable=False),
    sa.Column('merged_pr_count', sa.Integer(), nullable=False),
    sa.Column('has_contributing_guide', sa.Boolean(), nullable=False),
    sa.Column('has_code_of_conduct', sa.Boolean(), nullable=False),
    sa.Column('has_readme', sa.Boolean(), nullable=False),
    sa.Column('has_issue_templates', sa.Boolean(), nullable=False),
    sa.Column('has_pr_templates', sa.Boolean(), nullable=False),
    sa.Column('topics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('raw_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('synced_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('created_in_db', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_in_db', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('full_name'),
    sa.UniqueConstraint('github_id')
    )
    op.create_index('idx_repos_activity_score', 'repositories', ['activity_score'], unique=False, postgresql_using='btree')
    op.create_index('idx_repos_bf_score', 'repositories', ['beginner_friendliness_score'], unique=False, postgresql_using='btree')
    op.create_index('idx_repos_combined_score', 'repositories', ['combined_score'], unique=False, postgresql_using='btree')
    op.create_index('idx_repos_language', 'repositories', ['primary_language'], unique=False)
    op.create_index('idx_repos_stars', 'repositories', ['stars'], unique=False)
    op.create_index('idx_repos_synced', 'repositories', ['synced_at'], unique=False)
    op.create_table('issues',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('github_id', sa.String(length=20), nullable=False),
    sa.Column('repo_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('body_preview', sa.Text(), nullable=True),
    sa.Column('html_url', sa.String(length=500), nullable=True),
    sa.Column('state', sa.String(length=10), nullable=False),
    sa.Column('labels', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('comment_count', sa.Integer(), nullable=False),
    sa.Column('difficulty_estimate', sa.String(length=20), nullable=True),
    sa.Column('assignee_login', sa.String(length=100), nullable=True),
    sa.Column('is_assigned', sa.Boolean(), nullable=False),
    sa.Column('is_good_first_issue', sa.Boolean(), nullable=False),
    sa.Column('is_help_wanted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('closed_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('synced_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('github_id')
    )
    op.create_index('idx_issues_difficulty', 'issues', ['difficulty_estimate'], unique=False)
    op.create_index('idx_issues_gfi', 'issues', ['is_good_first_issue'], unique=False, postgresql_where='is_good_first_issue = true')
    op.create_index('idx_issues_open', 'issues', ['state'], unique=False, postgresql_where="state = 'open'")
    op.create_index('idx_issues_repo', 'issues', ['repo_id'], unique=False)
    op.create_table('repo_languages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('repo_id', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(length=50), nullable=False),
    sa.Column('bytes_count', sa.Integer(), nullable=False),
    sa.Column('percentage', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('repo_id', 'language', name='uq_repo_language')
    )
    op.create_table('repo_metrics_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('repo_id', sa.Integer(), nullable=False),
    sa.Column('activity_score', sa.Float(), nullable=True),
    sa.Column('beginner_friendliness_score', sa.Float(), nullable=True),
    sa.Column('stars', sa.Integer(), nullable=True),
    sa.Column('forks', sa.Integer(), nullable=True),
    sa.Column('good_first_issue_count', sa.Integer(), nullable=True),
    sa.Column('avg_pr_merge_hours', sa.Float(), nullable=True),
    sa.Column('recorded_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('repo_id', 'recorded_date', name='uq_repo_metrics_date')
    )


def downgrade() -> None:
    op.drop_table('repo_metrics_history')
    op.drop_table('repo_languages')
    op.drop_index('idx_issues_repo', table_name='issues')
    op.drop_index('idx_issues_open', table_name='issues', postgresql_where="state = 'open'")
    op.drop_index('idx_issues_gfi', table_name='issues', postgresql_where='is_good_first_issue = true')
    op.drop_index('idx_issues_difficulty', table_name='issues')
    op.drop_table('issues')
    op.drop_index('idx_repos_synced', table_name='repositories')
    op.drop_index('idx_repos_stars', table_name='repositories')
    op.drop_index('idx_repos_language', table_name='repositories')
    op.drop_index('idx_repos_combined_score', table_name='repositories', postgresql_using='btree')
    op.drop_index('idx_repos_bf_score', table_name='repositories', postgresql_using='btree')
    op.drop_index('idx_repos_activity_score', table_name='repositories', postgresql_using='btree')
    op.drop_table('repositories')
