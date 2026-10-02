#!/usr/bin/env python3
"""Build the Zune investor brief PDF.

Usage (repo root):  python3 docs/investor/build_pdf.py
Inputs : docs/REQUIREMENTS.md, docs/investor/content/extracted.json (from extract-workflow.js)
Outputs: docs/investor/Zune-Investor-Brief.pdf  (+ brief.html, previews/ for QA)
Needs  : node + playwright (docs/investor/render.js), pdftoppm (previews only).
"""
import html
import json
import os
import re
import subprocess
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INV = os.path.join(ROOT, "docs", "investor")
CONTENT = os.path.join(INV, "content", "extracted.json")
AS_OF = "2 Oct 2026"

# ---------------------------------------------------------------- tokens
INK, MUTED, LINE, BG = "#0f172a", "#5b6475", "#e3e6ec", "#ffffff"
BRAND, BRAND_SOFT = "#4f46e5", "#eef0ff"
TEAL, TEAL_SOFT = "#0d9488", "#e6f6f4"
AMBER, AMBER_SOFT = "#b45309", "#fef3c7"
RED, RED_SOFT = "#b91c1c", "#fee2e2"
GREEN, GREEN_SOFT = "#15803d", "#dcfce7"
SLATE_SOFT = "#f1f3f8"


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def chip(text, kind="mute"):
    return f'<span class="chip {kind}">{esc(text)}</span>'


CONF = {
    "verified": ("verified", "ok"),
    "partly-verified": ("partly verified", "warn"),
    "unverified": ("unverified", "bad"),
    "superseded": ("superseded", "mute"),
}
SEV = {"H": ("High", "bad"), "M": ("Medium", "warn"), "L": ("Low", "ok")}
BASIS = {"verified": ("sourced", "ok"), "reported": ("reported", "warn"), "estimate": ("estimate", "bad"),
         "primary": ("primary", "ok"), "secondary": ("secondary", "warn")}

ICONS = {
    "chat": '<path d="M4 5h16v11H10l-5 4v-4H4z"/>',
    "video": '<rect x="3" y="6" width="12" height="12" rx="2"/><path d="M15 10l6-3v10l-6-3z"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    "spark": '<path d="M12 3l2.2 6.2L21 12l-6.8 2.8L12 21l-2.2-6.2L3 12l6.8-2.8z"/>',
    "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l6 3.5-6 3.5z"/>',
    "cloud": '<path d="M7 18a4 4 0 0 1-.5-8A6 6 0 0 1 18 9a4.5 4.5 0 0 1-.5 9z"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M4 18l5-5 4 4 3-3 4 4"/>',
    "book": '<path d="M4 5h6a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H4zM20 5h-6a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h6z"/>',
    "pencil": '<path d="M4 20l1-4L16 5l3 3L8 19zM14 7l3 3"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
    "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "wifi": '<path d="M3 9a14 14 0 0 1 18 0M6 12.5a9 9 0 0 1 12 0M9 16a4.5 4.5 0 0 1 6 0"/><circle cx="12" cy="19" r="1"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "users": '<circle cx="9" cy="9" r="3"/><path d="M3 20a6 6 0 0 1 12 0M16 6a3 3 0 0 1 0 6M18 20a5 5 0 0 0-3-4.5"/>',
    "bolt": '<path d="M13 2L5 14h6l-1 8 8-12h-6z"/>',
    "alert": '<path d="M12 3l10 18H2zM12 10v5M12 18v.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "key": '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    "walkie": '<rect x="7" y="8" width="10" height="13" rx="2"/><path d="M10 8V3M8 12h8M8 15h8"/>',
    "server": '<rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><path d="M7 7h.01M7 17h.01"/>',
    "rupee": '<path d="M7 5h10M7 9h10M7 5c6 0 6 8 0 8l6 6"/>',
    "chart": '<path d="M4 20V4M4 20h16M8 16v-5M12 16V8M16 16v-3"/>',
    "scale": '<path d="M12 4v16M6 20h12M5 7h14M5 7l-2.5 6a3 3 0 0 0 5 0zM19 7l-2.5 6a3 3 0 0 0 5 0z"/>',
    "box": '<path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10"/>',
}


def icon(name, size=18, color="currentColor", sw=1.8):
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICONS.get(name, "")}</svg>')


CSS = f"""
@page {{ size: 297mm 210mm; margin: 0 }}
* {{ box-sizing: border-box }}
html, body {{ margin: 0; padding: 0; background: #fff }}
body {{ font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; color: {INK}; font-size: 9.6pt; line-height: 1.38 }}
.page {{ width: 297mm; height: 210mm; position: relative; overflow: hidden; page-break-after: always; background: {BG} }}
.page:last-child {{ page-break-after: auto }}
.hdr {{ position: absolute; top: 6.5mm; left: 16mm; right: 16mm; display: flex; justify-content: space-between; align-items: center;
  font-size: 7pt; letter-spacing: .08em; text-transform: uppercase; color: {MUTED} }}
.hdr .sec {{ display: flex; align-items: center; gap: 2mm; font-weight: 700; color: {BRAND} }}
.hdr .dot {{ width: 2.2mm; height: 2.2mm; border-radius: 50%; background: {BRAND} }}
.ftr {{ position: absolute; bottom: 5.5mm; left: 16mm; right: 16mm; display: flex; justify-content: space-between; font-size: 6.8pt; color: {MUTED} }}
.body {{ position: absolute; top: 14mm; bottom: 12mm; left: 16mm; right: 16mm; display: flex; flex-direction: column; gap: 4mm; overflow: hidden }}
h1 {{ font-size: 21pt; line-height: 1.12; margin: 0; letter-spacing: -.01em; font-weight: 700 }}
h2 {{ font-size: 11pt; margin: 0 0 1.6mm; font-weight: 700 }}
h3 {{ font-size: 8.6pt; margin: 0 0 1.2mm; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: {MUTED} }}
.sub {{ font-size: 10.5pt; color: {MUTED}; margin-top: 1.2mm }}
.row {{ display: flex; gap: 5mm }}
.col {{ display: flex; flex-direction: column; gap: 3.5mm; min-width: 0 }}
.g2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5mm }}
.g3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 4.5mm }}
.g4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm }}
.g6 {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 3mm }}
.card {{ border: 1px solid {LINE}; border-radius: 3mm; padding: 3.4mm 3.8mm; background: #fff; min-width: 0 }}
.card.soft {{ background: {SLATE_SOFT}; border-color: transparent }}
.card.brand {{ background: {BRAND_SOFT}; border-color: transparent }}
.card.teal {{ background: {TEAL_SOFT}; border-color: transparent }}
.card.amber {{ background: {AMBER_SOFT}; border-color: transparent }}
.card.red {{ background: {RED_SOFT}; border-color: transparent }}
.card.green {{ background: {GREEN_SOFT}; border-color: transparent }}
.tile {{ border-radius: 3mm; padding: 3mm 3.4mm; background: {SLATE_SOFT} }}
.tile .v {{ font-size: 15pt; font-weight: 700; line-height: 1.1; letter-spacing: -.01em }}
.tile .l {{ font-size: 7.6pt; color: {MUTED}; margin-top: .8mm }}
.tile .n {{ font-size: 7pt; color: {MUTED}; margin-top: .6mm }}
ul.pts {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1.7mm }}
ul.pts li {{ position: relative; padding-left: 4.2mm }}
ul.pts li::before {{ content: ''; position: absolute; left: 0; top: 1.6mm; width: 1.8mm; height: 1.8mm; border-radius: 50%; background: {BRAND} }}
ul.pts.sm {{ gap: 1mm; font-size: 8.3pt }}
ul.pts.sm li::before {{ top: 1.4mm; width: 1.4mm; height: 1.4mm }}
.ref {{ font-size: 6.4pt; color: {MUTED}; margin-left: 1mm; white-space: nowrap }}
.chip {{ display: inline-block; border-radius: 99px; padding: .25mm 2mm; font-size: 6.6pt; font-weight: 700; line-height: 1.5; white-space: nowrap; vertical-align: middle }}
.chip.ok {{ background: {GREEN_SOFT}; color: {GREEN} }}
.chip.warn {{ background: {AMBER_SOFT}; color: {AMBER} }}
.chip.bad {{ background: {RED_SOFT}; color: {RED} }}
.chip.mute {{ background: {SLATE_SOFT}; color: {MUTED} }}
.chip.brand {{ background: {BRAND_SOFT}; color: {BRAND} }}
table.t {{ width: 100%; border-collapse: collapse; font-size: 7.7pt; line-height: 1.3 }}
table.t th {{ text-align: left; background: {SLATE_SOFT}; color: #334155; font-weight: 700; padding: 1.3mm 2mm; font-size: 7.2pt }}
table.t td {{ padding: 1.2mm 2mm; border-top: 1px solid {LINE}; vertical-align: top }}
table.t.dense {{ font-size: 7pt }}
table.t.dense td {{ padding: .8mm 1.6mm }}
.note {{ font-size: 7pt; color: {MUTED} }}
.big {{ font-size: 36pt; font-weight: 700; letter-spacing: -.02em; line-height: 1 }}
.ic {{ flex: none; vertical-align: middle }}
.kv {{ display: grid; grid-template-columns: auto 1fr; gap: .8mm 3mm; font-size: 8.2pt }}
.kv b {{ color: {MUTED}; font-weight: 700 }}
.cols3 {{ column-count: 3; column-gap: 5mm; font-size: 7.6pt }}
.cols3 .blk {{ break-inside: avoid; margin-bottom: 2.6mm }}
.cols3 h3 {{ margin-top: 0 }}
.pill-row {{ display: flex; flex-wrap: wrap; gap: 1.4mm }}
.cover {{ background: #0b1020; color: #fff }}
.cover .hdr, .cover .ftr {{ color: #9aa3b8 }}
.cover .hdr .sec {{ color: #a5b4fc }} .cover .hdr .dot {{ background: #a5b4fc }}
svg text {{ font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif }}
"""


# ---------------------------------------------------------------- page scaffolding
class Doc:
    def __init__(self):
        self.pages = []  # (section, body_html, cls)

    def add(self, section, body, cls=""):
        self.pages.append((section, body, cls))
        return len(self.pages)

    def html(self):
        total = len(self.pages)
        out = []
        for i, (sec, body, cls) in enumerate(self.pages, 1):
            out.append(
                f'<section class="page {cls}"><div class="hdr"><div class="sec"><span class="dot"></span>{esc(sec)}</div>'
                f'<div>Zune &middot; Investor brief &middot; Draft {AS_OF}</div></div>'
                f'<div class="body">{body}</div>'
                f'<div class="ftr"><div>Confidential. Figures are labelled sourced / reported / estimate; see Evidence status.</div><div>{i} / {total}</div></div></section>'
            )
        return f'<!doctype html><html><head><meta charset="utf-8"><title>Zune investor brief</title><style>{CSS}</style></head><body>{"".join(out)}</body></html>'


def title_block(h, sub=None, right=""):
    s = f'<div class="sub">{esc(sub)}</div>' if sub else ""
    return f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:6mm"><div><h1>{esc(h)}</h1>{s}</div><div class="pill-row" style="flex:none;margin-top:1mm">{right}</div></div>'


def bullets(items, cls="", refs=True):
    lis = []
    for it in items:
        if isinstance(it, dict):
            t, r = it.get("text", ""), it.get("ref", "")
            lis.append(f'<li>{esc(t)}{f"<span class=ref>{esc(r)}</span>" if (r and refs) else ""}</li>')
        else:
            lis.append(f"<li>{it}</li>")
    return f'<ul class="pts {cls}">{"".join(lis)}</ul>'


def table(cols, rows, cls="", widths=None):
    th = "".join(f"<th>{esc(c)}</th>" for c in cols)
    trs = []
    for r in rows:
        tds = []
        for c in r:
            tds.append(f"<td>{c if isinstance(c, str) and c.startswith('<') else esc(c)}</td>")
        trs.append("<tr>" + "".join(tds) + "</tr>")
    cg = ""
    if widths:
        cg = "<colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>"
    return f'<table class="t {cls}">{cg}<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def tile(v, l, n="", basis=None):
    b = ""
    if basis and basis in BASIS:
        b = f' {chip(BASIS[basis][0], BASIS[basis][1])}'
    nn = f'<div class="n">{esc(n)}</div>' if n else ""
    return f'<div class="tile"><div class="v">{esc(v)}</div><div class="l">{esc(l)}{b}</div>{nn}</div>'


def card(inner, cls=""):
    return f'<div class="card {cls}">{inner}</div>'


# ---------------------------------------------------------------- SVG helpers
def svg(w, h, inner, style="width:100%;height:auto"):
    return f'<svg viewBox="0 0 {w} {h}" style="{style}" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'


def rbox(x, y, w, h, fill, stroke="none", r=8, sw=1.2, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def txt(x, y, s, size=12, fill=INK, weight="400", anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def mtxt(x, y, lines, size=12, fill=INK, weight="400", anchor="start", lh=1.25):
    out = []
    for i, ln in enumerate(lines):
        out.append(txt(x, y + i * size * lh, ln, size, fill, weight, anchor))
    return "".join(out)


def arrow(x1, y1, x2, y2, color=MUTED, sw=1.6, dash=""):
    d = f'stroke-dasharray="{dash}"' if dash else ""
    return (f'<defs><marker id="a{abs(hash((x1,y1,x2,y2,color)))%99999}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{color}"/></marker></defs>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" {d} marker-end="url(#a{abs(hash((x1,y1,x2,y2,color)))%99999})"/>')


# ---------------------------------------------------------------- content loading
def load_content():
    if os.path.exists(CONTENT):
        return json.load(open(CONTENT, encoding="utf-8"))
    return {"entries": [], "market": None}


def parse_decisions():
    rows = []
    txt_ = open(os.path.join(ROOT, "docs", "REQUIREMENTS.md"), encoding="utf-8").read()
    for m in re.finditer(r"^\| (D\d+) \| (.*) \| (\d{4}-\d{2}-\d{2}) \|\s*$", txt_, flags=re.M):
        rows.append((m.group(1), m.group(2), m.group(3)))
    rows.sort(key=lambda r: int(r[0][1:]))
    return rows


def md_inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"~~(.+?)~~", r"<s>\1</s>", s)
    return s


if __name__ == "__main__":
    from pages import build  # noqa: E402  (pages.py holds the page definitions)
    sys.exit(build(sys.modules[__name__]))
