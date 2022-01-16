"""add table 'mails' to store user emails and mail subscription state

Revision ID: e662248edcc3
Revises: 3e9cccff4d86
Create Date: 2021-12-06 21:29:34.869142

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e662248edcc3'
down_revision = '3e9cccff4d86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mails',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=100), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('comments', 'timestamp',
               existing_type=mysql.DATETIME(),
               server_default=sa.text('now()'),
               existing_nullable=False)
    op.alter_column('items', 'open_timestamp',
               existing_type=mysql.DATETIME(),
               server_default=sa.text('now()'),
               existing_nullable=False)
    op.alter_column('users', 'sign_up_timestamp',
               existing_type=mysql.DATETIME(),
               server_default=sa.text('now()'),
               existing_nullable=True)

    # Move mail subscription status from 'submissions' to new created 'mails' table and drop unused columns
    op.execute("""INSERT INTO mails(id, email, status)
                  SELECT UUID(), mail, status 
                  FROM submissions
                  WHERE mail IS NOT NULL;

                  ALTER TABLE submissions
                  DROP COLUMN mail,
                  DROP COLUMN status;"""
              )
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