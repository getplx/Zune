# Flash-and-deliver service, installer, intake and the staged pilot to ~200 users

## Purpose and scope

How a parent's own Pixel 10a (`stallion`) or 9a (`tegu`) becomes a locked, enrolment-ready Zune phone and reaches the family (D15, D16), and how about 200 families are onboarded in Bengaluru under gates (D21). **Stage 1** = in-person service, `zune-station` CLI (production) and WebUSB installer (station mode), QA and sealing, hand-over, return-to-stock, four cohorts, kill levels, support. **Stage 2** = self-install, remote-guided install, eSIM, price and payment, own hardware.

Not covered (`docs/build/`): image (`02-os-image-and-product.md`); Guardian, `service_unlock`, SOS (`03-lockdown-and-guardian.md`); keys, bundle signing, OTA, FW-1 flag (`04-device-signing-ota-release.md`); enrolment API, consent ledger, kill-state storage (`05-backend-and-parent-portal.md`); T&S (`06-communication.md`); legal text (`11-compliance-and-privacy-engineering.md`); test execution (`12-testing-qa-and-acceptance.md`); milestones, gate register (`01-prerequisites-and-phases.md`).

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision or report | Effect |
|---|---|
| D17, 04 REL-01 | Only `stallion` and `tegu`; Fairphone (R17, R18) and R20's Pixel 9 family and 8a dropped. |
| D21, 01 | C0 12, C1 30, C2 70, C3 88 (cumulative 12/42/112/200); R20's 90 sums to 202. |
| R19 vs R20 | R19 wins: invite-only, free until LEG-10, PAY-1, FW-1; R20's public funnel and prices unused. |
| D15 vs R18, R20 | No loaners or mail-in-with-spare; 4-6 company-owned replacement phones only with EXT-5 (PRE-14). |
| D18, D19, D28 | R18's CTIA check, US carrier locks, COPPA, USD, SMS tests, live 911 test become GST invoice, KYM, India SKUs, DPDP consents, INR, 112 by test mode. |
| R17 vs R18 | CLI is production for a 4-phone cell; WebUSB runs station mode on one phone, sharing `core`. |
| R18 "factory mode" app | Replaced by a Guardian FACTORY state entered by a single-use signed token (OPS-14); an always-present app is a bypass surface [R18]. |
| R18 return-to-stock, serial HMAC | Service-unlock exists before C0 (OPS-17). 05 BE-19 needs a stable `serial_hmac`: backend KMS HMAC, no serial in station logs. |
| R20 vs R18 | R20 support hours replace one business day; USD 85-125 and INR 1,850 become ceiling and floor. |
| D24, D27, D30, D31 | Guardian becomes Device Owner at claim; hand-over tells the child what parents see; no Wi-Fi sign-in pages; USB is charging only, so QA reports travel over Wi-Fi. |

## Requirements

**Eligibility and intake**
- **OPS-01 MUST** Service only `stallion` and `tegu` units whose model number is in `station/config/skus.yml` (India SKUs from the Z2 dev units); refuse all others.
- **OPS-02 MUST** Run the §4.1 hard checks on every phone, record pass or fail, return a failing phone unflashed. Never bypass FRP, accounts, MDM or carrier locks [R18 F11].
- **OPS-03 MUST** Never store or log an IMEI, serial, number, screen content or PIN: KYM is a boolean plus timestamp; the backend keeps `serial_hmac` only. Staff never unlock a customer phone: the parent removes accounts and screen lock, then resets it in front of staff.
- **OPS-04 MUST** Intake modes: in person (C0, C1); new-in-box phone shipped to us from the retailer (from C2); used-phone courier only in C3 and after EXT-5; returns by insured courier.
- **OPS-05 MUST** Custody: tamper-evident bag, exterior photos only (no screen, serial, IMEI) kept 30 days [INFERRED], locked store, at most 72 hours to hand-over, bailee's customers insurance before C1.
- **OPS-06 MUST** An adult guardian signs the §4.7 agreement and erase consent before staff power the phone beyond the reset; minors never sign [R19 §2.3]. The job stores `agreement_version`.

**Station**
- **OPS-07 MUST** The station holds no private key or long-lived token: public `bundle` keys, pinned platform-tools and signed bundles only; SSO session token in memory only (05 BE-28; 04 REL-12).
- **OPS-08 MUST** Every `fastboot` call carries `-s` for the job's phone (serial, or USB path where the serial changes between modes); a mismatch aborts; one host-wide lock until AT-O02 passes.
- **OPS-09 MUST** `flashing unlock` and `lock` run only after the operator types the last 4 serial characters shown with slot and model and presses the phone's confirmation [R18 F1].
- **OPS-10 MUST** Before the first wipe verify platform-tools SHA-256 and fastboot at least 35.0.1 [R18 F5], the ed25519 `manifest.json` signature (two `bundle` keys accepted during overlap), every file SHA-256, expiry, and key set equal to the station's (`dev|pilot|prod`).
- **OPS-11 MUST** Block, never warn: `product` not the bundle model; bootloader, baseband or anti-rollback above the bundle floor; `get_unlock_ability` not 1; job 101 or higher while `fw1_closed` is false (04 REL-22).
- **OPS-12 MUST** Run only the §4.3 commands: no write to modem, `persist` or IMEI partitions, `erase` only `avb_custom_key` and userdata via `-w` (04 REL-07), no exploit unlock. Keep an append-only job log (§4.4), no personal fields.

**QA and sealing**
- **OPS-13 MUST** `SEALED` only when every §4.5 check passes; a failure reruns once, then `BLOCKED` with a reason code.
- **OPS-14 MUST** Factory QA starts only from a single-use signed `factory_qa` token (TTL 30 minutes) that Guardian accepts while the phone has no claim blob and the server shows no claimed device for its `serial_hmac`; sealing consumes it (VO-6).
- **OPS-15 MUST** Locked-state proof: `attest` (04 REL-08), Guardian's signed "OEM unlocking off", and `get_unlock_ability` = 0 on every C0 phone and a one-in-five sample later [INFERRED]. No live 112 call at the station: test the Emergency screen and SOS countdown, then cancel (field test: LOCK-36).

**Hand-over and recovery**
- **OPS-16 MUST** Ship sealed but unenrolled, parent present; the claim code goes only to a `verified` guardian after consents, single use, matched to the ticket's family (05 BE-18, BE-20). Median visit at most 25 minutes including the 10-minute onboarding [R20 §4.6].
- **OPS-17 MUST** Service-unlock (03 LOCK-20; 04 §4.7) is built and rehearsed on two sacrificial units per model before C0. Only exception: C0 staff phones left with OEM unlocking on, flagged `oem_unlock_exception`; none from C1.
- **OPS-18 MUST** Return-to-stock is free to every pilot family at any time (§4.8), target two business days [INFERRED]; each unbrick-ladder rung has an owner and time limit.

**Pilot, support, cost**
- **OPS-19 MUST** A cohort opens only after the previous cohort's §4.9 gates are recorded in `zune/docs/milestones/`; C2 is flashed in two waves, to cumulative device 100 and then after FW-1 closes.
- **OPS-20 MUST** Invite-only and free: single-use invite codes; no public page, waitlist, marketing or payment before LEG-10, PAY-1, FW-1 (01 PRE-19, PRE-20).
- **OPS-21 MUST** Stop-ship (freeze new flashes in scope, apply a §4.10 level): a route to a browser or YouTube outside Videos Tier 2, an unapproved contact, a successful bypass, an unrecovered brick, a data exposure, a key compromise. Kill levels are drilled on staging and staff phones before C0 (SP-5), timed.
- **OPS-22 MUST** Support: English, 10:00-20:00 IST Monday-Saturday, first response within 4 business hours [R20 §4.7, INFERRED]; child-safety and SOS to T&S 24x7 (06 COM-29); check-ins on days 3 and 14 [R18]; playbook §4.11; never ask for a PIN.
- **OPS-23 MUST** Measure cost per device monthly against §4.12 (budget INR 12,000 per flashed device until C0 measures it). No non-staff family is invited until §4.13 is verified by a named owner and signed by the founder.

## Design and build instructions

### 4.1 Customer journey and hard checks

1. Invite code, then a text-only form; documents are inspected, never copied (ship-to-us invoices travel with the phone).
2. Intake visit (about 20 minutes [INFERRED]): `verifier` inspects the guardian's government ID (05 BE-20: `staff_id`, no ID image); the parent signs §4.7, registers a passkey and grants consents in `/setup`; staff run H1-H7; the parent removes accounts, then resets the phone.
3. Service, 90-120 minutes [R18, INFERRED]; hand-over (§4.6).

| Check | How | On fail |
|---|---|---|
| H1 Model, ownership | `product` is `stallion` or `tegu`; model number in `skus.yml`; original Indian GST invoice [R20 §2.1] with the guardian's name (or signed gift declaration) and the phone's serial | Refuse |
| H2 KYM | Sanchar Saathi KYM by SMS to 14422; record pass or fail | Refuse |
| H3 Accounts, FRP, MDM | After the reset the wizard asks for no prior account; no "managed by" | Return unopened |
| H4 OEM unlock | Toggle enabled on lab Wi-Fi (carrier check needs internet [R18 F1]); `get_unlock_ability` 1; never inferred from SIM-unlock [R18 F2] | Return |
| H5 Firmware | Not above bundle floors (OPS-11) | Hold list |
| H6 Battery, keys | Not swollen; health at least 80% (VO-8); power and volume keys work | Return |
| H7 SIM | Nano-SIM tray present; parent keeps the SIM; eSIM unusable (no LPA [R20]) and may be lost on reset [R18 F10] | Disclose |

### 4.2 Station layout and configuration

Cell: bare-metal Ubuntu 24.04, 16 GB RAM, 500 GB SSD, direct rear USB ports or PCIe USB cards, no hubs or VMs [R17 F5], certified short cables, lithium-safe cabinet, lab AP with internet plus a hand-over guest SSID, slots A-D labelled to USB paths, Chromium, test SIMs.

```
zune/station/
  core/    TypeScript, isomorphic: manifest.verify, rules (OPS-11), job states, log schema, FastbootTransport
  cli/     zune-station (Node, drives pinned platform-tools); adapters/{stallion,tegu}.ts
  web/     WebUSB installer, station mode (fastboot.js, MIT); Stage 2: self-install
  config/  station.yml  skus.yml  bundle_pub.pem{,.old}  qa-plan.yml
  tests/vectors/   fake-fastboot transcripts, refuse cases; both transports must pass
```
```
zune-station doctor | bundle verify <dir>
zune-station job new --ticket <qr> --slot A --bundle <id>
zune-station job preflight|flash|qa|seal|handover|rts --job <id>     # resumable
# station.yml: jobs.fw1_cap: 100  fastboot.min_version: 35.0.1  lock.mode: host  qa.token_ttl_min: 30
```
States: `INTAKE_OK, PREFLIGHT, UNLOCKED, FLASHED, LOCKED, QA, SEALED, HANDED_OVER`; `BLOCKED(reason)` from any; `RTS_*`. The WebUSB page needs Chromium (no Snap or Flatpak build, no private window) and direct USB; it is the single-phone fallback and the Stage 2 seed once its verdicts match the CLI's [R17 F5].

### 4.3 Flash sequence (Pixel adapter; contract in 04 §4.6)

```
v = getvar(slot, product serialno version-bootloader version-baseband unlocked secure
                 current-slot snapshot-update-status <anti-rollback var>)   # no wipe yet
require v.product == bundle.model, not above(v, bundle.floor), unlock_ability == 1,
        job.seq <= 100 or gates.fw1_closed
confirm_typed(slot,"UNLOCK"); fastboot -s S flashing unlock                # wipes; phone press
fw = fetch_google(bundle.firmware), sha256 pinned          # Zune never hosts it (04 REL-21)
flash bootloader to both slots (re-pin by USB path after reboot-bootloader); flash radio
fastboot erase avb_custom_key; fastboot flash avb_custom_key avb_pkmd_<model>.bin
fastboot -w --skip-reboot update images.zip                                # our signed image
confirm_typed(slot,"LOCK"); fastboot -s S flashing lock                    # wipes; phone press
boot -> ZuneSetup on lab AP -> factory QA (§4.5) -> seal
```

### 4.4 Job log

Fields: `job_id` (128-bit random), station, slot, `tech`, model, cohort, `seq`, bundle id, hash and key set, pre-flash `bl`, `bb`, `anti`, `ability`, each command with return code and time, QA verdicts, `oem_unlock_exception`, `agreement_version`, state. Forbidden: name, IMEI, serial, number, photo, PIN. The backend gets model, build, `serial_hmac` and the attestation digest (05 BE-19). Retention 12 months (05 BE-36).

### 4.5 Factory QA

The station gets a `ZUNE1S:<token>` from `POST /v1/station/jobs` and shows it as a QR; ZuneSetup scans it and Guardian enters FACTORY. USB is charging only (03 LOCK-26), so results go over Wi-Fi to `POST /v1/device/factory/qa` (both endpoints are cross-section needs).

| Area | Check | Pass |
|---|---|---|
| Boot, lock | Yellow boot screen; backend `attest` | `deviceLocked`, `SELF_SIGNED`, key hash equals the model's `avb_pkmd`, SPL at least the bundle's |
| Seal | Guardian turns OEM unlocking off, forgets the lab AP, reports state signed by the attested key; token consumed | OEM unlocking off; replay refused |
| Hardware | Lab AP; Private DNS on 853; Bluetooth pair; data on a test SIM; cameras; speaker; microphone loopback; charging | All pass; battery health at least 80% |
| Emergency | Emergency screen from lock screen and power menu; SOS countdown started, cancelled | No call placed |
| Enrolment path | Signed time sync; OTA metadata; station record `unclaimed` | Backend confirms |
| Audits | In-process by Guardian (no adb): 03 LT-02, LT-03 subset; intents `youtube.com`, `vnd.youtube`, `market:`; YouTube hosts refused; Tier 2 off; command log allowlist-clean | All denied; Guardian signs |

### 4.6 Hand-over and 10-minute onboarding

The parent opens `/children/{c}/devices`, Add device (05 §4.3); the phone scans the QR on the guest SSID; Guardian enrols, the parent sets the PIN twice (03 LOCK-14), Device Owner and roles follow (03 §4.2), the gesture tutorial runs (02 OS-23); staff forget the guest SSID.

Script: 0-2 min what the phone does and does not do (03 LOCK-37 wording; 112 not guaranteed); 2-4 child area, "ask a parent"; 4-5 Emergency, triple-press SOS; 5-7 portal: what parents read, child told (D27), time rules, approvals, remote lock; 7-8 contacts need both families' codes; 8-9 PIN custody, SIM responsibility, no Wi-Fi sign-in pages (D30 hotspot workaround); 9-10 support, free return-to-stock.

### 4.7 Customer agreement and consent checklist

Counsel finalises (LEG-3, LEG-4); content list, not legal text. Agreement, parent only: ownership representations (genuine India purchase, not stolen, paid off, no MDM, accounts removed); erase consent (two wipes plus `-w`, data lost, backup is the parent's duty, staff never access data); custody (OPS-05); warranty (Google India excludes damage from unlocking or altered firmware [R20 claim 21, SECONDARY]; free return-to-stock); remedy ladder (re-flash, reserve replacement if EXT-5, else compensation capped at purchase value [INFERRED; R19 Q9]); pilot terms (free, no SLA, kill switch); SIM responsibility; data terms (12 months, processors, grievance contact, withdrawal, erasure); translated notices (EXT-7).

Consent checklist (05 BE-30): Rule-10 record; `account`; `visibility` (child told); `ai` (vendors named, images reach the vendor); `location` if places are set; `diagnostics`; `third_party_video` only once Tier 2 is switched on (08 CNT-10); notice version and language; `contact_pair` later (06).

### 4.8 Unbrick, service-unlock, return-to-stock

Ladder: (A) before lock, rerun the bundle; (B) locked but unsealed (OEM unlocking still on [R18 §4.2, INFERRED]): physical unlock, `erase avb_custom_key`, reflash; (C) sealed and booting: A/B fallback (04 REL-19), else recovery sideload of a signed full OTA [R18 F8]; (D) sealed, Guardian alive: `service_unlock`, unlock, reflash; (E) else reserve replacement (EXT-5) or Google's authorised repair, which may refuse a modified phone.

Return-to-stock: parent step-up `unenroll`; staff co-approved `service_unlock` (two signatures, 72-hour window; 05 BE-23, 03 LOCK-20); at the station typed confirm, `flashing unlock`, `erase avb_custom_key`, flash Google stock, stock `flashing lock` unless declined. Device-side order: 04 §4.7.

### 4.9 Pilot staging and exit gates

| Cohort (cum.) | Who and intake | Minimum use | Exit gate |
|---|---|---|---|
| C0 12 (12) | Staff households, own Pixels, `pilot` keys | 4 weeks [INFERRED] | SP-1..7; 112 field test; zero open child-safety P1; hand-over median at most 25 min; first OTA reaches all; kill levels drilled; no successful bypass |
| C1 30 (42) | Invited Bengaluru families, in person, `prod` keys | 4 weeks | First-pass flash at least 95%; no unrecovered brick; 4-week daily use at least 85%; under 2 contacts per family per week; NPS at least 40 |
| C2 70 (112) | Bengaluru, new-in-box ship-to-us, courier to Hyderabad and Pune | 4 weeks | OTA at least 98% in 72 h; first-attempt enrolment at least 90%; yield at least 98% [R18]; FW-1 closed before device 101 |
| C3 88 (200) | Three cities; used-phone courier if EXT-5 | 8 weeks | 8-week retention at least 75%; no open Sev-1; at most 0.5 tickets per device-month; OTA at least 99% in 7 days [R18] |

NPS and the 4-week check-in are collected with a short form in the parent portal (or an India-hosted form), never a third-party survey or analytics tool. Thresholds are R18 and R20 values, unvalidated. Definitions [INFERRED]: yield is first-attempt `SEALED` jobs over jobs started; daily use is child activity on 5 or more days in each of 4 weeks; a ticket is a contact needing staff action beyond a how-to. C0 phones stay on the `pilot` channel (04 §4.4) and count toward 200. Courier families need DigiLocker or staff-inspected ID at a flash day (R19 Q2).

### 4.10 Kill levels

| Level | Effect | Mechanism | Approval |
|---|---|---|---|
| L1 | Named features off (`messenger`, `voice`, `video`, `walkie`, `assistant`, `assistant_images`, `assistant_voice`, `videos`, `videos_tier2`, or any capability in 03's `capabilities.json`) | `kill.level=1` plus `features` (03 LOCK-09; 05 BE-15) | One staff; two if global |
| L2 | Guardian and emergency only: MINIMAL mode | `kill.level=2`, 10 s if connected | Two staff |
| L3 | L2, OTA freeze, no new station jobs; roll-forward only (04 REL-13) | `halt:true` re-signed by `channel` (04 §4.8); `jobs.paused` | Two staff plus release owner |
| L4 | End of pilot for a cohort or all: L2, notice, return-to-stock offered with export and erasure | Parent step-up per family (05 BE-23) | Founder and counsel |

L0 is normal operation. Scopes `global|cohort|family|device`. Triggers: OPS-21 events, a legal order, a vendor withdrawal (AI, YouTube).

### 4.11 Support playbook

- Enrolment fails: new claim code, re-attest; serial mismatch goes to the station.
- Forgot PIN: `pin_reset` (03 LOCK-15). Phone reset: code from the bound family (03 LOCK-18); support releases only with invoice, ID and two staff approvals.
- Offline at home: blocked port 853 (03 VG-8) or a sign-in page that will not complete in ZunePortalViewer (D33); hotspot workaround.
- Lost or stolen: `lock`, then `unenroll` on request. Will not boot: §4.8.
- Tooling: a helpdesk tool hosted in India (or the staff console's case queue) holds contact details and ticket text only, never message or AI content, PINs or serials; staff paste nothing from the vault (break-glass only, 05 BE-28); the tool is a vendor-register row (11 CMP-29). Tickets carry the `serial_hmac` short form, not the serial.

### 4.12 Costs in INR

| Line | INR |
|---|---|
| Floor per in-person device: technician 500, station 225, 30-day support 300, insurance 150, reserve 675 [R20 §4.7] | 1,850 |
| Ceiling: R18 USD 85-125 at 95.97 per USD (US labour rate) | 8,200-12,000 |
| Courier extra: round trip 800-3,000, transit insurance about 1,500 [R20 §2.6] | 2,300-4,500 |
| 200 devices at floor and ceiling | 3.7-24.0 lakh |

Fixed [R18 and 04 USD figures converted, INFERRED]: station cell 2.9-4.8 lakh each, signing devices 2.4 lakh, counsel 9.6-24.0 lakh, bailee insurance 1.0-2.9 lakh a year, reserve phones 1.7-2.9 lakh (4-6 at INR 43-48k [R20]), cloud 8.1-16.1 lakh a year with DR (USD 700-1,400 a month, 05 §4.8, at 95.97; about INR 340-670 per child-month at 200 children, not R20's INR 180-200 each; 05's figure includes DR) plus AI about INR 138 per child-month (07 §4.6). Not costed: rejected applicants (10-25% [R18]), liability payouts, FX. The pilot is free; the company bears all of it. Prices belong to PAY-1.

### 4.13 Before the first external family

Evidence in `zune/docs/gates.md`: SP-1..7; C0 exit; LEG-1..10 and EXT-1..7 (01); `prod` key ceremony (EXT-4); service-unlock rehearsed; first OTA delivered; T&S 24x7 on-call named (06 COM-29, EXT-3); agreement and consent text final; bailee insurance; counsel's view on holding customers' radio equipment (VO-11); courier lithium answers (VO-10) before any courier job; 112 field test (LOCK-36); support desk staffed to OPS-22.

### 4.14 Reuse for self-install (Stage 2)

Reuse `core`, adapters, the QA subset, error-code telemetry and the WebUSB page. Gate claims on attestation bound to a station-recorded serial, since attestation alone can be relayed [R17 F6]. Build at 250 or more devices a month for two months, or over 3 technician FTE, with yield at least 98% on three models [R18]; break-even is 2.1-5k devices, far above v1's 200.

## Acceptance criteria and tests

- **AT-O01** Seeded rejects (US unit, prior account, MDM, newer bootloader, swollen battery, wrong buyer) each end `BLOCKED` with the right code and no wipe command logged.
- **AT-O02** Four phones, 20 consecutive jobs: every command carries the job's `-s`, none crosses devices, no hang. A hang sets `lock.mode: host` and §4.12 is recomputed.
- **AT-O03** Tampered file, bad signature, wrong key set, expired manifest and platform-tools mismatch abort before unlock; CLI and WebUSB agree on `tests/vectors`; unlock and lock refuse to run without the typed digits; a forged `flash modem` aborts with a tamper entry.
- **AT-O04** A sacrificial unit reaches `SEALED`: attest passes, `get_unlock_ability` is 0, unlock is refused, a replayed token is refused, the server refuses a token for a claimed serial.
- **AT-O05** Station disk and image hold no private key or token; a reboot ends the session; job logs hold no 15-digit number, serial or name.
- **AT-O06** Timed C0 hand-overs: median at most 25 minutes; a wrong-family code gets nothing.
- **AT-O07** On two units per model, ladder rungs B, C, D and return-to-stock complete with times recorded; an expired 72-hour window blocks unlock.
- **AT-O08** Each kill level fires in staging and on a staff phone: L1 and L2 within 10 s, L3 makes ZuneUpdater and the station refuse, L4 ends one staff phone on stock Android.
- **AT-O09** Four simulated playbook cases meet their limits. C0 yields measured hands-on minutes and INR per device against §4.12.

## Verify first

Nothing here was read from Google's `android-17.0.0_r1` tree. Log results in `zune/docs/verified-facts.md`.

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VO-1 | Pixel unlock and lock need on-device confirmation and wipe; `get_unlock_ability` readable locked; no `unlock_critical`; stock relock after `erase avb_custom_key` works [R18 F1, F8] | GrapheneOS pages only | Sacrificial 10a and 9a, India SKU; AT-O07 | Adapt prompts and QA rows; return phones unlocked with disclosure |
| VO-2 | `-s` stays pinned across `reboot-bootloader` with four phones, no hangs [R18 F5, F6] | Upstream never pins | AT-O02 | Host-wide lock; replan |
| VO-3 | Anti-rollback variable `anti` or `ap-ar-s`; 10a outside the May 2026 bump [R18 F9; 04 V5] | Search summaries | `getvar` per unit | Order by `version-bootloader`; hold units |
| VO-4 | OEM-unlock toggle works on India SKUs with no carrier-ID lock; units have a nano-SIM tray [R20 §2.1] | No Indian unit tested | First India units; every intake | Refuse the SKU; Wi-Fi-only if no tray |
| VO-5 | First-boot attestation works; a Guardian not yet Device Owner can turn OEM unlocking off [R18 F5, F8; 04 V4, V9, V12] | Forks and docs | Z2 lab; read `OemLockService` at the tag | Seal at claim; no courier intake |
| VO-6 | Token plus server check is one-way: no FACTORY re-entry after claim or wipe | New design | Red-team: intents, boot reasons, USB, replay | Strip FACTORY from the image; hold C1 |
| VO-7 | KYM by SMS to 14422 works for an unactivated phone [R20 §2.1] | DoT post only | Try dev units; else CEIR portal | Portal; else invoice only, tell counsel |
| VO-8 | Battery health readable (`BATTERY_PROPERTY_STATE_OF_HEALTH`) [MEMORY] | Memory | Query dev units | Cycle count, or new-in-box only |
| VO-9 | Google's licence allows company flashing, caching Google zips, stock reflash [R17 F1]; Google India warranty excludes unlock damage [R20 claim 21] | Licence unread (FW-1); warranty page blocked | Counsel reads image, OTA, driver and warranty pages | 100 staff-owned devices; no external family; keep the disclosure |
| VO-10 | Courier battery rules; the 30% charge rule is an air rule [R20 §2.6] | Sources conflict | Written answer per courier | In person only |
| VO-11 | Holding customers' radio equipment needs no authorisation; a re-flash is not manufacture [R19 Q8, Q11] | 2026 rules unread | Counsel (LEG-1) | Flash no non-staff phone |
| VO-12 | 50-60 minutes hands-on, 8-10 phones a day, INR 1,850-12,000, support hours, thresholds [R18, R20] | Estimates | Measure in C0 (AT-O09) | Replan; founder re-approves cost |

## Risks, open gates and out of scope

Risks:
1. Google's licence (FW-1) may refuse commercial flashing; device 101 falls inside C2.
2. A sealed phone with a dead Guardian or bad OTA can brick (04 risk 3); the remedy is the reserve (EXT-5).
3. Few families own a qualified INR 43-48k phone [R20]; invite-only limits supply.
4. Karnataka's under-16 announcement or an IT Rules change may capture the messenger (EXT-1).
5. Custody: theft laundering, loss, courier damage, lithium shipping; bailment needs counsel.
6. The 4-phone cell is unproven (VO-2); FACTORY is a bypass surface until VO-6 passes.
7. SIM in another phone, parent-assisted unlock, recovery wipe: disclosed limits (03).

Gates (IDs per 01):
- **[GATE: before build]** VO-1, VO-2, VO-5 run on the first Pixels (Z2).
- **[GATE: before staff pilot]** SP-1..7 including SP-5 kill drill and SP-6 service-unlock; AT-O02 and AT-O07 passed; unbrick ladder rehearsed.
- **[GATE: before external family]** §4.13 signed; LEG-1..10; EXT-1..7 including EXT-5 spare phones and EXT-7 notices; VO-6 and VO-11 closed.
- **[GATE: before charging]** PAY-1 and FW-1; FW-1 is also needed before device 101.

Out of scope: self-install and remote-guided install (Stage 2); Fairphone, Snapdragon (D17); eSIM; prices, payments; Hindi UI (D20); US and EU rules; own hardware (D21).
