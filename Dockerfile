FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY fastmile-api/pyproject.toml fastmile-api/README.md ./fastmile-api/
COPY fastmile-api/src ./fastmile-api/src

RUN pip install --no-cache-dir -e ./fastmile-api

EXPOSE 8000

CMD ["sh", "-c", "uvicorn fastmile_api.main:app --host 0.0.0.0 --port 8000"]
