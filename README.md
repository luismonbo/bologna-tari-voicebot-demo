# Bologna TARI Voicebot — Setup & Usage

An Italian-language voice assistant for the Comune di Bologna. Answers TARI (waste tax) questions via RAG and simulates appointment booking.

---

## Deliverables (quick reference)

| Brief requirement | Location |
|---|---|
| Backend code + setup instructions | This README + `backend/` |
| Vapi agent config | `vapi/assistant.json` + `scripts/setup_vapi.py` |
| System prompt (prompt design) | [`system_prompt.md`](system_prompt.md) |
| Choices, limitations & improvements | [`docs/choices-and-limitations.md`](docs/choices-and-limitations.md) |
| AI tools used | [`docs/ai-tools-used.md`](docs/ai-tools-used.md) |
| Docker Compose (extra) | `docker-compose.yml` — three services: `db`, `backend`, `frontend` |
| Frontend dashboard (extra) | `frontend/` — appointments + call logs at http://localhost:5173 |
| DB persistence (extra) | Postgres + pgvector (`appointments` table) |

---

## Prerequisites

Before starting, ensure you have:

### Required Software

- **Docker Desktop** (Mac/Windows) or **Docker Engine + Docker Compose** (Linux)
  - Downloads: https://www.docker.com/products/docker-desktop
  - Used to run the database, backend, and frontend in containers

- **uv** (Python package manager)
  - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh` (Mac/Linux) or see https://docs.astral.sh/uv/getting-started/installation/
  - Used to run the Vapi setup script and local Python commands
  
- **ngrok CLI** (free tier is sufficient)
  - Downloads: https://ngrok.com/download
  - Used to expose your local backend to Vapi (public tunnel)
  - Create a free account at https://ngrok.com/signup

### Required Accounts & API Keys

- **Vapi Account** (free tier available)
  - Sign up at https://vapi.ai
  - Go to **Settings** → **API Keys**
  - Copy your **Private API Key** (not the public key)
  - You'll paste this into `.env` in step 2

---

## Quick Start

### 1. Clone Repository

```bash
git clone <repo-url>
cd bologna-tari-voicebot
```

### 2. Create & Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` and add your Vapi Private API Key:

```env
VAPI_PRIVATE_API_KEY=your-vapi-private-api-key-here
```

**Where to get it:** [Vapi Dashboard](https://dashboard.vapi.ai) → Settings → API Keys → Copy "Private Key" (not Public Key)

### 3. Start All Services

```bash
docker compose up --build
```

Wait for all services to be ready. You should see:

```
backend    | Uvicorn running on http://0.0.0.0:8000
frontend   | VITE vX.X.X ready in XXXms
```

### 4. Expose Backend to Vapi (Open New Terminal)

In a new terminal window, run:

```bash
ngrok http 8000
```

You'll see output like:

```
Session Status      online
Forwarding          https://abc-123-def.ngrok.io -> http://localhost:8000
```

**Copy the forwarding URL** (e.g., `https://abc-123-def.ngrok-free.app`) — you'll need it in the next step.

### 5. Upload Vapi Assistant

In the same terminal (or another new one), run:

```bash
uv run scripts/setup_vapi.py
```

The script will:
1. Prompt for your **Vapi API Key** (or read from `.env`)
2. Prompt for your **ngrok URL** (paste the URL from step 4)
3. Upload the assistant to your Vapi account with the correct tool endpoints

You'll see output like:

```
✓ SUCCESS
Assistant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Name: Bologna TARI Assistant
Tools: 4 created
```

---

## Testing

### Test a Tool Endpoint

Make a test call to the backend:

```bash
curl -X POST http://localhost:8000/tools/query_services \
  -H "Content-Type: application/json" \
  -d '{"question": "Come si paga la TARI?"}'
```

You should get back RAG results.

### Access Frontend Dashboard

Open in your browser:

```
http://localhost:5173
```

You'll see:
- **Appointments table** — all booked appointments
- **Call logs** — recent calls from Vapi. May take 1 or 2 minutes for recent call to be logged. 

---

## Important: ngrok URL Changes

**Important:** Each time you restart ngrok, you get a **new URL**.

When the URL changes:
1. Run `uv run scripts/setup_vapi.py` again with the new URL
2. Or manually update the assistant in [Vapi Dashboard](https://dashboard.vapi.ai)

**Keep ngrok running** while you're testing. If you close it, Vapi cannot reach your backend.

---

## Using the Voice Bot

### Talk to the Assistant

1. Go to [Vapi Dashboard](https://dashboard.vapi.ai)
2. Find your assistant
3. Click the phone icon with the text "Talk"
4. Vapi will ask for permissions on the microphone to start the conversation. 

Speak in Italian. The assistant responds in Italian only.

**Example conversation:**

```
You:  "Ciao, come si paga la TARI?"
Bot:  "Puoi pagare la TARI tramite..."
You:  "Voglio prenotare un appuntamento"
Bot:  "Certo! Quando preferisci?"
```

> [!IMPORTANT]
> The agent currently only handles questions regarding how to pay the TARI and the agevolazione per unico occupante. Questions outside this scope should be rejected by the agent stating no information about that is present in the knowledge base.
### Test Tool Endpoints via ngrok

Use your ngrok URL to test endpoints:

```bash
curl -X POST https://abc-123-def.ngrok-free.app/tools/check_availability \
  -H "Content-Type: application/json" \
  -d '{"office": "tributi", "date": "2026-06-26"}'
```

Replace `abc-123-def` with your actual ngrok subdomain.

---

## Directory Structure

```
.
├── README.md                    ← Setup instructions (this file)
├── system_prompt.md             ← Vapi assistant system prompt (prompt design)
├── PLAN.md                      ← Full specification
├── .env.example                 ← Template (copy to .env)
├── docker-compose.yml           ← Services: db, backend, frontend
├── pyproject.toml               ← Python dependencies (uv)
│
├── docs/
│   ├── choices-and-limitations.md  ← Decisions, limitations & future improvements
│   └── ai-tools-used.md            ← AI tools used and how
│
├── backend/
│   ├── app/main.py              ← FastAPI app
│   ├── app/tools/               ← 4 tool endpoints
│   ├── app/domain/              ← Booking logic
│   ├── app/rag/                 ← RAG retrieval
│   ├── app/db/                  ← Database models
│   ├── tests/                   ← Unit & contract tests
│   └── Dockerfile
│
├── frontend/
│   ├── src/App.tsx              ← Main component
│   ├── src/components/          ← Appointments, Logs
│   ├── package.json
│   └── Dockerfile
│
├── vapi/
│   └── assistant.json           ← Vapi config (committed)
│
├── data/
│   └── tari_corpus/             ← RAG embeddings (pre-built)
│
└── scripts/
    ├── setup_vapi.py            ← Upload assistant to Vapi
    └── delete_appointment.py    ← Dev utility: delete bookings
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ngrok URL invalid" / "403 Forbidden" | Verify ngrok is running: `ngrok http 8000`. Test the URL: `curl https://your-ngrok-url/tools/query_services` |
| No appointments showing in frontend | Check `.env` has valid `VAPI_PRIVATE_API_KEY`. Verify backend is running: `docker compose logs backend` |
| Frontend can't reach backend | Check `VITE_BACKEND_URL` in `.env` is correct: `http://localhost:8000` (local) or `http://backend:8000` (Docker) |
| Tests failing | Reset database: `docker compose down && docker compose up --build` |
| "Postgres connection timeout" | Check database: `docker compose logs db` |

---

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `VAPI_PRIVATE_API_KEY` | ✓ Yes | — | From Vapi Dashboard → Settings → API Keys |
| `DATABASE_URL` | ✓ Yes | — | DATABASE_URL - default to postgresql+asyncpg://postgres:postgres@db:5432/tari_db
| `VITE_BACKEND_URL` | No | `http://localhost:8000` | Frontend's backend URL (local dev only) |

---

## Services & Ports

| Service | Port | URL | Role |
|---------|------|-----|------|
| **Backend (FastAPI)** | 8000 | http://localhost:8000 | Tool endpoints + Vapi proxy |
| **Frontend (React)** | 5173 | http://localhost:5173 | Appointments dashboard + call logs |
| **Database (PostgreSQL)** | 5432 | — (internal only) | Appointments + RAG embeddings |
| **Ollama (Embeddings)** | 11434 | — (internal only) | RAG embedding model |
| **ngrok** | — | https://your-ngrok-url | Tunnel (Vapi → your backend) |

---

## Commands Cheat Sheet

```bash
# === Testing ===
uv run pytest                                      # Run all tests
uv run pytest backend/tests/test_*.py -v           # Run with verbose output
curl -X POST http://localhost:8000/tools/query_services \
  -H "Content-Type: application/json" \
  -d '{"question": "Test"}'                        # Test endpoint

# === Development ===
uv sync                                            # Install Python dependencies
uv run uvicorn app.main:app --reload               # Run backend locally
cd frontend && npm run dev                         # Run frontend locally
uv run ruff check . && uv run ruff format .        # Lint & format code

# === Database ===
docker compose exec db psql -U postgres -d tari_db  # Connect to DB
docker compose logs db                             # View database logs

# === Inspection ===
docker compose logs backend                        # View backend logs
docker compose logs frontend                       # View frontend logs
uv run scripts/delete_appointment.py --name "John Doe" --date 2026-06-30  # Delete booking

# === Stop ===
docker compose down                                # Stop all services
```

---