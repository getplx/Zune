# 01 - AOSP base release, branches, cadence, build host

Status date: 2026-10-02. Basis tags: **[P]** read in a primary source or real source file this session; **[S]** reputable secondary (search-surfaced, page not fetchable here); **[I]** engineering inference; **[M]** memory, unchecked. Source keys (S1...) are listed at the end. `source.android.com`, `android.googlesource.com` and most news sites were egress-blocked, so Google's own wording is [S].

## Summary & recommendation

"Latest default Android image" means **AOSP Android 17, tag `android-17.0.0_r1` (build CP2A.260605.016, API 37.0), released 2026-06-16** [P: S1, S2, S3; date S]. That is the newest published platform source. **QPR1 (Pixel Drop, Sep 2026) is not in AOSP**: Google now publishes AOSP source only in Q2 and Q4, so QPR2 is expected around December 2026 [S: S8, S9].

Recommendation:
1. **Base the product on `android-17.0.0_r1` today** (pinned tag, never a floating branch), build and prove the stack on Cuttlefish, then **plan one deliberate rebase onto the Q4-2026 drop** before beta freeze, because that drop carries the fixes withheld in the interim.
2. **Zero-fork-first.** Use our own `device/zune/*` and `vendor/zune/*` trees, product makefiles and overlays. Fork an AOSP repo only when unavoidable, as a short patch stack rebased on the pinned tag. GrapheneOS forks 88 AOSP repos of 1,057 and LineageOS hosts 108 of 1,067 itself [P]; Zune's target is under 30.
3. **Treat security patching as the central business risk, not a build detail.** Without GMS or partner access we get no Play system updates and no early patches, and AOSP's public patch flow became lumpy in 2025-26. Fund a monthly patch-ingest pipeline and require monthly security drops from the ODM/SoC vendor.
4. Use **Ubuntu 24.04** build hosts (32 vCPU / 128 GB / 1 TB NVMe), Siso (the Android 17 default) and **Cuttlefish** for hardware-free CI.

## Findings

### F1. What the Android 17 base is

| Item | Value | Basis |
|---|---|---|
| Release tag | `android-17.0.0_r1`; GrapheneOS and LineageOS (lineage-24.0) both pin exactly this tag | [P] S1, S2 |
| Build ID | CP2A.260605.016 ("rebased onto CP2A.260605.016 AOSP release") | [P] S3 |
| Branch names | `android17-release`; `android-latest-release` manifest now points at it | [S] S12 |
| Default release config | `aosp_current` aliases `cp2a` (inherits `cp1a`, `mainline_2026_04`) | [P] S5 |
| SDK | 37 / 37.0 | [P] S5 |
| **SPL of the tag** | **2026-06-05** (Google commit "SPL June 2026"; GrapheneOS's first change moves it 2026-06-05 to 2026-07-05). The brief's "2026-07-01" is not what the tree shows; it is likely the first monthly SPL for which Android 17 appears in the bulletin | [P] S5; [I] |
| Kernel | GKI `android17-6.18`, launched 2025-11-30, EOL 2030-07-01. Supported: 6.18, 6.12, 6.6, 6.1, 5.15; 5.10 dropped in QPR1+. AOSP ships `kernel/prebuilts/6.18` | [S] S13; [P] S1 |
| Downstream map | LineageOS 23.0 = android-16.0.0_r1, 23.1 = r3, 23.2 = r4, **24.0 = Android 17** | [P] S2 |

The `aosp-mirror` GitHub org is **stale** (its `android-latest-release` was last updated 2025-11-11, pointing at `android16-qpr1-release`; no android-17 tags) [P: S6]. Both downstreams fetch AOSP straight from `android.googlesource.com` [P: S1, S2], so there is no GitHub fallback for Android 17.

### F2. Publishing cadence and security-patch plumbing

- Google: "Effective 2026... source code is published to AOSP in Q2 and Q4"; security patches continue monthly on "a dedicated security-only branch"; build from `android-latest-release` [S: S7, S10].
- Branch pattern for security-only releases: `android<N>-security-release` branches and `android-security-<N>.0.0_rX` tags exist for Android 10 through 15 [P: S6]. I could **not** verify an `android17-security-release` branch or `android-security-17.*` tags (googlesource blocked); verify first thing from the build host with `git ls-remote`.
- Evidence that the public flow degraded. Dates of `android-security-15.0.0_rN` tags [P: S6]:

| Tag | Date | Note |
|---|---|---|
| r3 to r9 | 2024-12-02 to 2025-06-02 | monthly |
| (none) | Jul, Aug 2025 | two bulletins with no tag |
| r10 | 2025-09-02 | 3-month gap |
| r11 | 2025-11-03 | 2-month gap |

Reporting agrees: July 2025 empty, August one patch, September incomplete [S: S10].
- Embargo: partners are notified of all issues at least a month ahead [S: S11], and GrapheneOS describes about 3 months of partner early access, with binary-only releases allowed until disclosure [S: S14].
- **Observed lag on Android 17.** About 40 security-labelled framework commits (BAL bypass, PduParser, ExternalStorageProvider, ...) authored Mar-Jul 2026 appear together in GrapheneOS's `17_09-09_base` branch (committed 2026-09-09) and in LineageOS `lineage-24.0` (2026-09-11 and 09-19). Median author-to-downstream lag is about 125 days (range roughly 75-190) [P: S3, S4 git metadata; the "public availability" reading is [I]].
- GrapheneOS, as a partner, shipped SPL 2026-09-05 before the Sept bulletin appeared and ships bulletin patches up to 7 months ahead as "security preview" releases [P: S3]. Non-partners are structurally behind.
- Sept 2026 bulletin: 180 vulnerabilities; 95 at SPL 09-01 (framework, system, ART, Mainline) and 85 at 09-05 (kernel and vendor/SoC); AOSP links were added in v1.1 [S: S15]. Only the 09-01 half is fixed in AOSP source; the 09-05 half comes via kernel (GKI LTS) and vendor drops.

### F3. How downstreams cope

| Project | Approach | Basis |
|---|---|---|
| GrapheneOS | Pins AOSP tag; per-update `17_MM-DD_base` branches hold AOSP plus security patches, with their patch stack rebased on top; bumps SPL monthly in `build/release`; partner early access; releases roughly every 1-2 weeks; Pixel-only | [P] S1, S3, S4, S5 |
| LineageOS | Pins tag in the manifest; merges bulletin patches into its forks; Updater shows ASB level; LOS 23.0 shipped on the initial Android 16 tag because QPR1 source was not public | [P] S2, S4; [S] S16, S27 |
| CalyxOS | Paused Aug 2025, resumed Jul 2026; Sep 2026 update (Android 16) carried SPL 2026-09-01 platform plus 09-05 kernel patches on 2026-09-10 | [S] S17 |

A non-partner can approach monthly cadence, but only with a dedicated owner and with gaps outside its control.

### F3b. Mainline and WebView supply chains (no GMS)

- Stock products set `MODULE_BUILD_FROM_SOURCE ?= true` [P: S19]; roughly 45 `packages/modules/*` projects are in tree [P: S1]. Without Play system updates, **every Mainline fix ships only through our OTA**.
- **No WebView provider in either downstream manifest** other than `WebViewBootstrap` (GrapheneOS adds Vanadium) [P: S1, S2]. Custom apps will embed web content (video, EPUB), so we need a WebView source plus a Chromium-cadence update path. This is an open design item.

### F4. Repo, sync and host

- `repo` flags exist in the current tool: `--partial-clone`, `--clone-filter`, `--partial-clone-exclude`, `--depth` on init; `--current-branch`, `--no-tags`, `--no-clone-bundle`, `--use-superproject` on sync; `--mirror` and `--partial-clone` are mutually exclusive [P: S18].
- Disk/RAM: GrapheneOS: 136 GiB+ for a sync with history, 90 GiB+ light, +100 GiB for a full build, 32 GiB+ RAM [P: S5]. Google: 400 GB (250 checkout + 150 build), 64 GB RAM, Ubuntu 22.04 [S: S20]. GrapheneOS supports Debian 12 and Ubuntu 24.04/24.10 [P: S5].
- Build time: Google's reference is a 72-core/64 GB machine at about 40 minutes for a full build, a 6-core/64 GB machine at several hours [S: S20]. Our estimate on 32 vCPU: **1.5-3 h clean, 3-15 min incremental** [I].
- AOSP's in-tree Dockerfile (`build/make/tools/docker`) is **Ubuntu 14.04, legacy only** [P: S19]; write our own Ubuntu 24.04 image. JDKs 21 and 25 are vendored in `prebuilts/jdk` [P: S1].

### F5. Build-system mechanics (Android 17)

- **Soong + Kati + Siso.** `NINJA_DEFAULT = NINJA_SISO`; `SOONG_NINJA=ninja` is the escape hatch; `SOONG_ONLY` exists [P: S21]. `prebuilts/siso` first appears in lineage-24.0 (absent in 23.2) [P: S2].
- **Bazel is gone from the platform build:** `build/bazel` is in lineage-23.0, absent from 23.1, 23.2, 24.0 [P: S2]. Kernels still use Kleaf/Bazel separately [I].
- **No ccache integration** found in `build/soong/ui/build` [P: S21, file listing]. Remote cache means Siso RBE (`siso_config/`, `rbe.go`), which needs an REAPI backend we would run ourselves [P: S21; [I] on the backend].
- **lunch syntax:** `<product>-<release>-<variant>`. Real examples: `aosp_cf_x86_64_only_phone-aosp_current-userdebug` [S: S22], `husky-cur-user` [P: S5; `cur` is a GrapheneOS alias]. `trunk_staging` = rolling development flags (SPL 2026-06-05 [P: S5]); production should use `aosp_current` (`cp2a`). `user`, `userdebug`, `eng` are build-variant configs. No `next` config exists in the tree inspected [P: S5].
- **Products:** `aosp_arm64` uses a Soong-defined system image [P: S19]; goldfish exposes `sdk_phone64_x86_64`, `sdk_phone64_arm64`, `sdk_phone16k_*`, `sdk_tablet_*`, `sdk_slim_*` [P: S23]; `core_64_bit_only.mk`, `go_defaults*.mk` exist for low-RAM hardware [P: S19].
- **Stock AOSP ships a browser.** AOSP's default `handheld_product.mk` listed `Browser2` and `Camera2`; GrapheneOS replaced them in 2020 [P: S19 history], and lineage-24.0 still pulls both repos from AOSP [P: S2]. **Do not inherit `aosp_arm64`/`handheld_product.mk` unchanged**; compose the product from `base_*` and selected pieces.

### F6. Android 17 changes that matter for a kids OS

- **Native supervision framework in AOSP**: `android.app.supervision.SupervisionManager`, `SupervisionAppService`, `Policy`, PIN and recovery info, roles `ROLE_SUPERVISION` and `ROLE_SYSTEM_SUPERVISION`, Settings "Supervision" screen, web-content-filter and app-store-filter screens. Key flags (`supervision_manager_apis`, settings screen, app service, `enable_supervision_manager_policy_apis`) are ENABLED in the Android 17 release chain. AOSP leaves `config_systemSupervision`, `config_allowedSupervisionRolePackages` and `config_defaultSupervisionProfileOwnerComponent` **empty**, so our parental-controls app plugs in through an overlay. `enable_supervision_package_usage_apis` is only on in `trunk_staging`; DPM supervision APIs are being deprecated [P: S4, S5]. This is the natural anchor for the parent portal's on-device agent.
- App-facing behavior changes [P: S24]: `ACCESS_LOCAL_NETWORK` required (walkie-talkie on LAN); background-audio hardening (needs foreground services); BAL hardening; Certificate Transparency and ECH on by default; per-app memory limits; static-final reflection blocked; large screens ignore orientation locks; SMS OTP delayed 3 h.
- 16 KB pages: supported since Android 15; Android 17 adds a fatal-abort mode for incompatible binaries; NDK r28+ aligns by default [P: S24]. Build all native code 16 KB-clean regardless of hardware choice.
- Advanced Protection Mode assumes Play Protect [S: S24]; we lock sideloading at build/policy level instead.
- aconfig namespaces for appfunctions, ondeviceintelligence, contentsafety and privatecompute exist [P: S5]; maturity not verified.

### F7. CI targets without hardware

- **Cuttlefish** (`aosp_cf_x86_64_only_phone`; arm64 guest naming unverified [M]) needs `/dev/kvm`; supports local x86/arm64 hosts and GCE with nested virtualization; Debian packages and docker/podman images (x86_64, ARM64) published [P: S25; S: S22].
- **Goldfish** (`sdk_phone64_*`) for emulator-style tests [P: S23]. QPR1 GSI binaries exist (CP3A.260905.010, 2026-09-17) for app-compatibility tests, but QPR1 source is not in AOSP [S: S24, S8]. Nested virtualization is not universal across clouds: use GCE or bare metal [I].

## Options & trade-offs

| Option | Pro | Con | Verdict |
|---|---|---|---|
| A. Pure AOSP `android-17.0.0_r1` + our trees | Clean provenance, least diff | We own patch ingest, WebView, OTA, kernel | **Chosen** |
| B. Fork GrapheneOS | Hardened, fast patches, mature OTA | Pixel-focused, 129 repos of their own, partner access not transferable | Reuse ideas, not the tree |
| C. LineageOS base | Many device trees, monthly merges, updater | 108 own repos and app set; not locked down | Only if hardware needs its device trees |
| D. Wait for Q4-2026 drop | Fewer withheld fixes | Idle for months | Rebase onto it instead |
| E. Track `android-latest-release` | Always current | Unreproducible, base shifts at each drop | Never in CI |

Manifest strategy: **fork the manifest** (`zune/manifest`: pinned upstream snapshot plus `zune.xml`, using `remove-project`/`extend-project` with `base-rev` to catch drift [P: S26]); `.repo/local_manifests` only for dev experiments.

## Recommended design for Zune

1. **Repos.** `zune/manifest` (generated from upstream `default.xml` at the tag), `device/zune/<soc>-common`, `device/zune/<model>`, `vendor/zune/{apps,overlay,config}`, optional `zune/<aosp-repo>` forks on branch `zune/android-17.0.0_r1`. Patch-stack discipline: commits atop the pinned tag, `git range-diff` on every upgrade, no merges of upstream.
2. **Product.** `zune_<model>` composes from `base_system.mk`/`base_product.mk`, the minimal telephony options we decide on, and our first-party apps as privileged Soong `android_app` modules. Exclude `Browser2` and `HTMLViewer`; review DocumentsUI, Messaging, Dialer and Tag per feature (WebView itself stays). RRO sets `config_systemSupervision` to our parental-controls agent. Variants: `userdebug` (dev) and `user` (ship), release config `aosp_current`.
3. **Commands** (build host):
```
repo init -u <zune-manifest-url> -b main --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle
repo sync -c -j8 --no-tags
source build/envsetup.sh && lunch aosp_cf_x86_64_only_phone-aosp_current-userdebug   # baseline
lunch zune_<model>-aosp_current-user && m -j"$(nproc)"                               # product
# vanilla baseline: repo init -u https://android.googlesource.com/platform/manifest -b refs/tags/android-17.0.0_r1
```
4. **Host.** CI: 32 vCPU, 128 GB, 1 TB NVMe, Ubuntu 24.04 in a pinned container; dev minimum 16 vCPU / 64 GB / 500 GB. Add a self-hosted mirror of our pinned revisions if CI hits googlesource limits (`--mirror` excludes partial clone).
5. **Security pipeline.** (a) Weekly `ls-remote` watcher for `android17-security-release`, `android-security-17.*` and the Q4 branch; (b) monthly ingest: cherry-pick into the patch queue, run Cuttlefish smoke plus app tests; (c) monthly GKI LTS kernel merge; (d) WebView and Mainline refresh; (e) OTA SLA: Critical within 14 days of the bulletin, others within 30; (f) ODM/SoC contract requiring monthly ASB drops; (g) seek Android partner/early-access status.
6. **Rebase plan.** Dec 2026/Jan 2027: rebase onto the Q4 drop (QPR2, API 37.2 [S: S9]); freeze before beta; next candidate Q2 2027 (Android 18) [I].
7. **CI.** Cuttlefish x86_64 per merge request, goldfish `sdk_phone16k_*` nightly for page-size regression.

## Risks & unknowns

- **Security exposure window**: public AOSP patches can trail authoring by 2.5-6 months and arrive batched; Mainline and WebView are ours to ship. Residual risk is real for a children's product.
- `android17-security-release` existence and cadence **unverified** (Google pages blocked); QPR2 date and branch name unverified.
- Partner/early-access eligibility for a startup unknown.
- Build time and host sizing are estimates [I].
- Hardware may force a vendor BSP kernel (6.1/6.6/6.12) and HAL branch that lags AOSP 17.
- The supervision framework is new and partly flagged: treat as moving, pin to our base.
- Leftover paths (WebView-based apps, intents, document viewers) can reintroduce browsing.

## Decisions needed from the founder

1. Commit to **AOSP Android 17 with a planned Q4-2026 rebase**, or accept a vendor BSP's older Android release (changes security posture).
2. Approve **security staffing and budget**: about 1 FTE platform/security engineer plus kernel support, and a monthly OTA service.
3. Pursue **Android partner/early-access status** (directly or via the ODM)? This affects hardware choice.
4. Confirm **no GMS** (assumed). It removes Play updates and drives the WebView and Mainline OTA burden.
5. Telephony/SMS in or out (changes attack surface, certification and the module list).
6. Own build infrastructure (cloud, 32 vCPU class) vs ODM-provided builds.

## Load-bearing claims

| # | Claim | Evidence | Basis |
|---|---|---|---|
| 1 | Latest AOSP = `android-17.0.0_r1` / CP2A.260605.016; downstreams pin it | S1, S2, S3 | P |
| 2 | AOSP source only in Q2/Q4; QPR1 not in AOSP, QPR2 expected Dec 2026 | S7, S8, S9 | S |
| 3 | Security-only branch tags for Android 15 had 2-3 month gaps in 2025 | S6 | P |
| 4 | About 40 security commits authored Mar-Jul 2026 landed downstream Sep 2026 | S3, S4 | P/I |
| 5 | GrapheneOS and LineageOS fork only ~8-10% of repos and pin the tag | S1, S2 | P |
| 6 | Android 17 build uses Siso by default; Bazel removed; no ccache hook | S21, S2 | P |
| 7 | AOSP 17 contains supervision framework with flags enabled and empty config hooks | S4, S5 | P |
| 8 | Stock AOSP product includes Browser2/Camera2; must not inherit unchanged | S19, S2 | P |
| 9 | aosp-mirror GitHub is stale (2025-11-11); AOSP 17 only on googlesource | S6, S1 | P |
| 10 | Cuttlefish/goldfish run without hardware; Cuttlefish needs KVM | S23, S25 | P |

## Sources

S1 https://raw.githubusercontent.com/GrapheneOS/platform_manifest/17/default.xml (+ `config.yml`). S2 https://raw.githubusercontent.com/LineageOS/android/lineage-24.0/default.xml (branches lineage-22.2, 23.0, 23.1, 23.2). S3 https://raw.githubusercontent.com/GrapheneOS/grapheneos.org/main/static/releases.html. S4 github.com/GrapheneOS/platform_frameworks_base branch `17_09-09_base` (supervision sources, config.xml) and github.com/LineageOS/android_frameworks_base `lineage-24.0` history. S5 github.com/GrapheneOS/platform_build_release branch 17 (release_configs, flag_values, aconfig); build guide https://raw.githubusercontent.com/GrapheneOS/grapheneos.org/main/static/build.html. S6 github.com/aosp-mirror/platform_manifest (tags, branches). S7 https://source.android.com/docs/whatsnew/site-updates. S8 https://www.androidauthority.com/grapheneos-android-17-qpr1-security-patches-comments-3712218/. S9 https://dev.to/axrisi/android-17-qpr1-why-the-new-apis-are-pixel-only-until-december-438f ; https://developer.android.com/about/versions/17/release-notes. S10 https://www.androidauthority.com/aosp-source-code-schedule-3630018/. S11 https://source.android.com/docs/security/bulletin/android-17. S12 https://x.com/Gracker_Gao/status/2067081023679320477. S13 https://source.android.com/docs/core/architecture/kernel/gki-android17-6_18-release-builds. S14 https://x.com/GrapheneOS/status/1964754118653952027. S15 https://www.securityweek.com/androids-september-2026-updates-patch-180-vulnerabilities/ ; https://source.android.com/docs/security/bulletin/2026/2026-09-01. S16 https://www.androidauthority.com/lineageos-summertime-update-2026-3685112/. S17 https://calyxos.org/news/2026/09/10/september-security-update/. S18 github.com/GerritCodeReview/git-repo (subcmds/init.py, sync.py, project.py, docs/manifest-format.md). S19 github.com/GrapheneOS/platform_build branch 17 (`target/product/*.mk`, `tools/docker`, history). S20 https://source.android.com/docs/setup/start/requirements. S21 github.com/GrapheneOS/platform_build_soong branch 17 (`ui/build/config.go`, `siso_config/`). S22 https://source.android.com/docs/setup/build/building ; https://source.android.com/docs/devices/cuttlefish/get-started. S23 github.com/GrapheneOS/device_generic_goldfish branch 17 (`AndroidProducts.mk`). S24 https://developer.android.com/about/versions/17/summary ; /behavior-changes-all ; /behavior-changes-17 ; /guide/practices/page-sizes ; /about/versions/17/qpr1/gsi-release-notes. S25 github.com/google/android-cuttlefish (README, container/README). S26 = S18 (`docs/manifest-format.md`, `base-rev`). S27 https://www.androidauthority.com/lineageos-23-release-3604073/.
