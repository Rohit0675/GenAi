from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from app.config import get_settings


class LLMConfigurationError(Exception):
    """Raised when the configured LLM cannot be initialized."""


def get_llm() -> BaseChatModel:
    settings = get_settings()

    if settings.llm_provider.lower() != "ollama":
        raise LLMConfigurationError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    if not settings.llm_model.strip():
        raise LLMConfigurationError(
            "LLM_MODEL is not configured. Set it in the .env file."
        )

    try:
        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )
    except Exception as exc:
        raise LLMConfigurationError(
            f"Failed to initialize the LLM: {exc}"
        ) from exc


def extract_text(response: Any) -> str:
    """
    Convert a LangChain model response into plain text.

    This keeps response-format handling outside the graph nodes.
    """
    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))

        return "\n".join(parts).strip()

    return str(content).strip()