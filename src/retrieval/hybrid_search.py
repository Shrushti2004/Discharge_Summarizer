# src/retrieval/hybrid_search.py

from src.db.weaviate_client import get_client
from src.retrieval.graph_retrieval import get_patient_data
from src.retrieval.semantic_query_generator import generate_semantic_query
from src.retrieval.retrieval_logger import log_retrieval_experiment
from sentence_transformers import SentenceTransformer

model = None


def get_embedding_model() -> SentenceTransformer:
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def hybrid_search(hadm_id: int) -> dict:
    """
    Retrieves semantically relevant clinical vectors from Weaviate
    by turning structured graph into an LLM-generated query + embedding.
    """

    # 1️⃣ Get structured data from Neo4j
    structured = get_patient_data(int(hadm_id))
    if structured is None:
        return {"query": "", "weaviate": {"data": {"Get": {"ClinicalDoc": []}}}}

    # 2️⃣ Generate clinical semantic text query via LLM
    semantic_query = generate_semantic_query(structured)

    # 3️⃣ Compute embedding
    query_vec = get_embedding_model().encode(semantic_query).tolist()

    # 4️⃣ Perform Weaviate semantic similarity search
    result = (
        get_client().query
        .get("ClinicalDoc", ["text", "hadm_id"])
        .with_near_vector({"vector": query_vec})
        .with_limit(10)  # top K
        .do()
    )

    # 5️⃣ Log for research analysis
    log_retrieval_experiment(hadm_id, semantic_query, result)

    return {
        "query": semantic_query,
        "weaviate": result
    }
