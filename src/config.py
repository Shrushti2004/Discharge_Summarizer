import os
from dotenv import load_dotenv

load_dotenv(override=True)


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")