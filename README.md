# apihop-mcp-server

Zero-dependency Model Context Protocol (MCP) server for **[API Hop](https://apihop.ai/en)** — connect Claude Code, Cursor, Windsurf, or any MCP host to leading LLMs and **32+ real-time Data APIs** (Google Search, Twitter/X, Similarweb, Airbnb, Amazon, YouTube, LinkedIn, Google Maps, and more) with a single API key.

## Key Resources

- **Get Your API Key**: [API Hop Platform](https://apihop.ai/en)
- **32+ Real-Time Data APIs**: [Data APIs Directory](https://apihop.ai/en/data-apis)
- **Supported AI Models**: [Models Directory](https://apihop.ai/en/models) · [Pricing](https://apihop.ai/en/pricing)
- **API Installation Guide**: [Docs & Base URL Reference](https://apihop.ai/en/docs/api-reference/ai-installation-guide)
- **Machine-Readable Catalog (285+ endpoints)**: [public-api-catalog.json](https://apihop.ai/docs/public-api-catalog.json)

## Quick Setup (Claude Code / Cursor / Claude Desktop)

Requires Python 3.9+ (standard library only, no `pip install` needed).

```json
{
  "mcpServers": {
    "apihop": {
      "command": "python3",
      "args": ["/path/to/apihop-mcp-server/server.py"],
      "env": {
        "APIHOP_API_KEY": "your-apihop-api-key"
      }
    }
  }
}
```

## Available MCP Tools

| Tool | Description |
| :--- | :--- |
| `apihop_list_models` | List all callable models (`GET /v1/models`) |
| `apihop_chat_completion` | Call any LLM via `POST /v1/chat-completions` |
| `apihop_twitter_user` | Fetch Twitter/X user profile (`GET /v1/twitter/users`) |
| `apihop_call_endpoint` | Call any of the 285+ LLM or Data API endpoints in the catalog |

## License

MIT
