#!/usr/bin/env python3
"""Start the MCP server locally with config from claude_desktop_config.json."""

import json
import os
import subprocess
import sys
from pathlib import Path

config_path = Path(__file__).parent / "claude_desktop_config.json"
if not config_path.exists():
    print(f"Error: {config_path} not found.")
    sys.exit(1)

config = json.loads(config_path.read_text())
env_vars = config["mcpServers"]["trilium-presenter"]["env"]

server = Path(__file__).parent / "server.py"
subprocess.run([sys.executable, server], env={**os.environ, **env_vars})
