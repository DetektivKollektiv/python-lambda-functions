"""Status for submission added

Revision ID: 69c8e4d86653
Revises: 4e67ce1abb34
Create Date: 2021-01-29 15:37:42.173571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69c8e4d86653'
down_revision = '4e67ce1abb34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('submissions', sa.Column('status', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('submissions', 'status')
    # ### end Alembic commands ###
