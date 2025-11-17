from .features import name_similarity, doc_keywords_overlap

def score_tool(intent: str, tool_name: str, doc: str, weights: dict) -> float:
    n = name_similarity(intent, tool_name)
    d = doc_keywords_overlap(intent, doc or '')
    h = 0.0  # history placeholder
    return (weights.get('name',0.4)*n +
            weights.get('doc',0.4)*d +
            weights.get('history',0.2)*h)
