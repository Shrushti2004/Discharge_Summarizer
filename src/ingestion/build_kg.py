import sys
import pandas as pd
from src.db.neo4j_client import run_query, verify_connection


def build_graph():

    verify_connection()

    print("Loading CSV files...")

    patients = pd.read_csv("data/raw/patients.csv/patients.csv")
    admissions = pd.read_csv("data/raw/admissions.csv/admissions.csv")
    diagnoses = pd.read_csv("data/raw/diagnoses_icd.csv/diagnoses_icd.csv")
    prescriptions = pd.read_csv("data/raw/prescriptions.csv/prescriptions.csv")

    print("Creating Patient nodes...")

    for _, row in patients.iterrows():
        run_query("""
            MERGE (p:Patient {id:$id})
            SET p.gender=$gender
        """, {
            "id": int(row["subject_id"]),
            "gender": row.get("gender", "Unknown")
        })

    print("Creating Admission nodes...")

    for _, row in admissions.iterrows():
        run_query("""
            MATCH (p:Patient {id:$sid})
            MERGE (a:Admission {id:$hadm})
            SET a.admittime = $admittime,
                a.dischtime = $dischtime
            MERGE (p)-[:HAS_ADMISSION]->(a)
        """, {
            "sid": int(row["subject_id"]),
            "hadm": int(row["hadm_id"]),
            "admittime": str(row.get("admittime", "")),
            "dischtime": str(row.get("dischtime", ""))
        })

    print("Creating Diagnosis nodes...")

    for _, row in diagnoses.iterrows():
        run_query("""
            MATCH (a:Admission {id:$hadm})
            MERGE (d:Diagnosis {name:$name})
            MERGE (a)-[:HAS_DIAGNOSIS]->(d)
        """, {
            "hadm": int(row["hadm_id"]),
            "name": row["long_title"]
        })

    print("Creating Drug nodes...")

    for _, row in prescriptions.iterrows():
        run_query("""
            MATCH (a:Admission {id:$hadm})
            MERGE (drug:Drug {name:$drug})
            MERGE (a)-[:PRESCRIBED]->(drug)
        """, {
            "hadm": int(row["hadm_id"]),
            "drug": row["drug"]
        })

    print("Knowledge Graph Built Successfully!")


if __name__ == "__main__":
    try:
        build_graph()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
