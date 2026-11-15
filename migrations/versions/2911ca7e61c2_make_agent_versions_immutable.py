"""make agent_versions immutable

Revision ID: 2911ca7e61c2
Revises: 1c10cb0432a1
Create Date: 2026-11-14 21:21:54.899143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2911ca7e61c2'
down_revision: Union[str, Sequence[str], None] = '1c10cb0432a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_agent_version_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION USING MESSAGE =
                'agent_versions rows are immutable (id ' || OLD.id
                || '); publish a new version instead';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_agent_versions_immutable
        BEFORE UPDATE ON agent_versions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_agent_version_update();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_agent_versions_immutable ON agent_versions;")
    op.execute("DROP FUNCTION IF EXISTS prevent_agent_version_update();")
