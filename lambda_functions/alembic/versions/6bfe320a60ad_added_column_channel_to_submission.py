"""Added column channel to Submission

Revision ID: 6bfe320a60ad
Revises: 1c7d0ba8060d
Create Date: 2020-10-25 18:59:46.342588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bfe320a60ad'
down_revision = '1c7d0ba8060d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('submissions', sa.Column('channel', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('submissions', 'channel')
    # ### end Alembic commands ###
