# NutriSense AI

> **Enterprise AI-Powered Nutrition Management SaaS Platform**

NutriSense AI is an enterprise-grade SaaS platform designed to manage institutional nutrition profiles, automate compliance reporting, provide computer-vision dietary analysis, and generate AI-driven health insights at scale.

---

## Key Features

**Kitchen intelligence** (details and interview notes: [docs/KITCHEN_INTELLIGENCE.md](docs/KITCHEN_INTELLIGENCE.md)):

- **Food waste tracker:** separates over-production (left in the pot) from plate waste, shows ₹ lost, worst dishes, and the gap between nutrients served and nutrients eaten. Optional AI before/after tray-photo scan.
- **Budget-aware menu planner:** a mixed-integer linear program (SciPy/HiGHS) picks a week of dishes meeting ICMR-NIN / PM POSHAN targets under a per-plate budget, and explains the minimum budget when a request is impossible.
- **Cooking forecast:** headcount forecast with weekly pattern, trend and 80% range, converted into kilos per dish; accuracy measured by walk-forward backtesting against a "same as last week" baseline.

Platform:

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

One command sets up and runs everything (Python 3.10–3.14, Node 18+; no database install needed, it uses SQLite locally):

```bash
python3 run.py        # Windows: py run.py   ·   VS Code: Ctrl+Shift+B
```

App: `http://localhost:5173` · API docs: `http://127.0.0.1:8000/docs`. See [START_HERE.md](START_HERE.md) for troubleshooting.

---

## Testing

```bash
backend/.venv/bin/python -m pytest backend/tests -q     # 79 tests
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
