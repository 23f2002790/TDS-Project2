from typing import List
from langchain_core.tools import tool
import subprocess

@tool
def add_dependencies(dependencies: List[str]) -> str:
    """
    Install additional Python dependencies dynamically using uv add
    """
    try:
        subprocess.check_call(
            ["uv", "add"] + dependencies,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return "Successfully installed dependencies: " + ", ".join(dependencies)

    except subprocess.CalledProcessError as e:
        return (
            "Dependency installation failed.\n"
            f"Exit code: {e.returncode}\n"
            f"Error: {e.stderr or 'No error output.'}"
        )

    except Exception as e:
        return f"Unexpected error: {e}"
