# NutriSense AI

> **Enterprise AI-Powered Nutrition Management SaaS Platform**

NutriSense AI is an enterprise-grade SaaS platform designed to manage institutional nutrition profiles, automate compliance reporting, provide computer-vision dietary analysis, and generate AI-driven health insights at scale.

---

## 🌟 Key Features

- **Enterprise Dashboard**: Comprehensive visualization of nutritional trends, meal tracking, and operational analytics.
- **AI-Powered Recommendation & Vision Engine**: Multi-provider AI core (Gemini, OpenAI, Anthropic support) supporting automated risk detection, meal photo nutrition extraction via Computer Vision, anomaly flagging, and personalized dietary guidance.
- **Compliance & Audit Reporting**: Real-time regulatory tracking, exportable PDFs/CSVs, automated audit logging middleware, and scheduled report distributions.
- **Dynamic Data Tables**: Lightning-fast, server-side paginated tables with multi-column sorting, debounce searching, and bulk actions.
- **Enterprise Security & Multi-Tenancy**: Complete JWT authentication lifecycle (access/refresh tokens, password reset), Role-Based Access Control (RBAC), tenant isolation, and SQL injection prevention.
- **Real-Time Communication**: WebSocket-backed real-time notifications, chat rooms, and announcement systems.
- **Premium UI/UX Design**: Built with React 18, Vite, Tailwind CSS, Zustand, dark mode support, skeleton loaders, and responsive layout primitives.

---

## 🛠 Architecture & Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Language**: TypeScript
- **State Management**: Zustand & React Query
- **Routing**: React Router DOM v6
- **Styling**: Tailwind CSS
- **Charts & UI**: Recharts, Lucide Icons

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL / SQLite (Development) with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT, OAuth2 Bearer, Passlib (Bcrypt)
- **Real-Time**: WebSockets & AsyncIO
- **AI Processing**: Modular AI Agent framework supporting Gemini 2.0, OpenAI GPT-4o, and Anthropic models with automated fallback routing and computer vision pipelines

---

## 📁 Repository Structure

```
NutriSense-AI/
├── backend/
│   ├── alembic/        # Database migration scripts
│   ├── app/
│   │   ├── agents/     # AI processing agents (Vision, Chat, Recommendations, Reports)
│   │   ├── api/        # FastAPI v1 router endpoints (Auth, Meals, Users, Reports, AI)
│   │   ├── core/       # Core security, middleware, and config settings
│   │   ├── db/         # Database sessions and connection handlers
│   │   ├── models/     # SQLAlchemy ORM models (User, Institution, Meal, Compliance, Audit)
│   │   ├── schemas/    # Pydantic validation schemas
│   │   ├── services/   # Business logic and service layer
│   │   └── utils/      # Utility helpers and datetime formatters
│   └── tests/          # Comprehensive pytest suite (Auth, Vision, Isolation, SQL Safety, WS)
├── frontend/
│   ├── src/
│   │   ├── components/ # Reusable UI components, Dashboard widgets, Charts
│   │   ├── lib/        # API client and validation helpers
│   │   ├── pages/      # Route pages (Landing, Auth, Overview, Meals, Compliance, Reports)
│   │   └── store/      # Zustand global state stores
│   └── vite.config.ts  # Optimized Vite build and chunking configuration
├── docker-compose.yml  # Local development container orchestration
├── docker-compose.prod.yml # Production multi-container layout
├── Dockerfile          # Single-container production build file
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18+
- **Python**: 3.10+
- **PostgreSQL**: v14+ (or SQLite for quick local development)

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env     # Configure database URI and secrets
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
Interactive API Documentation will be available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
The application frontend will start at `http://localhost:5173`.

---

## 🧪 Testing

Execute the comprehensive test suite covering backend logic, AI vision pipelines, tenant isolation, and security controls:

```bash
cd backend
pytest
```

---

## 🐳 Docker Deployment

To build and launch the application using Docker Compose:

```bash
# Production orchestration
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 🔒 Security & Environment Configuration

Copy `.env.example` to `.env` and set appropriate secret values. **Never commit `.env` files containing real production credentials.**

Key Environment Variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Random 256-bit string for signing JWT tokens
- `GEMINI_API_KEY` / `OPENAI_API_KEY`: API keys for AI provider integration
- `CORS_ORIGINS`: JSON list of permitted origin URLs

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
