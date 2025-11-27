from typing import List
from langchain_core.tools import tool
import subprocess


@tool
def add_dependencies(dependencies: List[str]) -> str:
    """
    Install additional Python packages if required by a quiz task.

    Used only when the LLM determines that a package is missing.
    Example: ["matplotlib", "tabula-py"]
    """

    if not dependencies:
        return "No dependencies provided."

    try:
        print(f"\n📦 Installing missing packages: {dependencies}\n")

        # Using 'python -m pip install' for max compatibility
        cmd = ["python", "-m", "pip", "install"] + dependencies
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"Successfully installed: {', '.join(dependencies)}"
        else:
            return (
                "Package installation failed.\n"
                f"Exit Code: {result.returncode}\n"
                f"Output: {result.stderr}"
            )

    except Exception as e:
        return f"Unexpected error while installing: {str(e)}"
