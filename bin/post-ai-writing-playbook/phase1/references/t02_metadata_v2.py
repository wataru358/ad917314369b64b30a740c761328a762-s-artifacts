"""Separate person bylines from the publication/organization username."""

from __future__ import annotations

import json

from lxml import html

from t02_metadata import extract_metadata as extract_v1, profile_url


def extract_metadata(raw, source, encoding="utf-8"):
    value = extract_v1(raw, source, encoding)
    value["metadata_version"] = "dev-writing-metadata-v2"
    value["v1_author_status"] = value["author_status"]
    value["publication_handle"] = value["author_handle"]
    document = html.fromstring(
        raw.decode(encoding, errors="replace").encode(),
        parser=html.HTMLParser(encoding="utf-8"),
    )
    containers = document.xpath('//*[@id="article-show-container"]')
    if not containers:
        containers = document.xpath("//article[@data-article-id]")
    main = containers[0] if len(containers) == 1 else None
    header_people = set()
    organizations = []

    def evidence(field, node, url):
        value["provenance"].append(
            {
                "field": field,
                "xpath": document.getroottree().getpath(node),
                "attribute": "href",
                "value": node.get("href"),
                "normalized_url": url,
                "json_pointer": None,
            }
        )

    if main is not None:
        for node in main.xpath(".//header//a[@href]"):
            if (
                "fw-bold" in node.get("class", "").split()
                and "".join(node.itertext()).strip()
            ):
                url = profile_url(node.get("href"), source["url"])
                if url:
                    header_people.add(url)
                    evidence("header_author_profile", node, url)
        for marker in main.xpath(".//header//span"):
            if " ".join("".join(marker.itertext()).split()).lower() != "for":
                continue
            previous, following = marker.getprevious(), marker.getnext()
            if (
                previous is None
                or following is None
                or previous.tag != "a"
                or following.tag != "a"
            ):
                continue
            person = profile_url(previous.get("href", ""), source["url"])
            organization = profile_url(following.get("href", ""), source["url"])
            if person and organization:
                header_people.add(person)
                organizations.append(
                    {
                        "url": organization,
                        "name": " ".join("".join(following.itertext()).split()),
                    }
                )
                evidence("header_author_for", previous, person)
                evidence("header_organization_for", following, organization)
    ld_people = set()
    for proof in value["provenance"]:
        if (
            proof["field"] == "jsonld_author"
            and proof["value"].get("@type") == "Person"
        ):
            author = proof["value"]
            url = (
                profile_url(author["url"], source["url"]) if author.get("url") else None
            )
            if url:
                ld_people.add(url)
    conflict = bool(header_people and ld_people and header_people != ld_people)
    ids = value["author_ids"]
    if value["v1_author_status"] == "coauthor_unparsed":
        status, aid = "coauthor_unparsed", None
    elif len(ids) > 1 or len(header_people) > 1 or len(ld_people) > 1:
        status, aid = "multiple_authors", None
    elif conflict:
        status, aid = "identity_conflict", None
    elif value["primary_numeric_id"]:
        status, aid = "single_numeric_id", "dev:user:" + value["primary_numeric_id"]
    elif len(header_people | ld_people) == 1:
        status, aid = (
            "profile_url_only",
            "dev:profile:" + next(iter(header_people | ld_people)).rsplit("/", 1)[1],
        )
    else:
        status, aid = "missing_metadata", None
    people = sorted(header_people | ld_people)
    value.update(
        author_status=status,
        author_id=aid,
        author_known=status == "single_numeric_id",
        author_handle=people[0].rsplit("/", 1)[1] if len(people) == 1 else None,
        author_profiles=people,
        organization_header_profiles=organizations,
        organization_url=organizations[0]["url"] if len(organizations) == 1 else None,
    )
    if organizations:
        value["organization_status"] = "explicit_header_for"
        if len(organizations) == 1:
            value["organization_slug"] = organizations[0]["url"].rsplit("/", 1)[1]
    return value
