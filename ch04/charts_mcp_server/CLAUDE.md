# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Development Setup
```bash
# Activate virtual environment
source charts_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser for screenshot generation
playwright install chromium

# Configure MinIO credentials in config/.secrets.toml before running
# Start the MCP server
python main.py
```

### Configuration
- Main config: `config/settings.toml` - server, chart, and MinIO settings
- Secrets: `config/.secrets.toml` - MinIO access credentials (not in git)
- Environment variables can override settings with prefix `CHARTS_MCP_`

## Architecture Overview

This is a **FastMCP HTTP server** that generates charts and returns image URLs. The architecture follows a modular pattern:

### Core Flow
1. **MCP Tool Call** → Chart Generator → **HTML Render** → Screenshot → **MinIO Upload** → URL Return

### Key Components

**Configuration Layer** (`src/config.py`):
- Uses Dynaconf for hierarchical configuration management
- Supports environment variables, TOML files, and multiple environments
- Central `settings` object imported throughout the codebase

**Chart Generators** (`src/charts/`):
- Three separate generators: `bar_chart.py`, `pie_chart.py`, `line_chart.py`
- Each follows the same pattern: create pyecharts object → render HTML → screenshot → upload
- Theme mapping from string names to pyecharts ThemeType enums
- Extensive chart_options support for customization

**Screenshot Pipeline** (`src/utils/screenshot.py`):
- Async Playwright-based HTML-to-image conversion
- Auto-detects ECharts containers for optimal cropping
- Configurable viewport and wait times for chart rendering

**Storage Integration** (`src/storage/minio_client.py`):
- MinIO client with bucket auto-creation
- Presigned URL generation with configurable expiry
- Content-type detection and custom domain support

**Temporary File Management** (`src/utils/temp_files.py`):
- UUID-based temp file naming with automatic cleanup
- Exit handler registration for cleanup on shutdown

### MCP Tools Exposed
- `generate_bar_chart`: X-axis categories + multiple data series
- `generate_pie_chart`: Name-value pairs for pie segments  
- `generate_line_chart`: Time series or category-based line data
- `get_server_info`: Configuration and capabilities metadata

## Data Flow Architecture

**Input Validation**: MCP tools accept typed parameters (List[str], List[Dict[str, Any]])
**Chart Creation**: pyecharts objects with theme/option configuration
**HTML Generation**: Embedded charts in full HTML documents
**Screenshot**: Playwright captures chart area with smart cropping
**Upload**: MinIO with automatic bucket creation and URL generation
**Cleanup**: Automatic temp file removal with fallback exit handlers

## Configuration Patterns

The system uses a layered configuration approach:
- `config/settings.toml`: Base configuration for all environments
- `config/.secrets.toml`: Sensitive credentials (MinIO access keys)
- Environment variables: `CHARTS_MCP_*` prefixed overrides
- Default values: Embedded in the code as fallbacks

Critical configuration sections:
- `[mcp_server]`: HTTP server binding and path
- `[minio]`: Object storage connection and bucket settings
- `[charts]`: Default dimensions, theme, and temp directory
- `[screenshot]`: Playwright viewport and timing settings

## Error Handling Strategy

Each major component has its own error handling:
- **Chart Generation**: pyecharts validation and theme mapping errors
- **Screenshot**: Playwright timeout and element detection failures  
- **MinIO**: Connection, authentication, and upload failures
- **Temp Files**: Cleanup failures with graceful degradation

Errors are logged via loguru and propagated up to MCP tool level for client visibility.