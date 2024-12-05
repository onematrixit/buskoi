"""Add created_at column

Revision ID: ea91897821fb
Revises: 5b8b76a765e3
Create Date: 2024-12-01 00:26:43.460989

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ea91897821fb'
down_revision = '5b8b76a765e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               nullable=True,
               existing_server_default=sa.text('current_timestamp()'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('current_timestamp()'))
        batch_op.drop_column('last_login')

    # ### end Alembic commands ###
