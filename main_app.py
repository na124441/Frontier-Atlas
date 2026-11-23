"""
FrontierAtlas — Intelligent AI Web Scraping & Data Platform
Simple, User-Friendly Interactive Assistant.

Just run:
    python main_app.py
    or
    py main_app.py
"""

import sys
import os
import subprocess
from pathlib import Path

# --- Environment Auto-Configuration ---
PYTHON_312 = r"C:\Users\nayan\AppData\Roaming\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe"
VENV_DIR = r"C:\Users\nayan\.venv_scraper"
VENV_PACKAGES = r"C:\Users\nayan\.venv_scraper\Lib\site-packages"
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

# Auto-re-exec under Python 3.12 if started under Python 3.14 or unconfigured launcher
if sys.version_info[:2] != (3, 12):
    if Path(PYTHON_312).exists():
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = VENV_DIR
        env["PYTHONPATH"] = f"{SRC_DIR};{VENV_PACKAGES};{env.get('PYTHONPATH', '')}"
        res = subprocess.run([PYTHON_312, str(ROOT_DIR / "main_app.py")] + sys.argv[1:], env=env)
        sys.exit(res.returncode)

# Ensure paths
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import box

from intelligent_scraper.cli import (
    render_banner,
    render_system_dashboard,
    render_architecture,
    render_entity_result_card,
    run_pipeline_flow,
    run_discovery_flow,
    run_data_viewer_flow,
    run_export_flow,
    run_test_suite_diagnostics,
    EntityResolver,
    SEED_STARTUPS
)

console = Console()


def display_welcome():
    render_banner(animate=False)
    render_system_dashboard()
    
    welcome_text = (
        "[bold bright_white]Welcome to FrontierAtlas Intelligent Web Crawler![/bold bright_white]\n\n"
        "[dim]This tool allows you to scrape AI startups, products, research papers, jobs, and news,\n"
        "resolve entity names, and export structured data to Google Sheets & CSV.[/dim]"
    )
    console.print(Panel(welcome_text, title="[bold cyan]User Guide[/bold cyan]", box=box.ROUNDED, border_style="cyan"))
    console.print()


def user_friendly_menu():
    while True:
        display_welcome()

        menu = Table(box=box.ROUNDED, border_style="bright_blue", show_header=True, header_style="bold bright_cyan", expand=True)
        menu.add_column("Option", style="bold yellow", width=10, justify="center")
        menu.add_column("Action", style="bold white", width=35)
        menu.add_column("Description", style="dim")

        menu.add_row("[1]", "🚀 Start Web Scraping", "Crawl live web sources, extract entities with LLMs, and export to CSV")
        menu.add_row("[2]", "🔍 Discover Web URLs", "Find new URLs from 14+ sources (YC, arXiv, TechCrunch, Job boards)")
        menu.add_row("[3]", "🏢 Test Entity Resolver", "Type any company name (e.g. 'Open AI Inc') to see how it canonicalizes")
        menu.add_row("[4]", "📊 View Scraped Data", "Browse the 6 exported data tabs (Startups, Products, Papers, Jobs, News)")
        menu.add_row("[5]", "📁 Export Current Data", "Re-export database records to Google Sheets and local CSV files")
        menu.add_row("[6]", "🏗️ View Architecture", "See visual ASCII diagram of the 6-stage crawling & intelligence pipeline")
        menu.add_row("[7]", "🧪 Run Diagnostics", "Run all 30 automated tests to verify system integrity")
        menu.add_row("[0]", "🚪 Exit", "Close the application")

        console.print(menu)
        console.print()

        choice = Prompt.ask("  [bold bright_cyan]What would you like to do?[/bold bright_cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "0"], default="1")

        if choice == "1":
            console.print()
            tasks = IntPrompt.ask("  [bold cyan]How many pages would you like to crawl?[/bold cyan]", default=5)
            console.print()
            asyncio.run(run_pipeline_flow(max_tasks=tasks))
            Prompt.ask("\n  [dim]Press Enter to return to main menu...[/dim]")

        elif choice == "2":
            console.print()
            asyncio.run(run_discovery_flow())
            Prompt.ask("\n  [dim]Press Enter to return to main menu...[/dim]")

        elif choice == "3":
            console.print()
            resolver = EntityResolver()
            console.print("  [white]Try entering company names with noise, e.g.:[/white]")
            console.print("  [yellow]• Open AI Inc    • Mistral AI SAS    • Anthropic PBC    • Anysphere Cursor[/yellow]\n")
            while True:
                name = Prompt.ask("  [bold cyan]Enter company name (or press Enter to return)[/bold cyan]", default="")
                if not name.strip():
                    break
                resolved = resolver.resolve_entity(name)
                norm = resolver.normalize_name(name)
                exact = resolver.exact_match(name) is not None
                render_entity_result_card(name, resolved, norm, exact, resolved in SEED_STARTUPS)
                console.print()

        elif choice == "4":
            console.print()
            asyncio.run(run_data_viewer_flow())
            Prompt.ask("\n  [dim]Press Enter to return to main menu...[/dim]")

        elif choice == "5":
            console.print()
            asyncio.run(run_export_flow())
            Prompt.ask("\n  [dim]Press Enter to return to main menu...[/dim]")

        elif choice == "6":
            console.print()
            render_architecture()
            Prompt.ask("\n  [dim]Press Enter to return to main menu...[/dim]")

        elif choice == "7":
            console.print()
            run_test_suite_diagnostics()
            Prompt.ask("\n  [dim]Press Enter to return to main menu...[/dim]")

        elif choice == "0":
            console.print("\n  [bold cyan]Thank you for using FrontierAtlas! Goodbye.[/bold cyan]\n")
            break


if __name__ == "__main__":
    try:
        user_friendly_menu()
    except KeyboardInterrupt:
        console.print("\n\n  [dim]Application closed by user.[/dim]\n")
