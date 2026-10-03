# No-browser / no-YouTube enforcement and the ZuneGuardian (Device Owner + supervision role)

## Purpose and scope

Specifies the layer that makes "no browser app, no way to type a URL, no route to youtube.com" true and gives the parent full control of allowing or disabling anything (D24): ZuneGuardian (`app.zune.guardian`) as Device Owner and supervision-role holder, with signed policy, parent PIN, reset and recovery, the bypass-vector suite and the 112-only path (D28).

**Stage 1** = every MUST, proven on Cuttlefish and both Pixels by Z3 exit and complete before the staff pilot. **Stage 2** = lockdown VPN (R04 "Zune Guard"), Chromium allowlist patch, per-UID firewall chains, attempted-link sink, Advanced Protection hooks, platform Supervision PIN, hard attestation gating.

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
| D30 (superseded by D33), D14 | Captive portals open in ZunePortalViewer (02 OS-20), with a bounded DNS window (LOCK-24). Never set `DISALLOW_CONFIG_WIFI`, `_MOBILE_NETWORKS`, `_BLUETOOTH` [R16 F3, 02 OS-14]; parent "network off" is forced airplane mode. |
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
- **LOCK-10 MUST** Commands (`lock`, `ring`, `pin_reset`, `kill`, `unenroll`, `service_unlock`, `policy_refresh`, `factory_qa`) carry `cmd_id`, `nonce`, `exp` and obey LOCK-07 signing; replay or expiry is rejected and logged.
- **LOCK-11 MUST** Schedules and budgets use `effective_now` (§4.5); unexplained wall-clock jumps of 5 minutes or more are ignored and reported. Auto time and zone are forced; zone comes from policy `tz` (default `Asia/Kolkata`).
- **LOCK-12 MUST** Time controls: daily budgets per app and total; bedtime by lock-task with Emergency reachable; "ask a parent" request; no extension without a signed grant or PIN. Exemptions (09 APP-24): `app.zune.clock` is never suspended by a budget, its alarm activity is in the lock-task allowlist, and alarm volume is not capped by `vol_max`.
- **LOCK-13 MUST** Every capability is an entry in `capabilities.json` with its mechanism (§4.3), seeded with the union of the capabilities and policy sections that 06 to 09 request (§4.4 table); unknown capabilities in a bundle are rejected; absent ones default off, except `emergency`, `parent_area`, `setup`, `settings_wifi`. Apps call `PolicyClient.check(capability, subject)` before send, connect or play; the server enforces again; Zune calls never rely on `DISALLOW_OUTGOING_CALLS`.

**Parent PIN**
- **LOCK-14 MUST** PIN: 6 or more digits, set on the device at pairing, never transmitted; verifier = HMAC-SHA256 under a non-exportable Keystore key (StrongBox if present) with a 16-byte salt; 5 attempts, then 30 s lockout doubling to 24 h, surviving reboot; `FLAG_SECURE`; trivial PINs refused.
- **LOCK-15 MUST** Forgotten PIN: signed `pin_reset` plus a one-time 8-digit code shown only in the authenticated portal after step-up; a new PIN is accepted only if the code is entered within 10 minutes; a child cannot start the flow.
- **LOCK-16 MUST** `ParentGate.confirm(reason)` is the only gate; sessions last at most 5 minutes, are scoped and end at screen-off; offline overrides are capped by `override_max_min` (default 60 per day), logged and uploaded.

**Reset and recovery**
- **LOCK-17 MUST** The only in-device reset is Parent area, `ParentGate.confirm`, then Guardian wipe, working while Guardian is sole setter of `DISALLOW_FACTORY_RESET` (VG-3).
- **LOCK-18 MUST** After any wipe the device boots to unpaired ZuneSetup: only Wi-Fi and mobile-data setup, pairing and Emergency are reachable. Setup completes only with a code from a guardian of the family bound to this serial and attestation key (server-checked, 05). The portal shows "device was reset" within 60 s of reconnect.
- **LOCK-19 SHOULD** A claim blob (family hash) in the persistent data block survives recovery wipes; only signed `unenroll` or `service_unlock` clears it (VG-4).
- **LOCK-20 MUST** OEM unlock stays off. `service_unlock` needs two signatures: parent step-up in the portal and the company `zune-service-ca` key (04). Guardian then clears its own `DISALLOW_FACTORY_RESET`, permits OEM unlock, logs it and reverts after 72 h (default [INFERRED]). The only standing exception is the C0 staff phones left with OEM unlocking on (10 OPS-17), flagged `oem_unlock_exception` in the posture report.

**Bypass controls (image and policy)**
- **LOCK-21 MUST** No `VIEW` + `http`/`https`/`ftp` handler, `WEB_SEARCH` handler, `CustomTabsService` or `CATEGORY_APP_BROWSER` handler exists in any partition (extends 02 OS-07).
- **LOCK-22 MUST** P-FWK-2: IntentFirewall also reads `/system_ext/etc/ifw` and blocks activity starts with scheme http, https, ftp or action `WEB_SEARCH` from any sender, logging each; `/data/system/ifw` cannot loosen it.
- **LOCK-23 MUST** Only Reader and Videos create a WebView (02 OS-27); Reader has no `INTERNET`; `INTERNET` holders equal `vendor/zune/allowlist/internet-holders.txt` (02 OS-05); a no-`INTERNET` app cannot reach the network by socket, `DownloadManager`, `MediaPlayer` or intent (kernel eBPF check [R04 F6]).
- **LOCK-24 MUST** Strict Private DNS to the Zune resolver (05) through `setGlobalPrivateDnsModeSpecifiedHost` plus `DISALLOW_CONFIG_PRIVATE_DNS` (placeholder resolver allowed until Z4); captive-portal detection stays on against the Zune probe (05 BE-42) so a sign-in network is recognised, the only sign-in UI is ZunePortalViewer (D33; 02 OS-20). Because strict Private DNS can make a captive network look offline (VG-8), when Android reports a captive portal Guardian may switch Private DNS to opportunistic for at most 10 minutes, restore strict mode when the network validates or the timer ends, and record both changes in `posture`; the viewer's host denylist is the control during that window. Guardian re-asserts `captive_portal_mode` at its default.
- **LOCK-25 MUST** `user` build, `ro.adb.secure=1`, `adb_enabled=0`, `development_settings_enabled=0`, `DISALLOW_DEBUGGING_FEATURES`, `persist.adb.tradeinmode` unset, no RadioInfo or `*#*#` handler; `DISALLOW_SAFE_BOOT`, and a safe-mode boot still runs Guardian with every restriction.
- **LOCK-26 MUST** USB file transfer, physical media, Bluetooth sharing and NFC are off; no USB gadget function except charging (no MTP, PTP, ACM, DIAG, ADB); USB host stays for USB-C audio (02).
- **LOCK-27 MUST** Tethering, VPN, credentials, accounts, user and profile creation, install, unknown sources, uninstall and app control are restricted; `fw.max_users=1`; no `VpnService` package ships.
- **LOCK-28 MUST** Nothing leaves Zune by share sheet or keyboard: Zune apps never call `createChooser`, `ACTION_SEND` handlers equal an allowlist, every `CATEGORY_APP_*` shortcut resolves to nothing or a Zune app.
- **LOCK-29 MUST** Zune notifications carry no URL; the lock screen offers only Emergency, flashlight and camera, plus one exception: the Guardian-launched incoming-call screen (`app.zune.calls`, Accept and Decline only, 06 §4.7) shows over the keyguard while a call invite is live; Walkie never does (06 COM-26); the cell-broadcast dialog does not linkify, or its links are dead through LOCK-22.
- **LOCK-30 MUST** Camera has no barcode feature; ZuneSetup's QR parser accepts only `ZUNE1:<code>` (pairing) and, only while the device has no claim blob, `ZUNE1S:<token>` (factory QA, LOCK-38); no `PROCESS_TEXT` web handler exists; Assistant renders plain text with no linkify or tap-to-open (server rules: 07).
- **LOCK-31 MUST** Videos Tier 2 is off by default, gated by `kill` and `webview_min_version` (02 OS-29); new-window and external navigation are denied (08).

**Telephony and emergency**
- **LOCK-32 MUST** Only Guardian holds `CALL_PHONE` and `CALL_PRIVILEGED` (CI allowlist); no package holds `READ_SMS`, `RECEIVE_SMS` or `SEND_SMS`, and no SMS role holder or receiver exists (D19: no SMS code on the device); `DISALLOW_OUTGOING_CALLS` and `DISALLOW_SMS` are set.
- **LOCK-33 MUST** Inbound non-emergency cellular calls are rejected within 1 s with no ring or UI and a logged event; callback relaxation uses AOSP's own flags only, with a parent alert; inbound SMS show nothing.
- **LOCK-34 MUST** Guardian ships the Emergency screen, a minimal `InCallService` and the dialer role. It owns `ACTION_DIAL_EMERGENCY` (`config_emergency_dialer_package`), is reachable from the lock screen and power menu, has one button dialling the literal `112` (no keypad or text field) and shows "cannot call 112 here" when service state forbids it.
- **LOCK-35 MUST** Three quick power presses open SOS (screen off or locked) with a 5-second cancel countdown; at zero Guardian sends an `sos` event (queued if offline) and, if `sos.dials_112` (default 1), dials 112; minimum interval 30 s.
- **LOCK-36 MUST** Record a 112 field test in `zune/docs/lab/112-field-test.md`: Jio, Airtel, Vi, BSNL; voice SIM, data SIM, no SIM; locked screen; Wi-Fi only.
- **LOCK-37 MUST** Product copy says only "no browser app and no way to type a web address; the device talks only to Zune-approved services; emergency calling is not guaranteed", never "no internet", "unbypassable", "100% safe" or "no YouTube content" (Tier 2 plays YouTube inside Videos).
- **LOCK-38 MUST** Guardian has a FACTORY state for the station (10 OPS-14, §4.5 there): entered only from a single-use `factory_qa` token (a command of type `factory_qa` signed under LOCK-10 and BE-13, TTL 30 minutes, bound to the device's `serial_hmac`) scanned as `ZUNE1S:<token>`, and only while no claim blob exists and the server shows no claimed device for the serial; it runs the in-process audits and signed report of 10 §4.5 (no adb, no shell), is left by sealing, expiry or reboot, and can never be re-entered after a claim or a wipe (10 VO-6; LT-19).

## Design and build instructions

### 4.1 Components and paths

```
zune/apps/guardian/          Gradle-built, imported by Soong with the platform cert (09 Mode G), /system_ext/priv-app: provision policy enforce time pin channel emergency reset factory
zune/libs/core/              schema/policy-v1.schema.json, schema/capabilities.json, PolicyClient, ParentGate, IZunePolicy.aidl, IZuneLink.aidl
zune/os/vendor/zune/         ifw/zune-ifw.xml  sysconfig/privapp-permissions-zune.xml  allowlist/*.txt  sepolicy/
zune/os/tools/bypass_suite/  lt01..lt19 (12 runs them)
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
Policy keys requested by other sections (all optional, absent means off or default; 05 generates server types, `capabilities.json` is seeded from this list):

| Key | Requested by | Content |
|---|---|---|
| `child{name,av}`, `home{v,tiles[]}`, `caps{diag,camera,photos,journal,notebook,clock,calculator,recorder,share,reader,weather,assistant,walkie}` | 09 §4.2 | Home layout and per-app capabilities |
| `assistant{on,mode,images,thumbnails,voice,cloud_voice,turns_day,session_min}`, `kill.features` += `assistant`, `assistant_images`, `assistant_voice` | 07 §4.2 | AI controls |
| `content{allow,deny,mobileOk}`, `kill.features` += `videos_tier2`, caps `weather`, `reader` | 08 §4.10 | Content and Tier 2 |
| `vis{notice_v}`, `places`, `cohort` (`lab|staff|external`), per-channel schedules in `contacts.entries` (`win`) | 05 §4.5, 06 §4.2 | Notice version, places, OTA cohort, schedules |
| `min.webview`, `grace`, `sos`, `kill`, `net`, `device` | this section | as in the example |
| `device.data_warn_mb`, `device.airplane_lock`, `emergency.card{child_name,guardians}` | 02 §6 | Values ZuneSettings shows: data warning, airplane lock, the Emergency info card |
| Name map | 06, 09 | contact-channel ids `msg`, `voice`, `video`, `ptt` (06) correspond to capabilities `messenger`, `voice`, `video`, `walkie` (09); a channel needs both the edge grant and the capability |

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
| E8 Re-entering the factory-QA state after claim or wipe | 38 | LT-19 |

## Acceptance criteria and tests

Tests are `LT-nn` (02 owns `AT-nn`). On `user` builds adb is off: read the LOCK-06 posture report and observe behaviour; shell checks run on userdebug Cuttlefish and dev Pixels.

- **LT-01** `dumpsys device_policy`, role holders and `dumpsys user` show Guardian as sole owner, role holder and restriction source; the set equals `restrictions.json`; one user.
- **LT-02** `am start -a android.intent.action.VIEW -d` with `https://`, `http://`, `ftp://`, `intent:` and `WEB_SEARCH` fail with an IFW log line, also with a permissive file in `/data/system/ifw`; scan and `query-activities` find no browser, Custom Tabs or `CATEGORY_APP_BROWSER` handler.
- **LT-03** Only Reader and Videos create a WebView (02 AT-07); a no-`INTERNET` test APK (userdebug) fails socket, `DownloadManager`, `MediaPlayer`, WebView and `ACTION_VIEW`; holders equal the allowlist.
- **LT-04** `private_dns_mode=hostname`; a non-allowlisted name does not resolve with Wi-Fi DNS set to a public server; a fake captive network opens ZunePortalViewer automatically, which has no URL entry, cannot load a denied host, closes when the network validates, and strict Private DNS is back within 10 minutes (02 AT-04).
- **LT-05** `ro.debuggable=0`, `ro.adb.secure=1`, no developer options; `fastboot flashing get_unlock_ability` returns 0 and unlock is refused; safe-mode boot keeps Guardian and every restriction.
- **LT-06** `lsusb -v` shows no MTP, PTP, ACM, DIAG or ADB interface; Bluetooth OPP send is refused; no NFC feature.
- **LT-07** Tether, VPN, user creation, install and uninstall attempts fail; no `VpnService` package.
- **LT-08** With USB and Bluetooth keyboards, Meta+B/E/P/S/C/L/M/U and Alt+Space open nothing outside Zune; `ACTION_SEND` resolves only to the allowlist.
- **LT-09** A URL in a Messenger text is untappable; a cell-broadcast test URL is dead; the lock screen shows only Emergency, flashlight, camera and, during a live call invite, the Accept and Decline call screen (LOCK-29); Assistant prompts "open example.com" and "give me a link" yield no tappable link.
- **LT-10** Bad signature, wrong device, old `rev`, expired signer and future `iat` are rejected and the last good policy stays; no bundle gives the fail-closed profile; `grace.offline_days`, `not_after` (userdebug time hook) or `kill.level=2` start MINIMAL mode and a fresh bundle ends it; a killed Guardian restarts per LOCK-04 while apps deny.
- **LT-11** Setting the wall clock back or forward does not move bedtime or budgets; a drift event is reported.
- **LT-12** Five wrong PINs lock out across reboot; the reset-code flow works and a child cannot start it; PIN screens are black in screenshots.
- **LT-13** Recovery wipe gives unpaired ZuneSetup with nothing else launchable; another family's code is refused; the portal shows "device was reset"; the PIN-gated reset works.
- **LT-14** `service_unlock` with one signature is rejected; with two it opens the window and reverts on timeout.
- **LT-15** Pixel with a staff SIM: 112 connects (test mode or agreed live call); no other number can be dialled; an inbound call is rejected within 1 s without ringing; inbound SMS shows nothing; a Bluetooth HFP dial is refused.
- **LT-16** Triple power press from screen-off and locked states opens SOS; Cancel stops it; the countdown delivers a guardian alert within 10 s on Wi-Fi; a second trigger within 30 s is ignored.
- **LT-17** A posture report arrives after boot with the expected hash; flipping a restriction on a dev build raises drift.
- **LT-18** Videos Tier 2 is off by default; `kill` or a `min.webview` above the installed version disables it within 10 s; new windows are denied.
- **LT-19** The FACTORY state accepts a valid single-use token only on an unclaimed, never-claimed device: a replayed, expired, wrong-serial or post-claim token, a post-wipe token on a claimed serial, and an intent, boot reason or USB route to FACTORY all fail; sealing consumes the token (10 AT-O04, VO-6).

## Verify first

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VG-1 | A privileged platform-signed app can set Device Owner before setup completes [R05 F5] | GrapheneOS tree; route inferred | Read `DevicePolicyManagerService`; Cuttlefish spike, Z3 week 1 | ManagedProvisioning trusted-source route (02 keeps it); else a registered DPMS patch |
| VG-2 | Supervision framework, role names, empty `config_*` hooks, flags, overlayability, role wins `AUTO_TIME`; every §4.3 constant exists; supervision need not be enabled, so no platform PIN user [R05 F1-F4, R16 F9] | GrapheneOS and `build_release` only | Read `frameworks/base`, `roles.xml`, `build/release`; compile Guardian; `cmd role` | D24 falls back to Device Owner plus privapp permissions; force time via DPM; tell 02 |
| VG-3 | A Device Owner that solely sets `DISALLOW_FACTORY_RESET` can still `wipeData` [R16 F9] | Source reading only | Spike, Z3 week 1 | Clear own restriction first; else `RecoverySystem` wipe |
| VG-4 | `config_persistentDataPackageName` lets Guardian write the persistent data block, which survives recovery wipes [R05 F6] | Untested | Write, recovery-wipe, read on both Pixels | Drop LOCK-19; rely on server-side serial and attestation binding |
| VG-5 | `OemLockManager` access, `DISALLOW_FACTORY_RESET` clearing the OEM-unlock bit, `get_unlock_ability` on 10a and 9a [R04 F7] | Pixel behaviour unmeasured | Read `OemLockService`; sacrificial Pixel | Service-unlock becomes signed recovery sideload only (04) |
| VG-6 | IntentFirewall syntax and the 30-line `/system_ext/etc/ifw` patch cover WebView `intent:` launches; shortcut and share routes close with no handler [R04 F5] | Mirror only; shortcuts from memory | Read `IntentFirewall.java`; LT-02, LT-08 | CI "no handler" gate plus WebView gate; add IFW rules |
| VG-7 | `DISALLOW_INSTALL_APPS` does not block ZuneUpdater or Guardian installs of signed updates [R04 risks] | Unverified in R04 | Install a signed update with restrictions set | Guardian installs as owner, or OTA only (breaks 02 OS-28 SLA) |
| VG-8 | Strict Private DNS via DPM, `captive_portal_mode` values, port 853 blocked networks look offline [R04 F4, F6] | Secondary sources | LT-04 on a Pixel and on a 853-blocked network | Per-UID `INTERNET` stays the base control; document the limit; if the viewer cannot open under strict DNS, widen the LOCK-24 window design |
| VG-9 | `DISALLOW_OUTGOING_CALLS` spares 112; Guardian can reject inbound calls; telephony fixes (CVE-2026-28615, commits 21585d3, 586e92c) are in the tag [R12] | Fixes landed after the June build | Read `Telecomm`; LT-15; compare tag with commits | Patch P-TEL-1 (deny-all in `GsmCdmaPhone.dial`, `SmsController`, Telecom), re-signing `com.android.telephonycore`; 02 fork decision |
| VG-10 | Guardian can hold the dialer role and own `ACTION_DIAL_EMERGENCY`; AOSP Dialer is unneeded [R12 §2.3] | 02 V7 open | Cuttlefish modem simulator; Pixel | Keep AOSP in-call UI with launcher activities disabled (02) |
| VG-11 | Power-key multi-press can be re-pointed to Guardian; India's panic-button rule requires three presses; 112 connects on SIM-less, voice-SIM and data-SIM devices [R19, R20] | Rule text unread; untested | Read `PhoneWindowManager`; LOCK-36 field test; counsel | Add P-FWK-3; show "unavailable" and disclose; escalate before pilot |

## Risks, open gates and out of scope

- **Single point of control.** A Guardian bug defeats every control; an `EnforcementBackend` interface isolates DPM calls from the flagged supervision APIs; CI runs LT-01..19 on each rebase.
- **What we cannot stop (disclose).** Recovery wipe (yields an inert device), parent-assisted unlock, a SIM moved to another phone, a friend bridging a stranger into a call, other devices in the home, web-derived AI answers and the Videos embed (R04 residual: medium).
- **Private DNS dependency:** if the resolver or port 853 is unreachable the device looks offline (VG-8).
- **[GATE: before build]** VG-1 and VG-2 results recorded; if both fail, the founder re-decides D24.
- **[GATE: before staff pilot]** Zero P0 bypass failures; LT-13 and LT-14 pass or an SP-6 exception is recorded; real Private DNS resolver; 112 field test and SOS shipped (SP-4).
- **[GATE: before external family]** Counsel reviews SOS, location use (DPDP s.9(3)), parent reading of messages (D27) and claim copy; an independent bypass test on a re-locked Pixel; T&S on-call for SOS alerts (EXT-3).
- **[GATE: before charging]** Marketing and contract wording match LOCK-37 and are counsel-approved.

Out of scope: call allowlists, SMS vault, carrier lines; platform Supervision PIN; lockdown VPN; Chromium fork; hard attestation; caregiver roles (05); Indic UI (D20); non-Pixel devices.
