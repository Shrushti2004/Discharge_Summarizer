import atexit
from neo4j import GraphDatabase
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

@atexit.register
def close_driver():
    if driver is not None:
        driver.close()

def run_query(query, params=None):
    with driver.session() as session:
        # Materialize rows before session closes to avoid ResultConsumedError.
        return list(session.run(query, params or {}))
