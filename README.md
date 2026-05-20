# AI Comment Generator Backend

FastAPI backend service for generating AI-powered documentation comments using OpenRouter models.

---

## Features

- FastAPI-based REST API
- OpenRouter AI integration
- Async request handling
- Configurable AI models
- Multi-language documentation support
- Environment-based configuration
- Built with uv package manager

---

## Tech Stack

- Python 3.12+
- FastAPI
- OpenAI SDK
- OpenRouter API
- uv
- Pydantic

---

## Project Structure

```text
backend/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   └── core/
│
├── main.py
├── pyproject.toml
├── uv.lock
├── render.yaml
├── .env.example
└── .gitignore
```

---

## Local Development

### Install Dependencies

```bash
uv sync
```

---

### Run Server

```bash
uv run uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

## Environment Variables

Create `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

BASE_URL=https://openrouter.ai/api/v1

LLM_MODEL=deepseek/deepseek-chat-v3-0324:free

MAX_TOKEN=300

LLM_TEMPERATURE=0.2

REQUEST_TIMEOUT=30
```

---

## API Endpoint

### Generate Comment

```http
POST /api/v1/comment/generate
```

Request Body:

```json
{
  "code": "def add(a, b): return a + b",
  "language": "python",
  "comment_style": "docstring",
  "model": "deepseek/deepseek-chat-v3-0324:free",
  "temperature": 0.2,
  "max_tokens": 300
}
```

---

## Render Deployment

### render.yaml

```yaml
services:
  - type: web
    name: ai-comment-generator-api
    runtime: python
    plan: free

    buildCommand: |
      pip install uv
      uv sync --frozen

    startCommand: |
      uv run uvicorn main:app --host 0.0.0.0 --port $PORT

    autoDeploy: true
```

---

## Deploy to Render

1. Push backend to GitHub
2. Create new Web Service in Render
3. Connect GitHub repository
4. Add environment variables
5. Deploy service

---

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## License

MIT
