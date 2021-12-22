"""relation between review and tags/comments added

Revision ID: 3e9cccff4d86
Revises: 5777ebc2e120
Create Date: 2021-11-02 18:11:12.646111

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3e9cccff4d86'
down_revision = '5777ebc2e120'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column(
        'review_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(None, 'comments', 'reviews', ['review_id'], ['id'])
    op.add_column('item_tags', sa.Column(
        'review_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(None, 'item_tags', 'reviews', ['review_id'], ['id'])
    op.drop_column('item_tags', 'count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item_tags', sa.Column('count', mysql.INTEGER(
        display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'item_tags', type_='foreignkey')
    op.drop_column('item_tags', 'review_id')
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_column('comments', 'review_id')
    # ### end Alembic commands ###