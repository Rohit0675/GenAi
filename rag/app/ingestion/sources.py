from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDefinition:
    company: str
    product: str
    url: str
    source_type: str = "official"
    category_hint: str | None = None
    published_date: str | None = None


SOURCES = [
    # Figma
    SourceDefinition(
        "Figma",
        "Figma",
        "https://www.figma.com/blog/the-figma-agent-is-here/",
        category_hint="AI",
    ),
    SourceDefinition(
        "Figma",
        "Figma",
        "https://www.figma.com/blog/config-2026-recap/",
        category_hint="AI",
    ),
    SourceDefinition(
        "Figma",
        "Figma",
        "https://www.figma.com/blog/2026-ai-report/",
        category_hint="AI",
    ),
    SourceDefinition(
        "Figma",
        "Figma",
        "https://www.figma.com/blog/how-we-built-generative-plugins-and-shaders/",
        category_hint="AI",
    ),

    # Canva
    SourceDefinition(
        "Canva",
        "Canva",
        "https://www.canva.com/en_in/newsroom/news/canva-create-2026-ai/",
        category_hint="AI",
        published_date="2026-04-15"
    ),

    # Notion
    SourceDefinition(
        "Notion",
        "Notion",
        "https://www.notion.com/releases/2026-09-15",
        category_hint="AI",
    ),
    SourceDefinition(
        "Notion",
        "Notion",
        "https://www.notion.com/releases/2026-07-01",
        category_hint="AI",
    ),
    SourceDefinition(
        "Notion",
        "Notion",
        "https://www.notion.com/releases/2026-01-20",
        category_hint="AI",
    ),
]