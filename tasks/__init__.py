"""
Task Tools Package

This package provides modular helper tools used by the LangGraph agent
to interact with quiz pages and execute data processing tasks.

Exposed Tools:
--------------
- get_rendered_html: Load dynamic webpages using Playwright.
- download_file: Download files needed for analysis.
- post_request: Submit answers to quiz endpoints.
- run_code: Execute dynamically generated Python code.
- add_dependencies: Install missing Python dependencies automatically.
"""

from .web_scraper import get_rendered_html
from .download_file import download_file
from .send_request import post_request
from .run_code import run_code
from .add_dependencies import add_dependencies

__all__ = [
    "get_rendered_html",
    "download_file",
    "post_request",
    "run_code",
    "add_dependencies"
]
