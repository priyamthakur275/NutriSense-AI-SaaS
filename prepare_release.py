import os
import re

base_dir = r"c:\Users\priya\Downloads\nutrisense-ai (2)"

readme_content = """# NutriSense AI Enterprise

NutriSense AI is an enterprise-grade SaaS platform designed to manage institutional nutrition profiles, automate compliance reporting, and provide AI-driven health insights at scale.

## Key Features

- **Enterprise Dashboard**: Comprehensive visualization of nutritional trends, meal tracking, and operational analytics.
- **AI Recommendation Engine**: Automated risk detection, anomaly flagging, and actionable dietary improvements.
- **Compliance Reports**: Real-time regulatory tracking, exportable PDFs/CSVs, and scheduled audit distributions.
- **Dynamic Data Tables**: Lightning-fast, server-side paginated tables with multi-column sorting, debounce searching, and bulk actions.
- **Modern Security Architecture**: Complete JWT authentication lifecycle, RBAC authorization, and secure endpoints.
- **Premium UI/UX**: Dark mode, responsive design, fluid micro-interactions, skeleton loading states, and robust accessibility standards.

## Architecture & Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Language**: TypeScript
- **Routing**: React Router DOM v6 (Lazy loaded chunks)
- **Styling**: Tailwind CSS & Vanilla CSS Design System
- **State Management**: Zustand
- **Data Fetching**: Axios & React Query
- **Charts**: Recharts
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT & OAuth2 Password Bearer
- **AI Processing**: Integration with LLM via structured JSON (Anthropic/OpenAI compatible hooks)

## Folder Structure

```
nutrisense-ai/
├── backend/
│   ├── app/
│   │   ├── api/        # FastAPI routers & endpoints
│   │   ├── core/       # Security, Config & Exceptions
│   │   ├── db/         # SQLAlchemy sessions & migrations
│   │   ├── models/     # DB Models
│   │   ├── schemas/    # Pydantic validation schemas
│   │   └── services/   # Business logic & AI Engine
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/ # Reusable UI components (Cards, Tables)
│   │   ├── lib/        # API configurations
│   │   ├── pages/      # Route components (Dashboard, Auth, Landing)
│   │   └── store/      # Zustand state logic
│   └── vite.config.ts  # Vite build & chunking optimization
├── docker-compose.yml  # Production Orchestration
└── README.md
```

## Installation & Running Locally

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL (v14+)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env     # Update your local DB credentials
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## Docker Setup (Production)

To spin up the entire stack using Docker Compose:
```bash
docker-compose up --build -d
```
This will orchestrate the PostgreSQL database, FastAPI backend server, and Nginx-served React frontend.

## Deployment Guide

1. Ensure all environment variables are populated securely in your production orchestrator.
2. The frontend is fully optimized utilizing manual chunking strategies. Build using `npm run build` and serve `dist` via Nginx or Vercel.
3. The backend leverages Gunicorn with Uvicorn workers for high concurrency.
4. Set `CORS_ORIGINS` to explicitly allow your frontend domain.

## Future Improvements

- Implementation of WebSockets for real-time AI insight broadcasting.
- Further expansion of PDF templating pipelines for institutional branding customization.

## License
MIT License. See `LICENSE` for more information.
"""

env_example_content = """# DATABASE
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nutrisense_db
DATABASE_URI=postgresql://postgres:postgres@localhost:5432/nutrisense_db

# SECURITY
SECRET_KEY=generate-a-secure-random-key-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# AI ENGINE
OPENAI_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
"""

license_content = """MIT License

Copyright (c) 2026 NutriSense AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
"""

contributing_content = """# Contributing to NutriSense AI

We welcome contributions! Please adhere to our internal coding standards:
1. Ensure all React components are strongly typed.
2. Run `npm run build` locally to verify Rollup chunk optimizations.
3. All FastAPI backend endpoints must implement Pydantic validation and robust RBAC checks via `Permission`.
4. Ensure `alembic` migrations are provided for any DB model changes.
"""

docker_compose_content = """version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-nutrisense_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URI=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-nutrisense_db}
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
"""

backend_dockerfile = """FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

frontend_dockerfile = """FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

frontend_nginx_conf = """server {
    listen 80;
    server_name localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
}
"""

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

write_file(os.path.join(base_dir, "README.md"), readme_content)
write_file(os.path.join(base_dir, "LICENSE"), license_content)
write_file(os.path.join(base_dir, "CONTRIBUTING.md"), contributing_content)
write_file(os.path.join(base_dir, ".env.example"), env_example_content)
write_file(os.path.join(base_dir, "docker-compose.yml"), docker_compose_content)

if not os.path.exists(os.path.join(base_dir, "backend", "Dockerfile")):
    write_file(os.path.join(base_dir, "backend", "Dockerfile"), backend_dockerfile)

if not os.path.exists(os.path.join(base_dir, "frontend", "Dockerfile")):
    write_file(os.path.join(base_dir, "frontend", "Dockerfile"), frontend_dockerfile)
    write_file(os.path.join(base_dir, "frontend", "nginx.conf"), frontend_nginx_conf)

# Remove console logs recursively in frontend/src (excluding specific test files if any)
src_dir = os.path.join(base_dir, "frontend", "src")
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith((".ts", ".tsx")):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # simple regex to remove console.log statements
            cleaned_content = re.sub(r'console\.log\(.*?\);?', '', content)
            if cleaned_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

print("Release preparation complete.")
