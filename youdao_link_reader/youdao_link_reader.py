#!/usr/bin/env python3
"""
Read a Youdao Note public share link and extract plain text.

Usage:
  python3 youdao_link_reader.py 'https://share.note.youdao.com/s/XXXX'
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable, Optional


DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class NoteResult:
    share_key: str
    title: str
    text: str
    raw_meta: dict[str, Any]


class FetchError(RuntimeError):
    pass


def _http_get(url: str, *, timeout_s: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_UA})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read()


def _http_head_follow_location(url: str, *, timeout_s: int = 20) -> str:
    """
    Resolve a /s/<short> link to a /noteshare?id=<shareKey> redirect target.
    Returns the Location header value (absolute URL).
    """

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": DEFAULT_UA})
    try:
        with opener.open(req, timeout=timeout_s) as resp:  # noqa: F841
            # If server returns 200 with no redirect, fall back to original URL.
            return url
    except urllib.error.HTTPError as e:
        # For 30x, urllib raises HTTPError (since we disabled redirects).
        if 300 <= e.code < 400:
            location = e.headers.get("Location")
            if not location:
                raise FetchError(f"Redirect without Location header for: {url}")
            return urllib.parse.urljoin(url, location)
        raise


def _extract_share_key(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)

    for key in ("id", "token", "shareKey"):
        if key in query and query[key]:
            return query[key][0]

    # /noteshare?id=... already handled above; handle /s/<short>
    path = parsed.path.rstrip("/")
    if path.startswith("/s/") and len(path.split("/")) >= 3:
        resolved = _http_head_follow_location(url)
        return _extract_share_key(resolved)

    raise FetchError(f"Cannot find share key in url: {url}")


def _walk_text_nodes(data: Any) -> Iterable[str]:
    """
    Youdao note 'content' is JSON with many leaf nodes like {'8': 'text'}.
    Extract all such strings in document order.
    """
    if isinstance(data, dict):
        v = data.get("8")
        if isinstance(v, str):
            t = v.strip()
            if t:
                yield t
        for vv in data.values():
            yield from _walk_text_nodes(vv)
    elif isinstance(data, list):
        for item in data:
            yield from _walk_text_nodes(item)


def fetch_youdao_note(share_url: str) -> NoteResult:
    share_key = _extract_share_key(share_url)

    meta_url = (
        "https://share.note.youdao.com/yws/api/personal/share"
        f"?method=get&shareKey={urllib.parse.quote(share_key)}"
    )
    meta = json.loads(_http_get(meta_url).decode("utf-8", errors="replace"))
    title = meta.get("name") or meta.get("fileMeta", {}).get("title") or share_key
    # Clean common suffix like ".note"
    title = re.sub(r"\.note$", "", str(title)).strip()

    note_url = (
        "https://share.note.youdao.com/yws/api/note/"
        f"{urllib.parse.quote(share_key)}"
        "?sev=j1&editorType=1&editorVersion=new-json-editor"
    )
    note = json.loads(_http_get(note_url).decode("utf-8", errors="replace"))
    content_str = note.get("content", "")
    if not isinstance(content_str, str) or not content_str:
        raise FetchError("Unexpected note content payload (missing 'content').")
    content = json.loads(content_str)

    lines: list[str] = []
    for t in _walk_text_nodes(content):
        if not lines or lines[-1] != t:
            lines.append(t)
    text = "\n".join(lines).strip()

    return NoteResult(share_key=share_key, title=title, text=text, raw_meta=meta)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 2 if len(argv) != 2 else 0

    share_url = argv[1].strip()
    try:
        res = fetch_youdao_note(share_url)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"# {res.title}")
    print()
    print(res.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
