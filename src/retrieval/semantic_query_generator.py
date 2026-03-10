# src/retrieval/semantic_query_generator.py

from src.llm.groq_client import call_groq

def generate_semantic_query(structured_data: dict) -> str:
    """
    Given structured patient data (from the graph),
    generate a natural language clinical retrieval query.
    """

    prompt = f"""
    You are a clinical AI assistant.

    Convert the structured electronic health record information below
    into a concise clinical retrieval query sentence that summarizes
    the patient's main conditions, procedures, medications, and labs:

    Diagnoses: {structured_data.get('diagnoses')}
    Medications: {structured_data.get('medications')}
    Labs: {structured_data.get('labs')}
    Procedures: {structured_data.get('procedures')}

    Output only the final query (one paragraph).
    """

    # call_groq uses your existing Groq client wrapper
    query_text = call_groq(prompt)
    return query_text.strip()