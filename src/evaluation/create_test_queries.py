import json
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "raw"
OUT_PATH = Path(__file__).with_name("test_queries.json")

diagnoses = pd.read_csv(DATA_DIR / "diagnoses_icd.csv" / "diagnoses_icd.csv")
prescriptions = pd.read_csv(DATA_DIR / "prescriptions.csv" / "prescriptions.csv")

test_queries = []

hadm_ids = diagnoses["hadm_id"].unique()[:50]  # choose 50 samples

for hadm in hadm_ids:
    diag = diagnoses[diagnoses["hadm_id"] == hadm]["long_title"].tolist()
    drugs = prescriptions[prescriptions["hadm_id"] == hadm]["drug"].tolist()

    ground_truth = ", ".join(diag + drugs)

    test_queries.append({"hadm_id": str(hadm), "expected_summary": ground_truth})

with OUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(test_queries, f, indent=2)

print(f"Test queries generated at: {OUT_PATH}")
