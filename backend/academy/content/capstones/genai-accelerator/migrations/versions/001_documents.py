from alembic import op
revision='001'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''CREATE TABLE documents (
        id TEXT PRIMARY KEY,org TEXT NOT NULL,digest TEXT NOT NULL,text TEXT NOT NULL,
        state TEXT NOT NULL CHECK(state IN ('accepted','ready','failed')),UNIQUE(org,digest))''')
    op.execute('''CREATE TABLE chunks (
        document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        position INTEGER NOT NULL CHECK(position>=0),text TEXT NOT NULL,PRIMARY KEY(document_id,position))''')
def downgrade():
    raise RuntimeError('Destructive rollback disabled; use a fresh disposable database for migration exercises.')
