# KaliVibe Architecture

This document describes the internal architecture of KaliVibe.

---

## Overview

KaliVibe is built on four core components:

1. **Agent (LLM Brain)** - The reasoning engine powered by OpenAI
2. **MCP Server** - The tool interface using Model Context Protocol
3. **Terminal Session** - The persistent bash shell using pexpect
4. **TUI Layer** - Optional Rich-based terminal UI for enhanced output

---

## Component Details

### 1. Agent (`src/agent/llm.py`)

The agent is the brain of KaliVibe. It:

- Connects to OpenAI's API
- Maintains conversation history
- Receives tool definitions from the MCP server
- Executes tool calls and returns results
- Runs an interactive CLI loop with pluggable UI

#### UI Abstraction

The agent accepts an optional `ui` parameter implementing a simple interface:

```python
class UIProtocol:
    def print_boot(self, msg: str) -> None: ...
    def print_system(self, msg: str) -> None: ...
    def print_agent(self, content: str) -> None: ...
    def print_tool_call(self, name: str, args: dict) -> None: ...
    def print_tool_result(self, text: str) -> None: ...
    def get_user_input(self) -> str: ...
    def start_loading(self) -> None: ...
    def stop_loading(self) -> None: ...
```

If no UI is provided, a `_DefaultCLI` fallback uses plain `print()` and `input()`.

```
┌─────────────────────────────────────┐
│           Agent Loop                │
├─────────────────────────────────────┤
│                                     │
│  1. Get user input                  │
│  2. Send to LLM with context        │
│  3. Receive response                │
│  4. If tool_calls:                  │
│     - Execute via MCP               │
│     - Return result to LLM          │
│     - Go to step 3                  │
│  5. Display response to user        │
│  6. Go to step 1                    │
│                                     │
└─────────────────────────────────────┘
```

#### System Prompt

The agent uses a carefully crafted system prompt that:
- Identifies KaliVibe as a security agent
- Provides rules for safe operation
- Encourages concise, actionable responses

### 2. MCP Server (`src/mcp_server/server.py`)

The MCP server exposes tools to the LLM using the FastMCP framework.

#### Tools

| Tool | Purpose | Implementation |
|------|---------|----------------|
| `execute_command` | Run bash commands | Calls `BashSession.execute()` |
| `read_file` | Read file contents | Direct Python `open()` |
| `write_file` | Write file contents | Direct Python `open()` with `makedirs` |

#### Path Resolution

The `resolve_path()` helper ensures file operations respect the bash session's current directory:

```python
def resolve_path(filepath: str) -> str:
    filepath = os.path.expanduser(filepath)
    if not os.path.isabs(filepath):
        current_bash_dir = bash.execute("pwd").strip()
        filepath = os.path.join(current_bash_dir, filepath)
    return filepath
```

This allows the LLM to use relative paths like `script.sh` after `cd /tmp`.

### 3. Terminal Session (`src/terminal/session.py`)

The terminal session provides a persistent bash shell using `pexpect`.

#### Key Design Decisions

1. **Clean Shell Environment**
   ```python
   self.child = pexpect.spawn("/bin/bash", ["--norc", "--noprofile"], ...)
   ```
   This prevents user aliases/configs from interfering.

2. **Custom Prompt Marker**
   ```python
   self.prompt_marker = "KaliVibe>"
   self.child.sendline(f"export PS1='{self.prompt_marker}'")
   ```
   A unique marker ensures reliable command completion detection.

3. **ANSI Sanitization**
   ```python
   ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
   output = ANSI_ESCAPE.sub("", output)
   ```
   Removes color codes and control sequences for clean LLM input.

4. **Timeout Protection**
   ```python
   self.child.expect(self.prompt_marker, timeout=timeout)
   # On timeout:
   self.child.sendintr()  # Ctrl+C
   ```
   Prevents infinite loops from hanging the agent.

### 4. TUI Layer (`src/tui/`)

The TUI layer provides an optional Rich-based terminal interface.

#### Components

- **`console.py`** - `RichUI` class implementing the UI protocol with:
  - Panels for agent responses and system messages
  - Markdown rendering for agent output
  - Syntax-highlighted JSON for tool arguments
  - Animated loading spinner during LLM calls
  - Clean input prompt with visual feedback

#### Enabling the TUI

```bash
uv run python -m src.main --tui
```

Without `--tui`, the agent uses plain CLI output.

---

## Data Flow

```
User Input
    │
    ▼
┌───────────────┐
│  Agent Loop   │
│   (llm.py)    │
└───────┬───────┘
        │
        ▼
┌───────────────┐     MCP Protocol      ┌───────────────┐
│    OpenAI     │ ◄──────────────────►  │   MCP Server  │
│     API       │    Tool Definitions   │  (server.py)  │
└───────────────┘     & Tool Calls      └───────┬───────┘
                                              │
                          ┌───────────────────┼───────────────────┐
                          ▼                   ▼                   ▼
                   ┌────────────┐      ┌────────────┐      ┌────────────┐
                   │  execute   │      │   read     │      │   write    │
                   │  command   │      │   file     │      │   file     │
                   └─────┬──────┘      └────────────┘      └────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   pexpect   │
                  │ BashSession │
                  └─────┬───────┘
                        │
                        ▼
                  ┌─────────────┐
                  │   /bin/bash │
                  └─────────────┘
```

---

## Configuration

Settings are managed in `src/config/settings.py`:

```python
class Settings:
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    LLM_MODEL: str | None = os.getenv("LLM_MODEL")
```

The `.env` file is loaded at import time using `python-dotenv`.

---

## Security Considerations

1. **Full Shell Access** - The LLM has unrestricted bash access
2. **No Sandboxing** - Commands run as the current user
3. **API Key Exposure** - `.env` must be protected
4. **Command Injection** - All user input is passed to bash

### Recommendations

- Run in isolated environments (VMs, containers)
- Use restricted shells or allowlists for production
- Audit command logs
- Never expose the agent to untrusted networks

---

## Extending KaliVibe

### Adding New Tools

1. Define the tool in `src/mcp_server/server.py`:
   ```python
   @mcp.tool()
   def my_new_tool(arg: str) -> str:
       """Tool description for the LLM."""
       # Implementation
       return "result"
   ```

2. The tool is automatically exposed to the LLM via MCP.

### Supporting Other LLMs

The agent code is OpenAI-specific but can be adapted for:
- Anthropic Claude (via their Python SDK)
- Local models (via Ollama or LM Studio)
- Other providers (via LiteLLM)

---

## Future Architecture Plans

- **Multi-terminal support** - Multiple bash sessions
- **Web dashboard** - Real-time monitoring
- **Command allowlists** - Restricted mode
- **Session persistence** - Save/restore terminal state
- **Plugin system** - Extensible tools via Python packages
