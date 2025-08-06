"""
Revision ID: %(rev)s
Revises: %(down_revision)s
Create Date: %(create_date)s

"""
from alembic import op
import sqlalchemy as sa
%(imports)s

# revision identifiers, used by Alembic.
revision = %(repr(up_revision))s
down_revision = %(repr(down_revision))s
branch_labels = %(repr(branch_labels))s
depends_on = %(repr(depends_on))s


def upgrade() -> None:
    %(upgrades)s


def downgrade() -> None:
    %(downgrades)s
