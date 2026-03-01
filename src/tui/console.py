"""Rich console and output helpers for the KaliVibe TUI."""

import json
import sys
import threading

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.text import Text


class RichUI:
    """UI abstraction that renders agent I/O with Rich (panels, markup, prompts)."""

    def __init__(self) -> None:
        self._console = Console()
        self._loading_stop: threading.Event | None = None
        self._loading_thread: threading.Thread | None = None

    def _run_loading_spinner(self) -> None:
        """Run a Live spinner until _loading_stop is set."""
        stop = self._loading_stop
        if not stop:
            return
        with Live(
            Panel(
                Spinner("dots", text="Waiting for agent response..."),
                title="[bold cyan]KaliVibe[/]",
                border_style="cyan",
            ),
            console=self._console,
            refresh_per_second=8,
            transient=True,
        ):
            while not stop.wait(timeout=0.1):
                pass

    def start_loading(self) -> None:
        """Show a loading spinner (runs in a background thread)."""
        if self._loading_thread is not None and self._loading_thread.is_alive():
            return
        self._loading_stop = threading.Event()
        self._loading_thread = threading.Thread(
            target=self._run_loading_spinner, daemon=True
        )
        self._loading_thread.start()

    def stop_loading(self) -> None:
        """Hide the loading spinner."""
        if self._loading_stop is not None:
            self._loading_stop.set()
        if self._loading_thread is not None:
            self._loading_thread.join(timeout=1.0)
        self._loading_stop = None
        self._loading_thread = None

    def print_boot(self, msg: str) -> None:
        """Print a system boot/status line."""
        self._console.print(f"[dim]{msg}[/]")

    def print_system(self, msg: str) -> None:
        """Print a system message (e.g. agent online, shutting down)."""
        self._console.print(Panel(msg, title="[System]", border_style="blue"))

    def print_agent(self, content: str) -> None:
        """Print the agent's text response."""
        self._console.print(
            Panel(
                Markdown(content), title="[bold green]KaliVibe[/]", border_style="green"
            )
        )

    def print_tool_call(self, name: str, args: dict) -> None:
        """Print a tool execution line."""
        args_str = json.dumps(args, indent=2) if args else "()"
        self._console.print(
            Text("⚙️  ", style="yellow")
            + Text(f"Executing: {name}", style="bold yellow")
        )
        self._console.print(
            Syntax(args_str, "json", theme="monokai", line_numbers=False)
        )

    def print_tool_result(self, text: str) -> None:
        """Print the result of a tool call."""
        self._console.print(
            Panel(text or "(no output)", title="Result", border_style="cyan")
        )

    def get_user_input(self) -> str:
        """Read one line of user input; show User panel only after they submit (with text inside)."""
        if not sys.stdin.isatty():
            return input().strip()

        self._console.print("[bold cyan]»[/] ", end="")
        text = input().strip()

        if text:
            sys.stdout.write(
                "\033[1A\033[K"
            )  # up one line, clear line (remove "» <input>" prompt)
            sys.stdout.flush()
            self._console.print(
                Panel(
                    f"[bold cyan]»[/] {text}",
                    title="[bold cyan]User[/]",
                    title_align="center",
                    border_style="cyan",
                    padding=(0, 1),
                )
            )
        else:
            sys.stdout.write(
                "\033[1A\033[K"
            )  # up one line, clear line (remove "» " prompt)
            sys.stdout.flush()
        return text
