# Choices, Limitations & Future Improvements

## Decisions Made

This section documents key architectural and implementation decisions made for the implementation of this prototype.

### Architecture & Design

- **Single service (TARI)** instead of multi-service to maximize conversation quality over breadth
- **Vapi Assistant + transient config-as-code** (`vapi/assistant.json`) for reproducibility
- **`apiRequest` tools** to keep backend a clean, independently testable REST API (not Vapi webhook-coupled)
- **Own RAG over Vapi Knowledge Base** using pgvector, as explicitly required by the brief
- **Pre-baked embeddings**: Scraping script is included, however, ingestion is decoupled from runtime; the demo loads ingests that scraped content at docker compose build time.

### Data & Persistence

- **Postgres + pgvector** for single DB service (appointments + embeddings; meets the 3-service requirement)
- **Idempotency key generated server-side** as `sha256(office|date|time|citizen_name)[:16]` to keep the LLM-facing API clean
- **Double-booking prevention via DB constraint** — `UNIQUE(office, date, time)` enforced at schema level
- **Session-per-request with generator dependency** — FastAPI dependency injection yields a Postgres-backed store and cleans up after each request

### Conversation & Prompting

- **All orchestration logic in the prompt**; tools are dumb, validated functions
- **Booking read-back before write** as a prompt instruction, not a tool constraint
- **Italian endpointing via Vapi/transcriber-native** (not LiveKit, which is English-only)
- **Transcriber: AssemblyAI multilingual** — supports Italian natively; Deepgram Nova would fail

### Technical Stack

- **LLM: gpt-5.4-nano** — cost-efficient, tool-calling capable, confirmed in Vapi dashboard
- **Embedding model: embeddinggemma (768 dims)** — fast, multilingual, open-source, deployed via Ollama
- **Async everywhere** — asyncio + asyncpg throughout backend for non-blocking I/O
- **Frontend: modern React patterns** — custom `useFetch` hook instead of raw useEffect/useState, avoiding race conditions and boilerplate
- **Corpus auto-ingestion** — one-shot `corpus-loader` service re-ingests on each `docker compose up --build`

### Development & Testing

- **Spec-driven approach**: contracts and conversation behavior were frozen in a spec before implementation
- **Test-first / TDD** for deterministic core: 4 tool contracts, booking idempotency, double-book prevention, availability logic, date validation
- **Integration tests hit real Postgres** (not mocks) to catch migration/schema drift
- **Conversation layer validated via scripted Italian scenarios**, not unit tests (human listening is the judge)

---

## Known Limitations

### Availability & Scheduling

- Availability is **simulated, not integrated** with a real comune calendar (hardcoded office hours + weekday-only)
- To schedule real appointments, the backend would need calendar API integration

### Corpus & Knowledge

- **Snapshot corpus**: 47 chunks from 2 JSON sources (two Bologna TARI pages)
- Refresh requires re-running `uv run python -m ingest`
- No automated re-ingestion from live comune site in production

### Authentication & Security (Prototype-Grade)

- **No authentication** on backend endpoints (suitable for demo, not production)
- **Prototype-grade security**: UUID validation on `call_id`, exact-match citizen lookup, bounded queries, sanitized errors
- Production deployment would require: full authentication, rate limiting, secrets management (Vault/AWS Secrets Manager), audit logging

### Frontend

- **Call logs require Vapi private API key** (backend proxies it); graceful empty state if key is missing or expired
- **No E2E tests** on frontend (only visual and manual testing)
- **No dark mode toggle** or advanced state management

### Language & Speech

- **Transcriber tuning for Italian** is approximate; not extensively tested on edge cases (accents, background noise, rapid speech)
- **AssemblyAI multilingual** model used (included in credits), but an Italian-specific model would be ideal
- **Accent marks & pronunciation**: no dictionary rules for "TARI" or domain jargon

### Data Collection

- **Fiscal code not requested** during booking (complicated dictation in prototype phase)
- **Name dictation relies on ASR fallibility** — spell-back instruction in prompt helps but isn't foolproof

### Database

- **PostgreSQL password hardcoded** in `docker-compose.yml` (acceptable for prototype; production would use a Vault)

---

## What I'd Improve With More Time

### RAG & Knowledge

- **Larger corpus** (currently 47 chunks; aim for better coverage of TARI information)
- **More frequent ingestion** (automated pipeline triggered by content changes)
- **GPU-accelerated inference** (llama.cpp or vLLM for embedding speed)
- **Hybrid retrieval** (BM25 + semantic for robustness)

### Calendar & Scheduling

- **Real comune calendar integration** (check actual availability, not simulation)
- **OAuth for authenticated citizens** (e.g., via SPID)
- **Multi-office support** (extend beyond Ufficio Tributi)

### Conversation & Evaluation

- **Richer evaluation dataset** (50+ scripted Italian dialogues covering edge cases)
- **Multi-service scaling** (handle TARI, ICI, SUAP, etc. with single backend and possibly a Vapi Squad instead of a single assistant)
- **Observability** (Langfuse for call tracing, latency analysis, user feedback loops)

### Frontend & UX

- **End-to-end tests** (Playwright for critical flows)
- **Unit tests for `useFetch` hook** and components
- **Dark mode toggle** with intentional design

### Deployment & Infrastructure

- **Multi-region deployment** (reduce latency for citizens across Italy)
- **CDN for frontend assets** (faster static delivery)
- **Rate limiting + DDoS protection** on all endpoints
- **Audit logging** for compliance (GDPR, administrative record-keeping)

### Vapi Configuration

- **Fine-tuned Italian transcriber thresholds** based on real speaker data
- **Dictionary pronunciation rules** for "TARI" and tributi jargon
- **Improve voice**: by choosing a different (not default Vapi) voice provider and introducing pronounciation dictionaries.

### Model & Provider Flexibility

- **Azure OpenAI or Anthropic API** as alternatives to OpenAI (reduces latency but for prototype did not want to overcomplicate)
- **Option to swap embedding models** without pipeline re-run (cached embeddings)

---

