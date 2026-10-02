# 09 - First-party app suite: stack, in-tree vs APK, per-app design

Status 2026-10-02. Tags: **[P]** read in a real file or primary page this session; **[S]** official page read through a summarising fetch tool; **[I]** engineering inference; **[M]** training memory, unchecked. Android 17 facts come from the GrapheneOS `17` and LineageOS `lineage-24.0` trees (the latter pins `android-17.0.0_r1`), because googlesource is blocked. The search budget ran out and the book-source sites were egress-blocked, so their licences are **[M]**. Keys (all under `raw.githubusercontent.com`): S1 `GrapheneOS/platform_manifest/17/default.xml`; S2 `LineageOS/android/lineage-24.0/default.xml`; S3 `readium/kotlin-toolkit/develop/<path>`; S4 `GrapheneOS/platform_build_soong/17/java/app_import.go`.

## 1. Summary & recommendation

1. **Two tiers.** *Tier A*, at most six OS-coupled components built in-tree with Soong and the platform key: ZuneSetup, ZuneGuardian + ZunePolicyService (05), ZuneUpdater, ZuneComms (13), ZuneHome. *Tier B*, every other app, built in a Gradle monorepo, signed with a separate `zune-apps` key, imported with `android_app_import` onto `/product`, and updated silently by ZuneUpdater. No store UI, ever.
2. **One UI stack**: Kotlin, Compose, a custom kid design system (ZuneKit, Material 3 foundations, three age-band profiles), Hilt, Room, `minSdk = targetSdk = 37`. Android 17 is the only OS, so there are no compat shims.
3. **Launcher from scratch in Compose**, not a Launcher3 or Lawnchair fork (3-button navigation, fixed parent-curated grid; report 03).
4. **Camera**: new CameraX app using GrapheneOS Camera (MIT) as reference. **Photos**: MediaStore-based, own app. **Notebook**: Jetpack Ink 1.0.
5. **EPUB**: Readium Kotlin Toolkit (BSD-3, WebView-based), with **no INTERNET permission** on the Reader; downloads go through ZuneComms. Reject KOReader/crengine/FBReader/Librera: copyleft, and no fixed-layout support [I].
6. **Egress consolidation**: only apps that talk to a Zune backend (Assistant, Walkie, Videos, Setup, Updater) and ZuneComms/Guardian hold INTERNET; Reader, Camera, Photos, Journal, Notebook and utilities hold none. WebView exists only in Reader and Videos (matches 04).
7. **Cost**: about 62 person-weeks (pw) for the Stage-1 apps here plus about 18 pw test/accessibility/usability, roughly 80 pw: 5 Android engineers for 16-20 weeks beside the platform track. Phone, Messenger, Video call, Weather and Settings are costed in 12, 13, 14, 16.

## 2. Findings

**F1. AOSP 17 still carries legacy apps but is missing what a kid OS needs.** `lineage-24.0` (pinned `android-17.0.0_r1`) pulls `packages/apps/Camera2`, `Browser2`, `QuickSearchBox`, `Music` and `external/jetpack-camera-app` from AOSP [P: S2]. GrapheneOS 17 hosts forks of `Gallery2`, `Contacts`, `Calendar`, `Launcher3`, plus `DeskClock` and `ExactCalculator`, and has dropped Camera2, Browser2 and QuickSearchBox [P: S1]. **No TTS or speech-recognition project exists** in either manifest [P: S1, S2; report 07]. Camera2 is legacy by inference: GrapheneOS wrote a CameraX app that "replaces AOSP Camera" [P: GrapheneOS/Camera README] [I].

**F2. Soong can build Compose; Maven-heavy apps still want Gradle.** The tree ships `external/kotlinc`, `kotlin-compose-compiler`, `kotlinx.serialization`, `dagger2`, `tink`, `robolectric`, `accessibility-test-framework`, and SystemUI links `androidx.compose.material3_material3` [P: S1; SystemUI/Android.bp@17]. Readium, Media3, Coil, SQLCipher, Ink and LiveKit are absent [P: S1 grep].

**F3. `android_app_import` fits Tier B.** Properties: `apk`, `certificate`, `presigned`, `preprocessed`, `privileged`, `overrides`, `lineage` (signing-key rotation), `product_specific` [P: S4]. GrapheneOS ships Camera and PdfViewer exactly this way (`product_specific`, `preprocessed`) [P: platform_external_Camera/17/Android.bp]. GrapheneOS SetupWizard2 is the Tier A precedent: `certificate: "platform"`, `privileged`, `system_ext_specific`, `platform_apis`, `overrides: ["Provision"]`, MIT licence [P: platform_packages_apps_SetupWizard2/17].

**F4. No GMS dependency in the core Jetpack pieces.** `work-runtime` and `camera-core`/`camera-camera2` `build.gradle` list no play-services, gcm or firebase dependency; WorkManager's `Schedulers` builds a `SystemJobScheduler` [P: androidx@androidx-main]. Media3 lists Play services as optional only [S: developer.android.com/jetpack/androidx/releases/media3]. Jetpack Camera App (Apache-2.0, in AOSP) is CameraX + Compose but has optional Play-services low-light modules [P: google/jetpack-camera-app app/build.gradle.kts].

**F5. Versions today [S: developer.android.com/jetpack/androidx/releases/{ink,camera,media3,room,security}].** Ink 1.0.0 stable (2025-12-17, native JNI; 1.1.0-alpha09 pre-release), CameraX 1.6.2 (2026-08-26), Media3 1.11.1 (2026-09-10), Room 2.8.5 (Room 3 is alpha: avoid). `security-crypto` is deprecated for direct Keystore or Tink. SQLCipher-for-Android works with Room 2 via `SupportOpenHelperFactory` [P: sqlcipher-android README]. Robolectric master supports API 37 [P: robolectric README].

**F6. Readium Kotlin Toolkit 3.4.0 (2026-09-11)**, BSD-3, minSdk 24, EPUB 2/3 reflowable and fixed-layout, RTL, search, decorations, TTS, OPDS 1.2/2.0, PDF, audiobooks [P: S3 LICENSE, CHANGELOG, README]. The EPUB navigator is an Android `WebView` that intercepts every navigation (`shouldOverrideUrlLoading`) and serves resources in-process via `shouldInterceptRequest` [P: S3 `EpubNavigatorFragment.kt`], so a no-INTERNET Reader is plausible [I]. The Compose "web navigators" are experimental [P: S3 docs]. Embedded fonts: OpenDyslexic, AccessibleDfA, iA Writer Duospace [P: S3 `epub-fonts.md`]. TTS defaults to Android's engine but "can be extended to use a different TTS engine"; the default path can open a voice-install flow (`requestInstallVoice`) [P: S3 `tts.md`]. LCP needs EDRLab's private `liblcp` [P: S3 `lcp.md`] and a user passphrase, which the app would supply programmatically [I].

**F7. Alternatives.** KOReader is AGPL-3.0, CoolReader/crengine GPL-2.0, Librera bundles AGPL MuPDF [P: COPYING/LICENSE/README]. FBReader is GPL and Moon+ proprietary [M, repo unreachable]. Lawnchair is Apache-2.0 but based on Launcher3 from **Android 16** [P: README, LICENSE.txt]. Launcher3's `Android.bp` defines five `android_app` variants and a feature-flag library [P: Launcher3/Android.bp@17].

**F8. Other licences [P].** Sentry self-hosted FSL-1.1-Apache-2.0; `sentry-java` MIT; ACRA Apache-2.0; PostHog MIT outside `ee/`. ScratchJr is BSD-style but its editor is shared JavaScript and its README expects Firebase `google-services.json`. Lexend, Andika, Atkinson Hyperlegible are SIL OFL 1.1 (google/fonts). Standard Ebooks: believed US public domain, contributions CC0, "check local law" elsewhere (an ebook repo's `LICENSE.md`).

**F9. Book sources [M, unverified]:** Project Gutenberg (US public domain; trademark and licence text need care); StoryWeaver, African Storybook, Global Digital Library (mostly CC BY, levelled); OpenStax (CC BY, older kids); Internet Archive (mixed; lending items not licensable). No universal e-book age rating exists; use publisher metadata (Thema age qualifiers) plus our own band and level [M/I].

**F10. Inherited constraints.** 03: Gradle prebuilts, 3-button navigation, recents stub. 04: WebView allowlist, no-INTERNET EPUB. 05: ZuneSetup does QR pairing, Guardian + `ZunePolicyService` hold policy. 07: sherpa-onnx STT/TTS. 13: LiveKit client in the visible Walkie app. 14: Home tile is a signed ContentProvider. 12: no Contacts UI. 16: no TalkBack in AOSP.

## 3. Options & trade-offs

| Delivery | Updates | Privilege | Risk | Test loop | Verdict |
|---|---|---|---|---|---|
| A. Soong, platform key | OTA only | Full | One key signs everything | Needs AOSP build | Six OS-coupled components only |
| **B. Gradle, own key, `android_app_import`** | Independent, same-key silent update | Normal, or priv-app via allowlist | Separate key plus `lineage` rotation | Any Android 17 emulator/Cuttlefish | **Default** |
| C. In-product store | Fastest | None | Adds an installer UI to break out of | n/a | Reject |

| EPUB engine | Licence | WebView | Fixed layout | Verdict |
|---|---|---|---|---|
| **Readium Kotlin** | BSD-3 | Yes | Yes | **Choose**; harden |
| KOReader / crengine | AGPL / GPL-2 | No | No [I] | Reject: copyleft |
| FBReader, Librera, Moon+ | GPL, AGPL parts, proprietary | n/a | n/a | Reject |
| Own native renderer | ours | No | Hard | About 12 pw [I]; only if WebView is banned |

| Launcher | Cost | Verdict |
|---|---|---|
| **Compose ZuneHome** | 5 pw | Choose |
| Fork Launcher3 | rebase every Q2/Q4 drop, 5 variants, Quickstep | Reject |
| Fork Lawnchair | Android 16 base | Reject |

## 4. Recommended design for Zune

### 4.1 App suite, priority and Stage-1 scope

| App | Tier | Pri | Stage-1 MVP | pw |
|---|---|---|---|---|
| zune-core, ZuneKit, CI pipeline | n/a | 1 | see 4.2 | 8 |
| ZuneHome | A | 1 | HOME role, approved-app grid, tile providers, status strip, bedtime screen, flashlight toggle, parent-locked edit | 5 |
| ZuneSetup | A | 1 | Fork SetupWizard2: language, Wi-Fi via stock `SETUP_INTERNET`, SIM, QR pairing (05), age band, kid name/avatar | 4 |
| Camera | B | 1 | CameraX photo/video, selfie, big shutter, no geotags (never request location), quota and schedule from policy | 4 |
| Photos | B | 1 | MediaStore grid, albums, delete to trash, "send to parent" (explicit); no cloud by default | 4 |
| Journal | B | 1 | Text, drawing, stickers, voice note, mood; Room + SQLCipher; modes private / child-shares / parent-visible; parent-triggered encrypted export | 6 |
| Notebook | B | 1 | Typed + Ink handwriting, sketch pages, checklists, `PdfDocument` export to parent only | 6 |
| Reader | B | 1 | See 4.3 | 6 |
| Assistant UI | B | 1 | Chat bubbles, push-to-talk, read-aloud, image attach (EXIF stripped), plain text only, no links | 6 |
| Walkie UI | B | 1 | One hold-to-talk button, contact tiles, haptics, schedule banner (backend: 13) | 3 |
| Videos UI | B | 1 | Topic shelves, offline Media3 player (06 Tier 1), IFrame wrapper (06 Tier 2), kill switch | 5 |
| Clock/alarm/timer | B | 1 | Alarm, timer, stopwatch, bedtime link | 2 |
| Calculator, Voice recorder | B | 1 | Four-op; record/play/rename | 2.5 |
| **Stage-1 total** | | | | **61.5** |
| Music (offline), Homework planner, Dictionary, 3-5 curated offline games, Family album, Journal auto-backup, Spanish | B | v1.1 | about 20 pw | 20 |
| "Where's mom" location, coding (ScratchJr-style), handwriting recognition, TalkBack bundling, on-device LLM | B | Later | Location needs consent and has no network provider (14); coding needs a third WebView exception; ML Kit digital ink needs GMS [I] | n/a |

Not built: file manager (DocumentsUI hidden), Contacts UI (portal-driven, 12).

### 4.2 Stack and repo layout

- **Monorepo**: `apps/*` (one Gradle module each), `libs/{core,design,speech,net,testing}`, `backend/*` (Go, 13), `os/{device,vendor,manifests,sepolicy}`. Gradle outputs land in `vendor/zune/apps/prebuilt/` (SHA-pinned, as 03).
- **`zune-core`**: binder client to `ZunePolicyService` (apps never decide policy from the network), parent-gate request, attested HTTP client (OkHttp 5 + kotlinx.serialization, TLS pinned, no cleartext), Keystore key helpers (Tink/Keystore, not `security-crypto`), crash/telemetry facade, an **egress lint** that fails CI on `android.webkit.*`, `ACTION_VIEW` of http(s), or INTERNET outside the allowlist.
- **Libraries**: Compose + Material 3, Hilt, Coil 3, Room 2.8 + SQLCipher (Journal, Notebook; other apps rely on file-based encryption), Media3, CameraX 1.6, Ink 1.0, Readium 3.4, LiveKit, sherpa-onnx. WorkManager only inside ZuneComms. No gRPC on device (13 uses REST + WebSocket).
- **Soong for Tier A**, `sdk_version: system_current` unless a hidden API forces `platform_apis`, because each `platform_apis` app can break at every Q2/Q4 rebase [I].
- **Privileges**: Tier B apps are non-priv (`untrusted_app` domain [M]) unless an allowlisted `signature|privileged` permission is needed; each priv-app needs a `privapp-permissions` entry, and a missing entry can stop boot, so CI boots Cuttlefish on every change [M].
- **GMS replacements**:

| GMS-bound item | Replacement |
|---|---|
| Firebase Crashlytics/Analytics/FCM/Remote Config | Sentry SDK (MIT) to GlitchTip [M] or Sentry (FSL), scrubbed; push over the ZuneComms socket; config in signed policy |
| Play Services Location | Platform `LocationManager` (GNSS only) |
| ML Kit (incl. `camera-mlkit-vision`) | Bundled LiteRT models, none in v1 |
| Maps SDK, Credential Manager, Play Integrity | MapLibre later; none; key attestation via Guardian (05) |
| Downloadable fonts | Bundled OFL fonts (Lexend, Andika, OpenDyslexic) |
| TextToSpeech / SpeechRecognizer | sherpa-onnx engine (07) |

- **Child-data minimisation [I; counsel to confirm]**: no analytics SDK on device; server-side aggregates; crash payload limited to stack, app version, OS build, device model; random per-install id reset on wipe; IP dropped at ingress; 30-day retention; PostHog only for the parent portal.
- **Design system**: three age-band profiles (about 4-6, 7-9, 10-12, as 07) set text scale, minimum target (suggest 64/56/48 dp, to validate), vocabulary and navigation depth. RTL-ready; English at launch. Semantics on every control, ATF checks in UI tests.

### 4.3 EPUB reader and library

- **Reader**: Readium legacy `EpubNavigatorFragment` hosted in Compose (stable path; web navigators are experimental). Reflowable + fixed-layout (most picture books), themes, font size, line spacing, three dyslexia-friendly fonts, read-aloud with sentence highlight through Readium's pluggable TTS engine backed by sherpa-onnx, bookmarks, progress, tap-image zoom. All external links are swallowed. Never use the default Android TTS voice-install flow (breakout) [P: `tts.md`].
- **No INTERNET in Reader**: ZuneComms downloads books and syncs `Locator` JSON progress (last-write-wins), exposing files through a signature-protected provider [I].
- **Library**: curated catalogue on our server and CDN, served as OPDS 2.0 filtered by family; the device never contacts Gutenberg or others. Each title carries source, licence, attribution, age band, our reading level, content flags, parent approval. Launch with Standard Ebooks and Gutenberg classics (US only, editorially screened), then CC BY collections with attribution; commercial titles via LCP in Stage 2.
- **v1.1**: tap-to-define (offline dictionary), highlights kept private, reading-time stats to the portal.

### 4.4 Testing

Robolectric (API 37) and Compose UI tests per module; screenshot tests per age band (Roborazzi/Paparazzi [M]); ATF accessibility checks; Macrobenchmark and baseline profiles on the target phones. **Cuttlefish** (Debian packages, KVM, x86/arm64, GCE [P: android-cuttlefish README]) boots our image in CI and runs `connectedAndroidTest` for priv-app, policy and egress tests. Firebase Test Lab cannot flash our OS, so keep an in-house rack of 6-10 real phones. **Kid usability**: each wave, 6-8 children per age band, moderated play tests with a parent present and written consent, tasks framed as missions; measure unaided completion, time, mis-taps, target-size variants; gate at about 80% unaided completion on core tasks [I].

### 4.5 Sequence

Wave 0 (weeks 0-4): zune-core, ZuneKit, Gradle-to-prebuilt-to-Cuttlefish pipeline, ZuneHome skeleton, ZuneSetup fork. Wave 1 (4-12): Camera, Photos, Notebook, Journal, Reader, Clock, Calculator, Recorder (device-local). Wave 2 (8-18): Assistant, Walkie, Videos on the 07/13/06 backends. Wave 3 (16-24): hardening, usability, accessibility, performance. **Reuse**: Readium, CameraX, Ink, Media3, sherpa-onnx, LiveKit, SQLCipher, Sentry/GlitchTip. **Build**: all UI, ZuneKit, catalogue tooling. **Buy**: illustration, sticker and sound packs; EDRLab LCP in Stage 2.

## 5. Risks & unknowns

- Readium inherits the WebView (04); 3.x navigators have churned, so pin versions and budget 1 pw per upgrade.
- Re-flash or repair (D16) wipes a private Journal; Stage 1 has a parent-triggered encrypted export, automatic backup is v1.1.
- Public-domain classics carry dated content; editorial review is a recurring cost.
- Camera quality and vendor extensions vary by Snapdragon HAL; test per device (GrapheneOS Camera marks extensions optional [P]).
- Unverified: Camera2 upkeep in AOSP 17, FBReader/Moon+ licences, book-source licences, LCP fees, `preprocessed` + dexpreopt, per-app SELinux domains.
- Ink 1.1 is alpha; no handwriting recognition without GMS. Counsel must confirm COPPA treatment of crash identifiers and photos.

## 6. Decisions needed from the founder

1. Journal default: private-to-child with opt-in sharing (recommended), or parent-visible.
2. Confirm the Stage-1 utility set and defer "where's mom" and coding.
3. Reader content at launch: public-domain and CC only (recommended), or fund publisher deals and LCP now.
4. Accept WebView in exactly two apps (Reader, Videos).
5. Age range and bands (youngest supported age drives handwriting, target sizes, voice-first design).
6. Launch languages: English only, or add Spanish in v1.1.
7. Crash reporting host: managed Sentry (US) vs self-hosted GlitchTip/Sentry.
8. Headcount: kid-UX designer and a content editor are required, not optional.

## 7. Load-bearing claims

| # | Claim | Basis | Source |
|---|---|---|---|
| 1 | Readium Kotlin 3.4.0 is BSD-3, supports reflowable and fixed-layout EPUB, TTS, OPDS, LCP, minSdk 24 | P | S3 LICENSE, README, CHANGELOG |
| 2 | Its EPUB navigator is a WebView with in-process resource serving and navigation interception | P | S3 `EpubNavigatorFragment.kt` |
| 3 | `android_app_import` supports presigned, certificate, privileged, preprocessed, lineage; GrapheneOS ships Camera this way | P | S4; platform_external_Camera/17/Android.bp |
| 4 | SetupWizard2 (MIT) is a platform-signed priv-app that overrides Provision | P | platform_packages_apps_SetupWizard2/17/Android.bp, LICENSE |
| 5 | WorkManager and CameraX core have no GMS dependency | P | androidx-main `build.gradle` files |
| 6 | AOSP 17 (`lineage-24.0` pin) still contains Camera2, Browser2, jetpack-camera-app; neither manifest has a TTS or speech engine | P | S2, S1 |
| 7 | Ink 1.0.0 stable, CameraX 1.6.2, Media3 1.11.1, Room 2.8.5; `security-crypto` deprecated | S | developer.android.com releases pages |
| 8 | KOReader AGPL-3.0, CoolReader GPL-2.0, Librera bundles AGPL MuPDF | P | repo COPYING/LICENSE/README |
| 9 | Lawnchair is Apache-2.0 but tracks Launcher3 from Android 16 | P | Lawnchair README, LICENSE.txt |
| 10 | Robolectric supports API 37 | P | robolectric README |
