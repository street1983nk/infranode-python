"""LlamaIndex tools for InfraNode.

    pip install "infranode[llamaindex]"

    from llama_index.core.agent import ReActAgent
    from infranode.integrations.llamaindex import infranode_tools

    tools = infranode_tools()
    # ... pass `tools` to your agent
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from infranode.client import DEFAULT_BASE_URL
from infranode.integrations._core import TOOL_DESCRIPTION, get_city_data, list_cities

if TYPE_CHECKING:
    from llama_index.core.tools import FunctionTool

__all__ = ["infranode_tools"]


def infranode_tools(base_url: str = DEFAULT_BASE_URL) -> "list[FunctionTool]":
    """Return LlamaIndex tools that expose the InfraNode open-data API to an agent."""
    try:
        from llama_index.core.tools import FunctionTool
    except ImportError as exc:  # pragma: no cover - import guard
        raise ImportError(
            "LlamaIndex is required. Install with: pip install \"infranode[llamaindex]\""
        ) from exc

    def _get_city_data(city: str, dataset: str) -> dict:
        return get_city_data(city, dataset, base_url=base_url)

    def _list_cities() -> list:
        return list_cities(base_url=base_url)

    return [
        FunctionTool.from_defaults(
            fn=_get_city_data,
            name="infranode_get_city_data",
            description=TOOL_DESCRIPTION,
        ),
        FunctionTool.from_defaults(
            fn=_list_cities,
            name="infranode_list_cities",
            description="List all German cities covered by InfraNode (slug, name, state).",
        ),
    ]
