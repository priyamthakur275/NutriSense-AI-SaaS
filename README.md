# NutriSense AI

> **Enterprise AI-Powered Nutrition Management SaaS Platform**

NutriSense AI is an enterprise-grade SaaS platform designed to manage institutional nutrition profiles, automate compliance reporting, provide computer-vision dietary analysis, and generate AI-driven health insights at scale.

---

## Key Features

- **Enterprise Dashboard:** Visualization of nutritional trends, meal tracking, and operational analytics.
- **AI-Powered Recommendation & Vision Engine:** Gemini and OpenAI support for automated risk detection, meal photo nutrition extraction via computer vision, anomaly flagging, and personalized dietary guidance.
- **Compliance & Audit Reporting:** Regulatory tracking, exportable PDFs/CSVs, automated audit logging, and scheduled report distributions.
- **Dynamic Data Tables:** Server-side pagination, multi-column sorting, debounced searching, and bulk actions.
- **Enterprise Security & Multi-Tenancy:** JWT authentication, RBAC, tenant isolation, and SQL injection prevention.
- **Real-Time Communication:** WebSocket-backed notifications, chat rooms, and announcements.
- **Premium UI/UX:** React, Vite, Tailwind CSS, Zustand, dark mode, skeleton loaders, and responsive layouts.

---

## Architecture & Tech Stack

### Frontend
- **Framework:** React 18 with Vite
- **Language:** TypeScript
- **State Management:** Zustand & React Query
- **Routing:** React Router DOM v6
- **Styling:** Tailwind CSS
- **Charts & UI:** Recharts, Lucide Icons

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL / SQLite (Development) with SQLAlchemy ORM
- **Migrations:** Alembic
- **Authentication:** JWT, OAuth2 Bearer, Passlib (Bcrypt)
- **Real-Time:** WebSockets & AsyncIO
- **AI Processing:** Gemini and OpenAI integrations with computer vision pipelines

---

## Repository Structure

```
NutriSense-AI/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |   |-- agents/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   `-- utils/
|   `-- tests/
|-- frontend/
|   `-- src/
|       |-- components/
|       |-- lib/
|       |-- pages/
|       `-- store/
|-- docker-compose.yml
|-- docker-compose.prod.yml
|-- Dockerfile
`-- README.md
```

---

## Getting Started

### Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Swagger UI: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

---

## Testing

```bash
cd backend
pytest
```

---

## Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## Security & Environment Configuration

Copy `.env.example` to `.env` and set local values. Never commit real production credentials.

Key variables:
- `DATABASE_URL`
- `SECRET_KEY`
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `CORS_ORIGINS`

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
