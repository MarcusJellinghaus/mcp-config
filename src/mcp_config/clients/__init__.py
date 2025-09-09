"""Client handlers for managing MCP server configurations in various clients.

This module provides abstract base class and implementations for managing
MCP server configurations in different client applications.
"""

from typing import Any, Callable, Union

from .base import ClientHandler
from .claude_desktop import ClaudeDesktopHandler
from .intellij import IntelliJHandler
from .vscode import VSCodeHandler

__all__ = [
    "ClientHandler",
    "ClaudeDesktopHandler",
    "IntelliJHandler",
    "VSCodeHandler",
    "get_client_handler",
    "CLIENT_HANDLERS",
    "HandlerFactory",
]

# Type alias for handler factories
HandlerFactory = Union[type[ClientHandler], Callable[[], ClientHandler]]

CLIENT_HANDLERS: dict[str, HandlerFactory] = {
    "claude-desktop": ClaudeDesktopHandler,
    "vscode-workspace": lambda: VSCodeHandler(workspace=True),
    "vscode-user": lambda: VSCodeHandler(workspace=False),
    "intellij": IntelliJHandler,
}


def get_client_handler(client_name: str) -> ClientHandler:
    """Get client handler by name.

    Args:
        client_name: Name of the client

    Returns:
        ClientHandler instance

    Raises:
        ValueError: If client name is not recognized
    """
    if client_name not in CLIENT_HANDLERS:
        raise ValueError(
            f"Unknown client: {client_name}. Available: {list(CLIENT_HANDLERS.keys())}"
        )

    handler_factory = CLIENT_HANDLERS[client_name]
    # Check if it's a lambda/callable or a class
    if callable(handler_factory) and not isinstance(handler_factory, type):
        # It's a lambda or function, call it to get the handler instance
        handler = handler_factory()
    else:
        # It's a class, instantiate it
        handler = handler_factory()

    # If it's ClaudeDesktopHandler, try to migrate any inline metadata
    if isinstance(handler, ClaudeDesktopHandler):
        handler.migrate_inline_metadata()

    return handler
