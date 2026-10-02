#!/usr/bin/env python3
"""Regenerate the report-status table in docs/HANDOFF.md from the files in docs/research/.

Usage (from the repo root):  python3 docs/handoff/refresh-status.py
A report counts as skeptic-verified if it contains a "Verification (second pass)" section.
"""
import datetime
import os
import re

TOPICS = [
    ("01", "AOSP base release, cadence, build host", "01-aosp-base-release.md"),
    ("02", "Hardware target (Pixel-first; reopened by D13)", "02-hardware-target.md"),
    ("03", "Minimal product config", "03-minimal-product-config.md"),
    ("04", "No-browser lockdown", "04-no-browser-lockdown.md"),
    ("05", "Parental-controls platform", "05-parental-controls-platform.md"),
    ("06", "Curated video (YouTube)", "06-curated-learning-video.md"),
    ("07", "AI assistant", "07-ai-assistant.md"),
    ("08", "Walkie-talkie / comms", "08-walkie-talkie-comms.md"),
    ("09", "Core apps stack", "09-core-apps-stack.md"),
    ("10", "OTA / signing / security / supply chain", "10-ota-signing-security-supply-chain.md"),
    ("11", "Compliance & legal", "11-compliance-legal-regulatory.md"),
    ("12", "Telephony: calls + SMS + allowlists (D4-D6; SUPERSEDED by D19)", "12-telephony-calls-sms-allowlists.md"),
    ("13", "Kid messenger + video calling (D7-D8)", "13-kid-messenger-and-video-calling.md"),
    ("14", "Weather education app (D9)", "14-weather-education-app.md"),
    ("15", "Snapdragon device selection (D13)", "15-snapdragon-device-selection.md"),
    ("16", "Minimal Settings app (D14)", "16-minimal-settings-app.md"),
    ("17", "Selling the image: BYO distribution, installer, licensing (D15)", "17-byo-image-distribution-installer.md"),
    ("18", "v1 flash-and-deliver operations (D16)", "18-v1-flash-and-deliver-operations.md"),
    ("19", "India: regulation and compliance (D18)", "19-india-regulatory-compliance.md"),
    ("20", "India: market, carriers, languages, content, pricing (D18)", "20-india-market-and-localization.md"),
    ("21", "Own-hardware roadmap, India (D21)", "21-own-hardware-roadmap-india.md"),
    ("00", "Cross-topic critique", "00-cross-topic-critique.md"),
]
START, END = "<!-- STATUS-TABLE:START -->", "<!-- STATUS-TABLE:END -->"

rows = ["| # | Topic | State |", "|---|-------|-------|"]
for n, title, fname in TOPICS:
    path = os.path.join("docs", "research", fname)
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read()
        reconciled = " + reconciled" if "Reconciliation with founder decisions" in txt else ""
        state = ("**written, skeptic-verified**" if "Verification (second pass)" in txt
                 else "**written**, skeptic pass pending") + reconciled
    else:
        state = "not yet written"
    rows.append(f"| {n} | {title} | {state} |")
block = (f"{START}\n" + "\n".join(rows) +
         f"\n\n(Generated {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC by "
         f"docs/handoff/refresh-status.py)\n{END}")

handoff = open("docs/HANDOFF.md", encoding="utf-8").read()
if START in handoff:
    handoff = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, handoff, flags=re.S)
else:
    a = handoff.index("| # | Topic | State |")
    b = handoff.index("Refresh in conversation 2")
    handoff = handoff[:a] + block + "\n\n" + handoff[b:]
open("docs/HANDOFF.md", "w", encoding="utf-8").write(handoff)
print("\n".join(rows))
