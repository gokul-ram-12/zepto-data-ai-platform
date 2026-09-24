# Final submission summary

## Repository

The project is submitted as one public repository: https://github.com/gokul-ram-12/zepto-data-ai-platform. The root contains `data_pipeline`, `analytics`, `support_assistant`, `tests`, `README.md`, `requirements.txt`, and `docker-compose.yml`. The history includes a feature branch with two commits and a merge back into `main`.

## Rubric remediation completed

The analytics module now includes explicit Boolean-mask calculations using compound `&` and alternative `|` conditions, four separate 2–4 sentence chart interpretations, and explicit survived/not-survived class balance reporting. The support assistant now configures ChromaDB with `hnsw:space=cosine` and includes `generate_real_answer()` with Pydantic validation and up to two corrective retries after the first attempt. The mock path remains deterministic and offline by default.

## Automated verification

Run the fast checks with `python tests/integration_test.py`. Run full source regeneration and verification with `MOCK_LLM=1 python tests/integration_test.py --run-pipelines`. The full regeneration run completed successfully: 100 scraped books, 889 cleaned Titanic rows, support-assistant examples on both routes, and all five integration test groups passing.

The test suite checks repository structure, the SQLite schema and fixed conversion rate, SQL/pandas equivalence, analytics reports and charts, class balance, model reloadability, the eight-document corpus, prompt skeleton, cosine Chroma metadata, LangGraph routes, mock API responses, real-mode retry behavior, and Git merge history.

## Local commands for final submission testing

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
MOCK_LLM=1 python tests/integration_test.py --run-pipelines
```

Start the API directly:

```bash
MOCK_LLM=1 uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

Start through Compose:

```bash
docker compose up --build
```

Test the endpoint:

```bash
curl -X POST http://localhost:7860/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the delivery fee below INR 149?"}'

curl -X POST http://localhost:7860/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the weather today?"}'
```

The first call should return a grounded answer with document sources. The second should return the fixed general-question response with an empty source list.

## Remaining user-side action

The sandbox does not have Docker installed, so the Docker image build and Compose startup must be run once on a local machine with Docker Desktop or Docker Engine. After the two endpoint calls and the full integration command pass locally, submit the single public GitHub repository URL above.
