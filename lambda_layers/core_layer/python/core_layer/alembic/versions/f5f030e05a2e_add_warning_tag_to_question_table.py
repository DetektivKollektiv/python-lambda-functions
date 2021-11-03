"""add warning tag to question table

Revision ID: f5f030e05a2e
Revises: efd97d68c529
Create Date: 2021-09-06 19:15:29.383121

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f5f030e05a2e'
down_revision = 'efd97d68c529'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('review_questions', sa.Column(
        'warning_tag', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('review_questions', 'warning_tag')
    # ### end Alembic commands ###
