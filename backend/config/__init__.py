"""
Configuration package.
Loads environment variables, settings, and other app-wide configurations.
"""

from pathlib import Path

# Project Root (AI-multi-agent-Hub-for-Gaming/)
BASE_DIR = Path(__file__).resolve().parents[2]

# Directory where uploaded files are stored
UPLOAD_DIR = BASE_DIR / "uploads"

