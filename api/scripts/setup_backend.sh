#!/usr/bin/env bash
set -e

echo "== Backend setup =="

# Go to backend root
cd "$(dirname "$0")/.."

# Create venv if not exists
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "Created .venv"
fi

source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
  echo "Add your OPENAI_API_KEY to .env"
fi

echo "Done."