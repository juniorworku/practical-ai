"""Self-contained Docker/DRF/PostgreSQL boundary lab, deliberately small UI."""
FILES = {
'backend/requirements.txt': 'Django==5.2.7\ndjangorestframework==3.16.1\npsycopg[binary]==3.2.10\ngunicorn==23.0.0\n',
'backend/Dockerfile': '''FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home learner
COPY app.py .
USER learner
EXPOSE 8000
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000", "--workers", "1"]
''',
'backend/app.py': '''import os
from django.conf import settings
settings.configure(
    SECRET_KEY=os.environ["DJANGO_SECRET_KEY"], DEBUG=False,
    ALLOWED_HOSTS=["localhost","127.0.0.1","backend"], ROOT_URLCONF=__name__,
    DATABASES={"default":{"ENGINE":"django.db.backends.postgresql", "NAME":os.environ["POSTGRES_DB"],
      "USER":os.environ["POSTGRES_USER"], "PASSWORD":os.environ["POSTGRES_PASSWORD"], "HOST":"db", "PORT":"5432"}},
    INSTALLED_APPS=["rest_framework"],
    REST_FRAMEWORK={"UNAUTHENTICATED_USER":None},
)
import django
django.setup()
from django.db import connection
from django.urls import path
from django.core.wsgi import get_wsgi_application
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return Response({"database":"postgresql","ready":True})
    except Exception:
        return Response({"ready":False,"error":"database_unavailable"},status=503)

@api_view(["GET","POST"])
def drafts(request):
    # Dedicated synthetic local lab only; no authentication or production migration system.
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS lab_drafts(id SERIAL PRIMARY KEY, body TEXT NOT NULL)")
        if request.method=="POST":
            body=request.data.get("body")
            if type(body) is not str or not body.strip() or len(body)>500:
                return Response({"error":"body_required_max_500"},status=400)
            cursor.execute("INSERT INTO lab_drafts(body) VALUES(%s) RETURNING id",[body.strip()])
            return Response({"id":cursor.fetchone()[0],"body":body.strip()},status=201)
        cursor.execute("SELECT id,body FROM lab_drafts ORDER BY id")
        return Response([{"id":row[0],"body":row[1]} for row in cursor.fetchall()])

urlpatterns=[path("api/health/",health),path("api/drafts/",drafts)]
application=get_wsgi_application()
''',
'frontend/Dockerfile': '''FROM nginx:1.28-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
''',
'frontend/nginx.conf': '''server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
    location / { try_files $uri /index.html; }
}
''',
'frontend/index.html': '''<!doctype html><html lang="en"><meta charset="utf-8"><title>Persistence boundary lab</title>
<h1>Synthetic draft store</h1><p>Local unauthenticated lab. Use synthetic text only.</p>
<form id="form"><label for="body">Draft text</label><input id="body" required maxlength="500">
<button>Save draft</button></form><p id="status" role="status"></p><pre id="records"></pre>
<script>
async function load() {
 const response=await fetch('/api/drafts/');
 if(!response.ok) throw Error('Read failed');
 document.querySelector('#records').textContent=JSON.stringify(await response.json(),null,2);
}
document.querySelector('#form').addEventListener('submit',async event=>{
 event.preventDefault();
 const input=document.querySelector('#body'), status=document.querySelector('#status');
 status.textContent='Saving';
 try {
  const response=await fetch('/api/drafts/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({body:input.value})});
  if(!response.ok) throw Error('Save failed; input retained');
  const saved=await response.json(); status.textContent='Saved record '+saved.id;
  await load();
 } catch(error) {status.textContent=error.message;}
});
load().catch(error=>document.querySelector('#status').textContent=error.message);
</script></html>
''',
'compose.yaml': '''services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: lab
      POSTGRES_USER: lab
      POSTGRES_PASSWORD: ${LAB_DB_PASSWORD:?Set LAB_DB_PASSWORD}
    volumes:
      - lab-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lab -d lab"]
      interval: 2s
      timeout: 3s
      retries: 30
  backend:
    build: ./backend
    environment:
      POSTGRES_DB: lab
      POSTGRES_USER: lab
      POSTGRES_PASSWORD: ${LAB_DB_PASSWORD:?Set LAB_DB_PASSWORD}
      DJANGO_SECRET_KEY: ${LAB_DJANGO_SECRET:?Set LAB_DJANGO_SECRET}
    depends_on:
      db:
        condition: service_healthy
  frontend:
    build: ./frontend
    ports:
      - "127.0.0.1:${LAB_PORT:-8091}:80"
    depends_on:
      - backend
volumes:
  lab-data:
'''
}

RESTORE_SCRIPT = '''set -eu
# Run from the container-lab directory created in session 19.
# Start that isolated stack and save at least one synthetic draft first.
export LAB_DB_PASSWORD=synthetic-local-lab-password
export LAB_DJANGO_SECRET=synthetic-local-lab-secret-for-testing-only
export LAB_PORT=8091
test ! -e lab-backup-review.dump
docker compose -p academy-student-lab exec -T db pg_dump -U lab -d lab --format=custom > lab-backup-review.dump
# createdb stops if this target already exists; never replace the live database.
docker compose -p academy-student-lab exec -T db createdb -U lab lab_restore_review
docker compose -p academy-student-lab exec -T db pg_restore -U lab --no-owner -d lab_restore_review < lab-backup-review.dump
source_rows="$(docker compose -p academy-student-lab exec -T db psql -U lab -d lab -At -v ON_ERROR_STOP=1 -c 'SELECT id,body FROM lab_drafts ORDER BY id')"
restored_rows="$(docker compose -p academy-student-lab exec -T db psql -U lab -d lab_restore_review -At -v ON_ERROR_STOP=1 -c 'SELECT id,body FROM lab_drafts ORDER BY id')"
test -n "$source_rows"
test "$source_rows" = "$restored_rows"
printf '%s\\n' 'PASS: isolated PostgreSQL restore matches source IDs and synthetic content'
'''
