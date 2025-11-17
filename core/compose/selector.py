from typing import Tuple, List
from ...core.types import ParsedIntent, ToolSpec

def choose_policy(parsed: ParsedIntent, candidates: List[ToolSpec], threshold: float) -> Tuple[str, str]:
    if candidates:
        c0 = candidates[0]
        if c0.score >= threshold:
            # If top candidate is significantly better than second, select it
            if len(candidates) >= 2:
                c1 = candidates[1]
                score_gap = c0.score - c1.score
                # If top candidate is 0.2+ points better, select it directly
                # This prevents composition when there's a clear winner (e.g., workflow tool vs MCP tool)
                if score_gap >= 0.2:
                    return 'select', f'Top-1 clear winner (gap: {score_gap:.2f})'
                # If both are close and above threshold, compose
                if c1.score >= (threshold - 0.05):
                    return 'compose', 'Top-2 above threshold window; composing'
            return 'select', 'Top-1 above threshold'
        if len(candidates) >= 2 and (candidates[0].score + candidates[1].score) / 2 >= (threshold - 0.05):
            return 'compose', 'Two partial matches warrant composition'
    return 'generate', 'No suitable candidates; falling back to generator'
