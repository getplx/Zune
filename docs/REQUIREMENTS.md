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
| D4 | **SUPERSEDED by D19 (2026-10-02).** (was: **Cellular voice calls and SMS are IN scope.**) | 2026-10-02 |
| D5 | **SUPERSEDED by D19 (2026-10-02).** (was: Parent controls an **allowlist of numbers that can call the device** (inbound) and **which numbers the child can call/communicate with** (outbound).) | 2026-10-02 |
| D6 | **SUPERSEDED by D19 (2026-10-02).** (was: **SMS is not readable on the device**; it is readable in the parental-control interface.) | 2026-10-02 |
| D7 | WhatsApp-like **in-product messenger** between kids using Zune devices. 1:1 only (**no groups**). Text + emoji only. Under the parental contact controls (approved contacts only). (Was "same as calls/SMS"; see D19.) | 2026-10-02 |
| D8 | **Video calling** only with approved participants: other Zune kids, or parents via the parental-control interface. The parent-side calling interface is deferred ("later"). | 2026-10-02 |
| D9 | **Weather app** that also teaches children about weather. | 2026-10-02 |
| D10 | **Walkie-talkie** (push-to-talk). | 2026-10-02 |
| D11 | **AI assistant** with a ChatGPT-style conversation UI; kids can ask questions and **send images**. | 2026-10-02 |
| D12 | Parental controls are browser-based (parent portal). | 2026-10-02 |
| D13 | The product is limited to a **small, curated set of supported devices**. High-end **Snapdragon**-class devices are acceptable ("very high grade"); the device list is not limited to Pixels. Supersedes the Pixel-first recommendation in `docs/research/02-hardware-target.md` until topic 15 reports. | 2026-10-02 |
| D14 | The device has a **Settings app with the minimum settings**: **Wi-Fi and mobile data stay fully standard ("as it is")**, plus only what is fairly required. **Nothing unnecessary.** | 2026-10-02 |
| D15 | **Business model: sell the OS image (software); customers bring a qualified phone** from a curated supported-device list and install it themselves. We do not sell or inventory hardware. | 2026-10-02 |
| D16 | **Version 1 delivery is company-provisioned.** The first batch of users contact us; **we flash the image on their qualified phone and give it to them.** Customer self-install (the BYO installer of D15) comes in a later version. (Phones are assumed to be customer-supplied, consistent with D15; correct this if we will supply phones.) | 2026-10-02 |
| D17 | **Start on a Pixel.** The founder accepted beginning with a Pixel (Pixel 10a / 9a class, "a good performing phone") as the first supported device. A Snapdragon phone is **not required for v1**; Snapdragon candidates (Fairphone Gen 6+, Nothing Phone (3)) become a later second-source / premium tier, subject to relock bring-up and written OEM terms (report 15). Supersedes D13's Snapdragon preference for v1. | 2026-10-02 |
| D18 | **India is the first launch market.** Supersedes assumption A1 (US). Implications to research: India's child-privacy law (DPDP Act and Rules; a "child" is under 18), telecom/messaging rules (DoT, TRAI), Indian carriers and VoLTE, emergency numbers and cell-broadcast alerts, Indic languages, rupee pricing and recurring-payment rules, Pixel supply and warranty in India. | 2026-10-02 |
| D19 | **No cellular voice calls and no SMS.** All communication is internet-based and WhatsApp-style: in-product **text messages, voice calls and video calls**, 1:1 only (no groups), approved contacts only, parent-controlled. **Supersedes D4, D5 and D6.** The device needs only data connectivity (Wi-Fi and mobile data, D14). | 2026-10-02 |
| D20 | **English only** for version 1: no Hindi or other Indian languages (Stage 2 at the earliest). | 2026-10-02 |
| D21 | **First phase: about 200 users on Pixel phones; eventually the company builds its own hardware.** Own hardware is a later roadmap phase, not v1. The 10/25/100 cohort sizes in report 18 are replaced by a staged ~200-user first phase. | 2026-10-02 |

## Child-device feature list (Stage 1 scope)

1. ~~Cellular phone calls~~ (superseded by D19) -> **in-app voice calls** (WhatsApp-style, internet, 1:1, approved contacts)
2. ~~SMS~~ (superseded by D19): no SMS on the device
3. Zune Messenger (1:1 text + emoji, no groups, parent-visible, contact-approved)
4. Video calling (1:1, approved participants only)
5. Walkie-talkie (push-to-talk, approved contacts)
6. AI assistant (chat UI, text + image input, age-appropriate, parent-visible)
7. Videos (curated educational YouTube content, age/topic-gated, no YouTube exit)
8. Weather (with educational explanations)
9. Camera, Photos, Journal, Notebook, EPUB reader (from the first brief; still in scope)
10. Other non-browsing utilities (clock/alarm, calculator, voice recorder, etc.)
11. Installer + device-qualification program (a product component under D15: web/desktop flasher,
    pre-flight checks, parent-portal enrolment, update channel)
12. v1 delivery service: customer intake, eligibility check, flash + re-lock + QA station,
    hand-over with parent-portal enrolment (company-provisioned; D16)
13. Settings (minimal: Wi-Fi and mobile data as standard; everything else only if fairly required;
    parent-gated where a child changing it would defeat a control)

## Parent portal (browser) — Stage 1 scope

Contact approvals/allowlists (messenger, voice, video, walkie-talkie), message review, AI and video
controls, screen-time rules, device pairing. Parent-side video/voice calling is deferred.

## Open assumptions (to confirm one at a time with the founder)

- A1. ~~Launch market assumed US~~ **Superseded by D18: India.** Reports 11-15, 17, 18 (and parts of 06, 07) were written assuming the US (COPPA, T-Mobile/AT&T, WEA/NWS, USD pricing); they must be reconciled to India (reports 19, 20).
- A2. ~~Can the child send SMS?~~ **Moot: no SMS (D19).** The Zune Messenger is the child's text channel.
- A3. Google Mobile Services: **assumed none** (pure AOSP).
- A4. Target hardware: **D17: start on Pixel 10a/9a** (Snapdragon later, report 15). Earlier narrowing:
  D13 curated device set, and **D15
  to bring-your-own-device** (customer installs our image on a qualified phone; no manufacturer).
  Exact devices undecided (topics 15, 17). Re-lockability: see A7.
- A5. Product name: "Zune" is a codename only (Microsoft trademark history).
- A7. ~~UNCONFIRMED interpretation: v1 is company-provisioned~~ **Confirmed on 2026-10-02: now D16.**
  Consequences (apply from now on): (a) every v1 device must be re-lockable with our own AVB key
  (Device Support Contract MUST), which narrows the Snapdragon list; (b) a flashing + QA station and
  a customer intake process replace the customer installer in v1 (report 18); (c) because we flash
  and return the device, OEM-blob handling, warranty, customer-data wipe and handling-of-customer-
  property questions arise. **Still open:** exact number of users in the first batch.
- A8. **Target age range of children: UNCONFIRMED.** Reports assumed roughly 6-13; India's DPDP Act
  treats everyone under 18 as a child.
- A9. **Emergency calling: UNCONFIRMED.** D19 removes cellular voice, but a phone's radio can still place
  emergency-only calls (112 in India). Recommended default: keep an emergency-only dial path (no other
  cellular numbers). Needs founder confirmation and an India regulatory check (report 19).
- A10. **Connectivity:** Wi-Fi plus mobile data (D14). Assumed a data-only SIM/eSIM is supported;
  Wi-Fi-only use must also work.
