"""Saved-HTML metadata with field-level provenance and conservative identity."""

from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import unquote, urljoin, urlsplit

from lxml import html


def profile_url(value, base):
    url = urlsplit(urljoin(base, str(value)))
    if url.hostname not in {"dev.to", "www.dev.to"}:
        return None
    path = unquote(url.path).strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", path) or path.lower() in {
        "about",
        "new",
        "tags",
        "t",
        "settings",
    }:
        return None
    return "https://dev.to/" + path.lower()


def objects(value):
    if isinstance(value, list):
        for v in value:
            yield from objects(v)
    elif isinstance(value, dict):
        yield value
        if "@graph" in value:
            yield from objects(value["@graph"])


def extract_metadata(raw, source, encoding="utf-8"):
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != source["html_sha256"]:
        raise ValueError(f"saved HTML hash mismatch for {source['article_id']}")
    document = html.fromstring(
        raw.decode(encoding, errors="replace").encode(),
        parser=html.HTMLParser(encoding="utf-8"),
    )
    provenance, issues = [], []

    def evidence(field, node, attribute=None, value=None, pointer=None):
        result = {
            "field": field,
            "xpath": document.getroottree().getpath(node),
            "attribute": attribute,
            "value": value,
            "json_pointer": pointer,
        }
        provenance.append(result)

    containers = document.xpath('//*[@id="article-show-container"]')
    if not containers:
        containers = document.xpath("//article[@data-article-id]")
    main = containers[0] if len(containers) == 1 else None
    if len(containers) > 1:
        issues.append("ambiguous_article_container")
    numeric, handle, coauthors, coauthor_unparsed = None, None, [], False
    organization_id, organization_slug = None, None
    if main is not None:
        for attribute, field in [
            ("data-author-id", "author_numeric_id"),
            ("data-author-username", "author_handle"),
            ("data-co-author-ids", "coauthor_ids"),
            ("data-organization-id", "organization_id"),
            ("data-organization-slug", "organization_slug"),
        ]:
            value = main.get(attribute)
            if value is not None:
                evidence(field, main, attribute, value)
        raw_id = main.get("data-author-id", "")
        numeric = raw_id if raw_id.isdigit() and int(raw_id) > 0 else None
        handle = main.get("data-author-username") or None
        raw_co = main.get("data-co-author-ids", "").strip()
        if raw_co:
            try:
                parsed = (
                    json.loads(raw_co) if raw_co.startswith("[") else raw_co.split(",")
                )
                coauthors = sorted(
                    {str(v).strip() for v in parsed if str(v).strip().isdigit()}
                )
                coauthor_unparsed = len(coauthors) != len(
                    set(str(v).strip() for v in parsed)
                )
            except (ValueError, TypeError):
                coauthor_unparsed = True
        organization_id = main.get("data-organization-id") or None
        organization_slug = main.get("data-organization-slug") or None
    ld_people, ld_organizations = set(), []
    for node in document.xpath('//script[@type="application/ld+json"]'):
        try:
            parsed = json.loads(node.text or "")
        except ValueError:
            issues.append("invalid_jsonld")
            continue
        for obj in objects(parsed):
            types = obj.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if not set(types) & {"Article", "BlogPosting", "TechArticle"}:
                continue
            authors = obj.get("author", [])
            if not isinstance(authors, list):
                authors = [authors]
            for author in authors:
                if not isinstance(author, dict):
                    issues.append("jsonld_author_not_object")
                    continue
                evidence("jsonld_author", node, value=author, pointer="/author")
                if author.get("@type") == "Person":
                    value = (
                        profile_url(author.get("url", ""), source["url"])
                        if author.get("url")
                        else None
                    )
                    if value:
                        ld_people.add(value)
                elif author.get("@type") == "Organization":
                    ld_organizations.append(author)
    dom_profile = profile_url("/" + handle, source["url"]) if handle else None
    conflict = bool(dom_profile and ld_people and dom_profile not in ld_people)
    numeric_ids = sorted({v for v in [numeric, *coauthors] if v}, key=int)
    if coauthor_unparsed:
        author_status, author_id = "coauthor_unparsed", None
    elif conflict:
        author_status, author_id = "identity_conflict", None
    elif len(numeric_ids) > 1 or len(ld_people) > 1:
        author_status, author_id = "multiple_authors", None
    elif numeric:
        author_status, author_id = "single_numeric_id", "dev:user:" + numeric
    elif len(ld_people) == 1:
        author_status, author_id = (
            "profile_url_only",
            "dev:profile:" + next(iter(ld_people)).rsplit("/", 1)[1],
        )
    else:
        author_status, author_id = "missing_metadata", None
    tags = []
    if main is not None:
        for node in main.xpath(".//header//a[@href]"):
            url = urlsplit(urljoin(source["url"], node.get("href")))
            if url.hostname in {"dev.to", "www.dev.to"} and re.fullmatch(
                r"/t/[A-Za-z0-9_\-]+/?", url.path
            ):
                tag = unquote(url.path.strip("/").split("/")[1]).lower()
                tags.append(tag)
                evidence("tag", node, "href", node.get("href"))
    canonicals = []
    for node in document.xpath("//link[@href]"):
        if "canonical" in node.get("rel", "").lower().split():
            url = urljoin(source["url"], node.get("href"))
            canonicals.append(url)
            evidence("canonical", node, "href", node.get("href"))
    canonicals = sorted(set(canonicals))
    source_path = urlsplit(source["url"]).path.strip("/").split("/")
    return {
        "article_id": source["article_id"],
        "author_id": author_id,
        "author_status": author_status,
        "author_known": author_status == "single_numeric_id",
        "primary_numeric_id": numeric,
        "author_ids": ["dev:user:" + v for v in numeric_ids],
        "author_profiles": sorted(
            ld_people | ({dom_profile} if dom_profile else set())
        ),
        "author_handle": handle,
        "url_handle_only": source_path[0] if len(source_path) >= 2 else None,
        "organization_id": organization_id,
        "organization_slug": organization_slug,
        "jsonld_author_organizations": ld_organizations,
        "organization_status": "explicit"
        if organization_id or organization_slug or ld_organizations
        else "not_observed",
        "tags": sorted(set(tags)),
        "tag_status": "ok" if tags else "missing_metadata",
        "canonical": canonicals[0] if len(canonicals) == 1 else None,
        "canonical_status": "ok"
        if len(canonicals) == 1
        else "conflict"
        if canonicals
        else "missing_metadata",
        "canonical_candidates": canonicals,
        "source_html_sha256": actual_hash,
        "source_html_file": source["html_file"],
        "issues": issues,
        "provenance": provenance,
    }


def classify(title, tags, config):
    title = title.lower()
    flags = []
    for category in config["type_priority"]:
        rule = config["types"][category]
        if any(tag in tags for tag in rule["tags"]) or any(
            re.search(pattern, title) for pattern in rule["title_patterns"]
        ):
            flags.append(category)
    topics = sorted(
        {topic for topic, known in config["topics"].items() if set(known) & set(tags)}
    )
    return {
        "article_type": flags[0] if len(flags) == 1 else "unknown",
        "article_type_priority_guess": flags[0] if flags else None,
        "article_type_cues": flags,
        "article_type_ambiguous": len(flags) > 1,
        "topics": topics or ["unknown"],
        "unmapped_tags": sorted(
            set(tags) - {t for values in config["topics"].values() for t in values}
        ),
    }
