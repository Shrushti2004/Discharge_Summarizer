from rouge import Rouge
from sklearn.metrics import precision_score
from bert_score import score

rouge = Rouge()

def compute_rouge(pred, ref):
    scores = rouge.get_scores(pred, ref)
    return scores[0]["rouge-l"]["f"]

def compute_bertscore(pred, ref):
    P, R, F1 = score([pred], [ref], lang="en")
    return F1.mean().item()

def precision_at_k(retrieved, relevant, k=5):
    retrieved_k = retrieved[:k]
    hits = len(set(retrieved_k) & set(relevant))
    return hits / k