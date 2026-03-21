from datetime import datetime

from src.db.neo4j_client import run_query


def _clean_list(values):
    return [value for value in values if value]


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _calculate_length_of_stay(admittime, dischtime):
    admit_dt = _parse_datetime(admittime)
    discharge_dt = _parse_datetime(dischtime)
    if admit_dt is None or discharge_dt is None:
        return None
    stay = discharge_dt - admit_dt
    return max(stay.days, 0)


def get_patient_data(hadm_id: int):
    query = """
    MATCH (p:Patient)-[:HAS_ADMISSION]->(a:Admission {id:$hadm})
    OPTIONAL MATCH (a)-[:HAS_DIAGNOSIS]->(d:Diagnosis)
    OPTIONAL MATCH (a)-[:PRESCRIBED]->(drug:Drug)
    RETURN
        p.id AS patient_id,
        p.gender AS gender,
        a.id AS admission_id,
        a.admittime AS admittime,
        a.dischtime AS dischtime,
        collect(DISTINCT d.name) AS diagnoses,
        collect(DISTINCT drug.name) AS medications
    """

    result = run_query(query, {"hadm": int(hadm_id)})
    record = result[0] if result else None

    if record is None:
        return None

    admittime = record["admittime"]
    dischtime = record["dischtime"]
    diagnoses = _clean_list(record["diagnoses"])
    medications = _clean_list(record["medications"])

    return {
        "patient_id": record["patient_id"],
        "gender": record["gender"],
        "admission_id": record["admission_id"],
        "admittime": admittime,
        "dischtime": dischtime,
        "length_of_stay_days": _calculate_length_of_stay(admittime, dischtime),
        "diagnoses": diagnoses,
        "medications": medications,
    }
