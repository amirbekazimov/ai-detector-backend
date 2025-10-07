"""Add AI bot detection columns to tracking_events

Revision ID: 67f1fb4941b0
Revises: 4cc9acc6d5b3
Create Date: 2025-10-07 02:00:05.600744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67f1fb4941b0'
down_revision: Union[str, Sequence[str], None] = '4cc9acc6d5b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add AI bot detection columns to tracking_events table
    op.add_column('tracking_events', sa.Column('detection_method', sa.String(50), nullable=True))
    op.add_column('tracking_events', sa.Column('bot_name', sa.String(100), nullable=True))
    op.add_column('tracking_events', sa.Column('is_ai_bot', sa.String(100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove AI bot detection columns from tracking_events table
    op.drop_column('tracking_events', 'is_ai_bot')
    op.drop_column('tracking_events', 'bot_name')
    op.drop_column('tracking_events', 'detection_method')
