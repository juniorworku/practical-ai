FROM python:3.12-slim
WORKDIR /lab
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home learner
COPY . .
USER 10001
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8010"]
