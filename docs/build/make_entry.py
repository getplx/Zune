#!/usr/bin/env python3
"""Generate docs/build/00-START-HERE.md, the repo-root CLAUDE.md and the single-file export
docs/build/ZUNE_BUILD_SPEC_FULL.md. Run from the repo root after the section files exist."""
import glob, os, re, datetime

ROOT = os.getcwd()
req = open("docs/REQUIREMENTS.md", encoding="utf-8").read()
rows = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(r"^\| (D\d+) \| (.*) \| (\d{4}-\d{2}-\d{2}) \|\s*$", req, flags=re.M)]
rows.sort(key=lambda r: int(r[0][1:]))
dec = "\n".join(f"| {d} | {t} | {dt} |" for d, t, dt in rows)
sections = sorted(glob.glob("docs/build/[0-9][0-9]-*.md"))
sections = [s for s in sections if not os.path.basename(s).startswith("00-")]
toc = "\n".join(f"{i+1}. [`{s}`]({os.path.basename(s)})" for i, s in enumerate(sections))

start = f"""# Zune: START HERE (build brief for a fresh Claude Code session)

Generated {datetime.date.today().isoformat()} from the research and the founder's decisions. You have NO memory of the conversation that
produced this. Everything you need is in this file, the numbered spec sections next to it, and `docs/` in this repo.

## 1. Mission

Build and deploy **Zune**: a kids-only custom **Android 17 (AOSP `android-17.0.0_r1`) OS image** plus a **browser-based parent portal** and
the cloud services behind them. The child's phone has **no web browser, no YouTube app or route to youtube.com, no cellular calls or SMS**.
It offers 1:1 text/voice/video and walkie-talkie with parent-approved contacts, a kid-safe AI assistant, curated learning video,
weather lessons, camera, photos, journal, notebook, EPUB reader and a minimal Settings app. Parents control everything from the portal.

Business model: the company **sells the image and the cloud service**. In version 1 customers contact us; **we flash and re-lock their own
Pixel 10a/9a** and hand it back (about 200 users, Bengaluru first, India launch market, English only). **No skin on stock Android (D22).**
Own hardware is a later phase. The purpose of this build is **a solid baseline that can be validated with the first customers before any
hardware investment.**

## 2. Binding decisions (authoritative; later wins; canonical file `docs/REQUIREMENTS.md`)

| # | Decision | Date |
|---|----------|------|
{dec}

Assumptions still open are listed at the bottom of `docs/REQUIREMENTS.md` (A-numbers). **D4-D6 are superseded by D19.**

## 3. How to work

1. **Verify access first:** `git ls-remote https://android.googlesource.com/platform/manifest | head -3`. If blocked, stop and tell the founder
   which host is denied. Do not work around the egress policy. A full AOSP **build** needs a separate build host
   (about 32 vCPU / 128 GB RAM / 1 TB NVMe minimum, 2 TB recommended, Ubuntu 24.04); a chat container can only inspect AOSP.
2. **Read in this order:** this file; `docs/REQUIREMENTS.md`; `99-consistency-log.md` (conflicts, gates, verify-first list); the section you
   are about to build; then the research reports it cites in `docs/research/` for background (they pre-date many decisions; where they
   disagree with `docs/REQUIREMENTS.md` or the spec sections, the decisions and spec win).
3. **Burn down "Verify first" before building on a claim.** Most Android findings came from GrapheneOS/LineageOS mirrors because Google's
   tree was unreachable during research. Each spec section ends with a Verify-first table (claim, how to verify, what to do if false).
4. **Gates.** Items marked `[GATE: ...]` are not engineering blockers except where stated. **No external family and no charging before
   the external-family gates are closed** (counsel's written view on DPDP s.9(3) and messenger classification; Google's answer on
   redistributing Pixel firmware; trust-and-safety and security staffing; key custodians; customer agreement; name clearance).
5. **Ask the founder one question at a time**, only for genuine decisions; otherwise apply the recommended default and record it.
6. **Git:** work on a branch off `research/android-kids-foundation`; commit and push to a branch; **do not open pull requests unless asked**;
   commit trailer `Co-Authored-By: Claude <noreply@anthropic.com>` plus the session link; **no model names in commit messages, trailers or authorship lines** (vendor model IDs in product configuration, such as 07's `config/models.yaml`, are not attribution).
7. **Record decisions** in `docs/REQUIREMENTS.md` with a date; keep spec sections in sync when a decision changes.
8. **Multi-agent runs** (the `Workflow` tool) need the founder's explicit opt-in ("use a workflow"). Reusable scripts: `docs/handoff/research-workflow.js`
   (research / verify / reconcile / critic) and `docs/build/build-spec-workflow.js` (regenerates the spec sections and would overwrite the consistency fixes recorded in `99-consistency-log.md`; do not rerun it without reapplying them).
9. **Be honest in claims and docs:** the defensible claim is "no browser app and no way to type a URL", never "unbypassable". Label estimates.

## 4. Repository layout to create (monorepo `zune/`)

`os/` (forked manifest, `device/zune`, `vendor/zune`, overlays, sepolicy) · `apps/*` (Android apps) · `libs/*` (shared Kotlin libs) ·
`backend/*` (services) · `portal/` (parent web app) · `station/` (flash/QA CLI + WebUSB installer) · `docs/` (this documentation).
Exact module names are in `01-prerequisites-and-phases.md` and `09-core-apps-and-design-system.md`.

## 5. First week (in order)

1. Verify AOSP access; record the result in `docs/build/PROGRESS.md` (create it; keep an append-only log of milestones, decisions, blockers).
2. Provision/confirm the build host, the two Pixel dev phones (unlocked), cloud accounts (see section 01 prerequisites), and the secrets manager.
3. Burn down the **top Verify-first items** in `99-consistency-log.md` (AOSP tag, release config, supervision framework in AOSP itself,
   `android17-security-release` branches, WebView provider, Browser2/Camera2 in `handheld_product.mk`, Pixel firmware licence text).
4. Milestone M1: fork the manifest, pin `android-17.0.0_r1`, baseline-build `aosp_cf_x86_64_only_phone-aosp_current-userdebug` on Cuttlefish.
5. Milestone M2 in parallel: Pixel 10a/9a vendor module, relock with a **test** AVB key on dev phones only, OTA from the first device.
6. Start the backend skeleton (`backend/`), the portal skeleton and the device channel; they do not depend on the OS image.
Then follow the milestones M3-M8 in `01-prerequisites-and-phases.md`.

## 6. Spec sections (read the one you are building)

{toc}

`ZUNE_BUILD_SPEC_FULL.md` is the same content concatenated into one file for tools that want a single document.

## 7. Definition of done for the baseline

See `12-testing-qa-and-acceptance.md`: every Stage-1 feature works end to end on a re-locked Pixel 10a/9a; the bypass suite passes; OTA works
from the first external device; the monthly patch pipeline has run at least once; the external-family gates are closed; the flash station has
processed the staff cohort. **Stage 2 ("make it better") starts only after the first external cohort has been supported.**
"""
open("docs/build/00-START-HERE.md", "w", encoding="utf-8").write(start)

claude = """# CLAUDE.md

This repository is the Zune project (a kids-only, browser-less Android 17 OS image + parent portal).

**Start with `docs/build/00-START-HERE.md`.** It is the build brief: mission, binding decisions, how to work, first-week checklist and the map of
spec sections. Authoritative decisions live in `docs/REQUIREMENTS.md` (later decisions win). Research background is in `docs/research/` and
`docs/HANDOFF.md`; investor material is in `docs/investor/`.

Working rules (also in the brief): verify AOSP network access first; burn down each section's "Verify first" table before relying on a claim; ask the
founder one question at a time; commit and push to a branch without opening pull requests; no model names in commits; multi-agent workflows only
with the founder's explicit opt-in.
"""
open("CLAUDE.md", "w", encoding="utf-8").write(claude)

full = [start, "\n\n---\n\n"]
for s in sections + (["docs/build/99-consistency-log.md"] if os.path.exists("docs/build/99-consistency-log.md") else []):
    full.append(f"\n\n---\n\n<!-- source: {os.path.basename(s)} -->\n\n" + open(s, encoding="utf-8").read())
open("docs/build/ZUNE_BUILD_SPEC_FULL.md", "w", encoding="utf-8").write("".join(full))
print("sections:", len(sections), "| full words:", sum(len(x.split()) for x in full))
