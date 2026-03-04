from src.retrieval.graph_retrieval import get_patient_data
from src.retrieval.hybrid_search import hybrid_search
from src.llm.discharge_summarizer import generate_summary

def run_graphrag(hadm_id):

    structured = get_patient_data(hadm_id)
    semantic = hybrid_search(f"admission {hadm_id}")

    summary = generate_summary({
        "structured": structured,
        "semantic": semantic
    })

    return structured, semantic, summary