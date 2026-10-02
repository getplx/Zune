# Zune — Handoff: conversation 1 (research) → conversation 2 (AOSP-connected)

Written 2026-10-02 by the research session. **Read this first**, then `docs/REQUIREMENTS.md`
(authoritative founder decisions), then the reports in `docs/research/`.

## 1. What this project is

A custom **kids-only Android 17 (AOSP) OS image**, sold as a product: clean minimal build, custom
first-party apps only, **no browser, no way to reach YouTube**, parents manage everything from a
**browser-based portal**. Features: cellular calls + SMS (parent-controlled number allowlists, SMS
readable only by parents), 1:1 kid messenger (text + emoji, no groups), 1:1 video calling with
approved people, walkie-talkie, AI assistant (chat UI, image input), curated educational videos
(from YouTube, shown only inside our app), weather with lessons, camera, photos, journal, notebook,
EPUB reader. Stage 1 = everything exists in simplest form; Stage 2 = make it better.

## 2. Why there is a second conversation

Conversation 1's container could **not** reach `android.googlesource.com`, `source.android.com`,
`dl.google.com` (egress policy, HTTP 403), and the founder could not change that setting. So all
AOSP facts so far come from GitHub mirrors (GrapheneOS `17` branch, LineageOS `lineage-24.0`) and
web search, **not from Google's own android-17.0.0_r1 tree**. Conversation 2 must run on a container
that can reach AOSP, and re-check everything that matters against primary sources.

### Start-up checklist for conversation 2
1. **Environment:** Network access must allow `android.googlesource.com`, `source.android.com`,
   `dl.google.com`, `developers.google.com` (Pixel image licence text), and optionally
   `gerrit.googlesource.com` (the `repo` tool's own source; or use
   `--repo-url https://github.com/GerritCodeReview/git-repo`). Already reachable in conv. 1:
   github.com (git clone), raw.githubusercontent.com, developer.android.com, maven.google.com,
   services.gradle.org, repo.maven.apache.org, storage.googleapis.com (repo launcher).
2. **Repo:** attach `getplx/Zune`; use branch `research/android-kids-foundation` (there is no
   `main` yet; ask the founder before creating one). Work on a new branch off it and `git fetch`
   again before running research: conversation 1 may still be pushing reports (see section 3).
3. **Paste** `docs/handoff/STARTER_PROMPT.md` as the first message.
4. **Compute reality:** a cloud chat container (~30 GB free disk, ~15 GB RAM, 4 cores) can sync a
   *partial, shallow* subset of AOSP for inspection, **not build the OS**. The real build needs a
   separate build host (section 7).

## 3. Research status (snapshot; refresh with the commands below)

Reports live in `docs/research/NN-*.md`. Each was written by an investigator agent, then (if the
verify stage ran) edited in place by an independent skeptic who appends `## Verification (second
pass)`. **None had completed verification when this file was first written.**

| # | Topic | State at handoff |
|---|-------|------------------|
| 01 | AOSP base release, cadence, build host | **Written**, unverified |
| 02 | Hardware target | **Written**, unverified |
| 03 | Minimal product config | researching |
| 04 | No-browser lockdown | researching |
| 05 | Parental-controls platform | queued |
| 06 | Curated video (YouTube) | queued |
| 07 | AI assistant | queued |
| 08 | Walkie-talkie / comms | queued |
| 09 | Core apps stack | queued |
| 10 | OTA / signing / security | queued |
| 11 | Compliance & legal | queued |
| 12 | Telephony: calls + SMS + allowlists | researching |
| 13 | Kid messenger + video calling | researching |
| 14 | Weather education app | queued |
| 15 | Snapdragon device selection (D13) | researching (added after the founder's 3rd message) |
| 16 | Minimal Settings app (D14) | researching (added after the founder's 3rd message) |
| 17 | Selling the image: BYO distribution, installer, licensing (D15) | researching (added after the 4th message) |
| 18 | v1 flash-and-deliver operations (D16) | queued (added after the 5th message) |
| 00 | Cross-topic critique | queued (runs after 01-11 + verification) |

Refresh in conversation 2:
```
git fetch origin research/android-kids-foundation && git log --oneline origin/research/android-kids-foundation
ls docs/research
grep -L "Verification (second pass)" docs/research/*.md   # reports NOT yet skeptic-checked
```
Topics 01-11 were launched before the founder's second message (D4-D12); 12-14 after it; 15-16 after
the third (D13-D14); 17 after the fourth (D15); 18 after the fifth (D16). Reports 01-11 were therefore written without those decisions in the brief
(see section 5).

## 4. Conclusions so far (reports 01 and 02; secondary sources, verify against AOSP)

**Base release (01).** "Latest" = **`android-17.0.0_r1`, build CP2A.260605.016, SDK 37**, released
2026-06-16. The tag's SPL looks like **2026-06-05** (not 2026-07-01). AOSP source is published only in
**Q2 and Q4**; QPR1 is *not* in AOSP; the next drop is expected ~Dec 2026.
- Pin the tag (never a floating branch); plan **one deliberate rebase onto the Q4-2026 drop**.
- **Zero-fork-first**: own `zune/manifest`, `device/zune/*`, `vendor/zune/*`, product makefiles and
  RRO overlays; fork an AOSP repo only when unavoidable (target < 30 forks; GrapheneOS forks 88).
- **Security patching is the central business risk.** Public security-only branch had 2-3 month
  gaps in 2025; ~40 security commits authored Mar-Jul 2026 reached downstreams ~125 days later;
  partners get ~3 months early access. With no GMS we ship every Mainline module and WebView fix
  ourselves. Needs a monthly patch-ingest pipeline, an ODM/SoC monthly-patch contract, and a
  bid for Android partner access.
- **Stock AOSP product includes `Browser2` and `Camera2`**: do not inherit `aosp_arm64` /
  `handheld_product.mk` unchanged; compose from `base_*`.
- **No WebView provider** in the downstream manifests apart from `WebViewBootstrap` (GrapheneOS adds
  Vanadium). We need a WebView source + Chromium-cadence update path (open design item; the EPUB
  reader and any video player need WebView).
- **Android 17 ships a native supervision framework** (`SupervisionManager`, `ROLE_SUPERVISION`,
  Settings "Supervision"), flags enabled in the release chain, with `config_systemSupervision` etc.
  **empty**, so our parental-controls agent plugs in through an overlay. Seen only in GrapheneOS's
  tree so far.
- Build: Siso default, Bazel gone from the platform build, no ccache hook, Ubuntu 24.04 host;
  **Cuttlefish** (`aosp_cf_x86_64_only_phone-aosp_current-userdebug`) for hardware-free CI.

**Hardware (02), SUPERSEDED IN PART by D13.** The founder later said the product may be limited to a
curated set of devices and that *high-end Snapdragon* is acceptable, so the Pixel/Tensor-first
recommendation below is **reopened**; report 15 re-does device selection. The Pixel material remains
useful as a reference path (documented relock, adevtool) and as a dev device. Original text:

**Hardware (02).** AOSP does not boot on arbitrary phones; Google stopped publishing Pixel device
trees/driver blobs with Android 16. Recommendation: **Pixel-first**: v0 = Cuttlefish + Pixel 9a
(`tegu`) and 10a (`stallion`), both `zumapro`; v1 = pre-flashed, bootloader-**relocked with our own
AVB key** Pixel 10a; device layer generated from Google stock images with GrapheneOS's MIT-licensed
`adevtool`. **Reject** GSI/"any Treble phone" and consumer BYO installer for v1; ODM own-hardware
only past a volume/cash gate (25k+ units/yr, $1.5M+). Pixel 11 not ready (GrapheneOS port stalled;
no MTE). LineageOS has **no official Android 17 builds** yet. Incumbent kid phones (Pinwheel, Bark,
Gabb, Troomi) rebadge commodity phones + subscription.
- **Biggest hazards:** (a) legal right to redistribute Google's Pixel firmware/blobs commercially
  is **unresolved**; (b) ~$450 landed hardware vs $100-240 competitor phones forces a bundle or
  subscription model.

## 5. Known conflicts: reports written before the founder's decisions

- **02 (Pixel/Tensor-first) vs D13 (Snapdragon, curated device set).** Key new questions: which
  Snapdragon phones allow relock with a custom AVB key; how a startup gets Qualcomm BSP / Android 17
  vendor support; retail-flash vs manufacturer-built (an unlocked bootloader defeats tamper
  resistance); price of high-end hardware for a kids' product; on-device AI via the Hexagon NPU.
  Topic 15 covers this.
- **D15 (sell the image; customers bring a qualified phone) vs report 02, which REJECTED a consumer BYO
  installer** (bricking, carrier-locked phones, unlocked-bootloader tamper risk). The founder has chosen
  BYO, so: how to ship the image without redistributing OEM blobs, the installer/flasher, relock where
  supported, update path for modem/vendor firmware, the licence/subscription model, and a device-
  qualification program. Upside to verify: keeping the phone's stock modem/IMS firmware may make
  VoLTE/carrier acceptance easier than for a flashed Pixel. Topic 17 covers this; also affects 04
  (enforcement cannot assume a relocked bootloader), 10 (our keys on customers' devices), 12, 15.
- **D16 (confirmed): v1 is company-flashed on the customer's phone and handed back; self-install later.**
  Topic 17's consumer installer becomes a v2 concern; v1 needs the flash-and-deliver service of
  topic 18 (report 02 path A mechanics, report 10 factory flow); every v1 device must be relockable
  (topic 15).
- **03 (minimal product) / 04 (no-browser) vs D14 (Settings).** Wi-Fi and mobile data must stay
  standard, yet Wi-Fi proxy/static DNS/Private DNS/VPN/tethering and captive-portal sign-in are
  bypass vectors. Topic 16 defines what is kept, read-only, parent-gated, hidden or forced.

Run `mode: "reconcile"` (section 8) after the research completes. Already identified:
- **02 recommends "no voice/SMS in v1"; founder decision D4-D6 puts cellular calls + SMS IN.**
  Consequences to research/verify: VoLTE/IMS acceptance of a non-stock OS on US carriers (carrier
  device-certification/IMEI allowlisting), eSIM (Pixel 10 US models reportedly eSIM-only; AOSP has
  no Google LPA), carrier-locked Pixels (Verizon never unlockable), E911 and Wireless Emergency
  Alerts (keep `CellBroadcastReceiver`), FCC/PTCRB/carrier certification, MVNO partner choice.
  Topic 12 covers this.
- **01 decision #5** ("telephony/SMS in or out") is now answered: IN.
- **06 (video)** assumed a fixed allowlist; D3 wants **topic-driven discovery driven by the child's
  question**. YouTube Data API search quota (default 10,000 units/day, 100 per search) and ToS on
  caching/derived indexes need re-checking; D2 requires that no route leads to YouTube itself.
- **07 (AI)** must cover **image input** (D11) and child photos as personal data.
- **08 (comms)** and **13 (messenger/video)** must share one identity/contact graph; **05 (portal)**
  must expose SMS reader, call allowlists, message review. **11 (compliance)** must add
  SMS-interception/consent law and child-to-child messaging duties.

## 6. Needs the real AOSP tree (settle these first in conversation 2)

Encoded as `EXTRA_VERIFY` in `docs/handoff/research-workflow.js`. Summary:
1. Does `android-17.0.0_r1` carry CP2A.260605.016 and SPL 2026-06-05? Release-config names
   (`aosp_current`, `cp2a`, `trunk_staging`). `git ls-remote` for `android17-release`,
   `android17-security-release`, `android-security-17.*` tags, and the Q4-2026 branch.
2. Supervision framework present and enabled **in AOSP itself** (not just GrapheneOS)?
3. What `build/make/target/product/*.mk` actually include at the tag (Browser2, Camera2, Dialer,
   Messaging, WebView provider, HTMLViewer, CellBroadcastReceiver...): the authoritative input for
   the minimal-product keep/remove table.
4. Google's **actual licence text** for Pixel factory images / driver binaries
   (`developers.google.com/android/images`): may a company pre-flash and sell modified Pixels?
5. AVB custom-key documentation and Pixel 9a/10a relock behaviour on Android 17; VSR/FCM rules.
6. Real sizes for `repo sync --partial-clone`; build-host recommendation from Google's docs.
7. Telephony module list in AOSP 17 (Telecom, TeleService, TelephonyProvider, Dialer, Messaging,
   CellBroadcastReceiver, euicc) for report 12; Telecom call-screening hooks; STIR/SHAKEN
   verification status API.
8. Captive-portal login app and Settings help links (browser bypass vectors) for report 04.
9. Real Settings app structure at the tag (screens, aconfig flags, Settings Panels the SystemUI Internet
   dialog depends on) for report 16; Qualcomm/CodeLinaro BSP facts need no AOSP access.

## 7. Build host (the chat container cannot build AOSP)

Recommended in report 01 (estimates): CI/build host **32 vCPU, 128 GB RAM, 1 TB NVMe, Ubuntu 24.04**
in a pinned container; developer minimum 16 vCPU / 64 GB / 500 GB. Full build 1.5-3 h clean,
3-15 min incremental. Google's published minimum is ~400 GB disk, 64 GB RAM. Cuttlefish needs
`/dev/kvm` (GCE nested virtualization or bare metal). Provisioning this host is a founder/DevOps
decision, not something a chat session can do.

## 8. Next steps for conversation 2 (in order)

0. **Verify AOSP access.** `git ls-remote https://android.googlesource.com/platform/manifest | head -3`.
   If blocked, stop and tell the founder which host is denied.
1. `git fetch`, then inventory reports (section 3 commands).
2. **Finish missing research:** run the workflow (the founder opts in with "use a workflow"):
   `Workflow({scriptPath: "<repo>/docs/handoff/research-workflow.js", args: {mode: "research", topics: [<missing slugs>]}})`
   Slugs: aosp-base hardware-target minimal-product no-browser parental-controls curated-video
   ai-assistant walkie-talkie core-apps ota-security compliance telephony-sms messenger-video
   weather-education snapdragon-hardware settings-minimal byo-distribution v1-provisioning-ops. (Max 2 agents run in parallel on a 4-core container.)
3. **Re-verify against primary sources:** `mode: "verify"` for at least aosp-base, hardware-target,
   minimal-product, no-browser, parental-controls, telephony-sms, core-apps, ota-security.
4. **Reconcile** every report written before the decisions: `mode: "reconcile"`.
5. **Critic:** `mode: "critic"` writes `docs/research/00-cross-topic-critique.md`.
6. **Founder decisions, one question at a time** (queue in section 9); record each in
   `docs/REQUIREMENTS.md` with a date.
7. **Phase 0 (needs the build host):** create `zune/manifest` pinned to `android-17.0.0_r1`;
   baseline `lunch aosp_cf_x86_64_only_phone-aosp_current-userdebug`; then `device/zune` +
   `vendor/zune` with a `zune_base` product (no Browser2/HTMLViewer, RRO for supervision agent),
   boot it on Cuttlefish, smoke test.
8. **Parallel Stage-1 tracks** once reports are reconciled: backend + parent portal skeleton,
   shared comms backbone (identity, contact graph, push, media plane), Kotlin/Compose app skeletons.

## 9. Founder preferences and open questions

**Working agreements (stated by the founder or implied):**
- **One question at a time.** (Explicitly asked.)
- Committing and pushing to a **branch** is approved; **do not open PRs** unless asked.
- Commit trailers: `Co-Authored-By: Claude <noreply@anthropic.com>` and the session link;
  **no model names** in commits or any pushed artifact.
- A stop hook demands a clean working tree: commit and push after writing files.
- Founder writes by voice dictation; messages can be garbled: restate your interpretation.

**Open question queue (ask in this order, one at a time; defaults in brackets):**
1. Launch market / first country [US]. *Asked once in conversation 1, unanswered.*
2. May the child **send** SMS, or only receive (parent-visible)? [child neither sends nor reads SMS]
3. Google Mobile Services: confirm none [none].
4. *(Answered: D15 customers bring their own phone; D16 we flash and hand over in v1, so every v1
   device must be re-lockable.)* **How many users in the first batch?** (sizes the ops design.)
   Then: which devices.
5. Pricing/licence model for the image: one-time licence vs per-child/per-family subscription vs both
   (the cloud services are the practical paywall; see report 17).
6. Authorise legal work + Google outreach (Pixel binary redistribution, partner security access).
7. Product name (codename "Zune" has Microsoft trademark history).
8. Create a `main` branch / repo structure (monorepo layout in report 09).

## 10. Repo state

- Remote `https://github.com/getplx/Zune` had no branches before this work. Branch
  `research/android-kids-foundation` carries everything. No PR exists.
- `docs/REQUIREMENTS.md`: canonical decisions (D1-D16). `docs/research/`: reports. `docs/handoff/`:
  `research-workflow.js` (reusable multi-agent script, tested with stubs in all four modes),
  `STARTER_PROMPT.md` (paste into the new chat).
