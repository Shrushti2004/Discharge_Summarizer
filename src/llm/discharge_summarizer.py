from src.llm.groq_client import call_groq

def generate_summary(context):

    prompt = f"""
    Generate a discharge summary using:

    Structured Data:
    {context['structured']}

    Semantic Context:
    {context['semantic']}
    """

    return call_groq(prompt)