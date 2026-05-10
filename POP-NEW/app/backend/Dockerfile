FROM python:3.12-slim

WORKDIR /app

COPY backend /app/backend
COPY frontend /app/frontend

ENV PYTHONPATH=/app/backend
EXPOSE 8080

CMD ["python", "/app/backend/pop_http.py", "--host", "0.0.0.0", "--port", "8080"]
