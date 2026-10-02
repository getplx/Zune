# 21. Own-hardware roadmap, India: from flashing customers' Pixels to our own device (D21)

Date 2026-10-02. Tags: **[PRIMARY]** real source file read this session (repo@ref:path); **[SECONDARY]** press, vendor page or search summary; **[INFERRED]** my judgement or arithmetic; **[MEMORY]** unchecked training knowledge. **Evidence limit:** `android.googlesource.com` and `source.android.com` returned 403 (tested once, not worked around). WebFetch was egress-blocked for every site tried (BIS, TEC, MediaTek, Indian press), so market, regulatory and vendor facts are WebSearch summaries; a BIS consultant and counsel must confirm them. Code facts come from a GrapheneOS `17` mirror, not Google's tree. FX about 96 INR/USD (report 20). No earlier report 21 existed.

## 1. Summary & recommendation

1. **Own hardware is a gated phase, not a date.** Run the 200-family Pixel phase (report 20) first. Send paper RFQs and build hardware-ready foundations (4.2) now; commit money only after the gates in 4.3.
2. **First own device: a rebadged, ODM-platform, 4G LTE data phone** on a Snapdragon 4 Gen 2 or 6-series class SoC (QCM6490 if budget allows), not a custom-designed phone. Precedents: HMD Fusion X1 and Light Phone III both use Snapdragon 4 Gen 2 [SECONDARY]. A custom ODM design (option b) waits for visible demand of 10k+ units a year.
3. **The case is price and tamper-proofing, not margin.** A Pixel 10a costs INR 47,999 (about 39,999 on sale), capping the funnel at the premium tier (report 20). An own device at INR 15-18k widens it, and fused keys allow a bootloader with no unlock path. The subscription earns the money, not the hardware [INFERRED].
4. **The central risk is patching, and it is worse in 2026.** Entry SoCs are outside Google's long-support programs, so we own kernel, firmware and HAL patch ingest. A memory shortage also raised low-end bills of materials about 25% in 2026, and Nothing cancelled its CMF Phone 3 Pro over memory cost [SECONDARY]. Promise **3 years of security patches**, not 7.
5. **No Indian incentive fits a small brand** [SECONDARY]: PLI ended 31 Mar 2026 and its replacement needs INR 1,000 crore turnover. Compliance (BIS, WPC, IMEI/TAC, EPR) is paperwork of about 3-5 months, parallel to DVT.
6. **Wi-Fi-only is the real regulatory simplification; a "data-only" cellular phone is not** (the modem stays, so IMEI and TAC stay). Make Wi-Fi-only a Stage-2 SKU.
7. **Settle the product name first** (BIS, TAC, WPC and EPR filings are brand-specific) and keep every signing key away from the ODM.

## 2. Findings

### 2.1 Platform, BSP and update lifetimes
- **Android 17 accepts old vendors.** The system matrix set is FCM levels 7, 8, 202404, 202504, 202604 (Android 13-17 vendors); kernel configs 5.10/5.15, 6.1, 6.6, 6.12, 6.18 [PRIMARY: GrapheneOS/platform_hardware_interfaces@17:compatibility_matrices/Android.bp; matches report 15]. An Android 14/15 vendor BSP can therefore carry our AOSP 17 system. Not checked against Google's tree.
- **Long support is for flagships.** Google's Longevity GRF started with Snapdragon 8 Elite; Google supports its kernel forks only about four years, so OEMs must bump the kernel after three [SECONDARY: https://www.androidauthority.com/android-longevity-grf-3493006/]. MediaTek's eight-year program covers Dimensity 9400/8400 and later premium parts [SECONDARY: https://www.mediatek.com/tek-talk-blogs/mediatek-extends-software-support-for-dimensity-powered-android-devices]. Entry chips are not listed (Samsung's six-year promise on the Dimensity 6300 M17e is Samsung's own) [SECONDARY].
- **IoT-grade silicon has real longevity.** MediaTek Genio 510/700: Android 15 available, 3 Android upgrades with vendor freeze, 3 years of security patches after the last upgrade, 4 years of BSP updates, 10-year chip lifecycle [SECONDARY: https://genio.mediatek.com/genio-510]. These have no integrated cellular modem [MEMORY], so they suit a Wi-Fi device. Qualcomm QCM6490: Fairphone 5 promises updates to 2031, but Android 16 on it needs a full VSR rework and kernel update, which shows the ODM-side cost [SECONDARY: https://9to5google.com/2023/08/30/fairphone-5-updates-specs-release-date/ ; https://forum.fairphone.com/t/android-16-for-fp5-what-we-know-so-far/130508].
- **BSP access.** Full Qualcomm BSPs need a software licence (Create Point); practical routes are an ODM licensee, Thundercomm or an OEM partner (report 15). Wingtech, Huaqin and Longcheer hold about 76% of ODM shipments for Samsung, Xiaomi and Oppo [SECONDARY: eetasia.com]; I found no small-brand MOQ for them. Tier-2 houses (Tinno), Dixon-Longcheer's "Dixtel" JV (74/26, approved July 2025) and Optiemus (Nothing's Chennai partner) are likelier fits [SECONDARY: business-standard.com; telecomlead.com].
- **Precedents.** Light Phone III: Foxconn-built, Snapdragon 4 Gen 2, company raised USD 12.7M [SECONDARY: Wikipedia, Tracxn]. HMD Fusion X1, a kids' phone with Xplora: Snapdragon 4 Gen 2, 6 GB/128 GB, EUR 269.99 [SECONDARY: https://www.hmd.com/en_int/press/hmd-fusion-x1-press-release].

### 2.2 Secure boot and unlock paths
- **Qualcomm:** the OEM root hash is fused (OEM_PK_HASH); EDL then needs a Firehose programmer signed to it [SECONDARY: https://docs.qualcomm.com/bundle/publicresource/topics/80-70020-11/sign-and-flash-images.html]. On our hardware only our programmer loads, but the March 2026 ABL "GBL" bug shows bootloader code, not fuses, decides lock strength (report 15).
- **MediaTek:** BootROM glitching and `mtkclient` bypass SLA/DAA on many parts; newer SoCs are patched and some OEMs disable BROM USB download [SECONDARY: https://www.nccgroup.com/research/there-s-a-hole-in-your-soc-glitching-the-mediatek-bootrom/]. Verify per SoC revision.
- **Unisoc:** BootROM bug CVE-2022-38694 loads unsigned FDL1 and unlocks T606, T615 and T7510 devices [SECONDARY: https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader]. **Reject Unisoc** for a tamper-resistant child device.
- **Own-hardware advantage** [INFERRED]: fuse our root key at the factory, blow debug fuses, compile `flashing unlock` out of the bootloader (stronger than relock), boot green not yellow, and use a signed service-unlock token. Fused keys are permanent, so custody (report 10) must exist before first fusing.
- **Attestation:** Android 16+ launch devices are RKP-only and whether Google's backend serves a non-GMS OS is unverified (report 10 F12). Own hardware needs its own RKP backend and root, or a Google agreement [INFERRED].

### 2.3 India compliance for us as brand owner (cellular phone; Wi-Fi-only noted)
| Item | What I found | Basis |
|---|---|---|
| BIS CRS | IS 13252 (Part 1) for phones, tablets and adapters; IS 16046 for Li-ion cells. Foreign factory needs an Indian representative; licence in the manufacturer's name. Govt fee INR 53,000 plus lab INR 10-80k; 30-45 working days; valid 2 years. https://www.elitasrcs.com/products/bis-registration-for-mobile-phones-is-13252-part-1 | SECONDARY |
| WPC ETA | Wi-Fi/Bluetooth by self-declaration (1-3 working days); cellular needs a separate approval route (unclear). 6 GHz de-licensed Jan 2026. https://eservices.dot.gov.in/equipment-type-approval-eta | SECONDARY |
| TEC MTCTE / ITSAR | Smartphones do **not** appear in MTCTE phases I-VI (per phase lists; confirm with TEC). 83 smartphone ITSAR requirements are proposed, not notified; the source-code-access idea was denied. Monitor. https://www.tuvsud.com/en/knowledge-hub/technical-updates/consumer-products-and-retail-essentials/india-products-under-phase-vi-of-mtcte-published | SECONDARY |
| IMEI/TAC | Register every IMEI on the ICDR portal before first sale, testing or R&D; TAC from GSMA (USD 400 each, 2019 fee; India TACs start 35). Tampering is an offence (report 19). https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190763&reg=48&lang=2 | SECONDARY |
| SAR | 1.6 W/kg per 1 g; TEC 13016:2020 covers body-worn Wi-Fi devices; SAR must be shown on the handset like the IMEI. https://tarangsanchar.gov.in/EMFPortal/DoT/SARLimitsforMobileHandsets | SECONDARY |
| Panic button, GPS | Smartphones: triple power-press panic, GPS mandatory (2016 Rules). Whether a voice-less device is a "handset" is a counsel question. https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=142272&reg=48&lang=2 | SECONDARY |
| E-waste, battery EPR | Producer registration on CPCB portal; recycling target 70% (FY25-27), 80% from FY27-28. Battery Waste Rules 2022 separately cover brand owners of embedded batteries. https://www.legalraasta.com/blog/epr-rules-for-e-waste-india/ | SECONDARY |
| Legal Metrology | Box: MRP incl. taxes, manufacture month/year, importer, origin, care contact. | SECONDARY |
| Duty and GST | BCD on finished phones 15% (cut from 20% in July 2024; one summary says 20% again in 2026: verify), plus 10% surcharge on BCD; IGST 18%; kits and PCBA about 10%. | SECONDARY, conflicting |
| Warranty, repair | Consumer Protection Act 2019 liability (report 19); Right to Repair portal is voluntary, with a repairability index. https://thebetterindia.com/291102/right-to-repair-smartphone-gadgets-manufacturers-things-to-know/ | SECONDARY |
| Later markets | US CPSIA, FCC, PTCRB; EU RED/EN 18031, CRA (report 02) | MEMORY |

### 2.4 Incentives
PLI for phones ended 31 Mar 2026. The Mobile Phone Manufacturing Scheme (INR 62,500 crore, FY27-31, approved 15 Jul 2026) pays 2.25-5% of eligible sales plus 3% for Indian design/R&D. **Track 1 needs INR 10,000 crore turnover; Track 2 (Indian brands) INR 1,000 crore and over 51% Indian ownership** [SECONDARY: https://www.pmindia.gov.in/en/news_updates/cabinet-approves-mobile-phone-manufacturing-scheme-mpms/ ; https://www.businessworld.in/article/rs-62-500-cr-mobile-manufacturing-scheme-targets-india-s-next-electronics-push-625582]. ECMS targets component makers [SECONDARY]. A startup gets none; only a partner EMS might pass savings through.

### 2.5 Cost and market inputs
- Vendor figures (low reliability): ODM FOB USD 48-115, MOQ 3-5k, "typical ODM launch USD 215k" (NRE 95k, certification 70k, pilot 50k, breakeven about 22k units) [SECONDARY: report 02; Alibaba guides]. Report 02's own estimate: USD 0.5-1.5M, 12-24 months [INFERRED].
- **Memory:** mobile DRAM about doubled in Q2 2026 (LPDDR4X 4 GB +75%); memory is 43-45% of a low-end BoM; sub-INR 10k phones rose about 32% and shipments fell 65% in H1 2026 [SECONDARY: https://www.digit.in/news/mobile-phones/smartphone-prices-surge-in-india-as-memory-costs-soar-budget-phones-hit-hardest-report.html ; https://wccftech.com/mobile-dram-prices-expected-to-increase-by-100-quarter-over-quarter-as-long-term-agreements-now-getting-signed-at-prices-as-high-as-21-gb/]. Small brands get no allocation priority [INFERRED].
- **Price anchors:** CMF Phone 2 Pro (Dimensity 7300 Pro) INR 18,999-22,999; CMF Phone 3 Pro cancelled for 2026 on memory cost [SECONDARY: smartprix; mobigyaan]. Motorola g-series: official unlock, but 1 OS upgrade and about 3-4 years of patches [SECONDARY].

## 3. Options & trade-offs

| Option | BSP and licence | Updates and patches | Tamper and keys | Cost and time [INFERRED unless tagged] | Verdict |
|---|---|---|---|---|---|
| (a) Rebadged ODM platform (Dixtel, Optiemus, Tinno-class) | ODM sublicenses the BSP; demand source escrow | A14/A15 vendor under our A17 system; patches by contract; 3-year promise | ODM fuses our key hash | F about USD 0.25M, lots of 1-3k; 12-16 months from RFQ to pilot lot (optimistic; report 02 says 12-24) | **First device** |
| (b) ODM-designed kids device (SD 7-series, QCM6490, Dimensity) | Same, plus PTT and SOS keys, sealed SIM | 4-year BSP typical, negotiable | Full control | F about USD 1.5M; 24-36 months | Only at 10k+/yr visibility |
| (c) Wi-Fi (+LTE) tablet or phone-like device (Genio 510/700) | MediaTek Genio, 10-year lifecycle | Best on paper: 4-year BSP | Avoid Unisoc | Lower BoM; no IMEI/TAC/cellular approvals; conflicts with D14 | Stage-2 "home" SKU |
| (d) OEM partnership (Fairphone-style, Nothing, Lava, HMD) | OEM keeps BSP and keys | OEM cadence | OEM rarely cedes keys [INFERRED] | Fairphone not in India (report 20); HMD uses its own software | Fallback |

**Data-only hardware (D19).** Dropping voice saves little BoM (the modem sits in the SoC). It skips IMS/VoLTE interoperability work (Jio is VoLTE-only, report 20), but IMEI, TAC, SAR and panic-button duties stay and 112 voice is lost (A9). Jio data without VoLTE reportedly works [SECONDARY: gizbot, jio.com]; untested for our build. **Recommendation:** keep a voice-capable modem, voice off except 112, decided on report 20's carrier matrix. A Wi-Fi-only device avoids IMEI, TAC, cellular certification and SIM tamper, at the cost of D14 and commute use.

**Alternatives without hardware.** (1) Snapdragon candidates (report 15) cost INR 40-65k: they fix supply risk, not price. (2) A cheaper India-sold phone (CMF Phone 2 Pro, Motorola g) qualified under the Device Support Contract tests price elasticity for about USD 30-60k [INFERRED], but patch windows are short and relock unproven. (3) Staying on Pixel keeps the best patch position (to 2032-33) at a INR 40k+ entry price.

**Own hardware wins when all hold** [INFERRED]: price is the top reason for lost families; retention and patch gates pass; 10k+ units a year look reachable within 18 months; no relocked retail phone meets a tamper requirement we need; USD 1M+ is committed; Pixel firmware redistribution (reports 17-18) is still unresolved.

## 4. Recommended Stage-1 design

### 4.1 Unit economics (all [INFERRED]; USD 1 = INR 96, GST creditable)
Assumptions: landed cost USD 115 (range 95-150) per phone; MRP INR 16,999 incl. GST (net 14,406); 6% warranty reserve (children drop phones), 3% payments and logistics, giving about INR 2,070 (USD 21) hardware contribution. Subscription INR 399/month, net 338, minus cloud about 190 (report 20) and payment fee 8 = INR 140/month; 2.5 paying years = USD 44. **Contribution m is about USD 65 per unit.** Pixel path for comparison: about INR 2,000 in year one, 1,700 a year after, no capex, but a INR 40k+ phone.

| Lifetime units | Path | Fixed F | Team 3 yrs | Peak working capital | Contribution | Net |
|---|---|---|---|---|---|---|
| 1,000 | (a) pilot lot | 0.25M | 0.30M | 0.12M | 0.07M | -0.49M |
| 10,000 | (a) in lots of 2-3k | 0.25M | 0.30M | 0.3-1.2M | 0.65M | about +0.1M (breakeven about 8.5k) |
| 100,000 | (b) | 1.5M | 1.2M | 3-5M | 7M (m about 70) | +4.3M (breakeven about 39k) |
USD. Supplier terms about 30% deposit, 70% before shipment [MEMORY]: cash leaves roughly 100 days before the first sale.

### 4.2 Do from day one (keeps own hardware possible)
1. **Device-agnostic layer:** the `vendor/zune/devices/<codename>` shim rule (reports 02, 03), public SDK only, no Pixel or Tensor dependencies in apps.
2. **Keys:** a separate hardware root key under HSM with two-person custody before any ODM contact (report 10); one AVB key per model chained under it; the ODM gets only the public hash. Check the SoC's allowed algorithm and key size first.
3. **OTA** that already updates modem, bootloader and vendor partitions, keyed by codename; roll-forward only (report 10).
4. **Secure Hardware Contract (SHC),** a superset of report 15's Device Support Contract and the RFQ spec: fused root and debug off; signed BROM/EDL path; no unlock command; RPMB rollback; green boot; source and escrow for bootloader, kernel and HAL; no ODM pre-installs; patch SLA (critical fix to OTA within 30 days of vendor release); 4-year BSP; 3-year RMA. Reuse the DSC tests and report 18's station as acceptance tests.
5. **Paper RFQs** (no NRE) to Dixtel, Optiemus, one Tier-2 house and one Shenzhen design house: SoC, BSP Android version, kernel, EDL/BROM status, MOQ, memory allocation, lead time.
6. **Foundations:** Indian Pvt Ltd (report 19), IEC code, product name and trademark (A5), BIS and EPR consultants, counsel gates G1-G10.
7. **Pilot telemetry for hardware:** drop and repair counts, call battery life, thermals, drop-off reasons, privacy-reviewed (DPDP). Third-party audit of vendor blobs (2016 Adups OTA backdoor precedent [MEMORY]).

### 4.3 Gates (from the 200-family phase)
| Gate | When | Pass |
|---|---|---|
| H1 start RFQ negotiation | end of C1, about M5 | D30 retention 85%+; first-pass flash 95%+; price is the top lost-family reason for 40%+ of drop-offs; 3,000 non-binding waitlist sign-ups from families without a qualified phone |
| H2 commit EVT funds (USD 0.5M) | end of C2, about M9 | OTA success 98% in 72 h; median patch lag under 30 days for 3 straight months; zero unrecovered bricks; under 2 support contacts per family per week; red-team shows zero open no-browser/no-YouTube bypass; counsel gates closed; SHC signed by an ODM; key ceremony rehearsed |
| H3 first PO | after DVT, about M15 | BIS, WPC, TAC and EPR done; independent tamper test passed on 300-500 pilot units; memory allocation secured |
| H4 scale (option b) | 1,000 units in field | W8 retention 75%+, returns under 6%, support under INR 150 per device per month, patch SLA met, 10k units a year visible |

### 4.4 Timeline (months from Oct 2026)
M0-3 C0, foundations, RFQs out. M3-6 C1; optional cheap-tier phone qualification. M6-10 C2/C3; ODM shortlist and boards. M10-12 EVT. M12-15 DVT and certification in parallel (about 3-5 months). M15-16 pilot lot. M16-20 limited sale of 1,000. M20-30 decide (b); first custom units about M30-36 [INFERRED].

## 5. Stage-2 improvements
Wi-Fi-only "home" SKU on Genio; custom (b) design with hardware PTT and SOS keys, charge-only USB, camera and mic switches, sealed SIM or eSIM with our LPA; own RKP backend; kernel LTS bump at year 3; second ODM; EU/US variants (CPSIA, RED, CRA); repair network.

## 6. Conflicts with earlier reports
- **02:** the "25k units/yr, USD 1.5M" gate is too coarse (a rebadge breaks even near 8-10k units); its USD 48-115 FOB predates the 2026 memory spike; the "cellular decision" is answered in section 3.
- **15:** its 25k gate and PTCRB/carrier-certification costs are US items; India needs BIS, WPC, IMEI/TAC, EPR. QCM6490/7-series advice stands, but Snapdragon 4 Gen 2 has the kids-phone precedents; the USD 650-900 bundle is moot.
- **17, 18:** own hardware swaps Google firmware redistribution for BSP licence and escrow; "yellow boot screen" and "no USB recovery after lock" go away with fused keys and a signed service-unlock.
- **10:** HSM custody is needed before first fusing, not at GA; RKP-only attestation needs an answer.
- **19:** "BIS/WPC/MTCTE/ITSAR deferred, 4-9 months": MTCTE does not list smartphones, 3-5 months if parallel; the "is a reflasher a manufacturer" question is moot (we are).
- **16, 03:** About must show IMEI and SAR (India), an exception to "nothing unnecessary". **12:** void under D19; 112 (A9) moves to the carrier matrix.

## 7. Risks & unknowns
1. **BSP lag and patch ownership:** entry SoCs get no Google long-support; a 3-year promise needs contract SLAs we cannot yet verify.
2. **Memory cost and allocation:** the first PO may price 25%+ above today's quotes or not be filled.
3. **Key custody:** a fused key cannot be rotated; loss or leak is a fleet recall.
4. **Certification delays and brand-specific filings;** BIS licence sits in the factory's name.
5. **Recall and warranty:** child abuse, battery safety; needs an Indian service network.
6. **ODM trust and policy:** pre-installed backdoors; Chinese-ODM JVs need Government approval (Dixtel did) [SECONDARY].
7. **Unknowns:** cellular ETA route; whether a voice-less device is a "handset" under the panic-button Rules; ITSAR notification; BCD rate; Jio/Airtel/Vi data-only attach; Google RKP for non-GMS.

## 8. Decisions needed from the founder (by impact)
1. **Gated, not scheduled:** adopt gates H1-H4; no ODM PO before H3. Default: yes.
2. **Authorise paper RFQs now** (no NRE, under NDA). Default: yes.
3. **First device:** rebadged 4G LTE data phone, voice-capable modem, voice off except 112. Default: yes; Wi-Fi-only is Stage 2.
4. **Silicon:** Snapdragon 4 Gen 2/6-series (QCM6490 if budget); never Unisoc; MediaTek only with verified BROM fuse-off. Default: yes.
5. **Support promise:** 3 years of security patches on own hardware. Default: yes.
6. **Key custody:** HSM with two founders, never at the ODM. Default: yes.
7. **Product name** settled by M6. Default: yes.
8. **Cheap-tier retail phone** qualification in C1-C2 to test price. Default: yes if bring-up under USD 60k.
9. **Funding envelope:** USD 0.5M for EVT at H2, USD 1.5M or more at H3. Default: yes.

## 9. Load-bearing claims

| # | Claim | Source | Basis |
|---|---|---|---|
| 1 | Android 17 accepts vendor FCM 7-202604 (Android 13-17), so older BSPs can host our system | GrapheneOS/platform_hardware_interfaces@17:compatibility_matrices/Android.bp | PRIMARY (mirror) |
| 2 | Long-support programs start at flagships; Google supports kernel forks about 4 years | androidauthority.com Longevity GRF; mediatek.com blog | SECONDARY |
| 3 | 2026 memory shock: LPDDR4X +75% in Q2, 43-45% of low-end BoM, sub-INR 10k prices +32%, CMF Phone 3 Pro cancelled | digit.in; wccftech.com; mobigyaan.com | SECONDARY |
| 4 | PLI ended 31 Mar 2026; MPMS tracks need INR 10,000 or 1,000 crore turnover | pmindia.gov.in; businessworld.in | SECONDARY |
| 5 | Smartphones absent from MTCTE phases I-VI; BIS IS 13252, WPC ETA, ICDR IMEI registration, GSMA TAC, 1.6 W/kg SAR apply | tuvsud.com; elitasrcs.com; pib.gov.in; tarangsanchar.gov.in | SECONDARY |
| 6 | Unisoc BootROM bug CVE-2022-38694 defeats secure boot; Qualcomm secure boot is a fused hash plus signed EDL programmer | github.com/TomKing062; docs.qualcomm.com | SECONDARY |
| 7 | Kids-phone precedent: HMD Fusion X1 on Snapdragon 4 Gen 2 at EUR 269.99; Light Phone III via Foxconn | hmd.com; Wikipedia | SECONDARY |
| 8 | Vendor ODM launch USD 215k, breakeven about 22k units; our model gives 8.5k (rebadge) to 39k (ODM) | Alibaba guide via report 02; section 4.1 | SECONDARY + INFERRED |
| 9 | Pixel 10a at INR 47,999 (about 39,999 on sale) limits the funnel to the premium tier | report 20 sources | SECONDARY |
