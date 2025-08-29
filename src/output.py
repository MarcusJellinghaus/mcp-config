"""Output formatting utilities for the MCP configuration tool."""

from pathlib import Path
from typing import Any, Dict, List, Optional


class OutputFormatter:
    """Formatter for various types of output."""
    
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message."""
        try:
            print(f"{OutputFormatter.ERROR} {message}")
        except (UnicodeEncodeError, UnicodeDecodeError):
            print(f"[ERROR] {message}")
    
    @staticmethod
    def print_validation_errors(errors: List[str]) -> None:
        """Print validation errors."""
        if errors:
            OutputFormatter.print_error("Validation failed:")
            for error in errors:
                print(f"  - {error}")
    
    @staticmethod
    def print_dry_run_header() -> None:
        """Print dry run header."""
        print("=" * 50)
        print("DRY RUN - No changes will be made")
        print("=" * 50)
    
    @staticmethod
    def print_auto_detected_params(params: Dict[str, str]) -> None:
        """Print auto-detected parameters."""
        print("Auto-detected parameters:")
        for key, value in params.items():
            display_key = key.replace("_", "-")
            print(f"  {display_key}: {value}")
    
    @staticmethod
    def print_configuration_details(
        server_name: str, 
        server_type: str, 
        user_params: Dict[str, Any]
    ) -> None:
        """Print configuration details."""
        print(f"\nConfiguring '{server_name}' ({server_type}):")
        for key, value in user_params.items():
            if value is not None:
                display_key = key.replace("_", "-")
                print(f"  {display_key}: {value}")
    
    @staticmethod
    def print_dry_run_config_preview(
        config: Dict[str, Any],
        config_path: Path,
        backup_path: Optional[Path] = None
    ) -> None:
        """Print a preview of the configuration that would be applied."""
        print(f"\nWould configure server: {config.get('name', 'Unknown')}")
        print(f"Server type: {config.get('type', 'Unknown')}")
        print(f"Command: {config.get('command', '')}")
        if config.get('args'):
            print(f"Arguments: {' '.join(config['args'])}")
        print(f"Configuration file: {config_path}")
        if backup_path:
            print(f"Backup would be created: {backup_path}")
        
        try:
            print(f"\n{OutputFormatter.SUCCESS} Configuration valid. Run without --dry-run to apply.")
        except (UnicodeEncodeError, UnicodeDecodeError):
            print("\n[SUCCESS] Configuration valid. Run without --dry-run to apply.")
    
    @staticmethod
    def print_dry_run_remove_preview(
        server_name: str,
        server_info: Dict[str, Any],
        remaining_servers: List[Dict[str, Any]],
        config_path: Path,
        backup_path: Optional[Path] = None
    ) -> None:
        """Print a preview of server removal."""
        print(f"\nWould remove server: {server_name}")
        print(f"Server type: {server_info.get('type', 'Unknown')}")
        print(f"Command: {server_info.get('command', '')}")
        print(f"Configuration file: {config_path}")
        if backup_path:
            print(f"Backup would be created: {backup_path}")
        
        if remaining_servers:
            print(f"\nRemaining servers ({len(remaining_servers)}):")
            for server in remaining_servers:
                print(f"  - {server['name']} ({server.get('type', 'unknown')})")
        else:
            print("\nNo servers would remain after removal.")
        
        try:
            print(f"\n{OutputFormatter.SUCCESS} Removal plan valid. Run without --dry-run to apply.")
        except (UnicodeEncodeError, UnicodeDecodeError):
            print("\n[SUCCESS] Removal plan valid. Run without --dry-run to apply.")
    
    @staticmethod
    def print_enhanced_server_list(
        servers: List[Dict[str, Any]],
        client_name: str,
        config_path: Path,
        detailed: bool = False
    ) -> None:
        """Print an enhanced server list."""
        print(f"\n{client_name.title()} Servers ({config_path}):")
        
        if not servers:
            print("  No servers configured")
            return
        
        for server in servers:
            managed_mark = "●" if server.get("managed", False) else "○"
            print(f"  {managed_mark} {server['name']} ({server.get('type', 'unknown')})")
            
            if detailed:
                print(f"    Command: {server.get('command', '')}")
                if server.get('args'):
                    args_str = " ".join(server['args'])
                    if len(args_str) > 80:
                        args_str = args_str[:77] + "..."
                    print(f"    Args: {args_str}")
                if not server.get("managed", False):
                    print("    Note: External server (not managed by mcp-config)")
                print()
    
    @staticmethod
    def print_validation_results(result: Dict[str, Any]) -> None:
        """Print validation results."""
        if result["success"]:
            try:
                print(f"{OutputFormatter.SUCCESS} Validation passed")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print("[SUCCESS] Validation passed")
        else:
            OutputFormatter.print_error("Validation failed")
        
        # Print individual checks
        if "checks" in result:
            print("\nChecks performed:")
            for check, passed in result["checks"].items():
                status = OutputFormatter.SUCCESS if passed else OutputFormatter.ERROR
                try:
                    print(f"  {status} {check.replace('_', ' ').title()}")
                except (UnicodeEncodeError, UnicodeDecodeError):
                    status_text = "[PASS]" if passed else "[FAIL]"
                    print(f"  {status_text} {check.replace('_', ' ').title()}")
        
        # Print warnings and errors
        if result.get("warnings"):
            print("\nWarnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        
        if result.get("errors"):
            print("\nErrors:")
            for error in result["errors"]:
                print(f"  - {error}")
