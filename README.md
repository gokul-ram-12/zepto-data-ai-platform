# Zepto Data & AI Platform

> **One connected capstone submission** covering data engineering, analytics and machine learning, and a grounded GenAI support service.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/integration%20tests-5%20groups%20passing-brightgreen)](#automated-verification)
[![License](https://img.shields.io/badge/services-no%20paid%20services-success)](#design-decisions)

This repository implements the three modules required by the Zepto AI/ML capstone in one public repository:

1. **Data pipeline** — scrapes catalogue data, cleans it, converts GBP to INR, loads normalized SQLite tables, and demonstrates SQL plus pandas querying.
2. **Analytics pipeline** — profiles and cleans the Titanic dataset, builds an EDA story, trains and evaluates classifiers, compares imbalance strategies, performs tuning, and completes a fare-regression side task.
3. **Support assistant** — embeds eight Zepto policy documents locally, stores them in ChromaDB, routes questions through LangGraph, and exposes a validated FastAPI endpoint.

## 📁 Repository layout

```text
zepto-data-ai-platform/
├── README.md
├── FINAL_SUBMISSION_SUMMARY.md
├── requirements.txt
├── docker-compose.yml
├── data_pipeline/
│   ├── pipeline.py
│   ├── README.md
│   └── artifacts/
├── analytics/
│   ├── analysis.py
│   ├── titanic.csv
│   ├── README.md
│   └── artifacts/
├── support_assistant/
│   ├── main.py
│   ├── Dockerfile
│   ├── README.md
│   └── docs/
└── tests/
    └── integration_test.py
```

## 🧰 Requirements

- Python 3.11 or newer; Python 3.11 is recommended on Windows.
- Internet access for the first data scrape, the first Titanic dataset fetch, and the first download of the local embedding model.
- Docker Desktop with Docker Compose for the container test.
- No paid API, LLM account, or API key is required for the graded baseline.

## 🪟 Windows PowerShell setup

Open PowerShell and run each command separately from the repository folder. Do not type the `>>` characters that PowerShell may show while it is waiting for a continuation line.

```powershell
cd "C:\Users\GOKUL\Downloads\vv\zepto-data-ai-platform"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If Python 3.11 is not installed, use `python -m venv .venv` instead of `py -3.11 -m venv .venv`.

Set the required deterministic support-assistant mode for the current PowerShell window:

```powershell
$env:MOCK_LLM = "1"
```

## 🐧 Linux/macOS setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
export MOCK_LLM=1
```

## 🧪 Automated verification

The rubric-driven integration suite checks repository structure, the SQLite schema and fixed conversion rate, SQL and pandas equivalence, Titanic reports and charts, Boolean-mask analysis, class-balance reporting, model reloadability, the eight-document corpus, prompt structure, cosine ChromaDB configuration, LangGraph routes, mock responses, real-mode validation retries, and Git merge history.

### Fast verification using existing artifacts

**Windows PowerShell:**

```powershell
$env:MOCK_LLM = "1"
python tests/integration_test.py
```

**Linux/macOS:**

```bash
MOCK_LLM=1 python tests/integration_test.py
```

### Full verification from source

This is the strongest check. It regenerates all module outputs and then runs every integration test.

**Windows PowerShell:**

```powershell
$env:MOCK_LLM = "1"
python tests/integration_test.py --run-pipelines
```

**Linux/macOS:**

```bash
MOCK_LLM=1 python tests/integration_test.py --run-pipelines
```

Expected final result:

```text
Ran 5 tests
OK
```

The full run currently produces 100 scraped books, 889 cleaned Titanic rows, both support-assistant example responses, and five passing integration-test groups.

## ▶️ Run each module manually

### 1. Data pipeline

```powershell
python data_pipeline/pipeline.py
```

The pipeline scrapes the first five catalogue pages from Books to Scrape, producing 100 rows. It uses the required fixed conversion rate:

> **1 GBP = 105.50 INR**

Outputs include `data_pipeline/artifacts/books.db` and `data_pipeline/artifacts/query_results.md`.

### 2. Analytics pipeline

```powershell
python analytics/analysis.py
```

The pipeline loads Seaborn's Titanic dataset once, saves `analytics/titanic.csv` as the offline fallback, creates EDA reports and charts, evaluates three classifiers, compares class-weight and SMOTE strategies, tunes Random Forest, completes fare regression, and saves a complete reloadable pipeline at `analytics/artifacts/best_pipeline.joblib`.

### 3. Support assistant examples

```powershell
$env:MOCK_LLM = "1"
$env:RUN_EXAMPLES = "1"
python support_assistant/main.py
```

The example run demonstrates one policy question and one unrelated question without making an LLM API call.

## 🚀 Run the FastAPI service directly

Start the server in PowerShell 1:

```powershell
$env:MOCK_LLM = "1"
python -m uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

Open Swagger UI in your browser:

```text
http://localhost:7860/docs
```

Open PowerShell 2 and test a policy question:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:7860/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query":"What is the delivery fee below INR 149?"}'
```

Expected behavior: the answer starts with `Based on the retrieved context:`, `sources` contains document IDs, and `confidence` is `1`.

Test an unrelated question:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:7860/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query":"What is the weather today?"}'
```

Expected response:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

Stop the direct server with `Ctrl+C`.

## 🐳 Run with Docker Compose

Install Docker Desktop for Windows from the [official Docker documentation](https://docs.docker.com/desktop/setup/install/windows-install/). Start Docker Desktop and wait until it reports that Docker is running.

Verify Docker in PowerShell:

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

From the repository folder, build and start the service:

```powershell
docker compose up --build
```

Compose builds the support-assistant image, installs the consolidated requirements, enables `MOCK_LLM=1`, publishes port `7860`, and uses an OpenAPI health check. Open:

```text
http://localhost:7860/docs
```

Test the endpoint from a second PowerShell window using the same `Invoke-RestMethod` commands above. Stop and remove the container with:

```powershell
Ctrl+C
docker compose down
```

## 🧠 Design decisions

**Data engineering:** The catalogue pipeline uses `requests` and BeautifulSoup against the public Books to Scrape practice site. It uses a fixed, keyless project rate of 105.50 INR per GBP, median-imputes numeric parsing failures, and stores categories and books in a normalized SQLite schema connected by a foreign key.

**Analytics:** The Titanic dataset is loaded once and carried through a single cleaned DataFrame. EDA uses threshold-based missing-value decisions, IQR outlier analysis, Boolean-mask survival checks, an exact six-column correlation matrix, four interpreted story charts, and an EDA-only standardization check. Modeling uses a stratified split followed by training-only preprocessing in scikit-learn pipelines, then evaluates Logistic Regression, Decision Tree, and Random Forest with the requested metrics.

**Support assistant:** Ingestion is handled by `load_documents()`, embedding by `Embedder.encode()` with `all-MiniLM-L6-v2`, storage and cosine retrieval by the `zepto_policies` ChromaDB collection, routing by LangGraph's `StateGraph`, and generation by `retrieve_and_answer` or `direct_answer`. The default `MOCK_LLM=1` path is deterministic and offline. The optional real branch uses the structured prompt and validates output with Pydantic, retrying twice with corrective instructions when validation fails.

## ✅ Submission explanation

This project is one connected Zepto Data & AI Platform. First, the data pipeline collects and organizes catalogue data into a relational database. Next, the analytics pipeline uses one cleaned Titanic dataset to demonstrate profiling, visualization, classification, imbalance handling, tuning, and regression. Finally, the support assistant turns Zepto policy documents into a searchable local knowledge base and exposes grounded answers through FastAPI. The project includes automated verification, Docker Compose support, generated artifacts, and a documented Git feature-branch workflow.

Submit exactly one public repository link:

<https://github.com/gokul-ram-12/zepto-data-ai-platform>

## 🔎 Support-assistant acceptance evidence

The support-assistant requirements are satisfied by the committed corpus, source code, tests, and recorded outputs below. The eight files in `support_assistant/docs/` are loaded by `load_documents()`, embedded by `Embedder.encode()` using `all-MiniLM-L6-v2`, and stored in the `zepto_policies` ChromaDB collection with `hnsw:space=cosine`. The integration suite verifies that the live collection contains eight documents and that a delivery query returns `doc_01` content.

The actual prompt text is present in `support_assistant/main.py` under `PROMPT_TEMPLATE`. It visibly contains `Role`, `Context`, `Task`, `Format`, `Length`, the negative constraint `Do not answer using information not present in the provided context`, and a delivery-fee few-shot example. The optional `MOCK_LLM=0` path uses this prompt through `generate_real_answer()` and retries validation twice after the first attempt.

With `MOCK_LLM` unset, the keyword heuristic routes the two recorded examples as follows:

| Example query | Route | Retrieval | Expected response evidence |
|---|---|---:|---|
| `What is the delivery fee below INR 149?` | `policy_question` → `retrieve_and_answer` | Yes | Starts with `Based on the retrieved context:` and includes `doc_01` |
| `What is the weather today?` | `general_question` → `direct_answer` | No | `I can only answer questions about Zepto policies right now.` with `sources: []` |

The final full regeneration run produced this verified output:

```text
Scraped and loaded 100 books
Analytics complete: 889 cleaned rows
Support assistant ready
OpenAPI routes: ['/ask']
Ran 5 tests
OK
```

The API response examples are:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials...",
  "sources": ["doc_01", "doc_03", "doc_05"],
  "confidence": 1.0
}
```

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

The rubric states that screenshots, PDFs, presentations, video, and audio are not accepted deliverables. Therefore, verification is intentionally recorded as reproducible text, JSON examples, committed source code, reports, and automated tests rather than screenshot files. The generated analytics charts remain available as supporting artifacts and are not used as substitutes for written interpretation.

## 📚 Key files

- [Final submission summary](FINAL_SUBMISSION_SUMMARY.md)
- [Integration test suite](tests/integration_test.py)
- [Docker Compose configuration](docker-compose.yml)
- [Data pipeline documentation](data_pipeline/README.md)
- [Analytics documentation](analytics/README.md)
- [Support assistant documentation](support_assistant/README.md)
- [Verification record](VERIFICATION.md)

## References

- [Books to Scrape](http://books.toscrape.com)
- [Seaborn dataset loader](https://seaborn.pydata.org/generated/seaborn.load_dataset.html)
- [Scikit-learn](https://scikit-learn.org/stable/)
- [LangGraph](https://python.langchain.com/docs/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
