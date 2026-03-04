import argparse
import random
import re
from pathlib import Path

import pandas as pd

from src.llm.discharge_summarizer import generate_summary
from src.retrieval.graph_retrieval import get_patient_data
from src.retrieval.hybrid_search import hybrid_search


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def phrase_coverage(phrases: list[str], summary: str, max_items: int = 10) -> float:
    if not phrases or not summary:
        return 0.0
    unique_phrases = []
    seen = set()
    for phrase in phrases:
        p = normalize_text(phrase)
        if p and p not in seen:
            seen.add(p)
            unique_phrases.append(p)
        if len(unique_phrases) >= max_items:
            break

    if not unique_phrases:
        return 0.0

    summary_norm = normalize_text(summary)
    hits = sum(1 for p in unique_phrases if p in summary_norm)
    return hits / len(unique_phrases)


def evaluate_one(hadm_id: int, run_llm: bool) -> dict:
    row = {
        "hadm_id": int(hadm_id),
        "graph_found": 0,
        "semantic_nonempty": 0,
        "semantic_hit_at_5": 0,
        "summary_generated": 0,
        "diag_coverage": 0.0,
        "med_coverage": 0.0,
        "error": "",
    }

    try:
        structured = get_patient_data(int(hadm_id))
        semantic = hybrid_search(f"admission {hadm_id}")

        row["graph_found"] = int(structured is not None)
        row["semantic_nonempty"] = int(bool(semantic))

        returned_ids = [
            int(doc.get("hadm_id"))
            for doc in semantic
            if isinstance(doc, dict) and doc.get("hadm_id") is not None
        ]
        row["semantic_hit_at_5"] = int(int(hadm_id) in returned_ids)

        if run_llm and structured is not None:
            summary = generate_summary({"structured": structured, "semantic": semantic})
            row["summary_generated"] = int(bool(summary and str(summary).strip()))
            row["diag_coverage"] = phrase_coverage(structured.get("diagnoses", []), summary)
            row["med_coverage"] = phrase_coverage(structured.get("medications", []), summary)

        return row
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
        return row


def get_sample_ids(sample_size: int, seed: int) -> list[int]:
    diagnoses_path = Path("data/raw/diagnoses_icd.csv/diagnoses_icd.csv")
    df = pd.read_csv(diagnoses_path, usecols=["hadm_id"])
    ids = df["hadm_id"].dropna().astype(int).unique().tolist()
    if not ids:
        return []
    if sample_size >= len(ids):
        return ids
    rnd = random.Random(seed)
    return rnd.sample(ids, sample_size)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate GraphRAG quality on admissions.")
    parser.add_argument("--sample-size", type=int, default=20, help="Number of admissions to evaluate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling admissions.")
    parser.add_argument(
        "--hadm-ids",
        nargs="*",
        type=int,
        default=None,
        help="Optional explicit hadm_ids. If provided, sampling is skipped.",
    )
    parser.add_argument(
        "--run-llm",
        action="store_true",
        help="Generate summaries and evaluate coverage (costs tokens).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/eval/rag_eval_results.csv",
        help="Path to save per-admission metrics CSV.",
    )
    args = parser.parse_args()

    hadm_ids = args.hadm_ids if args.hadm_ids else get_sample_ids(args.sample_size, args.seed)
    if not hadm_ids:
        print("No hadm_ids found for evaluation.")
        return

    print(f"Evaluating {len(hadm_ids)} admissions (run_llm={args.run_llm})...")
    rows = [evaluate_one(hid, run_llm=args.run_llm) for hid in hadm_ids]
    out_df = pd.DataFrame(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    total = len(out_df)
    error_count = int((out_df["error"] != "").sum())
    print("\n=== RAG Evaluation Summary ===")
    print(f"Total cases: {total}")
    print(f"Errors: {error_count}")
    print(f"Graph found rate: {out_df['graph_found'].mean():.3f}")
    print(f"Semantic non-empty rate: {out_df['semantic_nonempty'].mean():.3f}")
    print(f"Semantic hit@5: {out_df['semantic_hit_at_5'].mean():.3f}")
    if args.run_llm:
        print(f"Summary generated rate: {out_df['summary_generated'].mean():.3f}")
        print(f"Diagnosis coverage (avg): {out_df['diag_coverage'].mean():.3f}")
        print(f"Medication coverage (avg): {out_df['med_coverage'].mean():.3f}")
    print(f"Saved detailed results to: {output_path}")


if __name__ == "__main__":
    main()
