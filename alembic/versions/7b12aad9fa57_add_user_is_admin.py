"""add user_is_admin

Revision ID: 7b12aad9fa57
Revises: 0409bd4cb700
Create Date: 2023-09-24 08:49:50.079414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7b12aad9fa57'
down_revision: Union[str, None] = '0409bd4cb700'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_is_admin', sa.Boolean(), nullable=False))
    op.alter_column('users', 'models',
               existing_type=postgresql.ENUM('falcon', 'dolly', 'openai', name='model'),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'models',
               existing_type=postgresql.ENUM('falcon', 'dolly', 'openai', name='model'),
               nullable=False)
    op.drop_column('users', 'user_is_admin')
    # ### end Alembic commands ###
