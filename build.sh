#!/usr/bin/env bash
# Render build script — runs during every deploy
set -o errexit   # exit on error
set -o pipefail  # catch pipe failures

echo "==> Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Running database migrations"
alembic upgrade head

echo "==> Build complete"
