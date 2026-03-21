from datetime import datetime

from src.db.neo4j_client import run_query


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _days_between(start_value, end_value):
    start_dt = _parse_datetime(start_value)
    end_dt = _parse_datetime(end_value)
    if start_dt is None or end_dt is None:
        return None
    return (end_dt - start_dt).days


def _build_timeline_entry(record, current_hadm_id):
    diagnoses = [value for value in record["diagnoses"] if value]
    medications = [value for value in record["medications"] if value]

    entry = {
        "admission_id": record["admission_id"],
        "admittime": record["admittime"],
        "dischtime": record["dischtime"],
        "is_current": record["admission_id"] == current_hadm_id,
        "diagnoses": diagnoses,
        "medications": medications,
        "diagnosis_count": len(diagnoses),
        "medication_count": len(medications),
    }

    stay_days = _days_between(record["admittime"], record["dischtime"])
    entry["length_of_stay_days"] = stay_days
    return entry


def get_timeline(subject_id, current_hadm_id=None):
    result = run_query(
        """
        MATCH (p:Patient {id:$id})-[:HAS_ADMISSION]->(a:Admission)
        OPTIONAL MATCH (a)-[:HAS_DIAGNOSIS]->(d:Diagnosis)
        OPTIONAL MATCH (a)-[:PRESCRIBED]->(drug:Drug)
        RETURN
            a.id AS admission_id,
            a.admittime AS admittime,
            a.dischtime AS dischtime,
            collect(DISTINCT d.name) AS diagnoses,
            collect(DISTINCT drug.name) AS medications
        """,
        {"id": subject_id},
    )

    timeline = [_build_timeline_entry(record, current_hadm_id) for record in result]
    timeline.sort(
        key=lambda entry: (
            _parse_datetime(entry["admittime"]) is None,
            _parse_datetime(entry["admittime"]) or datetime.max,
            entry["admission_id"],
        )
    )
    return timeline


def build_temporal_context(structured):
    timeline = get_timeline(structured["patient_id"], structured["admission_id"])

    current_index = next(
        (index for index, item in enumerate(timeline) if item["admission_id"] == structured["admission_id"]),
        None,
    )
    previous_admission = timeline[current_index - 1] if current_index not in (None, 0) else None

    current_diagnoses = set(structured["diagnoses"])
    current_medications = set(structured["medications"])
    previous_diagnoses = set(previous_admission["diagnoses"]) if previous_admission else set()
    previous_medications = set(previous_admission["medications"]) if previous_admission else set()

    insights = {
        "prior_admissions_count": max(len(timeline) - 1, 0),
        "days_since_last_admission": None,
        "new_diagnoses": sorted(current_diagnoses - previous_diagnoses),
        "resolved_diagnoses": sorted(previous_diagnoses - current_diagnoses),
        "continued_medications": sorted(current_medications & previous_medications),
        "new_medications": sorted(current_medications - previous_medications),
        "stopped_medications": sorted(previous_medications - current_medications),
    }

    if previous_admission:
        insights["days_since_last_admission"] = _days_between(
            previous_admission["dischtime"],
            structured["admittime"],
        )

    return {
        "timeline": timeline,
        "previous_admission": previous_admission,
        "insights": insights,
    }
