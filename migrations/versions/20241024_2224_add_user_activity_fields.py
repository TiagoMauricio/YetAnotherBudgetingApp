"""Add user activity fields

Revision ID: 20241024222400
Revises:
Create Date: 2024-10-24 22:24:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20241024222400"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if the user table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "user" not in tables:
        # If users table doesn't exist, it will be created by SQLModel
        return

    # Add columns if they don't exist
    columns = [col["name"] for col in inspector.get_columns("user")]

    with op.batch_alter_table("user") as batch_op:
        if "is_active" not in columns:
            batch_op.add_column(
                sa.Column(
                    "is_active",
                    sa.Boolean(),
                    server_default=sa.text("true"),
                    nullable=False,
                )
            )
        if "last_login" not in columns:
            batch_op.add_column(
                sa.Column("last_login", sa.DateTime(timezone=True), nullable=True)
            )
        if "last_activity" not in columns:
            batch_op.add_column(
                sa.Column("last_activity", sa.DateTime(timezone=True), nullable=True)
            )

        # Update the updated_at column to have onupdate behavior
        batch_op.alter_column(
            "updated_at",
            type_=sa.DateTime(timezone=True),
            existing_type=sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        )


def downgrade() -> None:
    # Only drop the columns if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("user")]

    with op.batch_alter_table("user") as batch_op:
        if "last_activity" in columns:
            batch_op.drop_column("last_activity")
        if "last_login" in columns:
            batch_op.drop_column("last_login")
        if "is_active" in columns:
            batch_op.drop_column("is_active")

        # Revert updated_at column changes
        batch_op.alter_column(
            "updated_at",
            type_=sa.DateTime(),
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=None,
        )
