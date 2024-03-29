"""Added item_critical_questions table and relations

Revision ID: f090daf85005
Revises: 3e9cccff4d86
Create Date: 2022-01-03 16:48:48.719695

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from core_layer.alembic.versions.f090daf85005.calculate_warning_tags import calculate_warning_tags

# revision identifiers, used by Alembic.
revision = 'f090daf85005'
down_revision = '3e9cccff4d86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item_critical_questions',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('item_id', sa.String(length=36), nullable=False),
                    sa.Column('review_question_id', sa.String(
                        length=36), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['item_id'], ['items.id'], onupdate='CASCADE', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['review_question_id'], [
                        'review_questions.id'], onupdate='CASCADE', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('items', sa.Column(
        'warning_tags_calculated', sa.Boolean(), nullable=True))
    calculate_warning_tags()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'warning_tags_calculated')
    op.drop_table('item_critical_questions')
    # ### end Alembic commands ###
