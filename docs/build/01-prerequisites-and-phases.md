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
