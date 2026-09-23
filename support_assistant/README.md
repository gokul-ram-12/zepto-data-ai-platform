# Support Assistant

Run the deterministic graded baseline from the repository root with:

```bash
MOCK_LLM=1 python support_assistant/main.py
MOCK_LLM=1 uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

The service loads all eight policy files in `docs/`, embeds them with `all-MiniLM-L6-v2`, and stores them in the `zepto_policies` ChromaDB collection. If the embedding model is unavailable, the code uses a deterministic local development fallback so that routing and API behavior remain testable; the declared production embedding is still `all-MiniLM-L6-v2`.

## Architecture

**Ingestion:** `load_documents()` reads `doc_01.txt` through `doc_08.txt` and treats each document as one chunk.  
**Embedding:** `Embedder.encode()` uses Sentence Transformers and the `all-MiniLM-L6-v2` model.  
**Storage and retrieval:** `Retriever` upserts the vectors and documents into the persistent `zepto_policies` ChromaDB collection. `Retriever.search()` embeds the incoming query and retrieves the top three chunks by cosine similarity.  
**Generation:** LangGraph's `classify_intent` node routes policy questions to `retrieve_and_answer` and unrelated questions to `direct_answer`. The mock path creates a deterministic answer from the top retrieved chunk or a fixed general-question response. The final FastAPI response is validated by the `AskResponse` Pydantic model.

Only generation branches on `MOCK_LLM`. Retrieval runs in both modes. With `MOCK_LLM` unset or set to `1`, no LLM network call occurs. `MOCK_LLM=0` is intentionally an explicit extension point that raises a clear configuration error until a real provider is supplied.

## Example calls

Policy query:

```bash
curl -X POST http://localhost:7860/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the delivery fee below INR 149?"}'
```

Example response shape:

```json
{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials...","sources":["doc_01","doc_05","doc_04"],"confidence":1.0}
```

General query:

```bash
curl -X POST http://localhost:7860/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the weather today?"}'
```

Expected response:

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

## Docker

From the repository root:

```bash
docker build -f support_assistant/Dockerfile -t zepto-support .
docker run --rm -p 7860:7860 -e MOCK_LLM=1 zepto-support
```

## References

[1]: https://www.sbert.net/ "Sentence Transformers documentation"
[2]: https://docs.trychroma.com/ "ChromaDB documentation"
[3]: https://python.langchain.com/docs/langgraph/ "LangGraph documentation"
[4]: https://fastapi.tiangolo.com/ "FastAPI documentation"
