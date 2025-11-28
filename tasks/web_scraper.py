from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

@tool
def get_rendered_html(url: str) -> str:
    """
    Returns fully rendered HTML of a webpage using Playwright.

    Use only for real webpages. 
    Do NOT use for direct file links like CSV/PDF/Images.
    """
    print("\n➡ Fetching and rendering:", url)

    # Block obvious non-HTML links
    if url.lower().endswith((".csv", ".pdf", ".xlsx", ".png", ".jpg", ".zip")):
        return "NOT_HTML_URL"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="networkidle")
            html = page.content()

            page.close()
            browser.close()
            return html
            
    except Exception as e:
        return f"Error loading page: {str(e)}"
