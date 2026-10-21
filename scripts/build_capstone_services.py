"""Materialize three independent DRF/PG student projects from teaching templates."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];templates=ROOT/'scripts/capstones';base=ROOT/'backend/academy/content/capstones'
for slug,kind,port in [('ai-agent-bootcamp','boot',8211),('ai-workshops','workshop',8212),('ai-engineering-12-week','engineering',8214)]:
 folder=base/slug
 for source,target in [('service.py.txt','app.py'),(kind+'_core.py.txt','core.py'),('index.html.txt','index.html'),('check.py.txt','check.py')]:
  text=(templates/source).read_text()
  if slug=='ai-workshops' and target=='index.html':text=text.replace('What is the refund policy?','Supplier: Studio\nQuantity: 2\nUnit price: 10.00\nCurrency: USD')
  if slug=='ai-engineering-12-week' and target=='index.html':text=text.replace('<form id="form">','<form id="ingest"><label for="document">Synthetic source document</label><textarea id="document">Refund policy is 14 days for unopened items.</textarea><button>Ingest source</button></form><form id="form">').replace("document.querySelector('#form').onsubmit", "document.querySelector('#ingest').onsubmit=async e=>{e.preventDefault();try{const value=await request('/api/documents/',{source:'browser-fixture',text:document.querySelector('#document').value});status.textContent='Source ready: '+value.id}catch(e){status.textContent=e.message}};\ndocument.querySelector('#form').onsubmit")
  (folder/target).write_text(text)
 (folder/'requirements.txt').write_text('Django==5.2.7\ndjangorestframework==3.16.1\npsycopg[binary]==3.2.10\ngunicorn==23.0.0\n')
 (folder/'Dockerfile').write_text('FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt && useradd --create-home learner\nCOPY . .\nUSER learner\nEXPOSE 8000\nCMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "20"]\n')
 (folder/'.dockerignore').write_text('__pycache__\n.venv\n*.json\n.env\n')
 (folder/'compose.yaml').write_text(f'''name: capstone-{kind}
x-runtime: &runtime
  build: .
  environment:
    DJANGO_SECRET_KEY: synthetic-local-capstone-key-only
    POSTGRES_PASSWORD: synthetic-local-password-only
    REQUESTS_PER_MINUTE: '120'
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: capstone
      POSTGRES_USER: learner
      POSTGRES_PASSWORD: synthetic-local-password-only
    volumes: [data:/var/lib/postgresql/data]
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U learner -d capstone']
      interval: 2s
      timeout: 3s
      retries: 30
  schema:
    <<: *runtime
    command: ['python', 'app.py']
    depends_on:
      db: {{condition: service_healthy}}
  api:
    <<: *runtime
    ports: ['127.0.0.1:{port}:8000']
    depends_on:
      schema: {{condition: service_completed_successfully}}
    healthcheck:
      test: ['CMD', 'python', '-c', "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health/')"]
      interval: 2s
      timeout: 3s
      retries: 30
volumes:
  data:
''')
# Django intentionally leaves raw JSON decoding to JSONField; raw cursors need
# to handle the driver's JSON text explicitly rather than assuming a dict.
p=templates/'service.py.txt';s=p.read_text().replace("return row[0],row[1]","return row[0],json.loads(row[1]) if isinstance(row[1],str) else row[1]").replace("documents=[r[0] for r in c.fetchall()]","documents=[json.loads(r[0]) if isinstance(r[0],str) else r[0] for r in c.fetchall()]");p.write_text(s)
for slug in ['ai-agent-bootcamp','ai-workshops','ai-engineering-12-week']:(base/slug/'app.py').write_text(s)
