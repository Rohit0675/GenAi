# Competitive Intelligence RAG Backend

Standalone evidence layer for the AI-powered Competitive Intelligence Platform.

## Architecture

React Frontend → AI Agent → FastAPI RAG → ChromaDB

The RAG service owns source collection, extraction, cleaning, normalization, validation, deduplication, chunking, embeddings, indexing, semantic retrieval and metadata filtering. It does not perform competitive analysis.

## Real source policy

The initial source configuration contains fixed first-party URLs for Figma, Canva and Notion. It is intentionally not a broad crawler and does not invent feeds or endpoints. Source pages are treated as untrusted data.

## Folder structure

```text
rag/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── api/retrieve.py
│   ├── ingestion/
│   │   ├── sources.py
│   │   ├── fetch.py
│   │   ├── extract.py
│   │   ├── normalize.py
│   │   └── deduplicate.py
│   └── retrieval/
│       ├── embeddings.py
│       ├── vector\_store.py
│       └── search.py
├── data/raw/
├── data/processed/
├── scripts/
│   ├── ingest.py
│   └── rebuild\_index.py
├── tests/
├── chroma\_db/
├── requirements.txt
├── .env.example
└── README.md
```

## Windows setup

```powershell
cd C:\\Users\\piyus\\Documents\\AI\_Competitive\_Intelligence\\rag
py -3.14 -m venv .venv

.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

The project is currently validated with Python 3.14.7.

Ingest real sources

```powershell
python scripts/ingest.py
```

This fetches the configured official URLs, extracts content, rejects documents whose publication date cannot be reliably determined, validates the normalized schema, deduplicates, chunks, embeds and adds chunks to persistent ChromaDB. Individual source failures are reported and do not stop the remaining sources.

## Rebuild the index

```powershell
python scripts/rebuild\_index.py
```

This rebuilds the persistent Chroma collection from `data/processed/documents.json`.

## Start API

Port: **8000**

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

## Retrieve API

`POST /retrieve`

```json
{
  "query": "recent AI developments",
  "companies": \["Figma", "Canva", "Notion"],
  "date\_from": "2026-08-25",
  "date\_to": "2026-09-24",
  "category": "AI",
  "top\_k": 8
}
```

PowerShell:

```powershell
$body = @{
  query = "recent AI developments"
  companies = @("Figma", "Canva", "Notion")
  category = "AI"
  top\_k = 8
} | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/retrieve -Method Post -ContentType "application/json" -Body $body
```

## Response contract

```json
{
  "results": \[
    {
      "document\_id": "stable-id",
      "company": "Figma",
      "title": "real source title",
      "published\_date": "2026-05-20",
      "content": "real retrieved source chunk",
      "source\_url": "https://www.figma.com/blog/the-figma-agent-is-here/",
      "source\_type": "official",
      "relevance\_score": 0.82
    }
  ]
}
```

## Tests

```powershell
pytest -q
```

Mocks are used only for isolated unit tests. The runtime ingestion path uses real official sources.

## Agent integration

Team 2 should call:

`POST http://127.0.0.1:8000/retrieve`

Send the stable request schema shown above. The Agent should treat the response as evidence and perform interpretation/comparison itself. Do not connect the Agent or frontend directly to ChromaDB.

## Source limitations

* First-party pages can change markup or block automated requests; source failures are logged per URL.
* Some pages may not expose a reliably machine-readable publication date. Such pages are skipped rather than assigned a guessed date.
* Figma's release-notes page is a multi-item page; the initial adapter intentionally uses fixed individual first-party blog URLs instead of scraping the whole release-notes index.
* Source coverage is intentionally narrow for the MVP. Add new first-party URLs through `app/ingestion/sources.py` rather than introducing an uncontrolled crawler.

## Acceptance checklist

* \[x] Figma, Canva and Notion source configuration
* \[x] Real first-party fetch/extract path
* \[x] Normalized schema and validation
* \[x] Stable IDs and deduplication
* \[x] Chunking and local embeddings
* \[x] Persistent ChromaDB
* \[x] Semantic retrieval
* \[x] Company/date/category filtering
* \[x] POST /retrieve
* \[x] API validation
* \[x] Source failure isolation
* \[x] README and handoff instructions

