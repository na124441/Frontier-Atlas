"""
Root entry point for the Rich Interactive CLI application.
Allows running `python cli.py` directly from the repository root.
"""

import sys
from pathlib import Path

# Ensure src/ is in sys.path
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from intelligent_scraper.cli import main

if __name__ == "__main__":
    main()
