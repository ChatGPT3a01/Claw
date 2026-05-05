"""WebFetch tool — fetch and extract web page content."""
from __future__ import annotations

import re
from pathlib import Path
from .base import BaseTool, ToolResult


class WebFetchTool(BaseTool):
    name = "web_fetch"
    description = (
        "Fetch content from a URL and return it as text. "
        "Automatically strips HTML tags and extracts readable text. "
        "Useful for reading web pages, API responses, documentation, etc. "
        "Maximum response size: 50000 characters."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch (must be a valid HTTP/HTTPS URL)",
            },
            "max_chars": {
                "type": "integer",
                "description": "Maximum characters to return. Default: 30000",
            },
        },
        "required": ["url"],
    }
    is_read_only = True

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        url = args["url"]
        max_chars = args.get("max_chars", 30000)

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            import httpx
        except ImportError:
            return ToolResult.error("httpx not installed. Run: pip install httpx")

        try:
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                headers={"User-Agent": "LiangClaw/1.0"},
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()

                content_type = resp.headers.get("content-type", "")
                text = resp.text

                # Strip HTML if needed
                if "html" in content_type.lower() or text.strip().startswith("<"):
                    text = self._html_to_text(text)

                if len(text) > max_chars:
                    text = text[:max_chars] + f"\n\n... (已截斷，原始長度約 {len(resp.text)} 字元)"

                return ToolResult.ok(f"URL: {url}\nStatus: {resp.status_code}\n{'─' * 40}\n{text}")

        except httpx.HTTPStatusError as e:
            return ToolResult.error(f"HTTP error {e.response.status_code}: {url}")
        except httpx.ConnectError:
            return ToolResult.error(f"Connection failed: {url}")
        except httpx.TimeoutException:
            return ToolResult.error(f"Request timed out: {url}")
        except Exception as e:
            return ToolResult.error(f"Fetch error: {e}")

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Simple HTML to text conversion."""
        # Remove script and style blocks
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Convert common block elements to newlines
        text = re.sub(r"<(br|hr|/p|/div|/h[1-6]|/li|/tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
        # Remove all remaining tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode common entities
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&nbsp;", " ").replace("&quot;", '"')
        # Clean up whitespace
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
