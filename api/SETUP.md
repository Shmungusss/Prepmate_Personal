# Backend Setup Guide

This document explains how to fully set up and run the backend locally.

---

# Prerequisites

- Python 3.10+ (recommended 3.11)
- Git
- (Optional) Docker + Docker Compose

---

# 1. Clone the Repository

```bash
git clone <your-repo-url>
cd api
```

---

# 2. Create a Virtual Environment

Mac / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

# 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

# 4. Environment Variables

This project uses environment variables for configuration.

A template file `.env.example` is included in the repository.

Create a local `.env` file:

```bash
cp .env.example .env
```

Then open `.env` and provide real values.

Required environment variables:

- ENVIRONMENT
- OPENAI_API_KEY
- DATABASE_URL
- HOST
- PORT
- LLM

Example `.env` file:

```env
ENVIRONMENT=development
OPENAI_API_KEY=your_real_openai_key_here
DATABASE_URL=sqlite:///./app.db
HOST=0.0.0.0
PORT=8000
LLM=gpt-5.2
```

 Do NOT commit `.env` to GitHub. It contains secrets.

---

# 5. Run the Backend

From the `api/` directory:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

The API will run at:

```
http://localhost:8000
```

---

# 6. Health Check

Verify the backend is running:

```
GET http://localhost:8000/api/health
```

---

# Troubleshooting

If dependencies are missing:

```bash
pip install -r requirements.txt
```

If OpenAI requests fail:

- Ensure OPENAI_API_KEY is set in `.env`
- Restart the server after editing `.env`

---

# Notes

- `.env.example` documents required variables.
- `.env` stores your local secrets.
- Environment variables prevent hardcoding sensitive data.
