#!/usr/bin/env python3
"""Render the GitHub stats card (dark + light) for the profile README.

Data sources (all public, a token only raises the rate limits):
  - contribution calendar: the same HTML endpoint GitHub's own profile uses
  - commits / pull requests / issues: REST search API
  - stars and languages: REST repos API

Usage:
  python3 scripts/build_stats.py --login nils-pzr --out dist [--token "$GITHUB_TOKEN"]
  python3 scripts/build_stats.py --mock stats.json --out dist     # render from a saved fixture

Writes <out>/stats-dark.svg, <out>/stats-light.svg and <out>/stats.json.
Only the standard library is used so it runs on a bare GitHub Actions runner.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"

UA = "nils-pzr-profile-stats (+https://github.com/nils-pzr/nils-pzr)"
NOISE_LANGS = {"Dockerfile", "Shell", "Makefile", "Batchfile", "Procfile", "PowerShell"}
LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "CSS": "#663399", "HTML": "#e34c26", "SCSS": "#c6538c",
    "Python": "#3572A5", "Java": "#b07219", "PHP": "#4F5D95", "MDX": "#fcb32c", "Vue": "#41b883", "Svelte": "#ff3e00",
    "Go": "#00ADD8", "Rust": "#dea584", "C#": "#178600", "Swift": "#F05138", "Kotlin": "#A97BFF", "Ruby": "#701516",
    "Astro": "#ff5a03", "Shell": "#89e051", "Dockerfile": "#384d54", "Jupyter Notebook": "#DA5B0B", "Dart": "#00B4AB",
}


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------
def http_get(url: str, token: str | None, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def get_json(url: str, token: str | None):
    return json.loads(http_get(url, token))


def contributions_for_year(login: str, year: int, token: str | None) -> dict[str, int]:
    """Parse the public contribution calendar into {YYYY-MM-DD: count}."""
    url = f"https://github.com/users/{login}/contributions?from={year}-01-01&to={year}-12-31"
    html = http_get(url, None, accept="text/html").decode("utf-8", "replace")
    days: dict[str, str] = {}
    for tag in re.findall(r"<td\b[^>]*\bdata-date=\"[^\"]+\"[^>]*>", html):
        date = re.search(r'data-date="([^"]+)"', tag).group(1)
        ident = re.search(r'\bid="([^"]+)"', tag)
        if ident:
            days[ident.group(1)] = date
    counts: dict[str, int] = {}
    for ident, text in re.findall(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        if ident not in days:
            continue
        m = re.match(r"\s*(No|[\d,]+) contribution", text)
        if not m:
            continue
        n = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
        counts[days[ident]] = n
    if not counts and days:
        raise RuntimeError(f"contribution calendar for {year} parsed 0 counts (markup changed?)")
    return counts


def streaks(counts: dict[str, int], today: dt.date) -> tuple[int, int]:
    """(current streak, longest streak) in days."""
    active = {dt.date.fromisoformat(d) for d, n in counts.items() if n > 0}
    longest = cur = 0
    prev = None
    for d in sorted(active):
        cur = cur + 1 if prev and (d - prev).days == 1 else 1
        longest = max(longest, cur)
        prev = d
    # current streak may end today or yesterday
    end = today if today in active else today - dt.timedelta(days=1)
    current = 0
    while end in active:
        current += 1
        end -= dt.timedelta(days=1)
    return current, longest


def fetch(login: str, token: str | None) -> dict:
    today = dt.date.today()
    user = get_json(f"https://api.github.com/users/{login}", token)
    created = dt.datetime.fromisoformat(user["created_at"].replace("Z", "+00:00")).date()

    calendar: dict[str, int] = {}
    for year in range(created.year, today.year + 1):
        calendar.update(contributions_for_year(login, year, token))
    calendar = {d: n for d, n in calendar.items() if dt.date.fromisoformat(d) <= today}
    year_ago = today - dt.timedelta(days=365)
    last_year = sum(n for d, n in calendar.items() if dt.date.fromisoformat(d) > year_ago)
    current, longest = streaks(calendar, today)

    repos = get_json(f"https://api.github.com/users/{login}/repos?per_page=100&type=owner", token)
    stars = sum(r["stargazers_count"] for r in repos)
    lang_bytes: dict[str, int] = {}
    for r in repos:
        if r["fork"] or r["archived"]:
            continue
        for lang, n in get_json(r["languages_url"], token).items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n

    def search(kind: str, q: str) -> int:
        url = f"https://api.github.com/search/{kind}?q={urllib.parse.quote(q)}&per_page=1"
        return int(get_json(url, token)["total_count"])

    return {
        "login": login,
        "updated": today.isoformat(),
        "member_since": created.year,
        "contributions_total": sum(calendar.values()),
        "contributions_last_year": last_year,
        "streak_current": current,
        "streak_longest": longest,
        "commits": search("commits", f"author:{login}"),
        "pull_requests": search("issues", f"author:{login} is:pr"),
        "issues": search("issues", f"author:{login} is:issue"),
        "stars": stars,
        "public_repos": user["public_repos"],
        "followers": user["followers"],
        "languages": lang_bytes,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def b64(p: Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()


def fmt(n: int) -> str:
    return f"{n:,}"


def top_languages(lang_bytes: dict[str, int], n: int = 5) -> list[tuple[str, float, str]]:
    clean = {k: v for k, v in lang_bytes.items() if k not in NOISE_LANGS}
    total = sum(clean.values()) or 1
    ranked = sorted(clean.items(), key=lambda kv: kv[1], reverse=True)[:n]
    return [(k, v / total * 100, LANG_COLORS.get(k, "#c026d3")) for k, v in ranked]


def render(data: dict, theme: str) -> str:
    dark = theme == "dark"
    bg, fg = ("#0a0a0a", "#fafafa") if dark else ("#ffffff", "#0a0a0a")
    muted, subtle, surface = ("#a1a1aa", "#27272a", "#121212") if dark else ("#52525b", "#e4e4e7", "#f4f4f5")
    track = "#1f1f23" if dark else "#e4e4e7"
    W, H, PAD = 832, 236, 22
    pjs, jbm = b64(FONTS / "PlusJakartaSans-latin.woff2"), b64(FONTS / "JetBrainsMono-latin.woff2")
    style = (f"@font-face{{font-family:'PJS';font-weight:200 800;src:url(data:font/woff2;base64,{pjs}) format('woff2');}}"
             f"@font-face{{font-family:'JBM';font-weight:100 800;src:url(data:font/woff2;base64,{jbm}) format('woff2');}}"
             ".h{font-family:'PJS','Plus Jakarta Sans',Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
             ".m{font-family:'JBM','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}")

    updated = dt.date.fromisoformat(data["updated"]).strftime("%d %b %Y")
    tiles = [
        (fmt(data["contributions_total"]), "Contributions"),
        (fmt(data["commits"]), "Commits"),
        (fmt(data["pull_requests"]), "Pull requests"),
        (fmt(data["issues"]), "Issues"),
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="GitHub stats for {data["login"]}: {tiles[0][0]} contributions, {tiles[1][0]} commits, {tiles[2][0]} pull requests, {tiles[3][0]} issues">',
           f"<style>{style}</style>",
           '<defs><linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#7e22ce"/><stop offset="100%" stop-color="#e879f9"/></linearGradient></defs>',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{bg}" stroke="{subtle}"/>']

    # header
    out.append(f'<text class="h" x="{PAD}" y="{PAD + 15}" font-size="15" font-weight="700" letter-spacing="-0.2" fill="{fg}">Activity</text>')
    out.append(f'<text class="m" x="{W - PAD}" y="{PAD + 14}" text-anchor="end" font-size="10.5" letter-spacing="0.4" fill="{muted}">@{data["login"]}  ·  since {data["member_since"]}  ·  updated {updated}</text>')

    # stat tiles
    ty, th, gap = PAD + 32, 78, 12
    tw = (W - 2 * PAD - 3 * gap) / 4
    for i, (num, label) in enumerate(tiles):
        x = PAD + i * (tw + gap)
        out.append(f'<rect x="{x:.1f}" y="{ty}" width="{tw:.1f}" height="{th}" rx="10" fill="{surface}"/>')
        out.append(f'<rect x="{x + 14:.1f}" y="{ty + 16}" width="3" height="{th - 32}" rx="1.5" fill="url(#acc)"/>')
        out.append(f'<text class="h" x="{x + 28:.1f}" y="{ty + 38}" font-size="28" font-weight="800" letter-spacing="-1" fill="{fg}">{num}</text>')
        out.append(f'<text class="m" x="{x + 28:.1f}" y="{ty + 58}" font-size="10.5" font-weight="600" letter-spacing="1.2" fill="{muted}">{label.upper()}</text>')

    # languages
    ly = ty + th + 28
    langs = top_languages(data["languages"])
    out.append(f'<text class="m" x="{PAD}" y="{ly}" font-size="10.5" font-weight="600" letter-spacing="1.2" fill="{muted}">TOP LANGUAGES</text>')
    bar_y, bar_h, bar_w = ly + 12, 8, W - 2 * PAD
    out.append(f'<clipPath id="bar"><rect x="{PAD}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="4"/></clipPath>')
    out.append(f'<rect x="{PAD}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{track}"/>')
    x = float(PAD)
    for name, pct, color in langs:
        w = bar_w * pct / 100
        out.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{max(w, 2):.2f}" height="{bar_h}" fill="{color}" clip-path="url(#bar)"/>')
        x += w
    lx, lyy = PAD, bar_y + bar_h + 22
    for name, pct, color in langs:
        out.append(f'<circle cx="{lx + 5}" cy="{lyy - 4}" r="4.5" fill="{color}"/>')
        out.append(f'<text class="m" x="{lx + 16}" y="{lyy}" font-size="11" fill="{fg}">{name} <tspan fill="{muted}">{pct:.1f}%</tspan></text>')
        lx += 16 + int(6.7 * (len(name) + 7)) + 22
    out.append("</svg>\n")
    return "\n".join(out)


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default="nils-pzr")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--token", default=None)
    ap.add_argument("--mock", help="render from a saved stats.json instead of fetching")
    a = ap.parse_args()

    if a.mock:
        data = json.loads(Path(a.mock).read_text(encoding="utf-8"))
    else:
        try:
            data = fetch(a.login, a.token)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, KeyError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 1

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "stats.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    for theme in ("dark", "light"):
        (out / f"stats-{theme}.svg").write_text(render(data, theme), encoding="utf-8")
    print(f"ok: {out}/stats-dark.svg, stats-light.svg  ({data['contributions_total']} contributions, "
          f"{data['commits']} commits, {data['pull_requests']} PRs, {data['issues']} issues)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
