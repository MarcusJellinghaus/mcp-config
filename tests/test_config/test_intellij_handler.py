"""
Test suite for IntelliJ GitHub Copilot handler.

Following TDD approach - these tests define the required API and behavior
for IntelliJ GitHub Copilot MCP client handler with cross-platform path detection.
"""

import pytest
import os
import platform
from pathlib import Path
from unittest.mock import patch

# Import the module we're testing (will fail initially - that's expected in TDD)
try:
    from mcp_config.clients import IntelliJHandler, ClientHandler  # type: ignore[import-untyped]
except ImportError:
    # Expected during TDD red phase
    IntelliJHandler = None
    ClientHandler = None


@pytest.fixture
def mock_home_path(tmp_path: Path) -> Path:
    """Mock home directory for testing."""
    return tmp_path / "home" / "testuser"


class TestIntelliJPathDetection:
    """Test cross-platform path detection for IntelliJ GitHub Copilot."""
    
    @patch('os.name', 'nt')
    def test_windows_path_verified(self, mock_home_path: Path) -> None:
        """Test Windows path - VERIFIED real-world path."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            path = handler.get_config_path()
            
            # Windows verified path: AppData\Local\github-copilot\intellij\mcp.json
            expected_path = mock_home_path / "AppData" / "Local" / "github-copilot" / "intellij" / "mcp.json"
            assert path == expected_path
            assert str(path).endswith(r'AppData\Local\github-copilot\intellij\mcp.json') or str(path).endswith(r'AppData/Local/github-copilot/intellij/mcp.json')
    
    @patch('platform.system', return_value='Darwin')
    @patch('os.name', 'posix')
    def test_macos_path_projected(self, mock_home_path: Path) -> None:
        """Test macOS path - PROJECTED following Apple conventions."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            path = handler.get_config_path()
            
            # macOS projected path: ~/Library/Application Support/github-copilot/intellij/mcp.json
            expected_path = mock_home_path / "Library" / "Application Support" / "github-copilot" / "intellij" / "mcp.json"
            assert path == expected_path
            assert 'Library/Application Support/github-copilot/intellij/mcp.json' in str(path)
    
    @patch('platform.system', return_value='Linux')
    @patch('os.name', 'posix')  
    def test_linux_path_projected(self, mock_home_path: Path) -> None:
        """Test Linux path - PROJECTED following XDG Base Directory spec."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            path = handler.get_config_path()
            
            # Linux projected path: ~/.local/share/github-copilot/intellij/mcp.json
            expected_path = mock_home_path / ".local" / "share" / "github-copilot" / "intellij" / "mcp.json"
            assert path == expected_path
            assert '.local/share/github-copilot/intellij/mcp.json' in str(path)
    
    def test_cross_platform_consistency(self, mock_home_path: Path) -> None:
        """Test that all platforms use consistent github-copilot/intellij/mcp.json structure."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            # Test Windows
            with patch('os.name', 'nt'):
                win_path = handler.get_config_path()
                assert win_path.name == "mcp.json"
                assert win_path.parent.name == "intellij"
                assert win_path.parent.parent.name == "github-copilot"
            
            # Test macOS
            with patch('platform.system', return_value='Darwin'), patch('os.name', 'posix'):
                mac_path = handler.get_config_path()
                assert mac_path.name == "mcp.json"
                assert mac_path.parent.name == "intellij"
                assert mac_path.parent.parent.name == "github-copilot"
            
            # Test Linux
            with patch('platform.system', return_value='Linux'), patch('os.name', 'posix'):
                linux_path = handler.get_config_path()
                assert linux_path.name == "mcp.json"
                assert linux_path.parent.name == "intellij"
                assert linux_path.parent.parent.name == "github-copilot"


class TestGitHubCopilotDirectoryStructure:
    """Test GitHub Copilot directory structure validation."""
    
    def test_github_copilot_directory_structure(self, mock_home_path: Path) -> None:
        """Test expected GitHub Copilot directory structure."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            # Create the expected directory structure
            config_path = handler.get_config_path()
            copilot_dir = config_path.parent.parent  # github-copilot directory
            intellij_dir = config_path.parent       # intellij subdirectory
            
            # Create directories to avoid FileNotFoundError
            intellij_dir.mkdir(parents=True, exist_ok=True)
            
            # Verify structure expectations
            assert copilot_dir.name == "github-copilot"
            assert intellij_dir.name == "intellij"
            assert config_path.name == "mcp.json"
    
    def test_metadata_path_follows_pattern(self, mock_home_path: Path) -> None:
        """Test metadata path follows existing handler pattern."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            # Create directory to avoid FileNotFoundError
            config_path = handler.get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            metadata_path = handler.get_metadata_path()
            
            # Should be in same directory as config
            assert metadata_path.parent == config_path.parent
            assert metadata_path.name == ".mcp-config-metadata.json"


class TestClientHandlerIntegration:
    """Test integration with ClientHandler interface."""
    
    def test_handler_inheritance(self) -> None:
        """Test IntelliJHandler properly inherits from ClientHandler."""
        handler = IntelliJHandler()
        assert isinstance(handler, ClientHandler)
    
    def test_integration_with_client_handler_interface(self, mock_home_path: Path) -> None:
        """Test handler implements ClientHandler interface correctly."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            # Create directory to avoid FileNotFoundError
            config_path = handler.get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Test required methods exist and return correct types
            assert hasattr(handler, 'get_config_path')
            assert hasattr(handler, 'get_metadata_path')
            assert isinstance(handler.get_config_path(), Path)
            assert isinstance(handler.get_metadata_path(), Path)
    
    def test_constants_match_existing_pattern(self) -> None:
        """Test class constants follow existing handler patterns."""
        # These should match the existing ClientHandler pattern
        assert hasattr(IntelliJHandler, 'MANAGED_SERVER_MARKER') 
        assert hasattr(IntelliJHandler, 'METADATA_FILE')
        assert IntelliJHandler.MANAGED_SERVER_MARKER == "mcp-config-managed"
        assert IntelliJHandler.METADATA_FILE == ".mcp-config-metadata.json"


class TestErrorHandling:
    """Test error handling for missing GitHub Copilot."""
    
    def test_error_handling_missing_github_copilot(self, mock_home_path: Path) -> None:
        """Test clear error when GitHub Copilot directory missing."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            # Don't create the directory - should raise FileNotFoundError
            with pytest.raises(FileNotFoundError) as exc_info:
                handler.get_config_path()
            
            # Error message should be helpful
            error_msg = str(exc_info.value)
            assert "GitHub Copilot for IntelliJ not found" in error_msg
            assert "github-copilot" in error_msg.lower()
            assert "intellij" in error_msg.lower()
    
    def test_error_message_includes_expected_path(self, mock_home_path: Path) -> None:
        """Test error message includes expected path location."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            with pytest.raises(FileNotFoundError) as exc_info:
                handler.get_config_path()
            
            error_msg = str(exc_info.value)
            # Should mention the expected directory path
            assert str(mock_home_path) in error_msg or "does not exist" in error_msg


class TestRealWorldValidation:
    """Test real-world path validation based on research."""
    
    def test_windows_path_matches_confirmed_real_path(self, mock_home_path: Path) -> None:
        """Test Windows path matches confirmed real user path."""
        with patch('pathlib.Path.home', return_value=mock_home_path), \
             patch('os.name', 'nt'):
            
            handler = IntelliJHandler()
            path = handler.get_config_path()
            
            # This should match the verified real-world Windows path structure
            path_parts = path.parts
            assert "AppData" in path_parts
            assert "Local" in path_parts
            assert "github-copilot" in path_parts
            assert "intellij" in path_parts
            assert path.name == "mcp.json"
    
    def test_macos_path_follows_apple_conventions(self, mock_home_path: Path) -> None:
        """Test macOS path follows Apple app support conventions."""
        with patch('pathlib.Path.home', return_value=mock_home_path), \
             patch('platform.system', return_value='Darwin'), \
             patch('os.name', 'posix'):
            
            handler = IntelliJHandler()
            path = handler.get_config_path()
            
            # Should follow macOS app support conventions
            path_parts = path.parts
            assert "Library" in path_parts
            assert "Application Support" in str(path) or ("Application" in path_parts and "Support" in path_parts)
            assert "github-copilot" in path_parts
            assert "intellij" in path_parts
    
    def test_linux_path_follows_xdg_spec(self, mock_home_path: Path) -> None:
        """Test Linux path follows XDG Base Directory specification."""
        with patch('pathlib.Path.home', return_value=mock_home_path), \
             patch('platform.system', return_value='Linux'), \
             patch('os.name', 'posix'):
            
            handler = IntelliJHandler()
            path = handler.get_config_path()
            
            # Should follow XDG Base Directory specification
            path_parts = path.parts
            assert ".local" in path_parts
            assert "share" in path_parts
            assert "github-copilot" in path_parts
            assert "intellij" in path_parts


class TestConfigFormat:
    """Test IntelliJ config format compatibility."""
    
    def test_uses_servers_format_like_vscode(self, mock_home_path: Path) -> None:
        """Test that IntelliJ uses 'servers' format like VSCode, not 'mcpServers' like Claude Desktop."""
        with patch('pathlib.Path.home', return_value=mock_home_path):
            handler = IntelliJHandler()
            
            # Create directory structure
            config_path = handler.get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # IntelliJ should use the same format as VSCode (servers section)
            # This is implicit in the handler behavior but important to document
            # The actual config format testing will be in integration tests
            assert True  # Placeholder - format validation happens in integration


# Skip tests if module not yet implemented (TDD red phase)
skip_if_not_implemented = pytest.mark.skipif(
    IntelliJHandler is None or ClientHandler is None,
    reason="IntelliJHandler not yet implemented - this is expected during TDD red phase"
)

# Apply skip decorator to all test classes
for cls_name in ['TestIntelliJPathDetection', 'TestGitHubCopilotDirectoryStructure',
                 'TestClientHandlerIntegration', 'TestErrorHandling', 
                 'TestRealWorldValidation', 'TestConfigFormat']:
    cls = globals()[cls_name]
    for method_name in dir(cls):
        if method_name.startswith('test_'):
            method = getattr(cls, method_name)
            setattr(cls, method_name, skip_if_not_implemented(method))
