# Zepto Data & AI Platform

This repository implements the three-module capstone: a scraped catalog data pipeline, a Titanic analytics/modeling pipeline, and an offline-first Zepto policy support assistant.

## Setup

The project uses one consolidated `requirements.txt` at the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The analytics and support modules have deterministic fallbacks so their core outputs remain reproducible when external services are unavailable. The support assistant's graded path is `MOCK_LLM=1` or an unset variable.

## Run

```bash
python data_pipeline/pipeline.py
python analytics/analysis.py
MOCK_LLM=1 python support_assistant/main.py
```

To start the API:

```bash
MOCK_LLM=1 uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
curl -X POST http://localhost:7860/ask -H 'Content-Type: application/json' -d '{"query":"How much is delivery?"}'
```

See the module READMEs for the generated outputs, example calls, and implementation decisions.

## Design decisions

The data pipeline uses requests and BeautifulSoup for reproducible scraping, a fixed project-defined GBP/INR rate, and a normalized SQLite schema with categories and books tables. The analytics pipeline preserves one cleaned Titanic dataset across EDA, classification, imbalance analysis, tuning, and regression. The support assistant uses local embeddings and ChromaDB retrieval, while LangGraph routes policy and general questions; mock generation is deterministic and requires no paid service or API key.

## References

[1]: http://books.toscrape.com "Books to Scrape public scraping-practice site"
[2]: https://seaborn.pydata.org/generated/seaborn.load_dataset.html "Seaborn dataset loader"
[3]: https://scikit-learn.org/stable/ "Scikit-learn documentation"
[4]: https://python.langchain.com/docs/langgraph/ "LangGraph documentation"
[5]: https://fastapi.tiangolo.com/ "FastAPI documentation"
