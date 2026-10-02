# Zune research 05: Parental-controls platform (portal, on-device enforcement, sync)

Date 2026-10-02. Tags: **[P]** read in a primary source/real file this session; **[S]** reputable secondary or search summary; **[I]** my judgement; **[M]** memory, unchecked. Google's source and help sites were blocked, so no `android-17.0.0_r1` file was read directly. Keys: **GOS-fwb/perm/set/brel/rkp@17** = GrapheneOS `platform_frameworks_base`, `packages_modules_Permission`, `packages_apps_Settings`, `build_release`, `packages_modules_RemoteKeyProvisioning`, branch `17` (HEADs 2026-09-22..30: newer than the tag, with GrapheneOS edits). **AOSP16** = `aosp-mirror/platform_frameworks_base@android16-qpr1-release` (unmodified). **HMDM** = GitHub `h-mdm/hmdm-android`, `hmdm-server`.

## 1. Summary & recommendation

1. **`ZuneGuardian` = first-party privileged app that is Device Owner and holds Android's `SYSTEM_SUPERVISION` role**, both assigned by ZuneSetup before setup completes, plus the `ZunePolicyService` that report 12 already needs as the single verified policy store (hybrid option c). Supervision itself needs no framework fork.
2. **Android's consumer parental controls are not in AOSP.** AOSP has plumbing (service, role, bound app service, permission grants) with every config hook empty; features and the Family Link backend are Google's, and Android Management API needs Play Services. We build the engine, backend and portal.
3. **Cloud is authority; device enforces locally from signed bundles.** Sync is a doorbell on one persistent WebSocket with polling fallback. No FCM, no UnifiedPush.
4. **Fail closed by construction:** no browser, every app is a system app, and a claim lock in the persistent data block survives recovery wipes. A wiped device offers only pairing and emergency calls.
5. **Go + Postgres + Redis in one US region, per-family KMS envelope encryption; React PWA portal with passkeys.** Attestation is a signal, not the root of trust (F8).
6. Two conflicts with other reports need a decision (4.8): socket owner, and 04's reliance on the unfinished platform time-limit policy.

## 2. Findings

**F1. AOSP ships supervision plumbing; Google ships the product.**
- AOSP16 has `SupervisionManager`, `SupervisionService`, `SupervisionAppService`; `Policy`/`PackageUsagePolicy` are absent there (404) and arrive in 17 [P: AOSP16 raw paths; GOS-fwb `core/java/android/app/supervision/`].
- `config_defaultSupervisionProfileOwnerComponent`, `config_systemSupervision`, `config_allowedSupervisionRolePackages`, `config_supervisedUserCreationPackage` are empty [P: GOS-fwb `core/res/res/values/config.xml:6281,6284,6289,7336`]. A comment says the PO component "is used to give GMS Kids Module permission to supervise" [P: `SupervisionService.java:1108-1118`].
- Settings' Supervision dashboard is a shell binding a Messenger service in the `config_systemSupervision` package [P: GOS-set `.../supervision/ipc/SupervisionMessengerClient.kt`].
- Screen time, downtime, app limits and PIN are consumer features run via Family Link and a Google account [S: https://support.google.com/android/answer/16766047]. Android Management API needs Play Services [S: https://developers.google.com/android/management]. Zero-touch is Google's reseller program [M].

**F2. The role is powerful and system-only.** `SYSTEM_SUPERVISION` is `systemOnly`, `exclusive`, `static`, default holder `config_systemSupervision`; it grants `SUSPEND_APPS`, `MANAGE_SUPERVISION`, `MANAGE_PROFILE_AND_DEVICE_OWNERS`, `MANAGE_DEVICE_POLICY_{LOCK, LOCK_TASK, TIME, SAFE_BOOT, FACTORY_RESET, KEYGUARD, LOCATION, PACKAGE_STATE, APPS_CONTROL, RUNTIME_PERMISSIONS...}`; no WIPE_DATA, private-DNS or VPN permission [P: GOS-perm `PermissionController/res/xml/roles.xml:1394-1459`]. Flags for the permission update (bp2a), app service (bp4a) and policy APIs (cp2a) are ENABLED, READ_ONLY [P: GOS-brel `aconfig/*/`]. The system binds the holder's `SupervisionAppService` and rebinds after a crash [P: `SupervisionAppService.java`; `appbinding/finders/SupervisionAppServiceFinder.java`].

**F3. Platform policy is thin.** Only `PackageUsagePolicy` (ALLOWED/BLOCKED/TIME_LIMIT) via hide/suspend; `TIME_LIMIT` suspends at once (`TODO(b/482425646)`, own flag) [P: `SupervisionService.java:490-505`]. No schedule, contact, content or web policy. We own the engine and use the platform for primitives.

**F4. Primitives.** The role wins `AUTO_TIME` resolution [P: `devicepolicy/handlers/PolicyDefinitionFactory.java` ~112-130]. Lock task and the secondary lock screen accept the role holder [P: `DevicePolicyManagerService.java:14267-14290,14458-14469`]. `DISALLOW_{SAFE_BOOT, FACTORY_RESET, DEBUGGING_FEATURES, CONFIG_DATE_TIME, INSTALL_APPS, UNINSTALL_APPS, OEM_UNLOCK, ADD_USER, CONFIG_PRIVATE_DNS, CONFIG_VPN}` exist [P: `UserManager.java`]. Restricted profiles exist but are legacy [P: `UserManager.java:171-175`].

**F5. Provisioning hooks.** `EnableSupervisionActivity` skips confirmation until user setup completes [P: GOS-set `EnableSupervisionActivity.kt`]. A Device Owner "can only be set by adb or an app with the MANAGE_PROFILE_AND_DEVICE_OWNERS permission" [P: `DevicePolicyManagerService.java:10643`]; after setup only the supervision component may become profile owner [P: `:10634`]. QR enrollment works without GMS [P: HMDM README].

**F6. Reset persistence.** The persistent data block (PDB) survives resets "not initiated via the Settings UI"; only the uid of `config_persistentDataPackageName` (empty by default) may use it [P: `services/core/java/com/android/server/pdb/PersistentDataBlockService.java:83,349-354`; `config.xml:4132`].

**F7. Push without GMS.** Headwind runs Paho MQTT in `mqttWorker`/`mqttAlarm` modes, optional foreground service, 900 s reconnect worker, plus HTTP long-polling fallback [P: HMDM `app/build.gradle`, `PushNotificationMqttWrapper.java`, `PushLongPollingService.java`]; three modes suggest no single one survives Doze and OEM killers [I]. UnifiedPush/ntfy (Apache-2.0 + GPLv2) serve third-party apps through a distributor app [P: ntfy README; S: https://unifiedpush.org/]. Privileged apps can be Doze-exempted by sysconfig `allow-in-power-save` [P: GOS-fwb `SystemConfig.java:97-99,978-984`]; SystemUI is `android:persistent` [P: AOSP16 `packages/SystemUI/AndroidManifest.xml:410`]. microG relays GCM; GrapheneOS leaves push to apps [M].

**F8. Attestation leans on Google.** Devices launching with Android 16 support only RKP; verify chains server-side, check the CRL, use Google's `android/keyattestation` (Apache-2.0, Kotlin) [P: https://developer.android.com/privacy-and-security/security-key-attestation; https://raw.githubusercontent.com/android/keyattestation/main/README.md]. rkpd reads its server from system property `remote_provisioning.hostname`, empty by default [P: GOS-rkp `app/src/com/android/rkpdapp/utils/Settings.java:253-265`]. GrapheneOS fronts Google's service with its own proxy [S: grapheneos.org FAQ, search summary].

**F9. Reusable projects: learn, do not adopt.**

| Project | License | Note |
|---|---|---|
| Headwind MDM server + launcher | Apache-2.0 [P] | DO-based; kids shell, settings lock, kiosk are paid Enterprise [P: server README] |
| Flyve MDM agent | GPLv3 [P] | Archived 2021 [S]; avoid |
| TestDPC; KidSafe, OpenScreenTime | Apache-2.0 [P]; MIT [P, S] | API reference; userland hobby apps |
| Pinwheel, Troomi, Bark | n/a | Custom Android + MDM + portal [S: Screenwise, Android Central summaries] |

**F10. Family Link bypasses:** clock/time zone, factory reset, second account, ADB, WebView links in Help/ToS, safe mode [S: https://www.bitdefender.com/en-us/blog/hotforsecurity/family-link-bypass-android-2025].

**F11. Legal hooks.** Amended COPPA Rule (comply by 2026-04-22): written security program, retention policy, separate consent for third-party disclosure; geolocation and audio are personal information [S: https://www.hunton.com/privacy-and-cybersecurity-law-blog/coppa-rule-amendment-compliance-deadline-approaches]. California AB 1043 (operative 2027-01-01): OS providers collect age at setup and expose an age-bracket signal [S: https://reclaimthenet.org/california-ab-1043-os-age-verification-law]. Counsel via topic 11.

## 3. Options & trade-offs

| Option | Tamper resistance | Update agility | Complexity | Verdict |
|---|---|---|---|---|
| (a) Device Owner DPC only | Good | High (APK) | Medium | Lacks role plumbing and a framework policy store |
| (b) Platform service + hooks | Highest | OTA only | High; rebase every Q2/Q4 | Only for 04/12 patches |
| **(c) DO + role app + `ZunePolicyService`** | High | High for logic | Medium | **Recommend** |
| (d) AMAPI / Family Link | n/a | n/a | n/a | Impossible without GMS |

DO is a one-way door: it can be set only during provisioning, so adding it later means a wipe. It is cheap now and keeps 04's Stage 2 private-DNS/VPN options open [I].

## 4. Recommended design for Zune

**4.1 On-device.** `ZuneGuardian` in `/system_ext/priv-app`, `persistent`, privapp-permissions allowlist; RRO sets `config_systemSupervision` and `config_persistentDataPackageName` to it. Parts: bundle fetcher, evaluator, usage accountant (UsageStats), enforcer behind an `EnforcementBackend` interface, approvals UI with parent PIN, command executor, uploader, claim lock. Primitives: `setPackagesSuspended` with an "ask a parent" dialog for budgets; lock task or secondary lock screen for bedtime (dialer and SOS allowed); user restrictions; forced auto time. Single user. Hide Settings' Supervision entry or implement its Messenger service.

**4.2 Pairing, claim, transfer.**
- ZuneSetup creates an attested EC key (StrongBox if present) and calls `enroll/begin`. A guardian logs into the portal, taps "Add device", picks the child; the portal shows a one-time QR plus 8-char code (10 min, single use, rate-limited). **The device scans it** (typed fallback), so the secret originates in an authenticated parent session and no browser barcode API is needed.
- Server binds key to family and child and returns the first bundle. ZuneSetup enables supervision, sets DO, writes the PDB claim blob (claim id, family hash), then completes setup.
- After a wipe ZuneSetup reads the blob and accepts only a code from a guardian of that family, or a server-side release. Otherwise the device stays inert.
- v1 (D16): the provisioning station flashes, relocks and registers the phone (serial hash, attestation) as "unclaimed"; the parent scans at hand-over.
- Release/resale: the owner taps "Release device" (passkey step-up); the device gets a signed `unenroll`, wipes (`MASTER_CLEAR` [M]) and clears the blob. The customer owns the phone (D15), so the lock must never strand them: lost access goes to support (proof of purchase from the intake order), plus a "return to stock" station service.
- Schema is `child -> N device keys` from day one; Stage 1 UI allows one active device per child.

**4.3 Family model.** Family -> Guardians; Family -> Children -> Devices. Policy resolves family template (age band) -> child -> device override; safety settings take the most restrictive.

| Role | Can |
|---|---|
| Owner | All, billing, release/transfer, add/remove guardians |
| Guardian | Full child policy, contacts (13's handshake), reports, approvals |
| Caregiver (grandparent) | Per child, optionally time-boxed: approve time, locate, lock; no contacts, AI or transcript changes |

Co-parent changes need step-up auth and notify all guardians; every change enters an append-only hash-chained audit log guardians can read. Custody disputes: equal guardians plus a support-held freeze [I].

**4.4 Policy bundle.** Per-section revisions, canonical JSON (RFC 8785), JWS ES256 with a KMS-held key; an offline root pinned in the image signs 90-day signer certs. `ZunePolicyService` verifies and stores it (12's `/data/system/zune/policy.bin`); Guardian only fetches. Monotonic `rev` blocks rollback; `not_after` bounds staleness.

```json
{"v":1,"device":"d_1","rev":128,"not_after":"...","tz":"America/Chicago",
 "screen_time":{"daily_min":{"mon":120},"downtime":[{"days":["sun"],"from":"20:00","to":"07:00"}]},
 "apps":{"default":"allow","rules":[{"pkg":"app.zune.videos","state":"limit","daily_min":30}]},
 "contacts":{"rev":77,"entries":[{"e164":"+1...","dir":["in","out"],"ch":{"msg":1,"video":1,"ptt":1}}]},
 "content":{"age_band":"6-8","topics":["space"]},"assistant":{"on":true,"images":true,"transcripts":"full"},
 "location":{"mode":"off","visible_to_child":true},"sos":{"sms_fallback":true},"offline_grace_days":14}
```
- **Offline:** enforcement is local. Past `not_after` plus grace (default 14 days, as in 12) the device drops to guardians and emergency only, never fail-open.
- **Trusted time:** responses carry signed server time. Device stores (server time, elapsedRealtime, boot count); effective now = max(derived time, last trusted wall clock); rollback over 5 minutes is flagged to parents. Time and zone are forced automatic, Settings has no date page, schedules use the policy `tz`.
- **Approvals:** `approval.request{time|app|contact|topic|video}` goes to the guardian; one tap issues a TTL'd signed grant. Offline, a parent PIN (Keystore HMAC, escalating lockout) gives a time-boxed override, synced later.
- **Remote lock, find, SOS:** signed commands with nonce and expiry. SOS alerts guardians over WS with SMS fallback; it is separate from the always-available 911 call.
- **Location:** default off, per-child opt-in, child-visible indicator, 30-day retention [I]; overt, never covert.

**4.5 Sync.** Choose one TLS WebSocket as a doorbell: `policy.update{section, rev}`, then HTTPS `GET policy?since=rev`. Commands carry their own signatures, so any transport can deliver them. Fallbacks: JobScheduler 15 min, Doze-allowed alarms, reconnect on connectivity; SMS wake-up is Stage 2. Rejected: gRPC (carrier-proxy risk, no gain over 13's WS protocol), UnifiedPush (needs a distributor app), OEM push (vendor clouds) [I]. Doze: `allow-in-power-save` plus a persistent process; battery unmeasured [I]. **`ZuneGuardian` owns the socket**; ZuneComms, ZunePhone and the SMS vault use its Binder `ILink`, since the platform keeps that process bound and restarted (F2) and the control plane must outlive messenger bugs. Parents get Web Push (iOS needs Home Screen install [S: https://www.pushengage.com/documentation/setting-up-web-push-notifications-for-ios-ipad/]), email, and SMS for safety alerts.

**4.6 Backend and portal.**
- **Stack:** Go (one codebase with 13's `comms-api`), Postgres (usage as per-day per-app aggregates), Redis pub/sub for socket routing, S3-compatible storage, per-family KMS DEKs with crypto-shredding, AWS us-east-2 [I]. Kotlin/JVM would share policy code with the device, but Go wins on socket density and 13. Portal: React PWA, mobile-first, OpenAPI REST (`/v1/families/{f}/children/{c}/policy`; device `/v1/devices/{d}/{policy,events,approvals}`), SSE for live status.
- **Auth:** passkeys (go-webauthn BSD-3 [P] or SimpleWebAuthn MIT [P]), email OTP fallback, TOTP step-up. Devices: Keystore key signs challenges for short-lived tokens. A Kotlin sidecar using `android/keyattestation` checks the chain and pins our AVB key hash (yellow boot state with a custom key, per 15). Gate hard at the v1 station; at claim, a failed chain raises an integrity warning, but an unreachable RKP falls back to the station-recorded identity so a paying family is not stranded (F8).
- **Compliance hooks:** per-class retention (messages 180 d per 13, usage 90 d, location 30 d), consent ledger, DSAR export/delete, no third-party SDKs on device, RBAC with dual-approved break-glass staff access, AgeSignal provider from the setup age band.
- **Observability:** OpenTelemetry with PII scrubbing; SLOs on policy propagation (p95 under 10 s) and enforcement drift (acked vs server rev); alert parents when a device goes quiet.

Infra only, **excluding LiveKit, AI, SMS, carrier, staff**; rough, about 2x either way [I]:

| Devices | Shape | Monthly | Per device |
|---|---|---|---|
| 1k | 2 small nodes, small HA Postgres, small Redis | $250-500 | $0.25-0.50 |
| 10k | 3 nodes, mid HA Postgres, Redis | $0.9-2.2k | $0.09-0.22 |
| 100k | 4-6 nodes (100k sockets), large Postgres + replica, Redis cluster | $6-15k | $0.06-0.15 |

Logs and Postgres writes dominate; 13's "few hundred dollars" at 10k looks low once HA and observability count. v1 is company-provisioned (D16): 1k is the design point.

**4.7 Tamper matrix.**

| Attack | Mitigation |
|---|---|
| Uninstall/disable Guardian | System priv-app, DO, `DISALLOW_UNINSTALL_APPS`, `setUserControlDisabledPackages`, no app-list UI |
| Clock or time zone | Forced auto time, no UI, trusted-time floor, rollback flag |
| Settings factory reset | `DISALLOW_FACTORY_RESET`, no UI |
| Recovery wipe | PDB claim lock, inert unpaired state, portal alert on re-pair |
| Safe mode | `DISALLOW_SAFE_BOOT`; all apps are system apps, so nothing extra runs |
| ADB/developer options | `user` build, no developer UI, `DISALLOW_DEBUGGING_FEATURES` |
| Reflash/bootloader | Locked bootloader with our AVB key (yellow boot screen), OEM unlock off; ABL/EDL bugs are a device-selection risk (15) |
| Network blackhole, crash | Local enforcement; grace then minimal mode; role rebind |
| SIM swap | Call/SMS controls are on-device only; carrier lock is Stage 2 (12) |
| WebView link-outs | Topic 04 |

**4.8 Reconciliation.** 12: adopt `ZunePolicyService`, 14-day grace, never fail open. 04: drop reliance on `PackageUsagePolicy` time limits (F3); use suspend. 13: adopt contact graph, WS envelope, 180-day retention, Go; change socket owner and allow N devices per child. 17: same first-boot QR flow and Release/return-to-stock path; it hard-gates enrolment on attestation, which this report softens at claim. 03 Q5 answered: role + DO; ManagedProvisioning can stay out because system code sets DO directly [I].

## 5. Risks & unknowns
- GOS trees are not the pristine tag; re-verify every cited file on `android-17.0.0_r1` once AOSP is reachable.
- Role grants may miss restrictions we need (private DNS, VPN, OEM unlock, wipe); DO or 04's system-asserted set fills gaps. Validate on Cuttlefish, with DO UX strings and `setDeviceOwner` timing.
- The supervision API is flagged and moving; `EnforcementBackend` isolates it, CI runs each rebase.
- RKP refresh needs a configured host (17 also flags the Google dependency). BYO phones keep OEM vendor props, which may already set it; check per device in 15's qualification.
- Socket battery and carrier NAT timeouts are unmeasured.
- The server holds children's location, SMS and transcripts; a breach is existential. 24/7 SOS staffing is a dependency.
- Location, AB 1043 and COPPA retention are not counsel-reviewed; costs are estimates.

## 6. Decisions needed from the founder
1. Approve DO plus role (one-way door at provisioning).
2. Resale: hard claim lock with support override (recommended) vs soft.
3. Location sharing in Stage 1 (default off, opt-in) or defer.
4. Child sees what parents see (recommended).
5. Caregiver (grandparent) roles in Stage 1 or 2.
6. Offline grace default (14 days) and minimal-mode behavior.
7. Who staffs SOS and safety alerts 24/7.
8. Parent scans at hand-over (recommended) vs station pre-binds the phone to the family at intake.

## 7. Load-bearing claims
1. AOSP has the supervision service, role, bound app service and empty config hooks; consumer features are Google's. [P] AOSP16 raw paths; GOS-fwb `config.xml:6281-6289`.
2. The role grants `SUSPEND_APPS` and `MANAGE_DEVICE_POLICY_{LOCK_TASK, TIME, SAFE_BOOT, FACTORY_RESET...}`; flags enabled. [P] GOS-perm `roles.xml:1394-1459`; GOS-brel `aconfig`.
3. Platform `TIME_LIMIT` is unfinished, so we own the engine. [P] `SupervisionService.java:503`.
4. The role wins `AUTO_TIME`, defeating clock tampering. [P] `PolicyDefinitionFactory.java`.
5. Supervision enables without a dialog before setup completes; a permissioned app can set DO. [P] `EnableSupervisionActivity.kt`; `DevicePolicyManagerService.java:10643`.
6. PDB survives non-Settings resets, gated by `config_persistentDataPackageName`. [P] `PersistentDataBlockService.java:83,349`.
7. AMAPI and Family Link need Google services. [S] search summaries.
8. Android 16-launch devices support only RKP; rkpd host is a system property. [P] developer.android.com; GOS-rkp `Settings.java:253`.
9. No-GMS MDMs use own MQTT plus long-polling; sysconfig Doze allowlist is honored. [P] HMDM; `SystemConfig.java:978`.
