#!/usr/bin/env python3
"""Crawl same-domain pages and check links, assets, redirects, and HTTP mix.

Exit 0 is clean under the selected policy, 1 means broken links or another
configured failure, and 2 means the crawl could not start.
"""
from __future__ import annotations

import argparse
from collections import deque
from html.parser import HTMLParser
import os
import sys
import time
from urllib.parse import urldefrag, urljoin, urlparse

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "lib")))
try:
    from url_guard import safe_get, check_url, BlockedUrlError
except ImportError:
    sys.exit("url_guard.py not found - run from an intact site-doctor plugin")

UA = "site-doctor-linkcheck/1.0"
TIMEOUT = 12
MAX_BYTES = 2 * 1024 * 1024
MIN_REDIRECT_FETCH_LIMIT = 10


class LinkExtractor(HTMLParser):
    """Collect navigable links and resource URLs separately."""

    def __init__(self):
        super().__init__()
        self.links, self.assets = [], []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif (tag in ("img", "script", "iframe", "source", "video", "audio")
              and values.get("src")):
            self.assets.append(values["src"])
        elif tag == "link" and values.get("href"):
            self.assets.append(values["href"])


def positive_int(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_float(value):
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("start_url")
    parser.add_argument("--max-pages", type=positive_int, default=30)
    parser.add_argument("--delay", type=nonnegative_float, default=0.3)
    parser.add_argument(
        "--max-redirects",
        type=positive_int,
        default=1,
        help="fail URLs whose redirect chain exceeds this many hops",
    )
    parser.add_argument(
        "--mixed-content",
        choices=("warn", "fail"),
        default="warn",
        help="whether HTTP resources on HTTPS pages are warnings or failures",
    )
    return parser.parse_args(argv)


def request(url, method="HEAD", redirect_limit=MIN_REDIRECT_FETCH_LIMIT):
    """Return (status, final_url, redirect_hops, content_type, body_or_none)."""
    try:
        response = safe_get(
            url,
            method=method,
            timeout=TIMEOUT,
            allow_http=True,
            max_bytes=MAX_BYTES,
            max_redirects=redirect_limit,
            headers={"User-Agent": UA},
        )
    except BlockedUrlError as exc:
        return f"BLOCKED: {exc}", url, 0, "", None
    except Exception as exc:
        return f"ERR: {type(exc).__name__}", url, 0, "", None
    if method == "HEAD" and response.status in (403, 405, 501):
        return request(url, "GET", redirect_limit=redirect_limit)
    return (response.status, response.url, response.hops,
            response.headers.get("Content-Type", ""), response.body)


def skippable(url):
    return url.startswith(("mailto:", "tel:", "javascript:", "data:", "#"))


def main(argv=None):
    args = parse_args(argv)
    start = args.start_url.rstrip("/")
    host = urlparse(start).netloc
    if not host:
        print("Invalid URL")
        return 2
    try:
        check_url(start, allow_http=True)
    except BlockedUrlError as exc:
        print(f"BLOCKED unsafe target: {exc}")
        return 2

    redirect_fetch_limit = max(MIN_REDIRECT_FETCH_LIMIT, args.max_redirects + 1)
    queue = deque([start])
    seen_pages, checked = set(), {}
    broken, mixed, long_redirects = [], [], []

    while queue and len(seen_pages) < args.max_pages:
        page = queue.popleft()
        if page in seen_pages:
            continue
        seen_pages.add(page)
        status, final, hops, content_type, body = request(
            page, "GET", redirect_limit=redirect_fetch_limit
        )
        print(f"[crawl {len(seen_pages)}/{args.max_pages}] {status} {page}")
        if hops > args.max_redirects:
            long_redirects.append((page, final, hops))
        if not isinstance(status, int) or status >= 400 or body is None:
            broken.append((page, status, "(crawled page)"))
            continue
        if "html" not in content_type.lower():
            continue

        parser = LinkExtractor()
        try:
            parser.feed(body.decode("utf-8", errors="replace"))
        except Exception:
            continue

        page_https = urlparse(final).scheme.lower() == "https"
        for raw in parser.links + parser.assets:
            if skippable(raw):
                continue
            url = urldefrag(urljoin(final, raw))[0]
            scheme = urlparse(url).scheme.lower()
            if scheme not in ("http", "https"):
                continue
            if page_https and scheme == "http":
                mixed.append((final, url))
            if url not in checked:
                time.sleep(args.delay)
                link_status, link_final, link_hops, _, _ = request(
                    url, redirect_limit=redirect_fetch_limit
                )
                checked[url] = (link_status, link_final, link_hops)
                if not isinstance(link_status, int) or link_status >= 400:
                    broken.append((final, link_status, url))
                if link_hops > args.max_redirects:
                    long_redirects.append((url, link_final, link_hops))
            if (raw in parser.links and urlparse(url).netloc == host
                    and url not in seen_pages):
                queue.append(url)

    # A resource referenced repeatedly is one distinct mixed-content defect.
    mixed = list(dict.fromkeys(mixed))
    long_redirects = list(dict.fromkeys(long_redirects))

    print(f"\n=== Link check summary for {start} ===")
    print(f"Pages crawled: {len(seen_pages)}   Unique URLs checked: {len(checked)}")
    if broken:
        print(f"\nBROKEN ({len(broken)}):")
        for source, status, url in broken:
            print(f"  [{status}] {url}\n         found on: {source}")
    if long_redirects:
        print(f"\nREDIRECT CHAINS OVER {args.max_redirects} HOP(S) "
              f"({len(long_redirects)}):")
        for source, final, hops in long_redirects:
            print(f"  [{hops} hops] {source}\n         final: {final}")
    if mixed:
        level = "FAIL" if args.mixed_content == "fail" else "WARN"
        print(f"\nMIXED CONTENT [{level}] ({len(mixed)}):")
        for source, url in mixed:
            print(f"  {url}\n         loaded by: {source}")
    if not broken and not long_redirects and not mixed:
        print("No broken links, long redirects, or mixed content found.")

    failed = bool(broken or long_redirects)
    if args.mixed_content == "fail" and mixed:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
