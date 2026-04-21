"""Initial schema for SmileSchedule persistence."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


appointment_status = sa.Enum("scheduled", "cancelled", name="appointmentstatus")


def upgrade() -> None:
    appointment_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_patients_email", "patients", ["email"], unique=True)
    op.create_index("ix_patients_id", "patients", ["id"], unique=False)

    op.create_table(
        "availability_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dentist_name", sa.String(length=120), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_reserved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_availability_slots_id", "availability_slots", ["id"], unique=False)
    op.create_index("ix_availability_slots_start_time", "availability_slots", ["start_time"], unique=False)

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("slot_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("status", appointment_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["slot_id"], ["availability_slots.id"]),
        sa.UniqueConstraint("slot_id"),
    )
    op.create_index("ix_appointments_id", "appointments", ["id"], unique=False)
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"], unique=False)
    op.create_index("ix_appointments_slot_id", "appointments", ["slot_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_appointments_slot_id", table_name="appointments")
    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_index("ix_appointments_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_availability_slots_start_time", table_name="availability_slots")
    op.drop_index("ix_availability_slots_id", table_name="availability_slots")
    op.drop_table("availability_slots")

    op.drop_index("ix_patients_id", table_name="patients")
    op.drop_index("ix_patients_email", table_name="patients")
    op.drop_table("patients")

    appointment_status.drop(op.get_bind(), checkfirst=True)

