#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== 1. Building Frontend SPA ==="
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

echo "=== 2. Copying Frontend Dist to Backend Static ==="
rm -rf backend/static
cp -r frontend/dist backend/static

echo "=== 3. Installing Backend Dependencies ==="
cd backend
pip install --no-cache-dir -r requirements.txt

echo "=== 4. Running Alembic Database Migrations ==="
alembic upgrade head

echo "=== Build Completed Successfully! ==="
