# 16 - Minimal Settings: what stays, what goes, who can change it

Status date: 2026-10-02. Tags: **[P]** read in real source this session; **[S]** reputable secondary; **[I]** my inference; **[M]** memory, unchecked. Classes: **KC** child can change, **KR** shown read-only, **PG** parent-gated, **HID** hidden/removed, **FRC** forced by system.

**AOSP access: blocked.** `git ls-remote android.googlesource.com` failed (CONNECT 403) and `source.android.com` returned 403, so nothing below is checked against Google's `android-17.0.0_r1`. Source is GrapheneOS `17` branches (AOSP 17 plus their patches; their additions such as memtag, exploit protection and duress PIN are excluded): Settings @e5c0d9d (2026-09-22), frameworks/base @cf9df017 (2026-10-01), build_release @55fde9c, SetupWizard2 @3982cfc, external/talkback @e1a1a93, all `github.com/GrapheneOS/platform_*`; plus github.com/google/talkback @229212f.

## 1. Summary & recommendation

Do not rewrite Settings and do not slim-fork it. Wi-Fi and mobile data "as it is" (D14) means AOSP's own Wi-Fi/telephony UI, the hardest code in Settings; and stock Settings cannot be removed (prevent-disable per report 03, hard-referenced by the framework, F4). Recommend **Option D+, "front door and engine room"**:

1. **ZuneSettings** (new, Compose, platform-signed system app) is the only Settings UI a child sees: about 11 rows. It builds small native pages for Sound, Display, Accessibility-lite, Language, Battery, Storage, Emergency and About/Legal, and **deep-links to stock AOSP screens only for Wi-Fi, mobile data/SIM and Bluetooth**.
2. Stock `com.android.settings` stays installed as the **engine room**, default-deny: about 40 of its 437 manifest activity entries stay enabled, the rest are switched off by a generated `component-override` sysconfig (a mechanism that exists in system_server), plus `config_*` overlay knobs and user restrictions. `SettingsIntelligence` is dropped, which removes Settings search.
3. SystemUI is trimmed by overlay (6 QS tiles, 3-item power menu, trimmed lock-screen shortcuts), and a catch-all intent router inside ZuneSettings stops "activity not found" crashes.
4. The **parent gate** is the single parent PIN of report 05 (ZuneGuardian-owned, Keystore HMAC, escalating lockout, reset from the portal) behind a `ParentGate` interface. Android 17's platform Supervision PIN (a credential on a parentless supervising profile) fits technically (F9) but adds a profile user and flag-dependent code; keep it as a Stage-2 hardware-throttled upgrade.
5. **Stage 1 has zero Java patches to Settings**; Stage 2 adds a gate patch of at most 150 lines. Effort: about 8-9 engineer-weeks; each Q2/Q4 rebase about 2-4 days [I].

## 2. Findings

**F1. Stock Settings is large and growing.** 437 manifest activity entries (410 activities, 27 aliases), 337 explicitly exported; 379 `res/xml` files; ~250 `ENTRY_FRAGMENTS`; **233 Catalyst screens** (`@ProvidePreferenceScreen`) and 31 SPA pages built in code, which XML overlays cannot edit; 134 bool resources in `res/values/config.xml` [P: Settings `AndroidManifest.xml`, `core/gateway/SettingsGateway.java`, grep]. The top level has about 23 rows, from Network and Connected devices to Safety Center, Supervision, Emergency and Support [P: `res/xml/top_level_settings.xml`].

**F2. What can hide things, and the limits.**
- Overlay knobs work for both XML and Catalyst code paths: `config_show_wifi_hotspot_settings`, `config_show_private_dns_settings`, `config_show_vpn_options`, `config_show_reset_dashboard`, `config_show_system_update_settings`, `config_show_wifi_settings` (Wi-Fi preferences page), `config_show_top_level_*` [P: consumed in `WifiUtils`, `PrivateDnsPreferenceController`, `ResetDashboardScreen.kt`, `ConfigureWifiScreen.kt`].
- **sysconfig `<component-override package=..><component class=.. enabled="false"/>`** is parsed by `SystemConfig` and applied at scan to activities, receivers, providers and services [P: GOS-fwb `services/core/java/com/android/server/SystemConfig.java:1018,2438`, `pm/ScanPackageUtils.java:849`]. Settings itself hides screens by disabling components (`Utils.disableComponentsToHideSettings`) and re-enables a few at runtime (`SettingsInitialize.webviewSettingSetup`, dev tiles), so the override is a default, not a lock [P].
- `SubSettings.isValidFragment()` returns true unconditionally, while exported entry activities validate against `ENTRY_FRAGMENTS` (invalid fragments throw) [P]. In-screen navigation cannot be default-denied without a patch.
- Carrier config can retune mobile rows without restrictions: `KEY_EDITABLE_ENHANCED_4G_LTE_BOOL`, `KEY_HIDE_PREFERRED_NETWORK_TYPE_BOOL`, `KEY_ALLOW_ADDING_APNS_BOOL`, `KEY_HIDE_SIM_LOCK_SETTINGS_BOOL`, `KEY_EDITABLE_WFC_MODE_BOOL` [P: `CarrierConfigManager.java`].

**F3. Two user restrictions are traps.** `NetworkProviderSettings` and `MobileNetworkSettings` call `super(DISALLOW_CONFIG_WIFI)` / `super(DISALLOW_CONFIG_MOBILE_NETWORKS)` [P: `NetworkProviderSettings.java:395`, `MobileNetworkSettings.java:129`], which makes the whole page a restricted page [I: restricted-page behaviour]. The data toggle lives on that page, so setting either restriction contradicts D14. `UserManager` offers 83 `DISALLOW_*` constants [P]; `UserManagerService.setUserRestriction` needs only `MANAGE_USERS` (base restrictions, no Device Owner) [P: `UserManagerService.java:4070`].

**F4. The framework hard-references Settings.** `config_dataUsageSummaryComponent` = `Settings$DataUsageSummaryActivity` (data-warning notifications), `config_wifi_tether_enable`, `NotificationAccessConfirmationActivity`, `NetworkChangeNotification`, `config_appsAuthorizedForSharedAccounts` [P: `core/res/res/values/config.xml:477,3794,5004,7246`, `config_telephony.xml:602`]. SystemUI sends about 60 distinct `Settings.ACTION_*` intents plus hard-coded class names (`WifiDialogActivity`, `StorageWizardInit`, `HelpTrampoline`) [P: grep of `packages/SystemUI/src`]. A rewrite would have to implement all of them.

**F5. Wi-Fi and data UI is split between SystemUI and Settings.** Panel `ACTION_INTERNET_CONNECTIVITY` only broadcasts to SystemUI's Internet dialog; the NFC/Wi-Fi/Volume panels redirect to full pages under `slices_retirement` [P: `panel/PanelFeatureProviderImpl.java:46-85`]. The Internet dialog calls `NETWORK_PROVIDER_SETTINGS`, Wi-Fi details, `NETWORK_OPERATOR_SETTINGS`, the Wi-Fi password dialog and DPP/QR [P: `InternetDetailsContentController.java:458-471,954-965,1274,1694`]. Stock "Network & internet" (`network_provider_internet.xml`) holds Internet, SIMs, airplane, hotspot, Data Saver, VPN, Private DNS; its "Internet" page (`NetworkProviderSettings`) holds the Wi-Fi list, Add network, Saved networks, Wi-Fi preferences (wakeup, open-network alerts, WEP, install certificates, Wi-Fi Direct) and a mobile row. The per-SIM page has about 45 rows (data, roaming, usage, billing, VoLTE, preferred network, APN, operator selection, 2G, eSIM convert/transfer/erase) [P: `mobile_network_settings.xml`].

**F6. SystemUI defaults.** `quick_settings_tiles_default` = `internet,bt,dnd,cast,flashlight,airplane,rotation,wallet,alarm,controls,screenrecord,battery`; `quick_settings_tiles_stock` (the edit pool) has 36 tiles; `config_globalActionsList` = `emergency,lockdown,power,restart,logout,screenshot,bugreport`; lock-screen shortcuts `bottom_start:home`, `bottom_end:wallet`; `config_enableSafetyCenter` = true [P].

**F7. Search disappears without SettingsIntelligence.** `initSearchToolbar` and `SearchMenuController` hide search unless `config_settingsintelligence_package_name` is installed and enabled; `SearchResultTrampoline` verifies the caller [P: `search/SearchFeatureProvider.java:91`, `search/actionbar/SearchMenuController.java:74`]. Report 03 lists SettingsIntelligence as a hard keep; it is not.

**F8. Legal and help.** `SettingsLicenseActivity` and `ManualDisplayActivity` hard-code `setPackage("com.android.htmlviewer")` [P: `SettingsLicenseActivity.java:98-110`, `ManualDisplayActivity.java:54-59`], which reports 03/04 remove, so licences break unless we ship our own viewer (licence text is a legal duty [I]). Help is inert: `help_url_*` are empty, `HelpTrampoline` catches `ActivityNotFoundException`, and only four strings embed http links, all in screens we disable (SD card, 16K pages) [P].

**F9. Supervision in 17.0 (release `cp2a`).** Settings screen, manager APIs, PIN-recovery screen, role, app service, DPM sync, policy APIs and parent approval for PIN setup are ENABLED (via `bp4a`/`cp2a`; `cp2a` inherits `cp1a`, which inherits `bp4a`); **`enable_supervision_package_usage_apis` (time-limit policies) is ENABLED only in `trunk_staging`** [P: build_release `aconfig/*/android.app.supervision.flags`, `release_configs/cp2a.textproto`]. Setup creates a parentless `profile.supervising` user (max 1), sets its lock credential, then `setSupervisionEnabled(true)` [P: `SetupSupervisionActivity.kt:268`, `UserTypeFactory.java:366`]. `ACTION_ENABLE_SUPERVISION` skips its confirmation dialog **before `USER_SETUP_COMPLETE`** [P: `EnableSupervisionActivity.kt`]. PIN recovery calls the `ROLE_SYSTEM_SUPERVISION` holder's activities (`SET/VERIFY_PIN_RECOVERY`); role holders can add approval activities via `ACTION_CONFIRM_SUPERVISION_APPROVAL` [P: `SupervisionIntentProvider.kt`, `SupervisionPinRecoveryActivity.kt`, `SupervisionService.java:414`]. **The system applies `DISALLOW_FACTORY_RESET` only when no supervision role holder exists**, so ZuneGuard must assert it [P: `SupervisionService.java:1040-1052`]. `SupervisionRestrictionBypassActivity` clears a supervision-owned restriction after a PIN prompt, permanently [P]. Google's consumer feature uses a parent PIN, a recovery account, and factory reset if none is set [S: search summaries; support.google.com blocked].

**F10. Accessibility.** TalkBack and a TTS engine are absent from the AOSP 16 and LineageOS 24 manifests; GrapheneOS adds `external/talkback` as a **prebuilt APK** and `SpeechServices` as a prebuilt (repo licence MIT) [P: manifests, repo contents]. google/talkback is Apache-2.0 and builds an APK with `build.sh` [P]. The stock accessibility page also has "Downloaded apps", "Disability support" and TTS rows [P].

**F11. Setup precedent.** GrapheneOS's non-Google SetupWizard2 launches stock `android.settings.SETUP_INTERNET` (with skip text, enable-next-on-connect extras), `ACCESSIBILITY_SETTINGS_FOR_SUW` and `LocalePicker` [P: `WifiActions.kt`, `WelcomeActions.kt`], so Wi-Fi at first run can reuse stock Settings.

## 3. Decision table

| # | Item | Class | How enforced |
|---|---|---|---|
| 1 | Wi-Fi: toggle, scan, join with password, QR (DPP), saved networks, forget, network details | KC | Stock `NetworkProviderSettings`, `WifiDialogActivity`, DPP; **never** `DISALLOW_CONFIG_WIFI` |
| 2 | Add hidden network (SSID, security, password) | KC | Stock "Add network" |
| 3 | Wi-Fi advanced fields (proxy, static IP/DNS, MAC privacy, metered) | KC residual in S1, PG in S2 | No config knob exists; S2 layout overlay or gate patch |
| 4 | Wi-Fi preferences (wakeup, open-network alerts, WEP, install certificates, Wi-Fi Direct) | HID | `config_show_wifi_settings=false`, `DISALLOW_WIFI_DIRECT`, `DISALLOW_CONFIG_CREDENTIALS` |
| 5 | Captive-portal sign-in | HID | Unsupported v1 (report 04) |
| 6 | Mobile data toggle, data usage and warning view, Data Saver, network type, airplane | KC | Stock `MobileNetworkActivity`, `DataUsageSummaryActivity` |
| 7 | Data roaming | KC, default off | Parent can lock: `DISALLOW_DATA_ROAMING` |
| 8 | Data warning/limit editing, billing cycle | PG | Portal sets via `NetworkPolicyManager`; `BillingCycleActivity` off (crash-test) |
| 9 | APN, manual operator, SIM PIN, eSIM add/erase/transfer, SIM on/off | PG (S1: setup only) | Carrier config (F2); eSIM via ZuneSetup |
| 10 | VoLTE toggle, Wi-Fi calling, forwarding/barring, voicemail, calls/SMS defaults | FRC/HID | Carrier config; no entry (report 12) |
| 11 | Hotspot/tethering, VPN, Private DNS, proxy, network reset, adaptive connectivity, satellite | HID/FRC | `DISALLOW_CONFIG_TETHERING`, `WIFI_TETHERING`, `CONFIG_VPN`, `CONFIG_PRIVATE_DNS`, `NETWORK_RESET`; knobs; Guard pins strict Private DNS |
| 12 | Bluetooth: toggle, pair, connect, forget | KC | Stock `BluetoothSettingsActivity`, pairing dialogs |
| 13 | BT sharing, LE-audio sharing, Fast Pair, NFC, Cast, UWB, Thread, printing, USB modes | HID | `DISALLOW_BLUETOOTH_SHARING/NFC/ULTRA_WIDEBAND/THREAD/PRINTING/USB_FILE_TRANSFER`, feature masks |
| 14 | Brightness, auto-brightness, text size, dark theme, auto-rotate | KC | Native page |
| 15 | Screen timeout | KC up to parent cap | Native; Guard observes the key |
| 16 | Lock-screen style, ambient display, screensaver, wallpaper, refresh rate, colour mode, resolution, night light | HID | No UI |
| 17 | Media/ring/alarm volume, vibrate, ringtone (bundled list) | KC; media cap PG | Native, `AudioManager` |
| 18 | DND/Modes, notification channels, spatial audio | HID | Ringer mode via volume keys |
| 19 | Font/display size, bold, high-contrast text, colour inversion/correction, remove animations, mono audio, captions, flash alerts | KC | Native over `Settings.Secure` keys |
| 20 | Screen reader, Select to Speak, Switch Access, magnification, downloaded services | HID in S1 | Not in AOSP (F10); S2 |
| 21 | Language (en-US, es-US) | KC | Native; regional prefs, keyboards, gestures HID |
| 22 | Date, time, time zone | FRC | `AUTO_TIME/AUTO_TIME_ZONE=1`, `DISALLOW_CONFIG_DATE_TIME`; zone from NITZ else portal [I] |
| 23 | Software update | KR | Status in About; silent A/B; `config_show_system_update_settings=false` |
| 24 | Factory reset | PG | Parent area; other reset options HID; Guard asserts `DISALLOW_FACTORY_RESET` |
| 25 | Developer options, USB debugging, logs, backup, users/guest/private space, accounts | HID | `DISALLOW_DEBUGGING_FEATURES/ADD_USER/MODIFY_ACCOUNTS`, component-override |
| 26 | Apps, app info, permissions, default apps, special access, notification access | HID | `DISALLOW_APPS_CONTROL/UNINSTALL_APPS/CONFIG_DEFAULT_APPS`; fixed pre-grants [M]; PermissionController is a separate surface |
| 27 | Screen lock, biometrics, Safety Center, privacy dashboard, autofill, device admins | HID | `config_enableSafetyCenter=false`, override |
| 28 | Location master toggle | PG, default off (report 05) | `DISALLOW_CONFIG_LOCATION`; sub-pages HID; Weather uses a parent-set city |
| 29 | Emergency info card, alert history | KR | Native over EmergencyInfo, CellBroadcast |
| 30 | SOS gesture, WEA opt-outs | PG | Presidential alerts not opt-out [M] |
| 31 | Supervision page | HID | PIN confirm/set/recover activities stay |
| 32 | Battery level, saver | KC/KR | Native; per-app battery HID |
| 33 | Storage used/free | KR | Native; SD/USB HID |
| 34 | About: name, model, OS, build (no tap), IMEI/number | KR | Native |
| 35 | Legal, open-source licences, regulatory label | KR | Own plain-text viewer; label needs no PIN, within 3 steps [S: 47 CFR 2.935 via search summary] |

"Standard" Wi-Fi/data = rows 1-2, 6-7, 12. Rows 3-5, 8-11 are bypass or bricking vectors and are the only departures from "as it is"; see decision 1.

## 4. Options & trade-offs

| Option | Effort | Rebase per drop | Tamper resistance | Crash safety | Verdict |
|---|---|---|---|---|---|
| A. Stock Settings, overlays only | Low | Low | Weak (Catalyst/SPA, adult homepage) | Good | Part of D+ |
| B. Slim fork, delete screens | 3-4 weeks | 1-3 weeks (manifest, gateway, Catalyst churn) [I] | Good | Medium | Reject |
| C. New Compose app | 4-6 months [I] | Low, but system-API drift | Best | **Worst**: ~60 intents, framework class names, SUW, Wi-Fi/eSIM rebuilt | Reject |
| **D+. ZuneSettings front, stock engine room** | 8-9 weeks | 2-4 days | Good; strong with S2 gate | Good (router) | **Recommend** |

## 5. Recommended Stage-1 design

**Packages.** `ZuneSettings` (platform cert, privileged, `system_current`, non-exported pages) owns `android.settings.SETTINGS`; stock `SettingsHomepageActivity` and all non-allowlisted activities are disabled. `ZuneGuard` holds ROLE_SYSTEM_SUPERVISION and applies policy. Remove `SettingsIntelligence`, `HTMLViewer`, `CertInstaller`.

**Generated, not hand-maintained.** A CI script reads the built `AndroidManifest.xml`, subtracts `settings_allowlist.txt` (about 40 entries: Wi-Fi/Internet 14, mobile and data usage 8, panel 1, Bluetooth 7, credential/supervision 6, SUW accessibility 1) and emits (a) `component-override` XML, (b) the catch-all intent filters, (c) a diff of new upstream `config_*` bools. Any new upstream activity is denied by default. Airplane uses `AirplaneModeSettingsActivity`; `NetworkDashboardActivity` stays off.

**Catch-all router.** ZuneSettings declares every `android.settings.*` action found in SystemUI, framework and Zune apps that no allowlisted stock activity serves, and routes it to its home (`WIRELESS_SETTINGS` to the Wi-Fi & data row) or finishes silently. This prevents `ActivityNotFoundException` crashes in SystemUI [I] and covers the shade gear (`ACTION_SETTINGS`).

**Overlays.** Settings: F2 knobs plus `config_show_premium_sms`, `_assist_and_voice_input`, `_manage_device_admin`, `_screen_pinning_settings`, `_satellite_tile`, `_wifi_mac_address`, `_wifi_ip_address`. Framework: `config_enableSafetyCenter=false`; `config_ntpServers` (default `time.android.com`) and, if present, `config_httpsTimeUrls` to Zune endpoints [P]. Locales en_US, es_US [M]. Help URLs stay empty (CI check).

**SystemUI.** Tile default and stock lists = `internet,bt,airplane,flashlight,rotation,saver`; `config_globalActionsList` = `emergency,power,restart`; lock-screen affordances flashlight and camera [I: ids]. This drops cast, wallet, controls, screen record, mic/camera toggles and DND.

**Restrictions.** ZuneGuardian, as Device Owner (reports 04/05), asserts at every boot and on key changes those in rows 4, 11, 13, 22, 24-28, plus `DISALLOW_SAFE_BOOT` and `ADD_USER`; `MANAGE_USERS` base restrictions are the fallback (F3). Never set the two page-level restrictions of F3.

**Parent gate and portal.** The PIN is created at pairing in ZuneSetup, which also enables supervision without a dialog before setup completes (F9; report 05). **Forgot PIN:** the parent resets it in the portal (login on another device); the new verifier is delivered in the signed policy. Offline, the existing PIN keeps working. Locked rows show "Ask a parent", which calls `ParentGate.confirm()`; the same gate serves report 05's approvals UI. **Factory reset** is a PIN-gated button in the parent area; Guardian lifts `DISALLOW_FACTORY_RESET` for the wipe only. The wipe removes the PIN; the device returns to ZuneSetup and needs a new pairing code; the portal alerts and keeps the child profile; a recovery-mode wipe cannot be blocked (report 04 #16). **Remote settings** (signed policy, cached, **never expiring to unrestricted**): screen-timeout cap, media-volume cap, roaming, data warning/limit, location, airplane lock, SOS gesture, default language and time zone. Offline enforcement is local: persisted restrictions plus Guardian re-assertion.

**Accessibility and kids.** Native set is row 19. Targets at least 56 dp, text plus icon, about grade 3-4 reading level [I], all strings externalised from day 1, every page TalkBack-labelled before TalkBack ships. **CVAA (47 CFR Part 14) makes smartphone manufacturers responsible for accessible SMS/VoIP/video software they supply; third-party assistive options count only if available at nominal cost** [S]. With sideloading disabled that route is closed, so TalkBack plus TTS is likely launch-gating [I]; counsel via report 11.

**Screen map (final).**
```
Zune Settings (child home)
|- Wi-Fi & mobile data [stock]  Wi-Fi: list, add network, saved, details | Mobile: data, roaming, usage | Airplane
|- Bluetooth [stock]
|- Sound            volumes, vibrate, ringtone
|- Display          brightness, timeout (cap), text size, dark theme
|- Accessibility    text/display size, bold, contrast, colours, animations, mono audio, captions, flash alerts
|- Language         English, Espanol
|- Battery          level, saver
|- Storage          used/free
|- Emergency        info card, alert history   (SOS, opt-outs: parent)
|- About            name, model, OS, build, number, update status
|    |- Legal & licences, regulatory label (no PIN)
`- Parent area [PIN]  Reset device ; Stage 2 adds on-device unlock for rows 3, 8, 9
(no row: date/time forced, search, accounts, apps, notifications, security, developer)
```

**Work breakdown (Stage 1, engineer-weeks).** Overlays, sysconfig, restrictions, package removals 1.5; ZuneSettings home plus 8 native pages 3; ParentGate UI and Guardian API (depends on report 05) 1.5; allowlist/router generators and CI crawl (query-activities, intent fuzz, tap-every-row) 1; Cuttlefish and device test 1.5. **Week-1 spike on Cuttlefish:** `component-override` on `com.android.settings`, stock Wi-Fi/mobile screens under Device-Owner restrictions, SystemUI after tile and power-menu trimming, and `SETUP_INTERNET` from ZuneSetup (F11).

## 6. Stage-2 improvements

Gate patch (about 150 lines in `SettingsActivity`, `SubSettings.isValidFragment`, `CatalystSettingsActivity`) with a parent-session token that unlocks rows 3, 8, 9 on the device; platform Supervision PIN spike; "approved networks only" mode and parent-pushed Wi-Fi credentials from the portal [M: DPM `setWifiSsidPolicy` needs Device Owner; prototype]; parent-approved captive-portal sign-in (report 04); TalkBack built from google/talkback plus TTS; notification-block protection for Zune apps; travel time zone; richer emergency card; kid-friendly explainer strips on the stock Wi-Fi/data pages; more locales.

## 7. Conflicts with earlier reports

- **03:** lists SettingsIntelligence as a hard keep and "talkback" as a keep. Corrected: SettingsIntelligence is removable (F7); TalkBack and TTS are not in AOSP (F10). Its Q7 patch budget: answer is zero Settings patches in S1.
- **04:** "exclude AOSP Settings as child UI" is right for the UI but Settings cannot be excluded (F4); "Developer options stripped" is achievable without a patch but Settings can re-enable some components, so keep `DISALLOW_DEBUGGING_FEATURES`; "disable profile user types" must exempt `profile.supervising`; time limits via `PackageUsagePolicy` are **not enabled in 17.0** (F9). Help-link risk (#5) is lower than rated (F8).
- **05:** "Settings factory reset: `DISALLOW_FACTORY_RESET`, no UI" becomes a PIN-gated parent-area button (the brief asks for parent-gated reset); "hide Settings' Supervision entry" is adopted. 05's time limits via the platform `TIME_LIMIT` are already marked unfinished; flag `enable_supervision_package_usage_apis` is off in 17.0 (F9).
- **12:** "Settings forwarding/barring: `DISALLOW_CONFIG_MOBILE_NETWORKS`" blanks the whole mobile page, contradicting D14 (F3); use carrier config and no entry instead.
- **01/02/13/15:** no conflict.

## 8. Risks & unknowns

- Nothing is checked against Google's tag; GrapheneOS may differ in Settings and flags.
- Catalyst screens bypass `ENTRY_FRAGMENTS`; whether a disabled host activity makes the launching row a no-op or a crash is unverified, so a tap-every-row crawl is mandatory.
- Stock Wi-Fi advanced fields stay visible in Stage 1 (residual, low exploitability: no browser; Private DNS pinned).
- Supervision is new in 17.0 and flag-dependent; the platform PIN option (recovery with a non-Google account type, `fw.max_users=1`, profile-type disabling in report 04) is untested.
- Settings re-enables some of its own components at runtime (F2).
- PermissionController (privacy dashboard, permission manager) is a separate surface needing its own trimming [I]; notification long-press can block Zune notifications [I].
- No geo time-zone provider without GMS, so Wi-Fi-only devices need a portal-set zone [I].
- CVAA, FCC e-label and E911/WEA duties need counsel [S/M].

## 9. Decisions needed from the founder

1. **What "standard" Wi-Fi/data includes.** Default: rows 1-2, 6-7, 12 as stock; proxy/static IP, Private DNS, VPN, hotspot, Wi-Fi Direct, APN, eSIM management, data limits and captive portals parent-gated or hidden.
2. **Captive-portal Wi-Fi (hotel, school) unsupported in v1.** Default: accept; parent hotspot as workaround.
3. **TalkBack and TTS: launch-gating or Stage 2?** Default: Stage 2 build; decide with counsel before commercial launch.
4. **Parent PIN: Zune-owned (report 05) or platform Supervision PIN.** Default: Zune-owned in Stage 1; evaluate the platform PIN in Stage 2 for hardware throttling.
5. **Location default.** Default: off, parent opt-in via portal (report 05); Weather uses a parent-set city.
6. **Launch locales.** Default: en-US and es-US.
7. **SOS power-button gesture.** Default: off, parent-gated (accidental 911 calls); lock-screen emergency calls always work.
8. **Reset.** Default: parent PIN plus portal alert; accept that a recovery-mode wipe leaves an inert device.

## 10. Load-bearing claims

| # | Claim | Basis | Source |
|---|---|---|---|
| 1 | Stock Settings 17 has 437 activity entries (337 exported), ~250 gateway fragments, 233 Catalyst screens, 134 config bools | P | GOS-Settings@17 `AndroidManifest.xml`, `core/gateway/SettingsGateway.java`, `res/values/config.xml` |
| 2 | Sysconfig `component-override` disables activities at scan time | P | GOS-fwb@17 `services/core/java/com/android/server/SystemConfig.java:1018,2438`, `pm/ScanPackageUtils.java:849` |
| 3 | Settings search shows only if SettingsIntelligence is installed | P | GOS-Settings@17 `search/SearchFeatureProvider.java:91`, `search/actionbar/SearchMenuController.java:74` |
| 4 | Wi-Fi and mobile pages take `DISALLOW_CONFIG_WIFI` / `DISALLOW_CONFIG_MOBILE_NETWORKS` as page-level restrictions | P (behaviour I) | `network/NetworkProviderSettings.java:395`, `network/telephony/MobileNetworkSettings.java:129` |
| 5 | Framework hard-references Settings classes; SystemUI sends ~60 `Settings.ACTION_*` | P | GOS-fwb@17 `core/res/res/values/config.xml:477,5004,7246`; grep of `packages/SystemUI/src` |
| 6 | Supervision PIN lives on a `profile.supervising` user; setup skips confirmation before user setup completes; recovery via role-holder activities | P | Settings `supervision/SetupSupervisionActivity.kt`, `EnableSupervisionActivity.kt`, `SupervisionIntentProvider.kt`; fwb `UserTypeFactory.java:366` |
| 7 | System applies `DISALLOW_FACTORY_RESET` only with no supervision role holder | P | fwb `services/supervision/.../SupervisionService.java:1040-1052` |
| 8 | In 17.0 the supervision settings/PIN flags are enabled but `enable_supervision_package_usage_apis` is not | P | GOS build_release@17 `aconfig/{bp4a,cp2a,trunk_staging}/android.app.supervision.flags`, `release_configs/cp2a.textproto` |
| 9 | Licence and manual screens hard-code HTMLViewer; help URLs are empty | P | Settings `SettingsLicenseActivity.java:98-110`, `ManualDisplayActivity.java:54-59`, `HelpTrampoline.java`, `res/values/strings.xml:8436` |
| 10 | TalkBack/TTS are not in AOSP; GrapheneOS ships prebuilts; google/talkback is Apache-2.0 | P | GOS `platform_external_talkback`, `platform_external_SpeechServices`; github.com/google/talkback `README.md`, `LICENSE` |
