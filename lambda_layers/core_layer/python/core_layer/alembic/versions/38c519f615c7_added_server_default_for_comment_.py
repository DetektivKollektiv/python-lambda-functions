"""Added server default for comment timestamp

Revision ID: 38c519f615c7
Revises: f5f030e05a2e
Create Date: 2021-10-05 17:08:34.242909

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '38c519f615c7'
down_revision = 'f5f030e05a2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comments', 'timestamp',
                    existing_type=mysql.DATETIME(),
                    server_default=sa.text('now()'),
                    nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comments', 'timestamp',
                    existing_type=mysql.DATETIME(),
                    server_default=None,
                    nullable=True)
    # ### end Alembic commands ###
