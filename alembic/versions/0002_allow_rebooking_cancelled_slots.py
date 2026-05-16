"""Allow slots to be booked again after cancellation."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_rebook_cancelled_slots"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_names = {item["name"] for item in inspector.get_unique_constraints("appointments")}
    if "appointments_slot_id_key" in unique_names:
        op.drop_constraint("appointments_slot_id_key", "appointments", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("appointments_slot_id_key", "appointments", ["slot_id"])
