#!/usr/bin/env python3
"""Offline synthetic example. This is not the corpus extractor or a study result."""
import json
import math
from pathlib import Path
import statistics
import sys


if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required. Select python3.11 or a newer interpreter.")

def measure(row):
    paragraphs = row["paragraph_sentence_lengths"]
    lengths = [length for paragraph in paragraphs for length in paragraph]
    numbers = lengths + [row[k] for k in ("list_words", "other_words", "commas", "bold_pl", "bold_s")]
    if any(type(value) is not int or value < 0 for value in numbers) or any(n == 0 for n in lengths):
        raise ValueError("counts must be nonnegative integers; sentence lengths must be positive")
    p, l, u = sum(lengths), row["list_words"], row["other_words"]
    s, base, n = p + l + u, p + l, len(lengths)
    mean = p / n if n else None
    return {
        "example_only": True,
        "article_key": row["article_key"],
        "phase1_subset": {
            "M01_log1p_P": math.log1p(p),
            "M04_commas_per_1000_P": 1000 * row["commas"] / p if p else None,
            "M05_list_share_S": l / s if s else None,
            "M06_bold_per_1000_S": 1000 * row["bold_s"] / s if s else None,
        },
        "phase2": {
            "P2-M01": mean,
            "P2-M02": statistics.pstdev(lengths) / mean if n >= 2 else None,
            "P2-M03": row["commas"] / n if n else None,
            "P2-M04": p,
            "P2-M05": l / base if base else None,
            "P2-M06": 1000 * row["bold_pl"] / base if base else None,
        },
    }


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).with_name("example-input.jsonl")
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.strip():
            print(json.dumps(measure(json.loads(line)), ensure_ascii=False))
