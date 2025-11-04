"""Tests for help system module (step 4B implementation)."""

import pytest

from src.mcp_config.help_system import (
    INTELLIJ_SUPPORT_HELP,
    CommandHelpFormatter,
    print_command_help,
    print_intellij_support_help,
    print_parameter_help,
)


class TestIntelliJHelpSupport:
    """Test IntelliJ support in help system (step 4B)."""

    def test_intellij_support_help_constant(self) -> None:
        """Test that INTELLIJ_SUPPORT_HELP constant is defined and contains expected content."""
        assert INTELLIJ_SUPPORT_HELP is not None
        assert "IntelliJ/PyCharm Support" in INTELLIJ_SUPPORT_HELP
        assert "claude-desktop" in INTELLIJ_SUPPORT_HELP
        assert "claude-code" in INTELLIJ_SUPPORT_HELP
        assert "vscode-*" in INTELLIJ_SUPPORT_HELP
        assert "intellij" in INTELLIJ_SUPPORT_HELP
        assert "GitHub Copilot" in INTELLIJ_SUPPORT_HELP
        assert '"servers"' in INTELLIJ_SUPPORT_HELP

    def test_print_intellij_support_help(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print_intellij_support_help prints the expected content."""
        result = print_intellij_support_help()
        assert result == 0

        captured = capsys.readouterr()
        assert "IntelliJ/PyCharm Support" in captured.out
        assert "claude-code     → .mcp.json (project root)" in captured.out
        assert "intellij        → mcp.json (GitHub Copilot)" in captured.out

    def test_tool_overview_mentions_multiple_clients(self) -> None:
        """Test that format_tool_overview mentions VSCode and IntelliJ."""
        overview = CommandHelpFormatter.format_tool_overview()
        assert "Claude Desktop, VSCode, and IntelliJ/PyCharm" in overview
        assert "Multi-Client Support:" in overview
        assert "claude-desktop  → claude_desktop_config.json" in overview
        assert "claude-code     → .mcp.json (project root)" in overview
        assert "vscode-*        → .vscode/mcp.json" in overview
        assert "intellij        → GitHub Copilot mcp.json" in overview

    def test_setup_command_help_mentions_all_clients(self) -> None:
        """Test that setup command help mentions all supported clients."""
        help_text = CommandHelpFormatter.format_setup_command_help()
        assert "any supported MCP client" in help_text
        assert (
            "claude-desktop, claude-code, vscode-workspace, vscode-user, intellij"
            in help_text
        )

    def test_setup_command_verbose_help_explains_clients(self) -> None:
        """Test that verbose setup help explains each client type."""
        help_text = CommandHelpFormatter.format_setup_command_help(verbose=True)
        assert "claude-desktop: Claude Desktop app configuration" in help_text
        assert (
            "claude-code: Claude Code CLI project configuration (.mcp.json)"
            in help_text
        )
        assert (
            "vscode-workspace: VSCode workspace .vscode/mcp.json (team sharing)"
            in help_text
        )
        assert "vscode-user: VSCode user profile (personal, all projects)" in help_text
        assert "intellij: IntelliJ/PyCharm GitHub Copilot integration" in help_text

    def test_setup_command_examples_include_intellij(self) -> None:
        """Test that setup command examples include IntelliJ usage."""
        help_text = CommandHelpFormatter.format_setup_command_help()
        assert "Setup for Claude Code project" in help_text
        assert "--client claude-code" in help_text
        assert "code-proj" in help_text
        assert "Setup for IntelliJ/PyCharm GitHub Copilot" in help_text
        assert "--client intellij" in help_text
        assert "intellij-proj" in help_text

    def test_remove_command_help_mentions_all_clients(self) -> None:
        """Test that remove command help mentions all supported clients."""
        help_text = CommandHelpFormatter.format_remove_command_help()
        assert "any supported MCP client" in help_text
        assert (
            "claude-desktop, claude-code, vscode-workspace, vscode-user, intellij"
            in help_text
        )

    def test_remove_command_examples_include_intellij(self) -> None:
        """Test that remove command examples include IntelliJ usage."""
        help_text = CommandHelpFormatter.format_remove_command_help()
        assert "Remove from Claude Code project" in help_text
        assert "code-proj --client claude-code" in help_text
        assert "Remove from IntelliJ" in help_text
        assert "intellij-proj --client intellij" in help_text

    def test_list_command_help_mentions_all_clients(self) -> None:
        """Test that list command help mentions all supported clients."""
        help_text = CommandHelpFormatter.format_list_command_help()
        assert "across supported MCP clients" in help_text
        assert (
            "claude-desktop, claude-code, vscode-workspace, vscode-user, intellij"
            in help_text
        )

    def test_list_command_examples_include_intellij(self) -> None:
        """Test that list command examples include IntelliJ usage."""
        help_text = CommandHelpFormatter.format_list_command_help()
        assert "--client claude-code" in help_text
        assert "--client intellij" in help_text

    def test_validate_command_help_mentions_all_clients(self) -> None:
        """Test that validate command help mentions all supported clients."""
        help_text = CommandHelpFormatter.format_validate_command_help()
        assert (
            "claude-desktop, claude-code, vscode-workspace, vscode-user, intellij"
            in help_text
        )

    def test_validate_command_examples_include_intellij(self) -> None:
        """Test that validate command examples include IntelliJ usage."""
        help_text = CommandHelpFormatter.format_validate_command_help()
        assert "code-proj --client claude-code" in help_text
        assert "intellij-proj --client intellij" in help_text

    def test_help_command_recognizes_intellij_topic(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that help command recognizes 'intellij' as a valid topic."""
        result = print_command_help("intellij")
        assert result == 0

        captured = capsys.readouterr()
        assert "IntelliJ/PyCharm Support" in captured.out

    def test_help_command_topics_include_intellij(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that help command topics list includes IntelliJ."""
        result = print_command_help("help")
        assert result == 0

        captured = capsys.readouterr()
        assert (
            "intellij           Show IntelliJ/PyCharm setup information" in captured.out
        )

    def test_help_command_examples_include_intellij(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that help command examples include IntelliJ."""
        result = print_command_help("help")
        assert result == 0

        captured = capsys.readouterr()
        assert (
            "mcp-config help intellij            # IntelliJ/PyCharm setup info"
            in captured.out
        )


class TestMultiClientConsistency:
    """Test that multi-client support is consistently represented."""

    def test_all_commands_mention_multi_client_support(self) -> None:
        """Test that all command help texts mention multi-client support appropriately."""
        # Setup command should mention "any supported MCP client"
        setup_help = CommandHelpFormatter.format_setup_command_help()
        assert "any supported MCP client" in setup_help

        # Remove command should mention "any supported MCP client"
        remove_help = CommandHelpFormatter.format_remove_command_help()
        assert "any supported MCP client" in remove_help

        # List command should mention "across supported MCP clients"
        list_help = CommandHelpFormatter.format_list_command_help()
        assert "across supported MCP clients" in list_help

    def test_client_choices_consistent_across_commands(self) -> None:
        """Test that client choices are consistently listed across all commands."""
        expected_choices = (
            "claude-desktop, claude-code, vscode-workspace, vscode-user, intellij"
        )

        commands = [
            CommandHelpFormatter.format_setup_command_help(),
            CommandHelpFormatter.format_remove_command_help(),
            CommandHelpFormatter.format_list_command_help(),
            CommandHelpFormatter.format_validate_command_help(),
        ]

        for command_help in commands:
            assert expected_choices in command_help

    def test_examples_cover_all_major_clients(self) -> None:
        """Test that examples across commands cover all major client types."""
        # Setup command examples
        setup_help = CommandHelpFormatter.format_setup_command_help()
        assert "--client claude-code" in setup_help
        assert "--client vscode-workspace" in setup_help
        assert "--client intellij" in setup_help

        # Remove command examples
        remove_help = CommandHelpFormatter.format_remove_command_help()
        assert "--client claude-code" in remove_help
        assert "--client vscode-workspace" in remove_help
        assert "--client intellij" in remove_help

        # List command examples
        list_help = CommandHelpFormatter.format_list_command_help()
        assert "--client claude-code" in list_help
        assert "--client intellij" in list_help

        # Validate command examples
        validate_help = CommandHelpFormatter.format_validate_command_help()
        assert "--client claude-code" in validate_help
        assert "--client intellij" in validate_help
