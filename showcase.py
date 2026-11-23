"""
All-in-One Automated Video Showcase & Interactive TUI Launcher.
Wraps all commands into a single executable Python program.

Usage:
    python showcase.py              # Runs the interactive showcase menu
    python showcase.py --auto       # Runs the automated 2-minute non-voiceovered video demo!
"""

import sys
import os
import subprocess
from pathlib import Path

# --- Configuration & Environment Setup ---
PYTHON_312 = r"C:\Users\nayan\AppData\Roaming\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe"
VENV_DIR = r"C:\Users\nayan\.venv_scraper"
VENV_PACKAGES = r"C:\Users\nayan\.venv_scraper\Lib\site-packages"
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

# Auto-re-exec under Python 3.12 if started under Python 3.14 / other launcher
if sys.version_info[:2] != (3, 12):
    if Path(PYTHON_312).exists():
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = VENV_DIR
        env["PYTHONPATH"] = f"{SRC_DIR};{VENV_PACKAGES};{env.get('PYTHONPATH', '')}"
        res = subprocess.run([PYTHON_312, str(ROOT_DIR / "showcase.py")] + sys.argv[1:], env=env)
        sys.exit(res.returncode)

# Add paths directly
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box

from intelligent_scraper.cli import (
    render_banner,
    render_system_dashboard,
    render_architecture,
    render_entity_result_card,
    run_entity_resolver_flow,
    run_data_viewer_flow,
    run_test_suite_diagnostics,
    main_interactive,
    EntityResolver,
    SEED_STARTUPS
)

console = Console()


def run_automated_video_demo():
    """
    Runs the automated 2-minute non-voiceovered showcase demo.
    Automatically displays each screen with cinematic pauses,
    perfect for starting screen recording and letting it play!
    """
    console.clear()
    
    # ── Scene 1: Banner & System Status (25s) ──
    console.print(Panel(
        "[bold bright_cyan]🎬 SCENE 1/4: PLATFORM STATUS & DASHBOARD[/bold bright_cyan]\n"
        "[dim]FrontierAtlas AI Engineer Assessment Platform[/dim]",
        box=box.ROUNDED, border_style="cyan"
    ))
    render_banner(animate=False)
    render_system_dashboard()
    time.sleep(8)

    # ── Scene 2: System Architecture Diagram (25s) ──
    console.print(Panel(
        "[bold bright_cyan]🎬 SCENE 2/4: FULL 6-STAGE SYSTEM ARCHITECTURE[/bold bright_cyan]\n"
        "[dim]Two-tier adaptive crawling, LLM fallback chain, and 24h freshness filter[/dim]",
        box=box.ROUNDED, border_style="cyan"
    ))
    render_architecture()
    time.sleep(10)

    # ── Scene 3: Deterministic Entity Resolution (25s) ──
    console.print(Panel(
        "[bold bright_cyan]🎬 SCENE 3/4: DETERMINISTIC ENTITY RESOLUTION (FR-12)[/bold bright_cyan]\n"
        "[dim]Normalizing corporate noise into canonical seed registry[/dim]",
        box=box.ROUNDED, border_style="cyan"
    ))
    resolver = EntityResolver()
    
    samples = ["Open AI Inc", "Anthropic PBC", "Mistral AI SAS"]
    for sample in samples:
        resolved = resolver.resolve_entity(sample)
        norm = resolver.normalize_name(sample)
        exact = resolver.exact_match(sample) is not None
        render_entity_result_card(sample, resolved, norm, exact, resolved in SEED_STARTUPS)
        time.sleep(4)

    # ── Scene 4: 6-Tab Data Intelligence Explorer (25s) ──
    console.print(Panel(
        "[bold bright_cyan]🎬 SCENE 4/4: DATA INTELLIGENCE EXPLORER & 6-TAB EXPORTS (FR-17)[/bold bright_cyan]\n"
        "[dim]Structured multi-tab export across Startups, Products, Papers, Jobs, News, and Mappings[/dim]",
        box=box.ROUNDED, border_style="cyan"
    ))
    import asyncio
    asyncio.run(run_data_viewer_flow(specific_tab="A"))
    time.sleep(6)

    console.print(Panel(
        "[bold bright_green]✅ VIDEO DEMO COMPLETE — ALL CAPABILITIES DEMONSTRATED[/bold bright_green]\n"
        "[dim]FrontierAtlas / GraphOne AI Web Scraping Platform[/dim]",
        box=box.DOUBLE, border_style="bright_green"
    ))


def interactive_showcase_menu():
    """Interactive selector for the video showcase."""
    render_banner(animate=False)
    render_system_dashboard()

    menu = Table.grid(padding=(0, 2))
    menu.add_column(style="bold cyan", justify="right")
    menu.add_column(style="bold white")

    menu.add_row("[1]", "▶  Play Automated 2-Minute Video Demo (Hands-free recording!)")
    menu.add_row("[2]", "🏗️  Show System Architecture Diagram")
    menu.add_row("[3]", "🏢  Show Entity Resolution Card")
    menu.add_row("[4]", "📊  Show 6-Tab Data Overview")
    menu.add_row("[5]", "🚀  Launch Full Interactive TUI Dashboard")
    menu.add_row("[0]", "🚪  Exit")

    console.print(Panel(menu, title="[bold white]Showcase Launcher[/bold white]", box=box.ROUNDED, border_style="cyan"))

    choice = Prompt.ask("  [bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4", "5", "0"], default="1")

    if choice == "1":
        run_automated_video_demo()
    elif choice == "2":
        render_architecture()
    elif choice == "3":
        resolver = EntityResolver()
        resolved = resolver.resolve_entity("Open AI Inc")
        render_entity_result_card("Open AI Inc", resolved, "open", False, True)
    elif choice == "4":
        import asyncio
        asyncio.run(run_data_viewer_flow(specific_tab="A"))
    elif choice == "5":
        import asyncio
        asyncio.run(main_interactive())


if __name__ == "__main__":
    if "--auto" in sys.argv:
        run_automated_video_demo()
    else:
        interactive_showcase_menu()
