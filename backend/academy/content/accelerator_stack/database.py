import os
import psycopg
from psycopg.rows import dict_row

def connect():
    return psycopg.connect(os.environ['DATABASE_URL'],connect_timeout=3,row_factory=dict_row)
