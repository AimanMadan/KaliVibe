import asyncio
import os
import signal
import sys

from src.agent.llm import run_cli_agent
from src.tui import RichUI


def _has_keyboard_interrupt(exc: BaseExceptionGroup) -> bool:
    """Return True if any sub-exception is KeyboardInterrupt."""
    for sub in exc.exceptions:
        if isinstance(sub, KeyboardInterrupt):
            return True
        if isinstance(sub, BaseExceptionGroup) and _has_keyboard_interrupt(sub):
            return True
    return False


def _print_exception_group(exc: BaseExceptionGroup) -> None:
    """Print each sub-exception in an ExceptionGroup so the real cause is visible."""
    print(f"\nCritical Error: {exc}", file=sys.stderr)
    for i, sub in enumerate(exc.exceptions, 1):
        print(f"\n--- sub-exception {i} ---", file=sys.stderr)
        if isinstance(sub, BaseExceptionGroup):
            _print_exception_group(sub)
        else:
            import traceback

            traceback.print_exception(
                type(sub), sub, sub.__traceback__, file=sys.stderr
            )


def main() -> None:
    """Main entry point for KaliVibe."""
    ui = RichUI()  # Rich TUI is now the default

    def _on_sigint(*_args: object) -> None:
        print("\nSession terminated by user.")
        os._exit(0)

    signal.signal(signal.SIGINT, _on_sigint)

    try:
        asyncio.run(run_cli_agent(ui=ui))
    except KeyboardInterrupt:
        print("\nSession terminated by user.")
        os._exit(0)
    except BaseExceptionGroup as e:
        if _has_keyboard_interrupt(e):
            print("\nSession terminated by user.")
            os._exit(0)
        _print_exception_group(e)
        sys.exit(1)
    except Exception as e:
        print(f"\nCritical Error: {str(e)}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
