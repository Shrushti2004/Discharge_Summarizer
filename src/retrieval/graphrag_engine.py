# src/retrieval/graphrag_engine.py

from src.llm.discharge_summarizer import generate_summary
from src.retrieval.graph_retrieval import get_patient_data
from src.retrieval.hybrid_search import hybrid_search

def run_graphrag(hadm_id: int):
    """
    Runs structured + semantic + LLM summarization pipeline.
    """
    # run the new hybrid semantic search
    sem_output = hybrid_search(int(hadm_id))

    # sem_output["query"] = the LLM generated query
    # sem_output["weaviate"] = Top semantically similar docs

    # Combine with structured retrieval
    structured = get_patient_data(int(hadm_id))
    if structured is None:
        raise ValueError(f"No admission found for hadm_id={hadm_id}")

    summary = generate_summary(
        {"structured": structured, "semantic": sem_output["weaviate"]}
    )

    return structured, sem_output, summary
