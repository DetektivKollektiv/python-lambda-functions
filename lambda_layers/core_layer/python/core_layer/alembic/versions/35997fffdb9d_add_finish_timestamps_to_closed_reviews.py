"""Add finish timestamps to closed reviews

Revision ID: 35997fffdb9d
Revises: 7e1207d1a7e1
Create Date: 2021-01-14 15:56:05.466239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35997fffdb9d'
down_revision = '7e1207d1a7e1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE reviews SET finish_timestamp = NOW() WHERE status = 'closed'")
    pass


def downgrade():
    pass
