from __future__ import annotations

import re


def wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate between reference and hypothesis.

    WER = (S + D + I) / N
    where S = substitutions, D = deletions, I = insertions, N = reference word count.

    Returns a float between 0.0 (perfect) and 1.0 (all words wrong).
    """
    ref_words = _tokenize(reference)
    hyp_words = _tokenize(hypothesis)
    if not ref_words:
        return 1.0 if hyp_words else 0.0

    distance = _levenshtein(ref_words, hyp_words)
    return distance / len(ref_words)


def wer_details(reference: str, hypothesis: str) -> dict[str, int | float]:
    """Return detailed WER breakdown: substitutions, deletions, insertions, and WER."""
    ref_words = _tokenize(reference)
    hyp_words = _tokenize(hypothesis)
    if not ref_words:
        return {"substitutions": 0, "deletions": 0, "insertions": len(hyp_words), "wer": 1.0 if hyp_words else 0.0}

    s, d, i = _alignment_details(ref_words, hyp_words)
    n = len(ref_words)
    return {
        "substitutions": s,
        "deletions": d,
        "insertions": i,
        "wer": round((s + d + i) / n, 4) if n > 0 else 0.0,
    }


def compute_batch_wer(results: list[dict[str, str]]) -> dict[str, float]:
    """Compute aggregate WER over a batch of reference/hypothesis pairs.

    Each dict in `results` must have keys `reference` and `hypothesis`.
    """
    if not results:
        return {"wer": 0.0, "count": 0}
    total_errors = 0
    total_words = 0
    for item in results:
        ref = _tokenize(item["reference"])
        hyp = _tokenize(item["hypothesis"])
        if not ref:
            continue
        total_words += len(ref)
        total_errors += _levenshtein(ref, hyp)
    return {
        "wer": round(total_errors / total_words, 4) if total_words > 0 else 0.0,
        "count": len(results),
        "total_words": total_words,
        "total_errors": total_errors,
    }


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()


def _levenshtein(a: list[str], b: list[str]) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def _alignment_details(a: list[str], b: list[str]) -> tuple[int, int, int]:
    m, n = len(a), len(b)
    dp = [[(0, 0, 0)] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = (0, i, 0)
    for j in range(n + 1):
        dp[0][j] = (0, 0, j)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                sub = (dp[i - 1][j - 1][0] + 1, dp[i - 1][j - 1][1], dp[i - 1][j - 1][2])
                dele = (dp[i - 1][j][0], dp[i - 1][j][1] + 1, dp[i - 1][j][2])
                ins = (dp[i][j - 1][0], dp[i][j - 1][1], dp[i][j - 1][2] + 1)
                candidates = [sub, dele, ins]
                dp[i][j] = min(candidates, key=lambda x: x[0] + x[1] + x[2])
    return dp[m][n]
