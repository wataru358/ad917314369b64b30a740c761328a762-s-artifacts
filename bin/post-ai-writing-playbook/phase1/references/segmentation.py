import re

def owners(payload):
    """Merge fragments of each source owner, preserving first-occurrence order."""
    groups = {}
    for index, unit in enumerate(payload["prose_units"]):
        key = (unit["kind"], unit["source_path"])
        if key not in groups:
            groups[key] = {
                "kind": key[0],
                "source_path": key[1],
                "unit_indices": [],
                "text": "",
            }
        group = groups[key]
        group["unit_indices"].append(index)
        group["text"] += (" " if group["text"] else "") + unit["text"]
    return list(groups.values())


URL = re.compile(r"(?:https?://|www\.)[^\s<>\"']+", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
LEXEME = re.compile(r"\w+(?:['’\-]\w+)*(?:\.\w+(?:['’\-]\w+)*)*", re.UNICODE)
ASCII_WORD = re.compile(r"[A-Za-z]+(?:['\-][A-Za-z]+)*\Z")
NUMBER = re.compile(r"\d+(?:[.,]\d+)*\Z")
NUMBER_SCAN = re.compile(r"(?<![\w.\-])\d+(?:[.,]\d+)*(?![\w\-])")
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "e.g", "i.e"}


def protected_spans(text):
    spans = []
    for kind, pattern in [("url", URL), ("email", EMAIL)]:
        for match in pattern.finditer(text):
            end = match.end()
            if kind == "url":
                while end > match.start() and text[end - 1] in ".,;:!?)]}":
                    end -= 1
            if not any(a <= match.start() < b for a, b, _ in spans):
                spans.append((match.start(), end, kind))
    return sorted(spans)


def tokens(text):
    """Original-text offsets; normalize curly apostrophes only in token values."""
    result = [
        {"start": a, "end": b, "kind": kind, "value": text[a:b]}
        for a, b, kind in protected_spans(text)
    ]
    covered = [(t["start"], t["end"]) for t in result]
    for match in NUMBER_SCAN.finditer(text):
        if not any(match.start() < b and match.end() > a for a, b in covered):
            result.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "kind": "number",
                    "value": match.group(),
                }
            )
            covered.append(match.span())
    for match in LEXEME.finditer(text):
        if any(match.start() < b and match.end() > a for a, b in covered):
            continue
        raw = match.group()
        normalized = raw.replace("’", "'")
        if NUMBER.fullmatch(normalized):
            kind = "number"
        elif any(c.isdigit() for c in normalized) or "_" in normalized:
            kind = "identifier"
        elif any(ord(c) > 127 for c in normalized):
            kind = "unicode_word"
        else:
            # Pure alphabetic dotted forms are separate words (Node.js, e.g.).
            for sub in re.finditer(r"[^.]+", normalized):
                value = sub.group()
                if not ASCII_WORD.fullmatch(value):
                    raise RuntimeError(f"unclassified lexical token: {value}")
                start = match.start() + sub.start()
                result.append(
                    {
                        "start": start,
                        "end": start + len(value),
                        "kind": "word",
                        "value": value,
                    }
                )
            continue
        result.append(
            {
                "start": match.start(),
                "end": match.end(),
                "kind": kind,
                "value": normalized,
            }
        )
    return sorted(result, key=lambda t: t["start"])


def sentences(text):
    """English boundary rules applied within a single source owner only."""
    protected = protected_spans(text)
    ends = []
    for match in re.finditer(r"[.!?]+[\"'”’\)\]]*", text):
        start, end = match.span()
        punct = text[start:end].rstrip("\"'”’)]")
        if any(a <= start < b for a, b, _ in protected):
            continue
        previous = text[start - 1] if start else ""
        following = text[match.start() + len(punct) : match.start() + len(punct) + 1]
        after = text[end:].lstrip()
        if punct == ".":
            if previous.isdigit() and following.isdigit():
                continue
            if (not previous or previous.isspace()) and following.isalpha():
                continue  # .NET and .pl; a leading dot is not a sentence end.
            if previous.isalpha() and following.isalpha() and following.islower():
                continue  # Node.js and console.log
            preceding = re.search(r"([A-Za-z]+(?:\.[A-Za-z]+)*)$", text[:start])
            word = preceding.group(1) if preceding else ""
            if word.lower() in ABBREVIATIONS and after:
                continue
            if re.fullmatch(r"[A-Z]", word) and after and re.match(r"[A-Z]", after):
                continue  # J. R. Smith
            if (
                re.fullmatch(r"(?:[A-Za-z]\.)+[A-Za-z]", word)
                and after
                and after[0].islower()
            ):
                continue
        if punct.startswith("...") and after and after[0].islower():
            continue
        # Technical dots without whitespace and lowercase continuation stay inside.
        if end < len(text) and not text[end].isspace() and text[end].islower():
            continue
        ends.append(end)
    result = []
    start = 0
    for end in ends:
        if not text[start:end].strip():
            continue
        while start < end and text[start].isspace():
            start += 1
        result.append({"start": start, "end": end, "fragment": False})
        start = end
    if text[start:].strip():
        tail_words = [
            t
            for t in tokens(text[start:])
            if t["kind"]
            in {"word", "unicode_word", "identifier", "number", "url", "email"}
        ]
        # Nonlexical suffixes (emoji, emoticon) belong to the last sentence.
        suffix = text[start:].strip()
        if result and (not tail_words or suffix in {":D", ":)", ":-)", ":("}):
            result[-1]["end"] = len(text.rstrip())
        else:
            while start < len(text) and text[start].isspace():
                start += 1
            result.append({"start": start, "end": len(text.rstrip()), "fragment": True})
    return result


def comma_count(text):
    return sum(
        c == ","
        and not (
            i and i + 1 < len(text) and text[i - 1].isdigit() and text[i + 1].isdigit()
        )
        for i, c in enumerate(text)
    )

def project(payload):
    """Keep original prose-unit order and provide separate owner-local offsets."""
    units = []
    for index, unit in enumerate(payload["prose_units"]):
        if unit["kind"] not in {"paragraph", "list_item", "text"}:
            raise RuntimeError("unknown prose kind")
        units.append({"unit_index": index, **unit, "tokens": tokens(unit["text"])})
    blocks = owners(payload)
    for block_id, block in enumerate(blocks):
        block["block_id"] = block_id
        block["tokens"] = tokens(block["text"])
        block["sentences"] = sentences(block["text"])
        cursor = 0
        spans = []
        for index in block["unit_indices"]:
            text = units[index]["text"]
            spans.append(
                {
                    "unit_index": index,
                    "owner_start": cursor,
                    "owner_end": cursor + len(text),
                }
            )
            cursor += len(text) + 1
        block["unit_spans"] = spans
        for sentence in block["sentences"]:
            sentence["word_count"] = sum(
                t["kind"] == "word"
                and t["start"] >= sentence["start"]
                and t["end"] <= sentence["end"]
                for t in block["tokens"]
            )
            sentence["source_unit_spans"] = [
                {
                    "unit_index": s["unit_index"],
                    "start": max(sentence["start"], s["owner_start"])
                    - s["owner_start"],
                    "end": min(sentence["end"], s["owner_end"]) - s["owner_start"],
                }
                for s in spans
                if sentence["start"] < s["owner_end"]
                and sentence["end"] > s["owner_start"]
            ]
    return {"units": units, "owners": blocks}
