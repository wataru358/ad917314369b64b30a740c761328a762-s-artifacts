"""Project emphasis from saved clean DOM onto the immutable prose units."""

from __future__ import annotations

import re

from lxml import html

from article_extraction import _BLOCK, _SKIP_PROSE, _tag, _unsupported_widget
from segmentation import tokens


class ProjectionError(ValueError):
    pass


def normalize(pieces):
    text, mask = [], []
    for value, bold in pieces:
        for char in value:
            if char.isspace():
                if text and text[-1] == " ":
                    mask[-1] |= bold
                else:
                    text.append(" ")
                    mask.append(bold)
            else:
                text.append(char)
                mask.append(bold)
    left = 1 if text and text[0] == " " else 0
    right = len(text) - (1 if text and text[-1] == " " else 0)
    return "".join(text[left:right]), mask[left:right]


def dom_projection(body_html):
    root = html.fromstring(body_html.encode(), parser=html.HTMLParser(encoding="utf-8"))
    units, pieces = [], []
    kind, owner = "text", root.getroottree().getpath(root)

    def flush():
        nonlocal pieces
        text, mask = normalize(pieces)
        if text:
            intervals, start = [], None
            for i, active in enumerate([*mask, False]):
                if active and start is None:
                    start = i
                elif not active and start is not None:
                    intervals.append([start, i])
                    start = None
            units.append(
                {
                    "kind": kind,
                    "text": text,
                    "local_owner": owner,
                    "bold_spans": intervals,
                }
            )
        pieces = []

    def add(value, bold):
        if value:
            pieces.append((value, bold))

    def boundary(bold):
        if pieces and pieces[-1][0] and not pieces[-1][0][-1].isspace():
            pieces.append((" ", bold))

    def visit(node, inside_li=False, bold=False):
        nonlocal kind, owner
        tag = _tag(node)
        if not tag:
            return
        if tag in _SKIP_PROSE or _unsupported_widget(node):
            boundary(bold)
            return
        block = tag in _BLOCK or tag in {"li", "p"}
        if block:
            flush()
        old_kind, old_owner = kind, owner
        if tag == "li":
            kind, owner = "list_item", root.getroottree().getpath(node)
        elif tag == "p":
            kind, owner = (
                ("list_item" if inside_li else "paragraph"),
                root.getroottree().getpath(node),
            )
        elif block:
            kind, owner = (
                ("list_item" if inside_li else "text"),
                root.getroottree().getpath(node),
            )
        active = bold or tag in {"strong", "b"}
        add(node.text, active)
        for child in node:
            if _tag(child) == "br":
                boundary(active)
            else:
                visit(child, inside_li or tag == "li", active)
            add(child.tail, active)
        if block:
            flush()
            kind, owner = old_kind, old_owner

    visit(root)
    flush()
    headings = [
        {
            "level": int(_tag(n)[1]),
            "text": " ".join("".join(n.itertext()).split()),
            "local_path": root.getroottree().getpath(n),
        }
        for n in root.iter()
        if _tag(n) in {"h1", "h2", "h3", "h4", "h5", "h6"}
    ]
    return units, headings


def align_structure(payload):
    projected, headings = dom_projection(payload["body_html"])
    fixed = payload["prose_units"]
    if [(u["kind"], u["text"]) for u in projected] != [
        (u["kind"], u["text"]) for u in fixed
    ]:
        raise ProjectionError("clean DOM projection differs from saved prose units")
    # Local owner partition must agree even though source and clean XPaths differ.
    forward, reverse = {}, {}
    for p, f in zip(projected, fixed, strict=True):
        key, val = (p["kind"], p["local_owner"]), (f["kind"], f["source_path"])
        if forward.setdefault(key, val) != val or reverse.setdefault(val, key) != key:
            raise ProjectionError("clean/source owner partition differs")
    spans, bold_words = [], 0
    for index, unit in enumerate(projected):
        words = [t for t in tokens(unit["text"]) if t["kind"] == "word"]
        kept = [
            [a, b]
            for a, b in unit["bold_spans"]
            if any(t["start"] < b and t["end"] > a for t in words)
        ]
        spans.extend({"unit_index": index, "start": a, "end": b} for a, b in kept)
        bold_words += sum(
            any(t["start"] < b and t["end"] > a for a, b in kept) for t in words
        )
    return {
        "bold_spans": spans,
        "bold_intervals": len(spans),
        "bold_words": bold_words,
        "headings": headings,
        "projection_state": "ok",
    }
