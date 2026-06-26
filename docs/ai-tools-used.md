# AI Tools Used

## Tool

**Claude Code** — Anthropic's agentic CLI — was the primary development tool for this
prototype. It worked directly in the repository with file, shell, and test-runner access.

## How it was used (working style)

The project was built the way I work with agentic tools: **the human owns the spec and the
decisions; the agent implements under tight, written constraints.** This is all aided by frequent commits
after new features and fixes are implemented, with commit messages that are clear for humans and agents alike. 

- **Spec-driven.** The spec was written before any code — tool contracts, conversation and
  prompt design, and the build sequence were all frozen upfront and only updated when justified. `CLAUDE.md` instructs the agent
  to read it first and to ask before adding scope.
- **Test-first (TDD) for the deterministic core.** Contract and unit tests were written before
  implementation (red → green → refactor) for the four tool contracts, booking idempotency /
  double-book prevention, availability logic, and date validation/rejection — **118 tests across
  9 files**. The conversation layer was deliberately *not* unit-tested; it is validated with the
  scripted Italian voice scenarios and manual listening.
- **Guardrails as code.** `CLAUDE.md` "hard rules" constrained the agent throughout: tools are
  dumb validated functions, the backend stays a plain REST API, our own RAG only (no Vapi KB),
  idempotent booking, Italian only, and never scrape at build/startup.
- **Decision-log discipline.** Every non-trivial choice or tradeoff was logged as it was made —
  so the reasoning is auditable rather than reconstructed afterwards.
- **Persistent project memory.** The agent kept cross-session memory of build progress and of my
  preferences (e.g. "don't pin dependency versions — let `uv` resolve latest").
- **Conventions enforced by Claude Code's rule/skill system.** Python standards (PEP 8, `pytest`,
  `ruff` lint/format), `uv` for packaging, conventional-commit messages, and small scoped commits.
  Skills mostly included obra/superpowers, which helps to implement TDD with a sub-agent driven approach.
- **Separating planning and executing**: Claude Opus 4.8 was used for planning features and specs, while Sonnet 4.6 was used
  execute the tasks involved in the implementation. 

## What the agent produced

- **Backend (FastAPI):** the four `apiRequest` tool endpoints, pure domain logic
  (booking / availability / date validation), async SQLAlchemy + pgvector, and the Vapi log proxy.
- **RAG ingestion pipeline** (scrape → chunk → embed → load) plus the committed prebuilt corpus.
- **Frontend (React + Vite):** appointments table and call-log viewer.
- **Vapi assistant config** `scripts/setup_vapi.py` recreation
  script.
- **Docker Compose** stack, the test suite, and this documentation.

## Human in the loop

I defined the spec and architecture, made the product/UX and provider decisions (e.g. AssemblyAI
multilingual transcriber, the embedding model, the nano-class LLM — confirmed in the Vapi
dashboard), reviewed agent's output, modified code by hand when necessary, and ran the Italian voice tests by hand.