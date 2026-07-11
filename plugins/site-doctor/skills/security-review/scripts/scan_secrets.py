#!/usr/bin/env python3
"""Scan a tree for likely hardcoded secrets without disclosing them.

Findings contain only a relative path, line number, rule name, a short
prefix/suffix redaction, and a SHA-256 fingerprint.  Complete matching lines
and complete secret values are never retained in the findings or printed.

Usage:
    python3 scan_secrets.py /path/to/repo [--max-bytes 2000000] [--json]

Findings are heuristic and require human verification.  Exit 1 if any are
found, 0 if none are found, and 2 for invalid input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys


SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next",
             "__pycache__", ".venv", "venv", "coverage", ".cache"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
            ".pdf", ".zip", ".gz", ".tar", ".mp4", ".woff", ".woff2",
            ".ttf", ".eot", ".lock", ".min.js", ".map"}

# Patterns use a named ``secret`` group so only the credential itself is
# fingerprinted/redacted.  Keep specific rules before generic assignments.
PATTERNS = [
    ("AWS Access Key ID", re.compile(r"(?P<secret>AKIA[0-9A-Z]{16})")),
    ("AWS Secret Access Key", re.compile(
        r"(?i)aws.{0,20}?['\"](?P<secret>[0-9a-zA-Z/+]{40})['\"]")),
    ("GitHub token", re.compile(r"(?P<secret>gh[pousr]_[0-9A-Za-z]{36,})")),
    ("Slack token", re.compile(r"(?P<secret>xox[baprs]-[0-9A-Za-z-]{10,})")),
    ("Google API key", re.compile(r"(?P<secret>AIza[0-9A-Za-z_-]{35})")),
    ("Stripe live key", re.compile(r"(?P<secret>sk_live_[0-9a-zA-Z]{20,})")),
    ("Xendit secret key", re.compile(
        r"(?P<secret>xnd_(?:development|production)_[0-9A-Za-z]{20,})")),
    ("Midtrans server key", re.compile(
        r"(?P<secret>(?:SB-)?Mid-server-[0-9A-Za-z_-]{16,})")),
    ("SendGrid key", re.compile(
        r"(?P<secret>SG\.[0-9A-Za-z_-]{20,}\.[0-9A-Za-z_-]{20,})")),
    ("Resend key", re.compile(r"\b(?P<secret>re_[0-9A-Za-z]{16,})")),
    ("Supabase access token", re.compile(r"(?P<secret>sbp_[0-9a-f]{40})")),
    ("Supabase secret key", re.compile(
        r"(?P<secret>sb_secret_[0-9A-Za-z_-]{20,})")),
    ("Vercel token assignment", re.compile(
        r"(?i)vercel.{0,15}['\"](?P<secret>[0-9A-Za-z]{24})['\"]")),
    ("Cloudflare API token assignment", re.compile(
        r"(?i)cloudflare.{0,20}['\"](?P<secret>[0-9A-Za-z_-]{40})['\"]")),
    ("OpenAI key", re.compile(r"(?P<secret>sk-[A-Za-z0-9]{20,})")),
    ("JWT", re.compile(
        r"(?P<secret>eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\."
        r"[A-Za-z0-9_-]{10,})")),
    ("Generic API key assignment", re.compile(
        r"(?i)(?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|"
        r"client[_-]?secret)\s*[:=]\s*['\"]"
        r"(?P<secret>[0-9a-zA-Z_-]{16,})['\"]")),
    ("Hardcoded password assignment", re.compile(
        r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]"
        r"(?P<secret>[^'\"]{6,})['\"]")),
    ("Connection string with credentials", re.compile(
        r"(?i)(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|amqp)://"
        r"[^:@\s'\"]+:(?P<secret>[^@\s'\"]+)@")),
]

PRIVATE_KEY_BEGIN = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"
)
PRIVATE_KEY_END = re.compile(
    r"-----END (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"
)
SELF = os.path.realpath(__file__)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _redact(secret: str) -> str:
    """Expose at most four prefix/suffix characters, never a complete value."""
    if len(secret) <= 12:
        return "<redacted>"
    return f"{secret[:4]}...{secret[-4:]}"


def _finding(relative_path: str, line: int, rule: str,
             secret: str | None = None, fingerprint=None) -> dict:
    if fingerprint is None:
        fingerprint = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    return {
        "path": relative_path.replace(os.sep, "/"),
        "line": line,
        "rule": rule,
        "redacted": _redact(secret) if secret is not None else "----...----",
        "fingerprint": fingerprint,
    }


def scan_file(path: str, root: str, max_bytes: int) -> list[dict]:
    """Return sanitized findings; never place raw lines/secrets in the list."""
    if os.path.realpath(path) == SELF:  # rule source is not a scan target
        return []
    try:
        if os.path.getsize(path) > max_bytes:
            return []
    except OSError:
        return []

    relative = os.path.relpath(path, root)
    findings = []
    key_hasher = None
    key_line = None
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for lineno, line in enumerate(handle, 1):
                if key_hasher is not None:
                    key_hasher.update(line.encode("utf-8"))
                    if PRIVATE_KEY_END.search(line):
                        findings.append(_finding(
                            relative, key_line, "Private key block",
                            fingerprint=key_hasher.hexdigest(),
                        ))
                        key_hasher = None
                        key_line = None
                    continue

                begin = PRIVATE_KEY_BEGIN.search(line)
                if begin:
                    key_hasher = hashlib.sha256()
                    key_hasher.update(line.encode("utf-8"))
                    key_line = lineno
                    if PRIVATE_KEY_END.search(line, begin.end()):
                        findings.append(_finding(
                            relative, key_line, "Private key block",
                            fingerprint=key_hasher.hexdigest(),
                        ))
                        key_hasher = None
                        key_line = None
                    continue

                if len(line) > 2000:  # skip minified/data lines
                    continue
                for rule, pattern in PATTERNS:
                    match = pattern.search(line)
                    if match:
                        secret = match.group("secret")
                        findings.append(_finding(relative, lineno, rule, secret))
                        break
    except (OSError, UnicodeError):
        return []

    # An unterminated key is still a finding.  The incremental digest contains
    # all bytes seen, but the complete block was never accumulated in memory.
    if key_hasher is not None:
        findings.append(_finding(
            relative, key_line, "Private key block",
            fingerprint=key_hasher.hexdigest(),
        ))
    return findings


def scan_tree(root: str, max_bytes: int) -> tuple[int, list[dict]]:
    scanned = 0
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for name in filenames:
            if any(name.endswith(ext) for ext in SKIP_EXT):
                continue
            path = os.path.join(dirpath, name)
            findings.extend(scan_file(path, root, max_bytes))
            scanned += 1
    return scanned, findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--max-bytes", type=positive_int, default=2_000_000)
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable sanitized findings")
    args = parser.parse_args(argv)

    root = os.path.realpath(args.root)
    if not os.path.exists(root):
        parser.error("scan root does not exist")

    scanned, findings = scan_tree(root, args.max_bytes)
    if args.json:
        print(json.dumps({"scanned_files": scanned, "findings": findings},
                         sort_keys=True))
    else:
        print(f"Scanned {scanned} files.\n")
        if not findings:
            print("No obvious hardcoded secrets found.")
            print("(Absence of matches is not proof of safety; review auth and "
                  "configuration handling manually too.)")
        else:
            print(f"POTENTIAL SECRETS ({len(findings)}) - verify each before acting:\n")
            for finding in findings:
                print(f"  [{finding['rule']}]")
                print(f"    {finding['path']}:{finding['line']}")
                print(f"    redacted: {finding['redacted']}")
                print(f"    sha256: {finding['fingerprint']}\n")
            print("If a real secret was ever committed, rotate it; version-control "
                  "history retains it after deletion.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
