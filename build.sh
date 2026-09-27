#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Building Frontend SPA ==="
cd frontend
npm ci --legacy-peer-deps
npm run build
cd ..

echo "=== 2. Copying Frontend Dist to Backend Static ==="
rm -rf backend/static
cp -R frontend/dist backend/static

echo "=== 3. Installing Backend Dependencies ==="
cd backend
python -m pip install --no-cache-dir -r requirements.txt

echo "=== Build completed successfully ==="
