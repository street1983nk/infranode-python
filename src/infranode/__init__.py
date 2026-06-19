"""InfraNode: keyless Python client for the InfraNode open-data API.

See https://infranode.dev. Framework tools live in optional submodules:

    from infranode.integrations.langchain import infranode_tools   # extra: langchain
    from infranode.integrations.llamaindex import infranode_tools  # extra: llamaindex
"""

from infranode.client import (
    DEFAULT_BASE_URL,
    AsyncInfraNode,
    InfraNode,
    InfraNodeError,
    Record,
)

__version__ = "0.1.0"

__all__ = [
    "InfraNode",
    "AsyncInfraNode",
    "Record",
    "InfraNodeError",
    "DEFAULT_BASE_URL",
    "__version__",
]
