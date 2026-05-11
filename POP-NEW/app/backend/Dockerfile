FROM python:3.12.8-slim

RUN groupadd --system --gid 10001 pop \
    && useradd --system --uid 10001 --gid pop --no-create-home --shell /usr/sbin/nologin pop

WORKDIR /app

COPY --chown=pop:pop backend /app/backend
COPY --chown=pop:pop frontend /app/frontend

ENV PYTHONPATH=/app/backend \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER pop:pop

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3).read()"]

CMD ["python", "/app/backend/pop_http.py", "--host", "0.0.0.0", "--port", "8080"]
