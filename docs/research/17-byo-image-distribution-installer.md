# Zune research 17: Selling the image (BYO distribution, installer, qualification, updates, licensing)

Date: 2026-10-02. Tags: [PRIMARY] read in a real file or primary page this session (repo@ref:path or URL); [SECONDARY] reputable page, press or community list, often a search summary; [INFERRED] my judgement; [MEMORY] unchecked training knowledge. **android.googlesource.com and source.android.com returned HTTP 403 (checked once, not retried), as did developers.google.com, calyxos.org, wiki.lineageos.org, ecfr.gov, cornell.edu, federalregister.gov and cpsc.gov.** I used GitHub raw files and shallow clones (GrapheneOS, LineageOS, avbroot, a community unlock list) plus search. Google's Pixel licence text and statute wording were not read at source. Not legal advice; counsel questions are flagged. Written against REQUIREMENTS D1-D16/A7 and reports 04, 05, 12, 15.

> **[CORRECTED] banner (skeptic second pass, 2026-10-02).** AOSP (android.googlesource.com, source.android.com) and developers.google.com were still unreachable (HTTP 403), so no claim here was checked against Google's own android-17.0.0_r1 tree or Google's licence text. Each claim was re-checked against GitHub raw files (GrapheneOS, LineageOS), developer.android.com pages that were reachable, and search. Inline "[CORRECTED]" notes mark what changed; the final "Verification (second pass)" table gives verdicts. Main corrections: fastboot variable claim overstated; RKP claim misapplied to retail phones; attestation is relay-bypassable; Pixel QPR1 head start and anti-rollback pre-flight interplay omitted; amended COPPA Rule and state OS age-signal laws omitted; Troomi/Gabb price anchors out of date.

## 1. Summary & recommendation

D15 (sell the image) and D16 (v1 is company-flashed; customer self-install later) are workable, but the blob problem moves rather than disappears. A phone relocked with our AVB key accepts only payloads we sign, so firmware, modem and vendor patches must ship inside **our** OTA. That needs a right to redistribute OEM bytes, not just resell hardware. D16 buys a legal runway: in v1 we flash the customer's own phone with firmware fetched from the OEM, a lighter posture than publishing a download [INFERRED, counsel]. The question returns with the first monthly firmware update.

1. **One installer, used first as our provisioning station (D16), released to customers in v2.** Web-based (WebUSB, fastboot.js, MIT) with a stricter pre-flight than GrapheneOS's. Station operations belong to report 18.
2. **Relock with our AVB key is mandatory for every "Zune Ready" device** (A7), verified by attestation at the station (v1) and gating self-install claims (v2). No unlocked tier.
3. **Devices (reconciling 15):** Pixel 9a/10a (`zumapro`) first for engineering and private beta (documented relock, adevtool). Fairphone Gen 6+ (15's pick) becomes the commercial launch if it signs written firmware-redistribution terms and passes the relock test. The gate is OEM terms plus verified relock, not the SoC.
4. **Money:** a one-time provisioning fee (v1 labour, shipping, QA) plus a **per-child subscription**; the image is useless without an account, so cloud services are the paywall. A one-time-only image fee is a trap: AI, relay, patch and support costs recur, and EU update duties outlast it.
5. **Compliance relief is partial.** No equipment authorisation or inventory, but under D16 we hold customers' phones: custody, wipe, warranty and CPSIA framing need counsel. Keep the legal form an installation service on a customer-owned phone; never sell the handset.

## 2. Findings

### F1. What may be in the image
- AOSP is Apache-2.0; the kernel is GPL-2.0 (source offer if we ship a modified or self-built kernel); GPL parts cannot carry extra EULA restrictions [MEMORY]. **[CORRECTED]** AOSP is mostly, not purely, Apache-2.0 (it also carries GPL/LGPL and other-licence components), and the GPL-2.0 source (or written-offer) duty attaches to any distribution of the kernel binary, modified or not, so an unmodified OEM kernel carried inside our OTA (options c/d) triggers it too [MEMORY, counsel; GPL text not re-read this session].
- Google: factory images are "for use only on your personal Nexus or Pixel devices and may not be ... modified or redistributed ... except as specifically set forth in the license terms that came with your device"; driver binaries likewise [SECONDARY: snippets of developers.google.com/android/images, /drivers]. The enclosed licence is unread; adevtool prints the T&C notice [PRIMARY: GrapheneOS/adevtool@17:src/images/download.ts]. **[CORRECTED]** Second-pass search summaries (Google's pages still blocked) give the factory-image wording as "may not be disassembled, decompiled, reverse engineered, modified or redistributed by you or used in any way except as specifically set forth in the license terms that came with your device", and the driver wording as "for use only on your personal devices ... may not be redistributed ... except as specifically set forth in the license terms enclosed in each individual download" [SECONDARY]. The "used in any way except" clause is broader than the paraphrase above, so option (b)'s claim that flashing for the owner "fits personal-device use" is [INFERRED] and unproven. adevtool's notice points to developers.google.com/android/images#legal, /android/ota#legal and developer.android.com/studio/terms (beta images) [PRIMARY: adevtool@17 src/images/download.ts].
- Practice: GrapheneOS flashes Google firmware from its own images [PRIMARY: grapheneos.org install page]. Of 743 LineageOS wiki entries, 374 tell users to install a specific OEM Android first and 184 say LineageOS ships the firmware (they overlap) [PRIMARY: LineageOS/lineage_wiki@main:_data/devices]. **[CORRECTED]** Recount at lineage_wiki@902bd57 (2026-09-29): 743 entries; 374 `needs_specific_android_fw`; 188 have `ships_fw: true`, of which 184 are also among the 374 (so 184 is the overlap, not the total). Every Pixel and Fairphone 4/5/6 entry on 23.2 is in both groups. Redistributing Qualcomm/OEM blobs is widely seen as unlicensed but tolerated [SECONDARY]. No project documents its legal basis.
- GrapheneOS lets others sell devices running it if they say they are not GrapheneOS; its name is a registered US trademark [PRIMARY: faq.html].
- Google's prebuilt GSIs are dev tools (no production use, no redistribution, unlocked Treble device) [PRIMARY: developer.android.com/topic/generic-system-image]; our own source build is not a Google binary [INFERRED].

### F2. System-only (GSI-style) on stock vendor
- Android 17 ships framework compatibility matrices for vendor FCM levels 7, 8, 202404, 202504, 202604, so vendors back to Android 13 are accepted [PRIMARY: GrapheneOS/platform_hardware_interfaces@17:compatibility_matrices/Android.bp; floor reading INFERRED; matches 15]. Kernel floor unverified; GKI 6.1+ is the safe set. **[CORRECTED]** Cross-checked in a second tree (LineageOS/android_hardware_interfaces@lineage-24.0) with the same five levels; GrapheneOS's platform_manifest pins `refs/tags/android-17.0.0_r1` as default revision, but platform_hardware_interfaces is a GrapheneOS fork, so this is still not Google's tree. The same Android.bp ties each level to kernel configs (GrapheneOS: 7 -> 5.10/5.15, 8 -> 5.15/6.1, 202404 -> 6.6, 202504 -> 6.12, 202604 -> 6.18; LineageOS also lists 4.14/4.19/5.4 for 7), so the framework side tolerates 5.10 kernels and "GKI 6.1+" is our DSC policy, not an Android 17 limit. Matrix acceptance is necessary, not sufficient: it says nothing about HAL behaviour or about Pixel's QPR1 vendor drop (section 7, risk 7).
- Typical GSI breakage: camera extras, fingerprint, VoLTE, Widevine [SECONDARY via 02]. Pixel IMS and eSIM pieces come from stock images [PRIMARY via 12]; Qualcomm IMS often sits in OEM `system_ext`/`product`, which system-only replaces [INFERRED].
- AVB: with a custom key set and the device LOCKED, the bootloader boots images signed by the built-in or the custom key; yellow = user-set key, orange = unlocked; Pixel 2+ expose `avb_custom_key`, writable only while unlocked [PRIMARY: LineageOS/android_external_avb@lineage-24.0:README.md]. "System-only, then lock" works only if our signed vbmeta covers the OEM partitions' digests [INFERRED].

### F3. Unlock and custom-key relock by OEM (community data, 2026-09)
| OEM | Unlock | Custom-key relock | Stance (with 15) |
|---|---|---|---|
| Pixel | OEM toggle + `fastboot flashing unlock`; carrier variants locked | Documented | Reference, beta |
| Fairphone | Per-device website code | Reported FP3/4/5; Gen 6/6+ unverified | Commercial candidate |
| Nothing (3)/(3a) | Plain fastboot | Reported; not (2a) | Stage 2 |
| Sony Xperia 1 V/VI | Portal + IMEI code; US/carrier units may never unlock | Reported | Reference BSP only |
| Motorola | Portal code; g-series | Reported g-series; GrapheneOS flagships 2027 | Watch |
| Samsung, OnePlus, Xiaomi, ASUS | Samsung: One UI 8 removed unlock; OnePlus: "Deep Testing"; Xiaomi: 72 h wait, quota; ASUS: tool ended | OnePlus newer bootloaders and Xiaomi ignore custom keys | Exclude |

Sources [SECONDARY]: github.com/chenxiaolong/avbroot/issues/299; github.com/zenfyrdev/bootloader-unlock-wall-of-shame (HEAD 2026-09-27). **[CORRECTED]** Re-read issue 299 (second pass): "confirmed working" lists Fairphone 3 and "4 and 5" (not 6), Google Pixel 2+, Motorola moto g32/g34/g52/g84/g100/g200 and ThinkPhone (ThinkPhone may need a rollback-index adjustment), Nothing Phone (1)/(2)/(3)/(3a)/(4a), Sony Xperia 1 II/1 V/1 VI/5 IV/10 V, Razer Phone 2, OnePlus 6/6T; "not working" lists newer OnePlus (may fail to boot or brick), Nothing (2a), and Xiaomi (key flashable but not honoured). **Samsung and ASUS do not appear in the issue at all**: they are excluded for unlock policy, not for failed relock tests. The wall-of-shame README itself only says custom-key devices are "rare" and points to issue 299. Fairphone detail: Fairphone's own support page requires a per-IMEI/serial unlock code and a two-step `flashing unlock` then `flashing unlock_critical`; several FP6 community threads report OEM-unlock blocked or soft-bricked units, and one forum report says an official-tree FP6 relocks with a custom key only if the vbmeta is built with verification enabled (flags 0, `WITH_AVB=true`) [SECONDARY, search summaries]. This is encouraging but not a qualification result for Gen 6+. The two-step unlock means the relock sequence on Fairphone probably differs from Pixel's single `flashing lock` [INFERRED], one more reason the installer needs a per-device adapter. Carrier-financed phones are mostly locked (Verizon now requires payoff, or 12 months prepaid) [SECONDARY: broadbandbreakfast.com]. **The pool is mostly newly bought unlocked phones**, so "no hardware" really means "no inventory".

### F4. How others distribute and what they charge
| Project | Model | Charge |
|---|---|---|
| GrapheneOS | Pixels only; web and CLI installers; resellers independent | Free, donations [PRIMARY FAQ] |
| LineageOS | Community maintainers; 293 entries on 23.x; no official Android 17 builds | Free [PRIMARY data] |
| CalyxOS | Pixel, Fairphone, some Motorola; web installer (Pixel, Motorola) | Free; membership $700 yr 1 with Pixel 8a, then $10/yr [SECONDARY] |
| /e/OS (Murena) | 30+ devices DIY; sells Fairphone 6 preinstalled | Free; EUR 649 phone; cloud EUR 1.99-24.99/mo [SECONDARY] |
| iodé | 40+ devices; install service only in Toulouse | Free; Premium EUR 3.99-6.99/mo [SECONDARY] |
| Pinwheel, Troomi, Gabb | Rebadged hardware plus subscription; Pinwheel refuses BYO | $15-25/mo [SECONDARY via 02, 12] |

**No commercial BYO kids'-OS vendor found** [SECONDARY, negative result]. Bark ($14/mo), Qustodio (~$55-100/yr) and free Family Link are the BYO price anchors. **[CORRECTED]** Second-pass search summaries (vendor pages blocked, so [SECONDARY] and UNVERIFIED at source): Bark Premium is $14/mo or $99/yr (Bark Phone wireless plans $29-79/mo); Pinwheel is a $15/mo subscription, extra line $5, cellular separate; Troomi plans are $24.95/$29.95/$34.95 per month and Gabb from $29.99/$34.99 per month, both including cellular, so the table's "$15-25/mo" understates them and those two are not like-for-like with a software-only price. Pinwheel's own FAQ is reported to say its OS cannot be installed on your own phone (consistent with the table). Google has announced Android 17 built-in parental controls for all Android 17 devices (search summary of blog.google), which raises the free-alternative bar for the $12.99/mo anchor. CalyxOS $700 first year then $10/yr is confirmed [SECONDARY]; /e/OS, iodé and Murena prices were not re-checked.

### F5. Installer facts
- GrapheneOS's installer is `fastboot.js` (MIT) in the browser: `product` in a 21-codename allowlist, `unlocked` check, `flashing unlock`, download to browser storage, `snapshot-update:cancel`, `flashFactoryZip` (firmware, reboot, OS, `avb_custom_key`), `flashing lock`; setup then offers to disable OEM unlocking [PRIMARY: GrapheneOS/grapheneos.org@main:static/js/web-install.js]. Its pre-flight is thin.
- Documented failure modes: 2 GB RAM, 32 GB disk; Chromium only (no Snap/Flatpak, no private mode); Windows driver; Linux udev and `fwupd`; hubs and cables ("most common source of issues"); no VMs; carrier variants block unlock; the unlock toggle needs internet; it can run from an Android phone [PRIMARY: static/install/web.html]. Firefox and Safari lack WebUSB [SECONDARY]. **[CORRECTED]** The same page says current Windows 10/11 need no separate fastboot driver (only outdated Windows does), so "drivers" is a lesser failure cause than cables/hubs, which it calls "the most common source of issues". Its Android-host option requires Android 14-17 "with Play Protect certification" (or GrapheneOS/ChromeOS), which a Zune handset can never be, so a parent needs a different phone. Its supported-device allowlist has exactly 21 codenames including `tegu` (9a) and `stallion` (10a); adevtool@17 has `stallion.yml` (US ODM SKU GE1GQ) and `tegu.yml` (US SKU GXQ96) [PRIMARY]. The JS itself only issues `flashing unlock`, `snapshot-update:cancel`, `flashFactoryZip` (the `avb_custom_key` step lives in the vendored fastboot.js flow and the factory zip, labelled "verified boot key" in the UI), `flashing lock` and `erase:avb_custom_key`.
- Standard fastboot variables are only `version`, `version-bootloader`, `version-baseband`, `product`, `serialno`, `secure`, `is-userspace`, `is-logical`; everything else is OEM-specific, so each device needs an adapter [PRIMARY: LineageOS/android_system_core@lineage-24.0:fastboot/README.md]. The Updater and adevtool are MIT [PRIMARY]. Losing the AVB key forces unlock and wipe on every device [PRIMARY: avbroot README].

### F6. Attestation
RootOfTrust carries `verifiedBootKey`, `deviceLocked`, `verifiedBootState` [MEMORY; schema page blocked]. A new ECDSA root signs chains from 2026-02-01; trust both roots [PRIMARY: developer.android.com/privacy-and-security/security-key-attestation]. Recent devices fetch attestation keys from Google's remote provisioning; GrapheneOS proxies it, and a non-Google OS "would need their own service" [PRIMARY: FAQ].

### F7. Law (all [SECONDARY] search summaries unless noted; counsel to confirm)
- **FCC:** software changes that do not affect RF need no new filing; a third party altering RF behaviour becomes responsible. We keep modem and Wi-Fi firmware untouched.
- **CPSIA:** "children's product" = a "consumer product" (an "article") designed or intended primarily for children 12 or under; no CPSC guidance found on software or general-use phones marketed to kids. Risk rises if we hand back a phone marketed as a kids' product.
- **Liability:** Magnuson-Moss bars voiding a warranty for third-party software unless it caused the defect. UK CRA 2015 s.46: digital content that damages a consumer's device through lack of reasonable care means repair or compensation. EU Directive 2019/770: updates for the period a consumer may reasonably expect. EU CRA reporting is live since 2026-09-11 (rest 2027-12-11); Product Liability Directive 2024/2853 covers software placed on the market after 2026-12-09, including missing security updates.
- **Unlocking:** the DMCA s.1201 jailbreak exemption (renewed Oct 2024) covers the act, not trafficking in tools; OEM-sanctioned unlock is not circumvention. **Sanctioned paths only; never exploit-based unlocks (EDL, Qualcomm GBL)** [INFERRED, counsel].
- **Sales:** FTC click-to-cancel vacated July 2025; California's amended ARL (2025-07-01) requires online cancellation and annual reminders. Merchants of record (Paddle, Lemon Squeezy) charge about 5% + $0.50 and handle VAT and sales tax. Platform-TLS apps are likely ECCN 5D992.c or EAR99. Google bars "Android" in product names; say "built on the Android Open Source Project" [SECONDARY].

## 3. Options & trade-offs
| Option | What ships | Legal | Relock | Updates | Cost | Verdict |
|---|---|---|---|---|---|---|
| (a) System-only on stock vendor | system, system_ext, product | Cleanest | Needs custom-key support and re-signed vbmeta | Vendor, firmware frozen | Low-mid | Dev tool |
| (b) OEM firmware fetched at flash time, flashed unmodified, digests pinned in our vbmeta | Our partitions only | Strongest; flashing for the owner fits "personal device" use | Yes, unproven [INFERRED]: prototype on a sacrificial unit | Frozen until re-flash (wipe) | Mid-high | **v1 posture** |
| (c) Blobs in our OTA (GrapheneOS model) | Everything, one signed OTA | Needs OEM licence; tolerated for non-profits | Yes | Full | Mid (Pixel adevtool) | **Needed before OTA firmware** |
| (d) LineageOS-style tree (Snapdragon) | Blobs, vendor kernel | As (c) plus GPL kernel source | Not default | Firmware in 184 entries | High (about 1 FTE-quarter per device) [INFERRED] | Stage 2 |

## 4. Recommended Stage-1 design

**Stage-1 MVP:** a station-mode web installer for one Pixel platform (9a/10a) with strict pre-flight, relock and attestation check; manual qualification against the DSC; our OTA server (staged rollout, health gating); licence and subscription through the parent portal with a merchant of record; written OEM outreach running in parallel. Self-install, extra devices and OTA-delivered firmware wait for Stage 2 or gate G5.

### 4.1 Provisioning station (v1) and installer
Intake and operations are report 18's; the technical flow:
1. **Eligibility:** model and SKU lookup; US unlocked units only (carriers whitelist IMEI ranges of locally sold SKUs [PRIMARY: GrapheneOS usage.html]); owner requests any OEM unlock code; signed consent (two wipes, warranty, custody; accounts and screen lock removed).
2. **Pre-flight (block, do not warn):** `product` in allowlist; `secure`; `unlocked`; `version-bootloader` and `version-baseband` not newer than the pinned build (flashing an older bootloader after an anti-rollback bump can brick; Pixel 6 precedent [SECONDARY]); slot and `snapshot-update-status`; SKU and carrier id via adapter; host checks (Chromium, disk, no hub).
3. Unlock (wipe), flash firmware, reboot, OS, `avb_custom_key`, lock (wipe), boot. Release signed (Ed25519) and hash-checked.
4. **Verify by attestation at the station:** both roots, `deviceLocked=true`, SelfSigned, our key hash, patch level. Set OEM unlock off; register serial hash and attestation as "unclaimed" (05); QA script; hand over with a claim QR.
5. **v2 self-install:** same flow in the customer's browser or on a parent's Android phone. Unlike 05's "alert, don't gate", I recommend **gating the claim on attestation**, since no station evidence exists; our image must set the RKP host (05) or run a proxy.
6. **Safeguards:** opt-in telemetry, error codes only (no IMEI or serial); "return to stock" guide (erase `avb_custom_key`, flash stock via Google's web flasher [PRIMARY: GrapheneOS install page]); portal "Release device" sends a signed token that re-enables OEM unlocking, so owners can exit or trade in.
7. Support load [INFERRED]: self-install 20-30% need help (about $4-6 blended); v1 station $25-40 per unit.

### 4.2 Device Support Contract and qualification (extends 15)
- MUSTs: US unlocked SKU; sanctioned unlock without waits (bulk-requestable codes acceptable); custom-key relock verified on **our** build; A/B; GKI 6.1+; working attestation/RKP; VoLTE on two US carriers or MVNEs; E911 and WEA tests (12); 5+ years OEM support left; **written OEM redistribution terms (gate G5) before any OTA carries OEM firmware**.
- Per-release matrix: installer on four host OSes; relock; camera, audio, Bluetooth, Wi-Fi, GPS, charging; calls, SMS, MMS, VoLTE, WEA; OTA A to B with firmware, power loss, rollback; 72 h soak. Cost [INFERRED]: sibling model 1-2 engineer-weeks, new platform 4-6, 3 units (about $1.2k), 2-3 days per monthly release, carrier testing $5-15k.
- Capacity [INFERRED]: one commercial platform plus Pixel as beta/fallback in Stage 1; at most three by end of Stage 2 (GrapheneOS: Pixels only, full team; LineageOS: 293 entries via community maintainers).
- Governance: add by written proposal (owner, gates, 3 units); remove at OEM support end, SLA breach or unfixed relock regression; hold each OEM firmware update until it passes the relock test. **EOL promise** [INFERRED]: updates at least 3 years from listing, never past OEM support; 12 months' notice; pro-rata refund; final OTA, then safe mode.

### 4.3 Updates
- One A/B `update_engine` channel per codename; fork the MIT Updater; signed full OTAs with downgrade-blocking metadata; AVB rollback index bumped only for security fixes and after a healthy staged cohort. Rollout 1/10/50/100% over 7 days with a kill switch; a health service marks the slot good, else A/B reverts. Roll forward, never back.
- Firmware: v1 by re-flash service until G5 is signed, then in the OTA. Target monthly; promise "within N days of AOSP publication" until partner access (01, 10).
- **Accidental OEM OTA:** our image has no OEM updater; a locked bootloader blocks `fastboot flash`; recovery trusts only our cert. The risk exists only on unlocked phones, another reason relock is mandatory.
- **Bricking:** our-defect bricks get a full refund plus capped goodwill (decision 6); customer deviations do not; statutory rights untouched. With OEM unlocking disabled, a bad dual-slot OTA is unrecoverable (avbroot warning), hence health gating.

### 4.4 Licence, entitlement, pricing
- Default [INFERRED]: **$59 one-time provisioning (v1; $0-29 in v2) plus $12.99/mo or $119/yr per child**, family cap, 30-day refund (covers EU withdrawal). Anchors: Bark $14, Pinwheel $14.99, Troomi $19.95, Gabb $20-25 (with hardware); Family Link free. Cellular is a pass-through (12).
- Entitlement: one seat per attested device key; periodic re-attestation; 14-day offline grace (12's policy expiry).
- **Lapse = safe mode:** AI, messenger, video, walkie-talkie and curated video stop; guardian and emergency calls keep working from the last signed policy (deny-by-default); 911 always; security updates continue 12 months; 30-day data export.
- Piracy: assume the image leaks. No secrets in image or installer; apps need cloud; signed per-order links; mTLS device certs. **Protectable:** closed apps, backend and curated catalogue, brand, qualification know-how. Not protectable: AOSP and GPL parts (freely redistributable, so the EULA restricts only proprietary Zune components and the service) and the public installer JS.
- EULA: licence not sale; open-source carve-out and GPL notices; wipe, unlock and warranty warnings; no OEM or Google affiliation, OEM names used factually; liability cap with consumer-law carve-outs. Parent is sole purchaser via a merchant of record; a card transaction may serve as COPPA parental consent [MEMORY, counsel].

### 4.5 Compliance shift
| Disappears | Remains | New under D15/D16 |
|---|---|---|
| FCC/PTCRB/CE-RED as manufacturer; hardware CPSIA testing; inventory, RMA | COPPA/GDPR; GPL notices; carrier acceptance (stock modem/IMS bytes, IMEI-by-model); E911/WEA; export; MVNE duties (12) | Custody and shipping of customer phones; wipe consent; warranty and bricking exposure; unlock-instruction legality; EU CRA/PLD/DCD if sold in EU; kids'-phone marketing claims (FTC Act) |

## 5. Stage-2 improvements
Customer self-install web installer (v2); desktop app (platform-tools bundled, Firefox/Safari users, OEM portals, offline bundle); second platform through 15's gates (Nothing Phone (3), Motorola Signature 27); OEM redistribution deals; partner install network; refurbished-device partners; school and IT bulk licences; incremental OTAs; per-build watermarking; publish OS-layer patches for trust; EU launch with CRA/DCD files.

## 6. Conflicts with earlier reports and decisions
- **02:** BYO was rejected; D15/D16 require it. Re-evaluated: it works only as qualified-SKU provisioning, never "any Treble phone" (F2-F3). Hardware float, bundle pricing and ODM gate are moot; its Device Support Contract stands; its blob-licence risk (F5) now concerns OTA redistribution.
- **15:** its $650-900 hardware-bundle pricing conflicts with D15; replaced by software pricing. I keep its DSC and Fairphone preference but order work Pixel first (tooling) with Fairphone commercial only after written terms and a relock pass; its "OEM written permission to redistribute firmware" MUST is my gate G5.
- **05/16/18:** attestation "alert, not gate" holds for v1 (we gate at the station); I recommend gating self-install claims, and 05's empty RKP host must be set in our image. Settings needs a parent-gated "check for update / release device"; station operations are 18's.
- **04:** "pre-flashed relocked only" is confirmed. Honest claim: tamper-evident and resistant to a child without a computer, not unbreakable. A stock reflash needs the OEM-unlock toggle (absent in our build) plus a wipe; a stopped heartbeat alerts parents.
- **12:** VoLTE/IMS and eSIM stay stock only if shipped from the stock image (G5). BYO needs US SKUs and a qualified list shared with the MVNE.
- **01/10:** our OTA carries firmware; the AVB key is effectively unrotatable (rotation needs unlock and wipe): keep it in an offline HSM, use a separate rotatable OTA key; compromise is recall-class.

## 7. Risks & unknowns
1. Google's licence for commercial Pixel firmware redistribution; Fairphone's terms unsigned (high). Fallback: re-flash service, then pause.
2. RKP attestation depends on Google's service or our proxy (high).
3. Fairphone Gen 6/6+ relock unverified; OEMs can remove custom keys in later bootloaders (high).
4. Custody of customer phones, support load, bricking liability; estimates unvalidated (medium-high).
5. Android 17 kernel floor and AOSP facts unchecked at source; Chromium-only installer (medium).
6. Counsel: CPSIA framing of a returned kids' phone, FCC, EU CRA/PLD/DCD, ARL, DMCA, export, COPPA consent (medium).

## 8. Decisions needed from the founder (by impact)
1. Authorise counsel plus Google, Fairphone, Nothing and Motorola outreach on firmware redistribution. Default: yes; no OTA with OEM firmware and no public launch before an answer; private beta up to 100 devices.
2. Relock mandatory for "Zune Ready" (A7). Default: yes, no unlocked tier.
3. Launch device order. Default: Pixel 9a/10a for engineering and beta; Fairphone Gen 6+ commercial if terms and relock pass; else Pixel under Google's answer.
4. Pricing. Default: $59 provisioning plus $12.99/mo or $119/yr per child, 30-day refund.
5. Lapse policy. Default: safe mode, emergency and guardian calls always, security updates 12 more months.
6. Brick policy. Default: full refund plus up to $300 goodwill for our defects; reserve 1% of revenue [INFERRED].
7. Custody terms for v1. Default: customer-supplied phones, insured shipping or drop-off, signed wipe consent; we never sell handsets.
8. Uninstall path. Default: portal "Release device" plus return-to-stock guide.
9. Open-source posture. Default: GPL-required source only; revisit in Stage 2.
10. Launch market. Default: US only; EU after CRA/DCD review.

## 9. Load-bearing claims
1. Pixel images and binaries are personal-use, non-modifiable, non-redistributable except per an enclosed (unread) licence. [SECONDARY] developers.google.com/android/images, /drivers (snippets).
2. GrapheneOS's installer is WebUSB `fastboot.js` with a codename allowlist and flash/lock sequence. [PRIMARY] GrapheneOS/grapheneos.org@main:static/js/web-install.js.
3. A custom AVB key boots built-in and custom-signed images when locked; yellow state; Pixel `avb_custom_key` writable only unlocked; a lost AVB key forces unlock and wipe on every device. [PRIMARY] LineageOS/android_external_avb@lineage-24.0:README.md; chenxiaolong/avbroot README.
4. Custom-key relock is rare: Pixel documented; Fairphone, Nothing, Sony, Motorola reported; OnePlus, Xiaomi, Samsung, ASUS out. [SECONDARY] avbroot issue 299; zenfyrdev wall-of-shame.
5. LineageOS data: 374 of 743 entries need specific OEM firmware first; 184 ship it. [PRIMARY] LineageOS/lineage_wiki@main:_data/devices.
6. Attestation needs Google remote provisioning or our own service; new ECDSA root from 2026-02-01. [PRIMARY] GrapheneOS FAQ; developer.android.com/privacy-and-security/security-key-attestation.
7. Android 17 accepts vendors from FCM level 7; GSIs are non-production, non-redistributable. [PRIMARY] GrapheneOS/platform_hardware_interfaces@17:compatibility_matrices/Android.bp; developer.android.com/topic/generic-system-image.
8. Standard fastboot variables are minimal, so per-device adapters are needed. [PRIMARY] LineageOS/android_system_core@lineage-24.0:fastboot/README.md.
9. FCC software-change rule, CPSIA "article" wording, EU CRA/PLD dates, UK CRA s.46. [SECONDARY] search summaries (sources blocked).
