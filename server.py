#!/usr/bin/env python3
"""
Lightweight, zero-dependency MCP (Model Context Protocol) stdio server for API Hop (https://apihop.ai).
Gives Claude Code, Cursor, Windsurf, and other MCP clients one-key access to:
- Leading LLMs (OpenAI, Anthropic, Gemini, DeepSeek, Kimi, MiniMax)
- 32+ Real-Time Data APIs (Google Search, Twitter/X, Similarweb, Airbnb, Amazon, YouTube, etc.)

Set APIHOP_API_KEY in your environment before running.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("APIHOP_BASE_URL", "https://api.apihop.ai").rstrip("/")
API_KEY = os.environ.get("APIHOP_API_KEY", "")

TOOLS = [
    {
        "name": "apihop_list_models",
        "description": "List callable AI models available on API Hop (GET /v1/models).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "apihop_chat_completion",
        "description": "Call an LLM via API Hop unified chat completions endpoint (POST /v1/chat-completions).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Model ID from apihop_list_models"},
                "prompt": {"type": "string", "description": "User prompt text"},
            },
            "required": ["model", "prompt"],
        },
    },
    {
        "name": "apihop_twitter_user",
        "description": "Look up a Twitter/X user profile by username via API Hop (GET /v1/twitter/users).",
        "inputSchema": {
            "type": "object",
            "properties": {"username": {"type": "string", "description": "Twitter/X handle without @"}},
            "required": ["username"],
        },
    },
    {
        "name": "apihop_call_endpoint",
        "description": "Call any API Hop LLM or Data API endpoint (Google Search, Airbnb, Amazon, Similarweb, etc.) documented at https://apihop.ai/docs/public-api-catalog.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST"]},
                "path": {"type": "string", "description": "Endpoint path starting with / (e.g. /v1/models)"},
                "query": {"type": "object", "description": "Optional URL query parameters"},
                "body": {"type": "object", "description": "Optional JSON request body for POST"},
            },
            "required": ["method", "path"],
        },
    },
]


def http_json(method, path, query=None, body=None):
    if not API_KEY:
        return {"error": "APIHOP_API_KEY environment variable is not set. Get a key at https://apihop.ai/en"}
    url = BASE_URL + (path if path.startswith("/") else "/" + path)
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "body": e.read().decode("utf-8", errors="ignore")}
    except Exception as e:
        return {"error": str(e)}


def handle_tool(name, args):
    if name == "apihop_list_models":
        return http_json("GET", "/v1/models")
    if name == "apihop_chat_completion":
        return http_json(
            "POST",
            "/v1/chat-completions",
            body={"model": args["model"], "messages": [{"role": "user", "content": args["prompt"]}]},
        )
    if name == "apihop_twitter_user":
        return http_json("GET", "/v1/twitter/users", query={"username": args["username"].lstrip("@")})
    if name == "apihop_call_endpoint":
        return http_json(args["method"], args["path"], query=args.get("query"), body=args.get("body"))
    return {"error": f"Unknown tool: {name}"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        mid = msg.get("id")
        method = msg.get("method")
        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "apihop-mcp-server", "version": "0.1.0"},
                },
            }
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = msg.get("params", {})
            out = handle_tool(params.get("name"), params.get("arguments", {}))
            resp = {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=2)}]},
            }
        elif mid is not None:
            resp = {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
        else:
            continue
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
