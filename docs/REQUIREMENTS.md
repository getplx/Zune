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
| D22 | **No "skin" product.** We will not ship a launcher or Device-Owner layer on stock Android. The product is the full custom OS image. **Goal: build a solid baseline and validate it with an initial group of customers before investing in dedicated hardware.** | 2026-10-03 |
| D23 | **Target age range: 7 to 14.** (Resolves A8.) Design youngest-age UX (target sizes, voice-first, reading level) for 7, and moderation/AI/content for 7-9, 10-12, 13-14 bands. India's DPDP Act still treats all under-18 as children. | 2026-10-03 |
| D24 | **The Zune Guardian has full control of allowing and disabling anything** on the device (apps, features, settings, network, contacts, time, content). Approved: ZuneGuardian is the Device Owner and holds the Android 17 supervision role (a one-way door set at provisioning). | 2026-10-03 |
| D25 | **Videos follow the research recommendation (conditional go).** Tier 1 = licensed/open offline content plus paid partners, which is the launch base. Tier 2 = YouTube, made-for-kids-only, in one isolated embedded player, behind a remote kill switch; drop it if YouTube refuses or is silent after 8 weeks. Launch must not depend on YouTube. Amends D2/D3: there is still no YouTube app or route to youtube.com. | 2026-10-03 |
| D26 | **Web engine:** ship a hardened WebView (Vanadium prebuilt) with a named owner and an update SLA at Chromium cadence; WebView only in the two apps that need it (Reader, Videos). | 2026-10-03 |
| D27 | **Parent visibility and retention:** parents can read their child's messages and AI chats; the child is told; content retained in a restricted vault for 12 months (final period subject to counsel's reading of DPDP Rule 8(3)). | 2026-10-03 |
| D28 | **Emergency calling: 112 only.** No dialer; the platform emergency path stays; no other cellular calling. (Resolves A9; the "remove emergency calling" override is not used.) | 2026-10-03 |
| D29 | **AI vendor: OpenAI is the default; Anthropic is the fallback.** Supersedes report 07's Anthropic-first design. OpenAI's terms for products used by children, India data residency, zero retention and moderation endpoints must be verified before build. | 2026-10-03 |
| D30 | **Wi-Fi sign-in (captive portal) pages are unsupported in version 1;** parent-hotspot workaround documented. | 2026-10-03 |
| D31 | **Device defaults:** Bluetooth on; NFC off; USB file transfer off; **gesture ("iOS-style") navigation with no on-screen buttons** (needs a Quickstep-compatible launcher; flagged as a risk in report 03); English only; Stage-1 location from parent-set places only. | 2026-10-03 |

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
- A8. ~~Target age range~~ **Resolved: D23 (7-14).** Original note: Reports assumed roughly 6-13; India's DPDP Act
  treats everyone under 18 as a child.
- A9. ~~Emergency calling~~ **Resolved: D28 (112 only).**
- A10. **Connectivity:** Wi-Fi plus mobile data (D14). Assumed a data-only SIM/eSIM is supported;
  Wi-Fi-only use must also work.
- A11. **UNCONFIRMED (defaults applied; founder did not answer):** the company operates through an Indian private limited with India-region hosting (AWS Mumbai primary, Hyderabad DR). Outside-customer gates (counsel opinion on DPDP s.9(3), Google firmware-licence answer, T&S and security staffing, key custodians, first city, spare-phone exception, support promise, name clearance) remain OPEN and block the first external family, not the build.
