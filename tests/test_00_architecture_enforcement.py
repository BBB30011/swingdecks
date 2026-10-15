import os
import pytest
from pathlib import Path

def test_canonical_root_structure():
    """
    Ensures that no rogue "ghost" files or directories are created at the repository root.
    Only strictly whitelisted canonical paths are allowed.
    """
    root_dir = Path(__file__).parent.parent.resolve()
    
    # Define strictly allowed canonical entries
    allowed_dirs = {
        # Core Architecture & Operational Runtime
        "agents", "configs", "core", "dashboard", "data", "docs", "gates", "governance", 
        "knowledge", "logs", "positions", "queue", "reports", "research", 
        "runtime", "scratch", "scripts", "state", "tests",
        
        # Local Environment / Git / Agent Workspace / GitHub
        ".agents", ".git", ".github", ".pytest_cache", ".venv", "__pycache__"
    }

    allowed_files = {
        "main.py", 
        "README.md", 
        "CONTRIBUTING.md",
        "LICENSE",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        ".env.example",
        "requirements.txt",
        ".gitignore", 
        "conftest.py",
        "pytest.ini"
    }
    
    rogue_entries = []
    
    for entry in root_dir.iterdir():
        name = entry.name
        
        if entry.is_dir():
            if name not in allowed_dirs:
                rogue_entries.append(f"Ghost Directory: {name}/")
        elif entry.is_file():
            if name not in allowed_files:
                rogue_entries.append(f"Ghost File: {name}")
                
    if rogue_entries:
        error_msg = (
            "ARCHITECTURE VIOLATION: Rogue files or directories found at repository root.\n"
            "The SwingDeck repository operates on a strict Single Source of Truth architecture.\n"
            "Please remove the following items or add them to the canonical structure if intended:\n" +
            "\n".join(f"- {e}" for e in rogue_entries)
        )
        pytest.fail(error_msg)
