"""DEV article-body の構造と文章を、監査できる形で分けて抽出する。"""

from __future__ import annotations

import codecs
import hashlib
import re
from dataclasses import dataclass
from typing import Literal
from urllib.parse import unquote

from lxml import etree, html

POLICY_VERSION = "article-body-v2.0"


@dataclass(frozen=True)
class ProseUnit:
    kind: Literal["paragraph", "list_item", "text"]
    text: str
    source_path: str


@dataclass(frozen=True)
class Exclusion:
    reason: str
    path: str
    tag: str
    text_preview: str


@dataclass(frozen=True)
class QualityFlag:
    code: str
    source_path: str
    evidence: str


@dataclass(frozen=True)
class ExtractedBody:
    status: Literal["ok"]
    source_sha256: str
    policy_version: str
    selector: str
    encoding: str
    replacement_count: int
    lxml_version: str
    libxml_version: str
    parser_messages: tuple[str, ...]
    warnings: tuple[str, ...]
    raw_body_html: str
    body_html: str
    body_text: str
    prose_units: tuple[ProseUnit, ...]
    prose_text: str
    exclusions: tuple[Exclusion, ...]
    quality_flags: tuple[QualityFlag, ...]
    structural_counts: dict[str, int]


@dataclass(frozen=True)
class Failure:
    status: Literal["failed"]
    reason: Literal["missing_body", "ambiguous_body", "decode_error", "parse_error"]
    source_sha256: str
    policy_version: str
    encoding: str
    replacement_count: int
    lxml_version: str
    libxml_version: str
    parser_messages: tuple[str, ...]
    warnings: tuple[str, ...]


Result = ExtractedBody | Failure

_REMOVED = frozenset(
    "script style template noscript svg iframe form button input nav".split()
)
_MEDIA = frozenset(
    "figure figcaption img video audio picture source canvas embed object track map area".split()
)
_SKIP_PROSE = frozenset("h1 h2 h3 h4 h5 h6 pre code table blockquote".split()) | _MEDIA
_BLOCK = frozenset(
    "div center section article main header footer ul ol dl dt dd aside hr address".split()
)
_FULL_BLOCK = _BLOCK | frozenset(
    "p li h1 h2 h3 h4 h5 h6 pre blockquote table thead tbody tfoot tr th td caption figure figcaption details summary".split()
)
_SUPPORTED = frozenset(
    "div center span a p h1 h2 h3 h4 h5 h6 ul ol li strong b em i u s small sub sup mark br pre code blockquote table thead tbody tfoot tr th td caption figure figcaption img video audio picture source canvas embed object track map area section article main header footer dl dt dd aside hr address time kbd samp var abbr cite q details summary ruby rt rp wbr".split()
)
_SPACE = re.compile(r"\s+")
_CODE_LINE = re.compile(
    r"^(?:(?:var|let|const)\s+[\w$]+\s*=|function\s+[\w$]+\s*\(|app\.(?:get|post|put|delete|listen)\s*\(|[\w$.]+\s*=\s*require\s*\()"
)
_CHARSET = re.compile(
    r"(?:^|;)\s*charset\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([\w.\-]+))", re.I
)


def _versions() -> tuple[str, str]:
    return ".".join(map(str, etree.LXML_VERSION)), ".".join(
        map(str, etree.LIBXML_VERSION)
    )


def _tag(node: etree._Element) -> str:
    return node.tag.lower() if isinstance(node.tag, str) else ""


def _path(node: etree._Element) -> str:
    return node.getroottree().getpath(node)


def _text(node: etree._Element) -> str:
    return "".join(node.itertext())


def _normalized(value: str) -> str:
    return _SPACE.sub(" ", value).strip().casefold()


def _toc(node: etree._Element) -> bool:
    tag = _tag(node)
    marker = node.get("id", "").lower() in {"toc", "table-of-contents"}
    marker |= bool(
        set(node.get("class", "").lower().split()) & {"toc", "table-of-contents"}
    )
    marker |= node.get("role", "").lower() in {"navigation", "doc-toc"}
    # 見出しの目次という文字や単独のアンカーは本文なので、リストを持つ容器だけを除外する。
    return (
        marker
        and tag in {"nav", "div", "section", "aside", "ul", "ol"}
        and (tag in {"ul", "ol"} or bool(node.xpath(".//ul|.//ol")))
    )


def _unsupported_widget(node: etree._Element) -> bool:
    return _tag(node) not in _SUPPORTED or any(
        name.startswith(("ltag__", "highlight__"))
        for name in node.get("class", "").split()
    )


def _reason(node: etree._Element) -> str | None:
    classes = set(node.get("class", "").split())
    if "highlight__panel" in classes:
        return "known_code_ui"
    if "ltag__link" in classes:
        return "known_article_card"
    if "ltag-github-readme-tag" in classes:
        return "known_github_readme_card"
    if _toc(node):
        return "known_toc"
    if node.get("hidden") is not None or node.get("aria-hidden", "").lower() == "true":
        return "hidden_ui"
    style = _SPACE.sub("", node.get("style", "")).lower()
    if "display:none" in style or "visibility:hidden" in style:
        return "hidden_ui"
    if _tag(node) in _REMOVED:
        return "noncontent_subtree"
    return None


def _remove_preserving_tail(node: etree._Element) -> None:
    parent = node.getparent()
    if parent is None:
        return
    prev = node.getprevious()
    left = parent.text if prev is None else prev.tail
    tail = node.tail or ""
    # 削除したUIの位置に区切りを残す。空のspanや後続インライン要素を挟んでも語を接着させない。
    boundary = " "
    if prev is None:
        parent.text = (left or "") + boundary + tail
    else:
        prev.tail = (left or "") + boundary + tail
    parent.remove(node)


def _heading_link_toc(
    node: etree._Element,
    targets: dict[str, list[etree._Element]],
    headings: dict[str, list[etree._Element]],
) -> bool:
    for container in node.iter():
        if _tag(container) in {"ul", "ol"}:
            if (container.text or "").strip():
                return False
            if any(
                _tag(child) != "li" or (child.tail or "").strip() for child in container
            ):
                return False
    entries = list(node.iter("li"))
    matched: set[str] = set()
    previous = node.getprevious()
    explicit_toc = (
        previous is not None
        and _tag(previous) in {f"h{i}" for i in range(1, 7)}
        and _normalized(_text(previous)) in {"table of contents", "contents", "toc"}
    )
    if len(entries) < 3:
        return False
    for item in entries:
        if (item.text or "").strip():
            return False
        children = list(item)
        links = [child for child in children if _tag(child) == "a"]
        if len(links) != 1 or any(
            _tag(child) not in {"a", "ul", "ol"} for child in children
        ):
            return False
        if any((child.tail or "").strip() for child in children):
            return False
        link = links[0]
        href = link.get("href", "")
        if not href.startswith("#") or len(href) == 1:
            return False
        target_id = unquote(href[1:])
        hits = targets.get(target_id, [])
        if not hits and explicit_toc:
            hits = headings.get(_normalized(_text(link)), [])
        if len(hits) != 1 or _tag(hits[0]) not in {f"h{i}" for i in range(1, 7)}:
            return False
        if _normalized(_text(link)) != _normalized(_text(hits[0])):
            return False
        matched.add(_path(hits[0]))
    return len(matched) >= 3


def _clean(
    root: etree._Element, source_paths: dict[etree._Element, str]
) -> tuple[tuple[Exclusion, ...], tuple[str, ...]]:
    exclusions: list[Exclusion] = []
    warnings: list[str] = []
    stack = [root]
    while stack:
        node = stack.pop()
        # HTMLコメントは要素でも表示テキストでもない。tailは親の走査で保持する。
        if not _tag(node):
            continue
        if node is not root:
            reason = _reason(node)
            if reason:
                exclusions.append(
                    Exclusion(
                        reason,
                        source_paths[node],
                        _tag(node),
                        _SPACE.sub(" ", _text(node)).strip()[:160],
                    )
                )
                _remove_preserving_tail(node)
                continue
            if _tag(node) and _unsupported_widget(node):
                warnings.append(f"unsupported_widget:{_tag(node)}:{source_paths[node]}")
        stack.extend(reversed(list(node)))
    targets: dict[str, list[etree._Element]] = {}
    headings: dict[str, list[etree._Element]] = {}
    for node in root.iter():
        if _tag(node) in {f"h{i}" for i in range(1, 7)}:
            headings.setdefault(_normalized(_text(node)), []).append(node)
        keys = {node.get("id")}
        if _tag(node) == "a":
            keys.add(node.get("name"))
        owner = node
        for parent in node.iterancestors():
            if _tag(parent) in {f"h{i}" for i in range(1, 7)}:
                owner = parent
                break
        for key in keys - {None, ""}:
            hits = targets.setdefault(key, [])
            if owner not in hits:
                hits.append(owner)
    for node in list(root.iter()):
        if _tag(node) not in {"ul", "ol"} or node.getparent() is None:
            continue
        if any(_tag(parent) in {"ul", "ol"} for parent in node.iterancestors()):
            continue
        if _heading_link_toc(node, targets, headings):
            exclusions.append(
                Exclusion(
                    "heading_link_toc",
                    source_paths[node],
                    _tag(node),
                    _SPACE.sub(" ", _text(node)).strip()[:160],
                )
            )
            _remove_preserving_tail(node)
    return tuple(exclusions), tuple(warnings)


def _projection(
    root: etree._Element, source_paths: dict[etree._Element, str]
) -> tuple[ProseUnit, ...]:
    units: list[ProseUnit] = []
    pieces: list[str] = []
    kind: Literal["paragraph", "list_item", "text"] = "text"
    owner = source_paths[root]

    def flush() -> None:
        nonlocal pieces
        value = _SPACE.sub(" ", "".join(pieces)).strip()
        if value:
            units.append(ProseUnit(kind, value, owner))
        pieces = []

    def add(value: str | None) -> None:
        if value:
            pieces.append(value)

    def boundary() -> None:
        if pieces and pieces[-1] and not pieces[-1][-1].isspace():
            pieces.append(" ")

    def visit(node: etree._Element, inside_li: bool = False) -> None:
        nonlocal kind, owner
        tag = _tag(node)
        if not tag:
            return
        if tag in _SKIP_PROSE or _unsupported_widget(node):
            boundary()
            return
        is_li = tag == "li"
        is_p = tag == "p"
        block = tag in _BLOCK or is_li or is_p
        if block:
            flush()
        old_kind, old_owner = kind, owner
        if is_li:
            kind, owner = "list_item", source_paths[node]
        elif is_p:
            kind, owner = (
                ("list_item" if inside_li else "paragraph"),
                source_paths[node],
            )
        elif block:
            kind, owner = ("list_item" if inside_li else "text"), source_paths[node]
        add(node.text)
        for child in node:
            child_tag = _tag(child)
            if child_tag == "br":
                boundary()
            else:
                visit(child, inside_li or is_li)
            # tail は子の所有物ではなく親の文章。除外した code 等の後でも一度だけ読む。
            add(child.tail)
        if block:
            flush()
            kind, owner = old_kind, old_owner

    visit(root)
    flush()
    return tuple(units)


def _full_text(root: etree._Element) -> str:
    lines: list[str] = []
    current: list[str] = []

    def flush() -> None:
        value = "".join(current).strip()
        if value:
            lines.append(value)
        current.clear()

    def visit(node: etree._Element) -> None:
        tag = _tag(node)
        if not tag:
            return
        if tag == "pre":
            flush()
            code = _text(node)
            if code:
                lines.append(code)
            return
        if tag == "code":
            current.append(_text(node))
            return
        if tag == "img":
            alt = node.get("alt", "")
            current.append(" " + alt + " " if alt else " ")
            return
        if tag == "br":
            flush()
            return
        block = tag in _FULL_BLOCK
        if block:
            flush()
        if node.text:
            current.append(_SPACE.sub(" ", node.text))
        for child in node:
            visit(child)
            if child.tail:
                current.append(_SPACE.sub(" ", child.tail))
        if block:
            flush()

    visit(root)
    flush()
    return "\n".join(lines)


def _quality_flags(
    root: etree._Element, source_paths: dict[etree._Element, str]
) -> tuple[QualityFlag, ...]:
    flags: list[QualityFlag] = []
    heading_texts: dict[str, int] = {}

    def lines_with_breaks(node: etree._Element) -> list[str]:
        pieces: list[str] = []

        def walk(current: etree._Element) -> None:
            if current.text:
                pieces.append(current.text)
            for child in current:
                if _tag(child) == "br":
                    pieces.append("\n")
                else:
                    walk(child)
                if child.tail:
                    pieces.append(child.tail)

        walk(node)
        return "".join(pieces).splitlines()

    for node in root.iter():
        if _tag(node) in {f"h{i}" for i in range(1, 7)}:
            text = _normalized(_text(node))
            heading_texts[text] = heading_texts.get(text, 0) + 1
        elif (
            _tag(node) == "p"
            and len(node)
            and _tag(node[0]) == "strong"
            and not (node.text or "").strip()
        ):
            text = _normalized(_text(node[0]))
            heading_texts[text] = heading_texts.get(text, 0) + 1
    for node in root.iter():
        tag = _tag(node)
        if tag in {"ul", "ol"} and not node.xpath(".//a"):
            entries = list(node.iter("li"))
            names = [_normalized(_text(item)) for item in entries]
            matches = sum(heading_texts.get(name) == 1 for name in names)
            if (
                len(entries) >= 3
                and len(set(names)) >= 3
                and matches >= max(3, len(entries) - 1)
                and all(len(name) <= 100 for name in names)
            ):
                flags.append(
                    QualityFlag(
                        "outline_candidate",
                        source_paths[node],
                        " | ".join(
                            _SPACE.sub(" ", _text(item)).strip() for item in entries
                        )[:160],
                    )
                )
        elif tag == "p" and len(node.xpath(".//br")) >= 2:
            lines = lines_with_breaks(node)
            if sum(bool(_CODE_LINE.search(line.strip())) for line in lines) >= 2:
                flags.append(
                    QualityFlag(
                        "unmarked_code_candidate",
                        source_paths[node],
                        _SPACE.sub(" ", _text(node)).strip()[:160],
                    )
                )
    return tuple(flags)


def _counts(root: etree._Element) -> dict[str, int]:
    tags: dict[str, int] = {}
    for node in root.iter():
        tag = _tag(node)
        tags[tag] = tags.get(tag, 0) + 1
    return {
        "paragraphs": tags.get("p", 0),
        "list_items": tags.get("li", 0),
        "headings": sum(tags.get(f"h{i}", 0) for i in range(1, 7)),
        "code_blocks": tags.get("pre", 0),
        "inline_code": sum(
            1
            for node in root.iter("code")
            if not any(_tag(p) == "pre" for p in node.iterancestors())
        ),
        "tables": tags.get("table", 0),
        "blockquotes": tags.get("blockquote", 0),
        "figures": tags.get("figure", 0),
        "images": tags.get("img", 0),
    }


def extract_article(html_bytes: bytes, *, content_type: str | None = None) -> Result:
    digest = hashlib.sha256(html_bytes).hexdigest()
    lxml_version, libxml_version = _versions()
    match = _CHARSET.search(content_type or "")
    encoding = (
        next((part for part in match.groups() if part), "utf-8") if match else "utf-8"
    )
    warnings: list[str] = []
    messages: tuple[str, ...] = ()
    replacements = 0

    def fail(
        reason: Literal[
            "missing_body", "ambiguous_body", "decode_error", "parse_error"
        ],
    ) -> Failure:
        return Failure(
            "failed",
            reason,
            digest,
            POLICY_VERSION,
            encoding,
            replacements,
            lxml_version,
            libxml_version,
            messages,
            tuple(warnings),
        )

    try:
        codecs.lookup(encoding)
        try:
            decoded = html_bytes.decode(encoding)
        except UnicodeDecodeError:
            decoded = html_bytes.decode(encoding, errors="replace")
            # 元からあるU+FFFDはエラーではない。デコーダが追加した置換だけを数える。
            surviving = html_bytes.decode(encoding, errors="ignore")
            replacements = decoded.count("\ufffd") - surviving.count("\ufffd")
    except (LookupError, ValueError):
        warnings.append("unknown_charset")
        return fail("decode_error")
    if replacements:
        warnings.append(f"decode_replacements:{replacements}")
    parser = html.HTMLParser(encoding="utf-8", no_network=True, recover=True)
    try:
        document = html.document_fromstring(decoded, parser=parser)
        messages = tuple(
            f"{item.level_name}:{item.line}:{item.message}" for item in parser.error_log
        )
        if messages:
            warnings.append("parser_messages")
        ids = document.xpath("//*[@id='article-body']")
        if len(ids) > 1:
            return fail("ambiguous_body")
        if ids:
            root, selector = ids[0], "#article-body"
        else:
            candidates = document.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' crayons-article__body ')]"
            )
            if len(candidates) > 1:
                return fail("ambiguous_body")
            if not candidates:
                return fail("missing_body")
            root, selector = candidates[0], ".crayons-article__body"
        raw = etree.tostring(root, encoding="unicode", method="html", with_tail=False)
        source_paths = {node: _path(node) for node in root.iter() if _tag(node)}
        exclusions, unsupported = _clean(root, source_paths)
        warnings.extend(unsupported)
        units = _projection(root, source_paths)
        body_text = _full_text(root)
        quality_flags = _quality_flags(root, source_paths)
        if not units:
            warnings.append("no_prose")
        return ExtractedBody(
            "ok",
            digest,
            POLICY_VERSION,
            selector,
            encoding,
            replacements,
            lxml_version,
            libxml_version,
            messages,
            tuple(warnings),
            raw,
            etree.tostring(root, encoding="unicode", method="html", with_tail=False),
            body_text,
            units,
            "\n\n".join(unit.text for unit in units),
            exclusions,
            quality_flags,
            _counts(root),
        )
    except (etree.LxmlError, ValueError, RecursionError) as exc:
        warnings.append(f"parse_exception:{type(exc).__name__}")
        return fail("parse_error")
