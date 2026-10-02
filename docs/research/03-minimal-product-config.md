# Zune research 03: Clean minimal AOSP product configuration

Date: 2026-10-02. Basis tags: **[PRIMARY]** read in real source this session; **[SECONDARY]** reputable page or search summary; **[INFERRED]** my engineering judgement; **[MEMORY]** training knowledge, unchecked.
source.android.com and android.googlesource.com are blocked, so I could not read `android-17.0.0_r1` directly. Android 17 ground truth comes from derivatives that pin that tag: **GOS-build@17** = GrapheneOS/platform_build branch `17` (2026-09-12), **GOS-fwb@17**, **GOS-release@17** (build/release), **LOS-build@24** = LineageOS/android_build `lineage-24.0` (2026-09-22), and **AOSP16-build** = aosp-mirror/platform_build `android16-qpr1-release` (unmodified AOSP). Nothing here was build-tested; all makefiles are drafts.

## 1. Summary & recommendation

Do not inherit AOSP's stock phone products (`aosp_product.mk`, `generic_system.mk`, `handheld_*.mk`, `telephony_*.mk`) and then try to subtract from them. `inherit-product` records `@inherit` markers that cannot be filtered out, and `PRODUCT_PACKAGES_REMOVE` does not exist [PRIMARY]. Instead build a **default-deny composition**: Zune's own `zune_system.mk` / `zune_system_ext.mk` / `zune_product.mk` that inherit only `base_system.mk` and `base_system_ext.mk` and add an explicit allowlist. Enforce it with a CI test that diffs the built image's APK/APEX list against `vendor/zune/allowlist/packages.txt`, so new upstream components (Android 17 already adds a Web App installer module) never arrive silently.

- Keep all Mainline APEXes and platform hard dependencies (SystemUI, Settings, Telecom stack, KeyChain); most APEXes are boot-classpath jars. Neuter them with release flags, feature masks and RRO config.
- Replace Launcher, Setup, Camera, Gallery, Music, Updater with Zune apps. Delete Browser2, QuickSearchBox, HTMLViewer, CaptivePortalLogin, Print, CertInstaller, Traceur.
- Keep a WebView engine only if a first-party app needs it (curated YouTube is the likely need); AOSP's bundled prebuilt is not security-maintained.
- Overlays must be RRO modules (`PRODUCT_ENFORCE_RRO_TARGETS := *`), not `PRODUCT_PACKAGE_OVERLAYS` dirs.
- Targets: Cuttlefish (`PRODUCT_DEVICE := vsoc_arm64_only`) for development; Pixel 10a/9a via a fork of GrapheneOS `adevtool`, repointing its single product hub (`common/product-common.mk`) at the Zune layers (hardware: research 02).

## 2. Findings

**F1. How the stock product graph composes** [PRIMARY: GOS-build@17 `target/product/*.mk`; https://github.com/GrapheneOS/platform_build/tree/17/target/product]
- `aosp_arm64` = `core_64_bit` + `generic_system` + `handheld_system_ext` + `telephony_system_ext` + `aosp_product` + board `device.mk` (LOS-build@24 `aosp_arm64.mk`). `generic_system` = `handheld_system` + `telephony_system` + `languages_default` + `updatable_apex` + plumbing (update_engine, otapreopt, zygote rcs, `PRODUCT_ENFORCE_RRO_TARGETS := *`). `aosp_product` = `handheld_product` + `telephony_product` + Messaging, PhotoTable, ThemePicker. `handheld_*` inherit `media_*`, which inherit `base_*`.
- AOSP16-build `handheld_product.mk` lists Browser2, Calendar, Camera2, Contacts, DeskClock, Gallery2, LatinIME, Music, QuickSearchBox, SettingsIntelligence. LOS-build@24 wraps Browser2/Calendar/Camera2/Gallery2/Music in `ifeq ($(LINEAGE_BUILD),)` and ships its own browser (Jelly) unconditionally [PRIMARY: LOS vendor `config/common.mk`].
- The smallest phone-class chain that real products use is exactly the Pixel one: GOS adevtool `common/product-common.mk` inherits `core_64_bit_only`, `generic_system`, `handheld_system_ext`, `telephony_system_ext`, `aosp_product`, `handheld_vendor`, `telephony_vendor`. Cuttlefish "slim" (`aosp_cf_arm64_slim`) swaps in `media_system_ext` + `media_product` but still inherits `generic_system`, so `handheld_system.mk` still lands [PRIMARY: GrapheneOS/device_google_cuttlefish@17].
- `media_system.mk` itself adds `HTMLViewer` and the WebView feature XML and loader libs, and `base_system.mk` carries 300+ modules including the whole Mainline set [PRIMARY].

**F2. Removing things has only three working mechanisms** [PRIMARY: `core/product.mk:532-544`; no `PRODUCT_PACKAGES_REMOVE` anywhere in GOS-build@17 `core/` or `target/`; SECONDARY: https://github.com/MocLG/kioskhome-gsi README, an Android 13 kiosk GSI that hit this]
(a) do not inherit the file that adds it; (b) Soong `overrides:` (GOS `SetupWizard2` overrides `Provision`); (c) built-in switches (`PRODUCT_NO_DYNAMIC_SYSTEM_UPDATE`, `RELEASE_*` flags). GOS and LOS both fork `build/make` and edit these files.

**F3. Android 17 release flags decide which Mainline modules exist** [PRIMARY: GOS-release@17 `flag_values/{cp2a,bp4a,ap3a}`; `aosp_current` aliases `cp2a`; lunch is `<product>-cur-<variant>`]
With `cp2a` (17.0): `RELEASE_TELEPHONY_MODULE`, `RELEASE_TELECOM_MAINLINE_MODULE`, `RELEASE_WEBAPP_MODULE`, `RELEASE_NPUMANAGER_MODULE`, `RELEASE_CONSCRYPT_NSC` are true and NFC is the `com.android.nfcservices` APEX. `base_system.mk` and `default_art_config.mk` condition on these. `com.android.webapp` is Android 17's system Web App installer, off by default and toggled in Developer options [SECONDARY: https://github.com/jaduncan/mintpwa]. A vendor release config can override flags via `PRODUCT_RELEASE_CONFIG_MAPS` (the mechanism `generic_system.mk` uses for gms_mainline) [INFERRED that it works for our own flag override].

**F4. Mainline cannot be pruned by package name** [PRIMARY: `default_art_config.mk`]
adservices, appsearch, bt, conscrypt, devicelock, healthfitness, ondevicepersonalization, uwb, virt, wifi, tethering, nfcservices and others contribute `PRODUCT_APEX_BOOT_JARS`; many also contribute system-server jars. `MODULE_BUILD_FROM_SOURCE ?= true` in `aosp_arm64.mk` builds them from source and signs them with our keys (we have no Google-signed module prebuilts without GMS) [PRIMARY: LOS-build@24].

**F5. Hard dependencies** [PRIMARY]
- `data/etc/system-required-packages.xml` marks `android` and `com.android.settings` as `prevent-disable` (GOS-fwb@17).
- System-server apps: FusedLocation, InputDevices, KeyChain, SettingsProvider, WallpaperBackup, Telecom/TelecomUi/TelecomServiceResources (or TelecomShim) (`handheld_system.mk`, `base_system.mk`).
- SystemUI's `RecentsModule` throws `RuntimeException("No recents component configured")` if `config_recentsComponent` is empty, so do not blank it.
- `LauncherProxyService` (renamed from OverviewProxyService in 17) binds `android.intent.action.QUICKSTEP_SERVICE` from the package in `config_recentsComponentName`. In 3-button mode (`isLegacyMode`) no swipe-up UI is needed, and `OverviewProxyRecentsImpl` is a no-op with no proxy. A non-Quickstep Zune launcher therefore works with 3-button navigation.

**F6. WebView in Android 17** [PRIMARY unless tagged]
- GOS-release@17 `flag_values/cp2a` pins `RELEASE_PACKAGE_WEBVIEW_VERSION` 145.0.7632.218 and `RELEASE_USE_STANDALONE_WEBVIEW=true`, a prebuilt.
- Chromium's integrator guide says AOSP's prebuilt "is not currently updated on a regular schedule, and may have known security issues" and recommends shipping a recent self-built stable WebView. WebView for a new Android version is released only after that Android's source is published. Providers are listed in `frameworks/base/core/res/res/xml/config_webview_packages.xml` (GOS swaps in Vanadium, `app.vanadium.webview`). https://raw.githubusercontent.com/chromium/chromium/main/android_webview/docs/aosp-system-integration.md
- `external/chromium-webview` appears in the AOSP16 manifest but in neither the GOS 17 nor the LOS 24 manifest, so I could not confirm where AOSP 17 hosts it [PRIMARY for the absence; INFERRED for the cause].
- `SystemServer` starts `WebViewUpdateService` only if `FEATURE_WEBVIEW` is declared, and a missing default provider only logs a warning. A WebView-less image therefore boots, but any app that instantiates a WebView fails.

**F7. Neutering without deleting** [PRIMARY]
- `<unavailable-feature name=".."/>` in a permissions XML (Cuttlefish slim: `slim_excluded_hardware.xml`, `soc_specific`, `relative_install_path: "permissions"`).
- `SystemServer` gates services on features: Bluetooth ("No Bluetooth Service" if absent), Print, WebView, Mms (telephony), Autofill, Credentials, UWB, Wi-Fi Aware/RTT/Direct.
- Static RRO: `runtime_resource_overlay { product_specific: true }` with `<overlay isStatic="true" priority=".." targetPackage="android">` (GOS `GosOverlay`; GOS-adevtool `config/mk/google_devices/platform/zumapro/gos-overlays`).
- Config knobs in `core/res/res/values/config.xml`: `config_defaultBrowser` (empty by default), `config_defaultAssistant`, `config_systemGallery`, `config_defaultSms`, `config_defaultDialer`, `config_hasRecents`, `config_navBarInteractionMode`.
- SystemUI `quick_settings_tiles_default` is `internet,bt,dnd,cast,flashlight,airplane,rotation,wallet,alarm,controls,screenrecord,battery`. SettingsProvider `defaults.xml` has `def_device_provisioned`, `def_user_setup_complete`, `def_lockscreen_disabled` (all false). `config_user_types.xml` sets default restrictions at user creation only.
- Android 17 has a platform parental-supervision stack (`SupervisionService`/`SupervisionManager`, `config_systemSupervision`, `config_allowedSupervisionRolePackages`, `config_defaultSupervisionProfileOwnerComponent`, PIN and recovery flows) behind aconfig flags. Maturity unknown; a candidate hook for the parental-controls topic.

**F8. How apps and privileges are packaged** [PRIMARY: GrapheneOS/platform_packages_apps_SetupWizard2@17, platform_external_PdfViewer@17, kioskhome-gsi]
- In-tree privileged app: `android_app { certificate: "platform", privileged: true, system_ext_specific: true, platform_apis: true, overrides: ["Provision"], required: [privapp-permissions xml] }`; its finish step writes `DEVICE_PROVISIONED=1` and `USER_SETUP_COMPLETE=1`.
- Gradle-built app: `android_app_import { product_specific: true, apk: "prebuilt/app-release.apk", preprocessed: true }`.
- Priv-apps need `privapp-permissions-*.xml`; pre-granted runtime permissions go in `system/etc/default-permissions/*.xml` (kioskhome).

**F9. Prior art** [PRIMARY unless tagged]
- GrapheneOS forks `platform_build`, edits the handheld files, ships its own app repos (Camera, PdfViewer, Updater, SetupWizard2) and Vanadium; its Pixel layer is generated by `adevtool` (research 02).
- LineageOS: `vendor/lineage/config` tiers (`common_mini_phone`, `common_full_phone`, `wifionly.mk`, `data_only.mk`), RRO overlays, `enforce-product-packages-exist`. CalyxOS `vendor_calyx` and /e/OS (BlissLauncher, microG) follow that layout; iodéOS is a LineageOS fork with DNS-level parental control [SECONDARY].
- No open-source kids-specific AOSP product tree turned up; only kiosk GSIs (kioskhome-gsi), parental-control apps (KidSafe, Child Screen Time) and iodéOS [SECONDARY, web search].

## 3. Keep / remove / replace (phone-relevant)

| Component | Verdict | Notes |
|---|---|---|
| SystemUI, Settings, SettingsProvider, SettingsIntelligence | KEEP (hard) | F5. Hide Settings from the launcher and gate behind a parent PIN; RRO for QS tiles and defaults |
| Launcher3QuickStep | REPLACE: ZuneHome | HOME category, 3-button nav, valid `config_recentsComponentName` |
| Provision / SetupWizard | REPLACE: ZuneSetup | Parent-pairing flow; sets provisioned flags (F8) |
| Telecom, TeleService, TelephonyProvider, CarrierConfig, ContactsProvider, BlockedNumberProvider | KEEP (hard on a radio device) | Pixel always has a radio; SIM optional |
| Dialer, Contacts, Messaging, CellBroadcast, EmergencyInfo, ImsServiceEntitlement, ONS, Stk | DECIDE (Q1) | Wi-Fi/data-only: drop the UIs. Without a dialer there is no emergency calling [INFERRED] |
| CarrierDefaultApp | REMOVE | Opens carrier portal URLs via browser intents [MEMORY] |
| Camera2, Gallery2, Music, Calendar (AOSP) | REPLACE: ZuneCamera/Photos/etc. | No Email or Calculator project exists in AOSP16/GOS17/LOS24 manifests |
| DeskClock | KEEP or replace | Alarms |
| Browser2, QuickSearchBox, BookmarkProvider, PartnerBookmarksProvider, HTMLViewer | REMOVE | Browser surface |
| WebView (`webview`, `android.software.webview.prebuilt.xml`) | KEEP engine only (Q2) | F6; own signed build and update plan |
| CaptivePortalLogin | REMOVE v1 (Q3) | WebView mini-browser; breaks hotel/school Wi-Fi sign-in |
| CertInstaller, Traceur, DeviceDiagnostics, EasterEgg, DeviceAsWebcam, MusicFX, BluetoothMidiService, SharedStorageBackup, PrivateSpace, AvatarPicker | REMOVE | |
| PhotoTable, BasicDreams, LiveWallpapersPicker, ThemePicker/ThemesStub, WallpaperCropper | REMOVE | Launcher owns wallpaper; keep `WallpaperBackup` (system-server app) |
| Print: PrintSpooler, BuiltInPrintService, PrintRecommendationService | REMOVE + mask `android.software.print` | SystemServer gate (F7) |
| CredentialManager | REMOVE + mask credentials feature | SystemServer gate |
| KeyChain, FusedLocation, InputDevices | KEEP (system-server apps) | F5 |
| PackageInstaller | KEEP, neuter | `DISALLOW_INSTALL_*` restrictions [MEMORY]; removal needs a `base_system.mk` edit and is unproven |
| DocumentsUI, ExternalStorageProvider, DownloadProvider | KEEP | Needed by pickers and DownloadManager; drop `DownloadProviderUi` |
| LatinIME, UserDictionaryProvider | KEEP | |
| VpnDialogs, ProxyHandler, PacProcessor | KEEP | A local-VPN content filter needs the consent UI |
| TTS and speech engines | NOT in AOSP | Supply for the assistant; GOS adds its own `SpeechServices` |
| Updater client | REPLACE: ZuneUpdater | Uses `update_engine`; silent A/B |
| Bluetooth (`com.android.bt`), NFC (`nfcservices`), UWB, Wi-Fi, Health Connect, AdServices, OnDevicePersonalization, AppSearch, Virt | KEEP APEX | F4. Neuter: no UI, features masked, DISALLOW restrictions. Remove `Tag`; keep `SecureElement` |
| `com.android.webapp`, `DynamicSystemInstallationService` | REMOVE | `RELEASE_WEBAPP_MODULE=false`; `PRODUCT_NO_DYNAMIC_SYSTEM_UPDATE := true` |
| ManagedProvisioning | DECIDE (Q5) | Keep only if a Device Owner path is chosen |
| AccessibilityMenu, talkback, StorageManager | KEEP | Accessibility; small |

## 4. Options & trade-offs

| Option | For | Against |
|---|---|---|
| A. Inherit stock `aosp_product`/`generic_system`, subtract via `overrides:` stubs and RRO | No `build/make` fork | Needs a stub module per removal; new upstream apps appear silently; cannot drop `HTMLViewer` etc. cleanly |
| B. Fork `build/make` and delete lines (GOS/LOS/kioskhome) | Proven; terse | Every rebase conflicts in the same lines; additions still arrive silently |
| **C. Own allowlist composition from `base_*.mk` (recommended)** | Default-deny; no `build/make` fork; drift is caught by a diff job | Must copy about 50 lines of plumbing from `generic_system.mk`; a missed new plumbing item shows up as a runtime or build error, not a policy hole |

## 5. Recommended design for Zune

**Layout** (draft)
```
device/zune/products/        AndroidProducts.mk  zune_kids_cf.mk  zune_kids_stallion.mk
device/zune/generic_arm64/   BoardConfig.mk   (stub, generic target)
vendor/zune/config/          zune_base.mk zune_system.mk zune_system_ext.mk zune_product.mk
vendor/zune/allowlist/       packages.txt apex.txt
vendor/zune/overlay/         ZuneFrameworkOverlay ZuneSystemUIOverlay ZuneSettingsOverlay ZuneProviderOverlay
vendor/zune/sysconfig/       zune_features.xml privapp-permissions-zune.xml default-permissions-zune.xml
vendor/zune/sepolicy/        private/ public/
vendor/zune/release/         release_config_map.textproto   (RELEASE_WEBAPP_MODULE=false, ...)
vendor/zune/apps/prebuilt/   <App>/<version>.apk  (Git LFS, SHA256-pinned)
packages/apps/ZuneHome ZuneSetup ZuneGuard ZuneUpdater   (in-tree, privileged)
```
Ordinary apps (Assistant, Camera, Photos, Walkie, Journal, Notes, Reader, Learn) are built in their own Gradle CI and consumed as signed `android_app_import` prebuilts, so they update independently and AOSP builds stay fast. Only platform-privileged apps are in-tree. Pinning by hash is the supply-chain control.

**`device/zune/products/AndroidProducts.mk`** (DRAFT, unverified by build)
```make
PRODUCT_MAKEFILES := \
    zune_kids_cf:$(LOCAL_DIR)/zune_kids_cf.mk \
    zune_kids_stallion:$(LOCAL_DIR)/zune_kids_stallion.mk
COMMON_LUNCH_CHOICES := zune_kids_cf-cur-userdebug zune_kids_stallion-cur-user
```

**`vendor/zune/config/zune_system.mk`** (DRAFT; replaces `generic_system.mk` + `handheld_system.mk`)
```make
PRODUCT_NO_DYNAMIC_SYSTEM_UPDATE := true   # read at parse time by base_system.mk: set BEFORE inheriting it
$(call inherit-product, $(SRC_TARGET_DIR)/product/base_system.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/languages_default.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/cfi-common.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/memtag-common.mk)
# media_system.mk minus HTMLViewer
PRODUCT_PACKAGES += android.software.webview.prebuilt.xml libwebviewchromium_loader \
    libwebviewchromium_plat_support CompanionDeviceManager drmserver requestsync \
    preinstalled-packages-media-system.xml
# handheld_system.mk keepers (curated)
PRODUCT_PACKAGES += cameraserver CameraExtensionsProxy DocumentsUI ExternalStorageProvider \
    DownloadProvider FusedLocation InputDevices KeyChain MtpService PacProcessor ProxyHandler \
    VpnDialogs UserDictionaryProvider CalendarProvider TeleService TelephonyProvider \
    BlockedNumberProvider preinstalled-packages-platform-handheld-system.xml
PRODUCT_SYSTEM_SERVER_APPS += FusedLocation InputDevices KeyChain
# Telecom: flag-dependent (TelecomShim under RELEASE_TELECOM_MAINLINE_MODULE), copy the ifeq from handheld_system.mk
# generic_system.mk plumbing (copy; diff each rebase): update_engine update_verifier otapreopt_script cppreopts.sh
#   recovery-refresh netutils-wrapper-1.0 charger_res_images init.zygote64.rc ... PRODUCT_ENFORCE_RRO_TARGETS := *
```

**`vendor/zune/config/zune_base.mk`** (DRAFT)
```make
PRODUCT_BRAND := Zune
PRODUCT_MANUFACTURER := Zune            # keep device-level identity (ro.product.device) from the board layer
PRODUCT_SYSTEM_BRAND := Zune
PRODUCT_PACKAGES += ZuneHome ZuneSetup ZuneGuard ZuneUpdater ZuneAssistant ZuneCamera ZunePhotos \
    ZuneJournal ZuneNotes ZuneReader ZuneLearn ZuneWalkie \
    ZuneFrameworkOverlay ZuneSystemUIOverlay ZuneSettingsOverlay ZuneProviderOverlay \
    zune_features.xml privapp-permissions-zune.xml default-permissions-zune.xml
PRODUCT_PRODUCT_PROPERTIES += ro.boot.vendor.overlay.theme=com.android.internal.systemui.navbar.threebutton
PRODUCT_SOONG_NAMESPACES += vendor/zune
PRODUCT_RELEASE_CONFIG_MAPS += $(wildcard vendor/zune/release/release_config_map.textproto)
$(call enforce-product-packages-exist,)
```

**Soong patterns** (DRAFT)
```
android_app { name: "ZuneHome", privileged: true, system_ext_specific: true,
    certificate: "platform", sdk_version: "system_current",   // platform_apis only if forced
    overrides: ["Launcher3QuickStep"], required: ["privapp-permissions-zune"], /* srcs, static_libs */ }
android_app_import { name: "ZuneReader", apk: "prebuilt/ZuneReader/1.0.0.apk",
    product_specific: true, preprocessed: true }        // pattern from GOS PdfViewer
runtime_resource_overlay { name: "ZuneFrameworkOverlay", product_specific: true }
// manifest: <overlay android:isStatic="true" android:priority="100" android:targetPackage="android"/>
```
Framework overlay values (DRAFT): `config_defaultBrowser=""`, `config_defaultAssistant=app.zune.assistant`, `config_systemGallery=app.zune.photos`, `config_navBarInteractionMode=0`, `config_hasRecents=false`, `config_recentsComponentName` pointing at a valid ZuneHome stub, `config_systemSupervision`, `config_allowedSupervisionRolePackages` and `config_defaultSupervisionProfileOwnerComponent` set to `app.zune.guard`. SystemUI overlay sets `quick_settings_tiles_default` to a short list. Provider overlay sets `def_device_provisioned=false` (ZuneSetup flips it).

**`zune_features.xml`** (DRAFT; effect on a Pixel vendor image unverified)
```xml
<permissions>
  <unavailable-feature name="android.software.print"/>
  <unavailable-feature name="android.software.credentials"/>
  <unavailable-feature name="android.hardware.nfc"/>
</permissions>
```

**`device/zune/generic_arm64/BoardConfig.mk`** (DRAFT stub, mirrors `target/board/generic_arm64`)
```make
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_VARIANT := generic
TARGET_CPU_ABI := arm64-v8a
include build/make/target/board/BoardConfigGsiCommon.mk
BOARD_SEPOLICY_DIRS += vendor/zune/sepolicy/board
```
Cuttlefish needs no stub: `zune_kids_cf.mk` mirrors `aosp_cf_arm64_only_phone` (`core_64_bit_only` + `zune_system` + `zune_system_ext` + `zune_product` + `device/google/cuttlefish/shared/phone/device_vendor.mk`), `PRODUCT_DEVICE := vsoc_arm64_only`. For Pixel, `zune_kids_stallion.mk` inherits adevtool's `vendor/google_devices/stallion/stallion.mk` and our fork of `common/product-common.mk` swaps the `generic_system`/`handheld_*`/`aosp_product` inherits for the Zune layers.

**Build-time and device-time guards** (all [INFERRED] design)
1. CI diff of upstream `handheld_*.mk`, `telephony_*.mk`, `generic_system.mk`, `base_*.mk` against pinned copies on every rebase.
2. Allowlist test over `installed-files.txt`: any unknown APK/APEX fails the build.
3. On-device smoke tests: no `http(s)` VIEW handler, empty browser role holder, `pm list packages` matches the allowlist.
4. A Settings and SystemUI crawl with a no-browser build (tapping every row), because Settings assumes help and legal links resolve [INFERRED].

## 6. Risks & unknowns

- **Not build-verified.** Plausible but unproven: `<unavailable-feature>` on a Pixel vendor image, `PRODUCT_RELEASE_CONFIG_MAPS` flag overrides, `config_hasRecents=false` side effects, removing `PackageInstaller`.
- **Upstream cadence.** AOSP source ships only in Q2 and Q4 and QPR1 (`cp3a`) is absent from the release configs I read. Our base is `android-17.0.0_r1` plus backports we can reach; GrapheneOS publicly complains about gated QPR1 features and patches [SECONDARY, title only: androidauthority.com/grapheneos-android-17-qpr1-security-patches-comments-3712218/].
- **WebView maintenance.** Chromium ships about every 4 weeks and AOSP's prebuilt is explicitly stale, so shipping WebView means a signed update path forever (Vanadium, self-build or prebuilt).
- **Small image plus recovery sideload.** GrapheneOS reported Android 17 breaks recovery sideload for small system images (COW-space exhaustion) [SECONDARY, search snippet of an X post, not read directly]. `update_engine` network OTA is the intended path; test factory-recovery flows.
- **Silent capability growth.** Android 17 adds WebApp, NpuManager, ImsStack, Login, PersonalContext, ContactsPicker projects vs the AOSP16 manifest [PRIMARY]. Allowlist plus flag overrides is the only defence.
- **Emergency calling and carrier alerts** if cellular voice ships without a dialer (legal review). **Captive portals** fail without CaptivePortalLogin.
- **Privapp enforcement:** a missing `privapp-permissions` entry denies permissions or breaks boot (sources conflict). Test on userdebug with enforcement on.
- **16 KB pages / 64-bit-only** (Pixel layer sets `PRODUCT_NO_BIONIC_PAGE_SIZE_MACRO`, `core_64_bit_only`) bind every prebuilt app with native code [INFERRED].

## 7. Decisions needed from the founder

1. **Q1:** Cellular voice/SMS in v1? (Decides Dialer/Messaging/CellBroadcast/Emergency; recommend Wi-Fi plus optional data SIM, no voice.)
2. **Q2:** Ship a WebView? (Needed if curated YouTube or the reader embeds web content; recommend yes, with a named owner for monthly WebView updates.)
3. **Q3:** Support captive-portal Wi-Fi in v1? (Recommend no; document the hotspot workaround.)
4. **Q4:** Bluetooth yes (headphones), NFC off, USB file transfer off by default?
5. **Q5:** Parental-control enforcement model: platform Supervision role, Device Owner (keeps ManagedProvisioning) or a privileged `ZuneGuard`? (Owned by the parental-controls topic.)
6. **Q6:** Navigation: 3-button with no Recents (recommended) vs gestures (needs a Quickstep-compatible launcher fork)?
7. **Q7:** Patch budget: RRO-only for v1, or allow small patches to Settings/SystemUI?

## 8. Load-bearing claims

| # | Claim | Basis | Source |
|---|---|---|---|
| 1 | Pixel and Cuttlefish phone products inherit `generic_system` + `handheld_system_ext` + `telephony_system_ext` + `aosp_product`; no stock phone-class product I read omits `handheld_system.mk` | PRIMARY | GOS adevtool@17 `config/mk/google_devices/common/product-common.mk`; GOS device_google_cuttlefish@17 `vsoc_arm64_only/{phone,slim}/aosp_cf.mk` |
| 2 | `inherit-product` tags make un-inheriting impossible; `PRODUCT_PACKAGES_REMOVE` does not exist | PRIMARY | GOS-build@17 `core/product.mk:532-544` (grep finds none); kioskhome-gsi README |
| 3 | Settings and `android` are `prevent-disable`; SystemUI throws if `config_recentsComponent` is empty; 3-button mode needs no launcher proxy | PRIMARY | GOS-fwb@17 `data/etc/system-required-packages.xml`, `RecentsModule.java`, `LauncherProxyService.java`, `QuickStepContract.java` |
| 4 | Most Mainline APEXes are boot or system-server jars, so they cannot be dropped by package name | PRIMARY | GOS-build@17 `target/product/default_art_config.mk` |
| 5 | In 17.0 (`cp2a`) WebApp, telephony, telecom, NPU-manager modules are on; flags gate them | PRIMARY | GOS-release@17 `flag_values/cp2a/*`, `bp4a/RELEASE_TELEPHONY_MODULE` |
| 6 | AOSP's prebuilt WebView is not regularly updated; WebView for a new Android ships only after its source is public | PRIMARY | https://raw.githubusercontent.com/chromium/chromium/main/android_webview/docs/aosp-system-integration.md |
| 7 | `SystemServer` gates Bluetooth, Print, WebView, Autofill, Credentials on `FEATURE_*`; `<unavailable-feature>` is the product-level mask | PRIMARY | GOS-fwb@17 `services/java/com/android/server/SystemServer.java`; device_google_cuttlefish@17 `shared/slim/slim_excluded_hardware.xml` |
| 8 | Overlays must be RRO (`PRODUCT_ENFORCE_RRO_TARGETS := *`); the RRO and in-tree privileged-app patterns exist as described | PRIMARY | GOS-build@17 `generic_system.mk`; adevtool `gos-overlays/GosOverlay`; SetupWizard2 `Android.bp` |
| 9 | Android 17 ships a platform Supervision framework gated by aconfig flags | PRIMARY | GOS-fwb@17 `core/java/android/app/supervision/*`, `services/supervision/*`, `core/res/res/values/config.xml` |
