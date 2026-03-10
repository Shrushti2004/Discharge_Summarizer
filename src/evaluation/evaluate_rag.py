import argparse
import json
from pathlib import Path

from src.evaluation.metrics import compute_bertscore, compute_rouge
from src.retrieval.graphrag_engine import run_graphrag

TEST_QUERIES_PATH = Path(__file__).with_name("test_queries.json")


def evaluate(sample_size: int | None = None):
    with TEST_QUERIES_PATH.open("r", encoding="utf-8") as f:
        test_data = json.load(f)

    if sample_size is not None:
        test_data = test_data[:sample_size]

    results = []
    for item in test_data:
        hadm_id = item["hadm_id"]
        expected_summary = item["expected_summary"]

        _, _, generated_summary = run_graphrag(hadm_id)

        rouge_score = compute_rouge(generated_summary, expected_summary)
        bert_score = compute_bertscore(generated_summary, expected_summary)

        results.append(
            {
                "hadm_id": hadm_id,
                "rouge": rouge_score,
                "bert": bert_score,
            }
        )

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-size", type=int, default=None)
    args = parser.parse_args()

    print(json.dumps(evaluate(sample_size=args.sample_size), indent=2))


if __name__ == "__main__":
    main()
