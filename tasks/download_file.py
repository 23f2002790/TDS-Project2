from langchain_core.tools import tool
import requests
import os

@tool
def download_file(url: str, filename: str) -> str:
    """
    Download a file and save into LLMFiles/ folder.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        directory = "LLMFiles"
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)

        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return filename

    except Exception as e:
        return f"Error downloading file: {str(e)}"
