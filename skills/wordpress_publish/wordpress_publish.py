"""
WordPress Publish Skill — communicates with WordPress via the MCP Adapter.

Requires on the WordPress site:
  - MCP Adapter plugin: https://github.com/WordPress/mcp-adapter
  - WordPress abilities registered for post/category/tag management

Transport:  MCP Streamable HTTP (POST-only; does NOT use GET/SSE)
            GET is optional in the spec; WordPress MCP Adapter returns 405
            for it, so we speak raw JSON-RPC 2.0 over httpx POST directly.
Endpoint:   {wp_url}/wp-json/mcp/mcp-adapter-default-server
Auth:       WordPress Application Password via HTTP Basic Auth header

Expected MCP tool names (checked in priority order; first match wins):
  Post creation:    create-post | wp/create-post | wordpress/create-post
  Category list:    list-categories | get-categories | wp/get-categories
  Category create:  create-category | wp/create-category
  Tag list:         list-tags | get-tags | wp/get-tags
  Tag create:       create-tag | wp/create-tag
  Site info:        get-site-info | site-info | wordpress/site-info

Pass a tool_names override dict to the constructor for non-standard installs:
  skill = WordPressPublishSkill(
      wp_url="https://example.com",
      username="admin",
      app_password="xxxx xxxx xxxx xxxx",
      tool_names={"create_post": "my-plugin/publish-article"},
  )
"""

import base64
import json
import logging
import re
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default tool-name candidates (first match on the live server wins)
# ---------------------------------------------------------------------------

_DEFAULT_TOOL_CANDIDATES: Dict[str, List[str]] = {
    "create_post":      ["create-post", "wp/create-post", "wordpress/create-post", "posts/create"],
    "list_categories":  ["list-categories", "get-categories", "wp/get-categories", "wordpress/list-categories"],
    "create_category":  ["create-category", "wp/create-category", "wordpress/create-category"],
    "list_tags":        ["list-tags", "get-tags", "wp/get-tags", "wordpress/list-tags"],
    "create_tag":       ["create-tag", "wp/create-tag", "wordpress/create-tag"],
    "site_info":        ["get-site-info", "site-info", "wordpress/site-info"],
}

# MCP protocol version we advertise
_MCP_VERSION = "2025-06-18"


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class WordPressPublishResult:
    success: bool
    post_id: Optional[int] = None
    post_url: Optional[str] = None
    edit_url: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


@dataclass
class WordPressConnectionInfo:
    connected: bool
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    available_tools: List[str] = field(default_factory=list)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Lightweight MCP JSON-RPC client (POST-only, no SSE)
# ---------------------------------------------------------------------------

class _MCPSession:
    """
    Minimal MCP client using Streamable HTTP POST-only mode.

    The MCP spec makes the GET SSE stream optional (for server-initiated
    messages). WordPress MCP Adapter returns 405 for GET, so we skip it
    entirely and send every request as a POST with a JSON-RPC body.

    Usage:
        async with _MCPSession(url, auth_headers, timeout) as session:
            tools = await session.list_tools()
            result = await session.call_tool("create-post", {...})
    """

    def __init__(self, url: str, headers: Dict[str, str], timeout: int) -> None:
        self._url = url
        self._base_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **headers,
        }
        self._timeout = timeout
        self._session_id: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._req_id = 0

    async def __aenter__(self) -> "_MCPSession":
        self._client = httpx.AsyncClient(timeout=self._timeout)
        await self._initialize()
        return self

    async def __aexit__(self, *_) -> None:
        # Tear down the MCP session politely
        if self._session_id and self._client:
            try:
                await self._client.delete(self._url, headers=self._request_headers())
            except Exception:
                pass
        if self._client:
            await self._client.aclose()

    def _request_headers(self) -> Dict[str, str]:
        h = dict(self._base_headers)
        if self._session_id:
            h["Mcp-Session-Id"] = self._session_id
        return h

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _post(self, body: dict) -> dict:
        assert self._client is not None
        resp = await self._client.post(
            self._url,
            headers=self._request_headers(),
            json=body,
        )
        resp.raise_for_status()

        # Capture session ID on first response
        if sid := resp.headers.get("Mcp-Session-Id"):
            self._session_id = sid

        # Server may reply with direct JSON or SSE; handle both
        ct = resp.headers.get("content-type", "")
        if "text/event-stream" in ct:
            return _parse_sse(resp.text)
        return resp.json()

    async def _initialize(self) -> None:
        body = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": _MCP_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "content-creation-engine", "version": "1.0"},
            },
        }
        await self._post(body)

        # Notify the server we're ready (fire-and-forget)
        assert self._client is not None
        try:
            await self._client.post(
                self._url,
                headers=self._request_headers(),
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            )
        except Exception:
            pass

    async def list_tools(self) -> List[Dict[str, Any]]:
        resp = await self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
        })
        if "error" in resp:
            raise RuntimeError(f"tools/list error: {resp['error']}")
        return resp.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        resp = await self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        if "error" in resp:
            raise RuntimeError(f"MCP tool '{name}' error: {resp['error']}")
        return resp.get("result", {})


def _parse_sse(text: str) -> dict:
    """Extract the first JSON-RPC message from an SSE response body."""
    for line in text.splitlines():
        if line.startswith("data: "):
            try:
                return json.loads(line[6:])
            except json.JSONDecodeError:
                pass
    raise ValueError(f"No parseable data in SSE response: {text[:300]}")


def _parse_tool_content(result: dict) -> Any:
    """
    Extract a Python object from an MCP tools/call result.

    MCP returns: {"content": [{"type": "text", "text": "...json..."}], "isError": false}
    """
    for block in result.get("content", []):
        if block.get("type") == "text":
            text = block.get("text", "")
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text
    return result


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

class WordPressPublishSkill:
    """
    Publishes content to WordPress via the MCP Adapter plugin.

    Each public method opens exactly one MCP session so the connection
    overhead is paid once per logical operation.
    """

    def __init__(
        self,
        wp_url: str,
        username: str,
        app_password: str,
        timeout: int = 30,
        tool_names: Optional[Dict[str, str]] = None,
    ) -> None:
        self.wp_url = wp_url.rstrip("/")
        self.username = username
        self.app_password = app_password.replace(" ", "")
        self.timeout = timeout

        self._mcp_url = f"{self.wp_url}/wp-json/mcp/mcp-adapter-default-server"

        creds = base64.b64encode(
            f"{self.username}:{self.app_password}".encode()
        ).decode()
        self._auth_headers = {"Authorization": f"Basic {creds}"}

        # Merge caller-supplied name overrides into the candidates lists
        self._candidates: Dict[str, List[str]] = {
            k: list(v) for k, v in _DEFAULT_TOOL_CANDIDATES.items()
        }
        if tool_names:
            for op, name in tool_names.items():
                self._candidates.setdefault(op, []).insert(0, name)

        self._tool_cache: Optional[List[str]] = None

    # ------------------------------------------------------------------
    # Session context manager
    # ------------------------------------------------------------------

    @asynccontextmanager
    async def _session(self):
        async with _MCPSession(self._mcp_url, self._auth_headers, self.timeout) as session:
            yield session

    # ------------------------------------------------------------------
    # Tool discovery helpers
    # ------------------------------------------------------------------

    async def _get_tool_names(self, session: _MCPSession) -> List[str]:
        if self._tool_cache is None:
            tools = await session.list_tools()
            self._tool_cache = [t["name"] for t in tools]
            logger.debug(f"WordPress MCP tools: {self._tool_cache}")
        return self._tool_cache

    async def _find_tool(self, session: _MCPSession, operation: str) -> Optional[str]:
        available = await self._get_tool_names(session)
        for candidate in self._candidates.get(operation, []):
            if candidate in available:
                return candidate
        return None

    async def _require_tool(self, session: _MCPSession, operation: str) -> str:
        tool = await self._find_tool(session, operation)
        if tool:
            return tool
        available = await self._get_tool_names(session)
        candidates = self._candidates.get(operation, [])
        raise ValueError(
            f"No MCP tool found for '{operation}'. "
            f"Looked for: {candidates}. "
            f"Available on {self._mcp_url}: {available}. "
            "Register a matching WordPress ability or pass a tool_names override."
        )

    # ------------------------------------------------------------------
    # Core publish
    # ------------------------------------------------------------------

    async def publish(
        self,
        title: str,
        content: str,
        status: str = "draft",
        excerpt: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        slug: Optional[str] = None,
        featured_media: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> WordPressPublishResult:
        try:
            async with self._session() as session:
                tool = await self._require_tool(session, "create_post")

                args: Dict[str, Any] = {"title": title, "content": content, "status": status}
                if excerpt:
                    args["excerpt"] = excerpt
                if category_ids:
                    args["categories"] = category_ids
                if tag_ids:
                    args["tags"] = tag_ids
                if slug:
                    args["slug"] = slug
                if featured_media:
                    args["featured_media"] = featured_media
                if meta:
                    args["meta"] = meta

                raw = await session.call_tool(tool, args)
                data = _parse_tool_content(raw)

                if isinstance(data, dict):
                    post_id = data.get("id") or data.get("post_id")
                    if post_id:
                        return WordPressPublishResult(
                            success=True,
                            post_id=int(post_id),
                            post_url=data.get("link") or data.get("post_url", ""),
                            edit_url=f"{self.wp_url}/wp-admin/post.php?post={post_id}&action=edit",
                            status=data.get("status", status),
                        )

                return WordPressPublishResult(
                    success=False,
                    error=f"Unexpected response from '{tool}': {data}",
                )

        except ValueError as exc:
            return WordPressPublishResult(success=False, error=str(exc))
        except Exception as exc:
            logger.error(f"WordPress MCP publish failed: {exc}")
            return WordPressPublishResult(success=False, error=str(exc))

    # ------------------------------------------------------------------
    # Connection verification
    # ------------------------------------------------------------------

    async def verify_connection(self) -> WordPressConnectionInfo:
        try:
            async with self._session() as session:
                tools = await self._get_tool_names(session)

                site_name = None
                site_tool = await self._find_tool(session, "site_info")
                if site_tool:
                    try:
                        raw = await session.call_tool(site_tool, {})
                        data = _parse_tool_content(raw)
                        if isinstance(data, dict):
                            site_name = data.get("name") or data.get("site_name")
                    except Exception:
                        pass

                return WordPressConnectionInfo(
                    connected=True,
                    site_url=self.wp_url,
                    site_name=site_name,
                    available_tools=tools,
                )
        except Exception as exc:
            return WordPressConnectionInfo(connected=False, error=str(exc))

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    async def get_categories(self) -> List[Dict[str, Any]]:
        try:
            async with self._session() as session:
                return await self._get_categories(session)
        except Exception as exc:
            logger.error(f"get_categories failed: {exc}")
            return []

    async def _get_categories(self, session: _MCPSession) -> List[Dict[str, Any]]:
        tool = await self._find_tool(session, "list_categories")
        if not tool:
            logger.warning("No list-categories MCP tool found")
            return []
        raw = await session.call_tool(tool, {})
        data = _parse_tool_content(raw)
        return data if isinstance(data, list) else []

    async def resolve_category_names(self, names: List[str]) -> List[int]:
        if not names:
            return []
        try:
            async with self._session() as session:
                return await self._resolve_terms(session, names, "category")
        except Exception as exc:
            logger.error(f"resolve_category_names failed: {exc}")
            return []

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    async def get_tags(self) -> List[Dict[str, Any]]:
        try:
            async with self._session() as session:
                return await self._get_tags(session)
        except Exception as exc:
            logger.error(f"get_tags failed: {exc}")
            return []

    async def _get_tags(self, session: _MCPSession) -> List[Dict[str, Any]]:
        tool = await self._find_tool(session, "list_tags")
        if not tool:
            logger.warning("No list-tags MCP tool found")
            return []
        raw = await session.call_tool(tool, {})
        data = _parse_tool_content(raw)
        return data if isinstance(data, list) else []

    async def resolve_tag_names(self, names: List[str]) -> List[int]:
        if not names:
            return []
        try:
            async with self._session() as session:
                return await self._resolve_terms(session, names, "tag")
        except Exception as exc:
            logger.error(f"resolve_tag_names failed: {exc}")
            return []

    # ------------------------------------------------------------------
    # Shared term resolution (single session, fetch + create)
    # ------------------------------------------------------------------

    async def _resolve_terms(
        self, session: _MCPSession, names: List[str], term_type: str
    ) -> List[int]:
        fetch_op = "list_categories" if term_type == "category" else "list_tags"
        create_op = "create_category" if term_type == "category" else "create_tag"

        fetch_tool = await self._find_tool(session, fetch_op)
        existing: Dict[str, int] = {}
        if fetch_tool:
            raw = await session.call_tool(fetch_tool, {})
            terms = _parse_tool_content(raw)
            if isinstance(terms, list):
                existing = {
                    t["name"].lower(): t["id"]
                    for t in terms
                    if "name" in t and "id" in t
                }

        create_tool = await self._find_tool(session, create_op)
        ids: List[int] = []

        for name in names:
            key = name.lower()
            if key in existing:
                ids.append(existing[key])
            elif create_tool:
                try:
                    raw = await session.call_tool(create_tool, {"name": name})
                    data = _parse_tool_content(raw)
                    if isinstance(data, dict) and "id" in data:
                        ids.append(int(data["id"]))
                        existing[key] = int(data["id"])
                except Exception as exc:
                    logger.warning(f"Could not create {term_type} '{name}': {exc}")
            else:
                logger.warning(f"No create-{term_type} tool; '{name}' skipped")

        return ids

    # ------------------------------------------------------------------
    # Gutenberg block conversion (WordPress 5.0+ / 6.x block editor)
    # ------------------------------------------------------------------

    @staticmethod
    def markdown_to_blocks(content: str) -> str:
        """
        Convert Markdown to WordPress Gutenberg block markup (WP 5.0+).

        Each structural element is wrapped in block comment delimiters so
        the block editor recognises them natively, avoiding the Classic block.
        """
        lines = content.split("\n")
        blocks: List[str] = []
        i = 0
        _BLOCK_START = re.compile(
            r"^(#{1,6}\s|[-*+]\s|\d+\.\s|```|>|[-*_]{3,}\s*$)"
        )

        while i < len(lines):
            line = lines[i]

            m = re.match(r"^(#{1,6})\s+(.+)", line)
            if m:
                level = len(m.group(1))
                text = _inline_md(m.group(2))
                level_attr = "" if level == 2 else f' {{"level":{level}}}'
                blocks.append(
                    f'<!-- wp:heading{level_attr} -->\n'
                    f'<h{level} class="wp-block-heading">{text}</h{level}>\n'
                    f'<!-- /wp:heading -->'
                )
                i += 1
                continue

            if re.match(r"^[-*_]{3,}\s*$", line):
                blocks.append(
                    '<!-- wp:separator -->\n'
                    '<hr class="wp-block-separator has-alpha-channel-opacity"/>\n'
                    '<!-- /wp:separator -->'
                )
                i += 1
                continue

            if line.startswith("```"):
                lang = line[3:].strip()
                code_lines: List[str] = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                code = _escape_html("\n".join(code_lines))
                lang_attr = f' {{"language":"{lang}"}}' if lang else ""
                blocks.append(
                    f'<!-- wp:code{lang_attr} -->\n'
                    f'<pre class="wp-block-code"><code>{code}</code></pre>\n'
                    f'<!-- /wp:code -->'
                )
                i += 1
                continue

            if line.startswith("> "):
                quote_lines: List[str] = []
                while i < len(lines) and lines[i].startswith("> "):
                    quote_lines.append(_inline_md(lines[i][2:]))
                    i += 1
                blocks.append(
                    '<!-- wp:quote -->\n'
                    f'<blockquote class="wp-block-quote"><p>{" ".join(quote_lines)}</p></blockquote>\n'
                    '<!-- /wp:quote -->'
                )
                continue

            if re.match(r"^[-*+]\s+", line):
                items: List[str] = []
                while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                    text = _inline_md(re.sub(r"^[-*+]\s+", "", lines[i]))
                    items.append(
                        f'<!-- wp:list-item -->\n<li>{text}</li>\n<!-- /wp:list-item -->'
                    )
                    i += 1
                blocks.append(
                    '<!-- wp:list -->\n'
                    '<ul class="wp-block-list">\n' + "\n".join(items) + '\n</ul>\n'
                    '<!-- /wp:list -->'
                )
                continue

            if re.match(r"^\d+\.\s+", line):
                items = []
                while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                    text = _inline_md(re.sub(r"^\d+\.\s+", "", lines[i]))
                    items.append(
                        f'<!-- wp:list-item -->\n<li>{text}</li>\n<!-- /wp:list-item -->'
                    )
                    i += 1
                blocks.append(
                    '<!-- wp:list {"ordered":true} -->\n'
                    '<ol>\n' + "\n".join(items) + '\n</ol>\n'
                    '<!-- /wp:list -->'
                )
                continue

            if not line.strip():
                i += 1
                continue

            para_lines: List[str] = []
            while i < len(lines) and lines[i].strip() and not _BLOCK_START.match(lines[i]):
                para_lines.append(lines[i])
                i += 1
            if para_lines:
                text = _inline_md(" ".join(para_lines))
                blocks.append(
                    '<!-- wp:paragraph -->\n'
                    f'<p>{text}</p>\n'
                    '<!-- /wp:paragraph -->'
                )

        return "\n\n".join(blocks)

    @staticmethod
    def markdown_to_html(content: str) -> str:
        """Convert Markdown to plain HTML (legacy; prefer markdown_to_blocks for WP 6+)."""
        try:
            import markdown as md_lib
            return md_lib.markdown(content, extensions=["extra", "toc"])
        except ImportError:
            pass
        html = content
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)
        paragraphs = html.split("\n\n")
        wrapped = []
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if re.match(r"^<(h[1-6]|ul|ol|li|blockquote|pre)", p):
                wrapped.append(p)
            else:
                wrapped.append(f"<p>{p}</p>")
        return "\n\n".join(wrapped)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _inline_md(text: str) -> str:
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
