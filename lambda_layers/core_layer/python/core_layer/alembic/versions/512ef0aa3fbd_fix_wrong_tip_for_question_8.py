"""Fix wrong tip for question 8

Revision ID: 512ef0aa3fbd
Revises: 3dfcec659fd7
Create Date: 2020-12-22 09:28:20.529432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '512ef0aa3fbd'
down_revision = '3dfcec659fd7'
branch_labels = None
depends_on = None


def upgrade():

    op.execute('UPDATE review_questions SET info = "Tipp: \
        Achte auf die Besitzer * innen und Geldgeber * innen der Webseite des Medium, \
        auf der der betreffenden Artikel erschienen ist.Gibt es einen Verdacht auf staatliche Einflüsse \
        oder starken politischen Bias? RT(früher Russia Today) ist bspw.nachweislich vom \
        russischen Staat finanziert und verbreitet offiziell die Sichtweise der russischen Regierung auf und über das Weltgeschehen." WHERE id = "8"')
    pass


def downgrade():
    pass
