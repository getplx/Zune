# OS image: AOSP base, product definition, Settings, SystemUI, navigation, WebView

## Purpose and scope

How to build the Zune image from AOSP `android-17.0.0_r1` ("the tag"): manifest and patch discipline, default-deny product, overlays, telephony residue (112 only), ZuneSettings, SystemUI trim, gesture navigation, Vanadium WebView, radio and USB defaults, 16 KB cleanliness, variants, Cuttlefish CI.

**Stage 1** = every MUST below, simplest form. **Stage 2** = Settings gate patch (about 150 lines [R16 §6]) for on-device parent unlock of Wi-Fi advanced rows, Chromium origin allowlist, lockdown VPN, TalkBack and TTS, Bluetooth class allowlist.

Not covered here:
- ZuneGuardian, signed policy, Device-Owner provisioning, restrictions, bypass suite, Emergency screen, SOS: `03-lockdown-and-guardian.md`.
- Pixel device layers, AVB, signing, OTA, ZuneUpdater, patch pipeline: `04-device-signing-ota-release.md`.
- Device channel, NTP endpoints: `05-backend-and-parent-portal.md`.
- App internals, ZuneLauncher UI, ZuneSetup flow: `09-core-apps-and-design-system.md`; Reader and Videos: `08-content-videos-weather-reader.md`.
- Station: `10-delivery-operations-and-pilot.md`; legal: `11-compliance-and-privacy-engineering.md`; tests: `12-testing-qa-and-acceptance.md`; milestones and repo layout: `01-prerequisites-and-phases.md`.

Package namespace (provisional, name clearance): `app.zune.<module>` for every app module in 01 §4.3 (for example `app.zune.guardian`, `.launcher`, `.settings`, `.setup`, `.updater`, `.messenger`, `.calls`, `.walkie`, `.assistant`, `.videos`, `.weather`, `.photos`, `.reader`). Report evidence came from GrapheneOS and LineageOS trees, not Google's tag (see "Verify first").

## Decisions applied and reconciliations

| Decision | Effect |
|---|---|
| D22 | Full custom OS: ZuneLauncher, ZuneSettings, ZuneSetup are system components; product composed from `base_*`, never a layer on a stock phone product. |
| D14, D31 | ZuneSettings is minimal; Wi-Fi, mobile data, Bluetooth deep-link to stock screens. Bluetooth on, NFC off, USB file transfer off, gesture navigation, no on-screen buttons. |
| D19, D28 | No dialer UI, SMS, Contacts, Messaging. Telephony stack, CellBroadcastReceiver and a hidden in-call UI stay for 112 (resolves R03 Q1). |
| D20, D18 | English only: `en_IN`, fallback `en_US`. Indic fonts kept so Indian cell-broadcast alerts render. |
| D24 | ZuneGuardian is Device Owner and supervision-role holder: stock Supervision page hidden; sole setter of `DISALLOW_FACTORY_RESET`. |
| D26 | Vanadium only (stock `external/chromium-webview` not shipped); only Reader and Videos may create a WebView (resolves R03 Q2, R01 Decision 7). |
| D30 | CaptivePortalLogin removed; Settings buttons patched out; explainer screen. |
| D17, D21 | Pixel 10a (`stallion`), 9a (`tegu`) plus Cuttlefish CI; device layers: `04`. Codenames unverified (01 Verify 14). |
| 09 Mode G (adopted; resolves 02 V12) | Tier A apps are built by Gradle and imported by Soong as `android_app_import` prebuilts with the platform key; the in-tree `packages/apps/Zune*` build is a fallback by ADR. |

**Reconciliations applied**

| Report claim | Change |
|---|---|
| R03: three-button nav, `config_hasRecents=false`, ZuneHome overrides Launcher3QuickStep | Reversed by D31: Launcher3QuickStep stays as recents provider (§7). |
| R03: keep SettingsIntelligence, TalkBack, AccessibilityMenu, MtpService, CalendarProvider, Tag | SettingsIntelligence removable [R16 F7]; TalkBack not in AOSP [R16 F10]; rest removed. |
| R03/R16: lunch alias `cur`; en-US/es-US; 911, WEA | `cur` is GrapheneOS-only: use `aosp_current`. Locale per D20. 911 becomes 112; WEA becomes India cell broadcast. |
| R16: zero Java patches in Settings; `config_show_wifi_settings=false` hides Wi-Fi preferences | Both refuted [R16 F2, F8]: patches P-SET-1..3 (R16 decision 9 default). |
| R01: "under 30 forks" | Unsupported figure; Stage 1 cap is 5 forks. |

## Requirements

**Base and discipline**
- **OS-01 MUST** Pin the tag by commit SHA: `zune/os/manifest/pins.xml` (`repo manifest -r`) is committed and CI fails on any difference. No floating branch.
- **OS-02 MUST** Complete V1 to V3 first; record results in `zune/os/docs/BASELINE.md`.
- **OS-03 MUST** At most 5 forked AOSP repos in Stage 1. Every divergence is a registered patch (§1) on the tag: no merge commits, one change per commit, trailer `Zune-Patch: <ID>`, `git range-diff` on every rebase.
- **OS-04 MUST** System, system_ext and product partitions inherit only `base_system.mk`, `base_system_ext.mk`, `base_product.mk` (if present) and Zune files; never `aosp_product.mk`, `generic_system.mk`, `handheld_*`, `telephony_*`, `media_*`. The vendor partition (04) may inherit `*_vendor.mk`.
- **OS-05 MUST** `zune/os/tools/image_diff.py` gates every build: APKs, APEXes, privileged apps, `INTERNET` holders, exported components and WebView-referencing packages equal the reviewed baseline in `vendor/zune/allowlist/`.
- **OS-06 MUST** No REMOVE-row package (§3) exists in any partition (OsuLogin excepted, inert).
- **OS-07 MUST** Static scan of all APKs (APEX-contained included) finds no activity filter with `VIEW` + `BROWSABLE` + `http`/`https`/`ftp`, and no `WEB_SEARCH` handler.
- **OS-08 MUST** All overlays are RRO modules (`PRODUCT_ENFORCE_RRO_TARGETS := *`); keys an RRO cannot override (V3) are listed in `BASELINE.md`.

**Telephony and locale**
- **OS-09 MUST** Keep Telecom, TeleService, TelephonyProvider, CarrierConfig, CellBroadcastReceiver and a hidden in-call UI; no Dialer launcher, Messaging, Contacts, Stk, ONS; no SMS role holder.
- **OS-10 MUST** 112 can be placed from the Emergency screen (03) and lock screen, no other number can; a cell-broadcast test alert displays.
- **OS-11 MUST** `PRODUCT_LOCALES := en_IN en_US`; default font families incl. Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi, Odia retained.

**Settings and SystemUI**
- **OS-12 MUST** ZuneSettings is the only handler of `android.settings.SETTINGS`; 10 rows (§6); touch targets at least 56 dp (D23).
- **OS-13 MUST** Stock Settings is default-deny: a generated `component-override` disables every component outside `settings_allowlist.txt` (at most 45 activities), regenerated every build.
- **OS-14 MUST** Nobody sets `DISALLOW_CONFIG_WIFI` or `DISALLOW_CONFIG_MOBILE_NETWORKS` (they blank the pages [R16 F3]); CI greps sources and a device test reads `dumpsys user`.
- **OS-15 MUST** Developer options unreachable: no component, `development_settings_enabled=0`, build-number row inert.
- **OS-16 MUST** Wi-Fi, mobile data and Bluetooth pages are stock screens by deep link, unchanged except P-SET-1..3.
- **OS-17 MUST** ZuneSettings catches every `android.settings.*` action sent by SystemUI, framework or Zune apps that no allowlisted activity serves; no `ActivityNotFoundException` in the crawl (AT-04).
- **OS-18 MUST** Own plain-text licence viewer; stock licence and manual activities disabled (HTMLViewer hard-coded [R16 F8]).
- **OS-19 MUST** Reset only via Parent area -> `ParentGate.confirm()` -> Guardian wipe; Guardian is the only setter of `DISALLOW_FACTORY_RESET` (no `MANAGE_USERS` fallback) [R16 F9]; spike on Cuttlefish in week 1. After a wipe the device boots to ZuneSetup and needs a new pairing code; a recovery-mode wipe cannot be blocked (inert until re-paired, 03).
- **OS-20 MUST** Captive portal: explainer activity handles the sign-in action; P-SET-2 applied (D30).
- **OS-21 SHOULD** Wi-Fi password share QR hidden (P-SET-3).
- **OS-22 MUST** SystemUI: six tiles, three-item power menu, lock-screen shortcuts flashlight and camera.

**Navigation**
- **OS-23 MUST** Gesture navigation is default, not child-changeable, with no button bar (the thin gesture handle is allowed); ZuneSetup shows a first-boot gesture tutorial (`09`).
- **OS-24 MUST** HOME resolves to `app.zune.launcher`: Guardian sets persistent preferred activity and HOME role.
- **OS-25 MUST** Build Path A (§7); it passes NAV-1..8 (AT-06) by Z3 exit or Path B replaces it. Path C forbidden in Stage 1. Three-button only by founder decision.

**WebView**
- **OS-26 MUST** Vanadium is the only entry in `config_webview_packages.xml`; the Vanadium browser APK never ships.
- **OS-27 MUST** P-FWK-1: only `app.zune.reader` and `app.zune.videos` (package plus cert digest, from a verified `/system_ext` file) can create a WebView.
- **OS-28 MUST** WebView updates ship independent of full OTA, owned by a named `WebView owner` (`zune/os/OWNERS`); SLA: each Vanadium stable within 30 days, High/Critical within 14.
- **OS-29 SHOULD** Signed policy carries `min.webview` (03 §4.4); Guardian disables Videos Tier 2 below it (03, 08).

**Radios, USB, native code, build**
- **OS-30 MUST** Bluetooth on at first boot, pairing allowed, OPP sharing blocked.
- **OS-31 MUST** NFC off and unreachable: feature masked, `Tag` removed, restriction asserted.
- **OS-32 MUST** USB file transfer off: `MtpService` removed, restriction asserted, charge-only default, adb off in `user`.
- **OS-33 MUST** All native code (image, APKs, Vanadium) 16 KB-clean.
- **OS-34 MUST** Shipped images: `user`, `aosp_current`, release keys (04). `userdebug` only for CI and dev phones; never `eng` or `trunk_staging`.
- **OS-35 MUST** CI per §10 blocks merges. **OS-36 MUST** No GMS, Google services, analytics or ad SDKs.

## Design and build instructions

### 1. Repository, manifest, patch stack

```
zune/os/manifest/  upstream-android-17.0.0_r1.xml (Google default.xml at the tag)  zune.xml  pins.xml
zune/os/patches/   REGISTER.md  <repo>/*.patch (format-patch backup of each stack)
zune/os/device/zune/products/  AndroidProducts.mk zune_kids_cf.mk   (stallion, tegu: 04)
zune/os/vendor/zune/  config/ allowlist/ overlay/ sysconfig/ sepolicy/ release/ webview/ apps/prebuilt/
zune/apps/{guardian,launcher,settings,setup,updater}  Gradle-built (09 Mode G); only the prebuilt APKs enter vendor/zune/apps/prebuilt/
zune/os/tools/  image_diff.py settings_gen.py check_elf_alignment.sh nav_suite/   zune/os/ci/  Dockerfile
```
`zune.xml` includes the upstream file, then per fork `<remove-project name="platform/frameworks/base"/>` plus `<project path="frameworks/base" name="platform_frameworks_base" remote="zune" revision="refs/heads/zune/android-17.0.0_r1"/>`. Forks live under org `getplx` (names are proposals). The monorepo checks out at `<aosp>/zune`; directory `<linkfile>`s expose `device/zune` and `vendor/zune` and a root `.find-ignore` hides the checkout from Soong (01 §4.3, V11; fallback: check out at `vendor/zune`). Paths such as `vendor/zune/allowlist/` in this section mean `zune/os/vendor/zune/allowlist/`.

| ID | Repo | Change | Lines |
|---|---|---|---|
| P-FWK-1 | `frameworks/base` | WebView caller allowlist (§8) | 40 |
| P-FWK-2 | `frameworks/base` | IntentFirewall also reads `/system_ext/etc/ifw` (owner 03) | 30 |
| P-SET-1 | `packages/apps/Settings` | Hide row `configure_network_settings`; null-guard `setAdditionalSettingsSummaries` [R16 F2] | 20 |
| P-SET-2 | same | Hide "Sign in", "venue website" (`WifiDetailPreferenceController2`), carrier setup URL launch [R16 F8] | 30 |
| P-SET-3 | same | Hide Wi-Fi share QR | 15 |
| P-WIFI-1 | `packages/modules/Wifi` | Drop OsuLogin from APEX (conditional, V4) | 5 |
| P-LAU-1 | `packages/apps/Launcher3` | Strip overview actions/search if RRO cannot (conditional) | 100 |
| P-REL-1 | `build/release` | Flag overrides if a vendor map cannot (conditional, V2) | 20 |
| P-FWK-3 | `frameworks/base` | Re-point the power-key multi-press to Guardian SOS (conditional, owner 03, VG-11) | 40 |
| P-TEL-1 | telephony or Telecomm module repo | Deny-all in `GsmCdmaPhone.dial`, `SmsController`, Telecom (conditional, owner 03, VG-9) | 60 |

Budgets are planning limits. If every conditional row fires there are six forked repos (`frameworks/base`, `Settings`, `Wifi`, `Launcher3`, `build/release`, telephony), one above the OS-03 cap: raising it needs an ADR (04 V2 says the same). Start with two forks (`frameworks/base`, `Settings`). Rebase once onto the Q4-2026 drop (about December 2026, unverified), freeze before the staff pilot; monthly ingest: `04`.

### 2. Default-deny product

`vendor/zune/config/zune_system.mk` (draft):
```make
PRODUCT_NO_DYNAMIC_SYSTEM_UPDATE := true     # parse-time: before base_system.mk
PRODUCT_ENFORCE_RRO_TARGETS := *
$(call inherit-product, $(SRC_TARGET_DIR)/product/base_system.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base_system_ext.mk)
PRODUCT_LOCALES := en_IN en_US
PRODUCT_PACKAGES += $(shell cat vendor/zune/allowlist/product-packages.txt)
# plumbing copied from generic_system.mk (update_engine, update_verifier, otapreopt_script, zygote rc ...):
# diff against upstream on every rebase
PRODUCT_RELEASE_CONFIG_MAPS += $(wildcard vendor/zune/release/release_config_map.textproto)
```
`zune_base.mk` sets `ZUNE_BRAND` (one variable; name clearance pending) and `PRODUCT_SOONG_NAMESPACES += vendor/zune`. Products: `zune_kids_cf` (x86_64; mirror `aosp_cf_x86_64_only_phone` without its `generic_system`/`handheld`/`telephony` inherits), `zune_kids_stallion`, `zune_kids_tegu`. `product-packages.txt` (seeded from the KEEP and ADD rows of §3) is the input; `allowlist/image-apps.txt` is the reviewed output that `image_diff.py` compares with `installed-files.txt`, `apex_info.xml` and `aapt2 dump badging`, catching transitive additions. Ordinary apps ship as pinned `android_app_import` prebuilts (SHA-256 in `apps/prebuilt/PINS`; `arm64-v8a` on devices, `x86_64` for Cuttlefish); the five Tier A apps are also Gradle-built prebuilts (09 Mode G, V12).

### 3. Package keep/remove table

| Package(s) | Verdict | Condition |
|---|---|---|
| `android`, `SystemUI`, `SettingsProvider`, `Settings` | KEEP | Hard references; Settings is `prevent-disable` [R03 F5, R16 F4]; default-deny (§6). |
| `Launcher3QuickStep` | KEEP, never HOME | Recents and launcher-proxy provider (§7). |
| All Mainline APEXes | KEEP | Not prunable [R03 F4]; `RELEASE_WEBAPP_MODULE=false` drops `com.android.webapp` (V2). |
| `Telecom`, `TeleService`, `TelephonyProvider`, `CarrierConfig`, `ContactsProvider`, `BlockedNumberProvider`, `CellBroadcastReceiver` | KEEP | 112, APNs, alerts (MCC 404/405 [R20]). |
| In-call UI (`Dialer` or successor) | KEEP InCallService and emergency activities only | Launcher and dial-pad activities disabled (V7). |
| `Messaging`, `Contacts`, `Stk`, `ONS`, `ImsServiceEntitlement`, `EmergencyInfo` | REMOVE | D19/D28; Stk can request browser launches [M]; re-add ImsServiceEntitlement only if the 112 field test needs it. |
| `Browser2`, `QuickSearchBox`, `BookmarkProvider`, `PartnerBookmarksProvider`, `HTMLViewer`, `CaptivePortalLogin`, `CarrierDefaultApp`, `CertInstaller`, `SettingsIntelligence` | REMOVE | Browser and WebView surfaces [R04 F1]; CertInstaller only after P-SET-1; SettingsIntelligence removal ends Settings search. |
| `OsuLogin` (in `com.android.wifi`) | KEEP, inert | Not removable by makefile; WebView gate blocks it; P-WIFI-1 if V4 allows. |
| `PrintSpooler`, `BuiltInPrintService`, `PrintRecommendationService`, `Traceur`, `EasterEgg`, `DeviceAsWebcam`, `MusicFX`, `BluetoothMidiService`, `SharedStorageBackup`, `PrivateSpace`, `AvatarPicker`, `PhotoTable`, `BasicDreams`, `LiveWallpapersPicker`, `ThemePicker`, `ThemesStub`, `WallpaperCropper`, `CredentialManager`, `Tag`, `MtpService`, `DownloadProviderUi`, `CalendarProvider`, `AccessibilityMenu`, `DynamicSystemInstallationService`, `Camera2`, `Gallery2`, `Music`, `Calendar`, `DeskClock` | REMOVE | Mask print and credentials features [R03 F7]. Re-add only what breaks boot or a kept screen. |
| `KeyChain`, `FusedLocation`, `InputDevices`, `WallpaperBackup`, `PacProcessor`, `ProxyHandler`, `VpnDialogs`, `DocumentsUI`, `ExternalStorageProvider`, `DownloadProvider`, `UserDictionaryProvider`, `LatinIME`, `CompanionDeviceManager`, `cameraserver`, `CameraExtensionsProxy`, `PackageInstaller`, `PermissionController` | KEEP | Plumbing; launcher entries disabled; PackageInstaller neutered by restrictions (03). |
| `ManagedProvisioning` | KEEP until 03 fixes the Device-Owner route | Then remove if unused. |
| `Provision` | REPLACE with ZuneSetup | `overrides: ["Provision"]`; sets provisioned flags [R03 F8]. |
| TalkBack, TTS, Vanadium browser | ABSENT | TalkBack and TTS are Stage 2 [R16 F10]. |

### 4. Overlays (RRO modules)

| Overlay (target) | Values |
|---|---|
| `ZuneFrameworkOverlay` (`android`) | `config_navBarInteractionMode=2`; `config_defaultBrowser=""`; `config_defaultAssistant=app.zune.assistant`; `config_systemGallery=app.zune.photos`; `config_enableSafetyCenter=false`; supervision keys `config_systemSupervision`, `config_allowedSupervisionRolePackages`, `config_defaultSupervisionProfileOwnerComponent`, `config_persistentDataPackageName`, `config_emergency_dialer_package` and the dialer-role holder = `app.zune.guardian` (03 §4.1; V3, V7); `config_defaultSms` stays empty; `config_ntpServers` per 05 (never guess hostnames); `xml/config_webview_packages.xml`. Never blank `config_recentsComponent`. |
| `ZuneSystemUIOverlay` (`com.android.systemui`) | `quick_settings_tiles_default` and `_stock` = `internet,bt,airplane,flashlight,rotation,saver` (child cannot edit); `config_globalActionsList` = `emergency,power,restart`; keyguard flashlight and camera (ids: V10). Shade gear reaches ZuneSettings via the router. |
| `ZuneSettingsOverlay` (`com.android.settings`) | Every `config_show_*` knob in [R16 F2, §5] false; `help_url_*` empty (CI check). |
| `ZuneProviderOverlay` (`com.android.providers.settings`) | `def_device_provisioned=false`, `def_user_setup_complete=false`, Bluetooth on, NFC off (V13). |
| `ZuneLauncher3Overlay` (`com.android.launcher3`) | Overview actions, search, widgets, wallpaper entry points off. |
| `ZuneNetworkStackOverlay` | Captive-portal probe URLs to `connectivity.<zone>` (05 BE-42). Detection stays on so a sign-in network is recognised and the explainer shows (OS-20); the only sign-in UI is the explainer. |

### 5. Telephony residue (D28)

Keep the stack; enforce deny-all in policy, not by deleting code: `DISALLOW_OUTGOING_CALLS` and `DISALLOW_SMS` (emergency calls stay permitted, V7), no SMS or dialer role holder, inbound handling in `03`. Do not mask `android.hardware.telephony.messaging` before the 112 and cell-broadcast tests pass; carrier field tests: `12`.

### 6. ZuneSettings and the engine room

ZuneSettings: Compose, platform-signed, privileged, `system_current`, non-exported pages. Ten rows (R16's Language row dropped by D20):
```
Wi-Fi & mobile data [stock: NETWORK_PROVIDER_SETTINGS; mobile NETWORK_OPERATOR_SETTINGS, DATA_USAGE_SETTINGS;
                     airplane AIRPLANE_MODE_SETTINGS]   | Bluetooth [stock BLUETOOTH_SETTINGS] | Sound
Display (timeout capped by policy) | Accessibility (text/display size, bold, contrast, colours, animations,
mono audio, captions, flash alerts) | Battery | Storage | Emergency (info card from policy, alert history)
About (name, model, OS, build, update status, Legal & licences, regulatory info) | Parent area [PIN]: Reset
Absent: date/time (forced), search, accounts, apps, notifications, security, developer, language.
```
Regulatory info opens the stock screen if present, else shows the OEM label data from the stock image; never author label text [R16 row 35]. Parent-controlled values (timeout cap, volume cap, roaming, data warning, location, airplane lock, SOS gesture, time zone, default `Asia/Kolkata`) arrive via ZuneGuardian's bound service; ZuneSettings never uses the network. Locked rows show "Ask a parent" and call `ParentGate.confirm(reason): Boolean` (Guardian API, 03); without Guardian or PIN the Parent area stays locked.

Engine room: `settings_gen.py` reads the built Settings manifest (`aapt2 dump xmltree`) and `settings_allowlist.txt` (seed [R16 §5]: Wi-Fi/Internet 14, mobile and data 8, panel 1, Bluetooth 7, credential/supervision 6, SUW internet 1) and emits `/system_ext/etc/sysconfig/zune-settings-overrides.xml`, the router filters and a diff of new upstream `config_*` bools:
```xml
<config><component-override package="com.android.settings">
  <component class="com.android.settings.homepage.SettingsHomepageActivity" enabled="false"/> <!-- + all others -->
</component-override></config>
```
Settings re-enables some components at runtime [R16 F2]; Guardian re-asserts (03). Wi-Fi advanced fields (proxy, static IP/DNS) stay visible in Stage 1 [R16 row 3]. Captive portal: ZuneSettings handles `android.net.conn.CAPTIVE_PORTAL` (V14) and shows "This Wi-Fi needs a sign-in page. Ask a parent to use a phone hotspot."

### 7. Gesture navigation (D31)

SystemUI gesture mode relies on a launcher-proxy service in the package named by `config_recentsComponentName` (`QUICKSTEP_SERVICE`, `LauncherProxyService` in 17); a home app without one fits only three-button mode [R03 F5].

| Path | Architecture | Verdict |
|---|---|---|
| **A (build first)** | Stock `Launcher3QuickStep` stays as recents provider with RRO trim; `ZuneLauncher` is a plain Compose HOME app. Launcher3's `OverviewComponentObserver` falls back to `RecentsActivity` when another package is default home, as third-party launchers rely on [M]. | Zero fork if RRO suffices; else P-LAU-1. |
| **B (fallback)** | Fork `packages/apps/Launcher3`, strip workspace, all-apps, widgets; ZuneLauncher is the single Launcher3QuickStep-derived package. | Larger fork, churn each drop; estimate in Z3 spike. |
| **C** | Own launcher proxy, recents animation, input consumers. | Forbidden in Stage 1: hidden AIDL renamed between releases, no CTS coverage. |
| **D** | Three-button, ZuneLauncher only [R03 F5]. | Violates D31; founder decision only. |

Sequence: Guardian (Device Owner) calls `addPersistentPreferredActivity` for HOME and sets the HOME role to ZuneLauncher; SystemUI binds the Launcher3 proxy and swipe-up-and-hold opens `RecentsActivity`. Risks: overview chrome is Launcher3's (little theming); overview actions and search must be off; Launcher3's HOME activity must stay enabled or `OverviewComponentObserver` fails [M]; each rebase touches Quickstep. If A fails and B is not passing at Z3 exit, stop and escalate [GATE: before staff pilot].

### 8. WebView (D26)

Provisioning: obtain the Vanadium WebView APK(s) (provider plus any Trichrome library its manifest requires), verify the signing cert against `vendor/zune/webview/CERT.sha256`, check in under `apps/prebuilt/`, import as privileged system `android_app_import` (arm64-v8a), whitelist:
```xml
<webviewproviders><webviewprovider description="Vanadium WebView" packageName="app.vanadium.webview"
  availableByDefault="true"><signature>BASE64_CERT</signature></webviewprovider></webviewproviders>
```
P-FWK-1, in `WebViewUpdateService.waitForAndGetProvider`, which already reads the caller UID [R04 F3]:
```java
if (!ZuneWebViewCallers.allows(Binder.getCallingUid())) {  // /system_ext/etc/zune/webview_callers.xml
    Slog.w(TAG, "WebView denied");
    return new WebViewProviderResponse(null, WebViewFactory.LIBLOAD_FAILED_LISTING_WEBVIEW_PACKAGES);
}
```
Updates: ZuneUpdater (04) delivers signature-matched Vanadium APKs independent of OTA, staged (policy floor: OS-29). Owner weekly: watch upstream, re-verify cert, run AT-07, ship within SLA. Reader declares no `INTERNET`; Videos holds `INTERNET` (09 lists the five holders) and reaches only the Tier 2 hosts through the DNS allowlist and its request filter (08 CNT-14).

### 9. Radios, USB, 16 KB

| Item | Mechanism |
|---|---|
| Bluetooth on | Provider default on; Guardian asserts `DISALLOW_BLUETOOTH_SHARING`; never `DISALLOW_CONFIG_BLUETOOTH`; consider disabling OPP/PBAP/MAP profile properties (V13). |
| NFC off | `<unavailable-feature>` for `android.hardware.nfc*` in `zune_features.xml`, `Tag` removed, no tile, NFC restriction asserted (V13). |
| USB file transfer off | `MtpService` removed, `DISALLOW_USB_FILE_TRANSFER` and `DISALLOW_MOUNT_PHYSICAL_MEDIA`, charge-only default, `ro.adb.secure=1`. USB host feature not masked in Stage 1 (USB-C audio). |
| 16 KB | NDK r28+, `zipalign -P 16`, ELF LOAD alignment 0x4000; `check_elf_alignment.sh` scans partitions, APKs, APEXes, Vanadium. 4 KB kernel unless 04 decides otherwise [R01 F6]. |

### 10. Build, variants, CI

```
repo init -u https://github.com/getplx/Zune -b research/android-kids-foundation \
  -m zune/os/manifest/zune.xml --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle
repo sync -c -j8 --no-tags
source build/envsetup.sh && lunch zune_kids_cf-aosp_current-userdebug && m -j"$(nproc)"
# Z1 vanilla: repo init -u https://android.googlesource.com/platform/manifest -b refs/tags/android-17.0.0_r1
```
Release config is `aosp_current` (alias of `cp2a`, V2); flag overrides live in `vendor/zune/release/`; SPL bumps only via 04's pipeline. Use the working branch until `main` exists [HANDOFF §2]. Host: 32 vCPU, 128 GB RAM, 1 TB NVMe minimum (2 TB recommended, 01 PRE-02), Ubuntu 24.04 container, `/dev/kvm` [R01 F4].

| Lunch target | Use |
|---|---|
| `aosp_cf_x86_64_only_phone-aosp_current-userdebug` | Z1 vanilla baseline; record sync size, build time. |
| `zune_kids_cf-aosp_current-userdebug` | Every merge request: boot, `image_diff`, Settings crawl, NAV suite, WebView test. |
| `zune_kids_cf-aosp_current-user` | Nightly static gates; user-vs-userdebug file diff equals the debug allowlist. |
| `sdk_phone16k_x86_64-aosp_current-userdebug` (name per goldfish tree) | Nightly 16 KB boot, install Zune APKs, smoke. |
| `zune_kids_stallion-...`, `zune_kids_tegu-...` (`user`, `userdebug`) | Pixel 10a, 9a (04). |

## Acceptance criteria and tests

- **AT-01** `repo manifest -r` equals `zune/os/manifest/pins.xml`; `get_build_var BUILD_ID` matches `BASELINE.md`.
- **AT-02** `image_diff.py` passes on `zune_kids_cf` user and userdebug; adding `Browser2` makes it fail.
- **AT-03** On Cuttlefish `cmd package query-activities --brief -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d https://example.com` (also `http://`, `ftp://`) prints nothing; HOME `resolve-activity` returns `app.zune.launcher`.
- **AT-04** Crawl: `am start -a android.settings.SETTINGS` opens ZuneSettings; tapping every row of ZuneSettings, shade, quick settings, power menu and lock screen causes no crash or `ActivityNotFoundException`; the Developer-options action opens nothing; `dumpsys user` lacks `no_config_wifi` and `no_config_mobile_networks`; a fake captive Wi-Fi shows the explainer only.
- **AT-05** On a Pixel, stock pages: Wi-Fi join (password, QR, hidden network), mobile-data toggle, Bluetooth headset pairing work; Wi-Fi preferences row absent.
- **AT-06** NAV-1..8, scripted plus 20 minutes on a Pixel: swipe-up goes home; swipe-up-and-hold opens overview; card swipe dismisses a task; edge swipe goes back; rotation keeps gestures; no button bar; HOME survives reboot and Guardian restart.
- **AT-07** `dumpsys webviewupdate` lists only Vanadium; Reader and Videos create a WebView; a platform-signed test APK not on the list cannot, and the denial is logged; no Vanadium browser package.
- **AT-08** Pixel, shipping image: fresh provisioning leaves Bluetooth on; host `lsusb -v` shows no MTP/PTP interface; `pm list features` has no `android.hardware.nfc`; OPP send rejected.
- **AT-09** `check_elf_alignment.sh` zero failures; 16 KB goldfish boots (`getconf PAGE_SIZE` = 16384), Zune smoke passes.
- **AT-10** In emergency-number test mode (V7) a call from the Emergency screen reaches setup and shows in-call UI; other numbers are refused; no dialer icon; a cell-broadcast test alert renders, Hindi and Tamil samples included. Live 112 tests only as agreed with the carrier (`12`).
- **AT-11** `ro.build.type=user`, `ro.debuggable=0`, `ro.build.tags=release-keys`; no `com.google.android.gms`, `com.android.vending`.
- **AT-12** Re-applying each patch stack on the pinned tag gives an empty `git range-diff`.

## Verify first

Do V1 to V3 before anything else.

| # | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| V1 | Tag exists; build CP2A.260605.016; SPL 2026-06-05; AOSP reachable; `android17-security-release` or `android-security-17.*` exist | Google hosts were blocked [R01 F1-F2] | `git ls-remote` tag and branches; `get_build_var BUILD_ID PLATFORM_SECURITY_PATCH` | Re-pin to newest tag; no security branch means pin plus vendor patches (04). |
| V2 | `aosp_current` = `cp2a`; lunch is `product-release-variant`; vendor release-config map overrides `RELEASE_WEBAPP_MODULE`, SPL, supervision flags | GrapheneOS tree; override inferred [R03 F3] | Read `build/release/`; build with a map | Use real names; P-REL-1. |
| V3 | `base_product.mk` exists; contents of `handheld_*`, `telephony_*`, `media_*`; every REMOVE row removable; RRO overrides supervision keys and the WebView xml | Stock 17 not read [R01 F6, R03 F1] | Read files; build `zune_kids_cf`; boot; `image_diff` | `overrides:` stubs [R03 F2]; `PRODUCT_PACKAGE_OVERLAYS`; one `build/make` fork at most. |
| V4 | OsuLogin neutralisable by override or P-WIFI-1 | APEX-contained [R04 F1] | Inspect `com.android.wifi` | Rely on P-FWK-1 and 03's network deny. |
| V5 | Stock Quickstep with another default home gives working gestures; names `config_recentsComponentName`, `QUICKSTEP_SERVICE`, `LauncherProxyService`; Launcher3 HOME must stay enabled | From memory [R03 F5, M] | Read `OverviewComponentObserver`, `TouchInteractionService`, SystemUI; NAV suite with a stub ZuneLauncher in Z1 | Path B; then §7 gate. |
| V6 | `config_navBarInteractionMode=2` selects gestures; navigation-mode page unreachable | Inferred | `settings get secure navigation_mode` | Guardian sets it. |
| V7 | An in-call UI exists at the tag; `DISALLOW_OUTGOING_CALLS` permits emergency calls; `cmd phone emergency-number-test-mode` works; CB config covers MCC 404/405 | Dialer in 17 unverified [R03 §3, I] | Inspect manifest; Cuttlefish modem simulator; Pixel | Guardian ships an `InCallService` (03). |
| V8 | `waitForAndGetProvider()` is the choke point; zygote preload does not bypass it; Vanadium needs a Trichrome library | GrapheneOS source [R04 F3, I] | Read `WebViewFactory`, `WebViewUpdateServiceImpl`; AT-07 | Gate in `WebViewFactory.getProvider()` plus CI scan that only Reader and Videos reference `android.webkit.WebView`. |
| V9 | Vanadium binaries obtainable, redistributable (GPL-2.0-only patches), arm64, 16 KB-aligned, Android 17-compatible | Licence and distribution unread [R04 F2] | Read repo, licence, releases; ask GrapheneOS; alignment scan | Build Vanadium (or LineageOS WebView patches) on a dedicated host [GATE: before build]. |
| V10 | Settings counts, `config_show_*` effects, Catalyst behaviour, disabled-host behaviour; SystemUI ids | GrapheneOS/LineageOS only [R16] | Read the tag; tap-every-row crawl | Widen allowlist or patches. |
| V11 | `repo init -m <subdir>` and directory `<linkfile>` work with Soong, Kati, `AndroidProducts.mk` discovery | Unverified | Z1: link stub `device/zune`, run `lunch` | Separate repos split by CI. |
| V12 | Mode G works: Gradle-built Tier A APKs imported as `android_app_import` with the platform key are re-signed at release and run as privileged system apps (09 VP-1); in-tree Compose under Soong is only the fallback | Unverified | Z1 stub APK (09 Wave 0) | In-tree Soong build by ADR, Compose under Soong unproven (`09`). |
| V13 | NFC mask, restriction constants, Bluetooth profile properties, provider default keys, USB default work on the Pixel vendor image | Inferred [R03 F7, R16 row 13] | AT-08 on both Pixels | Guardian assertions. |
| V14 | `android.net.conn.CAPTIVE_PORTAL` is the sign-in action; no crash loop without CaptivePortalLogin | Memory | Fake captive network on Cuttlefish | Set `captive_portal_mode`; keep explainer. |
| V15 | Host sizing, Ubuntu 24.04, 1.5-3 h clean build, Cuttlefish product names | Estimates [R01 F4] | Z1 baseline build | Resize; keep a 22.04 image. |

## Risks, open gates and out of scope

- **Gesture navigation** may fail with a non-Quickstep home (V5). [GATE: before staff pilot] Path A or B passes AT-06, or the founder accepts three-button (a D31 deviation).
- **WebView** is a permanent Chromium update burden. [GATE: before build] V9 decides consume vs build. [GATE: before staff pilot] named owner and a demonstrated off-OTA update. [GATE: before charging] SLA met for two consecutive Chromium releases.
- **Security patching** of the tag and Mainline is the central risk (04). [GATE: before external family] pipeline running.
- **Patch drift**: Catalyst screens grew 27 to 237 in 18 months [R16]; Quickstep churns each drop; re-estimate after Z3.
- **112 without a stock dialer** (V7). [GATE: before staff pilot] 112 test passes on both Pixels (`12`).
- **Name clearance**: renaming `app.zune.*` costs a reflash. [GATE: before staff pilot] settle it.
- **Counsel** [GATE: before external family]: GPL-2.0 source duties (Vanadium, kernels); regulatory-label rules for India (unknown; R16's FCC and CVAA material is US, secondary); accessibility duties without TalkBack and TTS.

Out of scope: device layer, AVB, OTA (04); Guardian, policy, restrictions, bypass suite (03); Stage 2 items; own hardware.
