import re
from typing import NamedTuple


class TaskClassification(NamedTuple):
    task_type: str
    confidence: float


# Keyword and pattern rules for fast, deterministic task classification
PATTERNS = {
    "classification": [
        r"\b(classify|categorize|sentiment|label|tag|positive\b.*\bnegative|is this|rate this)\b",
        r"\b(class:|category:|sentiment:)\b",
    ],
    "extraction": [
        r"\b(extract|parse|pull out|convert to json|json schema|in json format|entities|structured data)\b",
        r"\b(return only json|output json|fields:)\b",
    ],
    "summarization": [
        r"\b(summarize|summary|tldr|tl;dr|briefly explain|condense|digest|short overview|key points)\b",
        r"\b(in \d+ sentences|in a nutshell|executive summary)\b",
    ],
    "code": [
        r"\b(write a python|write a function|implement|refactor|debug|code|javascript|typescript|sql query)\b",
        r"\b(class\s+\w+|def\s+\w+|function\s+\w+|```python|```javascript|```sql)\b",
    ],
    "math": [
        r"\b(calculate|compute|solve for|equation|formula|math|integral|derivative|algebra|arithmetic)\b",
        r"[\d\s\+\-\*\/\^\=]{7,}",
    ],
    "reasoning": [
        r"\b(analyze|critique|evaluate the implications|pros and cons|trade-offs|step by step|compare and contrast)\b",
        r"\b(why does|what are the consequences|philosophical|implications of)\b",
    ],
}


def classify_task(prompt_text: str) -> TaskClassification:
    """
    Classifies prompt text into a task category (e.g. classification, extraction,
    summarization, code, math, reasoning, conversational).
    """
    text_lower = prompt_text.lower()
    scores: dict[str, float] = {k: 0.0 for k in PATTERNS}

    for task_type, pattern_list in PATTERNS.items():
        for pat in pattern_list:
            matches = len(re.findall(pat, text_lower))
            if matches > 0:
                scores[task_type] += matches * 1.5

    best_task = max(scores, key=scores.get)
    best_score = scores[best_task]

    if best_score == 0.0:
        # Default fallback
        if len(prompt_text.split()) < 15:
            return TaskClassification(task_type="conversational", confidence=0.7)
        return TaskClassification(task_type="conversational", confidence=0.5)

    confidence = min(0.95, 0.5 + (best_score * 0.15))
    return TaskClassification(task_type=best_task, confidence=round(confidence, 2))
