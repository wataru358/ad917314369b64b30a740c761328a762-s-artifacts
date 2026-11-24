"""Mechanical article-level features. No year comparisons or inference."""

from __future__ import annotations

from collections import Counter
import math
import statistics

from segmentation import comma_count, project
from t02_structure import align_structure, ProjectionError


def mattr(values, width):
    if len(values) < width:
        return None
    counts = Counter(values[:width])
    total = len(counts)
    for i in range(width, len(values)):
        outgoing, incoming = values[i - width], values[i]
        counts[outgoing] -= 1
        if not counts[outgoing]:
            del counts[outgoing]
        counts[incoming] += 1
        total += len(counts)
    return total / (width * (len(values) - width + 1))


def measure(payload):
    projection = project(payload)
    units, owners = projection["units"], projection["owners"]
    counts = {"P": 0, "L": 0, "U": 0}
    symbols = {"paragraph": "P", "list_item": "L", "text": "U"}
    token_counts = Counter()
    words = []
    for unit in units:
        token_counts.update(t["kind"] for t in unit["tokens"])
        counts[symbols[unit["kind"]]] += sum(
            t["kind"] == "word" for t in unit["tokens"]
        )
        if unit["kind"] == "paragraph":
            words.extend(
                t["value"].lower() for t in unit["tokens"] if t["kind"] == "word"
            )
    ws, wp = sum(counts.values()), counts["P"]
    paragraphs = [b for b in owners if b["kind"] == "paragraph"]
    sentence_lengths = [
        s["word_count"]
        for b in paragraphs
        for s in b["sentences"]
        if s["word_count"] > 0
    ]
    n = len(sentence_lengths)
    mu = statistics.mean(sentence_lengths) if n else None
    sigma = statistics.pstdev(sentence_lengths) if n else None
    commas = sum(comma_count(u["text"]) for u in units if u["kind"] == "paragraph")
    try:
        structure = align_structure(payload)
    except ProjectionError as error:
        structure = {
            "projection_state": "projection_error",
            "projection_error": str(error),
            "bold_intervals": None,
            "bold_words": None,
            "bold_spans": [],
            "headings": [],
        }
    values = [
        wp,
        mu,
        sigma / mu if n >= 2 else None,
        1000 * commas / wp if wp else None,
        counts["L"] / ws if ws else None,
        1000 * structure["bold_intervals"] / ws
        if ws and structure["bold_intervals"] is not None
        else None,
    ]
    reasons = [
        None,
        "no_paragraph" if not paragraphs else "no_lexical_paragraph_words",
        "too_few_sentences",
        "no_paragraph" if not paragraphs else "no_lexical_paragraph_words",
        "no_prose",
        "projection_error" if structure["projection_state"] != "ok" else "no_prose",
    ]
    denominators = [None, n, n, wp, ws, ws]
    metrics = [
        {
            "metric_id": f"M{i + 1:02}",
            "value": value,
            "denominator": denominators[i],
            "state": "ok" if value is not None else "NA",
            "reason": None if value is not None else reasons[i],
        }
        for i, value in enumerate(values)
    ]
    raw_p = "\n\n".join(u["text"] for u in units if u["kind"] == "paragraph")
    singular = {"i", "me", "my", "mine", "myself", "i'm", "i'll", "i've", "i'd"}
    plural = {"we", "us", "our", "ours", "ourselves", "we're", "we'll", "we've", "we'd"}
    paragraph_words = [
        sum(t["kind"] == "word" for t in b["tokens"]) for b in paragraphs
    ]
    adjacent = [
        abs(a["word_count"] - b["word_count"])
        for p in paragraphs
        for a, b in zip(
            [s for s in p["sentences"] if s["word_count"] > 0],
            [s for s in p["sentences"] if s["word_count"] > 0][1:],
        )
    ]
    h23 = (
        sum(h["level"] in {2, 3} for h in structure["headings"])
        if structure["projection_state"] == "ok"
        else None
    )
    heading_text = " ".join(h["text"] for h in structure["headings"])
    features = {
        "W_P": wp,
        "W_L": counts["L"],
        "W_U": counts["U"],
        "W_S": ws,
        **{m["metric_id"]: m["value"] for m in metrics},
        "M01_log1p": math.log1p(wp),
        "paragraph_count": len(paragraphs),
        "paragraph_word_median": statistics.median(paragraph_words)
        if paragraph_words
        else None,
        "paragraph_word_median_reason": None if paragraph_words else "no_paragraph",
        "sentence_count": n,
        "sentence_sd": sigma,
        "sentence_low_n": 2 <= n <= 4,
        "sentence_fragment_count": sum(
            s["fragment"] for p in paragraphs for s in p["sentences"]
        ),
        "sentence_zero_word_units": sum(
            s["word_count"] == 0 for p in paragraphs for s in p["sentences"]
        ),
        "sentence_burstiness": (sigma - mu) / (sigma + mu) if n >= 2 else None,
        "sentence_burstiness_reason": None if n >= 2 else "too_few_sentences",
        "adjacent_sentence_difference_mean": statistics.mean(adjacent)
        if adjacent
        else None,
        "adjacent_sentence_difference_reason": None
        if adjacent
        else "no_adjacent_sentence_pair",
        "comma_count_P": commas,
        "comma_interval_mean": wp / (commas + 1) if wp else None,
        "bold_interval_count_S": structure["bold_intervals"],
        "bold_word_count_S": structure["bold_words"],
        "bold_word_share_S": structure["bold_words"] / ws
        if ws and structure["bold_words"] is not None
        else None,
        "headings_h2_h3": h23,
        "heading_density": 1000 * h23 / ws if ws and h23 is not None else None,
        "heading_density_reason": None
        if ws and h23 is not None
        else ("projection_error" if h23 is None else "no_prose"),
        "has_list": payload["structural_counts"]["list_items"] > 0,
        "first_person_singular_P": sum(w in singular for w in words),
        "first_person_plural_P": sum(w in plural for w in words),
        "pronoun_ambiguous_us_count": words.count("us"),
        "MATTR_100": mattr(words, 100),
        "MATTR_100_reason": None if wp >= 100 else "insufficient_window",
        "MATTR_50": mattr(words, 50),
        "MATTR_50_reason": None if wp >= 50 else "insufficient_window",
        "em_dash_P": raw_p.count("—"),
        "en_dash_P": raw_p.count("–"),
        "double_hyphen_P": raw_p.count("--"),
        "single_hyphen_P": raw_p.replace("--", "").count("-"),
        "question_mark_P": raw_p.count("?"),
        "exclamation_mark_P": raw_p.count("!"),
        "heading_question_marks": heading_text.count("?"),
        "heading_exclamation_marks": heading_text.count("!"),
        "heading_emoji_codepoints": sum(
            0x1F000 <= ord(c) <= 0x1FAFF or 0x2600 <= ord(c) <= 0x27BF
            for c in heading_text
        ),
        "structure_projection_state": structure["projection_state"],
        "structure_projection_error": structure.get("projection_error"),
        **{
            f"token_{k}_S": token_counts[k]
            for k in ["word", "unicode_word", "number", "identifier", "url", "email"]
        },
        **{f"structural_{k}": v for k, v in payload["structural_counts"].items()},
    }
    owner_words = sum(t["kind"] == "word" for b in owners for t in b["tokens"])
    if owner_words != ws or sum(sentence_lengths) != wp:
        raise ValueError("word conservation failed")
    return features, metrics, projection, structure
