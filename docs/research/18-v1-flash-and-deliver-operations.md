# Zune research 18: Version-1 flash-and-deliver operations (D15, D16)

Date: 2026-10-02. Tags: **[P]** read in a primary source or real file this session; **[S]** reputable secondary, often a search summary; **[I]** my judgement; **[M]** memory, unchecked. **Access:** `android.googlesource.com` and `source.android.com` returned HTTP 403 (not worked around), so nothing was checked against `android-17.0.0_r1`. The Pixel flow comes from GrapheneOS's docs and scripts and LineageOS's mirror of `external/avb` on GitHub. Google, Motorola and Fairphone support pages and several news sites were blocked, so OEM warranty and market facts are search summaries. Reports 15 and 17 appeared during the session (section 6). Costs and times are estimates [I].

## 1. Summary & recommendation

Run v1 as an **in-person-first, scripted service behind a hard eligibility gate**, not a mini-factory. Flashing is easy: about 10 unattended minutes plus two button presses. What hurts a pilot is the rest: phones that cannot be unlocked, carrier and account locks, stock firmware newer than our image, SIM handover, parent enrolment, and the terms for holding someone's phone.

1. **Gate before anything ships:** qualified model (15), unlocked and paid off, accounts removed, OEM unlocking available, not stolen. Customers self-test with screenshots.
2. **Cohorts of 10 (staff families), 25, then up to 100**, four weeks each, with exit gates. Batch size is still open (A7); these are defaults.
3. **Stations hold no secrets**, only the public key blob and signed bundles. Rotating the AVB key wipes every phone [P], so per-model keys and an offline signing ceremony come before cohort 2.
4. **Plan for the day after lock.** With OEM unlocking off (04, 05) a locked phone cannot be re-flashed over USB; OTA and signed recovery sideload are the only repair path. OTA ships from the first external device, and a parent-authorised **service-unlock** (17 proposes it) is required before cohort 2.
5. **Cleanest intake is a new-in-box phone** the parent buys and drops off: no data, accounts, FRP or carrier lock. Used phones are the gated exception. Few families own a qualified phone (15, 17), so recruitment is the real limit.
6. **Cost and price.** Fully loaded cost is $85-125 per device, not 17's $25-40 (station labour only). Charge $59 in person (17's default) and $99 mail-in; subsidy under $4k across 100 devices.
7. **Build self-install later**, at 250+ devices a month for two months or over 3 technician FTE; remote-guided install is the bridge.

## 2. Findings

**F1. Unlock and lock need a human at the phone.** `fastboot flashing unlock` and `lock` "need to be confirmed on the device and will wipe all data". OEM unlocking must be switched on inside the stock OS; on carrier SKUs that needs internet so the OS can check whether a carrier sold it locked [P: GrapheneOS/grapheneos.org@main:static/install/cli.html]. Two presses per phone cannot be scripted.

**F2. Carrier variants are the biggest trap.** A carrier id on the Pixel `persist` partition disables unlocking, and carrier support "probably won't" lift it [P: same page]. The FCC waived Verizon's 60-day auto-unlock in 2026: payoff required, subsidised phones may stay locked up to a year; AT&T needs payoff plus 60 days, T-Mobile 40 days plus payoff [S: https://phandroid.com/2026/01/14/fcc-lets-verizon-ditch-60-day-phone-unlock-rule/ ; https://www.t-mobile.com/responsibility/consumer-info/policies/sim-unlock-policy].

**F3. Few phones can be relocked.** AVB custom key: while LOCKED the bootloader boots images signed by the built-in or the custom key, shows a yellow screen, and `avb_custom_key` is writable only while unlocked [P: LineageOS/android_external_avb@lineage-24.0:README.md]. Reported to work: Pixel, Fairphone 3/4/5, some Motorola g-series, Nothing (3)/(3a)/(4a), some Sony; not newer OnePlus or Xiaomi [S: https://github.com/chenxiaolong/avbroot/issues/299]. Samsung removed unlock in One UI 8 [S: https://www.sammobile.com/news/say-goodbye-to-your-custom-roms-as-one-ui-8-kills-bootloader-unlock/]; Xiaomi adds a 168-hour wait [S]. Eligible models come from 15.

**F4. Warranty (all [S] search summaries; verify).** Google staff say unlocking alone does not void the Pixel warranty, but its text excludes "alterations" [S: https://support.google.com/store/answer/9155764]. Fairphone: intact if original Android is reinstalled before repair. Motorola, Sony, Nothing: unlocking reported to void it. Magnuson-Moss bars voiding cover merely for third-party service, but a warrantor may deny a defect the modification caused [S: https://www.taftlaw.com/news-events/law-bulletins/ftc-clarifies-that-a-manufacturer-provided-warranty-cannot-deceptively-imply-that-using-an-unauthorized-part-will-void-the-warranty/]. Every customer therefore needs a return-to-stock path.

**F5. Flash mechanics to copy** [P: GrapheneOS/device_common@17:generate-factory-images-common.sh]: fastboot version check; `getvar product` against the bundle ("wrong factory images... would likely brick"); both-slot bootloader; radio; `erase` then `flash avb_custom_key avb_pkmd.bin`; `fastboot -w update`. Platform-tools are pinned by SHA-256 and bundles verified by ed25519 signature [P: install/cli.html]. Flash takes 5-20 minutes [S].

**F6. USB.** Hubs and cables "are the most common source of issues"; use direct ports [P: install/cli.html]. Parallel `fastboot` can hang; lock each call [S: https://bugs.launchpad.net/bugs/1110622]. Each model needs its own adapter (17).

**F7. Key custody** [P: static/build.html]. `avb_pkmd.bin` "isn't needed for generating a signed release but rather to set the public key used by the device". RSA-4096 keys are scrypt/AES-256 encrypted at rest and decrypted to tmpfs only to sign; "unique keys per device variant"; keys "cannot be changed without flashing the generated factory images again which will perform a factory reset".

**F8. After lock, the OS is the repair path.** Signed zips install through recovery sideload with downgrade protection [P: static/usage.html]. Returning to stock needs an unlocked bootloader and `fastboot erase avb_custom_key` [P: install/cli.html]. GrapheneOS keeps the unlock toggle; Zune removes it (04), so a service-unlock must exist [I].

**F9. Anti-rollback.** Pixel bootloader updates raise a rollback counter (Pixel 6/8 May 2025, Pixel 10 family May 2026); older images then cannot boot, and flashing one slot risks an unbootable fallback [S: https://www.droid-life.com/2025/05/06/pixel-6-and-pixel-8-devices-get-new-bootloader-in-may-update-that-wont-allow-rolling-back/]. A customer phone may be newer than our bundle, so the station blocks on `version-bootloader` before unlock (17 agrees).

**F10. SIM and eSIM.** The Pixel 10a US model has a physical SIM plus eSIM; Pixel 10/Pro/XL are eSIM-only [S; resolves report 12's open item]. GrapheneOS can use eSIMs "installed previously on the device", but adding or managing them needs Google's proprietary component, off by default; carriers whitelist IMEI ranges for VoLTE [P: static/usage.html]. Whether our two wipes keep a profile is unverified [I]; eSIM QR codes are single-use [S]. Pilot rule: physical SIM, or the carrier QR in hand.

**F11. FRP and theft.** Google FRP lives in "a tiny, special region of persistent state not wiped by a factory reset" [P: faq.html]. An account-bound phone dead-ends at setup and we never bypass it. A flash service is also a laundering route for stolen phones: check the CTIA database and photo ID [S: https://cellularnews.com/mobile-phone/the-ctia-releases-the-stolen-phone-checker-tool-to-help-you-determine-your-phones-authenticity/].

**F12. Market and legal anchors [S].** Mail-in GrapheneOS installs sell for about $85, remote-guided $60. Google images "may not be... modified or redistributed" outside the device licence [https://developers.google.com/android/images]. Amended COPPA: compliance 2026-04-22, written security programme and retention policy [https://www.hunton.com/privacy-and-information-security-law/ftc-publishes-final-coppa-rule-amendments]. Carrier terms bar modifications that circumvent their policies [https://www.t-mobile.com/responsibility/legal/terms-and-conditions]. Bailee's customers insurance covers customer goods in our custody; general liability excludes them [https://inszoneinsurance.com/blog/bailees-customers-insurance-the-care-custody-and-control-trap-explained].

## 3. Options & trade-offs

| Decision | Options | Pick |
|---|---|---|
| Intake | In person; mail-in; new-in-box drop-ship | In person for cohorts 1-2, drop-ship from cohort 2, mail-in in cohort 3 with a spare phone: no loaner, no shipping risk |
| Key custody | Fleet; per-model; per-device | Per-model (one model's blast radius); throwaway key only for staff-owned cohort 1 |
| Unlock bit after lock | On (recoverable) or off | Off: on lets a child with a PC unlock |
| OEM firmware | Fetch at flash time and pin digests in our vbmeta; or ship in our OTA | Fetch and pin for v1 (17 option b); OTA firmware needs OEM terms (17, G5) |

## 4. Recommended Stage-1 design

### 4.1 Customer journey

1. **Web form** (parent browser): model, SKU, carrier, screenshots of Settings > About and the OEM-unlocking toggle. Customers request any OEM unlock code (Fairphone) themselves; we never store it.
2. **Eligibility:** US unlocked SKU on 15's list; carrier-unlocked and paid off, with proof (F2); stock bootloader not newer than our bundle (F9); accounts removed, Settings reset, toggle available; CTIA check passed and photo ID matches (F11); battery not swollen, health >= 80%, no MDM; carrier verified by cohort QA (12).
3. **Agreement and consent online** before drop-off: wipe consent, backup duty, warranty and risk terms, parent account with COPPA consent (13).
4. **Drop-off:** ticket QR, tamper-evident bag, exterior photos only, customer confirms the reset in front of us. We never ask for a PIN. A locked or account-bound phone goes back unopened.
5. **Service** (4.2): 90-120 minutes; the parent waits or collects later.
6. **Hand-over:** the parent opens the portal on their own phone, taps "Add device", the child device scans the QR (05). The phone ships unenrolled, OEM unlock off. A 10-minute onboarding covers what the child sees, "ask a parent", SOS, and what parents see including SMS. Mail-in uses a claim card and a first-week call.
7. **After-sales:** one-business-day response; check-ins on days 3 and 14; free return-to-stock in pilot.

### 4.2 Station and process

**BOM per 4-phone cell (about $3-5k):** bare-metal Ubuntu 24.04 workstation (16 GB RAM, 500 GB SSD) with PCIe USB host cards or direct ports; certified short USB-C cables with spares; a separate powered charging rack; lithium-safe cabinet; prepaid test SIMs per verified carrier; two reference Zune phones; lab AP; label printer.

**Software ("zune-station", a wrapper over pinned platform-tools, with one adapter per model, F6):**
1. Scan the ticket; read `product, serialno, version-bootloader, unlocked`; refuse on mismatch or rollback risk.
2. Verify the bundle's ed25519 signature and SHA-256; serialise `fastboot` calls per device.
3. Human confirms unlock; flash firmware, `avb_custom_key`, OS, `-w` (F5).
4. Human confirms lock (wipes again); first boot into **factory mode**, a Zune system app, inert after setup: it runs QA, creates an attested key, and as the last step disables OEM unlocking.
5. Server verifies the attestation chain (`android/keyattestation`, 05): locked, our key hash [M]. Phone is left at the unenrolled welcome screen.
6. Print the certificate of erasure, bag, hand over.

**Identity and logs.** Random 128-bit job ID; log model, bundle ID and hash, key ID, bootloader versions, timestamps, return codes, QA results, attestation digest, technician, station. **No name, IMEI, serial, number or photo**; a job-scoped HMAC of the serial (90-day key) supports RMA. The raw IMEI goes only into the stolen check, then is dropped. Erasure certificate: two wipes plus `fastboot -w` [P], plus family-key crypto-shred on return (05).

**Keys.** Signing runs in the release pipeline on an HSM or air-gapped host with dual control: per-model AVB keys and a separate ed25519 bundle key. Every bundle is flashed, locked and booted on a canary of the same model before a station may pull it. The unlock bit stays on until the final factory-mode step, so a bad lock is recoverable (unlock, erase key, reflash) [I]. **Sanctioned unlock paths only: no exploit-based unlock (EDL, GBL), no FRP bypass** (17).

**Unbrick.** Before lock: re-run the bundle. After handover: A/B rollback, recovery sideload (F8), service-unlock for reflash, else replacement or OEM RMA.

**Throughput (4-up, one technician):** 50-60 min hands-on, 90-120 wall (intake 8, stock prep 8, presses 4, flash 2 plus 12 unattended, QA with test SIM 15, hand-over 12): 8-10 phones a day, 15-20 once QA is scripted. 10 devices take a week part-time; 100 take 2.5 weeks for one technician; 1,000 take about 8 weeks with three technicians and three cells.

### 4.3 QA (on the shipped bits, via factory mode)

| Area | Test |
|---|---|
| Boot, lock | Attestation: locked, our key; OEM unlocking off |
| Telephony | VoLTE out and in per verified carrier; inbound SMS to the vault; emergency-number recognition. **No live 911 calls** (coordinate with the carrier, 12) |
| Hardware, enrolment | Cameras, speaker, mic, GPS fix, Wi-Fi, Bluetooth, wired charging, battery health >= 80%; dry-run claim with a QA token; policy fetch; OTA check-in |
| No-browser audit | No activity resolves `VIEW` for http/https/ftp, `WEB_SEARCH`, `text/html`; WebView refused for non-allowlisted callers (04) |
| No-YouTube audit | Intents for youtube.com, `vnd.youtube`, `market:`; DNS and connect probes to YouTube hosts fail outside Videos (04, 06) |

### 4.4 Legal and policy (counsel before cohort 1)

- **Agreement:** owner reps (ownership, unlocked, paid off, no MDM); wipe consent; warranty effects (F4) with free return-to-stock; brick remedy ladder (re-flash, then replacement or fee refund plus fair market value), capped at the lesser of documented value or $600 [I], with consumer-law carve-outs; no FRP bypass; pilot terms (features change, no SLA, telemetry consent). US only (A1).
- **Custody:** bailee's customers insurance, lithium-safe storage, 72-hour dwell target.
- **Data:** never retain IMEI, photos or PINs; deletion proof as above. Enrolled children's data is COPPA data: a consent method that permits disclosure, written security programme, retention policy (13, 05); SMS capture sign-off (12).
- **OEM blobs:** a relocked phone needs every verified partition covered by our vbmeta, so we flash the OEM's own firmware at a pinned version, byte-identical for modem and IMS (12), fetched from the OEM at flash time (17 option b) [I]. Google's licence (F12) and Fairphone's terms stay open until 17's gate G5; cohort 1 uses staff-owned phones.
- **Other:** carrier modification clauses are a disclosure; CPSIA treatment of a handed-back kids' phone is a counsel question (17).
- **Incident response:** custody loss (notify within 24 h, replace); data exposure (freeze, preserve, notify per state and COPPA rules); child-safety event (triage in 1 h, kill-switch, call the parent); key compromise (revoke, per-model scope, fleet re-flash).

### 4.5 Pilot design

| Cohort | Size | Who | Intake | Exit gate |
|---|---|---|---|---|
| 1 | 10 | Staff and friends, 3 carriers, staff-owned | In person | Zero Sev-1; first OTA reaches all; then G1 |
| 2 | 25 | External, ages 8-13; 15 in person, 10 new-in-box or mail | Mixed | Yield >= 95%; <= 60 min hands-on; CSAT >= 4.3/5; then G2, G5 |
| 3 | <= 100 | Waitlist, verified carriers (T-Mobile, AT&T first, 15) | Mail-in with spare phone | Yield >= 98%; <= 0.5 tickets/device/month |

**Models:** Pixel 9a/10a first (documented relock); Fairphone Gen 6+ only after 15's bring-up checklist and OEM terms (17, G5). **Selection:** a qualified phone or willingness to drop-ship one; parent at ease with a browser portal; verified carrier; some co-parent and multi-child homes.
**Metrics:** install success; hands-on minutes; days intake to hand-over (same day in person, <= 5 business days mail); tickets per device; CSAT plus two interviews per family; child-safety incidents (any browser or YouTube reach or unapproved contact is stop-ship); bypass attempts (a success is a P0); battery (full day of light use, under 8% overnight loss [I], unmeasured with the persistent socket); allowed-contact call completion; SMS to portal within 60 s (p95); OTA success >= 99% in 7 days; first-attempt enrolment >= 90%.
**OTA from day one:** canary, pilot, all rings with staged percentages; first external OTA in cohort 1. Rollback means **roll-forward**: downgrade protection (F8) blocks true rollback.
**Kill-switch:** L1 per-feature server flags; L2 fleet "guardians and emergency only" policy (05, 12); L3 OTA halt and roll-forward; L4 end the pilot with refunds and return-to-stock.
**Gates:** G0 before cohort 1: data map, COPPA notice and consent method, security programme, retention policy, incident plan. G1 before cohort 2: external review of portal and pairing, passed no-browser and no-YouTube audits, service-unlock built. G2 before cohort 3: processor contracts, breach tabletop. G5 (17): OEM terms.
**Parent comms:** a plain one-pager (what the child can and cannot do, what parents see, pilot status), an onboarding call, a promised incident-notification window.

### 4.6 Costs and staffing (USD, [I])

| | 10 | 100 | 1,000 |
|---|---|---|---|
| Hands-on min/device | 90 | 55 | 30 |
| Labour at $35/h | 52 | 32 | 18 |
| Shipping, round trip | 0 | 20 | 36 |
| Support | 35 | 20 | 12 |
| SIMs, packaging | 10 | 8 | 6 |
| Failure/RMA reserve | 20 | 18 | 9 |
| Insurance, overhead | 5 | 5 | 4 |
| **Per device** | **~122** | **~103** | **~85** |
| People | founder + 1 eng, part time | 1 technician, 0.5 support, 0.25 release eng | 3 technicians, 2 support, 1 logistics, 1 release eng, 0.5 compliance |
| Loaner float | 0 | 5 (~$0.75k) | 12-15 (~$2k) |

Fixed: station cell $3-5k each, HSM or KMS $1-5k, counsel $10-25k, bailee insurance $1-3k a year.
**What breaks first:** intake and eligibility; firmware drift and anti-rollback; the per-carrier SIM matrix; enrolment support; release and key management as models multiply.
**Self-install threshold:** 250+ devices a month for two months, or over 3 technician FTE, with yield >= 98% on three models. A $150-250k build against $50-70 saved per device breaks even at 2.5-5k devices, so 1,000 a year is borderline.

## 5. Stage-2 improvements

Scripted QA and a multi-port rack; paid loaners; carrier-QR eSIM provisioning; remote-guided install, then the customer installer. **Reuse for 17's installer:** signed bundle and manifest, per-model adapter, block-not-warn pre-flight rules, attestation check, factory-mode QA subset, error-code telemetry. The station CLI becomes the engine behind a WebUSB front end; self-install claims are gated on attestation (17).

## 6. Conflicts with earlier reports

- **02:** its factory flow assumes new unlocked stock, about $35 a unit and $0.5-0.9M float. D15/D16 mean customer phones of unknown history at $85-125 a unit; float vanishes.
- **15:** its Fairphone Gen 6+ plan and "hold each OEM update until it passes relock" fit; I add a per-model adapter, the OEM unlock-code step and its sacrificial-unit bring-up (15 section 4) before a model enters service.
- **17:** its $59 provisioning is below fully loaded cost (its $25-40 is labour only), hence mail-in $99 and a pilot subsidy. Its service-unlock token (17 section 4.1, item 6) becomes a Stage-1 requirement before cohort 2.
- **12:** the 10a SIM tray is physical plus eSIM [S]; SMS tests are inbound only (A2).
- **04:** adb is off on `user`, so QA needs factory mode; `DISALLOW_FACTORY_RESET` clears the unlock bit and blocks `setOemUnlockAllowedByUser`, so service-unlock must work around it.
- **05:** Device Owner is set only at provisioning, so the station stops at the unenrolled welcome screen.
- **10 (absent):** adopt F7: no private key on stations, per-model keys, rotation is a fleet wipe.

## 7. Risks & unknowns

1. Google's firmware licence and Fairphone's terms (high). 2. Carrier acceptance of a modified OS, and E911 without Google's service (high, 12). 3. Customer phones in unfixable states: anti-rollback, carrier id, FRP (high). 4. Service-unlock is unbuilt and untested against 04's restriction (high). 5. Relock on Fairphone Gen 6+ and the Pixel 10a under Android 17 unverified (medium). 6. Liability caps and exculpatory clauses vary by state (medium). 7. Few families own a qualified phone (medium). 8. Unchecked: AOSP AVB docs at `android-17.0.0_r1`, Google's licence text, current OEM warranty pages, full carrier BYOD terms.

## 8. Decisions needed from the founder

1. **Who supplies phones.** D16 assumed customer-supplied. Default: customer-supplied, new-in-box drop-ship preferred; we never buy or sell handsets.
2. **Batch size.** Default: 10, 25, then up to 100, gated.
3. **In person or mail-in.** Default: in person for cohorts 1-2; mail-in only in cohort 3.
4. **Price.** Default: free for cohort 1; $59 in person, $99 mail-in, refunded if we cannot provision; plus 17's subscription.
5. **Service-unlock and return-to-stock.** Default: build service-unlock before cohort 2; promise return-to-stock.
6. **Key ceremony.** Default: production per-model keys with dual control before cohort 2.
7. **Legal.** Default: engage counsel now (agreement, COPPA, insurance, Google licence, carrier terms); no external cohort before G0.
8. **Verified carriers and liability cap.** Defaults: T-Mobile and AT&T first (15); cap of the lesser of documented value or $600 plus fees.

## 9. Load-bearing claims

| # | Claim | Evidence | Basis |
|---|---|---|---|
| 1 | Unlock and lock each need on-device confirmation and wipe; OEM unlocking is enabled in the OS; carrier SKUs may block it | GrapheneOS/grapheneos.org@main:static/install/cli.html | P |
| 2 | Flash sequence: product check, both-slot bootloader, `avb_custom_key`, `fastboot -w update`; signed bundles | GrapheneOS/device_common@17:generate-factory-images-common.sh | P |
| 3 | Stations need only `avb_pkmd.bin`; per-variant keys; changing a key forces a factory reset | GrapheneOS/grapheneos.org@main:static/build.html | P |
| 4 | A locked custom-key device boots built-in or custom-signed images, shows yellow; the key is writable only while unlocked | LineageOS/android_external_avb@lineage-24.0:README.md | P |
| 5 | Locked devices accept signed recovery sideloads with downgrade protection; Google FRP survives factory reset | static/usage.html; static/faq.html | P |
| 6 | Custom-key relock works on Pixel, Fairphone, some Motorola, Nothing, Sony; not Xiaomi or newer OnePlus; Samsung removed unlock | https://github.com/chenxiaolong/avbroot/issues/299 | S |
| 7 | Pixel anti-rollback blocks older images | https://www.droid-life.com/2025/05/06/pixel-6-and-pixel-8-devices-get-new-bootloader-in-may-update-that-wont-allow-rolling-back/ | S |
| 8 | Verizon ended auto-unlock in 2026; carriers need payoff | https://phandroid.com/2026/01/14/fcc-lets-verizon-ditch-60-day-phone-unlock-rule/ | S |
| 9 | Mail-in installs sell at $60-85; $85-125 per device cost and 2.5-5k break-even are my estimates | search summaries; section 4.6 | S, I |
