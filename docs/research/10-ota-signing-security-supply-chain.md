# 10 - Release engineering: signing, OTA, verified boot, anti-theft, build infra

Status 2026-10-02. Tags: **[P]** read in a real file or primary page this session (`repo@ref:path` or URL); **[S]** secondary; **[I]** inference; **[M]** memory, unchecked. Google source hosts, grapheneos.org and price pages were blocked and the search quota ran out, so prices, EU/UK rules and AOSP security-branch status are [M] or unverified. Code was read in GrapheneOS `17` and LineageOS forks, not Google's tree; GrapheneOS FAQ text is from page copies saved earlier in the session scratchpad.

## Summary & recommendation

Copy GrapheneOS's proven release plumbing; do not invent one.

1. **OTA:** fork GrapheneOS's 1,377-line MIT `Updater` into `ZuneUpdater` (update_engine, static CDN files, our signed metadata). No hawkBit or Mender.
2. **Keys:** our own key set, generated offline; the build host never holds keys; a separate offline host signs. One AVB key per hardware model. AVB-key rotation is a recall, so it gets the strictest custody.
3. **Roll forward only.** SPL downgrades are blocked end to end; use rings, a halt switch and a hotfix lane.
4. **Patching is a named job** (0.5-1 FTE): monthly SPL train plus a 72-hour hotfix lane, fed by OEM drops, GKI LTS, Chromium stable, the AOSP security branch if reachable, and GrapheneOS/LineageOS branches as cross-checks.
5. **Anti-theft without GMS:** Android 17 already ships FRP-secret primitives; build a "Zune Activation Lock" on them with the parent portal.
6. **Attestation is a signal, not a gate** (agrees with 05).
7. **Infra:** two bare-metal hosts plus ephemeral self-hosted runners, about $0.5-0.9k/month [M]. People cost dominates.
8. **Support promise:** per-model end date, the earlier of OEM firmware end and 5 years; contractually 3.

## Findings

| # | Finding | Basis | Source |
|---|---|---|---|
| F1 | GrapheneOS builds `lunch <dev>-cur-user` + `m target-files-package otatools-package` on four named hosts. Output is unsigned target-files plus otatools. A separate script runs `sign_target_files_apks`, `ota_from_target_files -k releasekey`, `img_from_target_files`, then ed25519-signs the factory zip. Keys are scrypt-encrypted PKCS#8, decrypted to `/dev/shm` only to sign. | P | GrapheneOS/script@17: `build-releases`, `finalize.sh`, `generate-release.sh`, `decrypt-keys` |
| F2 | AOSP test keys must "NEVER be used" in released images. GrapheneOS makes 9 keys with `make_key` (bluetooth, gmscompat_lib, media, networkstack, nfc, platform, releasekey, sdk_sandbox, shared; RSA-4096, 10,000-day certs) plus an RSA-4096 AVB key. Its release script maps **44 APEX payload keys** and 59 `--extra_apks` entries, reusing `releasekey` and `avb.pem` for every APEX. | P | build@17:`target/product/security/README`; development@17:`tools/make_key`; script@17:`common.sh`, `generate-release.sh` |
| F3 | HSM hooks: `avbtool --signing_helper` receives `padding \|\| SHA-256 digest` and returns the raw RSA result; `ota_from_target_files --payload_signer` signs payloads externally; `SignApk` can load PKCS#11 keys, but releasetools passes `.pk8` paths. A cloud KMS has no raw-RSA call, so the helper must strip the padding and sign the digest. | P; helper trick I | LineageOS/android_external_avb@lineage-24.0:`avbtool.py:543-600`; build@17:`tools/releasetools/`, `tools/signapk/.../SignApk.java` |
| F4 | The tree ships verification tools: `check_target_files_signatures.py -c <previous>` (flags changed keys), `validate_target_files.py` (AVB), `check_ota_package_signature.py`, `compare_builds.py`, and an SPDX 2.3 SBOM generator (`tools/sbom/gen_sbom.py`). | P | build@17:`tools/` |
| F5 | AVB (Pixel section): custom key is flashed only while unlocked; a locked device boots images signed by the built-in **or** the custom key; boot state is yellow. Rollback index **defaults to 0** unless `BOARD_AVB_ROLLBACK_INDEX` is set (README example uses the SPL timestamp). Lock and unlock need physical presence and wipe data and stored rollback indexes. The certified GKI `boot.img` is not signed for verified boot; we sign it. AVB 1.4 adds ML-DSA (BoringSSL backend only). | P | https://raw.githubusercontent.com/LineageOS/android_external_avb/lineage-24.0/README.md |
| F6 | The OTA tool refuses SPL downgrades on release-keys builds ("a locked bootloader will reject SPL downgrade no matter what"); `--downgrade` forces a wipe. `update_engine` rejects older timestamps unless `ro.ota.allow_downgrade` **and** `ro.debuggable`. Its SPL guard fires only when `ro.boot.verifiedbootstate` is green. Our locked custom-key devices are yellow, so it merely schedules a powerwash: the client and server must enforce SPL monotonicity themselves. | P; yellow consequence I | build@17:`ota_from_target_files.py:1426-1446`; GrapheneOS/platform_system_update_engine@17:`aosp/hardware_android.cc:267-270`, `payload_consumer/delta_performer.cc:443-480,1295-1301` |
| F7 | The GrapheneOS Updater (MIT) is privileged and calls `UpdateEngine.applyPayload`. It runs a 6 h persisted job with network-type, battery-not-low and charging constraints, plus an idle-reboot job. It fetches a one-line `<device>-<channel>` file, tries an incremental, falls back to full, checks `RecoverySystem.verifyPackage` and metadata (device, timestamp, pre-build, `ota-type=AB`), pre-allocates storage, bans cleartext and pins ISRG roots (expiry refreshed monthly). `update_engine` verifies against `/system/etc/security/otacerts.zip`. The server learns only device, channel and version, and holds no signing keys. | P | GrapheneOS/platform_packages_apps_Updater@17 (`Service.java`, `PeriodicJob.java`, `network_security_config.xml`); update_engine@17:`aosp/platform_constants_android.cc:29`; FAQ copy |
| F8 | Alternatives: LineageOS Updater (Apache-2.0, JSON list with sha256/size); AOSP ships only the `SystemUpdaterSample` demo. hawkBit is an EPL-2.0 server with a JVM DDI client library; Mender targets embedded Linux/Yocto. Neither drives `update_engine`. | P; fit I | LineageOS/android_packages_apps_Updater@lineage-24.0 README; GrapheneOS/platform_bootable_recovery@17:`updater_sample/README.md`; eclipse-hawkbit/hawkbit and mendersoftware/mender READMEs |
| F9 | Benchmark: GrapheneOS (a partner) cut **43 release tags from 2026-01-08 to 2026-09-25** (one per 6 days). Its device bar is monthly bulletin patches "without any regular delays longer than a week" and at least 5 years of support. Non-partner lag was about 125 days for roughly 40 framework fixes (01). | P | `git ls-remote --tags GrapheneOS/platform_manifest`; GrapheneOS FAQ copy; 01 |
| F10 | No GMS means we own module and WebView freshness. AOSP builds Mainline from source (`PRODUCT_MODULE_BUILD_FROM_SOURCE`); `rkpd` is in `base_system`. GrapheneOS ships modules in full OS updates and updates Vanadium (GPLv2 patches, Chromium 154 in `args.gn`) out of band. Chromium's guide says the AOSP prebuilt WebView "is not currently updated on a regular schedule, and may have known security issues". | P | build@17:`target/product/module_common.mk`, `base_system.mk`; GrapheneOS/Vanadium@main (`LICENSE`, `args.gn`); Chromium "WebView for AOSP system integrators" guide (scratchpad copy, URL not re-verified) |
| F11 | Android 17 `PersistentDataBlockService` has real FRP: a 32-byte secret in the `ro.frp.pst` partition and `/data/system/frp_secret`; FRP defaults active and clears only if the secret matches; `isFactoryResetProtectionActive()` is open; `set/deactivateFactoryResetProtection(secret)` need `CONFIGURE_FACTORY_RESET_PROTECTION`; the permitted package is `config_persistentDataPackageName`; the OEM-unlock bit needs `OEM_UNLOCK_STATE`. AOSP has no FRP UI. GrapheneOS declines FRP (account dependence, brick risk). | P | GrapheneOS/platform_frameworks_base@17:`.../server/pdb/PersistentDataBlockService.java`; FAQ copy |
| F12 | Key Attestation: devices launching with Android 16 are RKP-only; a new ECDSA P-384 root signs chains from 2026-02-01; Google ships a Kotlin verifier library. `rkpd` is disabled when `remote_provisioning.hostname` is empty. Whether Google's RKP backend serves a non-GMS OS is unverified. | P | https://developer.android.com/privacy-and-security/security-key-attestation; android/keyattestation README; GrapheneOS/platform_packages_modules_RemoteKeyProvisioning@17:`util/.../RkpRegistrationCheck.java:114-116` |
| F13 | Zero-fork hardening exists as AOSP makefiles: `memtag-common.mk`, `fullmte.mk`, `cfi-common.mk`. `hardened_malloc` needs a bionic fork. MTE needs ARMv9 (Pixel 8+ per GrapheneOS). GrapheneOS's Setup Wizard turns OEM unlocking off at the end of setup, and it has no automated crash reporting. | P | build@17:`target/product/{memtag-common,fullmte,cfi-common}.mk`; script@17:`common.sh`; features/FAQ copies |
| F14 | `cmd phone emergency-number-test-mode` exists (an emergency-calling gate). The Pixel flash script runs `fastboot oem uart disable` and erases `dpm`/`fips`; it never runs `flashing lock` (manual, physical confirm; see 18). | P | GrapheneOS/platform_packages_services_Telephony@17:`TelephonyShellCommand.java:99,389`; device_common@17:`generate-factory-images-common.sh` |

## Options & trade-offs

| Decision | Options | Verdict |
|---|---|---|
| OTA client | (a) Fork GrapheneOS Updater; (b) LineageOS Updater; (c) hawkBit + hara-ddiclient; (d) Mender; (e) AOSP sample | **(a).** Smallest; already does update_engine, deltas, constraints and downgrade checks. (c)/(d) add a server plus glue for a rollout UI that metadata gives us [I]; revisit (c) past about 50k devices. |
| Key custody | Encrypted files on an offline host (GrapheneOS); YubiHSM 2-class; cloud HSM/KMS | Offline encrypted files for beta (at most 100 devices); HSM via `--signing_helper`/`--payload_signer` for GA; cloud KMS only with the digest helper (F3). |
| WebView | Self-build Chromium stable; consume Vanadium; AOSP prebuilt | **Never the prebuilt.** Self-build monthly on a dedicated runner; Vanadium is a fallback but leans on GrapheneOS hardening. |
| Mainline | Full OTA only; APEX side-channel | Full OTA in v1 (one mechanism, as GrapheneOS); APEX side-channel is Stage 2 [I]. |
| Build infra | Bare metal; cloud spot; GitHub-hosted | Bare metal: constant load; Cuttlefish needs KVM, awkward nested in clouds [I]. |

## Recommended design for Zune

**Keys.** Generate on an air-gapped machine: the AOSP key set (releasekey, platform, shared, media, networkstack, bluetooth, nfc, sdk_sandbox; `make_key`, RSA-4096), one AVB key per model (`SHA256_RSA4096`), and a separate ed25519 key for bundles and metadata. Store as scrypt-encrypted PKCS#8, passphrase split 2-of-3 among custodians, two sealed offsite backups; signing needs two people. CI holds only the metadata key: compromising it can freeze or halt updates but not install anything, because the OTA zip is still checked against `otacerts` and verified boot [I]. Set `BOARD_AVB_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)` and test downgrade rejection per model. Stage 2: chain every partition to delegated keys so the root vbmeta stays cold and a hot key rotates by OTA [I; test per bootloader].

| Key | Compromise effect | Rotation |
|---|---|---|
| AVB (per model) | Malicious images, needs physical write access | Recall: unlock, wipe, re-flash (18) |
| `releasekey` (OTA) | Denial of service; remote takeover only with AVB too | OTA ships a new `otacerts.zip` signed by the old key |
| `platform` and the other app keys | System-privileged app delivered by an APK update | Effectively permanent: HSM, minimal use |

**Pipeline and gates.** The build host builds `user`/`cur` with test keys and emits target-files, otatools, SBOM and GPL sources. Gates G1-G5 run, then two people sign offline (G6), then `check_target_files_signatures -c <previous>`, `validate_target_files` and `check_ota_package_signature` run, and the build goes to staging and rings.

| Gate | Check |
|---|---|
| G1 | Same container on two hosts, diff target-files (pin build time, user, host) |
| G2 | SPDX SBOM, NOTICE; kernel and Vanadium GPL sources published per release |
| G3 | Cuttlefish boot smoke, no-browser/no-YouTube bypass suite (04), policy tests (05, 12), Updater against a fake server, N-1 to N update |
| G4 | `ro.debuggable=0`, adb secure, no permissive SELinux domains, no test keys, SPL monotonic |
| G5 | Real devices, 3 per model and 2 carriers: full and incremental OTA, slot fallback, lock state, attestation, FRP, calls plus `emergency-number-test-mode`, SMS vault |
| G6 | Two-person sign-off |

Full CTS is a GMS-licensing step; run security and SELinux subsets plus our own tests [I].

**OTA service.** Static `/<model>/<channel>.json` on R2/S3+CDN, ed25519-signed: build, SPL, timestamp, full and delta URLs with sha256/size, `rollout_pct`, `min_spl`, `halt`, `expires`. The device keeps a random 0-99 bucket and sends no identifier. Rings: lab 48 h, 5%, 25%, 100% over about 7 days. The client keeps GrapheneOS's checks and adds an SPL >= installed check. Guardian policy sets the window (parent-set, default 01:00-05:00), unmetered Wi-Fi, charging or battery >= 30%, no call in progress, and a free-space precheck. Deadlines: normal 14 days (then any time), critical 72 h via `min_spl`. The child cannot disable it; a bad build gets a roll-forward hotfix (F6). Sizes [I]: full about 1.5-2.5 GB (a Lineage README example is 1.93 GB), monthly delta 0.1-0.4 GB, so 5,000 devices move 0.5-2 TB/month, nearly free on R2 [M]. `--vabc_compression_param=zstd` and `--enable_zucchini`/`--enable_lz4diff` trade build time for size [P].

**Patch train.** Each first Monday: ingest the bulletin, triage, diff the OEM monthly drop. Feeds: AOSP security branch (check with `git ls-remote` from the build host), GrapheneOS `17_MM-DD_base` and LineageOS merges as cross-checks, GKI `android17-6.18` LTS (we rebuild and sign `boot.img`, F5), and Chromium stable as a **separate privileged WebView APK** trusted via a `config_webview_packages` overlay and updated by ZuneUpdater between OTAs [I]. Target [I]: 90% of the fleet on the latest SPL within 10 days. One planned rebase a year onto the June or December AOSP drop. Apps must not load arbitrary URLs in WebView (04, 09).

**Hardening and anti-theft.**
- `user` builds, enforcing SELinux; adopt `memtag-common.mk` and `cfi-common.mk`, trial `fullmte.mk` on MTE devices, defer `hardened_malloc` (bionic fork).
- OEM-unlock bit off after provisioning (F13). Service unlock = parent-authorised signed command that lets Guardian set the bit, then physical confirm and wipe [I].
- **Zune Activation Lock** on F11: the station calls `setFactoryResetProtectionSecret` (Guardian holds `CONFIGURE_FACTORY_RESET_PROTECTION` and is `config_persistentDataPackageName`) and the secret is escrowed server-side under per-family KMS. After a recovery wipe `isFactoryResetProtectionActive()` stays true and our Setup Wizard offers emergency calls only until the parent authenticates and the server releases the secret. Remote wipe must avoid the Settings path that clears the secret [I; check Google's tree]. Lost mode is remote lock plus message.
- Attestation at Guardian check-in, with a server challenge and a pinned attest key: expect `verifiedBootKey` = our AVB key hash, `deviceLocked`, yellow state, SPL at least the minimum. Failure warns the parent and suspends cloud features. Test per model that RKP works (`remote_provisioning.hostname` value unverified); else fall back to station-recorded identity (05).
- A locked bootloader beats Settings, recovery and fastboot, not SoC exploit kits (EDL/BROM/ABL, see 15). OEM patch record is a qualification criterion; attestation and the cloud paywall are the backstop.

**Provisioning/RMA.** Bundles are ed25519-signed by us. The station flashes, sets `avb_custom_key`, locks (manual confirm), turns OEM unlock off, sets the FRP secret, checks attestation, runs QA and enrols. RMA reuses the flow; unlock and lock clear data and rollback indexes (F5).

**Telemetry, disclosure, incidents.** No Google SDKs. Guardian uploads only crash summaries (stack, build id, app version, rotating random install ID; no logcat, content or contacts), parent-visible, kept 30 days, on a self-hosted Sentry-compatible server [M]; deeper logs are user-initiated, as in GrapheneOS [P]. Publish `security.txt` (RFC 9116 [M]), a security@ inbox, a safe-harbour page and 90-day coordinated disclosure; no bounty in v1. Sev1 = any child-safety exposure, bad or malicious OTA, key compromise, data breach; containment uses kill-switches L1-L4 (18). Drill before cohort 1. Counsel owns COPPA, state-breach and (if sold there) EU CRA/UK PSTI duties [M].

**Infra and cost** [M, verify]:

| Item | Choice | Cost |
|---|---|---|
| Build and test | 2 bare-metal hosts, 16C/32T, 128 GB, 2 TB NVMe (AOSP/Cuttlefish; Chromium) | $250-400/mo rented, or about $6k bought |
| CI | GitHub Actions self-hosted, ephemeral, private repo, pinned Ubuntu 24.04 container, no keys | $0 |
| Artifacts | R2 or B2+CDN | under $20/mo |
| Device lab | 3 models x 3 units plus SIMs | $4-8k once, $100-200/mo |
| Signing, telemetry | 2 YubiHSM-class devices plus offline laptop; one small VM | about $2.5k once, $30/mo |

Total about $0.5-0.9k/month plus $10-18k once. No remote build cache needed at this cadence (01).

## Risks & unknowns

- **Security-branch access** (`android17-security-release`) is unverified; non-partner lag was about 125 days (01).
- **AVB key leak or rotation** means a per-phone wipe; per-model keys cap the blast radius.
- **OEM firmware** (bootloader, modem, vendor) needs redistribution rights to ship in our OTA (17), or that layer goes stale.
- **RKP/attestation without GMS**, and the FRP code in Google's own tree, are unverified.
- **Bootloader variance:** chained vbmeta, rollback-index locations, key sizes; test each model on a sacrificial unit.
- **Operating load:** monthly WebView build; Virtual A/B free space on full phones; battery cost of the persistent channel.
- Prices, CRA/PSTI dates and COPPA conclusions are [M] or counsel items.

## Decisions needed from the founder

1. Support promise: contractual 3 years, target 5, per-model end date? (Default: yes.)
2. Name three key custodians and approve about $2.5k signing hardware and the offline-signing rule.
3. Fund a 0.5-1 FTE release/security owner; authorise partner-access outreach to Google/ODM.
4. Approve forking GrapheneOS's MIT Updater and the static-CDN design.
5. Bare-metal build hosts (default) or cloud.
6. Forced-update policy: 14 days normal, 72 h critical, daytime reboot and metered data at the deadline?
7. Default screen lock (none or parent-set PIN) and whether lost mode includes location.
8. Crash reporting: default-on with parent consent, or opt-in?
9. Confirm US-only launch; EU/UK rules (CRA, PSTI, ecodesign) would change the support promise and disclosure duties.

## Load-bearing claims

1. GrapheneOS's Updater is 1,377 lines, MIT, update_engine-based, static-file driven (GrapheneOS/platform_packages_apps_Updater@17) [P].
2. `avbtool --signing_helper` takes padded digests; `ota_from_target_files --payload_signer` exists (`avbtool.py:543-600`; script help) [P].
3. SPL downgrade is blocked on locked release-keys devices, so rollback means roll-forward (`ota_from_target_files.py:1426-1446`; `delta_performer.cc:443-480`) [P].
4. A custom AVB key is set only while unlocked and lock transitions wipe data and rollback indexes, so AVB-key rotation is a recall (LineageOS/android_external_avb README) [P].
5. Android 17 has FRP-secret primitives and no FRP UI (`PersistentDataBlockService.java`, GrapheneOS frameworks/base@17) [P]; Google's tree unchecked.
6. AOSP test keys are public and must never ship; offline signing covers about 44 APEX modules (`target/product/security/README`; `generate-release.sh`) [P].
7. AOSP's prebuilt WebView is not regularly updated and Mainline builds from source, so every fix ships through our pipeline (Chromium guide; `module_common.mk`) [P].
8. Even a partner ships about weekly (43 tags in 260 days, `git ls-remote`) [P]; non-partner lag about 125 days (01) [P via 01].
9. Attestation is RKP-only for Android-16-launch devices and `rkpd` is off without a hostname property (developer.android.com; `RkpRegistrationCheck.java`) [P].
10. hawkBit and Mender do not target `update_engine` (READMEs) [P]; the fit call is [I].
