# Contributing

## Development Setup
```bash
git clone https://github.com/MarcusJellinghaus/mcp-config.git
cd mcp-config
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

pip uninstall mcp-code-checker mcp-server-filesystem
pip install "mcp-code-checker @ git+https://github.com/MarcusJellinghaus/mcp-code-checker.git"
pip install "mcp-server-filesystem @ git+https://github.com/MarcusJellinghaus/mcp_server_filesystem.git"

```

## Development Tools
```bash
# Format code (runs ruff, black, isort)
./tools/format_all.bat          # Windows

# Run all checks and copy errors to clipboard for LLM analysis
./tools/checks2clipboard.bat    # Windows - runs pylint, pytest, mypy
                                # Copies detailed error output to clipboard
                                # for pasting into Claude/ChatGPT/etc.

# Individual tools
./tools/black.bat               # Code formatting
./tools/mypy.bat                # Type checking  
./tools/pylint_check_for_errors.bat  # Error checking

# Test installation
./tools/test_cli_installation.bat    # Windows
./tools/test_cli_installation.sh     # Unix/Linux/macOS

# Reinstall package
./tools/reinstall.bat           # Windows
```

## Manual Testing
```bash
# Run tests
pytest

# Test CLI directly
mcp-config --help
mcp-config validate
```

## Submit Changes
1. Fork repository
2. Create feature branch  
3. Run `./tools/format_all.bat` to fix formatting
4. Run `./tools/checks2clipboard.bat` to check for errors
5. If errors found, paste clipboard content to LLM for analysis
6. Make changes and add tests
7. Repeat steps 4-5 until all checks pass
8. Submit pull request
