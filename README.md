# NutriSense AI Enterprise

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
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
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
