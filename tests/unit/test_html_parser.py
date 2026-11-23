"""Unit tests for HTML Parser and Cleaner."""
import pytest
from intelligent_scraper.extraction.html_parser import HTMLParser
from intelligent_scraper.extraction.content_cleaner import ContentCleaner


def test_html_parser_title_and_links():
    html = """
    <html>
        <head>
            <title>Anthropic Launches Claude 3.5</title>
            <meta property="og:title" content="Claude 3.5 Sonnet Release" />
            <link rel="canonical" href="https://anthropic.com/news/claude-3-5" />
        </head>
        <body>
            <header><nav><a href="/home">Home</a></nav></header>
            <main>
                <h1>Claude 3.5 Sonnet</h1>
                <p>Anthropic today announced its newest frontier model.</p>
                <a href="/research">Research Paper</a>
                <a href="https://external.org/benchmarks">Benchmarks</a>
            </main>
            <footer>Copyright 2024</footer>
        </body>
    </html>
    """
    parser = HTMLParser()
    title = parser.extract_title(html)
    assert title == "Anthropic Launches Claude 3.5"

    links = parser.extract_links(html, base_url="https://anthropic.com")
    assert "https://anthropic.com/research" in links
    assert "https://external.org/benchmarks" in links
    assert "https://anthropic.com/home" in links


def test_content_cleaner_removes_boilerplate():
    html = """
    <html>
        <body>
            <nav>Navigation Bar</nav>
            <script>var x = 10;</script>
            <style>.test{color:red;}</style>
            <article>
                <h1>Deep Learning Breakthrough</h1>
                <p>Researchers have discovered a new optimization algorithm.</p>
            </article>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    cleaner = ContentCleaner()
    cleaned = cleaner.clean_content(html)
    assert "Navigation Bar" not in cleaned
    assert "var x = 10" not in cleaned
    assert "Footer content" not in cleaned
    assert "Deep Learning Breakthrough" in cleaned
    assert "Researchers have discovered" in cleaned
