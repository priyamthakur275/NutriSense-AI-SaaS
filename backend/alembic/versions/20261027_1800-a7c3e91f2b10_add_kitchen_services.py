"""add kitchen services (waste tracking, forecasting)

Revision ID: a7c3e91f2b10
Revises: bda055faeb59
Create Date: 2026-10-27 18:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7c3e91f2b10"
down_revision: Union[str, None] = "bda055faeb59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "kitchen_services",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column(
            "meal_type",
            sa.Enum("BREAKFAST", "LUNCH", "DINNER", name="kitchen_meal_type", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("plates_served", sa.Integer(), nullable=False),
        sa.Column("is_sample", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.String(length=300), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kitchen_services_owner_id", "kitchen_services", ["owner_id"])
    op.create_index("ix_kitchen_services_owner_date", "kitchen_services", ["owner_id", "service_date"])

    op.create_table(
        "kitchen_service_dishes",
        sa.Column("service_id", sa.Uuid(), nullable=False),
        sa.Column("dish_key", sa.String(length=50), nullable=False),
        sa.Column("prepared_kg", sa.Float(), nullable=False),
        sa.Column("pot_leftover_kg", sa.Float(), nullable=False, server_default="0"),
        sa.Column("plate_waste_kg", sa.Float(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["kitchen_services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kitchen_service_dishes_service_id", "kitchen_service_dishes", ["service_id"])


def downgrade() -> None:
    op.drop_index("ix_kitchen_service_dishes_service_id", table_name="kitchen_service_dishes")
    op.drop_table("kitchen_service_dishes")
    op.drop_index("ix_kitchen_services_owner_date", table_name="kitchen_services")
    op.drop_index("ix_kitchen_services_owner_id", table_name="kitchen_services")
    op.drop_table("kitchen_services")
