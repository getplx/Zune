# Zune: START HERE (build brief for a fresh Claude Code session)

Generated 2026-10-03 from the research and the founder's decisions. You have NO memory of the conversation that
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
4. Milestone Z1: fork the manifest, pin `android-17.0.0_r1`, baseline-build `aosp_cf_x86_64_only_phone-aosp_current-userdebug` on Cuttlefish.
5. Milestone Z2 in parallel: Pixel 10a/9a vendor module, relock with a **test** AVB key on dev phones only, OTA from the first device.
6. Start the backend skeleton (`backend/`), the portal skeleton and the device channel; they do not depend on the OS image.
Then follow the milestones Z3-Z8 in `01-prerequisites-and-phases.md`.

## 6. Spec sections (read the one you are building)

1. [`docs/build/01-prerequisites-and-phases.md`](01-prerequisites-and-phases.md)
2. [`docs/build/02-os-image-and-product.md`](02-os-image-and-product.md)
3. [`docs/build/03-lockdown-and-guardian.md`](03-lockdown-and-guardian.md)
4. [`docs/build/04-device-signing-ota-release.md`](04-device-signing-ota-release.md)
5. [`docs/build/05-backend-and-parent-portal.md`](05-backend-and-parent-portal.md)
6. [`docs/build/06-communication.md`](06-communication.md)
7. [`docs/build/07-ai-assistant.md`](07-ai-assistant.md)
8. [`docs/build/08-content-videos-weather-reader.md`](08-content-videos-weather-reader.md)
9. [`docs/build/09-core-apps-and-design-system.md`](09-core-apps-and-design-system.md)
10. [`docs/build/10-delivery-operations-and-pilot.md`](10-delivery-operations-and-pilot.md)
11. [`docs/build/11-compliance-and-privacy-engineering.md`](11-compliance-and-privacy-engineering.md)
12. [`docs/build/12-testing-qa-and-acceptance.md`](12-testing-qa-and-acceptance.md)
13. [`docs/build/99-consistency-log.md`](99-consistency-log.md)

`ZUNE_BUILD_SPEC_FULL.md` is the same content concatenated into one file for tools that want a single document.

## 7. Definition of done for the baseline

See `12-testing-qa-and-acceptance.md`: every Stage-1 feature works end to end on a re-locked Pixel 10a/9a; the bypass suite passes; OTA works
from the first external device; the monthly patch pipeline has run at least once; the external-family gates are closed; the flash station has
processed the staff cohort. **Stage 2 ("make it better") starts only after the first external cohort has been supported.**
