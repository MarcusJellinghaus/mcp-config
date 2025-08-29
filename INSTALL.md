# Installation

## Requirements
- Python 3.11+
- pip

## Install
```bash
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git
```

## Development Install
```bash
git clone https://github.com/MarcusJellinghaus/mcp-config.git
cd mcp-config
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Verify Installation
```bash
mcp-config --help
```

## Troubleshooting
If command not found:
```bash
python -m mcp_config --help
```
