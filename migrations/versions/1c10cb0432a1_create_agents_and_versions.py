"""create agents and versions

Revision ID: 1c10cb0432a1
Revises: 
Create Date: 2026-11-13 15:03:36.153966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1c10cb0432a1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. agents first, WITHOUT the foreign key to agent_versions (that table doesn't exist yet)
    op.create_table('agents',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('current_version_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=True)

    # 2. agent_versions, which can reference agents because agents now exists
    op.create_table('agent_versions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('agent_id', sa.Uuid(), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('agent_id', 'version_number', name='uq_agent_version_number')
    )
    op.create_index(op.f('ix_agent_versions_agent_id'), 'agent_versions', ['agent_id'], unique=False)

    # 3. Now that both tables exist, add the circular foreign key
    op.create_foreign_key(
        'fk_agents_current_version',   # constraint name
        'agents', 'agent_versions',    # from table, to table
        ['current_version_id'], ['id'] # from column, to column
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse order: drop the circular foreign key first, or neither table can be dropped
    op.drop_constraint('fk_agents_current_version', 'agents', type_='foreignkey')
    op.drop_index(op.f('ix_agent_versions_agent_id'), table_name='agent_versions')
    op.drop_table('agent_versions')
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_table('agents')
    # ### end Alembic commands ###
