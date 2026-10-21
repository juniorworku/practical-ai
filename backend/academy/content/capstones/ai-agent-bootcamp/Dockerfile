FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home learner
COPY . .
USER learner
EXPOSE 8000
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "20"]
