"""Page definitions for the investor brief. build(B) is called by build_pdf.py with the framework module."""
import os
import re
import subprocess
import json
import glob
import textwrap

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
        "<b>One product, not ten apps.</b> AI tutor, curated learning videos, weather lessons, camera, journal, book reader, parent portal.",
        "<b>Software-led model.</b> No hardware inventory; recurring revenue from cloud services (portal, AI, comms, content).",
        "<b>Timing.</b> Android 17 ships a native supervision framework; child-safety law is tightening worldwide.",
    ])
    kill = B.bullets([
        '<b>Google firmware licence</b> for commercially re-distributing Pixel firmware is unread and unresolved. '+B.chip("High","bad"),
        '<b>Security patching.</b> AOSP source drops twice a year; public fixes reach downstream months late (~125-day median seen). '+B.chip("High","bad"),
        '<b>Re-lock support.</b> Only Pixel has vendor-documented custom-key re-lock; Snapdragon phones are unproven. '+B.chip("High","bad"),
        "<b>India child-privacy law (DPDP).</b> Under-18 is a child; a parental-monitoring product needs legal confirmation. "+B.chip("High","bad"),
        "<b>Addressable base.</b> Qualified Pixels are scarce and costly in India (see Market). "+B.chip("Med","warn"),
        "<b>YouTube API terms</b> for topic-driven curation inside a closed client. "+B.chip("Med","warn"),
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
             ("phone", "Voice & video calls", "1:1 over the internet; approved contacts only", "#0d9488"),
             ("walkie", "Walkie-talkie", "Push-to-talk with approved contacts", "#b45309"),
             ("spark", "AI assistant", "Chat UI; text + image input; age policy; parent-visible", "#be185d"),
             ("play", "Learning videos", "Curated YouTube embeds, only inside Zune", "#1d4ed8"),
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
             ("Comms backbone", "messaging + LiveKit: voice, video, walkie"), ("AI gateway", "moderation, age policy -> LLM vendor"),
             ("Content service", "curated video list, weather bundle"), ("OTA + update server", "staged rollout, A/B rollback"),
             ("Signing", "offline HSM: AVB key; separate rotatable OTA key")]
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
             + B.mtxt(602, 480, ["Child data minimised; per-family envelope encryption.", "Policy is signed and cached: safe when offline.", "Stack: Kotlin/Compose apps; Postgres/Redis; LiveKit."], 9.5, B.INK, "400", "start", 1.3))
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


def topic_page(B, e, visual=None, nkp=6, nnum=6, ntab=1, nrisk=3, section=None):
    right = B.chip(e["id"], "brand") + conf_chip(B, e)
    pts = B.bullets(e.get("keyPoints", [])[:nkp])
    nums = "".join(B.tile(n["value"], n["label"], n.get("note", ""), n.get("basis")) for n in e.get("numbers", [])[:nnum])
    tabs = ""
    for t in e.get("tables", [])[:ntab]:
        tabs += f'<h3 style="margin-top:2mm">{B.esc(t["title"])}</h3>' + B.table(t["columns"], t["rows"][:8], "dense")
    right_col = visual if visual else (f'<div class="g3" style="grid-template-columns:repeat(2,1fr)">{nums}</div>{tabs}' if (nums or tabs) else "")
    risks = "".join(
        f'<div class="card" style="padding:2.2mm 2.8mm"><div style="margin-bottom:.8mm">{B.chip(B.SEV[r["severity"]][0], B.SEV[r["severity"]][1])}</div><div style="font-size:7.8pt;font-weight:700;line-height:1.25">{B.esc(r["risk"])}</div><div style="font-size:7.2pt;color:{B.MUTED};margin-top:.8mm">{B.esc(r["mitigation"])}</div></div>'
        for r in e.get("risks", [])[:nrisk])
    sup = f'<div class="card amber" style="padding:2mm 3mm;font-size:7.6pt"><b>Superseded:</b> {B.esc(e["superseded"])}</div>' if e.get("superseded") else ""
    stage = f'<div class="card soft" style="padding:2mm 3mm;font-size:7.8pt"><b>Stage 1:</b> {B.esc(e.get("stage1",""))}</div>'
    return f'''
{B.title_block(e["investorHeadline"], e["title"], right)}
<div class="g2" style="flex:none"><div class="card brand" style="padding:2.6mm 3.4mm"><h3>Decision</h3><div style="font-size:8.8pt">{B.esc(e["decision"])}</div></div><div class="card teal" style="padding:2.6mm 3.4mm"><h3>Why it matters</h3><div style="font-size:8.8pt">{B.esc(e["whyItMatters"])}</div></div></div>
<div class="row" style="flex:1;min-height:0"><div class="col" style="flex:1.15"><h3>Key points</h3>{pts}</div><div class="col" style="flex:1">{right_col}</div></div>
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
<div class="cols3" style="flex:1;min-height:0">{"".join(blocks)}</div>'''


# ----------------------------------------------------------------------------- appendices
def decisions_pages(B, doc):
    rows = B.parse_decisions()
    half = (len(rows) + 1) // 2
    for k, chunk in enumerate([rows[:half], rows[half:]]):
        trs = [[f"<b>{d}</b>", B.md_inline(t), dt] for d, t, dt in chunk]
        body = (B.title_block("Decision log" + (" (continued)" if k else ""), "Dated founder decisions; later decisions supersede earlier ones. Canonical source: docs/REQUIREMENTS.md")
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
    n_ver = 0
    for p in reports:
        if "Verification (second pass)" in open(p, encoding="utf-8").read():
            n_ver += 1
    ctx = {"n_reports": len(reports), "n_verified": n_ver, "E": E, "market": data.get("market")}
    doc = B.Doc()
    doc.add("Cover", cover(B, ctx), "cover")
    doc.add("Summary", exec_summary(B, ctx))
    doc.add("Problem", problem_page(B, ctx))
    doc.add("Product", product_page(B, ctx))
    doc.add("Architecture", architecture_page(B, ctx))
    for rid in ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21"]:
        if rid in E:
            doc.add("Topic " + rid, topic_page(B, E[rid]))
    doc.add("Roadmap", roadmap_page(B, ctx))
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
