from alembic import op
revision='002'
down_revision='001'
branch_labels=None
depends_on=None

def upgrade():
    op.execute("ALTER TABLE documents ADD COLUMN parser_version TEXT NOT NULL DEFAULT 'sentence-v1'")
def downgrade():
    raise RuntimeError('Use an additive forward recovery; do not drop metadata on a live dataset.')
