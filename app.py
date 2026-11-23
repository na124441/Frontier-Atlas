"""
Self-contained root launcher for the FrontierAtlas Rich CLI.
Automatically respawns under Python 3.12 (matching the venv packages),
so running `py app.py` or `python app.py` works seamlessly from any Python.
"""

import sys
import os
import subprocess
from pathlib import Path

PYTHON_312 = r"C:\Users\nayan\AppData\Roaming\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe"
VENV_DIR = r"C:\Users\nayan\.venv_scraper"
VENV_PACKAGES = r"C:\Users\nayan\.venv_scraper\Lib\site-packages"
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

# If not running on Python 3.12, re-exec under the Python 3.12 interpreter
if sys.version_info[:2] != (3, 12):
    if Path(PYTHON_312).exists():
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = VENV_DIR
        env["PYTHONPATH"] = f"{SRC_DIR};{VENV_PACKAGES}"
        result = subprocess.run([PYTHON_312, str(ROOT_DIR / "cli.py")] + sys.argv[1:], env=env)
        sys.exit(result.returncode)
    else:
        print(f"Error: Python 3.12 interpreter required, but not found at {PYTHON_312}")
        sys.exit(1)

# If already running on Python 3.12, add paths directly and launch
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)

from intelligent_scraper.cli import main

if __name__ == "__main__":
    main()
