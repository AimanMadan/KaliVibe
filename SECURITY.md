# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in KaliVibe, please report it responsibly.

### How to Report

1. **Do NOT** open a public issue
2. Email security concerns to: [your-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Time

- Initial response: within 48 hours
- Vulnerability assessment: within 7 days
- Fix timeline: depends on severity

## Security Considerations

⚠️ **Important:** KaliVibe executes real commands on your system with full shell access.

### 🖥️ Virtual Machine Required (Strongly Recommended)

**Always run KaliVibe in a VM.** This is not optional for safe usage.

| Recommendation | Why |
|----------------|-----|
| Use VirtualBox, VMware, or Parallels | Isolate from your host |
| Take snapshots before running | Easy rollback if something goes wrong |
| Isolate VM network | Prevent accidental exposure |
| Don't run on your primary machine | Protect your real data |

### Risks

- The LLM has unrestricted access to your shell
- Commands run as your current user
- No sandboxing or command filtering by default

### Best Practices

1. **Run in a virtual machine** (required for safe usage)
2. **Review commands** before execution in sensitive environments
3. **Never expose** the agent to untrusted inputs
4. **Protect your `.env` file** - it contains your API key
5. **Audit logs** if using in production

### Secure Configuration

```env
# Use environment variables instead of .env in production
export OPENAI_API_KEY="your-key"
export LLM_MODEL="gpt-4o"
```

## Known Limitations

- No command allowlisting yet (planned)
- No session audit logging (planned)
- No authentication/authorization layer

---

Thank you for helping keep KaliVibe secure!
