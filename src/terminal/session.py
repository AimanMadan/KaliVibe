import pexpect
import os


class BashSession:
    def __init__(self):
        """Initializes a persistent, stateful bash pseudo-terminal."""
        # A unique, complex marker that standard commands won't accidentally output
        self.prompt_marker = "KaliVibe>"
        
        # Dynamically get the current user's home directory
        home_dir = os.path.expanduser("~")
        
        # Spawn a bash shell
        self.child = pexpect.spawn(
            '/bin/bash', 
            ['--norc', '--noprofile'], # --norc and --noprofile ensure a clean environment without custom aliases
            encoding='utf-8', 
            echo=False,
            dimensions=(24, 120),
            cwd=home_dir
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
                # Strip trailing whitespace and carriage returns
                return output.strip()
            
            return ""
            
        except pexpect.TIMEOUT:
            # If the command hangs (e.g., 'nc -lvnp 4444' or 'ping'), interrupt it
            self.child.sendintr()  # Sends a Ctrl+C signal
            
            # Wait for the prompt to return after the interrupt
            self.child.expect(self.prompt_marker)
            return f"Error: Command timed out after {timeout} seconds and was interrupted!"
            
        except pexpect.EOF:
            return "Error: The terminal session closed unexpectedly."

    def close(self):
        """Gracefully terminate the shell session."""
        if self.child.isalive():
            self.child.sendline("exit")
            self.child.close()

# uncomment to test out running commands in the terminal.
'''         
if __name__ == "__main__":
    print("Starting standalone terminal session test...")
    print("Type 'exit' or 'quit' to stop.")
    
    # Initialize the session
    session = BashSession()
    
    try:
        while True:
            # Get a command directly from your keyboard
            cmd = input("input: ")
            
            if cmd.strip().lower() in ['exit', 'quit']:
                break
            
            # Execute it through our pexpect wrapper
            # (Try running something like 'ping -c 4 8.8.8.8' or a command that hangs to test the timeout!)
            output = session.execute(cmd)
            
            # Print the captured output
            print(output)
            
    except KeyboardInterrupt:
        print("\nCaught KeyboardInterrupt. Exiting...")
    finally:
        # Ensure we clean up the pseudo-terminal process
        session.close()
        print("Session closed.")       
'''        