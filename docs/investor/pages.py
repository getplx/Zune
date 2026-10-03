"""Page definitions for the investor brief. build(B) is called by build_pdf.py with the framework module."""
import os
import re
import subprocess
import json
import glob
import textwrap
import math

NODE_RENDER = None


# ----------------------------------------------------------------------------- shared bits
def phone_art(B, w=300, h=540):
    """Stylised phone: app grid + crossed-out browser/YouTube/cellular."""
    icons = [("chat", "#818cf8"), ("video", "#34d399"), ("walkie", "#f59e0b"), ("spark", "#f472b6"),
             ("play", "#60a5fa"), ("sun", "#fbbf24"), ("camera", "#a78bfa"), ("image", "#2dd4bf"),
             ("book", "#fb7185"), ("pencil", "#4ade80"), ("shield", "#93c5fd"), ("gear", "#cbd5e1")]
    cells = []
    for i, (ic, col) in enumerate(icons):
        r, c = divmod(i, 3)
        x, y = 34 + c * 80, 84 + r * 84
        cells.append(f'<rect x="{x}" y="{y}" width="64" height="64" rx="18" fill="{col}" opacity=".16"/>'
                     f'<g transform="translate({x+16},{y+16}) scale(1.35)" fill="none" stroke="{col}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{B.ICONS[ic]}</g>')
    inner = (
        B.rbox(4, 4, w - 8, h - 8, "#111a33", "#2a3556", 38, 3)
        + B.rbox(w / 2 - 38, 16, 76, 14, "#0b1020", "none", 7)
        + B.txt(w / 2, 62, "Zune", 17, "#e5e9f7", "700", "middle")
        + "".join(cells)
        + B.rbox(34, 430, 232, 40, "#1b2547", "none", 14)
        + B.txt(150, 455, "no browser · no YouTube · no SMS", 12, "#c7d0ee", "700", "middle")
        + B.rbox(34, 480, 232, 36, "#15203f", "none", 12)
        + B.txt(150, 503, "approved contacts only", 12, "#9fb0e6", "400", "middle")
    )
    return B.svg(w, h, inner, f"width:{w*0.7}px;height:auto")


def cover(B, ctx):
    left = f'''
<div class="col" style="flex:1;justify-content:center;gap:5mm">
  <div style="font-size:8.5pt;letter-spacing:.2em;text-transform:uppercase;color:#a5b4fc;font-weight:700">Investor brief &middot; Draft v1 &middot; {B.AS_OF}</div>
  <div class="big" style="font-size:64pt">Zune</div>
  <div style="font-size:11pt;color:#9aa3b8;margin-top:-3mm">working name (codename; trademark clearance pending)</div>
  <div style="font-size:19pt;line-height:1.22;font-weight:700;max-width:150mm">A kids-only Android.<br>No browser. No YouTube exit. No cellular calling.<br><span style="color:#a5b4fc">Safe by construction, not by policy.</span></div>
  <div style="font-size:10.5pt;color:#c7d0ee;max-width:150mm;line-height:1.45">A custom Android 17 OS image and a browser-based parent portal, flashed onto qualified Pixel phones. Text, voice and video only with parent-approved contacts, a kid-safe AI tutor, curated learning videos, weather lessons and more.</div>
  <div class="pill-row" style="margin-top:2mm">{B.chip("India first","brand")}{B.chip("English only","brand")}{B.chip("~200-user first phase","brand")}{B.chip("Software-led, Pixel first","brand")}{B.chip("Own hardware later","brand")}</div>
</div>
<div style="width:95mm;display:flex;align-items:center;justify-content:center">{phone_art(B)}</div>
'''
    return f'<div class="row" style="flex:1;height:100%">{left}</div>'


def exec_summary(B, ctx):
    n_reports, n_ver = ctx["n_reports"], ctx["n_verified"]
    tiles = "".join([
        B.tile("0", "browsers and routes to YouTube", "enforced in the OS image"),
        B.tile("Android 17", "AOSP android-17.0.0_r1", "released 2026-06-16"),
        B.tile("~200", "users in the first phase", "customer-owned Pixels, India"),
        B.tile("Pixel 10a/9a", "first supported phones", "re-locked with our own key"),
        B.tile("2 stages", "S1: everything exists, S2: better", "no dates promised yet"),
        B.tile(f"{n_reports}", "research reports written", f"{n_ver} through a skeptic pass"),
    ])
    win = B.bullets([
        "<b>Enforcement in the image, not an app.</b> No browser and no YouTube route exist on the device; the bootloader is re-locked so only our signed images boot.",
        "<b>Contact graph, not phone numbers.</b> 1:1 text, voice, video and walkie-talkie only with contacts both families approve; no groups, no strangers.",
        "<b>The moat is the whole product, not the lock.</b> Kid-only contact graph, AI tutor, curated learning content and portal. A no-browser Pixel is already sold by Pinwheel (US) and a $199 phone by Freckle.",
        "<b>Software-led model.</b> No hardware inventory; recurring revenue from cloud services (portal, AI, comms, content).",
        "<b>Timing.</b> Android 17 ships a native supervision framework; child-safety law is tightening worldwide.",
    ])
    kill = B.bullets([
        '<b>Google firmware licence</b> for commercially re-distributing Pixel firmware is unread and unresolved. '+B.chip("High","bad"),
        '<b>Security patching.</b> AOSP source drops twice a year; public fixes reach downstream months late (~127-day median seen). '+B.chip("High","bad"),
        "<b>India child-privacy law (DPDP s.9(3)).</b> Under-18 is a child; parent-visible monitoring has no clear exemption. Counsel first. "+B.chip("High","bad"),
        "<b>Re-lock support.</b> Only Pixel has vendor-documented custom-key re-lock; Snapdragon phones are unproven. "+B.chip("High","bad"),
        "<b>Willingness to pay in India.</b> ~Rs 1,250/month proposed vs JioShield at Rs 1,000/year; ~40,000 parents must be reached to sign ~200. "+B.chip("High","bad"),
        "<b>Killable dependencies.</b> YouTube must be optional (Videos work without it); the LLM vendor's approval for a child-facing product is gate one. "+B.chip("Med","warn"),
    ])
    body = f'''
{B.title_block("A phone where the unsafe things simply do not exist", "What we are building, why it can win, what could kill it")}
<div class="row" style="flex:1;min-height:0">
  <div class="col" style="flex:1.05">
    {B.card("<h2>What it is</h2><div style='font-size:9pt'>A custom <b>Android 17 (AOSP)</b> OS image for children plus a <b>parent web portal</b>. The child's phone has <b>no web browser, no route to YouTube, no cellular calls or SMS</b>. It has WhatsApp-style 1:1 messaging, voice and video calls with parent-approved contacts, a kid-safe AI assistant (text + images), curated learning videos, weather with lessons, walkie-talkie, camera, photos, journal, notebook and a book reader.<br><br>Sold as <b>software plus a flash-and-hand-over service</b> on the customer's own qualified phone. <b>Version 1:</b> we flash and re-lock the phone and hand it back (about 200 users, India, Pixel 10a/9a). Later: customer self-install, then <b>our own hardware</b>.</div>", "brand")}
    <div class="g3">{tiles}</div>
    {B.card("<h2>The bet</h2><div style='font-size:9.4pt'>Parents should not have to police a general-purpose phone. Remove the dangerous capabilities from the OS, and give parents a portal for everything that remains.</div>", "soft")}
  </div>
  <div class="col" style="flex:1">
    {B.card("<h2>Why it can win</h2>"+win)}
    {B.card("<h2>What could kill it</h2>"+kill+"<div class='note' style='margin-top:1.5mm'>Details, mitigations and evidence quality: Risk register and Evidence status pages.</div>", "red")}
  </div>
</div>'''
    return body


def problem_page(B, ctx):
    def col(title, sub, items, bad_good, accent, soft):
        li = "".join(f'<li style="display:flex;gap:2mm;align-items:flex-start;margin-bottom:1.3mm">{B.icon("check" if g else "x", 13, GOOD if g else BADC, 2.4)}<span>{B.esc(t)}</span></li>' for t, g in zip(items, bad_good))
        return (f'<div class="card" style="background:{soft};border-color:transparent;flex:1"><div style="font-weight:700;font-size:11pt;color:{accent}">{B.esc(title)}</div>'
                f'<div class="note" style="margin:1mm 0 2.5mm">{B.esc(sub)}</div><ul style="list-style:none;margin:0;padding:0;font-size:8.6pt">{li}</ul></div>')
    GOOD, BADC = B.GREEN, B.RED
    c1 = col("1. Screen-time and filter apps", "Family Link, Qustodio, Net Nanny, Bark app",
             ["Policy layer on an open phone", "Child can still reach a browser and YouTube", "Defeated by reset, safe mode, sideloading, other apps", "Parents police an adult-grade device"],
             [True, False, False, False], B.MUTED, B.SLATE_SOFT)
    c2 = col("2. Managed kids' phones", "Pinwheel, Bark Phone, Gabb, Troomi",
             ["Rebadged commodity phones plus managed software", "Browser-free by policy, not by image (our reading; to validate)", "Subscription $15-20/mo; devices $100-240 (secondary sources)", "Pinwheel does not install on your own phone"],
             [True, False, True, False], B.AMBER, B.AMBER_SOFT)
    c3 = col("3. Zune", "Capabilities are absent from the OS image",
             ["No browser or YouTube exit in the image; re-locked bootloader", "Contact graph both families approve; no strangers, no groups", "Parent portal in any browser; signed policy; offline-safe", "Software-led: customer brings the phone"],
             [True, True, True, True], B.BRAND, B.BRAND_SOFT)
    why = B.bullets([
        "<b>Android 17</b> adds a native supervision framework (SupervisionManager, ROLE_SUPERVISION) we can anchor on. <span class='ref'>R01 F6</span>",
        "<b>AI tutors</b> are now credible for children when wrapped in age policy, moderation and parent visibility. <span class='ref'>R07</span>",
        "<b>Regulation</b> is moving toward duty of care for minors (India DPDP; US and EU rules). <span class='ref'>R11, R19</span>",
        "<b>AOSP is open</b> and Pixel offers a documented route to custom images re-locked with our own key. <span class='ref'>R02</span>",
    ], "sm")
    Y = f'<span class="chip ok">enforces here</span>'
    N = f'<span class="chip mute">stock / not ours</span>'
    P = f'<span class="chip warn">policy only</span>'
    layers = B.table(["Layer", "Filter apps", "Managed kids' phones*", "Zune"], [
        ["<b>App</b> (filters, screen time)", Y, Y, Y],
        ["<b>Device policy</b> (MDM / supervision)", P, Y, Y],
        ["<b>OS image</b> (what exists on the phone)", N, N, Y],
        ["<b>Bootloader</b> (what can boot)", N, N, Y],
        ["<b>Updates</b> (who ships fixes)", N, N, Y],
    ], "", ["34%", "20%", "24%", "22%"])
    return f'''
{B.title_block("Every kids' phone today is policy on top of an open phone", "Where Zune sits, and why now")}
<div class="row" style="flex:none;align-items:stretch">{c1}{c2}{c3}</div>
<div class="row" style="flex:1;min-height:0"><div class="card" style="flex:1.2"><h3>Where enforcement lives</h3>{layers}<div class="note" style="margin-top:1.4mm">*Our reading of how managed kids' phones work (stock firmware plus managed-device software; R02 F9, inferred). To validate.</div></div><div class="card soft" style="flex:1">{"<h3>Why now</h3>"+why}</div></div>
<div class="note">Competitor facts come from secondary sources (R02 F9); the Market page validates and extends them.</div>'''


def product_page(B, ctx):
    items = [("chat", "Messenger", "1:1 text + emoji; approved contacts; no groups, no links", "#4f46e5"),
             ("phone", "Voice & video calls", "1:1 over the internet; approved only. Voice reuses the video stack (to confirm)", "#0d9488"),
             ("walkie", "Walkie-talkie", "Push-to-talk with approved contacts", "#b45309"),
             ("spark", "AI assistant", "Chat UI; text + image input; age policy; parent-visible", "#be185d"),
             ("play", "Learning videos", "Curated learning video; YouTube tier gated by compliance review", "#1d4ed8"),
             ("sun", "Weather", "Live forecast with 'why is it...?' lessons", "#a16207"),
             ("camera", "Camera", "Kid camera; no geotags", "#6d28d9"),
             ("image", "Photos", "Private by default; parent-shared", "#0f766e"),
             ("book", "Book reader", "EPUB; parent-approved library", "#be123c"),
             ("pencil", "Journal & notebook", "Private text, drawing, handwriting", "#15803d"),
             ("gear", "Settings (minimal)", "Wi-Fi and mobile data as standard; nothing else needed", "#475569"),
             ("shield", "Never on device", "Browser, YouTube, app store, cellular calls, SMS", "#b91c1c")]
    tiles = "".join(
        f'<div class="card" style="display:flex;gap:2.4mm;align-items:flex-start;padding:2.6mm 3mm"><div style="width:9mm;height:9mm;border-radius:2.6mm;background:{c}1f;display:flex;align-items:center;justify-content:center;flex:none">{B.icon(ic, 19, c, 1.8)}</div>'
        f'<div><div style="font-weight:700;font-size:9.3pt">{B.esc(t)}</div><div style="font-size:7.8pt;color:{B.MUTED};line-height:1.3">{B.esc(d)}</div></div></div>'
        for ic, t, d, c in items)
    parent = B.bullets([
        "Approve contacts (both families for cross-family)", "Read messages and AI chats; review calls metadata", "Set screen-time and quiet hours",
        "Control AI and learning-video settings", "Pair and manage devices (QR claim code)", "Remote lock; activity feed; approvals queue",
        "<i>Later:</i> parent-side voice and video calling"], "sm")
    return f'''
{B.title_block("One safe phone for a child, one portal for the parent", "Stage 1 scope: everything exists in its simplest form (D1-D21)")}
<div class="row" style="flex:1;min-height:0">
  <div class="col" style="flex:2.5;gap:4mm"><div class="g3" style="align-content:start">{tiles}</div>
  <div class="g2" style="flex:1;min-height:0">{B.card("<h3>Safety defaults</h3>"+B.bullets(["Every contact needs parent approval; cross-family contacts need both families", "No groups, links, attachments or discovery in messaging (Stage 1)", "No recording or covert listening on calls or walkie-talkie", "Stage 1 locations: parent-set places only"], "sm"), "soft")}{B.card("<h3>Stage 2: make it better</h3>"+B.bullets(["Richer content, games, sensors, climate stories", "Parent-side voice and video calling", "Customer self-install and more qualified devices", "More languages (Hindi and regional)"], "sm"), "soft")}</div></div>
  <div class="col" style="flex:1">{B.card("<h2>Parent portal (any browser)</h2>"+parent, "brand")}
  {B.card("<h3>Principles</h3>"+B.bullets(["English only; India first", "Parent-visible by design (age-appropriate disclosure to the child)", "Safe when the network is down (signed, cached policy)", "Nothing the child does can add an app or open the web"], "sm"), "soft")}</div>
</div>'''


def architecture_page(B, ctx):
    W, H = 1000, 540
    s = []
    s.append(B.txt(10, 22, "ON THE CHILD'S PHONE", 11, B.MUTED, "700"))
    s.append(B.txt(590, 22, "CLOUD", 11, B.MUTED, "700"))
    apps = ["Messenger", "Voice/video", "Walkie-talkie", "AI assistant", "Videos", "Weather", "Camera", "Photos", "Journal", "Notebook", "Reader", "Settings"]
    for i, a in enumerate(apps):
        r, c = divmod(i, 4)
        x, y = 10 + c * 108, 32 + r * 32
        s.append(B.rbox(x, y, 100, 26, B.BRAND_SOFT, "none", 6) + B.txt(x + 50, y + 17, a, 10.5, B.BRAND, "700", "middle"))
    s.append(B.rbox(10, 134, 428, 112, B.TEAL_SOFT, "none", 8))
    s.append(B.txt(20, 152, "ZUNE OS LAYER (our code)", 10, B.TEAL, "700"))
    boxes = [("ZuneGuardian", "supervision agent, signed policy, socket"), ("Launcher + SystemUI", "trimmed: 6 quick tiles, 3-item power menu"),
             ("ZuneSettings", "stock Settings kept default-deny"), ("Policy enforcement", "intents, network, installs, WebView scope")]
    for i, (t, sub) in enumerate(boxes):
        r, c = divmod(i, 2)
        x, y = 18 + c * 208, 160 + r * 40
        s.append(B.rbox(x, y, 202, 34, "#ffffff", B.TEAL, 6, 1) + B.txt(x + 8, y + 14, t, 10.5, B.INK, "700") + B.txt(x + 8, y + 27, sub, 8.6, B.MUTED))
    s.append(B.rbox(10, 256, 428, 52, B.SLATE_SOFT, "none", 8) + B.txt(20, 274, "AOSP ANDROID 17 BASE (pinned tag android-17.0.0_r1)", 10, B.MUTED, "700")
             + B.txt(20, 294, "Browser2 and HTMLViewer removed; under ~30 forked repos", 10, B.INK))
    s.append(B.rbox(10, 316, 428, 52, B.AMBER_SOFT, "none", 8) + B.txt(20, 334, "VERIFIED BOOT", 10, B.AMBER, "700")
             + B.txt(20, 354, "Bootloader re-locked with the Zune AVB key: only our images boot", 10, B.INK))
    s.append(B.rbox(10, 376, 428, 52, "#e2e8f0", "none", 8) + B.txt(20, 394, "HARDWARE + VENDOR FIRMWARE", 10, "#334155", "700")
             + B.txt(20, 414, "Pixel 10a / 9a (customer-supplied); Google firmware and radio as shipped", 10, B.INK))
    cloud = [("Parent portal (web)", "any browser; passkeys"), ("API gateway + auth + policy", "signed policy bundles"),
             ("Comms backbone", "Go/WebSocket chat; LiveKit video; Opus walkie"), ("AI gateway", "moderation, age policy -> LLM vendor"),
             ("Content service", "curated video list, weather bundle"), ("OTA + update server", "staged rollout, A/B rollback"),
             ("Signing", "offline HSM: per-model AVB keys; separate rotatable OTA key")]
    for i, (t, sub) in enumerate(cloud):
        r, c = divmod(i, 2)
        x, y = 590 + c * 205, 34 + r * 68
        wbox = 198 if i != 6 else 403
        s.append(B.rbox(x, y, wbox, 58, "#ffffff", B.BRAND, 8, 1.3) + B.txt(x + 10, y + 23, t, 11, B.INK, "700") + B.txt(x + 10, y + 42, sub, 9.5, B.MUTED))
    s.append(B.arrow(442, 190, 585, 190, B.BRAND, 2.2))
    s.append(B.arrow(585, 210, 442, 210, B.BRAND, 2.2))
    s.append(B.mtxt(514, 132, ["one persistent TLS", "socket (ZuneGuardian)", "signed policy;", "no Google push"], 9.5, B.BRAND, "700", "middle", 1.2))
    s.append(B.rbox(10, 444, 428, 84, "#ffffff", B.MUTED, 8, 1.2, 'stroke-dasharray="5 4"'))
    s.append(B.txt(20, 463, "FLASH STATION / INSTALLER (v1: ours; v2: customer)", 10, B.MUTED, "700"))
    for i, t in enumerate(["unlock", "flash", "re-lock", "attest", "hand over"]):
        x = 20 + i * 82
        s.append(B.rbox(x, 472, 74, 26, B.SLATE_SOFT, "none", 13) + B.txt(x + 37, 489, t, 10.5, B.INK, "700", "middle"))
    s.append(B.txt(20, 518, "WebUSB + fastboot; holds no secrets; pre-signed per-model bundles", 9.5, B.MUTED))
    s.append(B.arrow(224, 444, 224, 431, B.MUTED, 1.6, "4 3"))
    s.append(B.rbox(590, 440, 400, 88, B.BRAND_SOFT, "none", 8) + B.txt(602, 462, "Data and trust", 10.5, B.BRAND, "700")
             + B.mtxt(602, 480, ["Child data minimised; per-family envelope encryption.", "Policy is signed and cached: safe when offline.", "Stack: Kotlin/Compose apps; Go, Postgres, Redis; LiveKit."], 9.5, B.INK, "400", "start", 1.3))
    s.append(B.arrow(500, 330, 586, 300, B.MUTED, 1.4, "4 3"))
    s.append(B.txt(470, 350, "OTA updates (signed)", 9, B.MUTED, "400", "start"))
    return f'''
{B.title_block("How it fits together", "Phone, cloud and factory: three planes with one signed trust chain")}
<div style="flex:1;min-height:0;display:flex;align-items:center">{B.svg(W, H, "".join(s))}</div>
<div class="note">Source: reports R01, R03, R05, R09, R10, R13, R16, R18. Technology choices are recommendations, not yet built.</div>'''


def roadmap_page(B, ctx):
    phases = [("0", "Foundation", ["Pin android-17.0.0_r1", "Fork manifest; Cuttlefish baseline", "Build host: 32 vCPU, 128 GB, 1 TB", "Legal gates opened: Google firmware, Indian counsel"], B.BRAND),
              ("1", "Bring-up", ["Pixel 10a/9a vendor module (adevtool CI)", "Re-lock with our AVB key", "OTA from first device", "Key ceremony; offline signing"], B.TEAL),
              ("2", "Core OS", ["ZuneSettings; launcher; SystemUI trim", "ZuneGuardian + policy channel", "No-browser and no-YouTube audits", "Supervision overlay"], B.AMBER),
              ("3", "Apps + cloud", ["Comms: text, voice, video, walkie", "AI gateway; curated videos; weather", "Camera, photos, journal, notebook, reader", "Parent portal"], "#be185d"),
              ("4", "Staff pilot", ["Staff families on the flash station", "Security and privacy review gates", "Support playbook"], "#1d4ed8"),
              ("5", "First phase", ["~200 users, India, Pixel 10a/9a", "Staged intake with exit metrics", "Monthly patch pipeline live"], B.GREEN),
              ("6", "Scale-out", ["Customer installer (WebUSB)", "More qualified devices", "Stage 2 improvements"], "#475569"),
              ("7", "Own hardware", ["ODM RFQs after gates", "BIS / WPC as manufacturer", "Fused secure-boot keys"], "#111827")]
    s = []
    W, H = 1000, 300
    pw = 117
    for i, (n, t, its, col) in enumerate(phases):
        x = 4 + i * (pw + 8)
        s.append(f'<path d="M{x} 6 h{pw-14} l14 22 l-14 22 h-{pw-14} l14 -22 z" fill="{col}"/>' if i else f'<path d="M{x} 6 h{pw-14} l14 22 l-14 22 h-{pw-14} z" fill="{col}"/>')
        s.append(B.txt(x + (22 if i else 12), 34, f"{n}", 16, "#fff", "700") + B.txt(x + (40 if i else 30), 33, t, 10, "#fff", "700"))
        yy = 72
        for it in its:
            lines = textwrap.wrap(it, 20)
            for k, ln in enumerate(lines):
                s.append(B.txt(x + 4, yy + k * 13, ("• " if k == 0 else "  ") + ln, 10, B.INK))
            yy += len(lines) * 13 + 6
    s.append(B.rbox(4, 262, 5 * (pw + 8) - 12, 26, B.BRAND_SOFT, "none", 13) + B.txt(14, 280, "STAGE 1: make every feature exist, end to end, in its simplest form", 10.5, B.BRAND, "700"))
    s.append(B.rbox(5 * (pw + 8) - 4, 262, 3 * (pw + 8) + 4, 26, B.SLATE_SOFT, "none", 13) + B.txt(5 * (pw + 8) + 6, 280, "STAGE 2: make it better", 10.5, B.MUTED, "700"))
    gates = B.bullets([
        "<b>G0 Legal:</b> written answer or counsel opinion on Google firmware; Indian counsel on DPDP and OTT rules; no paid launch before it.",
        "<b>G1 Device:</b> re-lock verified on a sacrificial unit of every qualified model; OEM terms signed.",
        "<b>G2 Security:</b> monthly patch pipeline, key custody (offline HSM), OTA tested on real devices.",
        "<b>G3 Pilot exit:</b> install success, support load, child-safety incidents and bypass attempts within thresholds.",
    ], "sm")
    deps = B.bullets([
        "<b>Google:</b> Pixel firmware licence; partner security-patch access (unknown for a startup)",
        "<b>Indian counsel:</b> DPDP consent architecture; OTT messaging; handset rules",
        "<b>LLM vendor:</b> terms for products used by children; India availability",
        "<b>YouTube:</b> API compliance review for a closed, curated client",
        "<b>Hosting:</b> India-region cloud; LiveKit (self-host or cloud)",
    ], "sm")
    return f'''
{B.title_block("Roadmap: gates before dates", "Sequenced by dependency; durations come after staffing and funding decisions")}
<div style="flex:none">{B.svg(W, H, "".join(s))}</div>
<div class="g2" style="flex:1;min-height:0">{B.card("<h3>Gates</h3>"+gates, "soft")}{B.card("<h3>External dependencies</h3>"+deps, "soft")}</div>
<div class="note">No calendar dates are stated because no staffing or funding assumptions exist yet. Phases derive from reports R01, R02, R15, R16, R17, R18, R21.</div>'''


def entry_by_id(entries):
    return {e["id"]: e for e in entries}


def conf_chip(B, e):
    t, k = B.CONF.get(e.get("confidence", "unverified"), ("unverified", "bad"))
    return B.chip(t, k)


def short(t, n):
    t = (t or "").strip()
    if len(t) <= n:
        return t
    cut = t[:n]
    for sep in (". ", "; ", ", "):
        i = cut.rfind(sep)
        if i > n * 0.55:
            return cut[: i + 1].rstrip(",;") + (" …" if sep != ". " else "")
    return cut.rsplit(" ", 1)[0] + " …"


HEAD_OVERRIDE = {"R11": "Compliance: India law now governs the launch; the US map is a later-market reference"}


def topic_page(B, e, visual=None, nkp=5, nnum=3, ntab=1, nrisk=3, section=None):
    right = B.chip(e["id"], "brand") + conf_chip(B, e)
    pts = B.bullets(e.get("keyPoints", [])[:nkp])
    nums = "".join(B.tile(n["value"], n["label"], n.get("note", "")[:60], n.get("basis")) for n in e.get("numbers", [])[:nnum])
    tabs = ""
    for t in e.get("tables", [])[:ntab]:
        tabs += f'<div><h3>{B.esc(t["title"])}</h3>' + B.table(t["columns"], t["rows"][:7], "dense") + "</div>"
    right_col = visual if visual else tabs
    risks = "".join(
        f'<div class="card" style="padding:2.2mm 2.8mm"><div style="margin-bottom:.8mm">{B.chip(B.SEV[r["severity"]][0], B.SEV[r["severity"]][1])}</div><div style="font-size:7.8pt;font-weight:700;line-height:1.25">{B.esc(r["risk"])}</div><div style="font-size:7.2pt;color:{B.MUTED};margin-top:.8mm">{B.esc(r["mitigation"])}</div></div>'
        for r in e.get("risks", [])[:nrisk])
    sup = f'<div class="card amber" style="padding:2mm 3mm;font-size:7.6pt"><b>Superseded:</b> {B.esc(short(e["superseded"], 230))}</div>' if e.get("superseded") else ""
    stage = f'<div class="card soft" style="padding:2mm 3mm;font-size:7.8pt"><b>Stage 1:</b> {B.esc(short(e.get("stage1",""), 260))} <span class="note">Full scope: detail sheet.</span></div>'
    tiles = f'<div class="g3" style="grid-template-columns:repeat(3,1fr);gap:3mm">{nums}</div>' if nums else ""
    return f'''
{B.title_block(HEAD_OVERRIDE.get(e["id"], e["investorHeadline"]), e["title"], right)}
<div class="g2" style="flex:none"><div class="card brand" style="padding:2.6mm 3.4mm"><h3>Decision</h3><div style="font-size:8.8pt">{B.esc(e["decision"])}</div></div><div class="card teal" style="padding:2.6mm 3.4mm"><h3>Why it matters</h3><div style="font-size:8.8pt">{B.esc(e["whyItMatters"])}</div></div></div>
<div class="row" style="flex:1 1 auto"><div class="col" style="flex:1.1"><h3>Key points</h3>{pts}{tiles}</div><div class="col" style="flex:1">{right_col}</div></div>
{sup}
<div class="g3" style="flex:none">{risks}</div>
{stage}'''


def detail_sheet(B, e):
    right = B.chip(e["id"], "brand") + conf_chip(B, e)
    blocks = []
    blocks.append(f'<div class="blk"><h3>Decision</h3>{B.esc(e["decision"])}<div class="note" style="margin-top:1mm">{B.esc(e.get("confidenceNote",""))}</div></div>')
    blocks.append(f'<div class="blk"><h3>Why it matters</h3>{B.esc(e["whyItMatters"])}</div>')
    blocks.append(f'<div class="blk"><h3>Key points</h3>{B.bullets(e.get("keyPoints", []), "sm")}</div>')
    if e.get("numbers"):
        rows = [[n["label"], f'<b>{B.esc(n["value"])}</b>' + (f'<div class="note">{B.esc(n.get("note",""))}</div>' if n.get("note") else ""), B.chip(*B.BASIS.get(n["basis"], ("", "mute")))] for n in e["numbers"]]
        blocks.append(f'<div class="blk"><h3>Numbers</h3>{B.table(["Metric", "Value", "Basis"], rows, "dense", ["38%", "48%", "14%"])}</div>')
    for t in e.get("tables", []):
        nt = ("<div class='note'>" + B.esc(t.get("note", "")) + "</div>") if t.get("note") else ""
        blocks.append('<div class="blk"><h3>' + B.esc(t["title"]) + "</h3>" + B.table(t["columns"], t["rows"], "dense") + nt + "</div>")
    if e.get("risks"):
        rows = [[B.chip(B.SEV[r["severity"]][0], B.SEV[r["severity"]][1]), r["risk"], r["mitigation"]] for r in e["risks"]]
        blocks.append(f'<div class="blk"><h3>Risks</h3>{B.table(["Sev.", "Risk", "Mitigation"], rows, "dense", ["13%", "46%", "41%"])}</div>')
    st = f'<b>Stage 1:</b> {B.esc(e.get("stage1",""))}'
    if e.get("stage2"):
        st += "<div style='margin-top:1mm'><b>Stage 2:</b></div>" + B.bullets(e["stage2"], "sm")
    blocks.append(f'<div class="blk"><h3>Scope</h3>{st}</div>')
    if e.get("openItems"):
        blocks.append(f'<div class="blk"><h3>Open items</h3>{B.bullets(e["openItems"], "sm")}</div>')
    if e.get("flaggedClaims"):
        rows = [[c["claim"], c["why"]] for c in e["flaggedClaims"]]
        blocks.append(f'<div class="blk"><h3>Do not take as fact</h3>{B.table(["Claim", "Why"], rows, "dense", ["50%", "50%"])}</div>')
    if e.get("superseded"):
        blocks.append(f'<div class="blk"><div class="card amber" style="padding:2mm 3mm"><b>Superseded:</b> {B.esc(e["superseded"])}</div></div>')
    return f'''
{B.title_block(e["title"], "Detail sheet: " + e["investorHeadline"], right)}
<div class="flowwin"><div class="flowcols">{"".join(blocks)}</div></div>'''


# ----------------------------------------------------------------------------- custom pages that use extracted data
SHORT = {"R01": "AOSP base", "R02": "Hardware", "R03": "Minimal OS", "R04": "No-browser", "R05": "Parental controls", "R06": "Learning video",
         "R07": "AI assistant", "R08": "Walkie-talkie", "R09": "Core apps", "R10": "OTA + security", "R11": "Compliance", "R12": "Telephony (dropped)",
         "R13": "Messenger + video", "R14": "Weather", "R15": "Snapdragon", "R16": "Settings", "R17": "Selling the image", "R18": "Flash-and-deliver",
         "R19": "India regulation", "R20": "India market", "R21": "Own hardware"}


def num(E, rid, label_part):
    for n in E.get(rid, {}).get("numbers", []):
        if label_part.lower() in n["label"].lower():
            return n
    return None


def patch_page(B, ctx):
    E = ctx["E"]
    W, H = 1000, 262
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    x0, mw = 150, 70
    s = []
    for i, m in enumerate(months):
        x = x0 + i * mw
        s.append(f'<line x1="{x}" y1="20" x2="{x}" y2="236" stroke="{B.LINE}" stroke-width="1"/>' + B.txt(x + mw / 2, 14, m, 10, B.MUTED, "700", "middle"))
    s.append(f'<line x1="{x0+12*mw}" y1="20" x2="{x0+12*mw}" y2="236" stroke="{B.LINE}" stroke-width="1"/>')
    rows = [("AOSP source published", 52), ("Monthly security bulletins", 100), ("Fix authored -> public downstream", 150), ("Zune patch pipeline (target)", 206)]
    for t, y in rows:
        s.append(B.txt(6, y + 4, t, 10.5, B.INK, "700"))
    # row 1
    s.append(f'<circle cx="{x0+5*mw+0.5*mw}" cy="52" r="9" fill="{B.BRAND}"/>' + B.txt(x0 + 5.5 * mw, 78, "Android 17 (r1)", 9, B.BRAND, "700", "middle"))
    s.append(f'<circle cx="{x0+8.5*mw}" cy="52" r="8" fill="none" stroke="{B.MUTED}" stroke-width="2" stroke-dasharray="3 2"/>' + B.txt(x0 + 8.5 * mw, 78, "QPR1: not in AOSP", 9, B.MUTED, "400", "middle"))
    s.append(f'<circle cx="{x0+11.5*mw}" cy="52" r="9" fill="{B.AMBER}" opacity=".85"/>' + B.txt(x0 + 11.5 * mw, 78, "QPR2 (expected)", 9, B.AMBER, "700", "middle"))
    # row 2
    for i in range(12):
        s.append(f'<circle cx="{x0+i*mw+mw/2}" cy="100" r="4.5" fill="{B.TEAL}"/>')
    s.append(B.txt(x0 + 8.5 * mw, 124, "Sep: 180 vulnerabilities; half only via kernel/vendor", 9, B.TEAL, "700", "middle"))
    # row 3 lag bar
    s.append(B.rbox(x0 + 2 * mw + 6, 140, 5 * mw - 12, 20, B.AMBER_SOFT, B.AMBER, 10, 1) + B.txt(x0 + 4.5 * mw, 154, "fixes authored Mar-Jul", 10, B.AMBER, "700", "middle"))
    s.append(B.arrow(x0 + 7 * mw - 4, 150, x0 + 8.3 * mw, 150, B.RED, 2.4))
    s.append(B.rbox(x0 + 8.3 * mw, 140, 1.2 * mw, 20, B.RED_SOFT, B.RED, 10, 1) + B.txt(x0 + 8.9 * mw, 154, "public (Sep)", 10, B.RED, "700", "middle"))
    s.append(B.txt(x0 + 4.5 * mw, 178, "median lag about 127 days (range 65-178) for downstream non-partners [R01, sourced]", 9.5, B.RED, "700", "middle"))
    # row 4 target
    for i in range(12):
        s.append(B.rbox(x0 + i * mw + 14, 198, mw - 28, 16, B.GREEN_SOFT, B.GREEN, 8, 1))
    s.append(B.txt(x0 + 6 * mw, 232, "monthly OTA; target: Critical within 14 days of the bulletin, others within 30 [R01, estimate]", 9.5, B.GREEN, "700", "middle"))
    timeline = B.svg(W, H, "".join(s))
    tiles = "".join([
        B.tile("2 / year", "AOSP source drops (Q2, Q4)", "QPR1 (Sep) is not in AOSP; QPR2 expected ~Dec", "verified"),
        B.tile("~127 days", "median fix lag, author to downstream", "range 65-178; 49-commit batch, Sep 2026", "verified"),
        B.tile("14 / 30 days", "our patch SLA (critical / other)", "design target, not yet achievable", "estimate"),
        B.tile("1 FTE+", "platform/security engineer plus kernel support", "founder staffing decision", "estimate"),
    ])
    r01 = E.get("R01", {}).get("keyPoints", [])
    r10 = E.get("R10", {}).get("keyPoints", [])
    return f'''
{B.title_block("Security patching is the central business risk", "A child-safety product needs monthly fixes; public AOSP now ships twice a year")}
<div class="card" style="flex:none;padding:3mm">{timeline}</div>
<div class="row" style="flex:1;min-height:0">
  <div class="col" style="flex:1.7"><div class="g2"><div><h3>Why it is hard (R01)</h3>{B.bullets(r01[:5], "sm")}</div><div><h3>How we ship fixes (R10)</h3>{B.bullets(r10[:5], "sm")}</div></div></div>
  <div class="g2" style="flex:1;align-content:start">{tiles}</div>
</div>'''


def devices_page(B, ctx):
    E = ctx["E"]
    W, H = 470, 380
    s = []
    s.append(B.rbox(0, 0, 470, 52, B.SLATE_SOFT, "none", 10) + B.txt(235, 22, "Any phone", 12, B.INK, "700", "middle") + B.txt(235, 40, "Android devices that could run our image", 9.5, B.MUTED, "400", "middle"))
    flt = [("Re-lock with OUR key (v1 = we flash and lock)", 76), ("Unlockable and sold in the launch market", 126), ("Vendor-documented, community-proven", 176)]
    for t, y in flt:
        s.append(f'<path d="M20 {y} h430 l-30 36 h-370 z" fill="{B.BRAND_SOFT}" stroke="{B.BRAND}" stroke-width="1.2"/>' + B.txt(235, y + 23, t, 10.5, B.BRAND, "700", "middle"))
    s.append(B.arrow(235, 52, 235, 74, B.MUTED) + B.arrow(235, 112, 235, 124, B.MUTED) + B.arrow(235, 162, 235, 174, B.MUTED) + B.arrow(235, 212, 235, 236, B.MUTED))
    s.append(B.rbox(0, 240, 470, 56, B.GREEN_SOFT, B.GREEN, 10, 1.3) + B.txt(235, 262, "QUALIFIED NOW", 9.5, B.GREEN, "700", "middle") + B.txt(235, 282, "Pixel 10a / 9a (Tensor, zumapro): documented custom-key re-lock", 11, B.INK, "700", "middle"))
    s.append(B.rbox(0, 304, 230, 70, B.AMBER_SOFT, B.AMBER, 10, 1.2) + B.txt(115, 322, "CANDIDATES (need a relock test)", 9, B.AMBER, "700", "middle")
             + B.mtxt(115, 340, ["Fairphone Gen 6+", "Nothing Phone (3)", "Motorola Signature 27"], 10, B.INK, "700", "middle", 1.25))
    s.append(B.rbox(240, 304, 230, 70, B.RED_SOFT, B.RED, 10, 1.2) + B.txt(355, 322, "REJECTED (relock / region)", 9, B.RED, "700", "middle")
             + B.mtxt(355, 340, ["OnePlus 13/15, Galaxy S26", "Xiaomi / Honor / Oppo / Vivo", "Xperia 1 VII (US)"], 10, B.INK, "700", "middle", 1.25))
    funnel = B.svg(W, H, "".join(s))
    t15 = next((t for t in E.get("R15", {}).get("tables", []) if "Candidate" in t["title"]), None)
    rows = [[c[:46] for c in r[:5:1]] for r in (t15["rows"] if t15 else [])]
    tbl = B.table(["Device", "SoC / RAM", "US price", "Relock evidence", "Verdict"], rows[:8], "dense", ["19%", "17%", "11%", "27%", "26%"]) if rows else ""
    dsc = next((t for t in E.get("R02", {}).get("tables", []) if "Support Contract" in t["title"]), None)
    dsc_html = B.table(dsc["columns"], dsc["rows"][:6], "dense", ["14%", "86%"]) if dsc else ""
    return f'''
{B.title_block("Start on the one phone that can be re-locked with our own key", "Device strategy: Pixel 10a/9a now; Snapdragon and own hardware later")}
<div class="row" style="flex:1;min-height:0">
  <div class="card" style="flex:0 0 118mm">{funnel}</div>
  <div class="col" style="flex:1"><h3>Candidates considered (R15; US prices; India availability in R20)</h3>{tbl}<h3 style="margin-top:1mm">Device Support Contract (R02)</h3>{dsc_html}<div class="note">Relock evidence for non-Pixel phones is user reports only. Tamper strength on Snapdragon is also bounded by OEM bootloader exploits and leaked programmers (R15).</div></div>
</div>'''


def delivery_page(B, ctx):
    E = ctx["E"]
    steps = [("1", "Contact", "web form; parent in any browser"), ("2", "Eligibility gate", "model/SKU, GST invoice + serial, carrier or account lock, firmware, battery"),
             ("3", "Intake", "drop-off or insured courier; new-in-box preferred; erase consent"), ("4", "Flash station", "unlock, flash, re-lock, attest, QA (~10 min + 2 button presses)"),
             ("5", "Hand-over", "unenrolled; parent QR enrolment; 10-minute onboarding"), ("6", "Ongoing", "OTA, support, parent-authorised service-unlock / return to stock")]
    W, H = 1000, 112
    s = []
    cw = 160
    for i, (n, t, d) in enumerate(steps):
        x = 4 + i * (cw + 8)
        col = [B.BRAND, B.TEAL, B.AMBER, "#be185d", B.GREEN, "#475569"][i]
        s.append(f'<path d="M{x} 4 h{cw-14} l14 22 l-14 22 h-{cw-14} {"l14 -22 z" if i else "z"}" fill="{col}"/>' + B.txt(x + (22 if i else 12), 33, n, 15, "#fff", "700") + B.txt(x + (42 if i else 32), 32, t, 11, "#fff", "700"))
        for k, ln in enumerate(__import__("textwrap").wrap(d, 25)):
            s.append(B.txt(x + 4, 72 + k * 13, ln, 10, B.INK))
    flow = B.svg(W, H, "".join(s))
    r18 = E.get("R18", {})
    r17 = E.get("R17", {})
    nums = "".join(B.tile(n["value"], n["label"], n.get("note", "")[:70], n.get("basis")) for n in (r18.get("numbers", [])[:6]))
    return f'''
{B.title_block("v1 delivery: we flash and hand back the customer's own phone", "Software-led: no inventory, no hardware sales (D15, D16); customer self-install comes later")}
<div class="card" style="flex:none;padding:3mm">{flow}</div>
<div class="row" style="flex:1;min-height:0">
  <div class="col" style="flex:1.3"><h3>What makes it work (R18)</h3>{B.bullets(r18.get("keyPoints", [])[:6], "sm")}<h3 style="margin-top:2mm">Selling the image (R17)</h3>{B.bullets(r17.get("keyPoints", [])[:4], "sm")}</div>
  <div class="g2" style="flex:1;align-content:start">{nums}</div>
</div>'''


def funnel_svg(B):
    W, H = 560, 250
    rows = [("Pixels sold in India, 2023 to Sep 2026", "~1.6M", 1.6e6, "estimate: 1.2-2.2M", B.BRAND),
            ("Still in use", "~1.2M", 1.2e6, "assume 75% of units", B.BRAND),
            ("Household with a child aged 8-14", "~300k", 3.0e5, "assume 25% (unsourced)", B.TEAL),
            ("Wants this device at this price", "~6,000", 6.0e3, "assume 2% (a guess; range 0.8k-26k)", B.AMBER),
            ("Parents to REACH to sign 200", "~40,000", 4.0e4, "assume 0.5% convert; 0.1% is impossible", B.RED)]
    out = []
    lo, hi = math.log10(2e3), math.log10(2.2e6)
    for i, (lab, val, n, note, col) in enumerate(rows):
        y = 10 + i * 46
        w = 40 + (math.log10(n) - lo) / (hi - lo) * 330
        out.append(B.txt(0, y + 12, lab, 10.5, B.INK, "700"))
        out.append(B.rbox(0, y + 18, w, 16, col, "none", 4))
        out.append(B.txt(w + 8, y + 31, val, 12, col, "700"))
        out.append(B.txt(w + 8 + len(val) * 7.4 + 8, y + 31, note, 9, B.MUTED))
    return B.svg(W, H, "".join(out))


def market_pages(B, ctx, doc):
    m = ctx.get("market")
    if not m:
        doc.add("Market", B.title_block("Market and competition", "Research in progress") + B.card("<h3>Pending</h3>Market-sizing research has not returned yet.", "amber"))
        return
    sz = m.get("marketSizing", [])
    pick = [2, 4, 6, 18, 26, 28, 30, 35, 37, 38, 39]
    rows = []
    for i in pick:
        if i < len(sz):
            x = sz[i]
            rows.append([x["metric"], "<b>" + B.esc(short(x["value"], 74)) + "</b>", short(x["source"], 34), B.chip(*B.BASIS.get(x["basis"], ("", "mute")))])
    mt = B.table(["Metric", "Value", "Source", "Basis"], rows, "dense", ["28%", "42%", "20%", "10%"])
    tiles = "".join([
        B.tile("~168M", "children aged 8-14 in India (Zune core band)", "estimate from age bands", "estimate"),
        B.tile("22%", "of India's 2025 phone units cost over INR 30k", "Counterpoint; Pixel was ~2% of >INR 45k", "reported"),
        B.tile("~0.43M", "Pixels sold in India per year (2025)", "no published figure; analyst-share arithmetic", "estimate"),
        B.tile("$1.6-2.8B", "global parental-control software, 2025", "analyst range; not investor-grade", "reported"),
    ])
    fun_note = B.bullets([
        "<b>Path A (owner already has a Pixel):</b> ~200 is possible only through targeted outreach; the pool is thousands nationally, not hundreds of thousands.",
        "<b>Path B (parent buys a Pixel for the child):</b> year-1 cost about Rs 59-71k (~$610-730) against Rs 1,000/yr JioShield or free Family Link.",
        "<b>Bottom line:</b> the binding constraint is willingness to pay ~Rs 1,250/month, not Pixel supply. Treat the 200-user phase as a test of price.",
    ], "sm")
    doc.add("Market", f'''
{B.title_block("Market: heavy parental concern, a thin paying niche", "Honest sizing; analyst market-size numbers are not investor-grade, so we show the funnel instead")}
<div class="row" style="flex:1;min-height:0">
  <div class="col" style="flex:1.05"><div class="card"><h3>Finding ~200 families (R20 + market research; every step labelled)</h3>{funnel_svg(B)}</div>{B.card(fun_note, "amber")}</div>
  <div class="col" style="flex:1"><div class="g2">{tiles}</div><h3>Selected sizing and anchors</h3>{mt}</div>
</div>''')
    comp = m.get("competitors", [])
    crow = [[f"<b>{B.esc(c['name'])}</b>", short(c.get("geography", ""), 22), short(c.get("price", ""), 70), short(c.get("funding", "") or "n/a", 46), short(c.get("weakness", ""), 118)] for c in comp[:13]]
    ct = B.table(["Competitor", "Where", "Price", "Funding", "Gap vs Zune"], crow, "dense", ["16%", "9%", "27%", "17%", "31%"])
    tw = B.bullets([f"<b>{B.esc(short(t['item'], 52))}.</b> {B.esc(short(t['detail'], 120))}" for t in m.get("tailwinds", [])[:7]], "sm")
    ins = B.bullets([
        "<b>Not a moat:</b> Pinwheel already sells Pixel 9a phones with a no-browser OS at $599 + $14.99/mo; Freckle (1 Oct 2026) sells a $199 no-browser phone. The moat must be communication graph, AI tutor, learning content and portal.",
        "<b>Price anchor:</b> JioShield launched 26-29 Sep 2026 at Rs 1,000/year; Zune's unvalidated ~Rs 1,250/month is ~15x that.",
        "<b>Cold start:</b> Zune kids only talk to approved Zune contacts; Indian children use WhatsApp, so recruit in school or parent clusters.",
        "<b>Capital:</b> Pinwheel raised ~$6.4M in total; Qustodio's consumer ARR is ~$21M after ~15 years.",
    ], "sm")
    doc.add("Market", f'''
{B.title_block("Competition: the concept is validated, the lock is copyable", "Closest analogues, substitutes and tailwinds (prices from company pages where available; many from reviewers)")}
<div class="row" style="flex:1;min-height:0">
  <div class="col" style="flex:1.55"><h3>Competitors and substitutes</h3>{ct}</div>
  <div class="col" style="flex:1">{B.card("<h3>What it means for Zune</h3>"+ins, "brand")}{B.card("<h3>Tailwinds</h3>"+tw, "soft")}</div>
</div>
<div class="note">Source: market research agent (sources named per figure in the data file); unverified items listed in Evidence status. {len(m.get("gaps", []))} research gaps recorded.</div>''')


def risk_pages(B, ctx, doc):
    E = ctx["E"]
    allr, top = [], []
    for rid in sorted(E):
        if E[rid].get("confidence") == "superseded" and rid in ("R12",):
            continue
        rs = E[rid].get("risks", [])
        for r in rs:
            allr.append((rid, r))
        hs = [r for r in rs if r["severity"] == "H"]
        for r in hs[:1]:
            top.append((rid, r))
    counts = {}
    for rid, r in allr:
        counts.setdefault(rid, {"H": 0, "M": 0, "L": 0})[r["severity"]] += 1
    bars = []
    for rid in sorted(counts):
        c = counts[rid]
        bars.append(f'<div style="display:flex;align-items:center;gap:1.6mm;font-size:7.3pt;white-space:nowrap"><span style="width:7mm;font-weight:700">{rid}</span><span style="width:27mm;color:{B.MUTED}">{SHORT.get(rid, "")}</span>'
                    + "".join(f'<span style="display:inline-block;height:3mm;width:{c[k]*3.6}mm;background:{col};border-radius:.8mm"></span>' for k, col in (("H", B.RED), ("M", "#f59e0b"), ("L", "#22c55e")) if c[k])
                    + f'<span style="color:{B.MUTED}">{c["H"]}/{c["M"]}/{c["L"]}</span></div>')
    per = 10
    chunks = [top[i:i + per] for i in range(0, len(top), per)] or [[]]
    nh = sum(1 for _, r in allr if r["severity"] == "H")
    for k, ch in enumerate(chunks):
        rows = [[f'<b>{rid}</b>', SHORT.get(rid, rid), r["risk"], r["mitigation"]] for rid, r in ch]
        side = ""
        if k == 0:
            side = f'<div class="card" style="flex:0 0 74mm;align-self:flex-start"><h3>Risk concentration</h3><div style="display:flex;flex-direction:column;gap:1.1mm">{"".join(bars)}</div><div class="note" style="margin-top:2mm"><span style="color:{B.RED}">&#9632;</span> High &nbsp;<span style="color:#f59e0b">&#9632;</span> Medium &nbsp;<span style="color:#22c55e">&#9632;</span> Low &nbsp;(counts: H/M/L)</div></div>'
        body = (B.title_block("Risk register" + (" (continued)" if k else ": the top risks"), f"Top high-severity risks per topic; all {len(allr)} risks ({nh} high) are on the detail sheets")
                + f'<div class="row" style="flex:1;min-height:0">{side}<div style="flex:1;min-width:0">{B.table(["Src", "Topic", "Risk", "Mitigation"], rows, "", ["6%", "13%", "45%", "36%"])}</div></div>')
        doc.add("Risks", body)


def evidence_page(B, ctx):
    E = ctx["E"]
    cnt = {}
    for e in E.values():
        cnt[e["confidence"]] = cnt.get(e["confidence"], 0) + 1
    tiles = "".join(B.tile(str(cnt.get(k, 0)), B.CONF[k][0]) for k in ("verified", "partly-verified", "unverified", "superseded"))
    rows = []
    for rid in sorted(E):
        e = E[rid]
        t, k = B.CONF[e["confidence"]]
        rows.append([f"<b>{rid}</b>", SHORT.get(rid, rid), B.chip(t, k), short(e.get("confidenceNote", ""), 130), str(len(e.get("flaggedClaims", [])))])
    half = (len(rows) + 1) // 2
    return f'''
{B.title_block("What is verified, and what is not", "Every report went through research; skeptic passes re-check the load-bearing claims. Do not take flagged claims as fact.")}
<div class="row" style="flex:none;gap:4mm"><div class="g4" style="flex:1">{tiles}</div><div class="card soft" style="flex:2;font-size:8pt"><b>How to read this.</b> Evidence came from GrapheneOS and LineageOS source on GitHub plus web search: Google's own AOSP tree, Google licence pages and most Indian legal texts were unreachable from the research environment. A follow-up session with AOSP access will re-verify. Skeptic passes for several reports are still to be re-run.</div></div>
<div class="g2" style="flex:1;min-height:0;align-items:start"><div>{B.table(["Src", "Report", "Status", "Note", "Flags"], rows[:half], "dense", ["7%", "26%", "12%", "47%", "8%"])}</div><div>{B.table(["Src", "Report", "Status", "Note", "Flags"], rows[half:], "dense", ["7%", "26%", "12%", "47%", "8%"])}</div></div>'''


def asks_page(B, ctx):
    items = [
        ("Legal", "Written answer or counsel opinion on Google's licence to redistribute Pixel firmware commercially", "Blocks any paid launch", "Counsel + Google outreach"),
        ("Legal", "Indian counsel: DPDP s.9(3) monitoring, messenger classification, parent access vs interception law", "Gate before any external family", "Indian counsel; Indian private limited"),
        ("Product", "Target age range of children (assumed ~6-13; India treats under-18 as a child)", "Drives safety design, AI, content", "Founder"),
        ("Product", "Emergency calling: keep a 112-only path? (default yes; to field-test on data-only SIMs)", "Safety + regulatory", "Founder + counsel"),
        ("Security", "Fund monthly patching: about 1 platform/security engineer plus kernel support; seek partner access", "Central business risk", "Founder / hiring"),
        ("Security", "WebView supply: Vanadium prebuilt vs own Chromium build, with a Chromium-cadence update SLA", "Largest attack surface", "Tech lead"),
        ("Content", "Videos vs decisions D2/D3: research recommends a licensed offline base plus an optional made-for-kids-only YouTube tier behind a kill switch (ask YouTube in writing; drop at 8 weeks if refused)", "Conflicts with a YouTube-only curation promise", "Founder + legal"),
        ("Commercial", "Price: test INR price on a waitlist; ~Rs 1,250/month is ~15x JioShield (Rs 1,000/yr); first phase invite-only and free until Indian payments are ready", "Willingness to pay is the binding constraint", "Founder"),
        ("AI", "Obtain the LLM vendor's written approval for a child-facing product; India-region inference", "Gate one for the assistant", "Founder"),
        ("Commercial", "Pricing: invite-only and free first phase until Indian payments are ready; test INR price on a waitlist", "Unit economics unvalidated", "Founder"),
        ("Operations", "First city (Bengaluru proposed), staff the flash station, spare-phone reserve (4-6) as an exception to no inventory", "Pilot logistics", "Founder"),
        ("Hardware", "Own-hardware gates H1-H4; paper RFQs under NDA; key custody in an HSM; promise 3 years of patches", "Later phase", "Founder"),
        ("Brand", "Name clearance: 'Zune' is a codename with Microsoft trademark history", "Before any public use", "Founder + counsel"),
    ]
    rows = [[B.chip(a, "brand"), B.esc(b), B.esc(c), B.esc(d)] for a, b, c, d in items]
    return f'''
{B.title_block("Decisions and help we need", "The open items that change the plan most; each has a recommended default in the research")}
{B.table(["Area", "Decision / ask", "Why it matters", "Owner"], rows, "", ["10%", "50%", "22%", "18%"])}'''


def founder_page(B, ctx):
    box = lambda t, ph: f'<div class="card" style="flex:1;border-style:dashed"><h2>{t}</h2><div style="color:{B.MUTED};font-size:8.6pt">{ph}</div></div>'
    return f'''
{B.title_block("To be completed by the founder", "Facts the research cannot supply. Nothing on this page is estimated.")}
<div class="g2" style="flex:1;min-height:0">
{box("Team and roles", "Founder background; who owns platform/security, backend, apps, ops; key hires needed (security engineer + kernel support is in the plan).")}
{box("Traction and validation", "Waitlist size, parent interviews, pilot commitments, partners, letters of intent.")}
{box("Funding ask and use of funds", "Round size and terms. Cost categories supported by the research: build infrastructure (about $10-18k one-time, $0.5-0.9k/month, estimate), legal (Indian counsel, Google), device lab, flash station, cloud (AI, comms), security staffing.")}
{box("Financial model", "Revenue, margin and runway. The research gives unvalidated pricing and unit-cost inputs only; a model should be built after pricing is tested on a waitlist.")}
</div>'''


def economics_page(B, ctx):
    E = ctx["E"]
    kws = ["price", "cost", "$", "inr", "/month", "per month", "breakeven", "margin", "fee", "subscription", "activation", "payback"]
    rows = []
    seen = set()
    for rid in ["R17", "R18", "R20", "R21", "R07", "R13", "R14", "R10", "R02"]:
        for n in E.get(rid, {}).get("numbers", []):
            text = (n["label"] + " " + n["value"]).lower()
            if any(k in text for k in kws) and (rid, n["label"]) not in seen:
                seen.add((rid, n["label"]))
                rows.append([f"<b>{rid}</b>", B.esc(n["label"])[:60], f'<b>{B.esc(n["value"])[:60]}</b>', B.chip(*B.BASIS.get(n["basis"], ("", "mute"))), B.esc(n.get("note", ""))[:70]])
    half = (len(rows) + 1) // 2
    cols = ["Src", "Figure", "Value", "Basis", "Note"]
    wd = ["6%", "27%", "27%", "10%", "30%"]
    return f'''
{B.title_block("Unit economics: inputs, not a forecast", "Prices and costs from the reports; most are estimates and none is validated with customers")}
<div class="g2" style="flex:1;min-height:0;align-items:start"><div>{B.table(cols, rows[:half], "dense", wd)}</div><div>{B.table(cols, rows[half:], "dense", wd)}</div></div>
<div class="card amber" style="flex:none;font-size:8pt"><b>Read with care.</b> The report skeptics flagged that the proposed price and cost figures conflict in places (cloud cost per child can erase subscription margin; US-dollar and rupee plans differ; public-funnel pricing conflicts with the invite-only, free first phase proposed on legal grounds). A financial model should follow a priced waitlist test.</div>'''


# ----------------------------------------------------------------------------- appendices
def decisions_pages(B, doc):
    rows = B.parse_decisions()
    trs = [[f"<b>{d}</b>", "<span>" + B.md_inline(t) + "</span>", dt] for d, t, dt in rows]
    body = (B.title_block("Decision log", "Dated founder decisions; later decisions supersede earlier ones. Canonical source: docs/REQUIREMENTS.md")
            + B.table(["#", "Decision", "Date"], trs, "", ["5%", "87%", "8%"]))
    doc.add("Appendix A. Decisions", body)


def glossary_page(B):
    g = [("AOSP", "Android Open Source Project: Google's open base of Android"), ("AVB", "Android Verified Boot; a custom key lets the bootloader trust only our images"),
         ("Re-lock", "Locking the bootloader again after flashing, so nothing else can be installed"), ("A/B + OTA", "Dual-slot system with over-the-air updates and rollback"),
         ("adevtool", "GrapheneOS tool that builds Pixel vendor modules from Google's stock images"), ("Cuttlefish", "Google's virtual Android device, used for hardware-free testing"),
         ("SPL", "Security patch level, e.g. 2026-06-05"), ("GKI", "Generic Kernel Image: Google's common Android kernel"),
         ("Mainline / APEX", "Updatable system modules; with no Google Play they update only through our OTA"), ("WebView", "System web renderer that apps embed; a browsing risk we must contain"),
         ("Supervision framework", "Android 17 SupervisionManager / ROLE_SUPERVISION for parental controls"), ("FGS", "Foreground service: Android's rule for background audio, camera and mic"),
         ("LiveKit / SFU", "Open-source real-time media server for voice, video and push-to-talk"), ("DSC", "Device Support Contract: our checklist a phone must pass to be qualified"),
         ("DPDP Act", "India's Digital Personal Data Protection Act 2023 (child = under 18)"), ("COPPA", "US children's privacy law (under 13)"),
         ("BIS / WPC", "Indian product-registration and radio-approval regimes"), ("IMD", "India Meteorological Department"),
         ("WEA", "US Wireless Emergency Alerts; India uses cell-broadcast alerts"), ("GMS", "Google Mobile Services (Play, FCM...): not used in Zune")]
    rows = [[f"<b>{B.esc(a)}</b>", b] for a, b in g]
    half = (len(rows) + 1) // 2
    body = (B.title_block("Glossary", "Terms an Android and infrastructure reader will want pinned down")
            + f'<div class="g2">{B.table(["Term", "Meaning"], rows[:half], "", ["28%", "72%"])}{B.table(["Term", "Meaning"], rows[half:], "", ["28%", "72%"])}</div>')
    return body


# ----------------------------------------------------------------------------- build
def build(B):
    data = B.load_content()
    entries = data.get("entries", [])
    E = entry_by_id(entries)
    reports = sorted(glob.glob(os.path.join(B.ROOT, "docs", "research", "[0-9][0-9]-*.md")))
    n_ver = sum(1 for p in reports if "Verification (second pass)" in open(p, encoding="utf-8").read())
    ctx = {"n_reports": len(reports), "n_verified": n_ver, "E": E, "market": data.get("market")}
    doc = B.Doc()
    doc.add("Cover", cover(B, ctx), "cover")
    doc.add("Summary", exec_summary(B, ctx))
    doc.add("Problem", problem_page(B, ctx))
    market_pages(B, ctx, doc)
    doc.add("Product", product_page(B, ctx))
    doc.add("Architecture", architecture_page(B, ctx))
    story = [("No browser", "R04"), ("Parental controls", "R05"), ("Communication", "R13"), ("Communication", "R08"),
             ("AI assistant", "R07"), ("Learning video", "R06"), ("Weather", "R14"), ("Core apps", "R09"), ("Settings", "R16"),
             ("Base OS", "R01"), ("Base OS", "R03")]
    for sec, rid in story:
        if rid in E:
            doc.add(sec, topic_page(B, E[rid]))
    doc.add("Security and updates", patch_page(B, ctx))
    if "R10" in E:
        doc.add("Security and updates", topic_page(B, E["R10"]))
    doc.add("Devices", devices_page(B, ctx))
    doc.add("Delivery", delivery_page(B, ctx))
    for sec, rid in [("Delivery", "R17"), ("India", "R19"), ("India", "R20"), ("Compliance", "R11"), ("Own hardware", "R21")]:
        if rid in E:
            doc.add(sec, topic_page(B, E[rid]))
    doc.add("Economics", economics_page(B, ctx))
    doc.add("Roadmap", roadmap_page(B, ctx))
    risk_pages(B, ctx, doc)
    doc.add("Evidence", evidence_page(B, ctx))
    doc.add("Asks", asks_page(B, ctx))
    doc.add("Founder", founder_page(B, ctx))
    decisions_pages(B, doc)
    for rid in sorted(E):
        doc.add("Appendix B. Detail sheets", detail_sheet(B, E[rid]))
    doc.add("Appendix C. Glossary", glossary_page(B))
    html_path = os.path.join(B.INV, "brief.html")
    pdf_path = os.path.join(B.INV, "Zune-Investor-Brief.pdf")
    open(html_path, "w", encoding="utf-8").write(doc.html())
    r = subprocess.run(["node", os.path.join(B.INV, "render.js"), html_path, pdf_path], capture_output=True, text=True, cwd=B.INV)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode
