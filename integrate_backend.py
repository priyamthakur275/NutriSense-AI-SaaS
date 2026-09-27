import os
import shutil
import subprocess

base_dir = r"c:\Users\priya\Downloads\nutrisense-ai (2)"
frontend_dir = os.path.join(base_dir, "frontend")
backend_dir = os.path.join(base_dir, "backend")

# Build frontend
print("Building frontend...")
subprocess.run(["npm", "run", "build"], cwd=frontend_dir, shell=True, check=True)

# Move to backend/static
static_dir = os.path.join(backend_dir, "static")
if os.path.exists(static_dir):
    shutil.rmtree(static_dir)

print("Copying dist to static...")
shutil.copytree(os.path.join(frontend_dir, "dist"), static_dir)

# Update main.py
main_py_path = os.path.join(backend_dir, "app", "main.py")
with open(main_py_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace root handler
root_handler = """@app.get("/")
def root() -> dict:
    return {
        "service": settings.PROJECT_NAME,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }"""

new_handler = """import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
            
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
"""

if root_handler in content:
    content = content.replace(root_handler, new_handler)
else:
    # If the root handler is not exactly as expected, append it safely if SPA logic isn't there
    if "serve_spa" not in content:
        content += "\n\n" + new_handler

with open(main_py_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Integration complete.")
