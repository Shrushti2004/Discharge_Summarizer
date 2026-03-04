from src.db.neo4j_client import run_query

def get_timeline(subject_id):
    result = run_query("""
        MATCH (p:Patient {id:$id})-[:HAS_ADMISSION]->(a)
        RETURN a.id AS admission
        ORDER BY a.id
    """, {"id": subject_id})

    return [r["admission"] for r in result]