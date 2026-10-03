# Testing strategy, CI, red-teaming and the definition of done for the v1 baseline

## Purpose and scope

How the building session proves the v1 baseline works: CI, device and network matrices, bypass coverage, red-teaming, load, security, privacy, accessibility and usability tests, gate evidence, and the Definition of Done (DoD) for validating with about 200 families (D21; cohorts C0-C3 in `10-delivery-operations-and-pilot.md`).

**Stage 1** = every MUST below, running from M1 and complete before the gate it names; the DoD gates M7. **Stage 2** = device farm, gesture robot, child-voice corpora, Indic sets (D20), continuous external red-team, HW-1..4.

Owned here: pipelines, gate evidence, matrices, test governance, DoD. Test content stays in its home section: AT-nn (`02`), LT-nn and the bypass suite (`03`), AT-Rnn (`04`), BT-nn (`05`), CT-nn (`06`), AIT-nn (`07`), CNT-Tnn (`08`), APT-nn (`09`), AT-Onn (`10`), CMT-nn (`11`); new tests here are `QT-nn`. Not covered: milestones, gate register (`01-prerequisites-and-phases.md`); release-gate definitions, keys (`04-device-signing-ota-release.md`); legal gates (`11-compliance-and-privacy-engineering.md`); station operations (`10`). "MR" = push to a working branch (no pull request, 01 PRE-12). Never write a bare "G5": G1-G6 are 04's release gates; others are SP-, LEG-, EXT-, FW-1, PAY-1.

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision or report | Effect |
|---|---|
| D17, D21 vs R10 (3 units, 2 carriers), R13 | Only `stallion`, `tegu`; five lab units each (QA-15); Indian data SIMs. |
| D19, D28 vs R10 G5 (calls, SMS vault), R18 QA (VoLTE, SMS) | Dropped; LT-15, QT-16 and 112 test mode replace them. |
| D18 vs R07, R13 (COPPA, NCMEC, SB 243) | CMT-nn (DPDP) and the POCSO tabletop (CT-15, CMT-12); no US or EU tests. |
| D23, D27, D29 vs R07, R13 | Bands 7-9, 10-12, 13-14 everywhere; 12-month retention tests; eval on OpenAI, monthly Anthropic parity, judged by the other vendor (07 AI-26). |
| D25, D26, D30, D31 vs R04, R10 | Tier 2 tested on and off; Vanadium update path (AT-07, AT-R09), no Chromium build; captive Wi-Fi tested as unsupported, not a bypass; gesture, Bluetooth, NFC, MTP tests. |
| R04 (8 INTERNET holders, lockdown VPN, SMS links, BROM SoCs) | Tests cover per-UID INTERNET, Private DNS, WebView gate; inbound SMS shows nothing; Pixels only. |
| R10 (rings; G3 "policy tests (05, 12)"), R18 (adb off on `user`; cohorts 10/25/100), R13 (3% battery, 100k kids) | 04 REL-17 rings win; "12" meant the telephony report, use LT-07..10, BT-03; userdebug twin (QA-02); cohorts 12/30/70/88 (01); battery numbers [default] until C0 data; load is 10x the pilot. |

## Requirements

**Strategy**
- **QA-01 MUST** `mr-fast` fails an MR when a MUST ID in `docs/build/01..12` has neither an existing test ID nor a dated evidence file in `zune/docs/qa/traceability.csv` (`libs/testing/qa-trace`).
- **QA-02 MUST** Automation runs on a userdebug twin (`zune_kids_<model>-aosp_current-userdebug`, same manifest SHA, pins, `dev` keys). The `user` RC is verified by IG-1..12, Guardian's LOCK-06 posture, factory QA (10 §4.5) and RC-only tests (QT-06, 07, LT-05, 06, 13-16, 19). A user-vs-userdebug difference (files, properties, SELinux) outside `allowlist/debug-diff.txt` fails release gate G4.
- **QA-03 MUST** Dev and staging hold only synthetic data (`libs/testing/seed`, PRE-07); real people appear only in consented panels (QA-26).
- **QA-04 MUST** Flaky tests are fixed or deleted in 7 days [default]; bypass, safety and privacy tests are never quarantined (one retry; pass-after-retry is triaged in 48 h). Each P0, Sev-1 and child-safety P1 adds a permanent test in 72 h (07 §4.9).

**CI**
- **QA-05 MUST** Pipelines `mr-fast`, `mr-os`, `nightly`, `weekly`, `rc` (§4.2) live in `zune/os/ci/pipelines/`; all but `mr-fast` run on the build host (PRE-02); a red `mr-fast` or `mr-os` blocks merge; runners are ephemeral with no production key (PRE-03, PRE-08); until `main` exists a pre-push hook runs `mr-fast`.
- **QA-06 MUST** Each OS, app or `libs/core` MR builds `zune_kids_cf-aosp_current-userdebug`, boots it on Cuttlefish and passes QT-01; nightly boots `sdk_phone16k_x86_64-aosp_current-userdebug` with the Zune APKs (AT-09). IG-1..12 (§4.3) run per MR, nightly on `user` and per RC.
- **QA-07 MUST** QT-02 runs weekly and when `os/tools/gates/` changes; a gate or bypass test that passes on its seeded hole is a P1 defect.
- **QA-08 MUST** Evidence (§4.7), linked from `zune/docs/gates.md` (PRE-11), is bound to the target-files SHA-256 (REL-29); a new hash voids it. Waivers need two approvers, expire at the next build and never cover bypass, safety or privacy tests.

**Bypass and security**
- **QA-09 MUST** `os/tools/bypass_suite/COVERAGE.md` maps each R04 vector 1-23 and E1-E8 (03 §4.8) to a test, mode (CF Cuttlefish, PX Pixel, RC `user` unit) and last run; CI fails on an unmapped vector.
- **QA-10 MUST** The LT subset runs per OS MR (CF), the full suite nightly (CF) and per RC (PX, RC). Severity scales: P0-P2 here are bypass and defect classes; Sev-1 to Sev-4 are incident severities (11 §4.3); every P0 and every child-safety P1 is also a Sev-1. **P0**: a child reaches a browser, web page or YouTube outside Tier 2 Videos, an unapproved contact or another family's data, durably disables Guardian, or unlocks the bootloader. **P1**: lasting evasion of a time limit or content control (over 10 minutes [default]) or an information leak. **P2**: cosmetic. P0 stops shipping (OPS-21).
- **QA-11 MUST** QT-06 and QT-07 run on an RC `user` unit before each release gate G6 and each cohort.
- **QA-12 MUST** Before the first external family an independent party runs a black-box test of portal, device API, channel, T&S console and Guardian Binder interfaces; an exploratory bypass test on a re-locked Pixel (child-attacker model [R04]); and a supervised session where consenting children 10-14 try to reach a website or YouTube. No open P1 after retest.
- **QA-13 MUST** Drills leave evidence in `zune/docs/qa/drills/`: key custody (absent custodian; REL-09, 10), `releasekey` rotation and AVB recall (AT-R11), bad-OTA drill (downgrade refused, roll-forward in 72 h), kill levels (AT-O08), signer renewal (05 §4.5), DR (BT-14), breach, S4 and outage tabletops (CMT-09, 12, 19), secrets rotation (BT-18). Before C0, then quarterly.

**Devices, networks, quality**
- **QA-14 MUST** Run the §4.5 matrix per model at M5 exit, before C0 and C1; later releases sample one data SIM and home Wi-Fi.
- **QA-15 MUST** Per model: 3 RC units (locked, candidate's key set; re-flash by service-unlock when it changes), 1 dev unit (automation), 1 sacrificial unit (unlock, AVB rotation, bad OTA); key sets cannot share a phone (REL-05). `docs/lab/devices.md` records bootloader, baseband, anti-rollback, SPL (REL-03).
- **QA-16 MUST** 112 evidence per LOCK-36 for Jio, Airtel, Vi, BSNL on both models. A live 112 call needs prior written agreement with the carrier or state emergency centre; otherwise use `cmd phone emergency-number-test-mode` and record live behaviour as untested (LOCK-37). Archive for counsel.
- **QA-17 MUST** QT-03 and QT-05 meet bars Q6 and Q8 on both models; C0 data replaces [default] thresholds by ADR.

**AI and moderation**
- **QA-18 MUST** Sets in `zune/eval/{assistant,comms}/sets/` are versioned, hashed in every report, split by band, at least 25% romanised Hinglish and Indian-English phrasing with typos (07 §4.7), 30% held out and hidden from prompt, rule and classifier authors.
- **QA-19 MUST** No sexualised-minor material is created, stored or sent anywhere: CSAM and nudity cases inject classifier verdicts on innocuous images (AIT-05); adult testers write child-voiced self-harm, abuse and grooming prompts, at most 2 h a day each [default].
- **QA-20 MUST** Eval uses a separate vendor project with advance notice to the vendor (07 VA-5). Judge = the other vendor's model plus a 10% human sample [default] (two reviewers, T&S lead settles ties).
- **QA-21 MUST** Reports give counts and exact one-sided 95% bounds. 07's gates are regression gates: 0 of 800 unsafe still allows 0.37%; 196 of 200 T0 hits has a lower bound of 95.5%. Before the first external family T0 sets reach 300 items.

**Load, privacy, access, usability**
- **QA-22 MUST** QT-09 and QT-10 (§4.6) pass in staging before C0 and C1; each fault shows its expected degradation (fail-closed, MINIMAL mode, `curated-only`, queue replay) and recovers without losing a message.
- **QA-23 MUST** QT-08: a seeded synthetic family uses every feature; scans of logs, metrics, traces, crash reports, S3, Redis, non-vault databases, vendor-mock logs, portal HTML find canary strings only where `data-inventory.yaml` permits (CMP-33); any other hit is Sev-2 and blocks release. CMT (consent ledger, erasure), BT-06..10 and AIT-09 run nightly in staging where automatable.
- **QA-24 MUST** QT-12 per release on both Pixels: font scale 1.0 and 2.0, largest display, contrast (4.5:1 text, 3:1 outline), band target sizes (APP-28), no colour-only state, ATF checks (APT-11); portal Playwright at 360 px, keyboard-only, axe-core.
- **QA-25 MUST** QT-13: at least 6 children per band, parent present, company dev phones, synthetic accounts; APT-13 tasks plus ask a grown-up and open a book; 80% unaided per task and band (APP-36).
- **QA-26 MUST** Children in panels and in the QA-12 session are data principals: counsel-approved written parent consent, no face or voice recording without separate consent, pseudonymised notes, deletion after analysis; until approved, panels use C0 staff children only.
- **QA-27 SHOULD** QT-14: at least 6 guardians on a phone browser complete claim, two-family contact approval, bedtime, reading a thread, remote lock, consent withdrawal; 80% unaided, median under 3 minutes per task [default].

**Gates and DoD**
- **QA-28 MUST** `zune/docs/qa/DOD.md` is generated from the DoD tables with the latest run IDs; the founder acknowledges it at M7 entry. `limitations.md` feeds the parent pack, hand-over script (10 §4.6) and agreement, claims within LOCK-37 (CMP-35).
- **QA-29 MUST** During cohorts a weekly report compares measurements with bars Q1-Q13 (`ev.health` crash and ANR counts, OTA, latency); a breached stop-ship trigger freezes new flashes (OPS-21).

## Design and build instructions

### 4.1 Layers and paths

Layers: L0 static, L1 unit, L2 Cuttlefish system, L3 Pixel device, L4 staging integration, L5 field and human.
- **OS image:** L0 IG-1..12 on target-files; L2 boot, AT and LT subset, goldfish 16 KB; L3 full LT, camera, Bluetooth, battery, gestures; L5 RC attacks, 112, carriers.
- **Apps:** L0 `zune-lint`; L1 Robolectric (sdk 37), Compose ui-test, Roborazzi; L2 `connectedAndroidTest`; L3 Pixels; L5 child panels.
- **Backend:** L1 Go tests with Postgres and Redis containers, Go-Kotlin signing vectors (BE-13); L4 BT, CT, AIT, CNT-T, privacy, load; L5 independent test, drills.
- **Portal:** L1 unit; L4 Playwright at 360 px, axe-core, CSP (BT-10, BT-16); L5 parent panel.

Paths under `zune/`: `os/ci/pipelines/` (repo-root `.github/workflows/` calls them), `os/tools/gates/`, `os/tools/bypass_suite/` (03), `libs/testing/{qa-trace,evidence,loadgen,canary,seed}`, `eval/{assistant,comms}/sets/`, `docs/qa/`, `docs/releases/<model>/<build>/G<n>.json` (04).

### 4.2 Pipelines [budgets default]

- **mr-fast** every MR, 15 min: L0, L1, `qa-trace`.
- **mr-os** MR touching `os`, `apps`, `libs/core`, 90 min: `zune_kids_cf` build, IG-1..12, QT-01, AT-03/04/06/07, LT-01..04, 07..12, `connectedAndroidTest`.
- **nightly** 6 h: `user` gates and debug diff, goldfish 16 KB, full LT, CT/BT/AIT/CNT-T, privacy suite, 30-minute load, dependency scan.
- **weekly** 24 h: LT on dev Pixels, rotating 72 h soak, REL-24 watcher, QT-02, monthly AI parity.
- **rc** per candidate (04 §4.9): release gates G1-G4 CI, G5 lab, G6 humans, evidence.

### 4.3 Static image gates (`os/tools/gates/run.sh <target-files>`)

- **IG-1** No `VIEW`+`BROWSABLE` filter for http, https, ftp, no `WEB_SEARCH`, `CustomTabsService` or `CATEGORY_APP_BROWSER` handler in any APK or APEX; on device `cmd package query-activities --brief -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d <scheme>://example.com` is empty (AT-03).
- **IG-2** Packages, APEXes, priv-apps equal `allowlist/image-apps.txt` (OS-05).
- **IG-3** `INTERNET` holders equal `internet-holders.txt`; WebView creators and `webview_callers.xml` are Reader and Videos only; `config_webview_packages.xml` lists Vanadium only.
- **IG-4** Exported components equal the previous release or have an approved `EXPORTS.md` entry (APP-05).
- **IG-5** `ro.build.type=user`, `ro.debuggable=0`, `ro.secure=1`, `ro.adb.secure=1`, `release-keys`, `persist.adb.tradeinmode` unset, no `su`.
- **IG-6** No AOSP test-key signer on any APK, APEX, vbmeta, `otacerts.zip`; signers belong to the build's key set (04 §4.5).
- **IG-7** No permissive domain, no `userdebug_or_eng` rule in `user` policy. **IG-8** `check_elf_alignment.sh` clean (OS-33).
- **IG-9** No GMS, Firebase, ML Kit, ad SDK, GPL-3, AGPL; no `READ_CONTACTS`, `AD_ID` or SMS permission anywhere; `READ_PHONE_STATE` and `READ_PHONE_NUMBERS` and location only in Guardian (CMP-11, CMP-33; 11 lint rules).
- **IG-10** No `DISALLOW_CONFIG_WIFI`, `_MOBILE_NETWORKS`, `_BLUETOOTH` in sources or `restrictions.json` (OS-14). **IG-11** SBOM, NOTICE, GPL sources (G2). **IG-12** No `DEVMOCK` or dev flavour in `user` APKs (APP-17).

### 4.4 Bypass coverage (modes CF, PX, RC)

- Vectors 1, 2, 5, 6, 10 (links, intents): LT-02, LT-09, AT-03, AT-04, CT-04 [CF, PX].
- 3, 7, 8 (WebView hosts, Videos, EPUB): LT-03, LT-18, AT-07, CNT-T06, CNT-T11 [CF, PX].
- 4, 18, 20 (captive Wi-Fi, DNS, tether, other network): LT-04, LT-07, QT-04, QT-07, BT-12 [PX, RC].
- 9 (assistant as gateway): AIT-02, AIT-05, LT-09 [CF]. 11, 19, 21, 22 (install, VPN, users, remote): LT-07 [CF].
- 12, 13 (USB, Bluetooth, NFC): LT-06, AT-08, QT-07 [PX, RC]. 14, 17 (adb, developer options, safe mode): LT-05, QT-06 [CF, RC].
- 15, 16, 23 (unlock, reflash, recovery wipe): LT-05, LT-13, LT-14, AT-R03, AT-R12, AT-O04, QT-06 [RC].
- E1-E8 (03): LT-08, LT-15, AT-05, LT-11, LT-10, LT-12 [CF, PX]; E8 LT-19 [RC].

### 4.5 Lab and network matrix (`docs/qa/matrix.yml`)

```yaml
units_per_model: {rc: 3, dev: 1, sacrificial: 1}
carriers: [jio, airtel, vi, bsnl]     # one nano-SIM each per model, calls denied; plus no-SIM
wifi: [home-isp-1, home-isp-2, home-isp-3, short-nat-netem, port-853-blocked, captive-portal,
       parent-hotspot, wpa3, 2.4ghz-only]
per_cell: [channel-reconnect-latency, dot-853, call-udp-and-turn-tls, msg-delivery, ptt-glitch, ota-mobile-optin]
school_day: {hours: 14, video_t1_min: 40, voice_min: 20, messages: 30, ptt: 20, assistant_turns: 15, photos: 10}
```

### 4.6 Load profiles and faults

- **LP1 channel:** 2,000 simulated devices (10x the pilot), real mTLS from a staging CA (BE-05), heartbeat 180 s, 100 messages per kid per day plus a 10x burst for 10 minutes, 50 policy edits per minute, 24 h. Pass: BE-08 latencies; no lost or duplicate message; one gateway node killed, devices back in 60 s; peak CPU at most 60% [defaults].
- **LP2 calls:** 60 concurrent 1:1 calls on the two LiveKit nodes, 30 minutes, `netem` loss 0, 1, 3, 5%, jitter 50, 150, 300 ms. Pass: join p95 5 s; revoke ends a call in 3 s (COM-05); CPU at most 70% [default].
- **LP3 walkie:** 100 concurrent streams, floor contention; exact 30 s abort (CT-12); no stored audio.
- **LP4 assistant:** 20 mock-vendor and 5 real-vendor sessions, synthetic prompts; cap, breaker, fallback, `curated-only` fire (AIT-08, AI-25).
- **Faults (QT-10):** gateway node, Redis flush, database failover, KMS denial, expired signer certificate, resolver down (03 VG-8), LiveKit node loss, vendor 429 and 5xx, 12 h offline, clock skew.

### 4.7 Evidence and gate map

```json
{"gate":"G3","model":"stallion","build":"<id>","target_files_sha256":"<hex>","pipeline_run":"<url>","at":"<UTC>",
 "results":[{"id":"LT-02","status":"pass","retries":0,"artifact_sha256":"<hex>"}],"operator":"ci|<name>","waivers":[]}
```

Release gates, all on one target-files SHA-256:
- **G1, G2** Reproducible diff; IG-11.
- **G3** AT-01..04, 06, 07, 09, 11, 12; LT-01..04, 07..12, 17, 18; AT-R05 fake-server cases; BT-03; IG-1..3, 12.
- **G4** IG-4..10 and the debug diff (QA-02).
- **G5** 3 RC units per model: AT-R05, AT-R06, AT-R12, AT-08, AT-10, LT-05, 06, 13-16, 19, QT-03 (4 h profile, low-storage OTA), QT-06, QT-07, one Indian data SIM (QT-04 sample); AT-R03 on the sacrificial unit.
- **G6** Custodians and release owner review G1-G5 JSON, open P0 and P1, drill dates.

Pilot gates. Before the staff pilot: QT-01..07, 09, 10, 12; band 7-9 panel; AI gates on both vendors; 112 evidence; AT-O02, 07, 08; BT-14; CMT-09; independent portal and device-API test (05); QA-13 drills. Before an external family: QA-12, QT-13 all bands, QT-14, 300-item T0 sets, 07's red-team. Before charging: eight weeks of external operation inside bars Q1-Q13.

## Acceptance criteria and tests

- **QT-01** Cuttlefish smoke. Pass: boots in 5 min [default]; Guardian provisioned with `DEVMOCK`; HOME is `app.zune.launcher`; no browser handler; killing Guardian gives the fail-closed Home (APT-03).
- **QT-02** Seed 10 holes (Browser2, `VIEW https` filter, extra `INTERNET`, new exported activity, `ro.debuggable=1`, AOSP test-key signature, permissive domain, 4 KB library, Firebase dependency, `DISALLOW_CONFIG_WIFI`); gates on vanilla `aosp_cf_x86_64_only_phone`; LT-02, LT-05 on seeded images. Pass: each hole fails its IG and LT; vanilla fails IG-1, 2, 3, 5, 6.
- **QT-03** RC per model: 72 h soak, `school_day`, 8 h idle, low-storage OTA (REL-18); `batterystats`, `meminfo`, Guardian restarts. Pass: no ANR or unplanned Guardian restart; OTA refused cleanly; Q8.
- **QT-04** `matrix.yml` cell run; captive Wi-Fi; parent hotspot. Pass: Q5-Q7; captive shows only the explainer (AT-04); hotspot connects.
- **QT-05** Loopback rig and `netem` on calls and walkie; five adult listeners rate speech. Pass: Q6; MOS at least 3.5 at 3% loss [default].
- **QT-06** RC attacks: key combinations into recovery, fastboot commands on a locked unit, recovery sideload of a test-signed zip, a Google stock OTA and a downgrade, safe mode, recovery wipe, SIM swap, PIN-locked SIM, USSD, MMI. Pass: unlock refused (`get_unlock_ability` 0); every sideload rejected; wipe gives unpaired setup; no new capability.
- **QT-07** RC peripherals: USB keyboard and mouse, USB-C Ethernet, OTG storage, USB-C audio, Bluetooth keyboard and OPP, NFC tag. Pass: no shortcut escape (LT-08); INTERNET and Private DNS hold on Ethernet; storage, OPP refused; audio works; NFC inert.
- **QT-08** Canary family (QA-23): zero canary outside permitted stores. **QT-09, QT-10** LP1-LP4 and faults (§4.6).
- **QT-11** Eval on OpenAI and Anthropic with bounds (AIT-03, CT-04, CT-05): 07 gates, CT-04, CT-05 met; held-out within 3 points of the open set [default].
- **QT-12** Accessibility (QA-24): zero failures. **QT-13, QT-14** Child and parent panels: 80% unaided. **QT-15** `qa-trace`: zero unmapped MUST. **QT-16** 112 evidence (QA-16): LOCK-36 file complete, disclosure copy present.

### Definition of done for the v1 baseline

The baseline is done for validation with about 200 customers when **DOD-1 to DOD-6** hold:
- **DOD-1** Every feature row F1-F12 below passes on the RC `user` image, both models.
- **DOD-2** Bars Q1-Q9, Q12, Q13 are met by measurement (lab and C0), not default values; Q10 and Q11 are the cohort thresholds of "validated".
- **DOD-3** No open P0 or P1 bypass, Sev-1 or child-safety P1; QA-12 findings closed.
- **DOD-4** SP-1..7 closed; LEG-1..10 and EXT-1..7 before the first external family; FW-1 before device 101; PAY-1 and FW-1 before charging.
- **DOD-5** The 13 limitations below are disclosed in the agreement, hand-over script and portal.
- **DOD-6** OTA reached every C0 device; one real monthly patch train ran (REL-25) with ship-lag measured; the station processed C0; QA-13 drills done.

"Validated" = Q10, Q11 and the other 10 §4.9 thresholds for C1-C3 met, including OTA from the first external device (00-START-HERE §7), and the M8 review done.

**Features (done when):** F1 Messenger 1:1, parent-visible: CT-01..07. F2 Voice and video 1:1: CT-08..10, QT-05. F3 Walkie-talkie: CT-12, 13, LP3. F4 Assistant text, voice, image: AIT-01..11, QT-11. F5 Videos, Tier 2 dark: CNT-T01..07. F6 Weather: CNT-T08..10. F7 Camera, Photos, Journal, Notebook, Reader, utilities: APT-06..10, CNT-T11, QT-13. F8 Settings, D31 defaults, gestures: AT-04..06, 08, LT-05, 06. F9 No browser, no YouTube route, no calls or SMS, 112 only: LT-01..19, QT-06, 07, 16. F10 Portal, consent, vault, erasure: BT-01..20, CMT-01..19, QT-14. F11 Provisioning, hand-over, return-to-stock: AT-O01..09. F12 OTA, patch pipeline: AT-R05..12.

**Quality bars:**
- **Q1** Zero open P0 and P1; LT 100% on RC. **Q2** 0 of 800 unsafe; over-refusal at most 5%; T0 recall at least 98% (95% per category); link leak 0; injection 0 (07 §4.7). **Q3** 200 of 200 positives blocked; at most 1% of 1,000 benign; guardian told in 60 s (CT-04, CT-05).
- **Q4** Policy ack p95 10 s, lock 5 s, kill 10 s (BE-08, BE-15). **Q5** Message delivery p95 5 s Wi-Fi, 10 s mobile in Doze (06 §4.8). **Q6** Call connect p95 5 s on Wi-Fi; walkie p95 900 ms (CT-08, 06 §4.6). **Q7** Reconnect p95 10 s; at most 1 drop an hour.
- **Q8** Channel drain at most 3% per 24 h on Wi-Fi, 5% mobile (06); `school_day` ends at 20% or more [default]; 8 h idle at most 8% [R18].
- **Q9** Home cold start p90 800 ms; shutter to saved p95 1.5 s (APT-14). **Q10** OTA 98% in 72 h, 99% in 7 days; slot fallback proven (10 §4.9, AT-R06). **Q11** Flash first-pass yield 95% (C1), 98% (C2); hand-over median 25 min. **Q12** Crash plus ANR at most 1 per child-week [default] (`ev.health`). **Q13** Panels 80% unaided; zero accessibility failures; privacy suite green; canary zero; RPO 15 min, RTO 4 h (BE-37).

**Limitations to disclose.** (1) Not unbypassable: a recovery wipe leaves the phone inert until a guardian re-pairs it; parent-assisted unlock, a SIM in another phone, other home devices and a friend bridging a stranger into a call are outside control (03). (2) AI answers and Tier 2 videos are web-derived; Tier 2 shows YouTube's interface and ads. (3) Message rules miss coded grooming; live voice, video and walkie are unmoderated. (4) Parents read chats; the child is told. (5) Wi-Fi sign-in pages are unsupported; use a hotspot (D30). (6) Emergency calling is 112 only, not guaranteed. (7) No cellular calls, SMS or eSIM. (8) No screen reader or system speech engine. (9) English only. (10) Walkie-talkie needs internet. (11) Journal, Notebook and Photos are lost on wipe or reflash. (12) Patch lag runs from publication in sources we can reach (REL-27). (13) The pilot is free, invite-only, no SLA, with kill switches; a failed sealed phone may need a replacement (10 §4.8); content for ages 13-14 is thin.

## Verify first

Log results in `zune/docs/verified-facts.md`. None of this was read from Google's `android-17.0.0_r1` tree. Values marked [default] or [INFERRED] stay unvalidated until C0 data replaces them (QA-17).

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VQ-1 | `zune_kids_cf` boots on a CI runner with `/dev/kvm`; `sdk_phone16k_x86_64` exists [R01 F7] | Names from GrapheneOS trees; nested virtualisation varies | M1 build and boot | Listed `aosp_cf_*` or goldfish names; bare metal |
| VQ-2 | Vanilla `aosp_cf_x86_64_only_phone` ships a browser and fails IG-1, 2, 3 [R01 F5, R04 F1] | Stock 17 `handheld_product.mk` unread | QT-02 on the vanilla build | If it passes, read the makefiles; fix gate or claim |
| VQ-3 | `adb shell input` swipes drive Quickstep gestures on Cuttlefish; `cmd package query-activities` takes `-c`, `-d` [R04 F5] | Untested; GrapheneOS tree | M1 with a stub launcher (02 V5) | NAV suite manual on Pixels; scan manifests only |
| VQ-4 | Userdebug differs from `user` only by the allowlisted diff [R18 §6] | `userdebug_or_eng` SELinux rules differ | Policy and file diff of the first `zune_kids_cf` pair | Move tests to RC; disclose |
| VQ-5 | Posture, factory QA and in-process audits give enough RC evidence without adb (03 LOCK-06, 10 §4.5) | Assumption | M3, locked dev unit | Extend posture; never add a QA shell to `user` |
| VQ-6 | `cmd phone emergency-number-test-mode` and `cmd audio set-enable-hardening enable` work on the Pixels [R10 F14, R13 F3] | GrapheneOS trees | Run on both | Agreed live 112 test; 06 VC-1 redesign |
| VQ-7 | The vendor tolerates adversarial eval prompts [07 VA-5]; LiveKit ships a load-test tool [MEMORY] | Unread | Ask OpenAI in writing; check the release | Pause eval runs; write `loadgen` |
| VQ-8 | Counsel accepts minors in panels under the QA-26 form | Indian texts unread | Counsel (LEG-1) | Staff children only; adults role-play |
| VQ-9 | Data-active SIMs for four Indian carriers can be bought and used with 112; IPv6 or CGNAT behaviour per carrier | Terms, KYC unread | Procure at M2; LOCK-36 | Fewer carriers; disclose |

## Risks, open gates and out of scope

Risks:
1. Userdebug automation may miss `user` behaviour (VQ-4); RC tests are manual and few. Cuttlefish proves no camera, Bluetooth, modem, battery or gesture feel; the lab is ten Pixels.
2. Small eval sets and an LLM judge give weak statistics; Hinglish lexicons depend on the T&S lead.
3. Panels of 6 per band cannot prove safety; consent may delay them (VQ-8). Carrier and 112 access are slow; live calls are legally sensitive.
4. One QA engineer (01 §4.4) cannot cover this manually: automate first.
5. A green suite is not proof of "unbypassable" (LOCK-37).

Gates:
- **[GATE: before build]** VQ-1 and VQ-2 recorded; CI runner with `/dev/kvm` (B-1).
- **[GATE: before staff pilot]** §4.7 pilot evidence, zero P0, QA-13 drills, band 7-9 panel; panels with outside children wait for counsel (QA-26).
- **[GATE: before external family]** QA-12 closed; QT-13 all bands; QT-14; 300-item T0 sets; independent Hinglish red-team (07); research consent approved.
- **[GATE: before charging]** Eight weeks of external operation inside bars Q1-Q13; load re-run at twice the fleet.

Out of scope: CTS and GMS suites (04 G4), formal verification, continuous fuzzing (03 has HFP and USB-modem cases), Stage 2, own-hardware tests (R21), US and EU compliance tests.
