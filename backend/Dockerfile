FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home academy && mkdir -p staticfiles && chown -R academy:academy /app
USER academy
EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
