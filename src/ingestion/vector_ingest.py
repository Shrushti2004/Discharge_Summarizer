import pandas as pd
import uuid
from sentence_transformers import SentenceTransformer
from src.db.weaviate_client import create_schema, get_client


model = SentenceTransformer("all-MiniLM-L6-v2")


def make_doc_uuid(hadm_id: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"clinicaldoc:{hadm_id}"))


def ingest():

    print("Creating schema in Weaviate...")
    create_schema()

    print("Loading CSV files...")

    diagnoses = pd.read_csv("data/raw/diagnoses_icd.csv/diagnoses_icd.csv")
    prescriptions = pd.read_csv("data/raw/prescriptions.csv/prescriptions.csv")
    admissions = pd.read_csv("data/raw/admissions.csv/admissions.csv")

    print("Grouping data by admission...")

    # Group diagnoses per admission
    diag_group = diagnoses.groupby("hadm_id")["long_title"].apply(list)

    # Group drugs per admission
    drug_group = prescriptions.groupby("hadm_id")["drug"].apply(list)

    for hadm_id in diag_group.index:
        hadm_id = int(hadm_id)

        diagnoses_list = diag_group.get(hadm_id, [])
        drugs_list = drug_group.get(hadm_id, [])

        # Build clinical document
        text = f"""
        Admission ID: {hadm_id}

        Diagnoses:
        {'; '.join(diagnoses_list)}

        Medications:
        {'; '.join(drugs_list)}
        """

        vector = model.encode(text).tolist()

        # Idempotent write: remove any previous objects for this admission first.
        get_client().batch.delete_objects(
            class_name="ClinicalDoc",
            where={
                "path": ["hadm_id"],
                "operator": "Equal",
                "valueInt": hadm_id,
            },
        )

        get_client().data_object.create(
            {
                "text": text,
                "hadm_id": hadm_id
            },
            "ClinicalDoc",
            uuid=make_doc_uuid(hadm_id),
            vector=vector
        )

        print(f"Ingested admission {hadm_id}")

    print("Vector ingestion completed!")


if __name__ == "__main__":
    ingest()
