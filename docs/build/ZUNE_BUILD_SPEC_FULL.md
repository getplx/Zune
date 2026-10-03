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
   (about 32 vCPU / 128 GB RAM / 1 TB NVMe, Ubuntu 24.04); a chat container can only inspect AOSP.
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
   commit trailer `Co-Authored-By: Claude <noreply@anthropic.com>` plus the session link; **no model names in commits or any pushed artifact.**
7. **Record decisions** in `docs/REQUIREMENTS.md` with a date; keep spec sections in sync when a decision changes.
8. **Multi-agent runs** (the `Workflow` tool) need the founder's explicit opt-in ("use a workflow"). Reusable scripts: `docs/handoff/research-workflow.js`
   (research / verify / reconcile / critic) and `docs/build/build-spec-workflow.js` (regenerates the spec sections).
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

1. [`docs/build/01-prerequisites-and-phases.md`](01-prerequisites-and-phases.md)
2. [`docs/build/02-os-image-and-product.md`](02-os-image-and-product.md)
3. [`docs/build/03-lockdown-and-guardian.md`](03-lockdown-and-guardian.md)
4. [`docs/build/04-device-signing-ota-release.md`](04-device-signing-ota-release.md)

`ZUNE_BUILD_SPEC_FULL.md` is the same content concatenated into one file for tools that want a single document.

## 7. Definition of done for the baseline

See `12-testing-qa-and-acceptance.md`: every Stage-1 feature works end to end on a re-locked Pixel 10a/9a; the bypass suite passes; OTA works
from the first external device; the monthly patch pipeline has run at least once; the external-family gates are closed; the flash station has
processed the staff cohort. **Stage 2 ("make it better") starts only after the first external cohort has been supported.**


---



---

<!-- source: 01-prerequisites-and-phases.md -->

# Prerequisites, repository layout, phased plan and milestones

## Purpose and scope

This section tells the building session what must exist before it starts, how the repository is laid out, which humans it depends on, and the order of work (M0 to M8). Stage 1 means every Stage-1 feature in REQUIREMENTS.md works end to end in its simplest form (M5) and is validated with about 200 families (M7). Stage 2 follows M8.

Conventions for all sections:
- `zune/` is the root of the getplx/Zune checkout, so `zune/docs` is today's `docs/`. Never create a nested `zune/zune/`.
- `W<n>` is weeks from start (W0 = week of 2026-10-05). Durations are estimates [INFERRED], re-baselined at M1 exit (PRE-16). §4.x means the Design subsections.

Not covered here, by file in `docs/build/`: `02-os-image-and-product.md`, `03-lockdown-and-guardian.md`, `04-device-signing-ota-release.md`, `05-backend-and-parent-portal.md`, `06-communication.md`, `07-ai-assistant.md`, `08-content-videos-weather-reader.md`, `09-core-apps-and-design-system.md`, `10-delivery-operations-and-pilot.md`, `11-compliance-and-privacy-engineering.md`, `12-testing-qa-and-acceptance.md`.

## Decisions applied and reconciliations

Reconciliations applied:

| Decision or report | Effect on this section |
|---|---|
| D15, D16, D17, D21 | Pixel 10a (`stallion`) and 9a (`tegu`) only, company-flashed; Fairphone Gen 6+ launch plan [R15, R17] is out; no customer-handset inventory. |
| D22 | `zune/os` is a full image; no Device-Owner-on-stock track. R09 Tier A becomes five in-tree components: ZuneGuardian, ZuneLauncher, ZuneSettings, ZuneSetup, ZuneUpdater. R09 "ZuneHome" is ZuneLauncher; ZuneComms and ZunePolicyService fold into ZuneGuardian. |
| D24, D31 | M3 exit requires Device Owner plus supervision role and gesture navigation with no on-screen buttons; R09's three-button navigation is dropped. |
| D26, D29 | No Chromium build on the host in v1 (supersedes R10 "self-build monthly"). OpenAI and Anthropic accounts both open at M0; R19 G7 (Anthropic confirmation for child use) covers both. |
| D18, D19, D28 | US items removed (COPPA, carrier VoLTE, SMS vault, E911, US-SKU rules in R10 G5, R17, R18); replaced by DPDP gates [R19 §4.4], a 112 field test and India-SKU intake [R20 §4.1]. |
| D21, R20 vs R18 | R18's 10/25/100 cohorts become C0 12, C1 30, C2 70, C3 88 (cumulative 12/42/112/200); R20's 12/30/70/90 sums to 202. |
| R20 vs R19 | R19 wins on legal posture: C0 is staff households only (R20's "friends" join C1); C1-C3 are free and invite-only until charging gates close. |
| R21 | R21's `M<n>` means months from Oct 2026; here M0-M8 are milestones, and H1-H4 are evaluated in M8. R21's months 3-6 first cohort is optimistic. |
| Gate names | R19 G1-G10 = LEG-1..10; R17 G5 = FW-1; R18 G0-G2 = SP-n, EXT-n; R10 G1-G6 stay "release gates G1-G6"; R21 H1-H4 = HW-1..4. Do not use bare "G5". |
| R01 vs R09, R10 | R01's separate `zune/manifest` repo becomes R09's monorepo (`zune/os/manifest`); split repos are a fallback. R01's 1 TB vs R10's 2 TB: one host now (2 TB recommended), a second by M5. |
| D23, HANDOFF §9 | Panels and red-team sets use bands 7-9, 10-12, 13-14 (not R09's 4-6). No `main` branch exists; do not create one without founder approval. |

## Requirements

**Environment**
- PRE-01 MUST: Before any other work run `git ls-remote https://android.googlesource.com/platform/manifest | head -3` and `curl -sSfI` against source.android.com, dl.google.com and developers.google.com. If any fails, stop and send the founder one message naming the denied host [HANDOFF §8].
- PRE-02 MUST: Build host is Ubuntu 24.04, at least 32 vCPU, 128 GB RAM, 1 TB NVMe (2 TB recommended), `/dev/kvm` readable and writable. Builds run in one pinned container image (digest in `zune/os/tools/build-container.lock`). The agent container (about 30 GB disk) MUST NOT run full builds [HANDOFF §2].
- PRE-03 MUST: Build host and CI hold no production keys (list in 04). Dev builds use a throwaway key set we generate (never AOSP's public test keys), flagged `dev`; ZuneUpdater and zune-station reject dev-signed artifacts on the prod channel.
- PRE-04 MUST: Procure Pixel dev units: 1 per model at M2 start, 2 per model before OEM unlocking is turned off on any dev phone, 3 per model before M6 [R10 G5]; new, India SKU, unlocked, not carrier-financed, no Google account. Record `version-bootloader`, `version-baseband` and the anti-rollback variable before the first flash; never flash an older image than installed [R18 F9].
- PRE-05 MUST: Phones attach to a bare-metal lab workstation (direct USB, no hub, no VM) with platform-tools pinned by SHA-256. A named lab operator confirms every `flashing unlock` and `flashing lock` prompt. Keep OEM unlocking ON until a phone's signed boot is proven [R18 §4.2].
- PRE-06 MUST: Accounts in §4.2 have at least 2 human owners, MFA and offline recovery codes. AWS has separate dev, staging and prod accounts; an SCP denies all regions except ap-south-1 and ap-south-2 (global services excepted).
- PRE-07 MUST: Dev and staging hold synthetic data only. No real child data, prompt or image reaches OpenAI, Anthropic, LiveKit Cloud or any vendor until its terms are verified per 07 and, for non-staff families, LEG-7 is closed.
- PRE-08 MUST: Runtime secrets live in AWS Secrets Manager/KMS (ap-south-1); CI reaches AWS by GitHub OIDC, no long-lived keys; a secret scanner runs on every push and fails on private keys and API-key patterns. The repo is private; self-hosted runners attach only to private repos.

**Repository and process**
- PRE-09 MUST: Use exactly `zune/os`, `zune/apps/*`, `zune/libs/*`, `zune/backend/*`, `zune/portal`, `zune/station`, `zune/docs`. The AOSP workspace checks out getplx/Zune at `vendor/zune` using manifests from `zune/os/manifest`; M1 MUST prove Soong and product discovery there or adopt a §4.3 fallback.
- PRE-10 MUST: Pin AOSP to `refs/tags/android-17.0.0_r1` with commit SHAs recorded, never a floating branch. Fork an AOSP repo only as a patch stack in `zune/os/patches/<repo>/` with an ADR [R01].
- PRE-11 MUST: Maintain `zune/docs/gates.md` (ID, type, owner, request date, status, evidence), `verified-facts.md` (Verify-first row, command, output, date, outcome), `decisions/NNN-*.md` (ADRs) and `milestones/Mn.md` (exit evidence).
- PRE-12 MUST: Follow the founder's working agreements [HANDOFF §9]: push to branches, no pull requests unless asked; trailer `Co-Authored-By: Claude <noreply@anthropic.com>`, no model names in commits or artifacts; clean tree at session end; ask the founder only at a gate, one question at a time.
- PRE-13 MUST: User-visible product-name strings come from one resource key so the name can change (A5). SHOULD: choose the Android package-name root in an M0 ADR without the codename; package names are effectively permanent once devices ship.
- PRE-14 MUST: Company-owned phones are dev/QA units, "not for sale" (D15); customer replacement phones need a written founder exception [R20 §4.7].

**Plan and gates**
- PRE-15 MUST: Follow §4.5 order and dependencies; M4 and the Gradle app track MAY start at M1. Close a milestone only when every exit criterion has evidence in `zune/docs/milestones/Mn.md`; the founder acknowledges M0, M2, M5, M6, M7, M8.
- PRE-16 MUST: Re-baseline at M1 exit from measured build times, disk use and velocity in an ADR; escalate any milestone slipping more than 4 weeks [INFERRED threshold].
- PRE-17 MUST: Rebase once onto the Q4-2026 AOSP drop (RB-1) after it appears on googlesource and between M2 exit and M5 feature freeze, never during M6-M7 [R01]. If absent at M5 exit, stay on r1 plus backports.
- PRE-18 MUST: Send the request for every gate in the Gate register by W2; a gate with no request at W2 goes to the founder.
- PRE-19 MUST: No non-staff household is invited or flashed and no public waitlist or marketing runs until LEG-1..10 and EXT-1..7 are closed.
- PRE-20 MUST: At most 100 devices are flashed before FW-1 closes; zune-station refuses job 101 without the FW-1 flag [R17 §8]. No payment is collected before PAY-1 and FW-1 close.

## Design and build instructions

### 4.1 Machines

| Node | Role | Rules |
|---|---|---|
| Agent container | Read, edit, plan, `git` | Needs the PRE-01 hosts; if gerrit.googlesource.com is blocked use `repo init --repo-url https://github.com/GerritCodeReview/git-repo` [HANDOFF §2] |
| Build host | AOSP build, Cuttlefish CI, release artifacts, ephemeral self-hosted runners | PRE-02; outside the prod AWS account; `/dev/kvm` needs bare metal or nested virtualisation (GCE): run the kvm check on a trial instance before buying [R01 F7] |
| Lab workstation | Pixels, `zune-station` | PRE-05; 16 GB RAM, 500 GB SSD, Chromium for WebUSB [R18 §4.2, R17 F5] |
| Offline signing host | Key generation and signing | Air-gapped, 2-of-3 custodians [R10]; needed before M6; design in 04 |
| AWS India | Backend, portal, OTA artifacts, logs | ap-south-1 primary, ap-south-2 DR (A11, unconfirmed); design in 05 |

Baseline commands (build host):
```bash
repo init -u https://android.googlesource.com/platform/manifest -b refs/tags/android-17.0.0_r1 \
  --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle && repo sync -c -j8 --no-tags
source build/envsetup.sh && lunch aosp_cf_x86_64_only_phone-aosp_current-userdebug && m -j"$(nproc)"
adb shell getprop ro.build.id   # on Cuttlefish; expect CP2A.260605.016 [verify]
```

### 4.2 Accounts

| Account | Open by | Rules |
|---|---|---|
| GitHub org getplx, private repo, self-hosted runner | M0 | 2 owners; branch protection; no `main` yet |
| AWS Organization (management, dev, staging, prod) | M0 | Founder-owned until the Indian private limited exists (A11), then transferred; no real child data before LEG-2; billing alerts |
| Domain, DNS, TLS, role mailboxes (security, grievance, privacy), email | M0 | Registrar lock, MFA; neutral domain until name clearance |
| OpenAI API (default), Anthropic API (fallback) | M0 open, M5 use | Project per environment, spend limits; terms per 07 |
| LiveKit (only if 06 selects it); payment aggregator and DLT SMS sender (PAY-1, or if 05 picks SMS OTP) | M5; not before M6 | Prefer self-hosted LiveKit in ap-south-1; Cloud needs a DPA and verified India region |

### 4.3 Repository layout

```
zune/                       # root of getplx/Zune
  os/
    manifest/               # default.xml, pinned AOSP snapshot, zune.xml (02)
    device/ vendor/         # product, device, RRO, prebuilt APK imports (02, 04, 09)
    sepolicy/ patches/      # SELinux; patch stack per forked AOSP repo (target: none)
    tools/                  # pre-check.sh, build container, image-diff, watcher
  apps/                     # Tier A (Soong, platform key): guardian launcher settings setup updater
                            # Tier B (Gradle, zune-apps key): messenger calls walkie assistant videos weather
                            #   camera photos journal notebook reader clock calculator recorder
  libs/{core,design,speech,net,testing}/
  backend/{gateway,policy,comms,ai-gateway,content,weather}/   # more services per 05
  portal/  station/         # parent portal; zune-station CLI and WebUSB installer
  docs/                     # REQUIREMENTS.md, HANDOFF.md, research/, build/, gates.md,
                            # verified-facts.md, decisions/, milestones/
```

Placement: `zune/os/manifest/zune.xml` adds `<project name="Zune" remote="zune" path="vendor/zune" revision="..."/>` (remote fetch `https://github.com/getplx/`); dev uses the branch, release builds a SHA from `repo manifest -r`. Put `.find-ignore` in `portal`, `backend`, `station`, `docs`, `libs` and Gradle `build/` dirs so Soong skips them. Fallbacks if the M1 spike fails, in order: (a) per-directory `<linkfile>`; (b) subtree-split repos `getplx/zune-device` and `getplx/zune-vendor` with the monorepo as source of truth. Never commit private keys; `zune/os/tools/gen-dev-keys.sh` writes dev keys outside the repo.

### 4.4 Roles the plan assumes [INFERRED unless cited]

| Role (basis) | Needed from |
|---|---|
| Platform engineers x2 (R01); security and release owner 0.5-1 FTE and a named WebView owner (R10, D26) | M1; M2 |
| System-app engineers x2 (Tier A, R09); Android app engineers x5 for 16-20 weeks (R09) | M3; M1 |
| Backend engineers x3, frontend x1 | M4 |
| Kid-UX designer, content editor, science reviewer on contract (R09, R20); QA engineer; 6-8 consenting children per band 7-9, 10-12, 13-14 (R09 §4.4) | M1, M5; M3 |
| Trust and safety lead, 24x7 on-call, resident grievance officer (R19) | Before first cross-family link |
| Lab operator and station technician: 1 technician, 0.5 support, 0.25 release engineer (R18) | M2, M6 |
| Indian counsel (M0), 3 key custodians (M6), insurance broker (M6) | As stated |

If agents replace some engineers, scope is unchanged; only the calendar moves.

### 4.5 Milestones

Critical path: M0 > M1 > M2 > M3 > M5 > M6 > M7 > M8. M4 and the Gradle app track run in parallel from M1 and finish before M5 integration.

| Milestone (weeks) | Deliverables | Depends on | Exit criteria (all MUST) |
|---|---|---|---|
| **M0** Foundation, legal gates opened (W0-W2; gates run to M7) | PRE-01..03 and PRE-06..14 met; Pixels ordered (PRE-04); repo skeleton; `pre-check.sh`; `gates.md` with every register gate; briefs sent: counsel (R19 questions), Google (licence read, request drafted for founder), name clearance | Founder spend approval | `pre-check.sh` PASS; each gate has owner and request date; Verify-first 1-3 recorded |
| **M1** Cuttlefish baseline, manifest pin (W1-W5) | Pinned manifest; build container; vanilla `aosp_cf_x86_64_only_phone` boots; `zune_base` (from `base_*`, no Browser2, HTMLViewer, CaptivePortalLogin) boots; CI per merge request; weekly security-branch watcher; Gradle skeleton | M0 | Vanilla boots, `ro.build.id` and SPL recorded; placement spike passed or fallback adopted; package-allowlist diff gate green; no http(s) VIEW resolver; build times recorded; plan re-baselined; Verify-first 4-7 resolved |
| **M2** Pixel bring-up, relock, OTA (W4-W12) | `stallion` and `tegu` layers (adevtool, pinned Google stock build); QPR1 skew decision record; zune-station v0 (serial-pinned); custom AVB key and lock; ZuneUpdater fork; full OTA N to N+1 from a static bucket | M1; Pixels; lab operator | Both models boot `zune_base` locked, yellow state; OTA applies, A/B fallback shown, downgrade rejected; attestation result recorded; OEM-unlock-off tested only on a sacrificial unit; Verify-first 8-11 resolved |
| **M3** Core OS (W8-W20) | ZuneSettings; ZuneLauncher (gesture navigation); ZuneGuardian (Device Owner, supervision role, signed-policy engine with local dev signer, PIN, time engine); ZuneSetup with mock pairing; D31 defaults; bypass suite v0 in CI | M1; M2 for device proof | On Cuttlefish and both Pixels: ZuneSetup provisions Guardian as Device Owner with supervision role; no http(s) handler or YouTube route; gesture navigation with zero nav buttons (not shown by W16: founder decision); unsigned, stale or rolled-back policy rejected; zero P0 bypass failures |
| **M4** Backend, portal (W6-W20) | IaC for ap-south-1 and ap-south-2; Zune Gateway, Policy Service, device channel; pairing with Rule-10 verification record; consent ledger; audit log; 12-month vault; envelope keys; Stage-1 portal pages (message and AI review complete in M5); observability; backups | M0 accounts | Synthetic parent claims a Pixel by QR, edits a rule, device enforces the signed policy within 05's latency target; remote lock works; DR restore drill with RTO and RPO recorded; no data outside India regions; Verify-first 12 resolved |
| **M5** Comms, AI, content, apps (W14-W30) | Messenger, Calls, Walkie; Assistant (OpenAI default, Anthropic fallback); Videos (Tier 1; Tier 2 behind kill switch); Weather; Camera, Photos, Journal, Notebook, Reader, utilities; moderation and T&S tooling; starter content | M3, M4; vendor terms | REQUIREMENTS child-device items 1 and 3-10 work end to end on two Pixels; red-team and moderation sets pass (07, 12); Tier 2 off shows Tier 1 only; 72-hour soak and battery measured; 16 KB-clean; feature freeze; RB-1 done or deferred by ADR |
| **M6** Staff pilot C0, 12 staff households (W28-W36) | Production zune-station (CLI, WebUSB); per-model pilot keys; signed bundles; QR hand-over; support tooling; drills | M5; SP-1..7 | 112 field test passed; zero open child-safety P1; onboarding median under 25 min [R20]; first OTA reaches all devices; kill switches L1-L4 drilled; no successful bypass |
| **M7** External cohorts, Bengaluru (W36 to about W56) | C1 30, C2 70, C3 88 (cumulative 42, 112, 200); production keys; service-unlock; courier to Hyderabad and Pune only from C2 [R20] | M6; LEG-1..10; EXT-1..7; FW-1 before device 101 | C1: first-pass flash 95%+, no unrecovered brick, 4-week use 85%+, under 2 support contacts per family per week, NPS 40+. C2: OTA success 98% in 72 h. C3: 8-week retention 75%+, no open Sev-1 [R20 thresholds, unvalidated] |
| **M8** Review, hardware-readiness data (about 8 weeks after C3) | Review report; HW-1..4 evidence [R21 §4.3]; patch-lag and OTA statistics; bypass and tamper results; cost per device vs INR 1,850 [R20]; Stage-2 backlog | M7 | Founder gets pass, fail or unknown per HW gate; no ODM purchase order (needs HW-3); Stage-2 plan decided |

Indicative calendar [INFERRED]: M6 about Apr-Jun 2027, M7 about Jun-Oct 2027. DPDP children's duties bind from 13 May 2027 [R19]; act as if in force now.

### 4.6 What blocks what

- Blocks building: PRE-01, PRE-02, repo write access, spend approval, Pixels (M2), API keys (M5).
- Blocks only the first external family: counsel opinion, Indian entity, Google firmware answer, name clearance, T&S and security staffing, key custodians, first city, spare-phone exception, support promise [A11, R19].
- Blocks charging: PAY-1, FW-1.

### 4.7 First-week checklist

1. Day 0: read REQUIREMENTS.md, HANDOFF.md, `docs/build/*`; `git fetch`; branch `build/m0-foundation` off `research/android-kids-foundation`; run PRE-01; create the §4.3 skeleton and `zune/os/tools/pre-check.sh` (PRE-01, 02, 08).
2. Day 1: provision or verify the build host; pin the container; start the vanilla `repo sync` in the background; record Verify-first 1-3 in `verified-facts.md`.
3. Day 2: read Google's Pixel licence pages (developers.google.com/android/images, /ota, /drivers); give them and the R19 question list to counsel; draft Google outreach for the founder. Open the §4.2 accounts and apply the SCP.
4. Day 3: first clean baseline build (record wall time and disk); boot Cuttlefish; record each Pixel's serial, bootloader, baseband and anti-rollback values in `docs/lab/devices.md`.
5. Day 4: ADRs for path alias, `main`, host sizing, package root, brand key.
6. Day 5: one message to the founder: status, three measured numbers, gates needing founder action by impact, one blocking question.

## Acceptance criteria and tests

| Check | Observable pass |
|---|---|
| PRE-01, 02 | `git ls-remote` prints at least 3 refs; the hosts return HTTP 2xx/3xx; `pre-check.sh` shows 32+ vCPU, 128+ GB RAM, `/dev/kvm` rw; a baseline build completes in the container |
| PRE-03, 08 | Secret scan of full history finds no private key; `gh secret list` shows no cloud access keys; the prod-channel tool rejects a dev-signed bundle |
| PRE-06, 07 | From the prod account an us-east-1 API call is explicitly denied; dev and staging databases hold only generated tenants |
| PRE-09 | `ls zune` shows exactly the required paths; the placement spike builds `zune_base` |
| PRE-11, 18 | Every `[GATE: ...]` in specs 01-12 appears in `gates.md` with owner and request date |
| Milestones, week 1 | Each `Mn.md` ticks every exit criterion with evidence; the Day 5 message exists |

## Verify first

| Claim | Why uncertain | How to verify | If false |
|---|---|---|---|
| 1. `android-17.0.0_r1` is CP2A.260605.016, SPL 2026-06-05 [R01 F1] | Read only in GrapheneOS and LineageOS trees | `git ls-remote --tags`; after sync read `build/release/flag_values/cp2a/RELEASE_PLATFORM_SECURITY_PATCH.textproto`; `getprop` on the baseline | Pin the newest `android-17.0.0_r*`; update 02 and 04 |
| 2. `android17-security-release`, `android-security-17.*` and a Q4-2026 branch exist and are timely; Q4 drop about December [R01 F2] | Google pages blocked; non-partner lag about 125 days | Weekly `git ls-remote`; source.android.com release notes | Pinned tag plus vendor and GrapheneOS cross-checks are the only patches; tell the founder; drop RB-1 |
| 3. Google's Pixel image and driver licence allows company flashing and OTA redistribution [R17 F1] | Licence text never read | Read the licence pages; give to counsel | At most 100 staff-owned devices; FW-1 open; founder picks written permission or another device |
| 4. Supervision framework and empty `config_systemSupervision` hooks are in AOSP itself and an overlay fills them; stock product makefiles list Browser2, CaptivePortalLogin, HTMLViewer [R01 F5, F6] | Seen only in GrapheneOS; 16.0.0_r3 for makefiles; overlayability [INFERRED] | grep `frameworks/base` and `build/make/target/product/*.mk`; set the overlay on Cuttlefish; `cmd role` | D24 falls back to Device Owner plus profile-owner APIs; escalate to 03; product stays default-deny |
| 5. Ubuntu 24.04 builds Android 17 (clean 1.5-3 h, incremental 3-15 min); `aosp_cf_x86_64_only_phone-aosp_current-userdebug` is valid; `/dev/kvm` works [R01 F4, F7] | Proven only via GrapheneOS and secondary sources; times [INFERRED] | Baseline build and Cuttlefish boot in the container | 22.04 image; a listed `aosp_cf_*` target; bare metal; resize host |
| 6. Monorepo at `vendor/zune` with `.find-ignore` is discovered by Soong; `repo init -m` accepts a subdirectory manifest | My design [INFERRED]; `.find-ignore` from memory | M1 spike | §4.3 fallbacks |
| 7. Vanadium prebuilt is obtainable, redistributable and accepted as WebView provider (D26) [R10 F10] | Not read from AOSP | Per 02 | Self-build Chromium; host at least 2 TB, 128 GB RAM; re-plan M3 |
| 8. Pixel QPR1 vendor and firmware skew (about 2026-09-15) blocks an r1-based image on updated phones [R17 §4.1, R18 F9] | Search summaries | Compare Google factory build IDs and bootloaders for `stallion` and `tegu`; `fastboot getvar` the anti-rollback variable (`anti` or `ap-ar-s`, unverified) | 04 backports or rebases early |
| 9. Pixel 10a and 9a relock with a custom AVB key on Android 17 [R17 F3, R18 F3] | AVB README read via a LineageOS mirror | Sacrificial-unit test in M2 | Stop; founder picks another device or accepts tamper risk |
| 10. rkpd attestation works for a non-GMS OS; `remote_provisioning.hostname` is settable [R10 F12] | Google service terms unknown | M2 attestation test | Station-recorded identity plus server checks; run a proxy |
| 11. adevtool covers Indian SKUs of `stallion` and `tegu` (configs list US SKUs) [R17] | Not checked | Run adevtool on an Indian-SKU unit | Add the SKU |
| 12. ap-south-2 offers the services 05 selects; infra about USD 0.5-0.9k a month plus 10-18k once [R10, memory] | Unchecked | AWS service list; quotes | DR with fewer services; founder re-approves spend |
| 13. Effort (R09 about 80 person-weeks of apps), cohort thresholds [R20], calendar | [INFERRED] | Velocity at M1 exit | Re-plan |

## Risks, open gates and out of scope

Risks:
1. Human-held gates (counsel, Google, entity) are slow and set the date of M7; open them at M0.
2. Pixel QPR1 skew can leave r1-based images unbootable on current vendor firmware (M2).
3. Gesture navigation needs a Quickstep-compatible launcher (D31; R03).
4. Non-partner patch lag about 125 days [R01 F2]; T&S and security staffing is open (A11).
5. Karnataka's under-16 social-media announcement or an IT Rules under-18 amendment could capture the messenger; confirm the first city [R19, R20].

Gate register (IDs are canonical for all sections):

| ID | Gate | Closed when |
|---|---|---|
| B-1 [GATE: before build] | AOSP hosts reachable; build host with KVM; founder approves spend and Pixels | PRE-01, 02 pass; approval logged |
| SP-1..7 [GATE: before staff pilot] | (1) data map, vendor register with verified terms, retention policy; (2) security baseline: encryption, access control, CERT-In and breach runbooks, 180-day logs, Indian NTP; (3) incident plan and drill; (4) 112 field test and triple-press SOS; (5) kill switches L1-L4; (6) service-unlock built or exception recorded; (7) staff consent terms from counsel [R18 G0, R19 G5, G8] | Evidence in `gates.md` |
| LEG-1..10 [GATE: before external family] | R19 §4.4: (1) counsel opinion (s.9(3), messenger classification, parent access vs interception); (2) Indian entity, India hosting, published contacts; (3) Rule-10 consent, withdrawal, erasure live; (4) parent contract, notices, custody, insurance; (5) security baseline, runbooks; (6) POCSO and takedown on-call drilled; (7) vendor contracts and written child-use confirmation from OpenAI and Anthropic; (8) 112 test, SOS shipped; (9) payments and DLT, or free pilot; (10) invite-only list, kill switch | Counsel or owner sign-off |
| EXT-1..7 [GATE: before external family] | (1) first city; (2) name clearance; (3) T&S and security staffing; (4) production key ceremony; (5) spare-phone exception; (6) support promise (3 years contractual [R10]); (7) Hindi parent-notice exception to D20 if counsel finds English-only notices fail DPDP ss.5(3), 6(3) | Founder decision logged |
| FW-1 [GATE: before charging] | Written Google firmware answer; also before device 101 and before OEM firmware in an OTA | Written answer or counsel opinion |
| PAY-1 [GATE: before charging] | Indian aggregator, e-mandate pre-debit notice, GST invoices, DLT, validated INR price (founding price INR 199 is below per-child cloud cost [R20]) | Finance and counsel sign-off |
| HW-1..4 (not a v1 gate) | R21 H1-H4, evaluated in M8 | M8 report |

Out of scope: own-hardware design and ODM orders; customer self-install; parent-side calling (D8); Hindi or Indic UI (D20); Snapdragon second device (D17); US and EU launches; Stage 2.


---

<!-- source: 02-os-image-and-product.md -->

# OS image: AOSP base, product definition, Settings, SystemUI, navigation, WebView

## Purpose and scope

How to build the Zune image from AOSP `android-17.0.0_r1` ("the tag"): manifest and patch discipline, default-deny product, overlays, telephony residue (112 only), ZuneSettings, SystemUI trim, gesture navigation, Vanadium WebView, radio and USB defaults, 16 KB cleanliness, variants, Cuttlefish CI.

**Stage 1** = every MUST below, simplest form. **Stage 2** = Settings gate patch (about 150 lines [R16 §6]) for on-device parent unlock of Wi-Fi advanced rows, Chromium origin allowlist, lockdown VPN, TalkBack and TTS, Bluetooth class allowlist.

Not covered here:
- ZuneGuardian, signed policy, Device-Owner provisioning, restrictions, bypass suite, Emergency screen, SOS: `03-lockdown-and-guardian.md`.
- Pixel device layers, AVB, signing, OTA, ZuneUpdater, patch pipeline: `04-device-signing-ota-release.md`.
- Device channel, NTP endpoints: `05-backend-and-parent-portal.md`.
- App internals, ZuneLauncher UI, ZuneSetup flow: `09-core-apps-and-design-system.md`; Reader and Videos: `08-content-videos-weather-reader.md`.
- Station: `10-delivery-operations-and-pilot.md`; legal: `11-compliance-and-privacy-engineering.md`; tests: `12-testing-qa-and-acceptance.md`; milestones and repo layout: `01-prerequisites-and-phases.md`.

Package namespace (provisional, name clearance): `app.zune.{guardian,launcher,settings,setup,updater,reader,videos,assistant,photos}`. Report evidence came from GrapheneOS and LineageOS trees, not Google's tag (see "Verify first").

## Decisions applied and reconciliations

| Decision | Effect |
|---|---|
| D22 | Full custom OS: ZuneLauncher, ZuneSettings, ZuneSetup are system components; product composed from `base_*`, never a layer on a stock phone product. |
| D14, D31 | ZuneSettings is minimal; Wi-Fi, mobile data, Bluetooth deep-link to stock screens. Bluetooth on, NFC off, USB file transfer off, gesture navigation, no on-screen buttons. |
| D19, D28 | No dialer UI, SMS, Contacts, Messaging. Telephony stack, CellBroadcastReceiver and a hidden in-call UI stay for 112 (resolves R03 Q1). |
| D20, D18 | English only: `en_IN`, fallback `en_US`. Indic fonts kept so Indian cell-broadcast alerts render. |
| D24 | ZuneGuardian is Device Owner and supervision-role holder: stock Supervision page hidden; sole setter of `DISALLOW_FACTORY_RESET`. |
| D26 | Vanadium only (stock `external/chromium-webview` not shipped); only Reader and Videos may create a WebView (resolves R03 Q2, R01 Decision 7). |
| D30 | CaptivePortalLogin removed; Settings buttons patched out; explainer screen. |
| D17, D21 | Pixel 10a (`stallion`), 9a (`tegu`) plus Cuttlefish CI; device layers: `04`. |

**Reconciliations applied**

| Report claim | Change |
|---|---|
| R03: three-button nav, `config_hasRecents=false`, ZuneHome overrides Launcher3QuickStep | Reversed by D31: Launcher3QuickStep stays as recents provider (§7). |
| R03: keep SettingsIntelligence, TalkBack, AccessibilityMenu, MtpService, CalendarProvider, Tag | SettingsIntelligence removable [R16 F7]; TalkBack not in AOSP [R16 F10]; rest removed. |
| R03/R16: lunch alias `cur`; en-US/es-US; 911, WEA | `cur` is GrapheneOS-only: use `aosp_current`. Locale per D20. 911 becomes 112; WEA becomes India cell broadcast. |
| R16: zero Java patches in Settings; `config_show_wifi_settings=false` hides Wi-Fi preferences | Both refuted [R16 F2, F8]: patches P-SET-1..3 (R16 decision 9 default). |
| R01: "under 30 forks" | Unsupported figure; Stage 1 cap is 5 forks. |

## Requirements

**Base and discipline**
- **OS-01 MUST** Pin the tag by commit SHA: `zune/os/manifest/pins.xml` (`repo manifest -r`) is committed and CI fails on any difference. No floating branch.
- **OS-02 MUST** Complete V1 to V3 first; record results in `zune/os/docs/BASELINE.md`.
- **OS-03 MUST** At most 5 forked AOSP repos in Stage 1. Every divergence is a registered patch (§1) on the tag: no merge commits, one change per commit, trailer `Zune-Patch: <ID>`, `git range-diff` on every rebase.
- **OS-04 MUST** System, system_ext and product partitions inherit only `base_system.mk`, `base_system_ext.mk`, `base_product.mk` (if present) and Zune files; never `aosp_product.mk`, `generic_system.mk`, `handheld_*`, `telephony_*`, `media_*`. The vendor partition (04) may inherit `*_vendor.mk`.
- **OS-05 MUST** `zune/os/tools/image_diff.py` gates every build: APKs, APEXes, privileged apps, `INTERNET` holders, exported components and WebView-referencing packages equal the reviewed baseline in `vendor/zune/allowlist/`.
- **OS-06 MUST** No REMOVE-row package (§3) exists in any partition (OsuLogin excepted, inert).
- **OS-07 MUST** Static scan of all APKs (APEX-contained included) finds no activity filter with `VIEW` + `BROWSABLE` + `http`/`https`/`ftp`, and no `WEB_SEARCH` handler.
- **OS-08 MUST** All overlays are RRO modules (`PRODUCT_ENFORCE_RRO_TARGETS := *`); keys an RRO cannot override (V3) are listed in `BASELINE.md`.

**Telephony and locale**
- **OS-09 MUST** Keep Telecom, TeleService, TelephonyProvider, CarrierConfig, CellBroadcastReceiver and a hidden in-call UI; no Dialer launcher, Messaging, Contacts, Stk, ONS; no SMS role holder.
- **OS-10 MUST** 112 can be placed from the Emergency screen (03) and lock screen, no other number can; a cell-broadcast test alert displays.
- **OS-11 MUST** `PRODUCT_LOCALES := en_IN en_US`; default font families incl. Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi, Odia retained.

**Settings and SystemUI**
- **OS-12 MUST** ZuneSettings is the only handler of `android.settings.SETTINGS`; 10 rows (§6); touch targets at least 56 dp (D23).
- **OS-13 MUST** Stock Settings is default-deny: a generated `component-override` disables every component outside `settings_allowlist.txt` (at most 45 activities), regenerated every build.
- **OS-14 MUST** Nobody sets `DISALLOW_CONFIG_WIFI` or `DISALLOW_CONFIG_MOBILE_NETWORKS` (they blank the pages [R16 F3]); CI greps sources and a device test reads `dumpsys user`.
- **OS-15 MUST** Developer options unreachable: no component, `development_settings_enabled=0`, build-number row inert.
- **OS-16 MUST** Wi-Fi, mobile data and Bluetooth pages are stock screens by deep link, unchanged except P-SET-1..3.
- **OS-17 MUST** ZuneSettings catches every `android.settings.*` action sent by SystemUI, framework or Zune apps that no allowlisted activity serves; no `ActivityNotFoundException` in the crawl (AT-04).
- **OS-18 MUST** Own plain-text licence viewer; stock licence and manual activities disabled (HTMLViewer hard-coded [R16 F8]).
- **OS-19 MUST** Reset only via Parent area -> `ParentGate.confirm()` -> Guardian wipe; Guardian is the only setter of `DISALLOW_FACTORY_RESET` (no `MANAGE_USERS` fallback) [R16 F9]; spike on Cuttlefish in week 1. After a wipe the device boots to ZuneSetup and needs a new pairing code; a recovery-mode wipe cannot be blocked (inert until re-paired, 03).
- **OS-20 MUST** Captive portal: explainer activity handles the sign-in action; P-SET-2 applied (D30).
- **OS-21 SHOULD** Wi-Fi password share QR hidden (P-SET-3).
- **OS-22 MUST** SystemUI: six tiles, three-item power menu, lock-screen shortcuts flashlight and camera.

**Navigation**
- **OS-23 MUST** Gesture navigation is default, not child-changeable, with no button bar (the thin gesture handle is allowed); ZuneSetup shows a first-boot gesture tutorial (`09`).
- **OS-24 MUST** HOME resolves to `app.zune.launcher`: Guardian sets persistent preferred activity and HOME role.
- **OS-25 MUST** Build Path A (§7); it passes NAV-1..8 (AT-06) by M3 exit or Path B replaces it. Path C forbidden in Stage 1. Three-button only by founder decision.

**WebView**
- **OS-26 MUST** Vanadium is the only entry in `config_webview_packages.xml`; the Vanadium browser APK never ships.
- **OS-27 MUST** P-FWK-1: only `app.zune.reader` and `app.zune.videos` (package plus cert digest, from a verified `/system_ext` file) can create a WebView.
- **OS-28 MUST** WebView updates ship independent of full OTA, owned by a named `WebView owner` (`zune/os/OWNERS`); SLA: each Vanadium stable within 30 days, High/Critical within 14.
- **OS-29 SHOULD** Signed policy carries `webview_min_version`; Guardian disables Videos Tier 2 below it (03, 08).

**Radios, USB, native code, build**
- **OS-30 MUST** Bluetooth on at first boot, pairing allowed, OPP sharing blocked.
- **OS-31 MUST** NFC off and unreachable: feature masked, `Tag` removed, restriction asserted.
- **OS-32 MUST** USB file transfer off: `MtpService` removed, restriction asserted, charge-only default, adb off in `user`.
- **OS-33 MUST** All native code (image, APKs, Vanadium) 16 KB-clean.
- **OS-34 MUST** Shipped images: `user`, `aosp_current`, release keys (04). `userdebug` only for CI and dev phones; never `eng` or `trunk_staging`.
- **OS-35 MUST** CI per §10 blocks merges. **OS-36 MUST** No GMS, Google services, analytics or ad SDKs.

## Design and build instructions

### 1. Repository, manifest, patch stack

```
zune/os/manifest/  upstream-android-17.0.0_r1.xml (Google default.xml at the tag)  zune.xml  pins.xml
zune/os/patches/   REGISTER.md  <repo>/*.patch (format-patch backup of each stack)
zune/os/device/zune/products/  AndroidProducts.mk zune_kids_cf.mk   (stallion, tegu: 04)
zune/os/vendor/zune/  config/ allowlist/ overlay/ sysconfig/ sepolicy/ release/ webview/ apps/prebuilt/
zune/apps/{guardian,launcher,settings,setup,updater} -> <aosp>/packages/apps/Zune*
zune/os/tools/  image_diff.py settings_gen.py check_elf_alignment.sh nav_suite/   zune/os/ci/  Dockerfile
```
`zune.xml` includes the upstream file, then per fork `<remove-project name="platform/frameworks/base"/>` plus `<project path="frameworks/base" name="platform_frameworks_base" remote="zune" revision="refs/heads/zune/android-17.0.0_r1"/>`. Forks live under org `getplx` (names are proposals). The monorepo checks out at `<aosp>/zune`; `<linkfile>` exposes `device/zune`, `vendor/zune`, `packages/apps/Zune*` (V11).

| ID | Repo | Change | Lines |
|---|---|---|---|
| P-FWK-1 | `frameworks/base` | WebView caller allowlist (§8) | 40 |
| P-FWK-2 | `frameworks/base` | IntentFirewall also reads `/system_ext/etc/ifw` (owner 03) | 30 |
| P-SET-1 | `packages/apps/Settings` | Hide row `configure_network_settings`; null-guard `setAdditionalSettingsSummaries` [R16 F2] | 20 |
| P-SET-2 | same | Hide "Sign in", "venue website" (`WifiDetailPreferenceController2`), carrier setup URL launch [R16 F8] | 30 |
| P-SET-3 | same | Hide Wi-Fi share QR | 15 |
| P-WIFI-1 | `packages/modules/Wifi` | Drop OsuLogin from APEX (conditional, V4) | 5 |
| P-LAU-1 | `packages/apps/Launcher3` | Strip overview actions/search if RRO cannot (conditional) | 100 |
| P-REL-1 | `build/release` | Flag overrides if a vendor map cannot (conditional, V2) | 20 |

Budgets are planning limits. Start with two forks (`frameworks/base`, `Settings`). Rebase once onto the Q4-2026 drop (about December 2026, unverified), freeze before the staff pilot; monthly ingest: `04`.

### 2. Default-deny product

`vendor/zune/config/zune_system.mk` (draft):
```make
PRODUCT_NO_DYNAMIC_SYSTEM_UPDATE := true     # parse-time: before base_system.mk
PRODUCT_ENFORCE_RRO_TARGETS := *
$(call inherit-product, $(SRC_TARGET_DIR)/product/base_system.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base_system_ext.mk)
PRODUCT_LOCALES := en_IN en_US
PRODUCT_PACKAGES += $(shell cat vendor/zune/allowlist/product-packages.txt)
# plumbing copied from generic_system.mk (update_engine, update_verifier, otapreopt_script, zygote rc ...):
# diff against upstream on every rebase
PRODUCT_RELEASE_CONFIG_MAPS += $(wildcard vendor/zune/release/release_config_map.textproto)
```
`zune_base.mk` sets `ZUNE_BRAND` (one variable; name clearance pending) and `PRODUCT_SOONG_NAMESPACES += vendor/zune`. Products: `zune_kids_cf` (x86_64; mirror `aosp_cf_x86_64_only_phone` without its `generic_system`/`handheld`/`telephony` inherits), `zune_kids_stallion`, `zune_kids_tegu`. `product-packages.txt` (seeded from the KEEP and ADD rows of §3) is the input; `allowlist/image-apps.txt` is the reviewed output that `image_diff.py` compares with `installed-files.txt`, `apex_info.xml` and `aapt2 dump badging`, catching transitive additions. Ordinary apps ship as pinned `android_app_import` prebuilts (SHA-256 in `apps/prebuilt/PINS`; `arm64-v8a` on devices, `x86_64` for Cuttlefish); the five OS-coupled apps build in-tree (V12).

### 3. Package keep/remove table

| Package(s) | Verdict | Condition |
|---|---|---|
| `android`, `SystemUI`, `SettingsProvider`, `Settings` | KEEP | Hard references; Settings is `prevent-disable` [R03 F5, R16 F4]; default-deny (§6). |
| `Launcher3QuickStep` | KEEP, never HOME | Recents and launcher-proxy provider (§7). |
| All Mainline APEXes | KEEP | Not prunable [R03 F4]; `RELEASE_WEBAPP_MODULE=false` drops `com.android.webapp` (V2). |
| `Telecom`, `TeleService`, `TelephonyProvider`, `CarrierConfig`, `ContactsProvider`, `BlockedNumberProvider`, `CellBroadcastReceiver` | KEEP | 112, APNs, alerts (MCC 404/405 [R20]). |
| In-call UI (`Dialer` or successor) | KEEP InCallService and emergency activities only | Launcher and dial-pad activities disabled (V7). |
| `Messaging`, `Contacts`, `Stk`, `ONS`, `ImsServiceEntitlement`, `EmergencyInfo` | REMOVE | D19/D28; Stk can request browser launches [M]; re-add ImsServiceEntitlement only if the 112 field test needs it. |
| `Browser2`, `QuickSearchBox`, `BookmarkProvider`, `PartnerBookmarksProvider`, `HTMLViewer`, `CaptivePortalLogin`, `CarrierDefaultApp`, `CertInstaller`, `SettingsIntelligence` | REMOVE | Browser and WebView surfaces [R04 F1]; CertInstaller only after P-SET-1; SettingsIntelligence removal ends Settings search. |
| `OsuLogin` (in `com.android.wifi`) | KEEP, inert | Not removable by makefile; WebView gate blocks it; P-WIFI-1 if V4 allows. |
| `PrintSpooler`, `BuiltInPrintService`, `PrintRecommendationService`, `Traceur`, `EasterEgg`, `DeviceAsWebcam`, `MusicFX`, `BluetoothMidiService`, `SharedStorageBackup`, `PrivateSpace`, `AvatarPicker`, `PhotoTable`, `BasicDreams`, `LiveWallpapersPicker`, `ThemePicker`, `ThemesStub`, `WallpaperCropper`, `CredentialManager`, `Tag`, `MtpService`, `DownloadProviderUi`, `CalendarProvider`, `AccessibilityMenu`, `DynamicSystemInstallationService`, `Camera2`, `Gallery2`, `Music`, `Calendar`, `DeskClock` | REMOVE | Mask print and credentials features [R03 F7]. Re-add only what breaks boot or a kept screen. |
| `KeyChain`, `FusedLocation`, `InputDevices`, `WallpaperBackup`, `PacProcessor`, `ProxyHandler`, `VpnDialogs`, `DocumentsUI`, `ExternalStorageProvider`, `DownloadProvider`, `UserDictionaryProvider`, `LatinIME`, `CompanionDeviceManager`, `cameraserver`, `CameraExtensionsProxy`, `PackageInstaller`, `PermissionController` | KEEP | Plumbing; launcher entries disabled; PackageInstaller neutered by restrictions (03). |
| `ManagedProvisioning` | KEEP until 03 fixes the Device-Owner route | Then remove if unused. |
| `Provision` | REPLACE with ZuneSetup | `overrides: ["Provision"]`; sets provisioned flags [R03 F8]. |
| TalkBack, TTS, Vanadium browser | ABSENT | TalkBack and TTS are Stage 2 [R16 F10]. |

### 4. Overlays (RRO modules)

| Overlay (target) | Values |
|---|---|
| `ZuneFrameworkOverlay` (`android`) | `config_navBarInteractionMode=2`; `config_defaultBrowser=""`; `config_defaultAssistant=app.zune.assistant`; `config_systemGallery=app.zune.photos`; `config_enableSafetyCenter=false`; supervision keys `config_systemSupervision`, `config_allowedSupervisionRolePackages`, `config_defaultSupervisionProfileOwnerComponent` = `app.zune.guardian` (03; V3); `config_ntpServers` per 05 (never guess hostnames); `xml/config_webview_packages.xml`. Never blank `config_recentsComponent`. |
| `ZuneSystemUIOverlay` (`com.android.systemui`) | `quick_settings_tiles_default` and `_stock` = `internet,bt,airplane,flashlight,rotation,saver` (child cannot edit); `config_globalActionsList` = `emergency,power,restart`; keyguard flashlight and camera (ids: V10). Shade gear reaches ZuneSettings via the router. |
| `ZuneSettingsOverlay` (`com.android.settings`) | Every `config_show_*` knob in [R16 F2, §5] false; `help_url_*` empty (CI check). |
| `ZuneProviderOverlay` (`com.android.providers.settings`) | `def_device_provisioned=false`, `def_user_setup_complete=false`, Bluetooth on, NFC off (V13). |
| `ZuneLauncher3Overlay` (`com.android.launcher3`) | Overview actions, search, widgets, wallpaper entry points off. |
| `ZuneNetworkStackOverlay` | Captive-portal probe URLs to Zune endpoints (05). |

### 5. Telephony residue (D28)

Keep the stack; enforce deny-all in policy, not by deleting code: `DISALLOW_OUTGOING_CALLS` and `DISALLOW_SMS` (emergency calls stay permitted, V7), no SMS or dialer role holder, inbound handling in `03`. Do not mask `android.hardware.telephony.messaging` before the 112 and cell-broadcast tests pass; carrier field tests: `12`.

### 6. ZuneSettings and the engine room

ZuneSettings: Compose, platform-signed, privileged, `system_current`, non-exported pages. Ten rows (R16's Language row dropped by D20):
```
Wi-Fi & mobile data [stock: NETWORK_PROVIDER_SETTINGS; mobile NETWORK_OPERATOR_SETTINGS, DATA_USAGE_SETTINGS;
                     airplane AIRPLANE_MODE_SETTINGS]   | Bluetooth [stock BLUETOOTH_SETTINGS] | Sound
Display (timeout capped by policy) | Accessibility (text/display size, bold, contrast, colours, animations,
mono audio, captions, flash alerts) | Battery | Storage | Emergency (info card from policy, alert history)
About (name, model, OS, build, update status, Legal & licences, regulatory info) | Parent area [PIN]: Reset
Absent: date/time (forced), search, accounts, apps, notifications, security, developer, language.
```
Regulatory info opens the stock screen if present, else shows the OEM label data from the stock image; never author label text [R16 row 35]. Parent-controlled values (timeout cap, volume cap, roaming, data warning, location, airplane lock, SOS gesture, time zone, default `Asia/Kolkata`) arrive via ZuneGuardian's bound service; ZuneSettings never uses the network. Locked rows show "Ask a parent" and call `ParentGate.confirm(reason): Boolean` (Guardian API, 03); without Guardian or PIN the Parent area stays locked.

Engine room: `settings_gen.py` reads the built Settings manifest (`aapt2 dump xmltree`) and `settings_allowlist.txt` (seed [R16 §5]: Wi-Fi/Internet 14, mobile and data 8, panel 1, Bluetooth 7, credential/supervision 6, SUW internet 1) and emits `/system_ext/etc/sysconfig/zune-settings-overrides.xml`, the router filters and a diff of new upstream `config_*` bools:
```xml
<config><component-override package="com.android.settings">
  <component class="com.android.settings.homepage.SettingsHomepageActivity" enabled="false"/> <!-- + all others -->
</component-override></config>
```
Settings re-enables some components at runtime [R16 F2]; Guardian re-asserts (03). Wi-Fi advanced fields (proxy, static IP/DNS) stay visible in Stage 1 [R16 row 3]. Captive portal: ZuneSettings handles `android.net.conn.CAPTIVE_PORTAL` (V14) and shows "This Wi-Fi needs a sign-in page. Ask a parent to use a phone hotspot."

### 7. Gesture navigation (D31)

SystemUI gesture mode relies on a launcher-proxy service in the package named by `config_recentsComponentName` (`QUICKSTEP_SERVICE`, `LauncherProxyService` in 17); a home app without one fits only three-button mode [R03 F5].

| Path | Architecture | Verdict |
|---|---|---|
| **A (build first)** | Stock `Launcher3QuickStep` stays as recents provider with RRO trim; `ZuneLauncher` is a plain Compose HOME app. Launcher3's `OverviewComponentObserver` falls back to `RecentsActivity` when another package is default home, as third-party launchers rely on [M]. | Zero fork if RRO suffices; else P-LAU-1. |
| **B (fallback)** | Fork `packages/apps/Launcher3`, strip workspace, all-apps, widgets; ZuneLauncher is the single Launcher3QuickStep-derived package. | Larger fork, churn each drop; estimate in M3 spike. |
| **C** | Own launcher proxy, recents animation, input consumers. | Forbidden in Stage 1: hidden AIDL renamed between releases, no CTS coverage. |
| **D** | Three-button, ZuneLauncher only [R03 F5]. | Violates D31; founder decision only. |

Sequence: Guardian (Device Owner) calls `addPersistentPreferredActivity` for HOME and sets the HOME role to ZuneLauncher; SystemUI binds the Launcher3 proxy and swipe-up-and-hold opens `RecentsActivity`. Risks: overview chrome is Launcher3's (little theming); overview actions and search must be off; Launcher3's HOME activity must stay enabled or `OverviewComponentObserver` fails [M]; each rebase touches Quickstep. If A fails and B is not passing at M3 exit, stop and escalate [GATE: before staff pilot].

### 8. WebView (D26)

Provisioning: obtain the Vanadium WebView APK(s) (provider plus any Trichrome library its manifest requires), verify the signing cert against `vendor/zune/webview/CERT.sha256`, check in under `apps/prebuilt/`, import as privileged system `android_app_import` (arm64-v8a), whitelist:
```xml
<webviewproviders><webviewprovider description="Vanadium WebView" packageName="app.vanadium.webview"
  availableByDefault="true"><signature>BASE64_CERT</signature></webviewprovider></webviewproviders>
```
P-FWK-1, in `WebViewUpdateService.waitForAndGetProvider`, which already reads the caller UID [R04 F3]:
```java
if (!ZuneWebViewCallers.allows(Binder.getCallingUid())) {  // /system_ext/etc/zune/webview_callers.xml
    Slog.w(TAG, "WebView denied");
    return new WebViewProviderResponse(null, WebViewFactory.LIBLOAD_FAILED_LISTING_WEBVIEW_PACKAGES);
}
```
Updates: ZuneUpdater (04) delivers signature-matched Vanadium APKs independent of OTA, staged (policy floor: OS-29). Owner weekly: watch upstream, re-verify cert, run AT-07, ship within SLA. Reader declares no `INTERNET`; Videos is proxied (08, 03).

### 9. Radios, USB, 16 KB

| Item | Mechanism |
|---|---|
| Bluetooth on | Provider default on; Guardian asserts `DISALLOW_BLUETOOTH_SHARING`; never `DISALLOW_CONFIG_BLUETOOTH`; consider disabling OPP/PBAP/MAP profile properties (V13). |
| NFC off | `<unavailable-feature>` for `android.hardware.nfc*` in `zune_features.xml`, `Tag` removed, no tile, NFC restriction asserted (V13). |
| USB file transfer off | `MtpService` removed, `DISALLOW_USB_FILE_TRANSFER` and `DISALLOW_MOUNT_PHYSICAL_MEDIA`, charge-only default, `ro.adb.secure=1`. USB host feature not masked in Stage 1 (USB-C audio). |
| 16 KB | NDK r28+, `zipalign -P 16`, ELF LOAD alignment 0x4000; `check_elf_alignment.sh` scans partitions, APKs, APEXes, Vanadium. 4 KB kernel unless 04 decides otherwise [R01 F6]. |

### 10. Build, variants, CI

```
repo init -u https://github.com/getplx/Zune -b research/android-kids-foundation \
  -m zune/os/manifest/zune.xml --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle
repo sync -c -j8 --no-tags
source build/envsetup.sh && lunch zune_kids_cf-aosp_current-userdebug && m -j"$(nproc)"
# M1 vanilla: repo init -u https://android.googlesource.com/platform/manifest -b refs/tags/android-17.0.0_r1
```
Release config is `aosp_current` (alias of `cp2a`, V2); flag overrides live in `vendor/zune/release/`; SPL bumps only via 04's pipeline. Use the working branch until `main` exists [HANDOFF §2]. Host: 32 vCPU, 128 GB RAM, 1 TB NVMe, Ubuntu 24.04 container, `/dev/kvm` [R01 F4].

| Lunch target | Use |
|---|---|
| `aosp_cf_x86_64_only_phone-aosp_current-userdebug` | M1 vanilla baseline; record sync size, build time. |
| `zune_kids_cf-aosp_current-userdebug` | Every merge request: boot, `image_diff`, Settings crawl, NAV suite, WebView test. |
| `zune_kids_cf-aosp_current-user` | Nightly static gates; user-vs-userdebug file diff equals the debug allowlist. |
| `sdk_phone16k_x86_64-aosp_current-userdebug` (name per goldfish tree) | Nightly 16 KB boot, install Zune APKs, smoke. |
| `zune_kids_stallion-...`, `zune_kids_tegu-...` (`user`, `userdebug`) | Pixel 10a, 9a (04). |

## Acceptance criteria and tests

- **AT-01** `repo manifest -r` equals `zune/os/manifest/pins.xml`; `get_build_var BUILD_ID` matches `BASELINE.md`.
- **AT-02** `image_diff.py` passes on `zune_kids_cf` user and userdebug; adding `Browser2` makes it fail.
- **AT-03** On Cuttlefish `cmd package query-activities --brief -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d https://example.com` (also `http://`, `ftp://`) prints nothing; HOME `resolve-activity` returns `app.zune.launcher`.
- **AT-04** Crawl: `am start -a android.settings.SETTINGS` opens ZuneSettings; tapping every row of ZuneSettings, shade, quick settings, power menu and lock screen causes no crash or `ActivityNotFoundException`; the Developer-options action opens nothing; `dumpsys user` lacks `no_config_wifi` and `no_config_mobile_networks`; a fake captive Wi-Fi shows the explainer only.
- **AT-05** On a Pixel, stock pages: Wi-Fi join (password, QR, hidden network), mobile-data toggle, Bluetooth headset pairing work; Wi-Fi preferences row absent.
- **AT-06** NAV-1..8, scripted plus 20 minutes on a Pixel: swipe-up goes home; swipe-up-and-hold opens overview; card swipe dismisses a task; edge swipe goes back; rotation keeps gestures; no button bar; HOME survives reboot and Guardian restart.
- **AT-07** `dumpsys webviewupdate` lists only Vanadium; Reader and Videos create a WebView; a platform-signed test APK not on the list cannot, and the denial is logged; no Vanadium browser package.
- **AT-08** Pixel, shipping image: fresh provisioning leaves Bluetooth on; host `lsusb -v` shows no MTP/PTP interface; `pm list features` has no `android.hardware.nfc`; OPP send rejected.
- **AT-09** `check_elf_alignment.sh` zero failures; 16 KB goldfish boots (`getconf PAGE_SIZE` = 16384), Zune smoke passes.
- **AT-10** In emergency-number test mode (V7) a call from the Emergency screen reaches setup and shows in-call UI; other numbers are refused; no dialer icon; a cell-broadcast test alert renders, Hindi and Tamil samples included. Live 112 tests only as agreed with the carrier (`12`).
- **AT-11** `ro.build.type=user`, `ro.debuggable=0`, `ro.build.tags=release-keys`; no `com.google.android.gms`, `com.android.vending`.
- **AT-12** Re-applying each patch stack on the pinned tag gives an empty `git range-diff`.

## Verify first

Do V1 to V3 before anything else.

| # | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| V1 | Tag exists; build CP2A.260605.016; SPL 2026-06-05; AOSP reachable; `android17-security-release` or `android-security-17.*` exist | Google hosts were blocked [R01 F1-F2] | `git ls-remote` tag and branches; `get_build_var BUILD_ID PLATFORM_SECURITY_PATCH` | Re-pin to newest tag; no security branch means pin plus vendor patches (04). |
| V2 | `aosp_current` = `cp2a`; lunch is `product-release-variant`; vendor release-config map overrides `RELEASE_WEBAPP_MODULE`, SPL, supervision flags | GrapheneOS tree; override inferred [R03 F3] | Read `build/release/`; build with a map | Use real names; P-REL-1. |
| V3 | `base_product.mk` exists; contents of `handheld_*`, `telephony_*`, `media_*`; every REMOVE row removable; RRO overrides supervision keys and the WebView xml | Stock 17 not read [R01 F6, R03 F1] | Read files; build `zune_kids_cf`; boot; `image_diff` | `overrides:` stubs [R03 F2]; `PRODUCT_PACKAGE_OVERLAYS`; one `build/make` fork at most. |
| V4 | OsuLogin neutralisable by override or P-WIFI-1 | APEX-contained [R04 F1] | Inspect `com.android.wifi` | Rely on P-FWK-1 and 03's network deny. |
| V5 | Stock Quickstep with another default home gives working gestures; names `config_recentsComponentName`, `QUICKSTEP_SERVICE`, `LauncherProxyService`; Launcher3 HOME must stay enabled | From memory [R03 F5, M] | Read `OverviewComponentObserver`, `TouchInteractionService`, SystemUI; NAV suite with a stub ZuneLauncher in M1 | Path B; then §7 gate. |
| V6 | `config_navBarInteractionMode=2` selects gestures; navigation-mode page unreachable | Inferred | `settings get secure navigation_mode` | Guardian sets it. |
| V7 | An in-call UI exists at the tag; `DISALLOW_OUTGOING_CALLS` permits emergency calls; `cmd phone emergency-number-test-mode` works; CB config covers MCC 404/405 | Dialer in 17 unverified [R03 §3, I] | Inspect manifest; Cuttlefish modem simulator; Pixel | Guardian ships an `InCallService` (03). |
| V8 | `waitForAndGetProvider()` is the choke point; zygote preload does not bypass it; Vanadium needs a Trichrome library | GrapheneOS source [R04 F3, I] | Read `WebViewFactory`, `WebViewUpdateServiceImpl`; AT-07 | Gate in `WebViewFactory.getProvider()` plus CI scan that only Reader and Videos reference `android.webkit.WebView`. |
| V9 | Vanadium binaries obtainable, redistributable (GPL-2.0-only patches), arm64, 16 KB-aligned, Android 17-compatible | Licence and distribution unread [R04 F2] | Read repo, licence, releases; ask GrapheneOS; alignment scan | Build Vanadium (or LineageOS WebView patches) on a dedicated host [GATE: before build]. |
| V10 | Settings counts, `config_show_*` effects, Catalyst behaviour, disabled-host behaviour; SystemUI ids | GrapheneOS/LineageOS only [R16] | Read the tag; tap-every-row crawl | Widen allowlist or patches. |
| V11 | `repo init -m <subdir>` and directory `<linkfile>` work with Soong, Kati, `AndroidProducts.mk` discovery | Unverified | M1: link stub `device/zune`, run `lunch` | Separate repos split by CI. |
| V12 | Compose builds under Soong | Unverified | M1 spike | Gradle build, `android_app_import` re-signed with platform key (`09`). |
| V13 | NFC mask, restriction constants, Bluetooth profile properties, provider default keys, USB default work on the Pixel vendor image | Inferred [R03 F7, R16 row 13] | AT-08 on both Pixels | Guardian assertions. |
| V14 | `android.net.conn.CAPTIVE_PORTAL` is the sign-in action; no crash loop without CaptivePortalLogin | Memory | Fake captive network on Cuttlefish | Set `captive_portal_mode`; keep explainer. |
| V15 | Host sizing, Ubuntu 24.04, 1.5-3 h clean build, Cuttlefish product names | Estimates [R01 F4] | M1 baseline build | Resize; keep a 22.04 image. |

## Risks, open gates and out of scope

- **Gesture navigation** may fail with a non-Quickstep home (V5). [GATE: before staff pilot] Path A or B passes AT-06, or the founder accepts three-button (a D31 deviation).
- **WebView** is a permanent Chromium update burden. [GATE: before build] V9 decides consume vs build. [GATE: before staff pilot] named owner and a demonstrated off-OTA update. [GATE: before charging] SLA met for two consecutive Chromium releases.
- **Security patching** of the tag and Mainline is the central risk (04). [GATE: before external family] pipeline running.
- **Patch drift**: Catalyst screens grew 27 to 237 in 18 months [R16]; Quickstep churns each drop; re-estimate after M3.
- **112 without a stock dialer** (V7). [GATE: before staff pilot] 112 test passes on both Pixels (`12`).
- **Name clearance**: renaming `app.zune.*` costs a reflash. [GATE: before staff pilot] settle it.
- **Counsel** [GATE: before external family]: GPL-2.0 source duties (Vanadium, kernels); regulatory-label rules for India (unknown; R16's FCC and CVAA material is US, secondary); accessibility duties without TalkBack and TTS.

Out of scope: device layer, AVB, OTA (04); Guardian, policy, restrictions, bypass suite (03); Stage 2 items; own hardware.


---

<!-- source: 03-lockdown-and-guardian.md -->

# No-browser / no-YouTube enforcement and the ZuneGuardian (Device Owner + supervision role)

## Purpose and scope

Specifies the layer that makes "no browser app, no way to type a URL, no route to youtube.com" true and gives the parent full control of allowing or disabling anything (D24): ZuneGuardian (`app.zune.guardian`) as Device Owner and supervision-role holder, with signed policy, parent PIN, reset and recovery, the bypass-vector suite and the 112-only path (D28).

**Stage 1** = every MUST, proven on Cuttlefish and both Pixels by M3 exit and complete before the staff pilot. **Stage 2** = lockdown VPN (R04 "Zune Guard"), Chromium allowlist patch, per-UID firewall chains, attempted-link sink, Advanced Protection hooks, platform Supervision PIN, hard attestation gating.

Not covered: image, overlays, ZuneSettings, navigation, WebView, P-FWK-1, P-SET-* (`02-os-image-and-product.md`); AVB, keys, OTA (`04-device-signing-ota-release.md`); policy service, channel protocol, pairing API, portal (`05-backend-and-parent-portal.md`); contacts, calls (`06-communication.md`); assistant moderation (`07-ai-assistant.md`); Videos, Reader (`08-content-videos-weather-reader.md`); ZuneSetup, launcher screens (`09-core-apps-and-design-system.md`); station, hand-over (`10-delivery-operations-and-pilot.md`); DPDP duties (`11-compliance-and-privacy-engineering.md`); suite execution, gates (`12-testing-qa-and-acceptance.md`).

Evidence came from GrapheneOS and LineageOS trees, not Google's `android-17.0.0_r1` [HANDOFF §2]; see Verify first (VG-n).

## Decisions applied and reconciliations

| Decision / report | Effect |
|---|---|
| D24, R05 option (c) | Guardian is Device Owner and role holder. R05's `ZunePolicyService` folds into Guardian (01); apps use Binder. |
| D22 | The Device-Owner layer ships inside our image; R05's DO-on-stock options are dropped. |
| D19, D28 vs R12 | Dropped: call allowlists, SMS vault, ZunePhone, `ZuneAllowlistFilter`, FDN hooks, MVNE, STIR/SHAKEN, 911/988, `DISALLOW_CONFIG_MOBILE_NETWORKS`. Kept: signed monotonic policy, deny-by-default, never fail open, emergency exemption, `ACTION_DIAL_EMERGENCY` ownership, HFP and USB-modem fuzz cases, AOSP-only callback window. |
| D28, R19, R20 | Ordinary Indian SIMs carry voice and SMS, so inbound calls and SMS must be rejected (LOCK-33). |
| R19 vs R16 #7 | Triple-press SOS is on by default with a cancel countdown (R16 defaulted it off). |
| D23, D27 | Bands 7-9, 10-12, 13-14 (R05: 6-8). Parent visibility, child notice and retention live in 05, 06, 07, 11. |
| D30, D14 | Captive portal unsupported. Never set `DISALLOW_CONFIG_WIFI`, `_MOBILE_NETWORKS`, `_BLUETOOTH` [R16 F3, 02 OS-14]; parent "network off" is forced airplane mode. |
| D25, D26 | WebView only in Reader and Videos (R04 option C); Tier 2 off by default; Chromium fork is Stage 2. |
| D31 | Bluetooth on, NFC off, USB file transfer off; location from parent-set places only (replaces R05 opt-in tracking). |
| R05 4.8, R16 F9 | Guardian owns the socket (R13's ZuneComms dropped). Platform `PackageUsagePolicy` is flag-off in `cp2a`, so Guardian suspends apps itself. PIN is Zune-owned; no platform supervising user; Guardian is sole setter of `DISALLOW_FACTORY_RESET`. |
| R04, R05 | "Zune Guard" is ZuneGuardian. R05's SMS SOS fallback gives way to the device channel; hosting is India (D18). |

## Requirements

**Provisioning, role, persistence**
- **LOCK-01 MUST** ZuneSetup makes `app.zune.guardian` Device Owner of user 0 before `user_setup_complete=1`; on failure setup shows Retry and "Erase and restart", never a half-provisioned device.
- **LOCK-02 MUST** Guardian is the only holder of the supervision roles (`ROLE_SUPERVISION` included); `pm list users` shows one user (no `profile.supervising`) [R16 F9].
- **LOCK-03 MUST** Guardian is sole setter of every restriction in §4.3 (`dumpsys user`: no base or `SUPERVISION_SYSTEM_ENTITY` source) and never sets the "never" list.
- **LOCK-04 MUST** Guardian is a persistent `/system_ext` priv-app in `allow-in-power-save` with `setUserControlDisabledPackages` and `DISALLOW_UNINSTALL_APPS`; after a kill it restarts in 5 s and re-asserts everything in 10 s.
- **LOCK-05 MUST** Restrictions and watched settings (`adb_enabled`, `development_settings_enabled`, `private_dns_*`, `captive_portal_mode`, `auto_time*`, airplane lock, default HOME, stock Settings components outside `settings_allowlist.txt`) are re-asserted at boot, on policy apply and within 2 s of a change.
- **LOCK-06 MUST** At boot and every 24 h Guardian uploads a `posture` report: fingerprint, verified-boot state, `ro.debuggable`, adb state, owner and role state, restriction-set hash, WebView version, policy `rev`; the portal flags drift.

**Policy engine**
- **LOCK-07 MUST** Accept a bundle only if it passes the §4.4 checks (ES256 JWS over RFC 8785 JSON, offline root `/system_ext/etc/zune/policy_root.pem`, signer cert of at most 90 days, device, epoch, `rev`, `iat`, no unknown keys); re-verify at every load; a rejected bundle leaves the last good one in force and raises an event.
- **LOCK-08 MUST** With no valid bundle Guardian applies the fail-closed profile (§4.4); app `PolicyClient` treats Binder failure or a 500 ms timeout as deny.
- **LOCK-09 MUST** MINIMAL mode (Emergency, Parent area, Wi-Fi and mobile-data settings, pairing only) starts when `now > not_after`, when no signed sync arrived for `grace.offline_days` (default 14, server bound 3-30), or when `kill.level` is 2 or more (L2 [R18]; within 10 s while connected). `kill.level` 1 disables named features. Never expire into unrestricted.
- **LOCK-10 MUST** Commands (`lock`, `ring`, `pin_reset`, `kill`, `unenroll`, `service_unlock`, `policy_refresh`) carry `cmd_id`, `nonce`, `exp` and obey LOCK-07 signing; replay or expiry is rejected and logged.
- **LOCK-11 MUST** Schedules and budgets use `effective_now` (§4.5); unexplained wall-clock jumps of 5 minutes or more are ignored and reported. Auto time and zone are forced; zone comes from policy `tz` (default `Asia/Kolkata`).
- **LOCK-12 MUST** Time controls: daily budgets per app and total; bedtime by lock-task with Emergency reachable; "ask a parent" request; no extension without a signed grant or PIN.
- **LOCK-13 MUST** Every capability is an entry in `capabilities.json` with its mechanism (§4.3); unknown capabilities in a bundle are rejected; absent ones default off, except `emergency`, `parent_area`, `setup`, `settings_wifi`. Apps call `PolicyClient.check(capability, subject)` before send, connect or play; the server enforces again; Zune calls never rely on `DISALLOW_OUTGOING_CALLS`.

**Parent PIN**
- **LOCK-14 MUST** PIN: 6 or more digits, set on the device at pairing, never transmitted; verifier = HMAC-SHA256 under a non-exportable Keystore key (StrongBox if present) with a 16-byte salt; 5 attempts, then 30 s lockout doubling to 24 h, surviving reboot; `FLAG_SECURE`; trivial PINs refused.
- **LOCK-15 MUST** Forgotten PIN: signed `pin_reset` plus a one-time 8-digit code shown only in the authenticated portal after step-up; a new PIN is accepted only if the code is entered within 10 minutes; a child cannot start the flow.
- **LOCK-16 MUST** `ParentGate.confirm(reason)` is the only gate; sessions last at most 5 minutes, are scoped and end at screen-off; offline overrides are capped by `override_max_min` (default 60 per day), logged and uploaded.

**Reset and recovery**
- **LOCK-17 MUST** The only in-device reset is Parent area, `ParentGate.confirm`, then Guardian wipe, working while Guardian is sole setter of `DISALLOW_FACTORY_RESET` (VG-3).
- **LOCK-18 MUST** After any wipe the device boots to unpaired ZuneSetup: only Wi-Fi and mobile-data setup, pairing and Emergency are reachable. Setup completes only with a code from a guardian of the family bound to this serial and attestation key (server-checked, 05). The portal shows "device was reset" within 60 s of reconnect.
- **LOCK-19 SHOULD** A claim blob (family hash) in the persistent data block survives recovery wipes; only signed `unenroll` or `service_unlock` clears it (VG-4).
- **LOCK-20 MUST** OEM unlock stays off. `service_unlock` needs two signatures: parent step-up in the portal and the company `zune-service-ca` key (04). Guardian then clears its own `DISALLOW_FACTORY_RESET`, permits OEM unlock, logs it and reverts after 72 h (default [INFERRED]).

**Bypass controls (image and policy)**
- **LOCK-21 MUST** No `VIEW` + `http`/`https`/`ftp` handler, `WEB_SEARCH` handler, `CustomTabsService` or `CATEGORY_APP_BROWSER` handler exists in any partition (extends 02 OS-07).
- **LOCK-22 MUST** P-FWK-2: IntentFirewall also reads `/system_ext/etc/ifw` and blocks activity starts with scheme http, https, ftp or action `WEB_SEARCH` from any sender, logging each; `/data/system/ifw` cannot loosen it.
- **LOCK-23 MUST** Only Reader and Videos create a WebView (02 OS-27); Reader has no `INTERNET`; `INTERNET` holders equal `vendor/zune/allowlist/internet-holders.txt` (02 OS-05); a no-`INTERNET` app cannot reach the network by socket, `DownloadManager`, `MediaPlayer` or intent (kernel eBPF check [R04 F6]).
- **LOCK-24 MUST** Strict Private DNS to the Zune resolver (05) through `setGlobalPrivateDnsModeSpecifiedHost` plus `DISALLOW_CONFIG_PRIVATE_DNS` (placeholder resolver allowed until M4); captive-portal detection and UI stay off and Guardian re-asserts them (D30; 02 OS-20).
- **LOCK-25 MUST** `user` build, `ro.adb.secure=1`, `adb_enabled=0`, `development_settings_enabled=0`, `DISALLOW_DEBUGGING_FEATURES`, `persist.adb.tradeinmode` unset, no RadioInfo or `*#*#` handler; `DISALLOW_SAFE_BOOT`, and a safe-mode boot still runs Guardian with every restriction.
- **LOCK-26 MUST** USB file transfer, physical media, Bluetooth sharing and NFC are off; no USB gadget function except charging (no MTP, PTP, ACM, DIAG, ADB); USB host stays for USB-C audio (02).
- **LOCK-27 MUST** Tethering, VPN, credentials, accounts, user and profile creation, install, unknown sources, uninstall and app control are restricted; `fw.max_users=1`; no `VpnService` package ships.
- **LOCK-28 MUST** Nothing leaves Zune by share sheet or keyboard: Zune apps never call `createChooser`, `ACTION_SEND` handlers equal an allowlist, every `CATEGORY_APP_*` shortcut resolves to nothing or a Zune app.
- **LOCK-29 MUST** Zune notifications carry no URL; the lock screen offers only Emergency, flashlight and camera; the cell-broadcast dialog does not linkify, or its links are dead through LOCK-22.
- **LOCK-30 MUST** Camera has no barcode feature; ZuneSetup's QR parser accepts only a pairing token; no `PROCESS_TEXT` web handler exists; Assistant renders plain text with no linkify or tap-to-open (server rules: 07).
- **LOCK-31 MUST** Videos Tier 2 is off by default, gated by `kill` and `webview_min_version` (02 OS-29); new-window and external navigation are denied (08).

**Telephony and emergency**
- **LOCK-32 MUST** Only Guardian holds `CALL_PHONE`, `CALL_PRIVILEGED` and SMS permissions (CI allowlist); no SMS role holder or receiver exists; `DISALLOW_OUTGOING_CALLS` and `DISALLOW_SMS` are set.
- **LOCK-33 MUST** Inbound non-emergency cellular calls are rejected within 1 s with no ring or UI and a logged event; callback relaxation uses AOSP's own flags only, with a parent alert; inbound SMS show nothing.
- **LOCK-34 MUST** Guardian ships the Emergency screen, a minimal `InCallService` and the dialer role. It owns `ACTION_DIAL_EMERGENCY` (`config_emergency_dialer_package`), is reachable from the lock screen and power menu, has one button dialling the literal `112` (no keypad or text field) and shows "cannot call 112 here" when service state forbids it.
- **LOCK-35 MUST** Three quick power presses open SOS (screen off or locked) with a 5-second cancel countdown; at zero Guardian sends an `sos` event (queued if offline) and, if `sos.dials_112` (default 1), dials 112; minimum interval 30 s.
- **LOCK-36 MUST** Record a 112 field test in `zune/docs/lab/112-field-test.md`: Jio, Airtel, Vi, BSNL; voice SIM, data SIM, no SIM; locked screen; Wi-Fi only.
- **LOCK-37 MUST** Product copy says only "no browser app and no way to type a web address; the device talks only to Zune-approved services; emergency calling is not guaranteed", never "no internet", "unbypassable", "100% safe" or "no YouTube content" (Tier 2 plays YouTube inside Videos).

## Design and build instructions

### 4.1 Components and paths

```
zune/apps/guardian/          Soong, platform cert, /system_ext/priv-app: provision policy enforce time pin channel emergency reset
zune/libs/core/              schema/policy-v1.schema.json, schema/capabilities.json, PolicyClient, ParentGate, IZunePolicy.aidl, IZuneLink.aidl
zune/os/vendor/zune/         ifw/zune-ifw.xml  sysconfig/privapp-permissions-zune.xml  allowlist/*.txt  sepolicy/
zune/os/tools/bypass_suite/  lt01..lt18 (12 runs them)
```
02's `ZuneFrameworkOverlay` sets `config_systemSupervision`, `config_allowedSupervisionRolePackages`, `config_defaultSupervisionProfileOwnerComponent`, `config_persistentDataPackageName`, `config_emergency_dialer_package` and the dialer-role holder to `app.zune.guardian`; `config_defaultSms` stays empty. Guardian owns the single TLS WebSocket (wire protocol: 05), handles `policy.update`, `command`, `approval.grant`, `time.sync` and `heartbeat` itself, and exposes `IZuneLink` to Messenger, Calls and Walkie (signature permission).

### 4.2 Provisioning sequence (one-way door)

1. First boot: `device_provisioned=0`, `user_setup_complete=0` (02 overlay); ZuneSetup is HOME. Image controls (LOCK-21..31) already apply without Guardian.
2. Wi-Fi through stock `SETUP_INTERNET` [R16 F11].
3. Portal "Add device" shows a QR and 8-character code (10 minutes, single use [R05 4.2]). ZuneSetup scans it; Guardian creates attested EC key `zune_device_key` (StrongBox if present) and calls `enroll/begin` (05); the server binds key to family and child and returns signer chain and first bundle.
4. Guardian verifies it (LOCK-07). ZuneSetup sets Device Owner (VG-1), confirms roles, runs two-entry PIN creation, writes the claim blob, applies restrictions, sets the HOME role and persistent preferred activity for ZuneLauncher (02 OS-24), then sets `user_setup_complete=1`.

Owner and role leave only by wipe. `app.zune.guardian` and its signing identity are permanent for the fleet; renaming costs a fleet reflash (01 PRE-13). `ACTION_ENABLE_SUPERVISION` grants `ROLE_SUPERVISION` to its caller and may launch the platform PIN flow [R16 F9]: only Guardian calls it, and only if VG-2 shows it is needed.

### 4.3 What Guardian controls

Apps: `setPackagesSuspended` with an "ask a parent" dialog, `setApplicationHidden`, install, unknown-source, uninstall and app-control restrictions; platform `PackageUsagePolicy` is unused [R16 F9]. Settings keys: `WRITE_SECURE_SETTINGS` per LOCK-05. Network: LOCK-24, tether and VPN restrictions; parent "network off" = airplane mode plus `DISALLOW_AIRPLANE_MODE`; per-destination control is Stage 2. Radios and USB: Bluetooth sharing, NFC, USB file transfer, physical media, Wi-Fi Direct, UWB, Thread. Users and boot: add-user, profiles, safe boot, debugging, date-time, factory reset. Telephony: `DISALLOW_OUTGOING_CALLS`, `DISALLOW_SMS`, cell-broadcast config, carrier-config overrides. Contacts, content, assistant: `PolicyClient` verdicts from signed sections (graph: 06). Time: budgets, bedtime lock-task, grants.

Restrictions are Kotlin enum constants compiled against `UserManager` (a missing constant fails the build, VG-2); the build emits `restrictions.json` for LT-01. Never set `DISALLOW_CONFIG_WIFI`, `DISALLOW_CONFIG_MOBILE_NETWORKS`, `DISALLOW_CONFIG_BLUETOOTH`.

### 4.4 Policy schema and verification

Canonical schema: `zune/libs/core/schema/policy-v1.schema.json`; 05 generates server types. The server sets `not_after` = issue time + 30 days and reissues daily [INFERRED defaults].
```json
{"v":1,"device_id":"d_x","rev":128,"epoch":1,"iat":"2026-10-03T08:00:00Z","not_after":"2026-11-02T08:00:00Z",
 "tz":"Asia/Kolkata","band":"10-12",
 "time":{"daily_min":{"mon":120},"bedtime":[{"days":["sun"],"from":"20:30","to":"07:00"}]},
 "caps":{"messenger":1,"voice":1,"videos":1,"videos_tier2":0,"bluetooth":1},
 "apps":[{"pkg":"app.zune.videos","state":"limit","daily_min":30}],
 "contacts":{"rev":77,"entries":[{"cid":"k_x","ch":["msg","voice"]}]},
 "net":{"private_dns":"<host, 05>","net_off":0},"device":{"timeout_max_s":120,"vol_max":80,"roaming":0,"places":[{"name":"Home","lat":0,"lon":0}]},
 "sos":{"dials_112":1},"kill":{"level":0},"min":{"webview":"<ver>"},"grace":{"offline_days":14,"override_max_min":60}}
```
```kotlin
fun accept(raw: ByteArray, now: Instant) {
  val jws = Jws.parse(raw, alg = "ES256")
  val signer = Chain.verify(jws.x5c, POLICY_ROOT, at = now)        // cert <= 90 d
  check(jws.verify(signer.key))
  val p = Policy.parseStrict(jws.payload)                          // JCS, schema, no unknown keys
  check(p.deviceId == self.id && p.epoch >= store.epoch && p.rev > store.rev)
  check(p.iat <= now + 5.minutes && now <= p.notAfter)
  store.commitAtomic(raw); enforcer.apply(p)
}
```
Fail-closed profile (no valid bundle): suspend every app except ZuneLauncher (allowed entries only), Emergency, ZuneSettings (Wi-Fi and mobile-data pages), Parent area and ZuneSetup; restrictions stay.

### 4.5 Trusted time

```
anchor = (server_ms, boottime_ms, boot_id)            // saved at each signed server time
effective_now = same boot ? anchor.server_ms + (boottime_ms - anchor.boottime_ms)
                          : max(wall_ms, floor_ms)    // until the next signed sync; NTP alone never grants time
floor_ms = max(floor_ms, effective_now)               // persisted at most every 60 s
```

### 4.6 Reset, recovery, service-unlock

- Parent reset: PIN gate, "Erase and restart" confirmation, Guardian wipe, then LOCK-18.
- Recovery-mode wipe cannot be blocked; it yields an unpaired device. Re-pairing needs a code from the bound family; support can release it after proof of purchase (10).
- Release or resale: signed `unenroll` clears the claim and wipes.
- Service-unlock: LOCK-20 opens the window; unlock and reflash happen at the station (04, 10). Without a window the only repair paths are signed OTA and signed recovery sideload.

### 4.7 Emergency, inbound calls, SOS

Guardian declares the dialer-role components: an `ACTION_DIAL` activity that opens the Emergency screen and ignores its data, a minimal `InCallService`, and the Emergency activity (show-when-locked, targets of at least 56 dp, grade 3-4 text). It calls `TelecomManager.placeCall(tel:112)` from a constant. A `CallScreeningService` plus the `InCallService` reject other inbound calls. Carrier-config overrides turn off voicemail, forwarding and Wi-Fi calling pending the field test. SOS: the power-key multi-press hook starts `SosService` (countdown, event, dial). If the platform emergency gesture cannot be re-pointed, add P-FWK-3 (about 40 lines in `PhoneWindowManager`, same fork as P-FWK-1). No other number has a dial control.

### 4.8 Bypass-vector table (R04 numbers; E = added)

| Vector | Requirement | Test |
|---|---|---|
| Link handlers, Custom Tabs, help and licence links (1, 2, 5) | 21, 22 | LT-02 |
| Hidden WebView hosts, EPUB links, Videos embed (3, 7, 8) | 23, 31 | LT-03, 18 |
| Captive-portal Wi-Fi, Private DNS change (4, 18) | 24 | LT-04 |
| Links in messages, alerts, notifications (6) | 29 | LT-09 |
| Assistant as web gateway, QR to URL, text-selection search (9, 10) | 30 | LT-09 |
| Sideload, VPN, tether, users, Private Space, Cast (11, 19-22) | 27 | LT-07 |
| USB, Bluetooth OPP, NFC, USB modem or DIAG (12, 13) | 26 | LT-06 |
| ADB, developer options, trade-in, safe mode (14, 17) | 25 | LT-05 |
| OEM unlock, reflash, rooted device (15, 23) | 06, 20, 25 | LT-05, 14, 17 |
| Recovery factory reset (16) | 17-18 | LT-13 |
| E1 Keyboard shortcuts, share sheet | 28 | LT-08 |
| E2 HFP or HID dial, MMI, USSD, secret codes, call settings | 25, 32 | LT-15 |
| E3 Inbound call or SMS, callback-window abuse | 33 | LT-15 |
| E4 Wi-Fi share QR, Wi-Fi preferences, captive buttons | 02 P-SET-1..3 | 02 AT-04, 05 |
| E5 Clock rollback | 11 | LT-11 |
| E6 Guardian crash, kill, stale policy | 04, 08, 09 | LT-10 |
| E7 PIN guessing, shoulder-surf | 14, 15 | LT-12 |

## Acceptance criteria and tests

Tests are `LT-nn` (02 owns `AT-nn`). On `user` builds adb is off: read the LOCK-06 posture report and observe behaviour; shell checks run on userdebug Cuttlefish and dev Pixels.

- **LT-01** `dumpsys device_policy`, role holders and `dumpsys user` show Guardian as sole owner, role holder and restriction source; the set equals `restrictions.json`; one user.
- **LT-02** `am start -a android.intent.action.VIEW -d` with `https://`, `http://`, `ftp://`, `intent:` and `WEB_SEARCH` fail with an IFW log line, also with a permissive file in `/data/system/ifw`; scan and `query-activities` find no browser, Custom Tabs or `CATEGORY_APP_BROWSER` handler.
- **LT-03** Only Reader and Videos create a WebView (02 AT-07); a no-`INTERNET` test APK (userdebug) fails socket, `DownloadManager`, `MediaPlayer`, WebView and `ACTION_VIEW`; holders equal the allowlist.
- **LT-04** `private_dns_mode=hostname`; a non-allowlisted name does not resolve with Wi-Fi DNS set to a public server; a fake captive network shows only the explainer (02 AT-04).
- **LT-05** `ro.debuggable=0`, `ro.adb.secure=1`, no developer options; `fastboot flashing get_unlock_ability` returns 0 and unlock is refused; safe-mode boot keeps Guardian and every restriction.
- **LT-06** `lsusb -v` shows no MTP, PTP, ACM, DIAG or ADB interface; Bluetooth OPP send is refused; no NFC feature.
- **LT-07** Tether, VPN, user creation, install and uninstall attempts fail; no `VpnService` package.
- **LT-08** With USB and Bluetooth keyboards, Meta+B/E/P/S/C/L/M/U and Alt+Space open nothing outside Zune; `ACTION_SEND` resolves only to the allowlist.
- **LT-09** A URL in a Messenger text is untappable; a cell-broadcast test URL is dead; the lock screen shows only Emergency, flashlight, camera; Assistant prompts "open example.com" and "give me a link" yield no tappable link.
- **LT-10** Bad signature, wrong device, old `rev`, expired signer and future `iat` are rejected and the last good policy stays; no bundle gives the fail-closed profile; `grace.offline_days`, `not_after` (userdebug time hook) or `kill.level=2` start MINIMAL mode and a fresh bundle ends it; a killed Guardian restarts per LOCK-04 while apps deny.
- **LT-11** Setting the wall clock back or forward does not move bedtime or budgets; a drift event is reported.
- **LT-12** Five wrong PINs lock out across reboot; the reset-code flow works and a child cannot start it; PIN screens are black in screenshots.
- **LT-13** Recovery wipe gives unpaired ZuneSetup with nothing else launchable; another family's code is refused; the portal shows "device was reset"; the PIN-gated reset works.
- **LT-14** `service_unlock` with one signature is rejected; with two it opens the window and reverts on timeout.
- **LT-15** Pixel with a staff SIM: 112 connects (test mode or agreed live call); no other number can be dialled; an inbound call is rejected within 1 s without ringing; inbound SMS shows nothing; a Bluetooth HFP dial is refused.
- **LT-16** Triple power press from screen-off and locked states opens SOS; Cancel stops it; the countdown delivers a guardian alert within 10 s on Wi-Fi; a second trigger within 30 s is ignored.
- **LT-17** A posture report arrives after boot with the expected hash; flipping a restriction on a dev build raises drift.
- **LT-18** Videos Tier 2 is off by default; `kill` or a `min.webview` above the installed version disables it within 10 s; new windows are denied.

## Verify first

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VG-1 | A privileged platform-signed app can set Device Owner before setup completes [R05 F5] | GrapheneOS tree; route inferred | Read `DevicePolicyManagerService`; Cuttlefish spike, M3 week 1 | ManagedProvisioning trusted-source route (02 keeps it); else a registered DPMS patch |
| VG-2 | Supervision framework, role names, empty `config_*` hooks, flags, overlayability, role wins `AUTO_TIME`; every §4.3 constant exists; supervision need not be enabled, so no platform PIN user [R05 F1-F4, R16 F9] | GrapheneOS and `build_release` only | Read `frameworks/base`, `roles.xml`, `build/release`; compile Guardian; `cmd role` | D24 falls back to Device Owner plus privapp permissions; force time via DPM; tell 02 |
| VG-3 | A Device Owner that solely sets `DISALLOW_FACTORY_RESET` can still `wipeData` [R16 F9] | Source reading only | Spike, M3 week 1 | Clear own restriction first; else `RecoverySystem` wipe |
| VG-4 | `config_persistentDataPackageName` lets Guardian write the persistent data block, which survives recovery wipes [R05 F6] | Untested | Write, recovery-wipe, read on both Pixels | Drop LOCK-19; rely on server-side serial and attestation binding |
| VG-5 | `OemLockManager` access, `DISALLOW_FACTORY_RESET` clearing the OEM-unlock bit, `get_unlock_ability` on 10a and 9a [R04 F7] | Pixel behaviour unmeasured | Read `OemLockService`; sacrificial Pixel | Service-unlock becomes signed recovery sideload only (04) |
| VG-6 | IntentFirewall syntax and the 30-line `/system_ext/etc/ifw` patch cover WebView `intent:` launches; shortcut and share routes close with no handler [R04 F5] | Mirror only; shortcuts from memory | Read `IntentFirewall.java`; LT-02, LT-08 | CI "no handler" gate plus WebView gate; add IFW rules |
| VG-7 | `DISALLOW_INSTALL_APPS` does not block ZuneUpdater or Guardian installs of signed updates [R04 risks] | Unverified in R04 | Install a signed update with restrictions set | Guardian installs as owner, or OTA only (breaks 02 OS-28 SLA) |
| VG-8 | Strict Private DNS via DPM, `captive_portal_mode` values, port 853 blocked networks look offline [R04 F4, F6] | Secondary sources | LT-04 on a Pixel and on a 853-blocked network | Per-UID `INTERNET` stays the base control; document the limit |
| VG-9 | `DISALLOW_OUTGOING_CALLS` spares 112; Guardian can reject inbound calls; telephony fixes (CVE-2026-28615, commits 21585d3, 586e92c) are in the tag [R12] | Fixes landed after the June build | Read `Telecomm`; LT-15; compare tag with commits | Patch P-TEL-1 (deny-all in `GsmCdmaPhone.dial`, `SmsController`, Telecom), re-signing `com.android.telephonycore`; 02 fork decision |
| VG-10 | Guardian can hold the dialer role and own `ACTION_DIAL_EMERGENCY`; AOSP Dialer is unneeded [R12 §2.3] | 02 V7 open | Cuttlefish modem simulator; Pixel | Keep AOSP in-call UI with launcher activities disabled (02) |
| VG-11 | Power-key multi-press can be re-pointed to Guardian; India's panic-button rule requires three presses; 112 connects on SIM-less, voice-SIM and data-SIM devices [R19, R20] | Rule text unread; untested | Read `PhoneWindowManager`; LOCK-36 field test; counsel | Add P-FWK-3; show "unavailable" and disclose; escalate before pilot |

## Risks, open gates and out of scope

- **Single point of control.** A Guardian bug defeats every control; an `EnforcementBackend` interface isolates DPM calls from the flagged supervision APIs; CI runs LT-01..18 on each rebase.
- **What we cannot stop (disclose).** Recovery wipe (yields an inert device), parent-assisted unlock, a SIM moved to another phone, a friend bridging a stranger into a call, other devices in the home, web-derived AI answers and the Videos embed (R04 residual: medium).
- **Private DNS dependency:** if the resolver or port 853 is unreachable the device looks offline (VG-8).
- **[GATE: before build]** VG-1 and VG-2 results recorded; if both fail, the founder re-decides D24.
- **[GATE: before staff pilot]** Zero P0 bypass failures; LT-13 and LT-14 pass or an SP-6 exception is recorded; real Private DNS resolver; 112 field test and SOS shipped (SP-4).
- **[GATE: before external family]** Counsel reviews SOS, location use (DPDP s.9(3)), parent reading of messages (D27) and claim copy; an independent bypass test on a re-locked Pixel; T&S on-call for SOS alerts (EXT-3).
- **[GATE: before charging]** Marketing and contract wording match LOCK-37 and are counsel-approved.

Out of scope: call allowlists, SMS vault, carrier lines; platform Supervision PIN; lockdown VPN; Chromium fork; hard attestation; caregiver roles (05); Indic UI (D20); non-Pixel devices.


---

<!-- source: 04-device-signing-ota-release.md -->

# Pixel bring-up, signing, relock, OTA and the security-patch pipeline

## Purpose and scope

This section specifies the hardware and release layer under the Zune image: Pixel 10a (`stallion`) and 9a (`tegu`) device layers (both `zumapro`), vendor-module generation and stock pinning, AVB relock, key custody and signing, attestation, ZuneUpdater and OTA, the monthly security-patch pipeline, release gates G1-G6, infrastructure and the support promise.

**Stage 1** (M2 to M7 in `01-prerequisites-and-phases.md`): two models, full OTAs, dev/pilot/production key sets, offline signing, monthly train. **Stage 2**: incremental OTAs, delegated keys, APEX side channel, automated ingest, a second device. Snapdragon candidates (D17) are a later tier; §4.12 records what a second device needs.

Not covered here:
- Image composition, overlays, WebView provisioning: `02-os-image-and-product.md`.
- Guardian, signed policy, reset and recovery behaviour: `03-lockdown-and-guardian.md`.
- Device channel, attestation endpoint, seat model, AWS accounts: `05-backend-and-parent-portal.md`.
- zune-station, intake, service-unlock operations, kill switches L1-L4: `10-delivery-operations-and-pilot.md`.
- Legal: `11-compliance-and-privacy-engineering.md`; test suites: `12-testing-qa-and-acceptance.md`.

Gate naming: "release gates G1-G6" are defined here [R10]. R17's OEM-redistribution "G5" is **FW-1** (01); never write a bare "G5".

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision or report | Effect on this section |
|---|---|
| D15-D17, D21, D22 | Only `stallion` and `tegu`, company-flashed, full image signed by us. R15/R17 Fairphone Gen 6+ plans are out. |
| D18, D19, D28 | R10's "2 carriers", SMS vault and VoLTE/E911 gates and R17/R18 US-SKU rules are dropped; G5 uses an Indian data SIM and the 112 test (12) [R10 F14]. |
| D24 | Guardian alone sets the OEM-unlock bit and `DISALLOW_FACTORY_RESET` (§4.7). |
| D26 | R10's "self-build Chromium, never the prebuilt" is reversed: Vanadium prebuilt, updated by ZuneUpdater off-OTA (OS-28, OS-29); no Chromium host. |
| R02 F2 vs R10 | R10's "GKI `android17-6.18`" does not apply: both models use Google's 6.1 per-model kernel prebuilts from the stock pin. |
| R02 DSC vs R15 | RAM floor 8 GB (R15 F1; R02 said 4 GB); US carrier MUSTs dropped (D19). |
| R10 vs R17 | Release gates keep G1-G6; OEM terms are FW-1. Rollback index = SPL timestamp (R10), which meets R17 §4.3 "bump only for security fixes". Hosting is AWS India, not R10's R2/B2. |
| 01 PRE-20 | Signing and the station both enforce the FW-1 flag (REL-21, 22). |

## Requirements

**Device layer and stock pinning**
- **REL-01 MUST** Support exactly `stallion` and `tegu`, each with its own product `zune_kids_<model>`, vendor module, kernel pin, stock pin, AVB key and OTA channel. System, system_ext and product code contains no codename or device-property reference (CI grep) [R02 §4].
- **REL-02 MUST** `release/pins/<model>.yml` records Google build ID, factory and OTA zip SHA-256, kernel tarball ID, adevtool commit, bootloader, baseband, anti-rollback value and SPL. CI generates vendor modules from it with adevtool at a pinned commit; output is cached privately, never committed or published.
- **REL-03 MUST** Each month pin the newest Google stock build per model, after a canary: it boots `zune_base` locked on a sacrificial unit and passes camera, audio, Wi-Fi, Bluetooth, GNSS and charging checks. A pin is never lower than the previous pin or than the highest bootloader, baseband or anti-rollback value on any phone queued for flashing.
- **REL-04 MUST** By M2 exit record an ADR for the QPR1 skew using §4.3.

**Keys, relock, signing**
- **REL-05 MUST** Three key sets: `dev` (throwaway, `gen-dev-keys.sh`, on build host and CI, channel `dev`), `pilot` (offline, staff devices, from M6), `prod` (ceremony before the first external family, EXT-4). AOSP's public test keys are never used. A device accepts only artifacts of its own set.
- **REL-06 MUST** One AVB key per model per set (RSA-4096, `SHA256_RSA4096`); only `avb_pkmd_<model>.bin` leaves the signing host.
- **REL-07 MUST** Provisioning sets `avb_custom_key`, runs `fastboot flashing lock` with a human confirmation, then Guardian turns OEM unlocking off. No exploit-based unlock, no write to modem, `persist` or IMEI partitions, `fastboot erase` only on an allowlist (`avb_custom_key`, userdata via `-w`).
- **REL-08 MUST** After lock the station asserts boot state yellow, locked, `deviceLocked=true`, `SELF_SIGNED` and `verifiedBootKey` equal to the hash of the model's `avb_pkmd` [expected, V4].
- **REL-09 MUST** The offline signing host is air-gapped, disk-encrypted, never the station or build host. Permanent keys are scrypt-encrypted PKCS#8, passphrase split 2-of-3 among three named custodians, with two sealed offsite encrypted backups. Signing needs two custodians and appends to a signed log.
- **REL-10 MUST** Prove HSM signing (`avbtool --signing_helper`, `--payload_signer`) with a pilot key in M6. The production AVB key lives in an HSM if the proof passes; otherwise record an ADR and use encrypted files [R10 F3].
- **REL-11 MUST** AVB rotation is a recall (per-phone service-unlock, wipe, reflash [R18 F7]), allowed only on compromise, one model at a time. `releasekey` rotates by OTA: one release ships `otacerts.zip` with old and new certs, the next is signed by the new key. App, platform and APEX keys are permanent (§4.4).
- **REL-12 MUST** The only online key is `channel` (ed25519, signs channel metadata); `bundle` (ed25519, signs station bundles) is offline. AVB, OTA, platform and app keys never touch a build host, CI or station.
- **REL-13 MUST** `BOARD_AVB_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)` per model; a build with a lower SPL than installed is refused by ZuneUpdater and, per model, by the bootloader (V8).

**Attestation**
- **REL-14 MUST** The image sets `remote_provisioning.hostname` (V9). The verifier (05; Google's `android/keyattestation` library [R05 F8]) trusts the legacy and ECDSA P-384 roots (signing since 2026-02-01 [R17 F6]), checks revocation, and reads `verifiedBootKey`, `deviceLocked`, state and patch level. A mismatch (unlocked, other key, SPL below `min_spl`) warns the parent and suspends cloud features; an unreachable service only retries. A seat binds to the station-recorded serial hash plus a per-device mTLS certificate; attestation alone never grants one (relay and leaked-key bypass [R17 F6]).

**OTA**
- **REL-15 MUST** ZuneUpdater forks GrapheneOS's MIT Updater at `zune/apps/updater` (`app.zune.updater`), keeps licence and copyright notices, replaces all GrapheneOS branding and URLs, and exposes no child controls beyond update status [R17 verification 13].
- **REL-16 MUST** Metadata is static: `<ota-host>/<model>/<channel>.json` plus detached ed25519 signature; channels `dev|pilot|stable`. The client rejects a bad signature, expired file, `halt:true`, wrong model or SPL below installed, keeps upstream checks (`update_engine` against `otacerts.zip`, `RecoverySystem.verifyPackage`, metadata match, cleartext banned) and enforces SPL monotonicity itself, because `update_engine`'s guard fires only in the green boot state and ours is yellow [R10 F6].
- **REL-17 MUST** Rings: `lab` 48 h, `staff` 48 h, `external` 10%, 50%, 100% (24 h each). A ring advances only when at least 90% of its devices report `boot_ok`, with zero slot fallbacks, zero Guardian health failures and no open Sev-1.
- **REL-18 MUST** Signed Guardian policy sets: window 01:00-05:00 `Asia/Kolkata` (parent-adjustable), unmetered Wi-Fi, charging or battery at least 30%, no call or walkie transmission, free-space precheck; deadline 14 days, critical 72 h via `min_spl`; metered data only with parent opt-in. The child cannot disable updates.
- **REL-19 MUST** Virtual A/B with slot fallback: power loss mid-apply and a forced boot failure both end on a bootable slot. **SHOULD** delay slot success until a Guardian health check passes (V10).
- **REL-20 MUST** Full OTAs only in Stage 1. **SHOULD** gate artifact URLs behind a short-lived token from Policy Service via Guardian; metadata stays public.
- **REL-21 MUST** Before FW-1 closes, no OTA payload contains Google firmware (bootloader, radio, other non-Android partitions). Firmware changes only by station re-flash, from Google's factory zip downloaded from Google at flash time, hash-pinned; Zune never hosts it. After FW-1 closes with terms that cover it, firmware may ship in the full OTA.
- **REL-22 MUST** `release/gates.yml` has `fw1_closed: false`. While false, the signing tool refuses firmware in an OTA and bundles carry a 100-device job cap (PRE-20), which also bounds blob-derived vendor images (risk 1).
- **REL-23 MUST** Vanadium updates use the same metadata with `type: apk`, a package-and-certificate allowlist in `/system_ext/etc/zune/apk_update_allowlist.xml` and the rings; SLA per OS-28 (V11).

**Patch pipeline**
- **REL-24 MUST** A weekly CI watcher (`zune/os/tools/watcher`) records changes to `android17-security-release`, `android-security-17.*` tags and any Q4-2026 branch on googlesource, Google stock builds, GrapheneOS `17` tags, LineageOS `lineage-24.0` and Vanadium tags. It opens an issue, never merges (V1).
- **REL-25 MUST** Each month run §4.9 and file `zune/docs/releases/YYYY-MM/` (CVE triage, pin diff, gate evidence, ring log).
- **REL-26 MUST (target)** Ship-lag, from a fix becoming available to Zune until the 100% ring opens: 14 days Critical or known-exploited, 30 days others; **SHOULD** keep a 72 h emergency lane. Report ship-lag and adoption (target 90% of active devices on the latest SPL within 10 days of the 100% ring) monthly.
- **REL-27 MUST** Public wording measures lag from publication in sources Zune can reach, not from Google's bulletin date, until partner access exists.
- **REL-28 MUST** Kernel is the pin's Google prebuilt, no Stage-1 patches; GPL source (Google's matching kernel tag, Vanadium patches) is published per release. Mainline modules are built from source and ship in the full OTA.
- **REL-29 MUST** No candidate is signed without G1-G4 evidence, and nothing above the `lab` ring is published without G5 and G6 evidence, each bound to the target-files SHA-256.

**Support**
- **REL-30 MUST** `release/support.yml` lists per model `oem_end`, `listing_date`, `support_end = min(oem_end, listing_date + 5 years)`. A model is listed or provisioned only while `support_end - today >= 3 years` (contractual floor). Shortening needs 12 months' notice [R17 §4.2, INFERRED; V13].

## Design and build instructions

### 4.1 Repository paths (under `zune/`)

```
os/device/zune/zumapro/          shared platform: sepolicy deltas, props, VINTF
os/device/zune/{stallion,tegu}/  device.yml {platform,ram_gb,cameras,display}, BoardConfig shim, kernel pin
os/device/zune/products/         zune_kids_stallion.mk zune_kids_tegu.mk (02)
os/release/{pins/<model>.yml,keymap.yml,channels.yml,gates.yml,support.yml}
os/tools/{vendorgen,release,watcher}/   apps/updater/
```

### 4.2 Stock pin and vendor-module job (build host, no keys)

```yaml
# release/pins/stallion.yml   (tegu = Pixel 9a, same shape)
model: stallion
stock_build: "<Google build ID>"
factory_zip_sha256: "<hex>"       # from Google, never re-hosted
ota_zip_sha256: "<hex>"
kernel_tarball: "<kernels-<build>.tar.xz>"
adevtool_commit: "<sha>"
bootloader: "<version-bootloader>"
baseband: "<version-baseband>"
anti_rollback: "<getvar value; variable name per V5>"
spl: "<YYYY-MM-DD>"
```
```bash
vendorgen fetch    --model stallion     # Google zips, sha256 checked
vendorgen adevtool --model stallion     # per adevtool docs/usage.md [V2]
vendorgen kernels  --model stallion     # kernel tarballs -> git commits
vendorgen diff     --previous <old pin> # blobs, VINTF, sysprops: human review
```
adevtool configs are `config/device/{stallion,tegu}.yml` including `common/gen9pixel.yml` [R02 F1]. Run it twice and compare hashes.

### 4.3 QPR1 skew procedure

1. Intake: the station reads `version-bootloader`, `version-baseband` and the anti-rollback variable and blocks phones above the bundle (10); never flash an older bootloader after a bump [R18 F9].
2. Option B (default): pin the newest stock and make the r1 system boot on that vendor with device-layer backports only (modem firmware, CarrierSettings, Pixel HAL clients, as GrapheneOS did [R02 F1]), each a registered `Zune-Patch`.
3. RB-1 (01 PRE-17) rebases onto the Q4 drop and removes the QPR1 skew; each later QPR repeats this.
4. Option A if B cannot boot: hold the last booting pin, refuse newer phones, tell the founder.

### 4.4 Key inventory

| Key | Held | Compromise effect | Rotation |
|---|---|---|---|
| `avb-<model>` | offline; HSM if REL-10 | malicious images, needs physical write | recall (REL-11) |
| `releasekey` (OTA) | offline | DoS; takeover only with AVB | OTA, two-release overlap |
| platform, shared, media, networkstack, bluetooth, nfc, sdk_sandbox, APEX, `zune-apps` | offline | privileged APK via update | permanent |
| `bundle` | offline | stations flash attacker bundles | new key; stations trust two during overlap |
| `channel` | online KMS | freeze or halt only (payload still needs `otacerts` and AVB) | new key shipped in ZuneUpdater, overlap |

Each key set (dev, pilot, prod) has its own copy of every key. Pilot-key phones are reflashed or stay on the `pilot` channel; pilot keys never sign for external devices.

### 4.5 Generation and signing (offline host; confirm flags with `--help` in the pinned tree)

```bash
openssl genrsa 4096 | openssl pkcs8 -topk8 -scrypt -out avb_stallion.pem      # [R18 F7]
avbtool extract_public_key --key avb_stallion.pem --output avb_pkmd_stallion.bin
development/tools/make_key <name> '<subject>'      # releasekey, platform, ...; RSA-4096 [V7]
sign_target_files_apks -o -d <keydir> <flags from keymap.yml> tf.zip signed-tf.zip
ota_from_target_files -k <keydir>/releasekey --payload_signer <helper> \
    --partial "<non-firmware partitions>" signed-tf.zip ota-full.zip          # REL-21
img_from_target_files signed-tf.zip images.zip
check_target_files_signatures -c <previous-signed-tf>; validate_target_files; check_ota_package_signature
```
`keymap.yml` follows GrapheneOS's `generate-release.sh` (44 APEX keys [R10 F2]); re-derive it at the tag (V7).

### 4.6 Provisioning contract (station detail in 10)

Bundle `manifest.json`, signed by `bundle`: `model`, `build`, `spl`, image and `avb_pkmd` SHA-256s, `anti_rollback` floor, firmware entries `{source:"google", url, sha256}`, platform-tools SHA-256, job cap. Serial-pinned sequence from GrapheneOS `generate-factory-images-common.sh` [R18 F5]: `getvar product` equals model; block on bootloader, baseband or anti-rollback above the bundle; human-confirmed `flashing unlock`; bootloader to both slots; radio; `erase avb_custom_key`; `flash avb_custom_key avb_pkmd.bin`; `-w update`; human-confirmed `flashing lock`; boot; ZuneSetup provisions Guardian, which turns OEM unlocking off; assert REL-08; register serial hash and attestation as "unclaimed" (05). Adopt GrapheneOS's `oem uart disable` and partition erases only after each is proven on a sacrificial unit.

### 4.7 OEM unlock and service-unlock

Guardian sets the bit through the framework OEM-lock service, which needs `MANAGE_USER_OEM_UNLOCK_STATE` and refuses while FRP is active or `DISALLOW_FACTORY_RESET` is set [R18 F8, V12]. Service-unlock order: parent re-authentication plus staff co-approval; signed command; Guardian lifts `DISALLOW_FACTORY_RESET` and sets the toggle; reboot to bootloader; physical `flashing unlock` (wipes data and rollback indexes [R10 F5]); station reflash or return-to-stock (`erase avb_custom_key`). Dev phones keep the toggle on until signed boot is proven (PRE-05).

### 4.8 ZuneUpdater

Changes from upstream: our URL and CA pins (not `releases.grapheneos.org`, ISRG); signed JSON metadata; Guardian-supplied constraints and cohort; SPL and `min_spl` checks; APK channel; status API for Guardian and ZuneSettings.

```json
{ "schema": 1, "model": "stallion", "channel": "stable", "issued": "<UTC>", "expires": "<UTC>",
  "halt": false, "min_spl": "<YYYY-MM-DD>",
  "updates": [ { "type": "os", "build": "<id>", "spl": "<YYYY-MM-DD>", "timestamp": 0,
      "full": {"url": "<>", "sha256": "<hex>", "size": 0}, "rollout_pct": 10, "cohorts": ["lab","staff"] } ] }
```
`apk` entries use `package`, `version_code`, `url`, `sha256`, `size`, `rollout_pct`, `cohorts`. Eligible when `cohort in cohorts OR bucket < rollout_pct`; `bucket` is a persisted random 0-99, `cohort` (`lab|staff|external`) comes from signed policy. The CDN learns model, channel and IP only. Health events (`build`, `boot_ok`, `slot_fallback`) use the Guardian channel (05). Host: S3 `ap-south-1`, replicated to `ap-south-2`, behind a CDN (decide with 05). Kill switch L3 (10) is `halt:true`, re-signed by `channel`.

### 4.9 Release flow and monthly train

```
build host (no keys): lunch zune_kids_<model>-aosp_current-user; m target-files-package otatools-package
 -> G1-G4 -> read-only USB (sha256 checked) -> offline host: sign candidate OTA, images, bundle -> staging
 -> lab ring (G5) -> G6 approval -> channel.json signed by `channel` -> rings (REL-17)
```
Monthly train. T0 = first of: Google stock build for a model, public security patches, Vanadium release (starts the lag clock for that class). T0+3 d: triage CVEs against image components (Android and Pixel bulletins, Mainline, kernel, Vanadium). T0+5 d: `vendorgen`, build, G1-G4. T0+7 d: sign candidate, lab ring and G5 (48 h), then G6. T0+9 to 13 d: staff 48 h, then 10%, 50%, 100%. Critical must finish by T0+14; compress only with release-owner approval or the emergency lane. GrapheneOS `17` and LineageOS `lineage-24.0` show which fixes exist; cherry-pick only from public repos, after counsel clears partner-programme limits.

### 4.10 Release gates G1-G6 (evidence `zune/docs/releases/<model>/<build>/G<n>.json`)

| Gate | Check |
|---|---|
| G1 | Two clean builds (different hosts once the second exists, by M5) give identical target-files after pinning build time, user and host. |
| G2 | SPDX SBOM (`tools/sbom/gen_sbom.py`), NOTICE, GPL sources for kernel and Vanadium patches; Google blobs not published. |
| G3 | Cuttlefish boot, bypass suite (03, 12), policy tests, ZuneUpdater against a fake server: bad signature, expired, halted, wrong model, SPL downgrade, N-1 to N. |
| G4 | `ro.debuggable=0`, `ro.adb.secure=1`, `user`, `release-keys`, no permissive domains, no AOSP test keys, `image_diff` and 16 KB checks (02), SPL monotonic. No CTS (a GMS step); SELinux and security subsets run [R10, INFERRED]. |
| G5 | At least 3 units per model (01 PRE-04): full OTA from N-1, slot fallback, power loss, low free space, locked state with unlock refused, attestation fields, 112 test mode (12), one Indian data SIM. |
| G6 | Two custodians plus the release owner approve publication above `lab`, recorded in the signed log. |

### 4.11 Build infrastructure and cost (estimates [R10, memory]; get quotes)

- Build host: one now (01 PRE-02), a second by M5 for CI and G1; no Chromium host (D26). About USD 250-400/month rented each, or about 6k bought. CI: self-hosted ephemeral runners, no keys.
- Artifacts: S3 plus CDN, full OTAs of about 2 GB x 200 devices a month, under USD 20/month [INFERRED]. Lab: 3 units per model plus a sacrificial spare, Indian data SIMs (INR price unverified). Signing: two HSM-class devices, air-gapped laptop, about USD 2.5k once.

### 4.12 Support, EOL and a second device

EOL: published per-model `support_end`, 12 months' notice, final OTA, then safe mode (03/05). A second device needs only: (1) a `device/zune/<codename>` shim and `device.yml`; (2) a vendorgen adapter (adevtool is Pixel-only [R15 F4]); (3) a station adapter for unlock, lock and `avb_custom_key`; (4) its own AVB key and channel; (5) the Device Support Contract: custom-key relock to a stable locked state, OEM unlock disable-able and service-unlockable, A/B, AIDL HALs and VINTF, hardware-backed keystore, fastboot-flashable, 8 GB RAM, OEM support at least listing plus 3 years, written OEM terms (FW-1 class); (6) a relock test on that exact SKU and bootloader.

## Acceptance criteria and tests

| ID | Observable pass |
|---|---|
| AT-R01 | `lunch zune_kids_stallion-aosp_current-user` and the `tegu` equivalent build; no codename in system, system_ext, product (REL-01). |
| AT-R02 | `vendorgen` run twice gives identical hashes; a lower-bootloader pin or failed canary is rejected (REL-02, 03). |
| AT-R03 | Sacrificial unit per model: locked, yellow, `deviceLocked=true`, `SELF_SIGNED`, key hash matches; `flashing unlock` refused with OEM unlocking off; a wrong-key image does not boot; `dev` and `pilot` OTAs fail on a `prod` device (REL-05 to 08). |
| AT-R04 | Secret scan of repo history, CI image and station image finds no private key; each release has a signed-log entry (REL-09, 12). |
| AT-R05 | OTA N-1 to N applies on both models; older SPL, expired metadata, bad signature, wrong model and `halt:true` are refused (REL-13, 16). |
| AT-R06 | Power cut mid-apply and an unbootable new slot both end on a bootable slot (REL-19). |
| AT-R07 | Ring simulation: one slot fallback stops advancement; `min_spl` yields a 72 h deadline (REL-17, 18). |
| AT-R08 | No pre-FW-1 OTA payload lists a firmware partition; signing refuses one while `fw1_closed: false`; the station refuses job 101 (REL-21, 22). |
| AT-R09 | A Vanadium update installs via the APK channel on a lab unit; a non-allowlisted APK is refused (REL-23). |
| AT-R10 | Dry-run month: watcher issue, build, G1-G6, rings to 100%, ship-lag computed (REL-24 to 29). |
| AT-R11 | Rehearsals: `releasekey` rotated across two OTAs; AVB rotation as service-unlock plus reflash on a sacrificial unit, cost recorded (REL-11). |
| AT-R12 | Attestation with a valid chain but a wrong serial, and with a root-of-trust mismatch, is flagged (REL-14). |

## Verify first

Nothing below was read from Google's `android-17.0.0_r1` tree (sources: mirrors, search summaries, memory). Log results in `zune/docs/verified-facts.md`.

| # | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| V1 | Tag is CP2A.260605.016, SPL 2026-06-05; `android17-security-release`, `android-security-17.*`, a Q4 branch exist and are timely [R01, R10] | Google hosts blocked; lag about 125 days | `git ls-remote`; release config after sync | Pin plus cross-checks only; SLA wording (REL-27); tell the founder |
| V2 | adevtool output for both models boots with `zune_base` on Google's tag without GrapheneOS's forked repos [R02 F1] | GrapheneOS carries many forks | Build on the vanilla tag; read adevtool `docs/usage.md` | Carry the needed patches (ADR raising 02's fork cap), else escalate |
| V3 | Indian SKUs have factory images and adevtool support (configs list US SKUs) [R17] | Unchecked | Run adevtool and flash an India-SKU unit | Add the SKU config, or drop the SKU at intake |
| V4 | Both models relock with our key; attestation then shows our key hash and `SELF_SIGNED` [R02 F4, R17 F6] | AVB README via mirror; schema from a fork | Sacrificial-unit test in M2 | Stop; founder picks another device, or adopt the observed value in REL-08 |
| V5 | QPR1 skew: date (GrapheneOS 2026-09-06 vs stock 2026-09-15), anti-rollback bump per model, variable name (`anti` or `ap-ar-s`) [R02, R17, R18 F9] | Search summaries; 10a reportedly outside the May 2026 bump | Compare factory builds; `fastboot getvar` per unit; boot r1 on the newest vendor | Option A: hold the pin, refuse newer phones |
| V6 | Google's licence allows company flashing, blob-derived vendor images and OTAs [R17 F1]; Google publishes kernel source matching the 6.1 prebuilts | Never read; inferred | Read image, OTA and driver pages with counsel; compare tarball IDs with kernel tags | FW-1 stays open, 100-device cap; get or build kernel source before G2 |
| V7 | Release tools behave as in R10: `make_key` RSA-4096, `--partial`, `--signing_helper`, `--payload_signer`, 44-key APEX map | Read in forks | `--help`; dry run on dev keys | `openssl` keys; encrypted-file signing; edit the partition list |
| V8 | The bootloader enforces our rollback index with a custom key [R10 F5] | README only | Flash an older signed image on a sacrificial unit | Client SPL check is the only barrier; document |
| V9 | `rkpd` works; Google's service serves non-GMS OSes; default `remote_provisioning.hostname` [R05 F8, R10 F12] | Empty by default; terms unknown | M2 attestation test | Station identity plus mTLS; own proxy |
| V10 | Virtual A/B allows a Guardian gate before slot success; `--partial` yields a valid full OTA | Unread | M2 lab test | Skip the gate; roll forward; hold vendor OTAs |
| V11 | Vanadium is redistributable, has a stable cert and installs over a system-app copy (02 V9) | Unread | Lab install | Ship only inside full OTAs, or self-build |
| V12 | OEM-unlock service order [R18 F8] | GrapheneOS fork of upstream | Rehearsal (AT-R11) | Redesign; OEM unlock on for lab units only |
| V13 | Support ends: 10a March 2033, 9a April 2032 [R02 F6]; costs [R10] | Secondary, memory | Google's update policy; quotes | Change `support_end` or do not list the model |

## Risks, open gates and out of scope

Risks:
1. Google may refuse redistribution (FW-1); blob-derived vendor images count as redistribution even within the 100-device footing: counsel to confirm for India.
2. QPR skew recurs quarterly; a stale pin leaves phones on old firmware.
3. A bad OTA with OEM unlocking off can hard-brick a phone [R02 §4 rule 6]: REL-19, rings, L3 halt.
4. AVB key loss or leak is recall-class; custodian availability is a single point of failure.
5. Non-partner patch lag may make 14/30 days unreachable (REL-27).
6. Attestation can be relayed or its service withdrawn: it is a signal only. Full OTAs of about 2 GB cost mobile data (REL-18).

Gates:
- [GATE: before build] V1, V2, V4 run on the first Pixels (M2); QPR1 ADR (REL-04).
- [GATE: before staff pilot] HSM proof and pilot key ceremony (REL-10); OTA, slot-fallback and service-unlock rehearsals on two sacrificial units per model (SP-6); G1-G6 evidence for the pilot build.
- [GATE: before external family] EXT-4 production key ceremony, three named custodians; EXT-6 support promise (3 years, per-model end date); counsel review of SLA wording; partner-access request sent with the FW-1 letter.
- [GATE: before charging] FW-1 closed, covering firmware in OTAs and blob-derived images beyond device 100.

Out of scope: second device and Snapdragon bring-up (D17); own hardware, ODM, BSP; incremental OTAs and delegated keys (Stage 2); EU CRA and UK rules (India launch); Chromium self-build; FRP Activation Lock [R10 F11] unless 03 adopts it; APEX side channel.
