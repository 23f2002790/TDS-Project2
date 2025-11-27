from langchain_core.tools import tool
import requests
import os
import re

@tool
def download_file(url: str, filename: str = None) -> str:
    """
    Download a file from a direct link. 
    Stores everything inside /LLMFiles for consistency.

    If filename is not provided → extract filename from URL.
    Returns the local path so it can be used in analysis code.
    """

    try:
        os.makedirs("LLMFiles", exist_ok=True)

        # Auto filename if missing
        if not filename:
            filename = url.split("/")[-1]
            # Basic cleanup → remove query params if present
            filename = re.sub(r"[?#].*$", "", filename)

        save_path = os.path.join("LLMFiles", filename)

        print(f"\n⬇ Downloading file: {url}")
        print(f"📁 Saving as: {save_path}")

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print("✔ File download complete\n")
        return save_path  # important!

    except Exception as e:
        error_msg = f"Download failed: {e}"
        print("❌", error_msg)
        return error_msg
