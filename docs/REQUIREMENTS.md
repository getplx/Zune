# Zune — Founder Requirements (canonical)

Source: founder messages in session on 2026-10-02. This file is the single source of truth for
product decisions. Research reports in `docs/research/` must be reconciled against it; where a
report disagrees, this file wins. Append new decisions with a date; do not silently rewrite.

## Product

A custom AOSP-based Android OS image (base: Android 17, `android-17.0.0_r1`, clean build with the
bare-minimum services) for children, sold as a product (image and/or devices). Custom first-party
apps only. **No internet browser. No access to YouTube by any route.** Parents manage everything
from a **browser-based parental-control portal** (the child device has no browser).

Delivery is staged:

- **Stage 1 — make everything exist.** Every feature below works end to end, in its simplest form.
- **Stage 2 — make it better.** Polish, depth, performance, richer content.

## Decisions (resolved)

| # | Decision | Date |
|---|----------|------|
| D1 | No web browser on the device. | 2026-10-02 |
| D2 | No way for the end user to reach YouTube (no app, site, link-out, or deep link). Videos appear only inside the Zune **Videos** section. | 2026-10-02 |
| D3 | Videos are curated YouTube content, shown only if relevant to the child's **age group** or to a **topic the child asked about** (research). Fully controlled experience. | 2026-10-02 |
| D4 | **Cellular voice calls and SMS are IN scope.** | 2026-10-02 |
| D5 | Parent controls an **allowlist of numbers that can call the device** (inbound) and **which numbers the child can call/communicate with** (outbound). | 2026-10-02 |
| D6 | **SMS is not readable on the device**; it is readable in the parental-control interface. | 2026-10-02 |
| D7 | WhatsApp-like **in-product messenger** between kids using Zune devices. 1:1 only (**no groups**). Text + emoji only. Under the same parental contact controls as calls/SMS. | 2026-10-02 |
| D8 | **Video calling** only with approved participants: other Zune kids, or parents via the parental-control interface. The parent-side calling interface is deferred ("later"). | 2026-10-02 |
| D9 | **Weather app** that also teaches children about weather. | 2026-10-02 |
| D10 | **Walkie-talkie** (push-to-talk). | 2026-10-02 |
| D11 | **AI assistant** with a ChatGPT-style conversation UI; kids can ask questions and **send images**. | 2026-10-02 |
| D12 | Parental controls are browser-based (parent portal). | 2026-10-02 |

## Child-device feature list (Stage 1 scope)

1. Phone calls (allowlisted inbound and outbound; emergency calls always work)
2. SMS (captured and forwarded to parent portal; not displayed on device)
3. Zune Messenger (1:1 text + emoji, no groups, parent-visible, contact-approved)
4. Video calling (1:1, approved participants only)
5. Walkie-talkie (push-to-talk, approved contacts)
6. AI assistant (chat UI, text + image input, age-appropriate, parent-visible)
7. Videos (curated educational YouTube content, age/topic-gated, no YouTube exit)
8. Weather (with educational explanations)
9. Camera, Photos, Journal, Notebook, EPUB reader (from the first brief; still in scope)
10. Other non-browsing utilities (clock/alarm, calculator, voice recorder, etc.)

## Parent portal (browser) — Stage 1 scope

Allowlists (calls/SMS/messenger/video/walkie-talkie), SMS reader, message review, AI and video
controls, screen-time rules, device pairing. Parent-side video/voice calling is deferred.

## Open assumptions (to confirm one at a time with the founder)

- A1. Launch market / first country: **assumed US** until told otherwise.
- A2. Can the child **send** SMS, or only receive (parent-visible)? **Assumed: child does not
  send or read SMS on the device**; the Zune Messenger is the child's text channel.
- A3. Google Mobile Services: **assumed none** (pure AOSP).
- A4. Target hardware: undecided (see `docs/research/02-hardware-target.md`).
- A5. Product name: "Zune" is a codename only (Microsoft trademark history).
