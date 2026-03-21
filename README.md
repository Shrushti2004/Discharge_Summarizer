# Discharge Summarizer

Clinical GraphRAG pipeline for discharge summarization built with Neo4j, Weaviate, Groq, and FastAPI.

## What This Project Does

This project:

- loads clinical CSV data into Neo4j
- stores admission-level vector data in Weaviate
- uses Groq to generate a discharge summary
- shows the result in a FastAPI web app

## Tech Stack

- `Python`
- `FastAPI`
- `Neo4j`
- `Weaviate`
- `Groq`
- `Docker`

## Project Structure

```text
Discharge_Summarizer/
  Dockerfile
  docker-compose.yml
  requirements.txt
  .env                     # You will create this file
  data/
    raw/                   # Source CSV datasets
    eval/                  # Evaluation outputs
  src/
    api/                   # FastAPI app + templates
    db/                    # Neo4j and Weaviate clients
    ingestion/             # KG build + vector ingestion scripts
    retrieval/             # Retrieval, query generation, logging
    llm/                   # Groq client + summary generation
    evaluation/            # Offline evaluation script
```

## Before You Start

Install these first:

- `Python 3.10+` recommended: `Python 3.11`
- `Docker Desktop`
- `Neo4j desktop`
- a `Groq API key`

Also make sure you are working from the project root folder:

```powershell
cd c:\Users\Shrushti Modak\OneDrive\Desktop\Discharge_Summarizer
```

## Dataset Folder Format

Keep your CSV files inside `data/raw` in the same nested folder style already used in this repo.

Examples:

- `data/raw/admissions.csv/admissions.csv`
- `data/raw/patients.csv/patients.csv`
- `data/raw/diagnoses_icd.csv/diagnoses_icd.csv`
- `data/raw/prescriptions.csv/prescriptions.csv`

If you change this layout, the ingestion scripts may fail unless you also update the code.

## Step 1: Create Virtual Environment

Run these commands one time:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Step 2: Create `.env` File

Create a file named `.env` in the project root.

Add this exact content:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
WEAVIATE_URL=http://localhost:8080
GROQ_API_KEY=your_groq_api_key_here
```

## What Each `.env` Value Means

- `NEO4J_URI=bolt://localhost:7687`
  Use this when you run Python commands on your own machine.
- `NEO4J_USER=neo4j`
  Default username from this repo's `docker-compose.yml`.
- `NEO4J_PASSWORD=password`
  Default password from this repo's `docker-compose.yml`.
- `WEAVIATE_URL=http://localhost:8080`
  Local Weaviate URL for commands you run from PowerShell.
- `GROQ_API_KEY=...`
  Replace this with your real Groq key.

Important:

- do not keep `your_groq_api_key_here`
- replace it with your real key
- do not add quotes unless your value actually needs them

## Step 3: Start Required Services

Start Neo4j and Weaviate:

```powershell
docker compose up -d neo4j weaviate
docker compose ps
```

Expected ports:

- Neo4j Browser: `7474`
- Neo4j Bolt: `7687`
- Weaviate: `8080`

Useful links after Docker starts:

- Neo4j Browser: `http://localhost:7474`
- FastAPI app later: `http://127.0.0.1:8000`

## Step 4: Load Data Into Neo4j

Run:

```powershell
python -m src.ingestion.build_kg
```

This builds the knowledge graph from the raw CSV files.

## Step 5: Load Vector Data Into Weaviate

Run:

```powershell
python -m src.ingestion.vector_ingest
```

This:

- creates the Weaviate schema if needed
- builds admission documents
- generates embeddings
- stores vectors in Weaviate

## Step 6: Start the Web App

Run:

```powershell
uvicorn src.api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

Enter a `hadm_id` in the form to see:

- structured graph data
- admission timeline
- semantic retrieval results
- generated discharge summary

## First-Time Setup Summary

If you are running this project for the very first time, do everything in this order:

```powershell
cd c:\Users\Shrushti Modak\OneDrive\Desktop\Discharge_Summarizer
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
docker compose up -d neo4j weaviate
python -m src.ingestion.build_kg
python -m src.ingestion.vector_ingest
uvicorn src.api.main:app --reload
```

## Commands To Run Every Time

After the project has already been set up once, these are the usual commands you need each time:

```powershell
cd c:\Users\Shrushti Modak\OneDrive\Desktop\Discharge_Summarizer
.\venv\Scripts\Activate.ps1
docker compose up -d neo4j weaviate
uvicorn src.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Commands You Only Run When Data Changes

Run these again only if:

- you changed the CSV files
- you want to rebuild the graph
- you want to refresh vector data

```powershell
python -m src.ingestion.build_kg
python -m src.ingestion.vector_ingest
```

## Evaluation Commands

Run retrieval evaluation without LLM summary generation:

```powershell
python -m src.evaluation.evaluate_rag --sample-size 20
```

Run evaluation with LLM summary generation:

```powershell
python -m src.evaluation.evaluate_rag --sample-size 20 --run-llm
```

Output file:

- `data/eval/rag_eval_results.csv`

## Docker Notes

This repo's `docker-compose.yml` uses:

- Neo4j username: `neo4j`
- Neo4j password: `password`

Inside Docker, the app container talks to:

- `bolt://neo4j:7687`
- `http://weaviate:8080`

But in your local `.env` file, keep:

- `NEO4J_URI=bolt://localhost:7687`
- `WEAVIATE_URL=http://localhost:8080`

That is correct for running Python commands directly from PowerShell on your machine.

## Troubleshooting

## 1. Neo4j connection error

Check:

- `docker compose ps`
- Neo4j is running
- `.env` has the correct `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD`

Restart if needed:

```powershell
docker compose up -d neo4j
```

## 2. Weaviate connection error

Check:

- `docker compose ps`
- Weaviate is running
- `.env` has the correct `WEAVIATE_URL`

Restart if needed:

```powershell
docker compose up -d weaviate
```

## 3. Groq error

Check:

- your `GROQ_API_KEY` is present in `.env`
- the key is valid
- there are no extra spaces in the value

## 4. Empty retrieval results

Run vector ingestion again:

```powershell
python -m src.ingestion.vector_ingest
```

## 5. App opens but no useful output

Make sure:

- knowledge graph ingestion was completed
- vector ingestion was completed
- you entered a valid `hadm_id`

## Quick Command Cheat Sheet

Activate environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Start services:

```powershell
docker compose up -d neo4j weaviate
```

Build Neo4j graph:

```powershell
python -m src.ingestion.build_kg
```

Build Weaviate vectors:

```powershell
python -m src.ingestion.vector_ingest
```

Run app:

```powershell
uvicorn src.api.main:app --reload
```

Run evaluation:

```powershell
python -m src.evaluation.evaluate_rag --sample-size 20
```