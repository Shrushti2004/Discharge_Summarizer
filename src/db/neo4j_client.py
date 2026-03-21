import atexit
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

driver = None


def get_driver():
    global driver
    if driver is None:
        if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
            raise ValueError("Missing Neo4j config. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD.")
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
        )
    return driver


@atexit.register
def close_driver():
    if driver is not None:
        driver.close()


def verify_connection():
    try:
        get_driver().verify_connectivity()
    except (ServiceUnavailable, Neo4jError) as exc:
        raise RuntimeError(
            "Unable to connect to Neo4j. Start the Neo4j service and verify "
            "NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD in .env."
        ) from exc


def run_query(query, params=None):
    with get_driver().session() as session:
        # Materialize rows before session closes to avoid ResultConsumedError.
        return list(session.run(query, params or {}))
