# Claude Code Enhancements

This document describes the enhancements integrated into the Claude Code environment from various community repositories.

## 1. Hooks System

The `.claude/hooks/` directory contains Python scripts that intercept and enhance Claude Code's behavior at key lifecycle points:

### Available Hooks:
- **UserPromptSubmit**: Logs and validates user prompts before processing
- **PreToolUse**: Security filtering to block dangerous commands
- **PostToolUse**: Logs tool execution results
- **Notification**: Captures user interaction points
- **Stop**: Logs session completion
- **SubagentStop**: Tracks subagent completion
- **PreCompact**: Handles context compaction events
- **SessionStart**: Initializes new sessions

### Security Features:
- Blocks dangerous commands like `rm -rf`, `chmod 777`
- Prevents access to sensitive files (`.env`, `.ssh`, private keys)
- All events are logged to `/app/logs/hooks.jsonl`

## 2. MCP Servers

Two MCP (Model Context Protocol) servers are pre-configured:

### just-prompt
- **Purpose**: Multi-LLM provider interface (OpenAI, Anthropic, Gemini, Groq, DeepSeek, Ollama)
- **Location**: `/app/mcp-servers/just-prompt`
- **Features**:
  - Send prompts to multiple models in parallel
  - CEO and Board decision-making pattern
  - File-based prompt management
  - Model listing and provider management

### quick-data
- **Purpose**: Data analysis for JSON and CSV files
- **Location**: `/app/mcp-servers/quick-data-mcp`
- **Features**:
  - Arbitrary data analysis capabilities
  - File resource management
  - Reusable analysis workflows

## 3. Single-File Agents Examples

The `/app/examples/single-file-agents/` directory contains powerful single-file AI agents:

- **DuckDB Agents**: SQL query generation and execution
- **SQLite Agent**: Database operations
- **JQ Agent**: JSON processing with jq commands
- **Bash Editor Agent**: File and command execution
- **Polars CSV Agent**: Data transformation
- **Web Scraper Agent**: Web content extraction
- **Meta Prompt Generator**: Creates structured prompts

Each agent demonstrates:
- Self-contained dependencies using `uv`
- Precise prompt engineering
- Tool use patterns
- Error handling

## 4. Environment Setup

Required environment variables:
```bash
# AI Provider Keys
export ANTHROPIC_API_KEY='your-key'
export OPENAI_API_KEY='your-key'
export GEMINI_API_KEY='your-key'
export GROQ_API_KEY='your-key'
export DEEPSEEK_API_KEY='your-key'

# Optional Services
export ELEVEN_API_KEY='your-key'  # For TTS
export FIRECRAWL_API_KEY='your-key'  # For web scraping

# Local Services
export OLLAMA_HOST='http://localhost:11434'
```

## 5. Usage Examples

### Running Single-File Agents:
```bash
# DuckDB analysis
uv run /app/examples/single-file-agents/sfa_duckdb_openai_v2.py \
  -d ./data/analytics.db \
  -p "Show me all users with score above 80"

# Web scraping
uv run /app/examples/single-file-agents/sfa_scrapper_agent_openai_v2.py \
  -u "https://example.com" \
  -p "Extract all headings" \
  -o "headings.md"
```

### Using MCP Servers:
The MCP servers are automatically available in Claude Code through the `.claude/settings.json` configuration.

## 6. Best Practices

1. **Security**: Always review hook scripts before enabling them
2. **Logging**: Check `/app/logs/hooks.jsonl` for debugging
3. **API Keys**: Store sensitive keys in environment variables
4. **Testing**: Test agents with sample data before production use
5. **Customization**: Modify hooks and agents for your specific needs

## 7. Directory Structure

```
/app/
├── .claude/
│   ├── settings.json      # Hook and MCP configuration
│   └── hooks/            # Hook scripts
├── mcp-servers/          # MCP server implementations
│   ├── just-prompt/
│   └── quick-data-mcp/
├── examples/
│   └── single-file-agents/  # Example agent scripts
└── logs/                 # Hook event logs
```

## 8. Extending the System

To add new capabilities:
1. **New Hooks**: Add scripts to `.claude/hooks/` and update `settings.json`
2. **New MCP Servers**: Add to `mcp-servers/` and configure in `settings.json`
3. **New Agents**: Create single-file agents following the existing patterns

Remember: These enhancements are meant to augment Claude Code's capabilities while maintaining security and reliability.