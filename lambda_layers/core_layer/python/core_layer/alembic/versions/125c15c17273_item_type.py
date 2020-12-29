"""item_type

Revision ID: 125c15c17273
Revises: 7e1207d1a7e1
Create Date: 2020-12-29 21:09:34.691563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '125c15c17273'
down_revision = '7e1207d1a7e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item_types',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('items', sa.Column('item_type_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(None, 'items', 'item_types', ['item_type_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.add_column('review_questions', sa.Column('item_type_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(None, 'review_questions', 'item_types', ['item_type_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'review_questions', type_='foreignkey')
    op.drop_column('review_questions', 'item_type_id')
    op.drop_constraint(None, 'items', type_='foreignkey')
    op.drop_column('items', 'item_type_id')
    op.drop_table('item_types')
    # ### end Alembic commands ###
