# Discharge Summarizer (GraphRAG for Clinical Admissions)

This project builds a lightweight GraphRAG pipeline for clinical discharge summarization using:

- **Neo4j** for structured patient-admission graph data
- **Weaviate** for vector semantic retrieval over admission text
- **Groq LLM** for discharge summary generation
- **FastAPI** for a simple web interface

## Project Structure

```text
Discharge_Summarizer/
  Dockerfile             # Container image for FastAPI app
  .dockerignore
  requirements.txt
  data/
    raw/                  # Source CSV datasets
    eval/                 # Evaluation outputs
  src/
    api/                  # FastAPI app + HTML templates
    db/                   # Neo4j and Weaviate clients
    ingestion/            # KG build + vector ingestion scripts
    retrieval/            # Graph retrieval, semantic query generation, vector search, logging
    llm/                  # Groq client + summary generation
    evaluation/           # Offline RAG evaluation script
```

## Requirements

- Python 3.10+ (tested with Python 3.11)
- Running Neo4j instance
- Running Weaviate instance
- Groq API key

Python packages used by this repo:

See `requirements.txt`.

## Environment Variables

Create a `.env` file in the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
WEAVIATE_URL=http://localhost:8080
GROQ_API_KEY=your_groq_api_key
```

## Data Layout Note

Current scripts expect CSVs in nested paths like:

- `data/raw/admissions.csv/admissions.csv`
- `data/raw/patients.csv/patients.csv`

Keep this layout unless you also update paths in ingestion/evaluation scripts.

## Setup

From repository root:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

## Build the Knowledge Graph (Neo4j)

```powershell
python -m src.ingestion.build_kg
```

This loads patient/admission/diagnosis/prescription data into Neo4j.

## Ingest Vectors (Weaviate)

```powershell
python -m src.ingestion.vector_ingest
```

This creates `ClinicalDoc` schema (if missing), builds admission documents, embeds them, and writes vectors.

## Run the FastAPI App

```powershell
uvicorn src.api.main:app --reload
```

Open: `http://127.0.0.1:8000`

Enter an admission id (`hadm_id`) to view:

- structured graph data
- timeline admissions for that patient
- LLM-generated discharge summary

## Retrieval Flow (Current Codebase)

For each `hadm_id`, retrieval logic now:

1. Fetches structured data from Neo4j.
2. Uses Groq to generate a semantic clinical query (`semantic_query_generator.py`).
3. Embeds that query with `all-MiniLM-L6-v2`.
4. Runs Weaviate `near_vector` search (top 10).
5. Logs each retrieval experiment to `retrieval_logs.jsonl` (`retrieval_logger.py`).

## Evaluate Retrieval/Summary Quality

Without LLM generation:

```powershell
python -m src.evaluation.evaluate_rag --sample-size 20
```

With LLM generation + coverage metrics:

```powershell
python -m src.evaluation.evaluate_rag --sample-size 20 --run-llm
```

Output defaults to:

- `data/eval/rag_eval_results.csv`

## Run with Docker

Build image:

```powershell
docker build -t discharge-summarizer .
```

Run container:

```powershell
docker run -p 8000:8000 --env-file .env discharge-summarizer
```

Open: `http://127.0.0.1:8000`

Note: Neo4j and Weaviate are expected to run separately and be reachable from container using values in `.env`.
evalution

python src/evaluation/evaluate_rag.py
## Troubleshooting

- Neo4j auth/connection errors: verify `NEO4J_URI`, user, password.
- Weaviate query errors: verify `WEAVIATE_URL` and that schema `ClinicalDoc` exists.
- Empty retrieval results: run vector ingestion again and confirm data loaded.
- LLM errors: check `GROQ_API_KEY` and outbound network access.
- Missing `retrieval_logs.jsonl`: run at least one retrieval request through API/pipeline.



#first time run 
python -m src.ingestion.build_kg
python -m src.ingestion.vector_ingest



# 3) Start only app (neo4j + weaviate are already running)
# from project root
.\venv\Scripts\Activate.ps1

# start required services
docker compose up -d weaviate neo4j

# optional check
docker compose ps

# run app
uvicorn src.api.main:app --reload
