# First-party apps, launcher, onboarding and design system for ages 7-14

## Purpose and scope

Specifies the child-facing shell and first-party apps: build modes and stack, ZuneLauncher (gesture navigation, D31), ZuneSetup (first boot, QR pairing), MVPs for Camera, Photos, Journal, Notebook, utilities and the Reader and Settings entries, the ZuneKit design system, accessibility, crash reporting, tests, effort.

**Stage 1** = every MUST, simplest form: Tier A apps proven at M3, Tier B apps at M5 (`01-prerequisites-and-phases.md`). **Stage 2** = the items under "Out of scope".

Not covered here:
- Guardian, PIN, policy engine, Emergency screen: `03-lockdown-and-guardian.md`. Image, overlays, ZuneSettings rows, navigation Paths A/B: `02-os-image-and-product.md`. Keys, signing, ZuneUpdater: `04-device-signing-ota-release.md`. Backend, portal, channel, vault: `05-backend-and-parent-portal.md`.
- Messenger, Calls, Walkie: `06`. Assistant: `07`. Videos, Weather, Reader internals: `08`. Station: `10`. Legal: `11`. Test execution: `12`.

Evidence came from GrapheneOS, LineageOS and vendor docs, not Google's `android-17.0.0_r1` tree [HANDOFF §2]; see VP-n.

## Decisions applied and reconciliations

**Reconciliations applied**

| Decision / report | Effect |
|---|---|
| D22, D31, R03 F5 | ZuneLauncher is a plain Compose HOME app; stock `Launcher3QuickStep` stays as recents provider (02 §7 Path A). R03's three-button navigation is dropped. |
| D23 | Bands 7-9, 10-12, 13-14 replace R09's 4-6/7-9/10-12; design for age 7. |
| D20 | English only (`en_IN`, fallback `en_US`); R09's Spanish and R16's es-US dropped. |
| D24, D27 | Home layout, tile visibility and sharing come from signed policy. R09's Journal "parent-visible" mode and parent export are dropped: D27 covers messages and AI chats only. |
| 01 vs R09 (six Tier A) | Five in-tree (`guardian launcher settings setup updater`); a sixth needs an ADR. ZuneHome is ZuneLauncher; ZuneComms and ZunePolicyService live inside Guardian (03), so WorkManager runs only in Weather, Guardian, Updater. |
| 02 §2, V12 | 02 builds Tier A in Soong. Here its V12 fallback is the default (Mode G): Gradle builds every APK, Soong only packages it. |
| R09 egress list vs 03 LOCK-23, 06 COM-09/25, 07 AI-04 | INTERNET holders: guardian, updater, calls, videos, weather. Assistant, Walkie, Messenger, Setup hold none. |
| R09 Sentry/GlitchTip | No third-party crash SDK; own reporter (§4.8). |
| R09 Camera and Photos as two apps | One APK `app.zune.photos` (module `apps/photos` plus library `apps/camera`), private storage: avoids MediaStore delete prompts, cross-app access and suspended-provider failures. |
| R16 F10, 02 | TalkBack and a TTS service are not in AOSP; Stage 1 ships without them (§4.7). |
| R16 §5, R09 §4.2, 05 §4.5 | Targets 64/56/48 dp by band, 56 dp floor on system surfaces (02 OS-12), reading grade 3; band home templates (§4.2) feed `templates/band-*.yaml`. |

## Requirements

**Stack and build**
- **APP-01 MUST** One Gradle build (`zune/settings.gradle.kts`) covers `apps:*` and `libs:*`; versions only in `gradle/libs.versions.toml`, pinned at Wave 0, none dynamic; `compileSdk`, `minSdk`, `targetSdk` = 37; dependency verification (SHA-256) on; repositories only Google Maven and Maven Central.
- **APP-02 MUST** Tier A and Tier B differ only in signing and privilege (§4.1). CI holds no release key; release signing is on the offline host (04).
- **APP-03 MUST** Kotlin, Compose, Hilt in apps (libs are DI-free), Room 2.8.x (not Room 3), DataStore, Navigation Compose, `kotlinx.serialization` over OkHttp 5, AIDL for Binder, CameraX (Photos), Media3 (Recorder; Videos in 08), Jetpack Ink (Notebook, Journal), Coil 3 for local files only (versions: VP-4). No gRPC or protobuf on device. WorkManager only in Weather, Guardian, Updater.
- **APP-04 MUST** `zune-lint` (`libs/testing/lint`) fails CI on: `play-services`, `firebase`, `mlkit` or `gms` dependencies; `android.webkit` outside reader and videos; `Linkify` or URL annotations; `ACTION_VIEW` of http(s); `createChooser`; `requestPermissions`; non-constant strings in log calls; Coil network fetchers; `INTERNET` outside the five holders.
- **APP-05 MUST** Every manifest sets `allowBackup=false`, `usesCleartextTraffic=false`, no `QUERY_ALL_PACKAGES`; exported components are listed in `apps/<app>/EXPORTS.md`; native libraries are 16 KB aligned (02 OS-33).
- **APP-06 MUST** Apps reach Guardian only through `libs/core` clients. Guardian authenticates each Binder caller by UID, package, `hasSigningCertificate` against the compiled-in platform and `zune-apps` digests, and a per-interface package allowlist; a `signature` permission alone fails across the two keys (VP-2).

**Shell**
- **APP-07 MUST** `app.zune.launcher` is the only HOME. It is edge-to-edge, keeps taps out of the bottom gesture inset, consumes Back, scrolls to top on Home, declares no `QUICKSTEP_SERVICE`, and passes NAV-1..8 (02 AT-06) as the real launcher.
- **APP-08 MUST** Home renders from `PolicyClient` and policy `home` (§4.2): at most 16 tiles, states SHOWN, LOCKED_TIME, LOCKED_ASK, HIDDEN, a change visible within 1 s. No on-device editing, long-press menu, widget, wallpaper chooser, app drawer or search; tiles start only registry components.
- **APP-09 MUST** Home always shows Emergency (56 dp or more), which opens Guardian's Emergency screen (03 LOCK-34); the launcher never dials. Without a policy answer Home shows only Emergency, Settings and "Ask a grown-up" (03 §4.4).
- **APP-10 MUST** `ZAskGrownUp(kind, subject)` sends `approval.request` (05 BE-16), disables at 5 open requests and shows waiting and granted states. Bedtime shows a dimmed screen, clock, wake time and Emergency; Guardian enforces.
- **APP-11 SHOULD** Home shows time left today (words plus bar) and a weather tile from `content://app.zune.weather.tile/summary` (08 exposes it, caller-checked), caching the last value (VP-8).

**Setup**
- **APP-12 MUST** ZuneSetup is HOME only while `user_setup_complete=0`, follows §4.3, holds no `INTERNET` (Guardian calls the server), shows Emergency on every screen, resumes after process death, and on failure offers Retry and "Erase and restart" (03 LOCK-01).
- **APP-13 MUST** The QR parser accepts only `ZUNE1:<code>` and, while the device has no claim blob, the station's `ZUNE1S:<token>` which it hands to Guardian unread (03 LOCK-30, LOCK-38); manual entry uses an in-app keypad over `ClaimCode.ALPHABET` (value owned by 05); 5 bad codes cost a 60 s wait.
- **APP-14 MUST** Before PIN entry Setup shows "Give the phone to a grown-up"; PIN rules and `FLAG_SECURE` per 03 LOCK-14.
- **APP-15 MUST** Child name (20 characters), avatar id and band come from the verified bundle; the device never asks for a birth date; a mismatch directs the grown-up to the portal.
- **APP-16 MUST** No system permission dialog reaches a child: grants are static (`default-permissions-zune.xml`, 02) plus Guardian; an app without a grant shows its own "Ask a grown-up" screen (VP-6).
- **APP-17 MUST** A `devPairing` flavour (userdebug only) accepts `DEVMOCK`; CI fails if flavour or string is in a `user` build.
- **APP-18 SHOULD** Hands-on setup takes at most 10 minutes excluding downloads.

**Apps**
- **APP-19 MUST** Camera (in `app.zune.photos`): photo, video up to 5 minutes, front and back, flash auto or off; shutter 72 dp or more; no location permission or API, EXIF reduced to orientation; no barcode, filter or extension; handles `STILL_IMAGE_CAMERA` and `_SECURE`; refuses capture under 500 MB free.
- **APP-20 MUST** Photos: private storage (`filesDir`) with a Room index; no MediaStore, no `READ_MEDIA`; timeline and videos; delete goes to "Recently deleted" for 30 days; an allowlisted picker serves Assistant only.
- **APP-21 MUST** Sharing (Photos, Journal, Notebook): preview with "Your grown-up will see this", 2 MiB at most, 20 per day, via `IZuneShare` (§4.5); nothing uploads unprompted; `caps.share=0` hides the button.
- **APP-22 MUST** Journal: title, text up to 5,000 characters, mood (5), one drawing, bundled stickers; Room plus SQLCipher (VP-5); private by default (not in the vault, no parent view or export); per-entry share only; optional child code, parent reset erases.
- **APP-23 MUST** Notebook: typed pages, Ink handwriting, sketch pages, checklists; PDF export only through APP-21; the "Draw" tile opens Notebook's sketch activity; Room plus SQLCipher metadata, Tink-encrypted stroke files.
- **APP-24 MUST** Clock: alarm, timer, stopwatch; alarms ring on a locked screen, in Doze, after reboot and in bedtime, are not capped by `vol_max`, Clock is never suspended by a time budget, and its alarm activity is in Guardian's lock-task allowlist (added to 03 LOCK-12); bundled sounds only.
- **APP-25 MUST** Calculator: four operations, percent, `BigDecimal`. Recorder: record, play, rename, delete, mono AAC up to 30 minutes, private files, microphone service started only while visible, stops at bedtime.
- **APP-26 MUST** The Reader and Settings tiles open `app.zune.reader` and ZuneSettings; Reader's shelf screen uses ZuneKit; the Parent area opens only through `ParentGate.confirm` (03 LOCK-16).

**Design and accessibility**
- **APP-27 MUST** ZuneKit (`libs/design`) uses Material 3 only as token carrier, ships its own components and band profiles (§4.1), and also serves Guardian's PIN, Emergency and approval screens (03); CI checks contrast 4.5:1 for text roles, 3:1 for outlines.
- **APP-28 MUST** Targets: 7-9 at least 64 dp (primary 72), 10-12 at least 56, 13-14 at least 48; system surfaces 56 for all bands; gaps 8 dp (12 at 7-9); a UI test fails smaller controls.
- **APP-29 MUST** Child strings read at Flesch-Kincaid grade 3 or lower, 10 words or fewer per sentence; `adult_` strings (Setup parent screens) grade 8 or lower; `tools/copy_lint.py` gates CI; the product name comes only from `@string/brand_name` (01 PRE-13).
- **APP-30 MUST** Every control has an icon, a visible label and semantics; layouts survive font scale 1.0 to 2.0 and largest display size; no colour-only state; no horizontal swipe control within 32 dp of a side edge; every swipe has a button; predictive back registered.
- **APP-31 MUST** Voice-first at age 7: a `ZHearIt` button beside child copy in Setup, Reader, Weather cards, Assistant answers and error states. `Speaker` (`libs/speech`, 07 §4.8) speaks only from a visible activity, obeys volume cap and bedtime, 0.9x rate at 7-9.
- **APP-32 MUST** Stage-1 accessibility set: font and display size, bold, contrast, colour correction and inversion, remove animations, mono audio, captions, flash alerts (02 Accessibility page). ADR `zune/docs/decisions/NNN-accessibility-stage1.md` records no TalkBack and no system TTS; all controls stay TalkBack-ready.
- **APP-33 MUST** No streaks, badges, rewards or come-back notifications; notifications are plain text without URLs (03 LOCK-29).

**Crash and quality**
- **APP-34 MUST** Crash reporting per §4.8: no exception messages, extras or logcat; upload only with consent `diagnostics`, counts otherwise.
- **APP-35 MUST** Tests per §4.9; the performance budgets of APT-14 hold on both Pixels.
- **APP-36 SHOULD** Per wave, panels of 6-8 children per band, parent present, written consent; gate 80% unaided completion on core tasks [R09 §4.4].
- **APP-37 MUST** Data migrations: Room, SQLCipher and DataStore schemas are exported and versioned; `MigrationTestHelper` tests cover every N-1 to N step with seeded data; destructive migration is forbidden for Photos, Journal and Notebook (APP-20, 22, 23); an update that cannot migrate keeps the old data, fails closed and reports through `ev.health`; the `apk` OTA test (04 AT-R09) runs N-1 to N with data present. A wipe or reflash still loses local data (disclosed, limitation 11 in 12).

## Design and build instructions

### 4.1 Repository, build modes, ZuneKit

```
zune/settings.gradle.kts  gradle/libs.versions.toml  build-logic/
zune/apps/{launcher,setup,settings,guardian,updater}      Tier A
zune/apps/{messenger,calls,walkie,assistant,videos,weather,photos,camera,journal,notebook,reader,clock,calculator,recorder}  Tier B (camera = library)
zune/libs/{core,design,speech,net,testing}   core = PolicyClient ParentGate IZuneShare IZuneDiag ZuneCrash ClaimCode TileRegistry
```
Mode G (default): `./gradlew assembleRelease` builds unsigned, R8-shrunk, 16 KB-aligned APKs (arm64-v8a; x86_64 for Cuttlefish); `zune/os/tools/pin_apps.sh` copies them to `vendor/zune/apps/prebuilt/` and writes SHA-256 `PINS` (02). Soong packages them:
```
android_app_import { name: "ZuneLauncher", apk: "prebuilt/ZuneLauncher/<vc>.apk", certificate: "platform",
  privileged: true, system_ext_specific: true, required: ["privapp-permissions-zune"] }   // Setup adds overrides: ["Provision"]
android_app_import { name: "ZunePhotos", apk: "prebuilt/ZunePhotos/<vc>.apk", certificate: "zune-apps", product_specific: true }
```
Dev builds sign with the throwaway `dev` keyset; `sign_target_files_apks` swaps keys at release (04). `apk` OTA entries (04 REL-23, its allowlist must list Tier B packages) carry Tier B updates signed offline with the `zune-apps` key. Guardian and Setup compile against system-API stubs; a Soong-native build of one Tier A app (hidden APIs) needs an ADR.

ZuneKit band profiles (hypotheses, VP-10):

| Token | 7-9 | 10-12 | 13-14 |
|---|---|---|---|
| Min / primary target | 64 / 72 dp | 56 / 64 | 48 / 56 |
| Gap, gutter, radius | 12, 20, 24 dp | 8, 16, 20 | 8, 16, 16 |
| Body, label, minimum text | 20, 18, 16 sp | 18, 16, 14 | 16, 14, 14 |
| Title, display | 28, 36 sp | 24, 32 | 22, 32 |
| Home columns | 2 | 3 | 4 |

Fonts: Lexend for UI, Andika for stories and Journal text (OFL, bundled). Colours light/dark (each with its on-colour measured at 4.5:1 or better, 2026-10-03; the CI test keeps it so): surface `#FFFBF5`/`#17140F`, onSurface `#1F1B16`/`#EDE6DA`, primary `#1F4FD8`/`#AFC3FF`, accent `#B84A00`/`#FFB787`, error `#B3261E`/`#F2B8B5`, outline `#7A7367`/`#9A9283`. Grid 4 dp; motion 150 and 250 ms, zero when animations are off; dark theme follows ZuneSettings Display. Components: `ZButton ZIconButton ZTile ZTopBar ZPinPad ZKeypad ZHearIt ZAskGrownUp ZShareSheet ZShelfRow ZInkCanvas`; the ink canvas keeps 24 dp margins.

### 4.2 Policy additions and Home

Requested `policy-v1` additions (owner 03; 05 generates types; absent cap means off, 03 LOCK-13):
```json
"child":{"name":"Asha","av":"av_07"},
"home":{"v":1,"tiles":["chat","call","walkie","ask","watch","books","weather","camera","photos","draw","journal","notebook","clock","calculator","recorder","settings"]},
"caps":{"diag":1,"camera":1,"photos":1,"journal":1,"notebook":1,"clock":1,"calculator":1,"recorder":1,"share":1,"reader":1,"weather":1,"assistant":1,"walkie":1}
```
`TileRegistry` (compile-time, `libs/core`) maps tile id to the main activity of `app.zune.<id>` and cap `<id>`, except: `chat` to messenger, `call` to calls (cap `voice` or `video`), `ask` to assistant, `watch` to videos, `books` to reader, `camera` and `photos` to `app.zune.photos` (`.camera.CameraActivity`, `.gallery.GalleryActivity`), `draw` to `app.zune.notebook/.SketchActivity`, `settings` always shown. Unknown ids are ignored. Parents edit order and visibility in a portal page `/children/{c}/home` (05 to add).

Verdict: HIDDEN if cap absent or 0; LOCKED_TIME if the budget is spent or bedtime; LOCKED_ASK if the package is blocked; else SHOWN. Band default for `templates/band-*.yaml`: the tiles above in four groups (Talk, Learn, Make, Tools), columns by band.
```kotlin
class HomeViewModel(policy: PolicyClient, weather: WeatherTileSource) {
  val tiles = policy.changes()                               // Binder listener, replay 1
    .map { TileRegistry.resolve(it.home, it.caps, it.apps) }  // -> List<TileUi(state)>
    .catch { emit(FailClosed.tiles) }                         // Emergency, Settings, Ask a grown-up
}
```
`HomeActivity` has `MAIN`, `HOME`, `DEFAULT`, `launchMode=singleTask`, `taskAffinity=""`, `stateNotNeeded`; Guardian sets the HOME role (02 OS-24).

### 4.3 ZuneSetup sequence

Base: copy GrapheneOS `SetupWizard2` (MIT, keep notices, `overrides: ["Provision"]` and finish writes), replace its screens with Compose (VP-9). State `WELCOME, GESTURES, NET, PAIR, CONFIRM, PROVISION, PIN, APPLY, NOTICE, DONE` persists in DataStore.

| Step | Screen and mechanism |
|---|---|
| 1 | Welcome, adult voice, Emergency |
| 2 | Gesture tutorial (02 OS-23): Back via `OnBackInvokedCallback`; Home via `onNewIntent(HOME)` from a practice task; Recents confirmed by a grown-up tap (VP-3) |
| 3 | Wi-Fi via `android.settings.SETUP_INTERNET` [R16 F11]; note "Wi-Fi with a sign-in page does not work. Use a phone hotspot" (D30); skip only with mobile data |
| 4 | Pair: CameraX frames to ZXing core (VP-11), or keypad; Guardian runs `enroll/begin` (05 §4.3) |
| 5 | Confirm "This phone is for <name>" from the verified bundle |
| 6 | PROVISION: Device Owner and roles (03 §4.2, VG-1) |
| 7 | PIN twice (APP-14) |
| 8 | APPLY: claim blob, restrictions, grants, HOME role; Guardian completes enrolment |
| 9 | Child notice cards (grown-ups can see chats; how to ask; Emergency), button "Got it" |
| 10 | `user_setup_complete=1`; Home; content essentials keep downloading (08 CNT-05) |

After a wipe the flow restarts with "This phone was reset. Ask a grown-up in the family for a new code" (03 LOCK-18).

### 4.4 Camera and Photos

`filesDir/photos/<yyyy>/<uuid>.jpg|mp4`, with a Room index (`kind`, `path`, `taken_at`, `deleted_at`, `shared_at`). CameraX `OutputFileOptions` never sets location; a save pass keeps only orientation. Manifest: `CAMERA`, `RECORD_AUDIO` (video), no location, no `INTERNET`. Picker `app.zune.photos.PICK_FOR_ASSISTANT` returns one `content://app.zune.photos.picker/<token>` with `FLAG_GRANT_READ_URI_PERMISSION`, valid 60 s, only to the Assistant package.

### 4.5 Sharing pipeline

```aidl
interface IZuneShare {
  String submit(String kind, in ParcelFileDescriptor payload, String mime, String label); // photo|journal|note
  int status(String shareId);     // 0 queued, 1 sent, 2 failed, 3 refused
  void cancel(String shareId);    // before sent
}
```
Guardian checks caller-kind pairing, size, `caps.share`, 20 per day, then `POST /v1/device/shares` (mTLS) storing vault class `share` for 12 months (05 BE-31, BE-32) under consent purpose `visibility`. The portal lists shares at `/children/{c}/shared` with an audited read (BE-33).

### 4.6 Journal, Notebook, Clock, Recorder

Database key: 32 random bytes wrapped by a non-exportable Keystore AES-GCM key (StrongBox if present), opened through SQLCipher `SupportOpenHelperFactory`. Notebook strokes: Ink serialisation into Tink StreamingAead files under the same master key. Child code: HMAC verifier, 5 tries then 30 s doubling. A wipe or reflash erases Journal, Notebook and Photos; disclose at hand-over (10). Clock uses `AlarmManager.setAlarmClock`, a Direct-Boot-aware boot receiver and a show-when-locked `RingActivity` (VP-7).

### 4.7 Accessibility decision

Gap: no screen reader and no system `TextToSpeech` engine in Stage 1; duties for a software seller are a counsel question (11, R16 F10). Mitigation: in-app `Speaker`, full semantics, ATF checks. Stage 2: build TalkBack from `google/talkback` (Apache-2.0) and add a TTS service on `libs/speech`; GrapheneOS prebuilts are not reused (model licence unread).

### 4.8 Crash and diagnostics

```kotlin
// ZuneCrash.install(app): UncaughtExceptionHandler -> noBackupFilesDir/crash-<n>.json, ring of 5, 8 KB each
{"v":1,"pkg":"app.zune.journal","vc":104,"os":"<Build.ID>","model":"stallion","hour":492000,
 "exc":[{"cls":"java.lang.IllegalStateException","frames":[{"c":"...","m":"...","l":42}]}]}   // never message, cause message, extras
```
On next start the app reads its own `ApplicationExitInfo` and calls `IZuneDiag.counts(pkg, crash, anr, native, lowmem)`; Guardian forwards counts in `ev.health`. If policy `caps.diag=1` (set only with consent `diagnostics`, BE-30), `IZuneDiag.submit(json)` follows; Guardian uploads at most 20 a day to `POST /v1/device/diag`; the server groups by `sha256(top 5 frames)` into `ops.crash`, purged at 30 days [default], staff console only. No install id. No product analytics on device: usage minutes come from Guardian `ev.usage` only.

### 4.9 Tests

JUnit4 with Robolectric (sdk 37), Compose `ui-test`, Roborazzi goldens per band at font scale 1.0 and 2.0 in light and dark, ATF checks, Macrobenchmark with baseline profiles on dev Pixels (userdebug), Cuttlefish `connectedAndroidTest` on `zune_kids_cf-aosp_current-userdebug` per merge, and a rack of 6-10 phones [R09 §4.4].

### 4.10 Effort and order (person-weeks [INFERRED]; re-baseline at M1 exit, 01 PRE-16 and Verify 13)

| Wave | Weeks (01) | Work | pw |
|---|---|---|---|
| 0 | W1-W5 (M1) | Gradle, `libs/core`, ZuneKit v0, lint, APK-to-PINS-to-Cuttlefish CI, VP-1 and VP-3 spikes | 8 |
| 1 | W8-W20 (M3) | ZuneLauncher 5, ZuneSetup 4 (mock pairing, real at M4) | 9 |
| 2 | W10-W24 | Photos with Camera 8, Journal 6, Notebook 6, Clock 2, Calculator and Recorder 2.5 | 24.5 |
| 3 | W14-W30 (M5) | Sharing client 1.5, crash and diag 1, entries 0.5, hardening, accessibility, panels 12 | 15 |

Total 56.5 (Wave 0's 8 covers ZuneKit v0 and v1). Assistant UI, Walkie UI, Videos UI and Reader (about 20) are costed in 06, 07, 08.

## Acceptance criteria and tests

- **APT-01** A clean checkout builds all APKs; `pin_apps.sh` writes `PINS`; `zune_kids_cf` boots with them and `image_diff` (02 AT-02) passes.
- **APT-02** One seeded violation per APP-04 rule fails CI; `aapt2 dump permissions` shows `INTERNET` only in the five holders.
- **APT-03** NAV-1..8 pass with the real launcher; Back does nothing on Home; a policy change shows in 1 s; killing Guardian gives the fail-closed Home.
- **APT-04** A parameterised test over absent, off, allowed, limit-spent, bedtime and blocked states gives the §4.2 verdicts; a locked tile makes one portal approval, the sixth is refused.
- **APT-05** Setup completes on Cuttlefish (`DEVMOCK`) and on a Pixel with the real portal; killing the process at each step resumes; injected failure shows Retry and Erase; `http://x`, a wrong-length `ZUNE1:` and a 2 KB payload are rejected; `dumpsys window` never lists a permission dialog; the `user` APK lacks `DEVMOCK`.
- **APT-06** `exiftool` shows no GPS in captures; secure camera opens over the lock screen; capture is refused under 500 MB.
- **APT-07** A MediaStore query lists none of the app's files; trash and 30-day purge work (clock hook); the allowlisted picker caller reads once, any other gets `SecurityException`.
- **APT-08** Share sends only after confirmation; the 21st in a day, a payload over 2 MiB and `caps.share=0` are refused; the portal shows an audited read (05 BT-07).
- **APT-09** `strings` on the Journal file finds no sample text; entries survive process death; wrong-code lockout works; PDF leaves only via sharing.
- **APT-10** Alarms ring locked, in Doze, after reboot, in bedtime and with Clock's budget spent. Recorder stops at bedtime; `0.1+0.2` shows `0.3`.
- **APT-11** Goldens show no clipped text; target-size, contrast, copy-lint and ATF checks pass.
- **APT-12** An exception with message `SECRET-123` yields a report without it; no consent uploads counts only; with consent one grouped row appears; the 21st upload that day is dropped.
- **APT-13** Panels meet APP-36 for: open chat, take and find a photo, set an alarm, ask for time, find Emergency (`zune/docs/lab/usability-<wave>.md`).
- **APT-14** [default] Home cold start p90 at most 800 ms, warm 300 ms; Camera preview within 1.2 s; shutter to saved 1.5 s p95; at most 5% janky frames; final numbers set at M1.
- **APT-15** `MigrationTestHelper` N-1 to N passes for every database with seeded Journal, Notebook and Photos data; a failing migration keeps the old file and reports a health event (APP-37).

## Verify first

| ID | Claim | Why uncertain | How to verify | If false |
|---|---|---|---|---|
| VP-1 | Gradle APKs imported with `certificate: "platform"` or `"zune-apps"`, `privileged`, `overrides` are re-signed by `sign_target_files_apks`; an `apk` update signed with the prod `zune-apps` key replaces the system copy (03 VG-7); Guardian and Setup need only system-API stubs, not hidden `setDeviceOwner` [R09 F3, 02 V12] | GrapheneOS tree only | M1 stub APK on Cuttlefish: key-map run, `pm install -r`, compile Setup against stubs | `presigned: true` with offline signing; Soong-native or framework-jar build for that app by ADR |
| VP-2 | A `signature` permission does not reach `zune-apps` apps; `knownSigner` with `knownCerts` may [M] | Memory | M3 stub client | APP-06 caller check alone |
| VP-3 | Stock Quickstep with ZuneLauncher gives working gestures (02 V5); Setup detects Back and Home as in §4.3 | Memory | Stub in M1, real in M3 (AT-06) | Path B (Launcher3-derived), about 5-8 pw more [INFERRED], escalate; tutorial uses taps |
| VP-4 | Ink 1.0.0, CameraX 1.6.2, Media3 1.11.1, Room 2.8.5, Readium 3.4.0 are current, GMS-free, 16 KB-aligned; Robolectric and Roborazzi run on sdk 37 [R09 F4-F6] | Doc summaries | `./gradlew dependencies`, grep, `check_elf_alignment.sh`, an sdk-37 test | Pin newest working; Ink to Compose Canvas (about 2 pw) |
| VP-5 | SQLCipher works with Room 2.8.x on API 37, 16 KB aligned, redistribution allowed [R09 F5, M] | Licence unread | Sample DB; read licence | Plain Room plus Tink field encryption |
| VP-6 | `default-permissions-zune.xml` grants CAMERA, RECORD_AUDIO, POST_NOTIFICATIONS to product system apps without dialogs; Guardian can revoke [R03 F8, M] | Unproven | Cuttlefish `dumpsys package`; toggle caps | `GRANT_RUNTIME_PERMISSIONS` from Guardian; DO limits on sensors [M] |
| VP-7 | A non-privileged product app shows an alarm over the keyguard (`USE_EXACT_ALARM`, `USE_FULL_SCREEN_INTENT`) and re-arms in Direct Boot [M] | Memory | Locked, Doze, reboot tests | Clock becomes privileged, or Guardian starts the activity |
| VP-8 | A suspended package's provider is unreachable from other apps; CameraX writes no GPS without location; `STILL_IMAGE_CAMERA_SECURE` shows over the keyguard [M] | Memory | Suspend and query; `exiftool`; lock-screen test | Cache last values (Clock exempt, APP-24); strip with `ExifInterface` |
| VP-9 | SetupWizard2 is MIT, overrides `Provision`, writes the provisioned flags, launches stock `SETUP_INTERNET` [R09 F3, R16 F11] | Mirror read | Read repo at the pinned commit | Own `Provision`, about 2 pw |
| VP-10 | Targets 64/56/48, type sizes, grade 3, Home columns and a 10-minute setup suit ages 7-14 [R09, R16: INFERRED] | No child data | Panels, 6-8 per band | Edit the band profile; rerun APT-11 |
| VP-11 | ZXing core decodes QR without GMS; Lexend, Andika, OpenDyslexic OFL allow bundling [R09 F8] | Licences unread | Unit test; read licences | ZXing-cpp via NDK; swap fonts |

## Risks, open gates and out of scope

- **Gesture navigation** depends on VP-3 (02 §7). [GATE: before staff pilot] the real launcher passes AT-06 or the founder accepts three-button.
- **Mode G** moves Tier A off the Soong build; 01, 02 and 03 now adopt it (the in-tree build is the ADR fallback). [GATE: before build] VP-1 and VP-2 recorded in `verified-facts.md`.
- **Kid-UX values** are untested; a kid-UX designer is required (01 §4.4). [GATE: before staff pilot] panel results for band 7-9.
- **Accessibility without TalkBack and TTS** may be launch-gating. [GATE: before external family] counsel's written view (11) and the ADR. [GATE: before charging] revisit if gating.
- **Sharing and diagnostics** add data classes (`share`, `ops.crash`) and consent wording. [GATE: before external family] counsel confirms retention (LEG-1).
- **Data loss on wipe or reflash** for Journal, Notebook and Photos is disclosed in Stage 1.

Out of scope (Stage 2): automatic encrypted backup, on-device Home editing, handwriting recognition, TalkBack and TTS service, music, planner, dictionary, games, coding, "where is mom" (D31), on-device LLM, Indic and Spanish UI (D20).
