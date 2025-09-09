"""Abstract base class for MCP client handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ClientHandler(ABC):
    """Abstract base class for MCP client handlers."""

    @abstractmethod
    def get_config_path(self) -> Path:
        """Get the path to the client's configuration file."""
        pass

    @abstractmethod
    def setup_server(self, server_name: str, server_config: dict[str, Any]) -> bool:
        """Add server to client config - only touch our server entries."""
        pass

    @abstractmethod
    def remove_server(self, server_name: str) -> bool:
        """Remove server from client config - preserve all other servers."""
        pass

    @abstractmethod
    def list_managed_servers(self) -> list[dict[str, Any]]:
        """List only servers managed by this tool."""
        pass

    @abstractmethod
    def list_all_servers(self) -> list[dict[str, Any]]:
        """List all servers in config (managed + external)."""
        pass
