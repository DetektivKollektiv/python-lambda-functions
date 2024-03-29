"""add table 'mails' to store user emails and mail subscription state

Revision ID: e662248edcc3
Revises: 3e9cccff4d86
Create Date: 2021-12-06 21:29:34.869142

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from core_layer.alembic.versions.e662248edcc3.move_mail_addresses_from_submission_to_mail_model import move_mail_addresses_from_submission_to_mail_model

# revision identifiers, used by Alembic.
revision = 'e662248edcc3'
down_revision = 'f090daf85005'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        op.drop_table('mails')
    except:
        pass
    op.create_table('mails',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=100), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )

    op.add_column('submissions', sa.Column('mail_id', sa.String(length=36), nullable=True))
    op.drop_constraint('mails_ibfk_1', 'mails', type_='foreignkey')
    op.drop_column('mails', 'user_id')
    op.add_column('users', sa.Column('mail_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(None, 'users', 'mails', ['mail_id'], ['id'])   

    move_mail_addresses_from_submission_to_mail_model()

    op.drop_column('submissions', 'status')
    op.drop_column('submissions', 'mail')
    op.create_foreign_key(None, 'submissions', 'mails', ['mail_id'], ['id'])

    ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'sign_up_timestamp',
               existing_type=mysql.DATETIME(),
               server_default=sa.text('current_timestamp()'),
               existing_nullable=True)
    op.alter_column('items', 'open_timestamp',
               existing_type=mysql.DATETIME(),
               server_default=sa.text('current_timestamp()'),
               existing_nullable=False)
    op.alter_column('comments', 'timestamp',
               existing_type=mysql.DATETIME(),
               server_default=sa.text('current_timestamp()'),
               existing_nullable=False)
    op.drop_table('mails')
    # ### end Alembic commands ###