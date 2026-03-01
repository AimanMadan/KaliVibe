import json
import os
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.config.settings import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

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

async def run_cli_agent():
    """Connects to the MCP server and runs the interactive CLI chat loop."""
    
    server_params = StdioServerParameters(
        command="uv", 
        args=["run", "python", "-m", "src.mcp_server.server"],
        env=dict(os.environ)
    )

    print("Booting KaliVibe MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            mcp_tools = await session.list_tools()
            
            openai_tools = []
            for tool in mcp_tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print(f"\n[System]: Agent online using {config.LLM_MODEL}. Type 'exit' to quit.")

            while True:
                # --- NEW EXCEPTION HANDLING FOR CLEAN EXITS ---
                try:
                    user_input = input("\nUser> ")
                except (KeyboardInterrupt, EOFError):
                    print("\n[System]: Shutting down KaliVibe...")
                    break
                # ----------------------------------------------

                if user_input.lower() in ['exit', 'quit']:
                    break

                messages.append({"role": "user", "content": user_input})

                while True:
                    response = await client.chat.completions.create(
                        model=config.LLM_MODEL,
                        messages=messages,
                        tools=openai_tools
                    )

                    message = response.choices[0].message
                    messages.append(message)

                    if message.content:
                        print(f"\n[KaliVibe]: {message.content}")

                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            print(f"\n⚙️  [Executing]: {tool_name}({tool_args})")
                            
                            result = await session.call_tool(tool_name, tool_args)
                            text_result = "\n".join([content.text for content in result.content if content.type == "text"])
                            
                            print(f"📄 [Result]:\n{text_result}")
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": text_result
                            })
                    else:
                        break