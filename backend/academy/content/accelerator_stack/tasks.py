"""Read-only ingestion: row lock + one transaction make duplicate delivery harmless."""
import os
import psycopg
from celery import Celery
from database import connect
worker=Celery('policy_lab',broker=os.environ['BROKER_URL'])
worker.conf.update(task_serializer='json',accept_content=['json'],worker_prefetch_multiplier=1,
                   broker_connection_retry_on_startup=True,broker_transport_options={'visibility_timeout':60})

@worker.task(bind=True,acks_late=True,max_retries=2,soft_time_limit=10,time_limit=15)
def ingest(self,document_id):
    try:
        with connect() as db:
            db.execute("SET LOCAL statement_timeout = '5s'")
            row=db.execute('SELECT * FROM documents WHERE id=%s FOR UPDATE',[document_id]).fetchone()
            if row is None: return {'status':'missing'}
            if row['state']=='ready': return {'status':'already_ready'}
            if not row['text'].strip():
                db.execute("UPDATE documents SET state='failed' WHERE id=%s",[document_id])
                return {'status':'failed'}
            # This is a complete UTF-8 fixture ingestion, not a PDF parser or semantic embedding service.
            parts=[part.strip() for part in row['text'].split('.') if part.strip()]
            for index,text in enumerate(parts):
                db.execute('INSERT INTO chunks(document_id,position,text) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',
                           [document_id,index,text])
            db.execute("UPDATE documents SET state='ready' WHERE id=%s",[document_id])
        return {'status':'ready'}  # after COMMIT, not merely after sending a job
    except psycopg.OperationalError as error:
        raise self.retry(exc=RuntimeError('database temporarily unavailable'),countdown=1) from error
