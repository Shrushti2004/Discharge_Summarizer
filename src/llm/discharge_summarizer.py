from src.llm.groq_client import call_groq


SECTION_TITLES = [
    "Admission Overview",
    "Clinical Snapshot",
    "Diagnoses",
    "Medications",
    "Supporting Retrieval Context",
    "Discharge Considerations",
]


def _extract_semantic_docs(semantic_context):
    try:
        return semantic_context["data"]["Get"]["ClinicalDoc"]
    except (KeyError, TypeError):
        return []


def _build_supporting_context(documents, limit=3):
    snippets = []
    for doc in documents[:limit]:
        text = str(doc.get("text", "")).strip()
        if not text:
            continue
        snippets.append(
            {
                "hadm_id": doc.get("hadm_id"),
                "text": text[:400],
            }
        )
    return snippets


def _build_fallback_sections(context):
    structured = context["structured"]
    supporting_docs = _build_supporting_context(_extract_semantic_docs(context["semantic"]))

    overview = [
        f"Patient {structured['patient_id']} with admission {structured['admission_id']}.",
    ]
    if structured.get("admittime"):
        overview.append(f"Admitted on {structured['admittime']}.")
    if structured.get("dischtime"):
        overview.append(f"Discharged on {structured['dischtime']}.")
    if structured.get("length_of_stay_days") is not None:
        overview.append(f"Length of stay was {structured['length_of_stay_days']} day(s).")

    clinical_course = [
        f"This encounter includes {len(structured['diagnoses'])} diagnosis entries and {len(structured['medications'])} medication entries."
    ]

    diagnoses = structured["diagnoses"] or ["No diagnoses recorded."]
    medications = structured["medications"] or ["No medications recorded."]

    retrieval_lines = [
        f"Semantic query: {context['semantic'].get('query') or 'Not available.'}"
    ]
    if supporting_docs:
        retrieval_lines.extend(
            [
                f"Related admission {doc['hadm_id']}: {doc['text']}"
                for doc in supporting_docs
            ]
        )
    else:
        retrieval_lines.append("No related retrieval context was returned.")

    discharge_lines = [
        "Review the active diagnoses, medication list, and retrieved clinical context before finalizing discharge communication."
    ]

    sections = [
        {"title": "Admission Overview", "content": " ".join(overview)},
        {"title": "Clinical Snapshot", "content": " ".join(clinical_course)},
        {"title": "Diagnoses", "content": ", ".join(diagnoses)},
        {"title": "Medications", "content": ", ".join(medications)},
        {"title": "Supporting Retrieval Context", "content": " ".join(retrieval_lines)},
        {"title": "Discharge Considerations", "content": " ".join(discharge_lines)},
    ]
    return sections


def _parse_sections(summary_text, fallback_sections):
    parsed_sections = []
    current_title = None
    current_lines = []

    for raw_line in summary_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matched_title = next(
            (title for title in SECTION_TITLES if line.lower().startswith(title.lower())),
            None,
        )
        if matched_title:
            if current_title:
                parsed_sections.append(
                    {"title": current_title, "content": " ".join(current_lines).strip()}
                )
            current_title = matched_title
            remainder = line[len(matched_title):].lstrip(":- ").strip()
            current_lines = [remainder] if remainder else []
            continue

        if current_title:
            current_lines.append(line)

    if current_title:
        parsed_sections.append({"title": current_title, "content": " ".join(current_lines).strip()})

    if len(parsed_sections) >= 4:
        return parsed_sections
    return fallback_sections


def generate_summary(context):
    fallback_sections = _build_fallback_sections(context)
    prompt = f"""
You are a clinical AI assistant.

Create a concise discharge summary using the exact section headings below.
Keep the summary grounded only in the provided data and avoid inventing details.
Focus on the current admission only.
Do not include temporal comparisons, prior-admission comparisons, or readmission-gap commentary.
Keep each section brief and direct.

Required headings:
- Admission Overview
- Clinical Snapshot
- Diagnoses
- Medications
- Supporting Retrieval Context
- Discharge Considerations

Structured Data:
{context['structured']}

Semantic Context:
{context['semantic']}
"""

    raw_text = call_groq(prompt).strip()
    sections = _parse_sections(raw_text, fallback_sections)

    return {
      "raw_text": raw_text,
      "sections": sections,
    }
