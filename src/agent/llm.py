import asyncio
import json
import os
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.config.settings import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


class _DefaultCLI:
    """Default CLI UI: plain print() and input(). Used when no Rich TUI is passed."""

    @staticmethod
    def print_boot(msg: str) -> None:
        print(msg)

    @staticmethod
    def print_system(msg: str) -> None:
        print(msg)

    @staticmethod
    def print_agent(content: str) -> None:
        print(f"\n[KaliVibe]: {content}")

    @staticmethod
    def print_tool_call(name: str, args: dict) -> None:
        print(f"\n⚙️  [Executing]: {name}({args})")

    @staticmethod
    def print_tool_result(text: str) -> None:
        print(f"📄 [Result]:\n{text}")

    @staticmethod
    def get_user_input() -> str:
        return input("\nUser> ")

    @staticmethod
    def start_loading() -> None:
        print("\nThinking...", flush=True)

    @staticmethod
    def stop_loading() -> None:
        pass


SYSTEM_PROMPT = """
# ROLE AND IDENTITY
You are KaliVibe, an advanced, autonomous AI security assistant natively integrated into Kali Linux. You act as an expert AI pair-hacker and mentor—similar to an intelligent IDE, but built specifically for offensive security, penetration testing, and cybersecurity education. 

You have access to a persistent bash terminal via MCP tools. You are operating in a safe, authorized, and isolated environment. You have full permission to enumerate, configure, and manage this system.

# PRIMARY OBJECTIVES
1. Execute security workflows (reconnaissance, exploitation, post-exploitation, scripting) efficiently via your terminal tools.
2. Educate the user. Whether they are a seasoned professional or a beginner, explain your methodology, tool choices, and the output of your actions clearly and concisely.

# RULES OF ENGAGEMENT
1. ORIENTATION FIRST: Always maintain situational awareness. Verify your current directory (`pwd`, `ls`) and user privileges (`whoami`) before reading, writing, or executing files.
2. TERMINAL SAFETY: You are interacting with a non-interactive bash shell. 
   - NEVER run commands that require interactive user input (e.g., `nano`, `vim`, `top`, or `msfconsole` without the `-x` flag). 
   - If a command is expected to take a long time, use timeouts or run it in the background if appropriate.
3. RESILIENCE: If a command hangs, fails, or returns an error, do not panic. Analyze the `stderr` or output, briefly state why it failed, and immediately try an alternative approach. 
4. EDUCATIONAL TRANSPARENCY: Don't just run commands; explain the *why*. If you run an `nmap` scan, briefly mention why you chose specific flags (e.g., `-sV -sC`). If writing a Python exploit, add inline comments explaining the logic.
5. CONCISE EXECUTION: Avoid excessive verbosity. Structure your responses clearly:
   - **Thought:** A 1-2 sentence internal reasoning of what you need to do and why.
   - **Action:** The command or script you are executing.
   - **Result/Analysis:** A brief interpretation of the output and the immediate next step.

# TONE
Be direct, professional, highly technical, and encouraging. You are an elite hacker mentoring a peer. Do not use overly dramatic language; stick to the facts, the methodology, and the code.
"""

async def run_cli_agent(ui=None):
    """Connects to the MCP server and runs the interactive CLI chat loop.

    Args:
        ui: Optional UI object with print_boot, print_system, print_agent,
            print_tool_call, print_tool_result, and get_user_input. If None, uses
            plain print/input (_DefaultCLI).
    """
    if ui is None:
        ui = _DefaultCLI()

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "src.mcp_server.server"],
        env=dict(os.environ),
    )

    ui.print_boot("Booting KaliVibe")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()

            openai_tools = []
            for tool in mcp_tools.tools:
                openai_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                )

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            ui.print_system("Agent online. Type /exit, /quit, or /stop to quit.")

            while True:
                try:
                    user_input = await asyncio.to_thread(ui.get_user_input)
                except (KeyboardInterrupt, EOFError):
                    ui.print_system("Shutting down KaliVibe...")
                    break

                if user_input.strip().lower() in ("/exit", "/quit", "/stop"):
                    break

                messages.append({"role": "user", "content": user_input})

                while True:
                    ui.start_loading()
                    response = await client.chat.completions.create(
                        model=config.LLM_MODEL,
                        messages=messages,
                        tools=openai_tools,
                    )
                    ui.stop_loading()

                    message = response.choices[0].message
                    messages.append(message)

                    if message.content:
                        ui.print_agent(message.content)

                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)

                            ui.print_tool_call(tool_name, tool_args)

                            result = await session.call_tool(tool_name, tool_args)
                            text_result = "\n".join(
                                content.text
                                for content in result.content
                                if content.type == "text"
                            )

                            ui.print_tool_result(text_result)

                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_name,
                                    "content": text_result,
                                }
                            )
                    else:
                        break
