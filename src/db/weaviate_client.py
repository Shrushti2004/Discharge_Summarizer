import weaviate
from src.config import WEAVIATE_URL

client = None


def get_client():
    global client
    if client is None:
        if not WEAVIATE_URL:
            raise ValueError("Missing Weaviate config. Set WEAVIATE_URL.")
        client = weaviate.Client(WEAVIATE_URL)
    return client

def create_schema():
    schema = {
        "class": "ClinicalDoc",
        "vectorizer": "none",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "hadm_id", "dataType": ["int"]}
        ]
    }

    weaviate_client = get_client()
    if not weaviate_client.schema.exists("ClinicalDoc"):
        weaviate_client.schema.create_class(schema)
