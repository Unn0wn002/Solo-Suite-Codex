#!/usr/bin/env python3
"""Audit headers, HTTPS redirects, cookies, and exposed sensitive paths.

All outbound requests use the shared SSRF guard.  Exit 0 means no failures,
1 means at least one failure, and 2 means a target could not be checked.
"""
from __future__ import annotations

import os
import re
import sys
from urllib.parse import urljoin, urlparse, urlunparse

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "lib")))
try:
    from url_guard import safe_get, check_url, BlockedUrlError
except ImportError:
    sys.exit("url_guard.py not found - run from an intact site-doctor plugin")

UA = "solo-suite-site-doctor/1.0.11"
TIMEOUT = 15
MAX_HTTPS_REDIRECTS = 5
REDIRECT_STATUSES = (301, 302, 303, 307, 308)

SECURITY_HEADERS = {
    "strict-transport-security": "FAIL",
    "content-security-policy": "WARN",
    "x-content-type-options": "FAIL",
    "x-frame-options": "WARN",
    "referrer-policy": "WARN",
    "permissions-policy": "WARN",
}
LEAKY_HEADERS = ("server", "x-powered-by", "x-aspnet-version")
SENSITIVE_PATHS = ("/.env", "/.git/HEAD", "/.git/config", "/wp-config.php.bak")

results = {"PASS": 0, "WARN": 0, "FAIL": 0}


def report(level, msg):
    results[level] += 1
    print(f"  [{level}] {msg}")


def fetch(url, follow_redirects=True, method="GET"):
    try:
        response = safe_get(
            url,
            method=method,
            follow_redirects=follow_redirects,
            timeout=TIMEOUT,
            allow_http=True,
            read_body=False,
            headers={"User-Agent": UA, "Accept-Encoding": "gzip, br"},
        )
        return (
            response.status,
            {key.lower(): value for key, value in response.headers.items()},
            response.headers.get_all("Set-Cookie") or [],
        )
    except BlockedUrlError as exc:
        return None, {"_error": f"BLOCKED unsafe target: {exc}"}, []
    except Exception as exc:
        return None, {"_error": f"{type(exc).__name__}: {exc}"}, []


def _host(url):
    return (urlparse(url).hostname or "").rstrip(".").lower()


def check_https_redirect(url):
    """Follow and validate every HTTP redirect hop before declaring success."""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        report("FAIL", f"Target is not HTTPS: {url}")
        return

    http_url = urlunparse(("http",) + parsed[1:])
    expected_host = _host(url)
    current = http_url
    seen = set()
    permanent = True
    stayed_http = False

    for hop in range(MAX_HTTPS_REDIRECTS + 1):
        if current in seen:
            report("FAIL", "HTTP redirect loop detected")
            return
        seen.add(current)
        status, headers, _ = fetch(current, follow_redirects=False)
        if status is None:
            level = "WARN" if hop == 0 else "FAIL"
            report(level, f"Could not validate redirect hop {hop + 1}: "
                   f"{headers.get('_error')}")
            return

        if status not in REDIRECT_STATUSES:
            if hop == 0:
                report("FAIL", f"HTTP does not redirect to HTTPS (got {status})")
                return
            final = urlparse(current)
            if final.scheme.lower() != "https":
                report("FAIL", "HTTP redirect chain did not finish on HTTPS")
            elif _host(current) != expected_host:
                report("FAIL", "HTTP redirect chain changed to an unrelated host")
            elif status >= 400:
                report("WARN", f"HTTPS redirect target returned {status}")
            elif not permanent or stayed_http:
                reasons = []
                if not permanent:
                    reasons.append("uses a temporary redirect")
                if stayed_http:
                    reasons.append("contains an intermediate HTTP hop")
                report("WARN", "HTTP reaches HTTPS but " + " and ".join(reasons))
            else:
                report("PASS", "HTTP redirects permanently to HTTPS on the same host")
            return

        location = headers.get("location")
        if not location:
            report("FAIL", f"Redirect {status} has no Location header")
            return
        next_url = urljoin(current, location)
        try:
            check_url(next_url, allow_http=True)
        except BlockedUrlError as exc:
            report("FAIL", f"Unsafe redirect hop blocked: {exc}")
            return
        if _host(next_url) != expected_host:
            report("FAIL", "HTTP redirects to an unrelated host")
            return
        if urlparse(next_url).scheme.lower() == "http":
            stayed_http = True
        if status not in (301, 308):
            permanent = False
        current = next_url

    report("FAIL", f"HTTP redirect chain exceeds {MAX_HTTPS_REDIRECTS} hops")


_TOKEN = r"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
_EXTENSION = re.compile(
    rf"^\s*{_TOKEN}(?:\s*=\s*(?:{_TOKEN}|\"[^\"]*\"))?\s*$"
)


def validate_hsts(value, is_https=True):
    """Validate STS grammar and its security-relevant max-age semantics."""
    parts = value.split(";")
    if parts and not parts[-1].strip():
        parts.pop()
    if not parts or any(not part.strip() for part in parts):
        report("FAIL", "Invalid strict-transport-security syntax")
        return

    seen = set()
    max_age = None
    for part in parts:
        name = part.split("=", 1)[0].strip().lower()
        if name in seen:
            report("FAIL", f"Duplicate HSTS directive: {name}")
            return
        seen.add(name)
        if name == "max-age":
            match = re.fullmatch(
                r"\s*max-age\s*=\s*(\d+)\s*", part, flags=re.IGNORECASE
            )
            if not match:
                report("FAIL", "HSTS max-age must be one non-negative integer")
                return
            max_age = int(match.group(1))
        elif name in ("includesubdomains", "preload"):
            if not re.fullmatch(rf"\s*{name}\s*", part, flags=re.IGNORECASE):
                report("FAIL", f"HSTS {name} directive must not have a value")
                return
        elif not _EXTENSION.fullmatch(part):
            report("FAIL", "Invalid strict-transport-security extension syntax")
            return

    if max_age is None:
        report("FAIL", "HSTS is missing the required max-age directive")
    elif not is_https:
        report("WARN", "HSTS sent over HTTP is ignored by browsers")
    elif max_age == 0:
        report("WARN", "HSTS max-age=0 disables the policy")
    elif max_age < 15552000:
        report("WARN", f"HSTS max-age is short ({max_age}s); recommend >= 15552000")
    else:
        report("PASS", f"strict-transport-security is valid (max-age={max_age})")


def check_security_headers(headers, is_https=True):
    for name, missing_level in SECURITY_HEADERS.items():
        if name in headers:
            if name == "strict-transport-security":
                validate_hsts(headers[name], is_https=is_https)
            else:
                report("PASS", f"{name}: {headers[name][:90]}")
        elif (name == "x-frame-options" and
              "frame-ancestors" in headers.get("content-security-policy", "")):
            report("PASS", "frame-ancestors set via CSP (x-frame-options not needed)")
        else:
            report(missing_level, f"Missing header: {name}")

    for name in LEAKY_HEADERS:
        value = headers.get(name, "")
        if any(character.isdigit() for character in value):
            report("WARN", f"Version leakage: {name}: {value}")


def check_caching_and_compression(headers):
    encoding = headers.get("content-encoding", "")
    if encoding in ("gzip", "br", "zstd"):
        report("PASS", f"Compression enabled ({encoding})")
    else:
        report("WARN", "No compression on this response (gzip/brotli)")
    cache_control = headers.get("cache-control")
    if cache_control:
        report("PASS", f"cache-control: {cache_control}")
    else:
        report("WARN", "No cache-control header")


def check_cookies(cookies):
    for cookie in cookies:
        name = cookie.split("=", 1)[0]
        attributes = {
            part.split("=", 1)[0].strip().lower()
            for part in cookie.split(";")[1:]
            if part.strip()
        }
        missing = [flag for flag in ("secure", "httponly", "samesite")
                   if flag not in attributes]
        if missing:
            report("WARN", f"Cookie '{name}' missing flags: {', '.join(missing)}")
        else:
            report("PASS", f"Cookie '{name}' has Secure/HttpOnly/SameSite")


def check_sensitive_paths(url):
    base = "{0.scheme}://{0.netloc}".format(urlparse(url))
    for path in SENSITIVE_PATHS:
        status, headers, _ = fetch(base + path)
        if status == 200:
            content_type = headers.get("content-type", "")
            if "html" in content_type and path != "/.env":
                report("WARN", f"{path} returns 200 with HTML - likely a soft-404")
            else:
                report("FAIL", f"EXPOSED: {base}{path} returns 200")
        elif status is None:
            report("WARN", f"Could not verify {path}: {headers.get('_error')}")
        elif status in (401, 403, 404):
            report("PASS", f"{path} not exposed ({status})")
        else:
            report("WARN", f"{path} returned {status} - verify manually")


def main(urls):
    results.update({"PASS": 0, "WARN": 0, "FAIL": 0})
    exit_code = 0
    for url in urls:
        print(f"\n=== {url} ===")
        try:
            check_url(url, allow_http=True)
        except BlockedUrlError as exc:
            print(f"  [BLOCKED] unsafe target: {exc}")
            exit_code = max(exit_code, 2)
            continue
        status, headers, cookies = fetch(url)
        if status is None:
            print(f"  [ERROR] Could not connect: {headers.get('_error')}")
            exit_code = max(exit_code, 2)
            continue
        print(f"  Status: {status}")
        check_https_redirect(url)
        check_security_headers(
            headers, is_https=urlparse(url).scheme.lower() == "https"
        )
        check_caching_and_compression(headers)
        check_cookies(cookies)
        check_sensitive_paths(url)
    print(f"\nTotals: {results['PASS']} pass, {results['WARN']} warn, "
          f"{results['FAIL']} fail")
    if results["FAIL"]:
        exit_code = max(exit_code, 1)
    return exit_code


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1:]))
