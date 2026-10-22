#!/usr/bin/env python3
"""Build the static SVG assets for the profile README.

Everything is rendered offline from files in this repo:
  assets/fonts/   Plus Jakarta Sans + JetBrains Mono (latin subsets, OFL)
  assets/icons/   vendored logos (skillicons.dev tiles, simple-icons paths, Plone, Volto)

Run from anywhere:  python3 scripts/build_assets.py
Outputs go to assets/ (hero, buttons, divider, tech-stack grid), each in a
dark and a light variant where the README switches via <picture>.
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
ICONS = ASSETS / "icons"

# Brand tokens (mirrors nils-pzr.eu)
BG = {"dark": "#0a0a0a", "light": "#ffffff"}
FG = {"dark": "#fafafa", "light": "#0a0a0a"}
MUTED = {"dark": "#a1a1aa", "light": "#52525b"}
SUBTLE = {"dark": "#27272a", "light": "#e4e4e7"}
SURFACE = {"dark": "#121212", "light": "#f4f4f5"}
ACCENT_FROM, ACCENT_MID, ACCENT_TO = "#7e22ce", "#c026d3", "#e879f9"
TILE_FILL = "#242938"  # skillicons dark tile


def b64(p: Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()


PJS_B64 = b64(FONTS / "PlusJakartaSans-latin.woff2")
JBM_B64 = b64(FONTS / "JetBrainsMono-latin.woff2")

FONT_FACE_PJS = f"@font-face{{font-family:'PJS';font-weight:200 800;font-display:block;src:url(data:font/woff2;base64,{PJS_B64}) format('woff2');}}"
FONT_FACE_JBM = f"@font-face{{font-family:'JBM';font-weight:100 800;font-display:block;src:url(data:font/woff2;base64,{JBM_B64}) format('woff2');}}"
CLASS_H = ".h{font-family:'PJS','Plus Jakarta Sans',Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;}"
CLASS_M = ".m{font-family:'JBM','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}"


def write(name: str, svg: str) -> None:
    (ASSETS / name).write_text(svg, encoding="utf-8")
    print(f"  {name:28} {len(svg.encode()) / 1024:6.1f} KB")


# --------------------------------------------------------------------------
# Hero banner
# --------------------------------------------------------------------------
def hero(theme: str) -> str:
    dark = theme == "dark"
    W, H = 1200, 420
    dots = "rgba(255,255,255,0.10)" if dark else "rgba(10,10,10,0.10)"
    glow_a = 0.55 if dark else 0.28
    glow_b = 0.40 if dark else 0.20
    fg, muted = FG[theme], MUTED[theme]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Nils Plützer – Full-Stack Developer crafting modern web and mobile apps">
<style>{FONT_FACE_PJS}{FONT_FACE_JBM}{CLASS_H}{CLASS_M}</style>
<defs>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.2" fill="{dots}"/></pattern>
  <radialGradient id="fade" cx="50%" cy="45%" r="62%"><stop offset="0%" stop-color="#fff" stop-opacity="1"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="dotmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <radialGradient id="glowA" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{ACCENT_FROM}" stop-opacity="{glow_a}"/><stop offset="100%" stop-color="{ACCENT_FROM}" stop-opacity="0"/></radialGradient>
  <radialGradient id="glowB" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#d946ef" stop-opacity="{glow_b}"/><stop offset="100%" stop-color="#d946ef" stop-opacity="0"/></radialGradient>
  <linearGradient id="accent" gradientUnits="userSpaceOnUse" x1="190" y1="0" x2="520" y2="0">
    <stop offset="0%" stop-color="{ACCENT_FROM}"/><stop offset="55%" stop-color="{ACCENT_MID}"/><stop offset="100%" stop-color="{ACCENT_TO}"/>
    <animate attributeName="x1" values="190;130;190" dur="9s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="520;590;520" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{ACCENT_MID}" stop-opacity="0"/><stop offset="35%" stop-color="{ACCENT_FROM}"/><stop offset="65%" stop-color="#d946ef"/><stop offset="100%" stop-color="{ACCENT_MID}" stop-opacity="0"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="{BG[theme]}"/>
<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotmask)"/>
<ellipse cx="930" cy="80" rx="420" ry="220" fill="url(#glowA)"><animate attributeName="rx" values="420;470;420" dur="11s" repeatCount="indefinite"/></ellipse>
<ellipse cx="250" cy="380" rx="380" ry="200" fill="url(#glowB)"><animate attributeName="ry" values="200;240;200" dur="13s" repeatCount="indefinite"/></ellipse>

<g class="m" font-size="12.5" font-weight="500" letter-spacing="0.2">
  <g transform="translate(420 72)">
    <rect width="178" height="30" rx="15" fill="{SURFACE[theme]}" stroke="{SUBTLE[theme]}"/>
    <g transform="translate(14 8)" fill="none" stroke="{muted}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M9.3 11.7V2.3a1.2 1.2 0 0 0-1.2-1.2H5.9a1.2 1.2 0 0 0-1.2 1.2v9.4"/><rect x="1.2" y="3.5" width="11.6" height="8.1" rx="1.2"/>
    </g>
    <text x="34" y="19.5" fill="{muted}">@ Interaktiv GmbH</text>
  </g>
  <g transform="translate(610 72)">
    <rect width="170" height="30" rx="15" fill="{SURFACE[theme]}" stroke="{SUBTLE[theme]}"/>
    <circle cx="19" cy="15" r="4" fill="#22c55e"><animate attributeName="opacity" values="1;0.35;1" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="19" cy="15" r="4" fill="none" stroke="#22c55e" stroke-width="1.5" opacity="0.6"><animate attributeName="r" values="4;9" dur="2.2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0" dur="2.2s" repeatCount="indefinite"/></circle>
    <text x="32" y="19.5" fill="{muted}">Open to projects</text>
  </g>
</g>

<text class="h" x="600" y="196" text-anchor="middle" font-size="74" font-weight="800" letter-spacing="-2.5" fill="{fg}">Nils Plützer</text>
<text class="h" x="600" y="248" text-anchor="middle" font-size="29" font-weight="600" letter-spacing="-0.4" fill="{fg}"><tspan fill="url(#accent)" font-weight="700">Full-Stack Developer</tspan> crafting modern web &amp; mobile apps.</text>
<text class="m" x="600" y="306" text-anchor="middle" font-size="13.5" font-weight="500" letter-spacing="1.5" fill="{muted}">NEXT.JS   ·   REACT   ·   EXPO   ·   TYPESCRIPT   ·   PLONE   ·   PYTHON   ·   AI</text>
<text class="m" x="600" y="346" text-anchor="middle" font-size="12" font-weight="400" letter-spacing="0.5" fill="{muted}" opacity="0.7">Kerpen, Germany  —  nils-pzr.eu</text>
<rect x="0" y="{H - 2}" width="{W}" height="2" fill="url(#line)"/>
</svg>
"""


# --------------------------------------------------------------------------
# Divider
# --------------------------------------------------------------------------
DIVIDER = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="12" viewBox="0 0 1200 12">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="{ACCENT_MID}" stop-opacity="0"/><stop offset="30%" stop-color="{ACCENT_FROM}"/><stop offset="70%" stop-color="#d946ef"/><stop offset="100%" stop-color="{ACCENT_MID}" stop-opacity="0"/></linearGradient></defs>
<rect x="0" y="5" width="1200" height="2" rx="1" fill="url(#g)"/>
</svg>
"""


# --------------------------------------------------------------------------
# Link buttons (system font stack: tiny files)
# --------------------------------------------------------------------------
LUCIDE = {
    "arrow": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "at": '<circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/>',
}
LINKEDIN_PATH = "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"


def button(label: str, icon: str, width: int, primary: bool, theme: str) -> str:
    dark = theme == "dark"
    if primary:
        fill = stroke = FG[theme]
        fg = BG[theme]
    else:
        fill, stroke, fg = ("#141414", "#2a2a2e", "#fafafa") if dark else ("#fafafa", "#e4e4e7", "#0a0a0a")
    h, icon_x = 38, 16
    if icon == "linkedin":
        ic = f'<g transform="translate({icon_x} 11) scale(0.667)"><path fill="{fg}" d="{LINKEDIN_PATH}"/></g>'
    else:
        ic = f'<g transform="translate({icon_x} 11) scale(0.667)" fill="none" stroke="{fg}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{LUCIDE[icon]}</g>'
    text_cx = icon_x + 16 + 10 + (width - icon_x - 16 - 10 - 16) / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="{label}">
<rect x="0.5" y="0.5" width="{width - 1}" height="{h - 1}" rx="{(h - 1) / 2}" fill="{fill}" stroke="{stroke}"/>
{ic}
<text x="{text_cx:.1f}" y="24" text-anchor="middle" font-family="Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="14" font-weight="600" letter-spacing="-0.1" fill="{fg}">{label}</text>
</svg>
"""


# --------------------------------------------------------------------------
# Tech stack grid: labelled 48px tiles, grouped, packed into rows
# --------------------------------------------------------------------------
TILE, PITCH = 48, 92          # tile size and horizontal distance between tiles
GROUP_GAP = PITCH             # extra gap between two groups on the same row
ROW_CAP = 9                   # max tiles per row (9 * 92 - 44 = 784 px)
GRID_W = 832

# (label, source) – source is "tile:<skillicons file>", "si:<simple-icons file>:<color>", "plone", "volto"
GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Frontend", [("React", "tile:react"), ("Next.js", "tile:nextjs"), ("TypeScript", "tile:ts"), ("JavaScript", "tile:js"),
                  ("HTML", "tile:html"), ("CSS", "tile:css"), ("Tailwind", "tile:tailwind"), ("Bootstrap", "tile:bootstrap"),
                  ("shadcn/ui", "si:si-shadcnui:#ffffff")]),
    ("Mobile", [("Expo", "si:si-expo:#ffffff"), ("React Native", "si:si-react:#61DAFB"), ("SQLite", "tile:sqlite")]),
    ("CMS", [("Plone", "plone"), ("Volto", "volto"), ("Payload", "si:si-payloadcms:#ffffff")]),
    ("Backend", [("Node.js", "tile:nodejs"), ("Python", "tile:python"), ("Java", "tile:java"), ("Hono", "si:si-hono:"),
                 ("Better Auth", "si:si-betterauth:#ffffff"), ("Stripe", "si:si-stripe:")]),
    ("Data", [("PostgreSQL", "tile:postgres"), ("MySQL", "tile:mysql"), ("Supabase", "tile:supabase"), ("Drizzle", "si:si-drizzle:")]),
    ("Design & AI", [("Figma", "tile:figma"), ("Photoshop", "tile:ps"), ("Illustrator", "tile:ai"), ("Claude", "si:si-claude:")]),
    ("Infrastructure", [("Docker", "tile:docker"), ("NGINX", "tile:nginx"), ("Google Cloud", "tile:gcp"), ("Linux", "tile:linux"),
                        ("Bash", "tile:bash"), ("Git", "tile:git"), ("GitHub", "tile:github"), ("GitLab", "tile:gitlab")]),
]

_uid = 0


def namespace_ids(svg: str) -> str:
    """Prefix every id in an icon so several icons can share one document."""
    global _uid
    _uid += 1
    p = f"i{_uid}-"
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{p}{m.group(1)})', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{p}{m.group(1)}"', svg)
    return svg


def inner_svg(path: Path) -> str:
    """Return the content between the outer <svg ...> and </svg> of a file."""
    s = path.read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>(.*)</svg>", s, flags=re.S)
    assert m, path
    return m.group(1)


def si_path(path: Path, color: str) -> tuple[str, str]:
    s = path.read_text(encoding="utf-8")
    d = re.search(r' d="([^"]+)"', s).group(1)
    c = color or re.search(r'fill="(#[0-9A-Fa-f]{6})"', s).group(1)
    return c, d


def tile(source: str) -> str:
    """Render one 48x48 tile at the origin."""
    s = TILE / 256
    rx = 60 * s
    kind, _, rest = source.partition(":")
    if kind == "tile":  # skillicons file already contains its rounded background
        body = namespace_ids(inner_svg(ICONS / f"{rest}.svg"))
        return f'<g transform="scale({s:.5f})">{body}</g>'
    if kind == "si":
        name, _, color = rest.partition(":")
        c, d = si_path(ICONS / f"{name}.svg", color)
        k = 148 / 24 * s  # 24-unit icon drawn 148/256 of the tile
        off = (TILE - 148 * s) / 2
        return (f'<rect width="{TILE}" height="{TILE}" rx="{rx:.2f}" fill="{TILE_FILL}"/>'
                f'<g transform="translate({off:.3f} {off:.3f}) scale({k:.5f})"><path fill="{c}" d="{d}"/></g>')
    if kind == "plone":
        body = namespace_ids(inner_svg(ICONS / "plone.svg"))
        k = 150 / 40.686 * s
        off = (TILE - 150 * s) / 2
        return (f'<rect width="{TILE}" height="{TILE}" rx="{rx:.2f}" fill="{TILE_FILL}"/>'
                f'<g transform="translate({off:.3f} {off:.3f}) scale({k:.5f})">{body}</g>')
    if kind == "volto":
        global _uid
        _uid += 1
        cid = f"clip{_uid}"
        body = namespace_ids(inner_svg(ICONS / "volto.svg"))
        return (f'<clipPath id="{cid}"><rect width="{TILE}" height="{TILE}" rx="{rx:.2f}"/></clipPath>'
                f'<g clip-path="url(#{cid})"><g transform="scale({TILE / 800:.5f})">{body}</g></g>')
    raise ValueError(source)


def pack_rows() -> list[list[tuple[str, list[tuple[str, str]]]]]:
    rows: list[list] = []
    cur: list = []
    used = 0
    for g in GROUPS:
        n = len(g[1])
        need = n + (1 if cur else 0)
        if cur and used + need > ROW_CAP:
            rows.append(cur)
            cur, used = [], 0
            need = n
        cur.append(g)
        used += need
    if cur:
        rows.append(cur)
    return rows


def stack(theme: str) -> str:
    header_h, label_dy, row_gap = 26, 17, 26
    row_h = header_h + TILE + label_dy + row_gap
    rows = pack_rows()
    H = len(rows) * row_h - row_gap + 8
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{GRID_W}" height="{H}" viewBox="0 0 {GRID_W} {H}" role="img" aria-label="Tech stack">',
           f"<style>{FONT_FACE_JBM}{CLASS_M}</style>"]
    labels: list[str] = []
    y = 4
    for row in rows:
        x = 20  # left padding so centred labels like "PostgreSQL" are not clipped
        for name, items in row:
            out.append(f'<text class="m" x="{x}" y="{y + 11}" font-size="11" font-weight="600" letter-spacing="1.6" fill="{MUTED[theme]}">{name.upper().replace("&", "&amp;")}</text>')
            gx = x
            for label, src in items:
                out.append(f'<g transform="translate({gx} {y + header_h})"><title>{label}</title>{tile(src)}</g>')
                out.append(f'<text class="m" x="{gx + TILE / 2}" y="{y + header_h + TILE + label_dy}" text-anchor="middle" font-size="10.5" fill="{MUTED[theme]}">{label.replace("&", "&amp;")}</text>')
                labels.append(label)
                gx += PITCH
            x = gx - PITCH + TILE + GROUP_GAP + (PITCH - TILE)
        y += row_h
    out.append("</svg>\n")
    svg = "\n".join(out)
    return svg.replace('aria-label="Tech stack"', f'aria-label="Tech stack: {", ".join(labels)}"')


# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("assets/")
    for t in ("dark", "light"):
        write(f"hero-{t}.svg", hero(t))
        write(f"stack-{t}.svg", stack(t))
        write(f"btn-portfolio-{t}.svg", button("Portfolio", "arrow", 134, True, t))
        write(f"btn-linkedin-{t}.svg", button("LinkedIn", "linkedin", 130, False, t))
        write(f"btn-email-{t}.svg", button("Email", "mail", 108, False, t))
        write(f"btn-socials-{t}.svg", button("Socials", "at", 118, False, t))
    write("divider.svg", DIVIDER)
