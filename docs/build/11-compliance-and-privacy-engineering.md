# Compliance and privacy as engineering requirements (India first)

## Purpose and scope

This section turns the India legal map [R19] into buildable requirements: each obligation gets a requirement ID, an owning component and a test. It is engineering input, not legal advice; each reading is the strictest defensible one, and counsel's written views (LEG-1) may change it. Basis tags: **P** statute or judgment text read through a GitHub mirror (Gazette and the 16 Dec 2025 DPDP corrigendum unread), **S** secondary, **M** memory, **I** inferred.

**Stage 1** = every MUST, live before the staff pilot unless a gate says later; counsel gates block the first external family, not the build. **Stage 2** = Significant Data Fiduciary readiness (India DPO, DPIA, audit), DigiLocker as default Rule-10 path, parent-key E2EE only if counsel clears IT Act s.69, CSAM hash matching, Indic notices, own-hardware certification [R21], US and EU.

Not covered (`docs/build/`): vault, ledger storage, sweeper, portal (`05-backend-and-parent-portal.md`); Guardian, SOS, 112 (`03-lockdown-and-guardian.md`); moderation, T&S operations (`06-communication.md`); assistant, vendor terms (`07-ai-assistant.md`); content licences (`08-content-videos-weather-reader.md`); crash reporter, setup screens (`09-core-apps-and-design-system.md`); agreement text, custody, station (`10-delivery-operations-and-pilot.md`); keys, OTA, GPL publication (`04-device-signing-ota-release.md`); gate register (`01-prerequisites-and-phases.md`); test execution (`12-testing-qa-and-acceptance.md`).

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision or report | Effect |
|---|---|
| D18, D23, R19 §2.1 | Child = under 18 (s.2(f)); bands tune UX and moderation, never a duty. R11 and R13 COPPA logic dropped. |
| D27 vs R19 §3, R07 | R19's "excerpts at 13+" and R07's 30-day transcripts rejected: guardians read full threads and AI chats in every band, child told. CMP-09 to CMP-11 and LEG-1 carry the s.9(3) exposure. |
| D27, Rule 8(3) vs R12, R13 | One retention table (05 §4.6) replaces 90 d, 180 d, 13 months, 30 d; erasure defaults to `seal`. |
| R11-R13 (COPPA, card consent, AB 1043, FCC, 988, NCMEC, carrier law) | Replaced: a card is not a Rule 10 method [R19 §2.1]; NCMEC becomes SJPU, police or cyber-crime-portal reporting [R19 §2.4]; carrier-of-record, CPNI, SMS-vault law gone (D19, D28), interception, 112, identifier tampering kept [R19 §2.2]; US and EU only as §4.4 notes; R11's "avoid India" is wrong [R19 §6]. |
| D29 vs R07, R19 §4.1 | OpenAI direct processes outside India (07): India-region inference becomes a disclosed s.16 transfer (CMP-28); Bedrock stays the in-country option (07 VA-7). |
| D31 vs R19 "SOS only"; D20 vs ss.5(3), 6(3) | Parent-set places plus the SOS fix, basis Part B(4) [R19 §2.1]. Child UI English; parent notices carry `lang`, Hindi only on EXT-7. |
| D25 | YouTube Tier 2 is a third-party disclosure: purpose `third_party_video` (08 CNT-10), absent from 05 BE-30. |
| 10 OPS-12 vs 10 §4.3 | OPS-12 forbids modem writes, §4.3 flashes Google's radio image: stock hash-pinned radio only; EFS, persist, IMEI never written (CMP-25). |

## Requirements

**Verification and consent (DPDP s.9(1), Rule 10, s.6)**
- **CMP-01 MUST** Apply every child-data duty to every enrolled child in every band; no code path branches a duty on `band`; `child` stores `birth_ym` only.
- **CMP-02 MUST** Run CMP-03 to CMP-19 from the first real child's data (C0, staff terms per SP-7), not from 13 May 2027 [R19 §2.1]; dev and staging stay synthetic (PRE-07).
- **CMP-03 MUST** Create no child profile, claim code, device seat or vendor call before a `guardian_verification` row (`staff_id` or `digilocker`, 05 BE-20) and a granted `account` consent exist. The device says "Got it", never "I agree" (COM-14, AI-02).
- **CMP-04 MUST** Verification stores method, inspector id, document type, document-number HMAC, date and notice version; never an ID image, number or card. The inspector confirms adult age and a name match to the invoice (10 H1).
- **CMP-05 MUST** Purposes: `account` (necessary), `visibility`, `ai`, `contact_pair`, `location`, `diagnostics`, `third_party_video`. Each is a separate per-guardian grant per notice version; nothing pre-ticked or bundled beyond `account` (row: §4.2).
- **CMP-06 MUST** Withdrawal is one action in `/account`, as easy as granting (s.6(4)); the server stops the purpose in 60 s, the device in 10 s via signed policy. Withdrawing `visibility` disables Messenger and Assistant.
- **CMP-07 MUST** Notices are versioned files `backend/gateway/notices/<purpose>/<version>.<lang>.md` (`en` always, `hi` once EXT-7 is decided); a changed notice needs fresh consent. The same directory holds the legal copy counsel drafts (privacy policy, parent terms and agreement per 10 §4.7, grievance page, intermediary rules) and the child-readable notices (grade 3, 09 APP-29); no legal text ships that is not a versioned file with a counsel sign-off recorded in `gates.md`.
- **CMP-08 MUST** A cross-family edge needs both guardians' `contact_pair` consent naming what each parent reads (COM-03); one family's erasure never touches the other's copy (COM-15).

**Strict-reading design (s.9(2), s.9(3), Rule 12)**
- **CMP-09 MUST** Build no behavioural profile: no per-child score, interest, mood, engagement or habit store. Flags are item-level (S1-S4, T0-T2); usage is per-app daily minutes for parent time rules.
- **CMP-10 MUST** Parent reading is the guardian's act: each vault read writes an audit row every guardian sees (BE-33); staff read content only by break-glass or T&S case (BE-28, COM-34); the child is told before the first message and AI turn and by a persistent header.
- **CMP-11 MUST** Only `app.zune.guardian` holds a location permission, for the SOS fix and, with `location` consent and `presence_on`, enter or exit events for parent-set places. No other coordinates leave the device; presence shows a child-visible indicator and expires at 30 days (CNT-23: Weather has none).
- **CMP-12 MUST** No engagement design (streaks, rewards, return-nudging notifications, autoplay): Rule 12 never lifts s.9(2) [R19 §2.1]. Each release records a `wellbeing` checklist signed by product and T&S leads.

**Retention, erasure, export (Rule 8(3))**
- **CMP-13 MUST** Retention equals 05 §4.6; do not shorten message, AI or log retention below 12 months until counsel narrows Rule 8(3) (VL-3).
- **CMP-14 MUST** Withdrawal or erasure is applied (views removed, processing stopped) within 24 h [default] of step-up. Default `seal`: unreadable to portal and services, opened only by break-glass on legal process; `delete_now` only on counsel's instruction; a hold prevails (BE-34).
- **CMP-15 MUST** Export (JSON ZIP, one family) is ready within 24 h; guardians can correct display name and `birth_ym` in `/account`.

**Security, breach, logs (Rules 6, 7, CERT-In)**
- **CMP-16 MUST** `docs/compliance/rule6-matrix.md` maps each Rule 6 safeguard (encryption, access control, logging, backup, vendor terms) to a requirement and evidence, re-signed each cohort (SP-2).
- **CMP-17 MUST** `admin` opens an `incident` that starts: CERT-In 6 h from detection; Board intimation once a personal-data breach is confirmed (12 h target [default]); Board detailed report at 72 h [R19 §2.1]; guardian notices. Overdue timers page `sec` and the founder.
- **CMP-18 MUST** Logs are searchable 180 days in India, kept 12 months, free of personal content; hosts use Indian NTP (BE-36).
- **CMP-19 MUST** Publish a resident-in-India grievance officer, the DPDP contact (Rule 9) and `security@`, `privacy@`, `grievance@` in `/account` and ZuneSettings About. Acknowledge in 24 h, resolve in 7 days [default, VL-5] (Rule 14 limit 90 days); each case is an `ops.legal_case`. Also publish `/.well-known/security.txt` and a short vulnerability-disclosure policy (safe harbour for good-faith reports, 90-day coordination) pointing at `security@`; reports open an RB-1 case.

**Intermediary, POCSO, requests**
- **CMP-20 MUST** Treat the messenger as a social media intermediary [R19 §2.4]: closed graph only (COM-01, COM-02); rules and privacy policy in portal footer and About.
- **CMP-21 MUST** Cases `takedown_order` (3 h) and `ncii_csam_complaint` (2 h) [S, VL-5] have a named 24x7 on-call (COM-29). Action: set items `suppressed` in every family copy plus a `hold`; never hard-delete evidence.
- **CMP-22 MUST** A reporting officer, deputy and counsel are on call. Report to the SJPU, local police or cyber-crime portal, never NCMEC alone [R19 §2.4]; decide within 24 h [default] of a possible offence; never auto-report a child sender; name the founder and officer in `gates.md`.
- **CMP-23 MUST** Government and police requests enter only through `legal@`, are verified by counsel, need two staff approvals, cover only the named child, family and period, are logged, and notify the family unless the order forbids. No direct database access; no interception capability in Stage 1.

**Telecom and handset**
- **CMP-24 MUST** No child identifier is a phone number, IMEI or plaintext serial (serial = HMAC). Parents use passkey plus email OTP; `auth.sms_otp` stays false until counsel answers R19 Q11 (TIUE) and DLT is registered (BE-26).
- **CMP-25 MUST** v1 writes no RF, IMEI, EFS or persist data; the radio image is Google's, hash-pinned (OPS-12, REL-21); the job log is the evidence; no hardware is sold or imported (D15).
- **CMP-26 MUST** Triple-press SOS and the 112-only path pass the field test before the staff pilot; archive the evidence for counsel (LOCK-35, LOCK-36); copy says emergency calling is not guaranteed (LOCK-37).
- **CMP-27 SHOULD** Call Walkie internet push-to-talk, never radio [R19 Verification]. A reflash is a software change, not manufacture: BIS CRS and WPC ETA bind makers and importers, though Telecom Act s.2(q) counts software integral to equipment [R19 §2.3, I]. Review these and ITSAR quarterly in `gates.md`; build nothing in v1.

**Processors, AI, payments**
- **CMP-28 MUST** Personal data at rest stays in ap-south-1 or ap-south-2 (BE-03). Vendor processing abroad needs a register row with `approved_for_child_data=true` (s.8(2), s.16), named in the `ai` notice; `ai-gateway` checks the flag per request and refuses with `vendor`.
- **CMP-29 MUST** Each vendor has a row in `docs/compliance/vendor-register.md` (service, data classes, region, retention, DPA date, sub-processors, `approved_for_child_data`, exit); it is `verified` before real child data flows: DPA, written zero-retention or equivalent, no training (SP-1, LEG-7). Rows: AWS (including CloudFront and the India-region e-mail sender), OpenAI, Anthropic, Open-Meteo, MET Norway, Google (YouTube Tier 2 is a third-party disclosure), the browser Web Push services that carry portal notifications (payloads hold no child data, 05 BE-40), the DLT SMS provider and payment aggregator when used, the helpdesk tool (10 §4.11) and the paging service (05 BE-49).
- **CMP-30 MUST** The AI-02 disclosure runs every session; no image, video or voice generation; TTS stays on device and ephemeral; counsel decides if TTS is synthetic audio under the 2026 labelling rule (VL-11).
- **CMP-31 MUST** Before charging: no payment data in Zune systems; an Indian aggregator hosts checkout; Zune adds a reminder to the issuer's 24 h e-mandate notice; GST invoices; DLT sender. Until PAY-1, `entitlement` stays `free_pilot` (BE-44).

**Inventory, not collected, terms**
- **CMP-32 MUST** `docs/compliance/data-inventory.yaml` is the only data map; `compliance-lint` (§4.2) fails CI on any undocumented column, vault class, event kind, permission, egress host or dependency.
- **CMP-33 MUST** Never collect: analytics, ad or crash SDKs, advertising IDs, address books, phone numbers, IMEI, location history, call, walkie or voice audio, photos except an explicit share or AI image (07), face or voice templates, behavioural profiles; no third-party portal scripts.
- **CMP-34 MUST** Only a verified adult guardian contracts or consents (minors cannot contract [M]); store `agreement_version` (OPS-06). Copy lint blocks "100% safe", "unbypassable", "no internet", "no YouTube", "social network".
- **CMP-35 MUST** Each release ships SBOM, NOTICE and GPL source (04 G2, REL-28); CI rejects GPL-3 and AGPL components [R11 F12].

## Design and build instructions

### 4.1 Obligation map

| Obligation [basis] | Requirements | Owner | Test |
|---|---|---|---|
| DPDP s.9(1), Rule 10 [P] | CMP-01 to 05, 08 | `gateway`, `admin` verifier | CMT-01, 02, 05 |
| ss.5(3), 6(3), 6(4) [P] | CMP-06, 07 | `gateway`, portal | CMT-02, 03 |
| Rule 8(3), erasure [P; M] | CMP-13 to 15 | `vault` | CMT-04 |
| s.9(2), 9(3), Rule 12 Part B [P] | CMP-09 to 12, 33 | `policy`, `vault`, `ai-gateway`, Guardian | CMT-05 to 07 |
| s.8(1)-(2), s.16, Rule 13(4) [P] | CMP-28, 29 | `ai-gateway`, `admin` | CMT-08 |
| Rules 6, 7; CERT-In [P; S] | CMP-16 to 18 | `admin`, infra | CMT-09 |
| Rules 9, 14; IT Rules grievance officer [P; S] | CMP-19 | `gateway`, portal | CMT-10 |
| IT Rules intermediary, removal clocks [S] | CMP-20, 21 | `comms` T&S, `admin` | CMT-11 |
| POCSO ss.19-21, Rule 11 [P judgment] | CMP-22 | `comms` T&S | CMT-12 |
| IT Act s.69 [M]; Telecom Act ss.20(2), 42(2)(b) [P] | CMP-23 | `admin` | CMT-13 |
| Telecom Act ss.3, 42; TIUE; SIM binding [P; S] | CMP-24 | `gateway` | CMT-14 |
| Panic Button and GPS Rules 2016 [M]; s.42(3)(c); BIS, WPC, ITSAR [S] | CMP-25 to 27 | Guardian, station | LT-16, CMT-15 |
| IT Rules synthetic-media labelling [S] | CMP-30 | `assistant`, `ai-gateway` | CMT-16 |
| RBI e-mandate, GST, DLT [S; M] | CMP-31 | `admin` | PAY-1 |
| Consumer law, Contract Act s.11 [M] | CMP-34 | ops, copy | CMT-17 |
| OSS licences [M] | CMP-32, 35 | release | CMT-18 |

**s.9(3) strict-reading argument.** s.9(3) bars tracking and behavioural monitoring of children, and no Fourth Schedule row covers parental control or messaging [R19 §2.1]. The defensible reading: the parent is part of the child's Data Principal (s.2(j)(i)) and consents, so Zune is a conduit for the parent's reading, not a monitor. Hence every read is a guardian act (CMP-10); Zune's own processing stays inside Part B(4) and B(5) (SOS and place safety, keeping harmful content from the child), item-level only (CMP-09, 11); the child is told. Fallbacks if counsel says no: shorter content retention; summaries plus flagged excerpts at 13-14 (R19 §3); a s.9(4), s.9(5) or s.17(5) exemption request [R19 §2.1]. A `visibility_mode` column (default `full`) makes a fallback a policy change [R13 §3.2].

**Localisation.** No blanket localisation applies; Rule 13(4) reaches only data specified for Significant Data Fiduciaries [R19 §2.1]. Default: all rest data in India, vendor processing abroad disclosed (CMP-28); if counsel requires, in-country AI via Bedrock (amends D29).

### 4.2 Consent row, data inventory, lint

```json
{"purpose":"visibility","action":"grant|withdraw","guardian_id":"..","child_id":"..","verification_id":"..",
 "notice_v":"visibility-2026-10-01","lang":"en","step_up":true,"at":"..","prev_hash":"..","hash":".."}
```
It extends 05's `consent_ledger` (BE-30).

```yaml
# zune/docs/compliance/data-inventory.yaml  (one row per data element)
# required: id class purpose basis store region processors retain roles child_told erase source
- {id: msg.body, class: message_content, purpose: visibility, basis: "s.9(1) consent; Part B(5) [counsel]",
   store: zune-vault.item, region: ap-south-1, processors: [aws], retain: 12m,   # equals vault config
   roles: [guardian_a, guardian_b, break_glass], child_told: true, erase: seal, source: "R13 §4.1"}
# zune/libs/testing/compliance-lint/rules.yaml  (every merge request; also scans schemas, ev kinds, manifests, egress.yaml, lockfiles)
deny_deps: [com.google.firebase, com.google.android.gms, com.google.mlkit, io.sentry, com.adjust, com.appsflyer]
deny_licences: [GPL-3.0, AGPL-3.0]
deny_perms: {all: [AD_ID, READ_CONTACTS, READ_SMS, RECEIVE_SMS, SEND_SMS],
             except_guardian: [READ_PHONE_STATE, READ_PHONE_NUMBERS, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION]}   # READ_SMS, RECEIVE_SMS, SEND_SMS denied everywhere (D19, 03 LOCK-32)
```

### 4.3 Runbooks

Severity (every "Sev-n" in 04, 05, 10 and 12 means this): **Sev-1** child-safety harm or credible risk, personal-data exposure, key or signing compromise, fleet-wide brick or Guardian outage, a successful P0 bypass; **Sev-2** a single-family safety or data issue, or an outage of channel, OTA, AI or portal over 1 h; **Sev-3** degraded feature without safety effect; **Sev-4** cosmetic or request. Response targets [default]: Sev-1 15 min 24x7, Sev-2 1 h, Sev-3 next business day. Files `docs/compliance/runbooks/RB-1..5.md`; clocks are timers on `ops.incident(id, detected_at, certin_due_at, board_due_at, principals_notified_at, state)` and `ops.legal_case(id, kind, received_at, due_at, owner, counsel_ref, hold_id, state)`.

| RB | Trigger | First 15 minutes | Clocks and decisions | Output |
|---|---|---|---|---|
| 1 Breach | Suspected unauthorised access or disclosure, audit-verifier failure (BE-35), key loss, vendor notice | Open `incident`; contain (revoke sessions, rotate keys, kill level per 10 §4.10); hold logs | 6 h CERT-In report by `sec` lead [channel UNVERIFIED]; on confirmation Board intimation via counsel; tell each affected guardian what, when, which data; 72 h Rule 7 report; report when unsure | Timeline, 72 h postmortem, new test |
| 2 Child safety | S3 or S4 (06), T0 abuse or grooming (07), suspected CSAM at the image screen (AI-20), guardian report | Hold both copies (COM-32); quarantine, never forward; page the reporting officer | Counsel within 2 h; decide within 24 h; file with SJPU, police or cyber-crime portal; T&S decides guardian notice within 1 h (a guardian may be the risk); a child sender is a victim first | Receipt id, signed evidence export |
| 3 Removal | Government or court order, NCII or CSAM complaint | Log `legal_case`; on-call verifies the requester | 3 h orders, 2 h NCII and CSAM [S]; suppress in all copies plus hold; reply with receipt | Receipt; items stay held |
| 4 Official request | Police request, court, interception or blocking order, Board notice | Route to counsel; send nothing | Counsel verifies authority and scope; two staff approvals; minimum scope; family told unless prohibited; preservation request = hold only | Disclosure log, order copy |
| 5 Outage or bad release | Sev-1 or Sev-2 service outage, bad OTA, bad policy bundle, vendor withdrawal (AI, YouTube, LiveKit), certificate or signer expiry | Open `incident`; stop rollouts (10 L3, `halt:true`), roll forward only; move AI to the fallback or `curated-only`; start the BE-49 notice | Guardians told within 2 h for Sev-1 and Sev-2; engineering on-call per BE-49; DR promotion only on the BT-14 criteria | Status notice, 72 h postmortem, new test (QA-04) |

### 4.4 Later duties and markets

Not built, not launched (D18): amended COPPA, California AB 1043 age signal (2027-01-01), TAKE IT DOWN Act, EU CRA Class I, GDPR Art. 8, UK Online Safety Act [R11 F1, F2, F7, F9; mostly S]. Hooks kept: `birth_ym` only, versioned notices, per-region kill switch, SBOM, `security@`.

## Acceptance criteria and tests

`CMT-nn`; 12 runs them; drills are tabletop with a timer.

- **CMT-01** No claim code, child row or vendor call without a verification row and `account` consent; the table holds no ID image or number.
- **CMT-02** Each purpose refuses its feature without a `granted` row; withdrawal stops it in 60 s server-side and 10 s on the device; the chain verifies.
- **CMT-03** Every purpose has an `en` notice (`hi` if EXT-7 requires); a changed notice blocks the purpose until reconsent.
- **CMT-04** Erasure applies within 24 h; `seal` content is unreadable to portal and services; a staging clock plus 12 months sweeps it unless held; Family A's erasure leaves Family B's copy; export holds one family.
- **CMT-05** No consent, retention or verification code reads `band`; no per-child score, interest or mood column exists; every parent read has an audit row; the build has a `wellbeing` checklist.
- **CMT-06** `aapt` shows a location permission only in Guardian; presence is off by default; no coordinates in logs or vault except parent-set places (encrypted) and the SOS fix.
- **CMT-07** Dependency, permission and DNS scans find no denylisted SDK or advertising ID; the portal makes zero third-party requests (BT-10).
- **CMT-08** With the register flag false, prod `ai-gateway` sends nothing and returns `vendor`; the `ai` notice names vendors and regions.
- **CMT-09** Breach tabletop at 02:00 IST: CERT-In draft within 6 h, Board intimation within 12 h, guardian notices, 72 h report; a log query spans 180 days; `chrony` shows an Indian source; each Rule 6 matrix row has evidence.
- **CMT-10** Grievance mail is acknowledged within 24 h and closed within 7 days; `/account` shows the officer and contacts.
- **CMT-11** A simulated order and NCII complaint: items suppressed in all copies within 3 h and 2 h, hold set, nothing deleted.
- **CMT-12** S4 tabletop: counsel within 2 h, decision within 24 h, dry-run police-portal report, no child auto-report, evidence hash verifies.
- **CMT-13** A simulated police request needs two approvals, has no direct database path, is logged, and notifies the family unless flagged.
- **CMT-14** No MSISDN, IMEI or plaintext serial column exists; `auth.sms_otp` is false.
- **CMT-15** Twenty station jobs show no write to EFS, persist or IMEI and a radio hash equal to the pinned build; LT-16 passes.
- **CMT-16** Each assistant session carries the disclosure; no generation endpoint is called; the VL-11 TTS decision applies.
- **CMT-17** Copy lint finds no banned phrase, no "radio" in Walkie copy, and the emergency-not-guaranteed line (LOCK-37).
- **CMT-18** An undocumented column, permission, egress host or GPL-3 dependency fails CI; each release has an SBOM and NOTICE.
- **CMT-19** Outage tabletop with a bad OTA and a forced Sev-1: on-call paged within 5 minutes, rollout halted, guardians notified within 2 h, postmortem filed within 72 h (RB-5).

## Verify first

Nothing below was read from Google's tree. Log results in `zune/docs/verified-facts.md`.

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VL-1 | DPDP texts, rule and Part B numbering, 13 May 2027 commencement are as cited; no country is notified under s.16 against US, EU or UAE processing [R19 §2.1, P] | Mirrors; corrigendum unread | Counsel reads Gazette, corrigendum, MeitY notices | Re-map §4.1; a date moves the schedule, not the build; in-country AI (07 VA-7) |
| VL-2 | Staff-inspected ID, stored record and email OTP meet Rule 10; a card does not [R19 Q2, I] | Illustrations favour an authorised-entity reference | Counsel | DigiLocker mandatory; external families wait (05 V6) |
| VL-3 | Rule 8(3) covers message content; `seal` satisfies withdrawal and erasure [R19 Q4] | Scope ambiguous | Counsel | Default `delete_now`; shorter content retention |
| VL-4 | Parent reading is consented processing, not s.9(3) monitoring or interception (Telecom Act s.42(2)(b), IT Act s.69); B(5) covers safety screening, B(4) parent-set places [R19 Q1, Q6, Q12, I] | No guidance or Board ruling | Counsel; MeitY dialogue | §4.1 fallbacks; founder revisits D27 |
| VL-5 | CERT-In direction of 28 Apr 2022 (6 h, 180 days in India, NIC or NPL time) and IT Rules 2026 amendment (in force 20 Feb 2026; 3 h removal, 2 h NCII and CSAM, 7-day grievances, resident officer) [R19 §2.4, S] | Secondary; partly illegible | Counsel reads both | Adjust RB-1, RB-3, BE-36, `due_at`; keep hold |
| VL-6 | POCSO ss.19-21 and Rule 11 bind us as an intermediary; channel; s.21(2) exposure [R19 §2.4; judgment P] | Statute text unread | Counsel (R19 Q7) | Change RB-2 owner and clock; keep hold |
| VL-7 | 2026 DoT authorisation, radio-equipment possession, user-identification and 2024 interception rules do not reach the messenger, calls or custody of customers' phones [R19 Q11] | Texts unread | Counsel | Authorisation, or staff phones only (10 VO-12) |
| VL-8 | Panic Button and GPS Rules 2016 require a triple-press panic call and cover a voice-off handset [R19 §2.2, M] | Scope unread | Counsel; 03 VG-11 | Keep SOS (LOCK-35); disclose |
| VL-9 | The station can show EFS, persist, IMEI untouched; Google's radio image counts as unmodified [R19 §4.1, I] | Pixel mechanics from mirrors | Z2 fastboot transcripts, sacrificial unit | Rely on the command-allowlist log; tell counsel |
| VL-10 | Reported: 28 Sep 2026 Supreme Court statement, Karnataka under-16 ban, MeitY draft IT Rules, SIM-binding date, username notices [R19 §2.2, §2.4, S] | Sources blocked | Read order, notices, circulars | Stop external families (EXT-1); re-scope under-16 messaging |
| VL-11 | TTS audio is outside synthetic-media labelling; RBI e-mandate (21 Apr 2026: Rs 15,000, 24 h issuer notice), aggregator, GST threshold, DLT [R19 §2.4, §2.5, S; M] | Secondary | Counsel; read at PAY-1 | Audible TTS disclosure; PAY-1 stays open |
| VL-12 | The [default] clocks (24 h erasure, 12 h Board target, 24 h acknowledgement, 7-day resolution, 24 h POCSO decision) satisfy the law; only a parent can contract (Contract Act s.11 [M]) [I] | Chosen here | Counsel | Tighten the config |

## Risks, open gates and out of scope

Risks:
1. s.9(3) exposure (critical, up to Rs 200 crore [R19]) is accepted for the pilot on D27; counsel decides at LEG-1. s.9(5) "verifiably safe" is the nearest statutory route [R19 §2.1].
2. A rule barring under-18 accounts could capture the messenger (VL-10); stay closed and family-managed.
3. Unread 2026 telecom rules (VL-7) may require authorisation or bar flashing customers' phones.
4. The vault is a breach honeypot (05 risk 1); English-only notices may fail ss.5(3), 6(3).
5. T&S and security staffing is open (EXT-3); CMP-21 to CMP-23 fail without it; POCSO s.21(2) exposes the founder.

**Open counsel gates** (block the first external family, not the build; IDs per 01):

| Gate | Question | Posture while open |
|---|---|---|
| LEG-1 s.9(3) | Parent reading; B(4), B(5); s.9(5) [R19 Q1, Q12] | Strict-reading build; staff cohort only |
| LEG-1 classification | Messenger as intermediary; Karnataka, IT Rules proposals [R19 Q5, Q13] | `comms.cross_family_external=false` (COM-30) |
| LEG-1 interception | Parent access vs Telecom Act, IT Act s.69 [R19 Q3, Q6] | Dual consent; no interception capability |
| FW-1 | Google's written firmware answer | 100-device cap; no external family (01 §4.6) |
| LEG-4 | Bailee, consumer, custody terms; custody of customers' radio equipment [R19 Q8, Q9; 10 VO-12] | Staff phones only |
| EXT-2 | Name clearance | Codename, neutral domain |
| LEG-2, LEG-3, EXT-7 | Indian entity and resident officer (A11); Rule 10 and Rule 8(3) readings (VL-2, VL-3); Hindi parent notices [R19 Q10] | Staff-ID flow, `seal`, `lang` field ready |

- **[GATE: before build]** None legal. The counsel brief and R19 questions go out by W2 (01 PRE-18); the inventory and `compliance-lint` skeleton exist by Z1.
- **[GATE: before staff pilot]** SP-1 (data map, vendor register, retention), SP-2 (CMP-16 to CMP-18), SP-3 (CMT-09, 11, 12 drills), SP-4 (CMP-26), SP-7; CMT-01 to CMT-10 and CMT-13 to CMT-15 pass; reporting officer, T&S lead and grievance mailbox named.
- **[GATE: before external family]** LEG-1 to LEG-10, EXT-1, EXT-2, EXT-3, EXT-7, FW-1 or counsel's written view on the 100-device footing (01 PRE-20); VL-1 to VL-4 and VL-7 closed or a founder exception recorded in `gates.md`.
- **[GATE: before charging]** PAY-1 (CMP-31 built, VL-11 read), FW-1, consumer terms from counsel.

Out of scope: legal advice and contract text; US and EU builds; own-hardware certification [R21]; Significant Data Fiduciary programme; E2EE; DPIA; payment code.
