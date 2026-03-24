#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"

SPECIAL_PAGE_URLS = {
    "index.html": "/",
    "loaner-program.html": "/loaner-program/",
    "warranty-RENAME-index.html": "/warranty/",
    "g500-video.html": "/g500-video/",
    "g600-video.html": "/g600-video/",
    "van-tour.html": "/van-tour/",
}

PIXEL_CHECKS = {
    "gtm": (
        "googletagmanager.com/gtm.js?id=GTM-NP63652",
        "googletagmanager.com/ns.html?id=GTM-NP63652",
    ),
    "google_ads": (
        "googletagmanager.com/gtag/js?id=AW-667333334",
        "gtag('config', 'AW-667333334')",
    ),
    "facebook": (
        "connect.facebook.net/en_US/fbevents.js",
        "fbq('init', '403838910076167')",
        "facebook.com/tr?id=403838910076167&ev=PageView&noscript=1",
    ),
    "google_analytics": (
        "google-analytics.com/analytics.js",
        "ga('create', 'UA-38842004-1', 'auto')",
    ),
    "linkedin": (
        "_linkedin_partner_id = \"441156\"",
        "snap.licdn.com/li.lms-analytics/insight.min.js",
        "dc.ads.linkedin.com/collect/?pid=441156&fmt=gif",
    ),
    "plausible": ("plausible.io/js/plausible.js",),
    "pardot": (
        "piAId = '1125371'",
        "piCId = '132448'",
        "piHostname = 'go.visionsafe.com'",
        " + piHostname + '/pd.js'",
    ),
}


@dataclass
class PageResult:
    path: str
    url: str
    final_url: str | None
    status: int | None
    ok: bool
    missing_checks: list[str]
    error: str | None = None


def build_urls(base_url: str) -> list[tuple[str, str]]:
    pages = sorted(p.name for p in DIST_DIR.glob("*.html"))
    urls: list[tuple[str, str]] = []

    for page in pages:
        relative = SPECIAL_PAGE_URLS.get(page, f"/{page}")
        urls.append((page, urljoin(base_url.rstrip("/") + "/", relative.lstrip("/"))))

    return urls


def fetch_text(url: str, timeout: float) -> tuple[int, str, str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "visionsafe-pixel-check/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read().decode(charset, errors="replace")
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()
        status = getattr(response, "status", response.getcode())

    return status, content_type, final_url, body


def check_page(path: str, url: str, timeout: float, checks: dict[str, tuple[str, ...]]) -> PageResult:
    try:
        status, content_type, final_url, body = fetch_text(url, timeout)
    except HTTPError as exc:
        return PageResult(path, url, exc.geturl(), exc.code, False, [], f"HTTP {exc.code}")
    except URLError as exc:
        return PageResult(path, url, None, None, False, [], str(exc.reason))
    except Exception as exc:  # pragma: no cover
        return PageResult(path, url, None, None, False, [], str(exc))

    if "html" not in content_type.lower():
        return PageResult(path, url, final_url, status, False, [], f"unexpected content-type: {content_type}")

    missing = [name for name, markers in checks.items() if not all(marker in body for marker in markers)]
    ok = 200 <= status < 400 and not missing

    return PageResult(path, url, final_url, status, ok, missing)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch all deployed VisionSafe pages and verify live tracking snippets are present."
    )
    parser.add_argument(
        "--base-url",
        default="https://visionsafe.com",
        help="Base URL to test. Default: https://visionsafe.com",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Per-request timeout in seconds. Default: 15",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="PAGE",
        help="Optional dist HTML filenames to limit the run, e.g. index.html contact.html",
    )
    parser.add_argument(
        "--check",
        nargs="+",
        choices=sorted(PIXEL_CHECKS.keys()),
        help="Limit validation to specific checks, e.g. --check pardot",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)

    if not DIST_DIR.exists():
        print(f"dist directory not found: {DIST_DIR}", file=sys.stderr)
        return 2

    wanted = set(args.only or [])
    selected_checks = (
        {name: PIXEL_CHECKS[name] for name in args.check}
        if args.check
        else PIXEL_CHECKS
    )
    urls = build_urls(args.base_url)
    if wanted:
        urls = [item for item in urls if item[0] in wanted]

    if not urls:
        print("No pages selected.", file=sys.stderr)
        return 2

    results = [check_page(path, url, args.timeout, selected_checks) for path, url in urls]

    width = max(len(path) for path, _ in urls)
    for result in results:
        status_text = str(result.status) if result.status is not None else "ERR"
        label = "OK" if result.ok else "FAIL"
        print(f"{label:4} {status_text:>3} {result.path.ljust(width)} {result.url}")
        if result.error:
            print(f"      error: {result.error}")
        if result.final_url and result.final_url != result.url:
            print(f"      final: {result.final_url}")
        if result.missing_checks:
            print(f"      missing: {', '.join(result.missing_checks)}")

    failed = [result for result in results if not result.ok]
    print("")
    print(f"Checked {len(results)} page(s): {len(results) - len(failed)} OK, {len(failed)} failed")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
