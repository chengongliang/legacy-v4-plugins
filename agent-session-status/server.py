#!/usr/bin/env python3
import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


VALID_STATUSES = {"running", "completed", "blocked"}
PROTOCOL_VERSION = "2025-06-18"


class ValidationError(Exception):
    pass


class SessionStore:
    def __init__(self):
        self._sessions = {}

    def upsert(self, agent, payload):
        agent = str(agent or "").strip()
        if not agent:
            raise ValidationError("X-Agent header is required")

        session_id = str(payload.get("id", "")).strip()
        if not session_id:
            raise ValidationError("session id is required")

        status = str(payload.get("status", "")).strip()
        if status not in VALID_STATUSES:
            raise ValidationError("status must be running, completed, or blocked")

        title = str(payload.get("title", "")).strip() or session_id
        now = int(time.time())
        key = (agent, session_id)
        created_at = self._sessions.get(key, {}).get("createdAt", now)
        entry = {
            "id": session_id,
            "agent": agent,
            "title": title,
            "status": status,
            "createdAt": created_at,
            "updatedAt": now,
        }
        self._sessions[key] = entry
        return dict(entry)

    def snapshot(self):
        grouped = {}
        running_count = 0

        for entry in self._sessions.values():
            if entry["status"] == "running":
                running_count += 1
            grouped.setdefault(entry["agent"], []).append(dict(entry))

        agents = []
        for agent in sorted(grouped.keys(), key=str.lower):
            sessions = sorted(grouped[agent], key=lambda item: item["updatedAt"], reverse=True)
            agents.append({
                "agent": agent,
                "runningCount": sum(1 for item in sessions if item["status"] == "running"),
                "sessions": sessions,
            })

        return {
            "runningCount": running_count,
            "agents": agents,
            "updatedAt": int(time.time()),
        }


def _json_response(status, body):
    return status, {"Content-Type": "application/json"}, body


def _authorized(headers, token):
    if not token:
        return False
    return headers.get("Authorization", "") == "Bearer " + token


def _rpc_result(request_id, result):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _rpc_error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _text_tool_result(payload):
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, separators=(",", ":")),
            }
        ],
        "isError": False,
    }


def _session_tools():
    return [
        {
            "name": "report_session",
            "title": "Report agent session status",
            "description": "Create or update an in-memory session for the calling agent. Requires X-Agent and bearer token headers.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Stable session id for this agent.",
                    },
                    "title": {
                        "type": "string",
                        "description": "Human-readable session title.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["running", "completed", "blocked"],
                    },
                },
                "required": ["id", "title", "status"],
                "additionalProperties": False,
            },
        },
        {
            "name": "list_sessions",
            "title": "List reported agent sessions",
            "description": "Return the current in-memory session snapshot grouped by agent.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    ]


def _handle_mcp(store, token, headers, raw_body):
    try:
        request = json.loads(raw_body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _rpc_error(None, -32700, "Parse error")

    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        return _rpc_error(request.get("id") if isinstance(request, dict) else None, -32600, "Invalid Request")

    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if method == "notifications/initialized":
        return None

    if method == "initialize":
        return _rpc_result(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "agent-session-status",
                "version": "1.0.0",
            },
        })

    if method == "tools/list":
        return _rpc_result(request_id, {"tools": _session_tools()})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == "list_sessions":
            return _rpc_result(request_id, _text_tool_result(store.snapshot()))

        if name == "report_session":
            if not _authorized(headers, token):
                return _rpc_error(request_id, -32001, "Unauthorized")

            agent = headers.get("X-Agent", "").strip()
            if not agent:
                return _rpc_error(request_id, -32602, "X-Agent header is required")

            try:
                session = store.upsert(agent, arguments)
            except ValidationError as error:
                return _rpc_error(request_id, -32602, str(error))

            return _rpc_result(request_id, _text_tool_result({
                "session": session,
                "snapshot": store.snapshot(),
            }))

        return _rpc_error(request_id, -32602, "Unknown tool: " + str(name))

    return _rpc_error(request_id, -32601, "Method not found")


def handle_request(store, token, method, path, headers=None, raw_body=b""):
    headers = headers or {}
    parsed_path = urlparse(path).path

    if method == "GET" and parsed_path == "/health":
        return _json_response(200, {"ok": True})

    if method == "GET" and parsed_path == "/sessions":
        return _json_response(200, store.snapshot())

    if method == "GET" and parsed_path == "/mcp":
        return _json_response(405, {"error": "SSE streaming is not supported"})

    if method == "POST" and parsed_path == "/mcp":
        response = _handle_mcp(store, token, headers, raw_body)
        if response is None:
            return 202, {"Content-Type": "application/json"}, {}
        return _json_response(200, response)

    return _json_response(404, {"error": "not found"})


class SessionRequestHandler(BaseHTTPRequestHandler):
    server_version = "AgentSessionStatus/1.0"

    def _dispatch(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(length) if length > 0 else b""
        status, headers, body = handle_request(
            self.server.store,
            self.server.auth_token,
            self.command,
            self.path,
            self.headers,
            raw_body,
        )
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self._dispatch()

    def do_POST(self):
        self._dispatch()

    def log_message(self, fmt, *args):
        sys.stderr.write("agent-session-status: " + fmt % args + "\n")


class SessionServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, handler_class, auth_token):
        super().__init__(server_address, handler_class)
        self.store = SessionStore()
        self.auth_token = auth_token


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=55854)
    parser.add_argument("--token", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    httpd = SessionServer((args.host, args.port), SessionRequestHandler, args.token)
    print("agent-session-status listening on %s:%d" % (args.host, args.port), flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
