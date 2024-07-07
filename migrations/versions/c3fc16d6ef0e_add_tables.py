"""add tables

Revision ID: c3fc16d6ef0e
Revises: f1185025615d
Create Date: 2024-07-07 22:29:53.615938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3fc16d6ef0e'
down_revision = 'f1185025615d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organisation',
    sa.Column('orgId', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('orgId'),
    sa.UniqueConstraint('orgId')
    )
    op.create_table('user',
    sa.Column('userId', sa.String(length=80), nullable=False),
    sa.Column('firstName', sa.String(length=80), nullable=False),
    sa.Column('lastName', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('userId'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('userId')
    )
    op.create_table('user_organisation',
    sa.Column('user_id', sa.String(length=80), nullable=False),
    sa.Column('organisation_id', sa.String(length=80), nullable=False),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisation.orgId'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.userId'], ),
    sa.PrimaryKeyConstraint('user_id', 'organisation_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_organisation')
    op.drop_table('user')
    op.drop_table('organisation')
    # ### end Alembic commands ###