# Contributing to NutriSense AI

We welcome contributions! Please adhere to our internal coding standards:
1. Ensure all React components are strongly typed.
2. Run `npm run build` locally to verify Rollup chunk optimizations.
3. All FastAPI backend endpoints must implement Pydantic validation and robust RBAC checks via `Permission`.
4. Ensure `alembic` migrations are provided for any DB model changes.
