import pexpect
import os
import re

# This regex matches standard ANSI escape codes (colors, cursor moves, bracketed paste)
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


class BashSession:
    def __init__(self):
        """Initializes a persistent, stateful bash pseudo-terminal."""
        # A unique, complex marker that standard commands won't accidentally output
        self.prompt_marker = "KaliVibe>"

        # Dynamically get the current user's home directory
        home_dir = os.path.expanduser("~")

        # Spawn a bash shell
        self.child = pexpect.spawn(
            "/bin/bash",
            [
                "--norc",
                "--noprofile",
            ],  # --norc and --noprofile ensure a clean environment without custom aliases
            encoding="utf-8",
            echo=False,
            dimensions=(24, 120),
            cwd=home_dir,
        )

        # Override the default terminal prompt (PS1) with our unique marker.
        # This is how pexpect knows exactly when a command has finished executing.
        self.child.sendline(f"export PS1='{self.prompt_marker}'")

        # Wait for the initial setup to complete
        self.child.expect(self.prompt_marker)

    def execute(self, command: str, timeout: int = 30) -> str:
        """
        Executes a command in the bash session and returns the standard output.
        Includes a timeout to prevent the LLM from hanging the agent on infinite loops.
        """
        # Send the command to the shell
        self.child.sendline(command)

        try:
            # Wait for our unique prompt marker to reappear
            self.child.expect(self.prompt_marker, timeout=timeout)

            # Extract everything printed before the prompt marker
            output = self.child.before

            if output:
                # pexpect sometimes captures the echoed command itself; remove it if present
                output = output.replace(command + "\r\n", "", 1)
                # Strip all ANSI escape sequences (colors, bracketed paste, etc.)
                output = ANSI_ESCAPE.sub("", output)
                # Strip trailing whitespace and carriage returns
                return output.strip()

            return ""

        except pexpect.TIMEOUT:
            # If the command hangs (e.g., 'nc -lvnp 4444' or 'ping'), interrupt it
            self.child.sendintr()  # Sends a Ctrl+C signal

            # Wait for the prompt to return after the interrupt
            self.child.expect(self.prompt_marker)
            return (
                f"Error: Command timed out after {timeout} seconds and was interrupted!"
            )

        except pexpect.EOF:
            return "Error: The terminal session closed unexpectedly."

    def close(self):
        """Gracefully terminate the shell session."""
        if self.child.isalive():
            self.child.sendline("exit")
            self.child.close()
