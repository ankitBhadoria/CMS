"""Creating user campaign sequence.

Revision ID: 2c3ddf05ac68
Revises: 
Create Date: 2025-02-06 16:56:30.311306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c3ddf05ac68'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'usercampaignsequence',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('status', sa.Enum('upcoming', 'running', 'expired', name='status'), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('schedule_status', sa.Enum('scheduled', 'sent', name='schedule_status'), nullable=False, server_default='scheduled'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('userprofile_id', sa.Integer, sa.ForeignKey('userprofile.id'), nullable=False)
    )

def downgrade():
    op.drop_table('usercampaignsequence')
