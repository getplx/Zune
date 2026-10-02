# Zune research 05: Parental-controls platform (portal, on-device enforcement, sync)

Date 2026-10-02. Tags: **[P]** read in primary source/real file this session; **[S]** reputable secondary or search summary; **[I]** my judgement; **[M]** memory, unchecked. source.android.com, android.googlesource.com, developers.google.com, blog.google, support.google.com were blocked, so no `android-17.0.0_r1` file was read directly. Source keys: **GOS-x@17** = GrapheneOS `platform_frameworks_base` (fwb), `packages_modules_Permission` (perm), `packages_apps_Settings` (set), `build_release` (brel), `packages_modules_RemoteKeyProvisioning` (rkp), branch `17` (HEADs 2026-09-22..30: newer than the tag, with GrapheneOS edits). **AOSP16** = `aosp-mirror/platform_frameworks_base@android16-qpr1-release` (unmodified). **HMDM** = `h-mdm/hmdm-android` and `hmdm-server` (GitHub).

## 1. Summary & recommendation

1. **Build `ZuneGuardian` as a first-party privileged app that is Device Owner and holds Android's `SYSTEM_SUPERVISION` role**, both assigned by ZuneSetup before setup completes, plus the `ZunePolicyService` already required by report 12 as the single verified policy store. This is the hybrid (c). Framework patches stay at what 04 and 12 already budget; supervision itself needs none.
2. **Android's consumer parental controls are not in AOSP.** AOSP has the plumbing (service, role, bound app service, permission grants) with every config hook empty. The features and Family Link backend are Google's. Android Management API needs Play Services. We build the policy engine, backend and portal.
3. **Cloud is authority, device enforces locally from signed bundles.** Sync is a doorbell over one persistent WebSocket, with polling fallback. No FCM, no UnifiedPush.
4. **Fail closed by construction.** No browser, every app is a system app, a "claim lock" in the persistent data block survives recovery wipes. A wiped device only offers pairing and emergency calls.
5. **Backend: Go + Postgres + Redis, one US region, per-family KMS envelope encryption. Portal: React PWA, passkeys.** Attestation is a signal, not the root of trust (RKP dependency, F8).
6. Reconciliation with other reports is in 4.8. Two conflicts need a decision: who owns the socket (13 vs here) and platform time-limit policy (04 relies on it; it is unfinished).

## 2. Findings

**F1. AOSP ships supervision plumbing; Google ships the product.**
- AOSP16 already has `SupervisionManager`, `SupervisionService`, `SupervisionAppService`; `Policy`/`PackageUsagePolicy` are absent there (404) and arrive in 17 [P: AOSP16 raw paths; GOS-fwb@17 `core/java/android/app/supervision/`].
- `config_defaultSupervisionProfileOwnerComponent`, `config_systemSupervision`, `config_allowedSupervisionRolePackages`, `config_supervisedUserCreationPackage` are all empty [P: GOS-fwb `core/res/res/values/config.xml:6281,6284,6289,7336`]. The code comment says the PO component "is used to give GMS Kids Module permission to supervise" [P: `services/supervision/.../SupervisionService.java:1108-1118`].
- Settings' Supervision dashboard is a shell that binds a Messenger service in the `config_systemSupervision` package for its data [P: GOS-set `src/com/android/settings/supervision/ipc/SupervisionMessengerClient.kt`].
- Screen time, downtime, app limits and the PIN are Android's consumer controls, run by Family Link and need a Google account [S: https://support.google.com/android/answer/16766047 (search summary)]. Android Management API/Android Device Policy need Play Services [S: https://developers.google.com/android/management (search summary)]. Zero-touch is a Google reseller program [M].

**F2. The role is powerful and system-only.** `SYSTEM_SUPERVISION`: `systemOnly`, `exclusive`, `static`, default holder `config_systemSupervision`; grants `SUSPEND_APPS`, `MANAGE_SUPERVISION`, `MANAGE_PROFILE_AND_DEVICE_OWNERS` and `MANAGE_DEVICE_POLICY_{LOCK, LOCK_TASK, TIME, SAFE_BOOT, FACTORY_RESET, KEYGUARD, LOCATION, PACKAGE_STATE, APPS_CONTROL, RUNTIME_PERMISSIONS...}` [P: GOS-perm `PermissionController/res/xml/roles.xml:1394-1459`]. Flags `supervision_role_permission_update_enabled` (bp2a), `enable_supervision_app_service` (bp4a), `enable_supervision_manager_policy_apis` (cp2a) are ENABLED, READ_ONLY [P: GOS-brel `aconfig/*/`]. The system binds the holder's `SupervisionAppService` and rebinds after a crash [P: `SupervisionAppService.java` javadoc; `appbinding/finders/SupervisionAppServiceFinder.java`]. `MANAGE_DEVICE_POLICY_WIPE_DATA` and private-DNS/VPN permissions are not in the role grant [P: same file].

**F3. Platform policy is thin and unfinished.** Only `PackageUsagePolicy` (ALLOWED/BLOCKED/TIME_LIMIT) via hide/suspend. `TYPE_TIME_LIMIT` suspends immediately (`TODO(b/482425646)`, separate flag) [P: `SupervisionService.java:490-505`]. No schedule, contact, content or web policy. We own the engine and use the platform for primitives only.

**F4. Coexistence and primitives.** The role wins `AUTO_TIME` resolution (TopPriority: SYSTEM_SUPERVISION, financed controller, DPC) [P: `devicepolicy/handlers/PolicyDefinitionFactory.java` ~112-130]. Lock task and the secondary lock screen accept the role holder [P: `DevicePolicyManagerService.java:14267-14290, 14458-14469`]. `DISALLOW_{SAFE_BOOT, FACTORY_RESET, DEBUGGING_FEATURES, CONFIG_DATE_TIME, INSTALL_APPS, UNINSTALL_APPS, OEM_UNLOCK, ADD_USER, CONFIG_PRIVATE_DNS, CONFIG_VPN}` all exist [P: `UserManager.java`]. Restricted profiles exist but are legacy and useless for a single-kid device [P: `UserManager.java:171-175`].

**F5. Provisioning hooks.** `EnableSupervisionActivity` skips confirmation until user setup completes [P: GOS-set `EnableSupervisionActivity.kt` `canSkipUserConfirmation`]. A Device Owner "can only be set by adb or an app with MANAGE_PROFILE_AND_DEVICE_OWNERS" [P: `DevicePolicyManagerService.java:10643`]. After setup only the supervision component may become profile owner [P: `:10634`]. Google itself uses PO plus role during its transition [P: `SupervisionService.java:1087-1118`]. QR enrollment works without GMS [P: HMDM README].

**F6. Reset persistence.** The persistent data block (PDB) survives resets "not initiated via the Settings UI"; only the uid of `config_persistentDataPackageName` (default empty) can read/write it; credential FRP is on by default [P: GOS-fwb `services/core/java/com/android/server/pdb/PersistentDataBlockService.java:76-80,345-352`; `config.xml:1530,4132`].

**F7. Push without GMS.** Headwind (Apache-2.0) runs Paho MQTT with `mqttWorker`/`mqttAlarm` modes, an optional foreground service, a 900 s reconnect worker, plus HTTP long-polling fallback, because Doze and OEM killers defeat any single mode [P: HMDM `app/build.gradle`, `PushNotificationMqttWrapper.java`, `PushLongPollingService.java`]. UnifiedPush/ntfy (Apache-2.0 + GPLv2) are built for third-party apps needing a distributor app [P: ntfy README license; S: https://unifiedpush.org/]. A privileged app can be exempted from Doze via sysconfig `allow-in-power-save` [P: GOS-fwb `SystemConfig.java:97-99,978-984`]; SystemUI is `android:persistent` [P: AOSP16 `packages/SystemUI/AndroidManifest.xml:410`]. microG relays GCM and GrapheneOS leaves push to apps [M].

**F8. Attestation depends on Google infrastructure.** Devices launching with Android 16 support only RKP; verify chains server-side, check the CRL, use `android/keyattestation` (Apache-2.0, Kotlin) [P: https://developer.android.com/privacy-and-security/security-key-attestation; https://raw.githubusercontent.com/android/keyattestation/main/README.md]. rkpd takes its server from system property `remote_provisioning.hostname`, empty by default [P: GOS-rkp `app/src/com/android/rkpdapp/utils/Settings.java:253-265`]. GrapheneOS fronts Google's service with its own proxy [S: grapheneos.org FAQ (search summary)].

**F9. Reusable projects: learn, do not adopt.**

| Project | License | Note |
|---|---|---|
| Headwind MDM server + launcher | Apache-2.0 [P] | DO-based; kids shell, settings lock, kiosk are paid Enterprise features [P: server README] |
| Flyve MDM agent | GPLv3 [P], archived 2021 [S] | Dead; copyleft |
| TestDPC / enterprise-samples | Apache-2.0 [P] | API reference |
| KidSafe | MIT [P] | Userland hobby app |
| OpenScreenTime | MIT [S] | Userland hobby app |
| Pinwheel/Troomi/Bark | n/a | Custom Android + MDM + portal; no browser makes bypass hard; parents see deleted texts [S: Screenwise, Android Central summaries] |

**F10. Known Family Link bypasses:** time-zone/clock change, factory reset, second account or age-13 opt-out, ADB (Chronolink), hidden browsers via Help/ToS WebView links, safe mode [S: https://www.bitdefender.com/en-us/blog/hotforsecurity/family-link-bypass-android-2025; https://whitelist.video/blog/how-kids-bypass-google-family-link].

**F11. Legal hooks.** Amended COPPA Rule: effective 2025-06-23, comply by 2026-04-22; written security program, retention policy, separate consent for third-party disclosure; geolocation, audio and biometrics are personal information [S: https://www.hunton.com/privacy-and-cybersecurity-law-blog/coppa-rule-amendment-compliance-deadline-approaches; https://www.lw.com/en/insights/ftc-publishes-updates-to-coppa-rule]. California AB 1043 (operative 2027-01-01): OS providers collect age at setup and expose an age-bracket signal (<13, 13-15, 16-17, 18+) [S: https://reclaimthenet.org/california-ab-1043-os-age-verification-law; https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB1043 (not fetchable)]. Counsel via topic 11.

## 3. Options & trade-offs

| Option | Tamper resistance | Update agility | Complexity | Verdict |
|---|---|---|---|---|
| (a) Device Owner DPC only | Good; DO removal needs wipe | High (APK) | Medium; enterprise UX strings | Too thin alone: no role plumbing, no framework policy store |
| (b) Platform service + framework hooks | Highest | Low (OS OTA only) | High; rebase tax every Q2/Q4 drop | Only for the three patches below |
| **(c) DO + role holder app + small `ZunePolicyService`** | High | High for logic, OTA for patches | Medium | **Recommend** |
| (d) AMAPI / Family Link | n/a | n/a | n/a | Impossible without GMS (F1) |

DO is a one-way door: it can only be set during provisioning, so adding it later means a wipe. It is cheap now and keeps 04's Stage 2 private-DNS/VPN needs open [I].

## 4. Recommended design for Zune

**4.1 On-device.** `ZuneGuardian` in `/system_ext/priv-app`, `persistent`, privapp-permissions allowlist. RRO: `config_systemSupervision`, `config_persistentDataPackageName` = `app.zune.guardian`; others empty. Internals: bundle fetcher, policy evaluator, usage accountant (UsageStats), enforcer behind an `EnforcementBackend` interface (role+DO now), approvals UI with parent PIN, command executor, aggregate uploader, claim lock. Primitives: `setPackagesSuspended` with a kid-friendly dialog for budgets; lock task or secondary lock screen for bedtime with dialer/SOS allowed; user restrictions; forced auto time. Hide Settings' Supervision entry or implement its Messenger service. Single user only (`DISALLOW_ADD_USER`).

**4.2 Pairing, claim, transfer.**
- First boot: ZuneSetup creates an attested EC key (StrongBox if present) and calls `enroll/begin`. A guardian logs into the portal (passkey), taps "Add device", picks the child; the portal shows a one-time QR plus 8-char code (10 min, single use, rate-limited). **The device scans it** (typed fallback). Direction matters: the secret originates in an authenticated parent session, and no browser barcode API is needed.
- Server binds device key to family and child, returns the first bundle. ZuneSetup enables supervision, sets DO, writes the PDB claim blob (`claim_id`, family hash), then completes setup.
- Wiped device: ZuneSetup reads the blob, shows "belongs to a Zune family", accepts only a code from a guardian of that family or from a server-side release. Otherwise it stays inert.
- Resale: owner starts "Release device" with passkey step-up. The device receives a signed `unenroll`, wipes (`MASTER_CLEAR`, verify [M]) and clears the blob. Lost-access path: support verifies proof of purchase, then releases. Optional claim card in the box.
- Multiple children: one active device per child in Stage 1 UI, but the schema is `child -> N device keys` from day one (13's "kid bound to a paired device" must allow N credentials).

**4.3 Family model and roles.** Family -> Guardians; Family -> Children -> Devices. Policy resolves family template (age band) -> child -> device override; safety-relevant settings take the most restrictive.

| Role | Can |
|---|---|
| Owner | Everything, billing, release/transfer, add or remove guardians |
| Guardian | Full child policy, contacts (13's handshake), reports, approve requests |
| Caregiver (grandparent) | Per-child, optionally time-boxed: approve time requests, locate, lock; no contacts, AI or transcript changes |

Co-parent invites and removals need step-up auth and notify all guardians. Every change is attributed in an append-only, hash-chained audit log visible to guardians. Custody disputes: equal guardians plus a support-held freeze [I].

**4.4 Policy bundle.** JSON per-section revisions, canonicalized (RFC 8785), signed as a JWS (ES256, KMS-held key). Trust: offline root key pinned in the image signs a 90-day signer certificate; the device pins only the root. `ZunePolicyService` verifies, stores and exposes it (report 12's `/data/system/zune/policy.bin`); Guardian only fetches. Anti-rollback by monotonic `rev`; staleness by `not_after`.

```json
{"v":1,"child":"c_1","device":"d_1","rev":128,"issued_at":"...","not_after":"...","tz":"America/Chicago",
 "screen_time":{"daily_min":{"mon":120,"sat":180},"downtime":[{"days":["sun","mon"],"from":"20:00","to":"07:00"}],"school":[...]},
 "apps":{"default":"allow","rules":[{"pkg":"app.zune.videos","state":"limit","daily_min":30}]},
 "contacts":{"rev":77,"entries":[{"id":"k_9","e164":"+1...","dir":["in","out"],"ch":{"msg":1,"video":1,"ptt":1},"sms_fwd":true}]},
 "content":{"age_band":"6-8","topics":["space"],"requests":"ask"},
 "assistant":{"on":true,"images":true,"daily_msgs":50,"transcripts":"full"},
 "camera":{"on":true,"share":"approve"},"location":{"mode":"off|on_request|continuous","visible_to_child":true},
 "sos":{"notify":["g_1","g_2"],"sms_fallback":true},"lock":{"until":null},"offline_grace_days":14}
```
- **Offline:** enforcement is local. Past `not_after` plus grace (default 14 days, matching report 12) the device drops to guardians and emergency only, never fail-open.
- **Trusted time:** each response carries signed server time. Device stores (server_time, elapsedRealtime, boot count). Effective now = max(anchor-derived time, last trusted wall clock); a rollback beyond 5 minutes is flagged to parents. Time and time zone are forced automatic (role wins `AUTO_TIME`), Settings has no date page, and the schedule uses the policy `tz`.
- **Approvals ("ask a parent"):** `approval.request{kind: time|app|contact|topic|video}` pushes to the guardian; one tap issues a TTL'd signed grant. Offline: parent PIN (Keystore-HMAC, escalating lockout) grants a time-boxed override, synced later.
- **Remote lock, find, SOS:** signed commands with nonce and expiry. SOS alerts guardians over WS and SMS fallback; it is separate from the always-available 911 call.
- **Location:** default off, opt-in per child, child-visible indicator, 30-day retention [I]; overt, never covert.

**4.5 Sync.** One WebSocket (TLS, pinned key) is a doorbell: `policy.update{section, rev}` then HTTPS `GET policy?since=rev`; commands carry their own signature so any transport can deliver them. Fallbacks: JobScheduler 15 min, alarms with Doze-allowed, reconnect on connectivity, optional SMS wake-up in Stage 2. Doze: `allow-in-power-save` and persistent process; adaptive keepalive and quiet-hour relaxation per 13; battery target is unmeasured [I]. **Recommendation: `ZuneGuardian` owns the socket**; ZuneComms, ZunePhone and the SMS vault use its Binder `ILink`. Reason: it is the one process the platform itself keeps bound and restarts (F2), and the control plane must outlive messenger bugs. Parent-side notifications: Web Push (iOS needs Home Screen install [S: https://www.pushengage.com/documentation/setting-up-web-push-notifications-for-ios-ipad/]), email, SMS for safety alerts.

**4.6 Backend and portal.**
- Go services (one codebase with 13's `comms-api`), Postgres (partitioned usage aggregates, per-day per-app rows), Redis pub/sub for socket routing (NATS later), S3-compatible storage, KMS per-family DEKs with crypto-shredding, one US region with cross-region backup (A1).
- Auth: passkeys (go-webauthn BSD-3 [P] or SimpleWebAuthn MIT [P]), email OTP fallback, TOTP for step-up. Devices: Keystore key signs challenges for short-lived tokens. Attestation verified by a small Kotlin sidecar using `android/keyattestation` and pinned to our AVB key hash; it raises an alert, it does not gate pairing (F8).
- Portal: React PWA, mobile-first, OpenAPI client, live status over SSE.
- Compliance hooks: data classes with per-class retention (messages 180 d per 13, usage 90 d, location 30 d), consent ledger, DSAR export and delete, no third-party SDKs on device, RBAC plus break-glass staff access with dual approval, AgeSignal provider from the setup age band.
- Observability: OpenTelemetry with PII scrubbing; SLOs for online policy propagation p95 under 10 s and "enforcement drift" (device-acked rev vs server rev); parent alert when a device has not checked in.

Infra cost sketch, **excluding LiveKit, AI inference, SMS, carrier and staff**; ranges are rough, about 2x either way [I]:

| Devices | Shape | Monthly | Per device |
|---|---|---|---|
| 1k | 2 small app nodes, small HA Postgres, small Redis | $250-500 | $0.25-0.50 |
| 10k | 3 nodes, mid HA Postgres, Redis | $0.9-2.2k | $0.09-0.22 |
| 100k | 4-6 nodes (100k sockets), large Postgres + replica, Redis cluster | $6-15k | $0.06-0.15 |

Logs and Postgres writes dominate. 13's "few hundred dollars" at 10k looks low once HA and observability are included.

**4.7 Tamper matrix.**

| Attack | Mitigation |
|---|---|
| Uninstall or disable Guardian | System priv-app, DO, `DISALLOW_UNINSTALL_APPS`, `setUserControlDisabledPackages`; no Settings app list |
| Change clock or time zone | Forced auto time, no UI, trusted-time floor, rollback flag |
| Settings factory reset | `DISALLOW_FACTORY_RESET`, no UI |
| Recovery wipe | PDB claim lock plus inert unpaired state; portal alert on re-pair |
| Safe mode | `DISALLOW_SAFE_BOOT`; all apps are system apps, so nothing extra runs |
| ADB or developer options | `user` build, no developer UI, `DISALLOW_DEBUGGING_FEATURES` |
| Reflash or bootloader | Locked bootloader with our AVB key, OEM unlock off; Qualcomm EDL exposure is a topic 02/15 device filter [M] |
| Network blackhole, crash | Local enforcement; grace then minimal mode; role rebind |
| Second SIM or SIM swap | Call and SMS controls are on-device only; carrier-side lock is Stage 2 (12) |
| Link-outs from WebView | Topic 04 |

**4.8 Reconciliation.** 12: adopt `ZunePolicyService`, 14-day grace and "never fail open"; 04 wants Guardian "started every boot" (met by persistent plus role) and time limits via `PackageUsagePolicy` (do not: F3, implement via suspend); 13: adopt contact graph, WS envelope, 180-day retention, Go; change socket owner and N devices per child; 03 Q5 is answered (role + DO; keep ManagedProvisioning out, since system code sets DO directly [I]).

## 5. Risks & unknowns
- GOS trees are not the pristine tag. Re-verify every cited file on `android-17.0.0_r1` once AOSP is reachable (conversation 2) [P gap].
- Role grants may not cover all restrictions (private DNS, VPN, OEM unlock, wipe); unmapped. DO fallback or system-asserted set (04) fills gaps. Cuttlefish validation needed.
- Platform supervision API is flagged and moving; hidden behind `EnforcementBackend`, CI on each rebase.
- DO UX strings ("managed by your organization") and `setDeviceOwner` timing in ZuneSetup are untested.
- RKP: attestation refresh needs a configured server host (Google or proxy); unknown for D13 Snapdragon devices.
- Persistent socket battery and carrier NAT timeouts unmeasured.
- Server holds children's data (location, SMS, transcripts); a breach is existential. Staffing for on-call, SOS and T&S is a dependency.
- Location, AB 1043, COPPA retention, UK/EU not launch-ready; counsel.
- Cost ranges are estimates, not quotes.

## 6. Decisions needed from the founder
1. Approve DO plus role (one-way door at provisioning).
2. Resale policy: hard claim lock with support override (recommended) vs soft.
3. Location sharing in Stage 1 (default off, opt-in) or defer.
4. Child-visible transparency: child sees what parents see (recommended).
5. Caregiver roles (grandparents) in Stage 1 or Stage 2.
6. Offline grace default (14 days) and minimal-mode behavior.
7. Who runs 24/7 SOS alert handling and safety reports.
8. Claim card in the box vs portal-code only.

## 7. Load-bearing claims
1. AOSP has supervision service, role, bound app service and empty config hooks; consumer features are Google's. [P] AOSP16 raw paths; GOS-fwb `config.xml:6281-6289`.
2. `SYSTEM_SUPERVISION` role grants `SUSPEND_APPS` and `MANAGE_DEVICE_POLICY_{LOCK_TASK, TIME, SAFE_BOOT, FACTORY_RESET...}`, systemOnly, flags enabled. [P] GOS-perm `roles.xml:1394-1459`; GOS-brel `aconfig`.
3. Platform `TIME_LIMIT` is unfinished, so we own the engine. [P] `SupervisionService.java:503`.
4. Role wins `AUTO_TIME`, which defeats clock tampering. [P] `PolicyDefinitionFactory.java`.
5. Supervision can be enabled without a dialog before setup completes; DO can be set by a permissioned app. [P] `EnableSupervisionActivity.kt`; `DevicePolicyManagerService.java:10643`.
6. PDB survives non-Settings resets and is gated by `config_persistentDataPackageName`. [P] `PersistentDataBlockService.java`.
7. AMAPI/Family Link need Google services. [S] search summaries.
8. Android 16-launch devices support only RKP; rkpd host comes from a system property. [P] developer.android.com; GOS-rkp `Settings.java:253`.
9. No-GMS MDMs use own MQTT plus long-polling; Doze allowlist honored from sysconfig. [P] HMDM; `SystemConfig.java:978`.
10. Headwind is Apache-2.0 but its kids shell is paid. [P] HMDM LICENSE, server README.
