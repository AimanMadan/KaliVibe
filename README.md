# KaliVibe 🎧💻

**KaliVibe** is an autonomous security agent that runs natively on **Kali Linux**. It bridges Large Language Models with a persistent, stateful bash terminal using the **Model Context Protocol (MCP)**.

Think of it as an AI-powered sidekick for security professionals — one that remembers where it is, what it's done, and can execute real commands on your system.

> 🖥️ **Important:** Run KaliVibe in a **virtual machine**. The LLM has unrestricted shell access — protect your primary machine.

---

## ✨ Features

- **🔄 Persistent Shell** — Unlike standard LLM tools, KaliVibe maintains state across commands. `cd` into a directory? You stay there.
- **🛡️ Safe File I/O** — Dedicated tools for reading and writing files, avoiding bash escaping nightmares.
- **🧹 Sanitized Output** — Automatically strips ANSI escape codes and bracketed paste markers for clean LLM context.
- **⚡ Timeout Protection** — Commands that hang (like `nc -lvnp`) are auto-interrupted after 30 seconds.
- **🔌 MCP-Powered** — Uses the Model Context Protocol for standardized tool communication.

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Virtual Machine** | — | **Highly recommended** for safety |
| Python | 3.13+ | Required |
| uv | Latest | Python package manager |
| OpenAI API Key | — | For LLM access |
| Node.js/npm | 18+ | Optional, for MCP Inspector debugging |

> ⚠️ **Run in a VM!** KaliVibe gives the LLM full shell access. Always use a virtual machine with snapshots.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AimanMadan/KaliVibe.git
cd KaliVibe

# 2. Configure your secrets
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and preferred LLM_MODEL

# 3. Install dependencies
uv sync
```

### Running the Agent

```bash
uv run python -m src.main
```

You'll see:
```
Booting KaliVibe MCP Server...

[System]: Agent online using gpt-4o. Type 'exit' to quit.

User> _
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        KaliVibe                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    MCP Protocol    ┌──────────────────┐  │
│   │              │ ◄─────────────────► │                  │  │
│   │   OpenAI     │                     │   FastMCP        │  │
│   │   LLM Brain  │                     │   Server         │  │
│   │              │ ◄─────────────────► │                  │  │
│   └──────────────┘    Tool Calls       └────────┬─────────┘  │
│                                                  │            │
│                                  ┌───────────────┼───────┐    │
│                                  ▼               ▼       ▼    │
│                           ┌──────────┐  ┌──────────┐ ┌─────┐ │
│                           │ execute  │  │  read_   │ │write│ │
│                           │ command  │  │  file    │ │file │ │
│                           └────┬─────┘  └──────────┘ └─────┘ │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                      │
│                        │   pexpect    │                      │
│                        │   BashSession│                      │
│                        └──────┬───────┘                      │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                      │
│                        │  Kali Linux  │                      │
│                        │  Shell       │                      │
│                        └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
KaliVibe/
├── src/
│   ├── main.py              # Entry point
│   ├── config/
│   │   └── settings.py      # Centralized config & secrets
│   ├── agent/
│   │   └── llm.py           # OpenAI client + reasoning loop
│   ├── mcp_server/
│   │   └── server.py        # FastMCP tools (execute, read, write)
│   └── terminal/
│       └── session.py       # Persistent pexpect bash session
├── .env.example             # Environment template
├── pyproject.toml           # Project metadata & deps
└── README.md
```

---

## 🛠 Available Tools

KaliVibe exposes three MCP tools to the LLM:

| Tool | Description |
|------|-------------|
| `execute_command` | Run any bash command in a persistent terminal |
| `read_file` | Safely read file contents (avoids `cat` issues) |
| `write_file` | Write content to files (avoids escaping issues) |

---

## ⚙️ Configuration

Edit `.env` to customize behavior:

```env
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (defaults shown)
LLM_MODEL=gpt-4o
```

### Supported Models

Any OpenAI-compatible model:
- `gpt-4o` (recommended)
- `gpt-4o-mini`
- `gpt-4-turbo`
- `o1-preview` / `o1-mini`

---

## 📖 Usage Examples

### Basic Interaction

```
User> what's my current directory and what's here?

[KaliVibe]: Let me check that for you.
⚙️  [Executing]: execute_command({'command': 'pwd && ls -la'})
📄 [Result]:
/home/kali
total 32
drwxr-xr-x 4 kali kali 4096 Feb 26 10:00 .
drwxr-xr-x 3 root root 4096 Feb 25 09:00 ..
-rw-r--r-- 1 kali kali  220 Feb 25 09:00 .bash_logout
...

[KaliVibe]: You're in `/home/kali`. I can see the default home directory contents.
```

### Security Enumeration

```
User> check what ports are listening and what processes are running them

[KaliVibe]: I'll enumerate the listening ports and their associated processes.
⚙️  [Executing]: execute_command({'command': 'ss -tlnp'})
...
```

### File Operations

```
User> create a simple nmap scan script in /tmp/

[KaliVibe]: I'll create that for you.
⚙️  [Executing]: write_file({'filepath': '/tmp/scan.sh', 'content': '#!/bin/bash\n# Basic nmap scanner\ntarget=$1\nnmap -sV -sC $target\n'})
📄 [Result]: Successfully wrote 89 characters to '/tmp/scan.sh'.

[KaliVibe]: Done! Make it executable with `chmod +x /tmp/scan.sh`.
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync

# Run linting
uv run ruff check src/

# Format code
uv run ruff format src/
```

### Debugging with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run python -m src.mcp_server.server
```

---

## ⚠️ Security Considerations

**KaliVibe executes real commands on your system.** The LLM has full shell access.

### 🖥️ Run in a Virtual Machine (Highly Recommended)

KaliVibe gives an AI unrestricted shell access. For your safety:

- **ALWAYS run in a VM** (VirtualBox, VMware, Parallels, etc.)
- Use snapshots so you can revert if something goes wrong
- Isolate the VM from your host network if possible
- Never run on your primary/production machine

### Additional Precautions

- **Review commands** before letting the agent run unattended
- **Never expose** the agent to untrusted inputs or networks
- **Audit logs** regularly if using in production environments

---

## 🗺 Roadmap

- [ ] Web dashboard for session monitoring
- [ ] Multi-terminal support
- [ ] Command logging & replay
- [ ] Restricted mode with command allowlists
- [ ] Integration with other LLM providers (Anthropic, local models)

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - For the excellent tooling standard
- [OpenAI](https://openai.com/) - For the powerful LLM API
- [pexpect](https://pexpect.readthedocs.io/) - For robust terminal handling

---

<p align="center">
  <strong>Built with 💜 for the security community</strong>
</p>
