"""
Task tools used by the autonomous quiz solver agent.

Each tool is exposed as a LangChain-compatible callable.
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
    "add_dependencies",
]
