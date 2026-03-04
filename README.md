# Discharge Summarizer (GraphRAG for Clinical Admissions)

This project builds a lightweight GraphRAG pipeline for clinical discharge summarization using:

- **Neo4j** for structured patient-admission graph data
- **Weaviate** for vector + hybrid retrieval over admission text
- **Groq LLM** for discharge summary generation
- **FastAPI** for a simple web interface

## Project Structure

```text
Discharge_Summarizer/
  data/
    raw/                  # Source CSV datasets
    eval/                 # Evaluation outputs
  src/
    api/                  # FastAPI app + HTML templates
    db/                   # Neo4j and Weaviate clients
    ingestion/            # KG build + vector ingestion scripts
    retrieval/            # Graph, hybrid, and timeline retrieval
    llm/                  # Groq client + summary generation
    evaluation/           # Offline RAG evaluation script
```

## Requirements

- Python 3.10+ (tested with Python 3.11)
- Running Neo4j instance
- Running Weaviate instance
- Groq API key

Python packages used by this repo:

- `fastapi`
- `uvicorn`
- `jinja2`
- `python-multipart`
- `pandas`
- `python-dotenv`
- `neo4j`
- `weaviate-client`
- `sentence-transformers`
- `groq`

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
pip install fastapi uvicorn jinja2 python-multipart pandas python-dotenv neo4j weaviate-client sentence-transformers groq
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

## Troubleshooting

- Neo4j auth/connection errors: verify `NEO4J_URI`, user, password.
- Weaviate query errors: verify `WEAVIATE_URL` and that schema `ClinicalDoc` exists.
- Empty retrieval results: run vector ingestion again and confirm data loaded.
- LLM errors: check `GROQ_API_KEY` and outbound network access.

