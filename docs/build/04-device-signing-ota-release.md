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
