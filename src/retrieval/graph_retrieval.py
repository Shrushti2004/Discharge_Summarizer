from src.db.neo4j_client import driver


def get_patient_data(hadm_id: int):

    query = """
    MATCH (p:Patient)-[:HAS_ADMISSION]->(a:Admission {id:$hadm})
    OPTIONAL MATCH (a)-[:HAS_DIAGNOSIS]->(d:Diagnosis)
    OPTIONAL MATCH (a)-[:PRESCRIBED]->(drug:Drug)
    RETURN 
        p.id AS patient_id,
        p.gender AS gender,
        a.id AS admission_id,
        collect(DISTINCT d.name) AS diagnoses,
        collect(DISTINCT drug.name) AS medications
    """

    with driver.session() as session:
        result = session.run(query, {"hadm": hadm_id})
        record = result.single()

    if record:
        return {
            "patient_id": record["patient_id"],
            "gender": record["gender"],
            "admission_id": record["admission_id"],
            "diagnoses": record["diagnoses"],
            "medications": record["medications"]
        }

    return None