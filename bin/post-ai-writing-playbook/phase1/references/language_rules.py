def scores(detector, text):
    values = detector.compute_language_confidence_values(text)
    if not values:
        return {"top": None, "value": 0.0, "gap": 0.0, "top3": []}
    top = [
        {"language": v.language.iso_code_639_1.name.lower(), "value": v.value}
        for v in values[:3]
    ]
    return {
        "top": top[0]["language"],
        "value": top[0]["value"],
        "gap": top[0]["value"] - top[1]["value"],
        "top3": top,
    }


def segment_spans(text, size=1200):
    # Cover every character; no article length cutoff. Offsets refer to original S.
    return [(i, min(i + size, len(text))) for i in range(0, len(text), size)]


def evidence(detector, row):
    text = row["prose_text"]
    result = {
        "article_id": row["article_id"],
        "input_sha256": row["prose_sha256"],
        "input_part": "S (prose_text)",
        "input_chars": len(text or ""),
        "source_state": row["extraction_status"],
        "s": None,
        "p": None,
        "l": None,
        "segments": [],
    }
    if text:
        result["s"] = scores(detector, text)
        payload = row["payload"]
        for kind, part in [("paragraph", "p"), ("list_item", "l")]:
            part_text = " ".join(
                u["text"] for u in payload["prose_units"] if u["kind"] == kind
            )
            if part_text:
                result[part] = scores(detector, part_text)
        for start, end in segment_spans(text):
            result["segments"].append(
                {"start": start, "end": end, **scores(detector, text[start:end])}
            )
    return result


def classify(ev, rules):
    if ev["source_state"] != "ok":
        return "unavailable", "acquisition_or_body_unavailable", False
    if not ev["input_chars"]:
        return "empty", "no_prose_S", False
    score = ev["s"]
    confident = (
        lambda v: v
        and v["value"] >= rules["minimum_top_score"]
        and v["gap"] >= rules["minimum_score_gap"]
    )
    langs = {s["top"] for s in ev["segments"] if confident(s)}
    parts = {ev[k]["top"] for k in ("p", "l") if confident(ev[k])}
    if "en" in langs | parts and (langs | parts) - {"en"}:
        return "mixed", "confident_S_segment_or_P_L_disagreement", score["top"] == "en"
    if not confident(score):
        return "unknown", "insufficient_score_separation", False
    if score["top"] == "en":
        if (langs | parts) - {"en"}:
            return "mixed", "English_S_with_confident_nonEnglish_part", True
        return "english", "confident_English_S", False
    if "en" in langs | parts:
        return "mixed", "nonEnglish_S_with_confident_English_part", False
    return "non_english", "confident_nonEnglish_S", False

