from src.db.weaviate_client import client


def _bm25_search(query, limit=5):
    result = (
        client.query
        .get("ClinicalDoc", ["text", "hadm_id"])
        .with_bm25(query=query)
        .with_limit(limit)
        .do()
    )
    if not isinstance(result, dict) or result.get("errors"):
        return []
    return result.get("data", {}).get("Get", {}).get("ClinicalDoc") or []


def hybrid_search(query):
    result = (
        client.query
        .get("ClinicalDoc", ["text", "hadm_id"])
        .with_hybrid(query=query, alpha=0.5)
        .with_limit(5)
        .do()
    )

    if not isinstance(result, dict):
        return []
    if result.get("errors"):
        return _bm25_search(query, limit=5)
    docs = result.get("data", {}).get("Get", {}).get("ClinicalDoc") or []
    if docs:
        return docs
    return _bm25_search(query, limit=5)
