# KaliVibe 🎧💻

**KaliVibe** is an autonomous security agent designed to run natively on **Kali Linux**. It leverages the **Model Context Protocol (MCP)** to bridge the gap between Large Language Models and a persistent, stateful bash terminal.

## 🚀 Getting Started

### Prerequisites

* **Python 3.13+**
* **uv** (Python package manager)
* **OpenAI API Key**
* **Node.js/npm** (for MCP Inspector debugging)

### Installation

1. Clone the repository to `~/dev/KaliVibe`.
2. Create and configure your secrets:
```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and LLM_MODEL
```


3. Install dependencies:
```bash
uv sync
```



### Running the Agent

Start the orchestrator from the project root:

```bash
uv run python -m src.main
```

---

## 🏗 Project Architecture

* **`src/terminal/`**: Handles the persistent `pexpect` bash session and output sanitization.
* **`src/mcp_server/`**: The FastMCP server exposing terminal tools (execute, read, write) to the LLM.
* **`src/agent/`**: The OpenAI/Pydantic AI "brain" that manages the reasoning loop.
* **`src/config/`**: Centralized settings and secret management using `python-dotenv`.

---

## 🛠 Features

* **Persistent Shell:** Unlike standard LLM tools, KaliVibe maintains state across commands (e.g., `cd` persists).
* **Safe File I/O:** Dedicated tools for reading and writing files to avoid bash escaping issues.
* **Sanitized Output:** Automatically strips ANSI escape codes and bracketed paste markers for clean LLM context.
