# Zune research 02: Hardware target and device-support strategy

Date: 2026-10-02. Tags: [PRIMARY] read in real source or a primary page this session; [SECONDARY] press or vendor page (often only the search summary was readable); [INFERRED] my judgement. grapheneos.org, wiki.lineageos.org, source.android.com, developers.google.com and most news sites were egress-blocked, so GrapheneOS/LineageOS facts come from their GitHub repos.

## 1. Summary and recommendation

AOSP does not boot on arbitrary phones, and Google stopped publishing Pixel device trees, but Pixels remain the only hardware with a proven path to "custom AOSP, bootloader relocked with our own key, 7 years of firmware". Ship v1 on Pixels, keep the product layer device-agnostic, and defer own hardware until volume and funding justify it.

- **v0 (dev, now to about Dec 2026):** Cuttlefish for app and system work, plus two physical Pixels bought unlocked from Google Store: Pixel 9a (`tegu`) and Pixel 10a (`stallion`). Both are Tensor G4, the same `zumapro` platform, so one device-support code path covers both. [CORRECTED] Qualification: the adevtool config (`common/gen9pixel.yml`) is shared, but each model still has its own generated vendor module, its own kernel repo (`device_google_stallion-kernels_6.1`, `device_google_tegu-kernels_6.1`), its own stock build IDs and its own SKUs, so there are two vendor modules and two QA matrices, not one [PRIMARY: GrapheneOS/platform_manifest@17 default.xml; GrapheneOS/adevtool@17 config/device/{stallion,tegu}.yml, vendor-skels/google_devices/].
- **v1 (launch):** pre-flashed, bootloader-relocked Pixel 10a (9a as lower-cost sibling while stock lasts). Wi-Fi-first, optional data SIM, no voice/SMS until a carrier test matrix exists. Google supports the 10a to March 2033 [SECONDARY].
- **Long term:** keep Pixel a-series as primary through about 2028. Qualify one second-source OEM (Motorola moto g, Fairphone, Sony Xperia 10) behind a written Device Support Contract. Fund an ODM kids device only past a volume and cash gate (section 4).
- **Do not do in v1:** GSI-based "any Treble phone" support, a consumer BYO installer, Pixel 11, or an ODM phone.
- **Biggest hazards:** the legal basis for shipping Google's Pixel binaries commercially, and Pixel hardware (about $300-500) costing more than most competitors' whole kids' phone ($100-240).

## 2. Findings

### F1. Google no longer publishes Pixel device trees and driver binaries
- Since Android 16 (June 2025) AOSP omits Pixel device trees/driver binaries; Google said AOSP needs a reference target "independent of any particular hardware", now Cuttlefish [SECONDARY]. https://www.androidauthority.com/google-not-killing-aosp-3566882/
- AOSP source is published only in Q2 and Q4; monthly security patches go to a separate security-only branch [SECONDARY]. https://piunikaweb.com/2026/01/07/android-aosp-source-code-q2-and-q4-pixel-monthly-security-patches-unchanged/
- GrapheneOS's Android 17 manifest pins `android-17.0.0_r1` and contains no `device/google/<pixel>` trees, only per-device prebuilt-kernel repos (`device_google_{stallion,tegu,akita,laguna,...}-kernels`) plus `vendor/adevtool` [PRIMARY]. https://raw.githubusercontent.com/GrapheneOS/platform_manifest/17/default.xml
- `adevtool` (MIT) generates each Pixel's vendor module from Google's stock factory/OTA images (blobs, sysprops, SELinux, VINTF, radio/bootloader firmware) and converts Pixel `kernels-<build>.tar.xz` tarballs to git commits; on 2026-09-06 GrapheneOS moved Pixels to Android 17 QPR1 stock images [PRIMARY]. GrapheneOS/adevtool@17:README.md, docs/usage.md, src/commands/process-kernel-tarballs.ts, git log.
- Net: a downstream Pixel build is AOSP tag + a device layer derived from Google's stock images + Google's prebuilt kernels; with adevtool, bring-up is a tooling problem, not reverse engineering [INFERRED]. [CORRECTED] Qualification: it is a recurring engineering burden, not a one-off. Stock Pixel images are ahead of the AOSP source tag, so downstream must backport Pixel userspace pieces each cycle. GrapheneOS's `adevtool` commit "switch Pixels to 17 QPR1 images" (2026-09-06) touched 15 config files (+1,229/-144 lines) while the manifest still pins `android-17.0.0_r1` (CP2A.260605.016), and its release notes say Android 16 QPR1 "was pushed to the Android Open Source Project on November 11 rather than September 3 as expected" [PRIMARY: GrapheneOS/adevtool@17 git log; GrapheneOS/grapheneos.org static/releases.html @ 2026-10-01]. Budget at least one dedicated platform engineer for vendor-module/QPR skew work.

### F2. GrapheneOS Android 17 device matrix and platform map
- `all.yml` builds gens 6-10; gen 11 is commented out with commit "[temporary] exclude 11th gen Pixels from 'all'" [PRIMARY]. GrapheneOS/adevtool@17:config/device/all.yml.
- Platform per generation [PRIMARY, config/device/common/gen*.yml]: gs101 (6, 6a); gs201 (7, 7a, Fold, Tablet); zuma (8, 8a); **zumapro (9, 9 Pro, 9 Pro XL, 9 Pro Fold, 9a, 10a)**; laguna (10, 10 Pro, 10 Pro XL, 10 Pro Fold); malibu (11 family).
- Kernels in the manifest are 6.1 for stallion/tegu/akita and 6.6 for laguna, not the 6.18 GKI line [PRIMARY]. We consume Google's kernels; we do not own kernel work.
- GrapheneOS finished its Android 17 port on release day, 2026-06-16 [SECONDARY]. https://alternativeto.net/news/2026/6/privacy-focused-android-operating-system-grapheneos-has-fully-been-ported-to-android-17/ [CORRECTED] Primary release notes: the 2026-06-16 release (tag 2026061600) was GrapheneOS's "final release based on Android 16 QPR2/QPR3" because it had "completed our initial port to Android 17 and [was] resolving regressions"; the first Android 17 release is tag 2026061800 (2026-06-18), "rebased onto CP2A.260605.016" [PRIMARY: GrapheneOS/grapheneos.org static/releases.html @ 2026-10-01]. Two-day gap; no change to the recommendation.

### F3. LineageOS: no official Android 17 builds yet
- `hudson` lineage-build-targets (commit 2026-09-28) lists only lineage-22.2 (115 devices) and lineage-23.2 (205). `lineage-24.0` (Android 17) branches exist in vendor/lineage and some device repos, but no builds are scheduled [PRIMARY]. LineageOS/hudson@main:lineage-build-targets
- [CORRECTED] Official 23.2 Pixels stop at the Pixel 9 generation, not at the 9a: the 23.2 target list includes `tokay` (9), `caiman` (9 Pro), `komodo` (9 Pro XL), `comet` (9 Pro Fold) and `tegu` (9a), plus 8a (`akita`) and older; no Pixel 10-family device and no 10a (`stallion`) is scheduled. Pixel 10/10a device repos (`laguna`, `frankel`, `stallion`) exist with both `lineage-23.2` and `lineage-24.0` branches but are not official builds; Pixel 11 repos do not exist [PRIMARY: LineageOS/hudson@main lineage-build-targets; `git ls-remote` of LineageOS/android_device_google_*; second pass].
- Official 23.2 non-Pixel candidates [PRIMARY, LineageOS/lineage_wiki@main:_data/devices (second pass: the `master` branch cited by the author is stale; `main` is current)]: Fairphone 5/6, Motorola g84/g34/g45/g05/g15, Sony Xperia 10 V/VII, Nothing Phone (2), many OnePlus/Xiaomi. LineageOS support signals unlockability, not relock with custom keys.

### F4. Pixel unlock and relock with our own key
- GrapheneOS release tooling generates an AVB key (`avbtool extract_public_key` to `avb_pkmd.bin`), signs target files, and its flash script runs `fastboot erase avb_custom_key`, `fastboot flash avb_custom_key avb_pkmd.bin` [PRIMARY]. GrapheneOS/script@17:generate-keys, generate-release.sh; GrapheneOS/device_common@17:generate-factory-images-common.sh [CORRECTED] the `GrapheneOS/script` repo has no `main` branch (branches are `17` and `16-qpr2`). Also, the cited flash script only erases/flashes `avb_custom_key`; the final `fastboot flashing lock` step is not in these files. It is documented in the avbroot README (flash `avb_custom_key`, then `fastboot flashing lock`) and GrapheneOS's install flow, and GrapheneOS's FAQ lists the Pixel 10a (`stallion`) and 9a (`tegu`) as officially supported with its verified-boot model [PRIMARY: github.com/chenxiaolong/avbroot README; GrapheneOS/grapheneos.org static/faq.html @ 2026-10-01].
- Google is reportedly the only OEM documenting `avb_custom_key`; Fairphone 3/4/5 and some Motorola g-series are reported working [SECONDARY]. https://github.com/chenxiaolong/avbroot/issues/299
- Google Store/unlocked Pixels allow OEM unlock; Verizon variants never do; T-Mobile/AT&T only after payoff and carrier unlock [SECONDARY]. https://calyxos.org/install/verizon/ Unlocking alone does not void Google's warranty; software modifications can void related coverage [SECONDARY].

### F5. Binary licensing is the open legal problem
- Pixel factory images are "for use only on personal devices and may not be disassembled, decompiled, reverse engineered, modified or redistributed" except per the device licence [SECONDARY, summary of https://developers.google.com/android/images ; page not fetchable]. adevtool prints Google's T&C notice on every download [PRIMARY].
- GrapheneOS and similar projects ship derived images and Pinwheel sells Pixel 8a units with its OS [SECONDARY], but how a for-profit reseller is licensed is unknown. Unresolved until counsel and Google confirm.

### F6. Pixel lineup, prices and support as of Oct 2026

| Model (codename, platform) | Launch | US price | Support to | Fit |
|---|---|---|---|---|
| Pixel 11 / Pro / Pro XL / Fold (malibu) | 2026-08-20 | $899 / $1,099 / $1,299 / $1,899 | 7 yrs claimed | No: see F7 |
| Pixel 10a (`stallion`, zumapro) | 2026-03-05 | $499 | Mar 2033 | **v1 primary** |
| Pixel 10 family (laguna) | 2025-08 | from $799 | ~2032 | Too costly for kids |
| Pixel 9a (`tegu`, zumapro) | 2025-04 | $499 launch; ~$300-430 now | Apr 2032 | **v0/v1 sibling** |
| Pixel 8a (`akita`, zuma) | 2024-05 | $499 launch; refurb $339 (Google), $170-234 (3rd party) | ~May 2031 [INFERRED] | Post-launch cheap SKU |

Sources [SECONDARY]: https://blog.google/products-and-platforms/devices/pixel/google-pixel-10a/ , https://www.androidauthority.com/google-pixel-11-series-3693865/ , https://www.droid-life.com/2026/08/16/google-pixel-update-schedule-how-long-will-my-phone-get-updates/ , https://www.androidauthority.com/refurbished-pixel-8a-only-cheap-pixel-id-buy-2026-3654569/ . Android 17 GSI validation covers Pixel 6 through 10a [PRIMARY]: https://developer.android.com/about/versions/17/gsi-release-notes [CORRECTED] That is the QPR1 stable list (2026-09-17). The QPR2 Beta list (2026-09-29) drops Pixel 6/6 Pro (keeps 6a) and adds the Pixel 11, 11 Pro, 11 Pro XL and 11 Pro Fold [PRIMARY: https://developer.android.com/topic/generic-system-image/releases].

### F7. Pixel 11 is not ready
GrapheneOS reported a "partial port" after a week but could not finish: no hardware ARM memory tagging (MTE) in Tensor G6, which Google has not confirmed [SECONDARY]. https://www.androidauthority.com/no-grapheneos-google-pixel-11-3704622/ Gen 11 is excluded from adevtool `all` and has no LineageOS repos [PRIMARY]. [CORRECTED] The exclusion commit is labelled "[temporary]" (2026-08-22), after "add initial support for 11th gen Pixels" (2026-08-16), vendor-specs (2026-08-22) and an early-September build index (2026-09-14), i.e. work is in progress, not abandoned; but GrapheneOS's FAQ and release notes as of 2026-10-01 list no Pixel 11 as supported [PRIMARY: GrapheneOS/adevtool@17 git log; grapheneos.org repo]. Relock with a custom key is not "unverified": avbroot's README documents a custom-AVB-key flow for the Pixel 11 series (RSA still works; ML-DSA keys need the device updated to the latest stock OS and booted once because factory GSC firmware breaks custom ML-DSA key registration) [PRIMARY: github.com/chenxiaolong/avbroot README + CHANGELOG 3.34.0]. The MTE absence claim is still unverified here (secondary only). MTE is hardening, not a blocker for us, but the ecosystem is not ready.

### F8. Treble/GSI is a dev tool, not a product path
- Android 17 GSIs exist (QPR1 stable 2026-09-17, QPR2 beta 2026-09-29), ARM64 with/without GMS. They are "for app developers to perform app validation and for development purposes"; "You shouldn't redistribute GSIs" [CORRECTED] (full sentence: "...or use them in any other way except as specifically set forth in the license terms enclosed in each individual download"); not CTS-approved [CORRECTED] (Google says the binaries have "a similar CTS result" and that device makers "shouldn't use these versions of GSIs to run and submit compliance tests"); validated only on Pixels. Needs an unlocked, Treble-compliant device launched with Android 9+ [PRIMARY]. https://developer.android.com/topic/generic-system-image/releases , https://developer.android.com/topic/generic-system-image
- Community GSI lags: TrebleDroid `device_phh_treble` has branches up to `android-16.0`, none for 17; `treble_experimentations` last commit 2025-06-16 "A16 build" [PRIMARY]. Typical GSI breakage: camera extras, fingerprint, VoLTE, Widevine L1 [SECONDARY].
- Relock with our key needs the vendor chain re-signed, so "GSI on stock vendor, then lock" fails on most OEMs [INFERRED]; a child who can unlock the bootloader defeats the product.

### F9. What kids'-phone incumbents do [SECONDARY]
- Pinwheel: Pixel 8a, Galaxy A16, Moto G Play 2024, BLU G64; Plus 6 $219; $14.99/mo; "cannot install Pinwheel OS on your own device". https://support.pinwheel.com/hc/en-us/articles/10628470165403-FAQ-Pinwheel
- Bark: rebranded Galaxy A16/A36 (https://www.androidpolice.com/bark-phone-review/). Gabb: ZTE Z2 (Helio A22, 2020), later Samsung-based; Phone 4 Pro $199. Troomi: Galaxy A15/A17, $99.95 + $19.95/mo (https://sammyguru.com/troomi-kid-safe-galaxy-a17/).
- Lesson: nobody here builds hardware; they rebadge commodity phones, sell a subscription, and multi-source devices. Samsung/Moto/BLU units are probably stock firmware plus managed-device software, not relocked custom ROMs [INFERRED]. That is a cheaper, weaker fallback ("browser-free by policy") if Pixel supply fails.

### F10. ODM / own hardware
- Vendor marketing (low reliability): MOQ 3-5k, NRE $5-65k, 12-16 weeks, certification $12-30k per region, FOB $48-115, "typical ODM launch $215k" [SECONDARY]. https://smartbuy.alibaba.com/buyingguides/smartphone-odm Treat as an optimistic floor; my estimate for a certified cellular kids' phone is $0.5-1.5M and 12-24 months [INFERRED].
- BSP lag: HMD Luma (Unisoc T615, Mar 2026) shipped Android 15 (https://en.wikipedia.org/wiki/HMD_Luma); Google/Qualcomm long-support (GRF) covers 8 Elite and some 7-series only (https://9to5google.com/2025/02/24/qualcomm-android-updates/) [SECONDARY]. Entry silicon will not run latest AOSP with 5-7 years of patches, and we would own every monthly patch [INFERRED].
- Precedents are niche: Light Phone III (Foxconn, Snapdragon 4 Gen 2, AOSP-based, $599) and Punkt MC02 (Dimensity 900, $750) [SECONDARY]. Upside: we could burn our secure-boot keys at the factory and remove every unlock path [INFERRED].

### F11. Other OEMs [SECONDARY]
Fairphone 6: unlockable, 8 years of updates, EUR 549, but pricey and modular (https://support.fairphone.com/hc/en-us/articles/9979180437393-How-long-will-my-Fairphone-receive-software-and-security-updates). Motorola: official unlock portal (https://support.motorola.com/us/en/solution/ms87215) and a 2027 GrapheneOS partnership for flagships with MTE and 7-year updates (https://www.theregister.com/2026/03/02/motorola_grapheneos/). Neither has a 2026 device meeting our contract (section 4).

### F12. Compliance by path [SECONDARY]
- US CPSIA: products "primarily designed or intended for children 12 or younger" need third-party testing and a Children's Product Certificate. https://www.compliancegate.com/cpsia-childrens-product-certificate-cpc/
- EU RED cybersecurity (Delegated Reg. 2022/30) applies since 2025-08-01; EN 18031-2 covers childcare radio equipment. https://www.sgs.com/en-se/news/2025/06/red-cybersecurity-requirements-mandatory-on-1-august-2025
- Cellular adds FCC/PTCRB/carrier certification. Whether re-flashing a Pixel makes us the "manufacturer" is a counsel question [INFERRED]; an ODM phone does.

### F13. Security-patch plumbing
adevtool's `process-bulletin-patches` ingests "Partner Security Bulletin" patch ZIPs GPG-signed by Google [PRIMARY]: GrapheneOS/adevtool@17:src/commands/process-bulletin-patches.ts. Monthly downstream patches are gated behind partner access; startup eligibility is unknown (security/update topic).

## 3. Options and trade-offs

Costs and times are [INFERRED] unless noted.

| Path | Time to v1 | Upfront | Unit economics | Main risk | Verdict |
|---|---|---|---|---|---|
| A. Pre-flashed new Pixel 10a/9a | 3-5 mo after image ready | <$100k tooling + 1-2k units float (~$0.5-0.9M) | ~$450 landed ($400-450 device + ~$35 flash/QA/ship); a $529-599 bundle nets ~10-15% before returns | Blob licence; Pixel openness; price | **v1** |
| A2. Refurb Pixel 8a (Google Certified) | +1 bring-up | Same | ~$260-340 landed; sell ~$349 | Unknown lock state/history | Post-launch SKU |
| B. BYO installer (Pixel only) | 2 mo | Low | No hardware cost; high support cost | Bricked or carrier-locked phones; Pinwheel refuses BYO | School/IT pilot only |
| B2. GSI on any Treble phone | n/a | n/a | n/a | No relock, frozen vendor, no Android 17 community GSI | Reject |
| C. ODM own phone | 12-24 mo | $0.5-1.5M (vendors say $215k) | $50-115 FOB entry silicon; breakeven tens of thousands of units | Cash, BSP lag, we own patches, certification | Gate at scale |
| D. Second-source OEM, pre-flashed | 6-9 mo | Moderate | $150-350 devices | Per-OEM unlock/relock unverified | After v1 |
| E. Stock firmware + managed-device policy | 2-3 mo | Low | Any Samsung/Moto/BLU | "No browser" is policy, not image | Fallback only |

Price gap: competitor devices sell at $100-240 plus $15-20/mo; a $450 Pixel needs a bundle/subscription (about $12-15/mo, 24 months) or premium positioning [INFERRED]. See decision 2.

## 4. Recommended design for Zune

**Device Support Contract** (a device qualifies only if it meets every MUST):
- MUST: AVB 2.0 with custom-key relock; OEM unlock can be disabled; A/B; stable AIDL HALs and VINTF; hardware-backed keystore; fastboot-flashable; 4 GB+ RAM.
- SHOULD: 5+ years of vendor firmware; GKI kernel; complete Camera2 HAL; MTE.
- Today only Pixel 8a/9a/10a meet all of it with documented evidence; Fairphone and some Motorola are probable. [CORRECTED] Imprecise: GrapheneOS's published requirements are "met or exceeded by devices starting from Pixel 8 (shiba) through Pixel 10a (stallion)", so every Pixel 8, 9 and 10 model meets the contract; the a-series is chosen on price, not because the others fail [PRIMARY: GrapheneOS/grapheneos.org static/faq.html @ 2026-10-01].

**Layout (`vendor/zune`, device-agnostic):** `products/zune_base.mk` (packages), `overlays/` (RROs for framework, SystemUI, Settings, telephony), `sepolicy/` (system_ext/product only), `apps/`, and `devices/<codename>/`, a thin shim that inherits the base and the generated vendor module and carries a `device.yml` (platform, has_cellular, has_nfc, cameras, display). Support code is per platform (zumapro, laguna), not per model.

**Rules that keep the product portable:**
1. The product layer touches only system/system_ext/product, never vendor or kernel; this keeps a future GSI or alternative-vendor build possible.
2. Apps use public SDK/Jetpack (CameraX, MediaCodec, Bluetooth, Wi-Fi) and `hasSystemFeature`, never device props.
3. "No browser" is enforced in the image (no browser package, browsable intents or WebView entry points), so a factory reset cannot defeat it. Re-pairing after reset belongs to the parent-portal topic.
4. Vendor-module generation is CI: fork adevtool (MIT), pin a Google build per device per month, diff `vendor-specs`, smoke-test physical devices (camera, audio, Wi-Fi, BT, GPS, charging).
5. Release channels/OTA are keyed by codename; AVB and OTA keys are per product, independent of device.
6. Factory flow: unlocked Google-Store stock, flash image plus `avb_custom_key`, `fastboot flashing lock`, disable OEM unlocking, QA script, box. A 10-20 port station at ~10 min/unit costs a few dollars per unit; the real cost is inventory float.

**ODM gate (Path C):** sustained 25k+ units/year, $1.5M+ committed, a BSP vendor commitment of 5 years of updates and factory key provisioning, partner security-bulletin access, and a cellular decision. Until then keep a paper RFQ with 2 ODMs warm.

## 5. Risks and unknowns

1. **Blob licence (high):** shipping Google firmware in a commercial product is unconfirmed (F5). Get counsel and a Google contact before taking pre-orders; keep path E as fallback.
2. **Pixel openness trend (high):** device trees gone, source twice a year, kernel tarballs, Pixel 11 without MTE. Mitigate with a second-source OEM and no bet on gen 11.
3. **Security-patch access (high):** monthly patches come via a gated partner path (F13); without it we lag GrapheneOS and Google.
4. **Cellular (medium):** VoLTE/E911/WEA acceptance of a non-stock OS on US carriers is unverified, and carrier-locked Pixels are unusable. No voice/SMS plus carrier-unlocked units avoids it in v1.
5. **Price and supply (medium):** hardware exceeds competitors' device prices; bulk-purchase terms and 10a/9a stock are unknown.
6. **Compliance and warranty (medium):** CPSIA, RED/EN 18031, manufacturer status, modified-OS warranty coverage; budget a 5-10% return reserve [INFERRED].
7. **Not verified here:** GrapheneOS FAQ, Google's licence text, Pixel 10a relock on Android 17 in practice, Pixel 11 unlock/relock, Android 17 vendor-support-window rules (VSR/FCM) for older vendors.

## 6. Decisions needed from the founder

1. Approve Pixel-first v1 (10a/9a pre-flashed) plus the ODM gate, or insist on own hardware now (I advise against).
2. Price and revenue model: bundle or subscription, given $300-500 hardware vs $100-240 competitors.
3. Cellular: confirm v1 has no voice/SMS (Wi-Fi plus optional data SIM); voice later via an MVNO?
4. Launch market: US only (CPSIA, FCC) or EU too (RED, EN 18031)?
5. Authorise legal work and Google outreach on Pixel binary redistribution, bulk supply and Partner Security Bulletin access.
6. Capital for inventory float (~$0.5-0.9M at 1-2k units) or a pre-order model.
7. BYO installer: "no" for consumers; any appetite for a school/IT pilot?
8. GMS: confirm NO (default); the Pixel path is unaffected.

## 7. Load-bearing claims

1. Google omits Pixel device trees/driver binaries from AOSP since Android 16 (androidauthority.com/google-not-killing-aosp-3566882) [SECONDARY].
2. A downstream Pixel build = AOSP tag + vendor module generated from Google factory images + Google kernels (GrapheneOS/platform_manifest@17:default.xml; GrapheneOS/adevtool@17) [PRIMARY].
3. GrapheneOS Android 17 builds Pixel gens 6-10 incl. 10a, excludes gen 11; 9a and 10a share `zumapro` (adevtool@17:config/device/all.yml, common/gen9pixel.yml) [PRIMARY].
4. Pixel supports relock with a custom AVB key (GrapheneOS/device_common@17:generate-factory-images-common.sh) [PRIMARY].
5. LineageOS has no official Android 17 builds as of 2026-09-28; official Pixels stop at 9a (LineageOS/hudson@main:lineage-build-targets) [PRIMARY].
6. GSIs are app-validation-only, not redistributable, Pixel-validated; community GSI has no Android 17 branch (developer.android.com/topic/generic-system-image/releases; TrebleDroid/device_phh_treble) [PRIMARY].
7. Pixel 10a is $499 and supported to March 2033; Pixel 11 starts at $899 (blog.google 10a post; androidauthority Pixel 11 series) [SECONDARY].
8. Pixel 11 lacks MTE and GrapheneOS could not finish the port (androidauthority.com/no-grapheneos-google-pixel-11-3704622) [SECONDARY].
9. Pixel factory images may not be modified or redistributed; commercial licence unresolved (developers.google.com/android/images, via summary) [SECONDARY].
10. Incumbent kids' phones rebadge Samsung/Moto/BLU/Pixel hardware and sell a subscription (Pinwheel FAQ; Android Police Bark review; Troomi) [SECONDARY].
