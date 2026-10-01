from __future__ import annotations

import json
import re
from datetime import date, datetime

from bs4 import BeautifulSoup
import trafilatura

from app.ingestion.fetch import FetchedSource


DATE_RE = re.compile(
    r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b"
)

MONTH_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(\d{1,2}),\s+(20\d{2})\b"
)


class ExtractionError(RuntimeError):
    pass


def _date_from_text(text: str) -> date | None:
    m = DATE_RE.search(text)
    if m:
        return date(
            int(m.group(1)),
            int(m.group(2)),
            int(m.group(3)),
        )

    m = MONTH_RE.search(text)
    if m:
        return datetime.strptime(
            f"{m.group(1)} {m.group(2)} {m.group(3)}",
            "%B %d %Y",
        ).date()

    return None


def _jsonld_dates(soup: BeautifulSoup) -> list[date]:
    dates: list[date] = []

    for node in soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    ):
        try:
            data = json.loads(node.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        objects = data if isinstance(data, list) else [data]

        for obj in objects:
            if not isinstance(obj, dict):
                continue

            for key in (
                "datePublished",
                "dateCreated",
                "dateModified",
            ):
                value = obj.get(key)

                if isinstance(value, str):
                    try:
                        parsed = date.fromisoformat(value[:10])
                        dates.append(parsed)
                    except ValueError:
                        pass

    return dates


def _date_from_meta(soup: BeautifulSoup) -> date | None:
    """
    Try common HTML metadata fields used for publication dates.
    """

    meta_attributes = [
        {"property": "article:published_time"},
        {"property": "article:published"},
        {"name": "date"},
        {"name": "publish-date"},
        {"name": "published-date"},
        {"name": "publication-date"},
        {"itemprop": "datePublished"},
        {"itemprop": "dateCreated"},
    ]

    for attrs in meta_attributes:
        meta = soup.find("meta", attrs=attrs)

        if not meta:
            continue

        content = meta.get("content")

        if not content:
            continue

        try:
            return date.fromisoformat(content[:10])
        except ValueError:
            continue

    return None


def _date_from_time_elements(soup: BeautifulSoup) -> date | None:
    """
    Try <time datetime="..."> elements.
    """

    for time_tag in soup.find_all("time"):
        value = time_tag.get("datetime")

        if not value:
            value = time_tag.get_text(" ", strip=True)

        if not value:
            continue

        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            pass

        parsed = _date_from_text(value)

        if parsed:
            return parsed

    return None


def _canva_fallback_date(source: FetchedSource) -> date | None:
    """
    Canva's newsroom URL currently contains only the year:

        /canva-create-2026-ai/

    A year alone is not sufficient to construct a real publication date,
    so this function deliberately does NOT infer a month/day.

    This function is reserved for a known, explicit Canva publication
    date supplied by the source configuration in the future.
    """

    if source.url.startswith(
        "https://www.canva.com/en_in/newsroom/news/canva-create-2026-ai/"
    ):
        # Do NOT invent a month/day from the URL.
        return None

    return None


def extract_source(source: FetchedSource) -> dict:
    soup = BeautifulSoup(source.body, "html.parser")

    # Preserve the original HTML long enough for metadata extraction.
    original_soup = BeautifulSoup(source.body, "html.parser")

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    title = None

    og_title = original_soup.find(
        "meta",
        property="og:title",
    )

    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    if not title:
        title_tag = original_soup.find("title")

        if title_tag:
            title = title_tag.get_text(
                " ",
                strip=True,
            )

    if not title:
        h1 = original_soup.find("h1")

        if h1:
            title = h1.get_text(
                " ",
                strip=True,
            )

    # ---------------------------------------------------------
    # PUBLICATION DATE
    # ---------------------------------------------------------

    published: date | None = None

    # 1. Standard metadata
    published = _date_from_meta(original_soup)

    # 2. JSON-LD
    if published is None:
        dates = _jsonld_dates(original_soup)

        if dates:
            published = dates[0]

    # 3. <time datetime="...">
    if published is None:
        published = _date_from_time_elements(original_soup)

    # Remove non-content elements before extracting visible text.
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        tag.decompose()

    # 4. Look for explicit dates in visible page text.
    if published is None:
        visible_text = soup.get_text(
            " ",
            strip=True,
        )

        published = _date_from_text(
            visible_text[:12000]
        )
    if published is None and source.source.published_date:
        published = date.fromisoformat(
            source.source.published_date
        )    
    if published is None and source.source_definition.published_date:
        published = date.fromisoformat(
            source.source_definition.published_date
        )    

    # 5. Canva-specific fallback.
    #
    # This intentionally returns None unless a real date is
    # available. We never manufacture a date from "2026".
    if published is None:
        published = _canva_fallback_date(source)

    # ---------------------------------------------------------
    # CONTENT
    # ---------------------------------------------------------

    html = str(soup)

    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        include_links=False,
        favor_precision=True,
    )

    if not text:
        text = soup.get_text(
            "\n",
            strip=True,
        )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    ).strip()

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not title:
        raise ExtractionError(
            f"title unavailable: {source.url}"
        )

    if len(text) < 100:
        raise ExtractionError(
            f"insufficient extractable content: {source.url}"
        )

    # Publication date is intentionally allowed to remain None
    # here. normalize.py decides whether the document can be
    # stored in the processed dataset.

    return {
        "title": title,
        "published_date": published,
        "content": text,
        "final_url": source.url,
    }