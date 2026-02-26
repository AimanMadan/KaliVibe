import asyncio
from src.agent.llm import run_cli_agent

def main():
    """Main entry point for KaliVibe."""
    try:
        # Currently defaults to the CLI agent loop. 
        # Future TUI initialization will go here.
        asyncio.run(run_cli_agent())
    except KeyboardInterrupt:
        print("\nSession terminated by user.")
    except Exception as e:
        print(f"\nCritical Error: {str(e)}")

if __name__ == "__main__":
    main()