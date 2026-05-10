FROM python:3.12-slim

WORKDIR /app

COPY backend /app/backend
COPY frontend /app/frontend

ENV PYTHONPATH=/app/backend
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3).read()"]

CMD ["python", "/app/backend/pop_http.py", "--host", "0.0.0.0", "--port", "8080"]
