from difflib import SequenceMatcher
import re

def name_similarity(intent: str, tool_name: str) -> float:
    a = intent.lower()
    b = tool_name.lower().replace('.py','')
    return SequenceMatcher(None, a, b).ratio()

def doc_keywords_overlap(intent: str, doc: str) -> float:
    def tokens(s):
        return set(re.findall(r'[a-zA-Z]{3,}', s.lower()))
    i = tokens(intent)
    d = tokens(doc or '')
    if not i or not d:
        return 0.0
    return len(i & d) / len(i | d)
