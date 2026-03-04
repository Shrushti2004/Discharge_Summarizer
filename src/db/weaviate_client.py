import weaviate
from src.config import WEAVIATE_URL

client = weaviate.Client(WEAVIATE_URL)

def create_schema():
    schema = {
        "class": "ClinicalDoc",
        "vectorizer": "none",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "hadm_id", "dataType": ["int"]}
        ]
    }

    if not client.schema.exists("ClinicalDoc"):
        client.schema.create_class(schema)