"""Add rating and release-year database constraints.

Revision ID: b7c9d1e2f3a4
Revises: a08ab2f2c2a3
"""
from alembic import op

revision = "b7c9d1e2f3a4"
down_revision = "a08ab2f2c2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("movies", recreate="always") as batch_op:
        batch_op.create_check_constraint(
            "check_movie_rating_range", "rating >= 0 AND rating <= 10"
        )
        batch_op.create_check_constraint("check_movie_year_1888", "year >= 1888")


def downgrade() -> None:
    with op.batch_alter_table("movies", recreate="always") as batch_op:
        batch_op.drop_constraint("check_movie_year_1888", type_="check")
        batch_op.drop_constraint("check_movie_rating_range", type_="check")
