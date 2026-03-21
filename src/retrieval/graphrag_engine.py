# src/retrieval/graphrag_engine.py

from src.llm.discharge_summarizer import generate_summary
from src.retrieval.graph_retrieval import get_patient_data
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.temporal_retrieval import build_temporal_context


def run_graphrag(hadm_id: int):
    """
    Runs structured + temporal + semantic + LLM summarization pipeline.
    """
    structured = get_patient_data(int(hadm_id))
    if structured is None:
        raise ValueError(f"No admission found for hadm_id={hadm_id}")

    temporal = build_temporal_context(structured)
    sem_output = hybrid_search(int(hadm_id))

    summary = generate_summary(
        {
            "structured": structured,
            "temporal": temporal,
            "semantic": sem_output["weaviate"],
        }
    )

    return structured, temporal, sem_output, summary
