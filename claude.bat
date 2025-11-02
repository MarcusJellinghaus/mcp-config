@echo off
REM Simple launcher for Claude Code with MCP servers

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Set project directories for MCP servers
set "MCP_CODER_PROJECT_DIR=%CD%"
set "MCP_CODER_VENV_DIR=%CD%\claude-mcp\.venv"

REM Start Claude Code
echo Starting Claude Code with:
echo VIRTUAL_ENV=%VIRTUAL_ENV%
echo MCP_CODER_PROJECT_DIR=%MCP_CODER_PROJECT_DIR%
echo MCP_CODER_VENV_DIR=%MCP_CODER_VENV_DIR%
C:\Users\%USERNAME%\.local\bin\claude.exe %*
