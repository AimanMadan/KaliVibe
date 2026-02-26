from mcp.server.fastmcp import FastMCP
from src.terminal.session import BashSession
import os

# Initialize the FastMCP server
mcp = FastMCP("KaliVibe")

# Initialize the terminal session
bash = BashSession()


def resolve_path(filepath: str) -> str:
    """Helper function to sync Python's file operations with the bash session's current directory."""
    filepath = os.path.expanduser(filepath)
    # If the LLM provided a relative path (e.g., "script.py" instead of "/tmp/script.py")
    if not os.path.isabs(filepath):
        # Ask the bash session for its true current working directory
        current_bash_dir = bash.execute("pwd").strip()
        filepath = os.path.join(current_bash_dir, filepath)
    return filepath


@mcp.tool()
def execute_command(command: str) -> str:
    """Executes a bash command in a persistent Kali Linux terminal and returns the output.
    Use this to navigate directories, run scripts, enumerate the system, and manage processes.
    IMPORTANT: You are running in a persistent state. If you change directories (cd), you stay there.

    Args:
        command: The exact bash command or script to execute in the terminal.
    """
    try:
        output = bash.execute(command)
        # If a command succeeds but has no output (like 'mkdir folder'), explicitly tell the LLM
        return (
            output
            if output
            else f"Command '{command}' executed successfully with no output."
        )
    except Exception as e:
        return f"Error executing command: {str(e)}"


@mcp.tool()
def read_file(filepath: str) -> str:
    """
    Reads the contents of a file directly using Python.
    Use this instead of 'cat', 'less', or 'nano' through the terminal for cleaner, reliable output.

    Args:
        filepath: The absolute or relative path to the file you want to read (e.g., '/etc/passwd' or 'script.sh').
    """
    # Sync with bash session's current directory
    filepath = resolve_path(filepath)

    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' does not exist."
    if not os.path.isfile(filepath):
        return f"Error: '{filepath}' is a directory, not a file. Use 'ls' instead."

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """
    Writes raw content to a file, overwriting it if it exists.
    Use this instead of 'echo' or 'cat' via the terminal when creating or modifying
    scripts, configuration files, or any multi-line text. This avoids bash escaping issues.

    Args:
        filepath: The absolute or relative path where the file should be written.
        content: The raw, unescaped string content to write into the file.
    """
    # Sync with bash session's current directory
    filepath = resolve_path(filepath)

    try:
        # Ensure the directory exists before trying to write the file
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{filepath}'."
    except Exception as e:
        return f"Error writing to file: {str(e)}"


def run_server():
    """Entry point to start the MCP server using standard input/output transport."""
    # This locks the process and listens for JSON-RPC messages from the LLM via stdio
    mcp.run()


if __name__ == "__main__":
    run_server()
