import os
from alembic import context
from sqlalchemy import create_engine
# URL is read at runtime and never printed. The driver name differs from the psycopg DSN.
url=os.environ['DATABASE_URL'].replace('postgresql://','postgresql+psycopg://',1)
engine=create_engine(url)
with engine.connect() as connection:
    context.configure(connection=connection,target_metadata=None)
    with context.begin_transaction(): context.run_migrations()
engine.dispose()
