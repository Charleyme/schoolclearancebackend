"""update officer assignement school constraint

Revision ID: ad318d57aed2
Revises: 7dc20ffca61f
Create Date: 2026-09-22 10:04:05.497610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad318d57aed2'
down_revision: Union[str, Sequence[str], None] = '7dc20ffca61f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_constraint(
        "unique_officer_assignment",
        "officer_assignments",
        type_="unique"
    )

    op.create_unique_constraint(
        "unique_officer_assignment",
        "officer_assignments",
        [
            "user_id",
            "clearance_unit_id",
            "school_id"
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "unique_officer_assignment",
        "officer_assignments",
        type_="unique"
    )

    op.create_unique_constraint(
        "unique_officer_assignment",
        "officer_assignments",
        [
            "user_id",
            "clearance_unit_id"
        ]
    )