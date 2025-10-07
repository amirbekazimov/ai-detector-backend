"""Add AI bot IP ranges tables

Revision ID: fbedc40a981e
Revises: 67f1fb4941b0
Create Date: 2025-10-07 02:01:25.080286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbedc40a981e'
down_revision: Union[str, Sequence[str], None] = '67f1fb4941b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ai_bot_ip_ranges table
    op.create_table('ai_bot_ip_ranges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_name', sa.String(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('ip_range_start', sa.String(), nullable=True),
        sa.Column('ip_range_end', sa.String(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_bot_ip_ranges_id'), 'ai_bot_ip_ranges', ['id'], unique=False)
    op.create_index(op.f('ix_ai_bot_ip_ranges_bot_name'), 'ai_bot_ip_ranges', ['bot_name'], unique=False)
    op.create_index(op.f('ix_ai_bot_ip_ranges_source_type'), 'ai_bot_ip_ranges', ['source_type'], unique=False)
    op.create_index(op.f('ix_ai_bot_ip_ranges_ip_address'), 'ai_bot_ip_ranges', ['ip_address'], unique=False)
    
    # Create ip_range_update_log table
    op.create_table('ip_range_update_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_name', sa.String(), nullable=False),
        sa.Column('update_type', sa.String(), nullable=False),
        sa.Column('changes_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ip_range_update_log_id'), 'ip_range_update_log', ['id'], unique=False)
    op.create_index(op.f('ix_ip_range_update_log_bot_name'), 'ip_range_update_log', ['bot_name'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_index(op.f('ix_ip_range_update_log_bot_name'), table_name='ip_range_update_log')
    op.drop_index(op.f('ix_ip_range_update_log_id'), table_name='ip_range_update_log')
    op.drop_table('ip_range_update_log')
    
    op.drop_index(op.f('ix_ai_bot_ip_ranges_ip_address'), table_name='ai_bot_ip_ranges')
    op.drop_index(op.f('ix_ai_bot_ip_ranges_source_type'), table_name='ai_bot_ip_ranges')
    op.drop_index(op.f('ix_ai_bot_ip_ranges_bot_name'), table_name='ai_bot_ip_ranges')
    op.drop_index(op.f('ix_ai_bot_ip_ranges_id'), table_name='ai_bot_ip_ranges')
    op.drop_table('ai_bot_ip_ranges')
