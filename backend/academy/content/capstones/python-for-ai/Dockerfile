FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home learner
COPY . .
RUN mkdir /state && chown learner /state
USER learner
ENV BIND_HOST=0.0.0.0 STATE_PATH=/state/cache.sqlite3 PORT=8094
EXPOSE 8094
CMD ["python", "server.py"]
