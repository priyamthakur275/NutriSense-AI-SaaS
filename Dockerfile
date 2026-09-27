# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ .
RUN npm run build

# Stage 2: Runtime Backend + Frontend SPA
FROM python:3.10-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./static

EXPOSE 8000

CMD ["sh", "-c", "python -c \"import time, os, sqlalchemy; print('Checking DB connection...'); db=os.getenv('DATABASE_URL','').replace('postgres://','postgresql://',1); engine=sqlalchemy.create_engine(db); conn=None; [time.sleep(3) for i in range(10) if not conn and not (lambda: [setattr(locals(),'conn',engine.connect()), print('DB ready!')] if True else None)()]\" || true; alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
