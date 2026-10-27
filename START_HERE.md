# Run NutriSense AI on your computer

## 1. Install two things (once)

| Tool | Version | Download |
| --- | --- | --- |
| **Python** | 3.10 to 3.14 (3.12 or 3.13 recommended) | https://www.python.org/downloads/ (Windows: tick **"Add python.exe to PATH"**) |
| **Node.js** | 18 or newer (the **LTS** version) | https://nodejs.org |

Restart VS Code after installing them. No PostgreSQL, Docker or API keys are needed: locally the app uses a SQLite file that is created automatically.

## 2. Run it

**VS Code:** open the project folder, then press **Ctrl+Shift+B** (Mac: **Cmd+Shift+B**), or **Terminal → Run Task… → "NutriSense: Run (backend + frontend)"**.

**Terminal**, in the project folder:

| OS | Command |
| --- | --- |
| Windows | `py run.py` (or double-click `start_windows.bat`) |
| macOS / Linux | `python3 run.py` (or `./start.sh`) |

The first run installs everything (2–5 minutes); after that it starts in seconds. When you see **"Everything is running"**, the browser opens:

- App: http://localhost:5173 (register a new account to sign in)
- API docs: http://127.0.0.1:8000/docs
- **Ctrl+C** in that terminal stops both servers.

Options: `--backend-only`, `--setup-only` (install/repair only), `--no-browser`.

AI features (chat, meal-photo analysis) need a key: put `GEMINI_API_KEY=...` (or `OPENAI_API_KEY=...`) in `backend/.env` and run again. Everything else works without one.

## 3. Troubleshooting

| What you see | Fix |
| --- | --- |
| "Python 3.9 / 3.15 is not supported" | Install Python 3.13 and run `python3.13 run.py` (Windows: `py -3.13 run.py`) |
| `npm` / `node` not found | Install Node LTS and restart VS Code |
| "Port 8000 / 5173 is in use" | Close the other terminal running the app (or restart the computer) and run again |
| Package install fails mentioning a compiler / "Microsoft Visual C++" | Use Python 3.12 or 3.13, delete `backend/.venv`, run again |
| Login/register shows a network error | The backend isn't running: start with `run.py`, not just `npm run dev` |
| Anything else | Look at `.run-logs/backend.log` and `.run-logs/frontend.log` |

Start completely fresh: delete `backend/.venv`, `frontend/node_modules`, `backend/.env` and `backend/nutrisense.db`, then run again.

## 4. Tests

VS Code: **Run Task… → "NutriSense: Backend tests"** (59 tests), or `backend/.venv/bin/python -m pytest backend/tests -q` (Windows: `backend\.venv\Scripts\python -m pytest backend\tests -q`).

## 5. Live site

https://nutrisense-ai-x3cl.onrender.com runs on Render (free web service) with a free Neon PostgreSQL database. On the free plan it sleeps after 15 minutes without visitors; the first visit after that takes about a minute to wake up.
