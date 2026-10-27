#!/usr/bin/env python3
"""One-command local runner for NutriSense AI (Windows, macOS, Linux).

    python run.py              # set up (first time) and start backend + frontend
    python run.py --setup-only # install / repair only
    python run.py --backend-only
    python run.py --no-browser

What it does:
  1. Checks Python (3.10-3.14) and Node.js (18+). If started with an
     unsupported Python it re-launches itself with a supported one if found.
  2. Creates backend/.env (local SQLite database, random secret key).
  3. Creates backend/.venv and installs requirements (only when they change).
  4. Runs database migrations (alembic upgrade head).
  5. Runs `npm ci` in frontend/ (only when package-lock.json changes).
  6. Starts FastAPI on http://127.0.0.1:8000 and Vite on http://localhost:5173,
     opens the browser, and stops both on Ctrl+C.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
LOGS = ROOT / ".run-logs"
IS_WIN = os.name == "nt"
MIN_PY, MAX_PY = (3, 10), (3, 14)
BACKEND_PORT, FRONTEND_PORT = 8000, 5173


def say(msg: str) -> None:
    print(f"[nutrisense] {msg}", flush=True)


def die(msg: str) -> None:
    print(f"\n[nutrisense] ERROR: {msg}\n", flush=True)
    sys.exit(1)


# ---------------------------------------------------------------- Python
def py_ok(v: tuple[int, int]) -> bool:
    return MIN_PY <= v <= MAX_PY


def find_supported_python() -> list[str] | None:
    candidates: list[list[str]] = []
    for minor in (13, 12, 14, 11, 10):
        if IS_WIN:
            candidates.append(["py", f"-3.{minor}"])
        candidates.append([f"python3.{minor}"])
    for cmd in candidates:
        exe = shutil.which(cmd[0])
        if not exe:
            continue
        try:
            out = subprocess.run(cmd + ["-c", "import sys;print(sys.version_info[0],sys.version_info[1])"],
                                 capture_output=True, text=True, timeout=20)
            major, minor = map(int, out.stdout.split())
            if py_ok((major, minor)):
                return cmd
        except Exception:
            continue
    return None


def ensure_python() -> None:
    v = sys.version_info[:2]
    if py_ok(v):
        return
    if os.environ.get("NUTRISENSE_RELAUNCHED"):
        die(f"Python {v[0]}.{v[1]} is not supported.")
    alt = find_supported_python()
    if alt:
        say(f"Python {v[0]}.{v[1]} is not supported; switching to {' '.join(alt)}")
        env = dict(os.environ, NUTRISENSE_RELAUNCHED="1")
        sys.exit(subprocess.call(alt + [str(Path(__file__).resolve())] + sys.argv[1:], env=env))
    die(f"Python {v[0]}.{v[1]} is not supported. Install Python 3.12 or 3.13 from "
        "https://www.python.org/downloads/ (Windows: tick 'Add python.exe to PATH'), "
        "restart VS Code, and run again.")


# ---------------------------------------------------------------- helpers
def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")


def file_hash(*paths: Path) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    h.update(sys.version.encode())
    return h.hexdigest()


def run(cmd: list[str], cwd: Path, what: str, env: dict | None = None) -> None:
    say(what)
    r = subprocess.run(cmd, cwd=cwd, env=env, shell=False)
    if r.returncode != 0:
        die(f"'{' '.join(map(str, cmd))}' failed (see the output above).")


def npm_cmd() -> str:
    exe = shutil.which("npm.cmd" if IS_WIN else "npm") or shutil.which("npm")
    if not exe:
        die("Node.js / npm not found. Install the LTS version from https://nodejs.org, restart VS Code, run again.")
    return exe


def ensure_node() -> None:
    node = shutil.which("node")
    if not node:
        die("Node.js not found. Install the LTS version from https://nodejs.org, restart VS Code, run again.")
    out = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    try:
        major = int(out.lstrip("v").split(".")[0])
    except ValueError:
        major = 0
    if major < 18:
        die(f"Node.js {out} is too old. Install the LTS version from https://nodejs.org.")


def port_in_use(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def http_ok(url: str, timeout: float = 3) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status < 500
    except Exception:
        return False


# ---------------------------------------------------------------- setup
def write_env() -> None:
    env_file = BACKEND / ".env"
    if env_file.exists():
        text = env_file.read_text(encoding="utf-8")
        # Old copies pointed at a local Postgres most people don't have.
        if "DATABASE_URL=postgresql://nutrisense:nutrisense@localhost" in text:
            text = text.replace("DATABASE_URL=postgresql://nutrisense:nutrisense@localhost:5432/nutrisense",
                                "DATABASE_URL=sqlite:///./nutrisense.db")
            env_file.write_text(text, encoding="utf-8")
            say("Switched backend/.env to the local SQLite database")
        return
    env_file.write_text(
        "# Local development settings (created by run.py, git-ignored)\n"
        "ENVIRONMENT=development\nDEBUG=true\n"
        f"SECRET_KEY={secrets.token_urlsafe(48)}\n"
        "DATABASE_URL=sqlite:///./nutrisense.db\n"
        'CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000"]\n'
        "LOG_LEVEL=INFO\n"
        "AI_PROVIDER=gemini\n"
        "# Optional: paste a key to enable the AI features locally\n"
        "GEMINI_API_KEY=\nOPENAI_API_KEY=\n",
        encoding="utf-8",
    )
    say("Created backend/.env (SQLite database, random secret key)")


def setup_backend() -> None:
    if VENV.exists() and not venv_python().exists():
        shutil.rmtree(VENV, ignore_errors=True)
    if not venv_python().exists():
        run([sys.executable, "-m", "venv", str(VENV)], BACKEND, "Creating backend/.venv ...")
    req = BACKEND / "requirements.txt"
    stamp = VENV / ".req-hash"
    want = file_hash(req)
    if not stamp.exists() or stamp.read_text() != want:
        run([str(venv_python()), "-m", "pip", "install", "--disable-pip-version-check", "-q", "--upgrade", "pip"],
            BACKEND, "Updating pip ...")
        run([str(venv_python()), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(req)],
            BACKEND, "Installing backend packages (first run takes a few minutes) ...")
        stamp.write_text(want)
    else:
        say("Backend packages up to date")
    run([str(venv_python()), "-m", "alembic", "upgrade", "head"], BACKEND, "Applying database migrations ...")


def setup_frontend() -> None:
    lock = FRONTEND / "package-lock.json"
    stamp = FRONTEND / "node_modules" / ".lock-hash"
    want = file_hash(lock)
    if not stamp.exists() or stamp.read_text() != want:
        run([npm_cmd(), "ci", "--legacy-peer-deps", "--no-audit", "--no-fund"], FRONTEND,
            "Installing frontend packages (first run takes a few minutes) ...")
        stamp.write_text(want)
    else:
        say("Frontend packages up to date")


# ---------------------------------------------------------------- start
def start(cmd: list[str], cwd: Path, log_name: str) -> subprocess.Popen:
    LOGS.mkdir(exist_ok=True)
    log = open(LOGS / log_name, "w", encoding="utf-8")
    kwargs: dict = {"cwd": cwd, "stdout": log, "stderr": subprocess.STDOUT}
    if IS_WIN:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(cmd, **kwargs)


def stop(p: subprocess.Popen) -> None:
    if p.poll() is not None:
        return
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        else:
            os.killpg(p.pid, signal.SIGTERM)
        p.wait(timeout=10)
    except Exception:
        p.kill()


def wait_for(url: str, proc: subprocess.Popen, log_name: str, seconds: int) -> None:
    for _ in range(seconds * 2):
        if proc.poll() is not None:
            tail = (LOGS / log_name).read_text(encoding="utf-8", errors="replace")[-3000:]
            die(f"{log_name.split('.')[0]} stopped while starting. Last log lines:\n{tail}")
        if http_ok(url):
            return
        time.sleep(0.5)
    die(f"{url} did not respond in {seconds}s. See .run-logs/{log_name}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run NutriSense AI locally")
    ap.add_argument("--setup-only", action="store_true")
    ap.add_argument("--backend-only", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    ensure_python()
    if not args.backend_only:
        ensure_node()
    write_env()
    setup_backend()
    if not args.backend_only:
        setup_frontend()
    if args.setup_only:
        say("Setup complete. Run `python run.py` to start.")
        return

    health = f"http://127.0.0.1:{BACKEND_PORT}/api/v1/health"
    procs: list[subprocess.Popen] = []
    try:
        if port_in_use(BACKEND_PORT):
            if http_ok(health):
                die(f"A NutriSense backend is already running on port {BACKEND_PORT}. "
                    "Close the other terminal running it (or restart VS Code) and run again.")
            die(f"Port {BACKEND_PORT} is used by another program. Close it and run again.")
        say("Starting backend on http://127.0.0.1:8000 ...")
        be = start([str(venv_python()), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
                    "--port", str(BACKEND_PORT), "--reload"], BACKEND, "backend.log")
        procs.append(be)
        wait_for(health, be, "backend.log", 90)

        url = f"http://127.0.0.1:{BACKEND_PORT}/docs"
        if not args.backend_only:
            if port_in_use(FRONTEND_PORT):
                die(f"Port {FRONTEND_PORT} is in use (an old `npm run dev`?). Close it and run again.")
            say("Starting frontend on http://localhost:5173 ...")
            fe = start([npm_cmd(), "run", "dev", "--", "--port", str(FRONTEND_PORT), "--strictPort"],
                       FRONTEND, "frontend.log")
            procs.append(fe)
            wait_for(f"http://127.0.0.1:{FRONTEND_PORT}/", fe, "frontend.log", 120)
            wait_for(f"http://127.0.0.1:{FRONTEND_PORT}/api/v1/health", fe, "frontend.log", 30)
            url = f"http://localhost:{FRONTEND_PORT}"

        print("\n" + "=" * 60)
        say("Everything is running")
        say(f"  App:      {url}")
        say(f"  API docs: http://127.0.0.1:{BACKEND_PORT}/docs")
        say("  Logs:     .run-logs/   |   Press Ctrl+C to stop")
        print("=" * 60 + "\n", flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        while all(p.poll() is None for p in procs):
            time.sleep(1)
        die("A server stopped unexpectedly. See .run-logs/backend.log and .run-logs/frontend.log")
    except KeyboardInterrupt:
        say("Stopping ...")
    finally:
        for p in procs:
            stop(p)


if __name__ == "__main__":
    main()
