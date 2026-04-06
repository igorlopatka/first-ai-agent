# First AI Agent

Starter projektu został przebudowany z prostego CLI do backendu przygotowanego pod model `Copilot-first`.

## Stack

- Agno
- Arize Phoenix
- Langfuse
- Ragas
- Pydantic
- FastAPI

## Co jest w projekcie

- backend usługi pod Microsoft 365 Copilot,
- adapter kanału Copilot,
- strukturalne kontrakty request/response,
- telemetry pod Phoenix i Langfuse,
- skrypt ewaluacyjny Ragas,
- przykładowy manifest publikacyjny dla pilotażu,
- dokument referencyjny architektury agentów korporacyjnych.

## Szybki start

1. Utwórz środowisko wirtualne i zainstaluj zależności:

```bash
pip install -e .
```

2. Skopiuj plik środowiskowy:

```bash
cp .env.example .env
```

3. Ustaw przynajmniej:

- `OPENAI_API_KEY`

4. Uruchom backend:

```bash
uvicorn first_ai_agent.service:app --reload
```

5. Sprawdź healthcheck:

```bash
curl http://127.0.0.1:8000/health
```

6. Wyślij przykładowe żądanie:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/copilot/message \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Wyjasnij prostym jezykiem, do czego sluzy Langfuse",
    "user_id": "user-123",
    "tenant_id": "tenant-xyz",
    "session_id": "session-1"
  }'
```

## Główne endpointy

- `GET /health`
- `GET /api/v1/copilot/onboarding`
- `POST /api/v1/agent/respond`
- `POST /api/v1/copilot/message`

## Pliki warte uwagi

- `src/first_ai_agent/service.py`
- `src/first_ai_agent/copilot_adapter.py`
- `src/first_ai_agent/agent.py`
- `src/first_ai_agent/schemas.py`
- `docs/enterprise-agent-architecture.md`
- `src/first_ai_agent/m365_manifest.json`

## Microsoft 365 Copilot

Projekt zawiera przykładowy adapter i manifest dla pilotażu custom agenta. To nie jest pełne, gotowe wdrożenie tenantowe, ale solidny backendowy fundament pod integrację z Microsoft 365 Agents SDK i publikację do testowej kohorty użytkowników.

## Ewaluacja

Uruchom:

```bash
python -m first_ai_agent.evaluate
```

Skrypt zawiera 10 scenariuszy pilotażowych skupionych na prostym języku, doprecyzowaniach i jakości odpowiedzi dla użytkownika nietechnicznego.
