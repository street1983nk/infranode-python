"""LangChain tools for InfraNode.

    pip install "infranode[langchain]"

    from langchain_openai import ChatOpenAI
    from langchain.agents import create_react_agent
    from infranode.integrations.langchain import infranode_tools

    tools = infranode_tools()
    # ... bind `tools` to your agent / LLM
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from infranode.client import DEFAULT_BASE_URL
from infranode.integrations._core import TOOL_DESCRIPTION, get_city_data, list_cities

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

__all__ = ["infranode_tools"]


def infranode_tools(base_url: str = DEFAULT_BASE_URL) -> "list[BaseTool]":
    """Return LangChain tools that expose the InfraNode open-data API to an agent."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as exc:  # pragma: no cover - import guard
        raise ImportError(
            "LangChain is required. Install with: pip install \"infranode[langchain]\""
        ) from exc

    def _get_city_data(city: str, dataset: str) -> dict:
        return get_city_data(city, dataset, base_url=base_url)

    def _list_cities() -> list:
        return list_cities(base_url=base_url)

    return [
        StructuredTool.from_function(
            func=_get_city_data,
            name="infranode_get_city_data",
            description=TOOL_DESCRIPTION,
        ),
        StructuredTool.from_function(
            func=_list_cities,
            name="infranode_list_cities",
            description="List all German cities covered by InfraNode (slug, name, state).",
        ),
    ]
