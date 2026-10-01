from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

import requests

from app.config import MAX_SOURCE_BYTES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from app.ingestion.sources import SourceDefinition

log = logging.getLogger(__name__)

@dataclass
class FetchedSource:
    source: SourceDefinition
    url: str
    status_code: int
    content_type: str
    body: bytes
    content_hash: str

class SourceFetchError(RuntimeError):
    pass

def fetch_source(source: SourceDefinition) -> FetchedSource:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    try:
        response = requests.get(
            source.url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SourceFetchError(f"fetch failed for {source.url}: {exc}") from exc

    body = response.content
    if len(body) > MAX_SOURCE_BYTES:
        raise SourceFetchError(f"source exceeds MAX_SOURCE_BYTES: {source.url}")

    return FetchedSource(
        source=source,
        url=response.url,
        status_code=response.status_code,
        content_type=response.headers.get("content-type", ""),
        body=body,
        content_hash=hashlib.sha256(body).hexdigest(),
    )
