# src/retrieval/retrieval_logger.py

import json
from datetime import datetime

LOG_PATH = "retrieval_logs.jsonl"

def log_retrieval_experiment(hadm_id: str, semantic_query: str, weaviate_results: dict):
    """
    Append a log entry for retrieval experiments (for publication analysis).
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "hadm_id": hadm_id,
        "semantic_query": semantic_query,
        "results_count": len(weaviate_results.get("data", {}).get("Get", {}).get("ClinicalDoc", [])),
        "results": weaviate_results
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")