# 11. Compliance, legal and regulatory map for a kids' OS

Date: 2026-10-02. Research, not legal advice. Tags: **[P]** read in a primary text or real file this session; **[S]** secondary (news, law-firm or compiled-research pages); **[I]** my judgement; **[M]** training memory, unchecked.

**Evidence limit.** Web search was exhausted and federalregister.gov, ftc.gov, ecfr.gov, eur-lex, leginfo, ico.org.uk, cpsc.gov and fcc.gov were blocked. I read what GitHub served: the California Legislature's bulk law data (a mirror), CRA Annex III, the Android 17 manifest, and compiled legal-research files (cited as repo paths, several dated Sep 2026). Apart from AB 1043 and CRA Annex III, every legal date below is [S] or [M]; counsel must re-read primary texts.

## 1. Summary & recommendation

Zune is a **child-directed online service with an OS, camera, voice, SMS capture and an LLM**, so it sits in the strictest tier of every regime. Recommendation:

1. **US-only launch, company-provisioned (D16), target age 6-12 ("under 13") first.** Retain US kids-privacy counsel before the private beta; join an FTC-approved COPPA safe-harbor program before general availability.
2. **Comply with California AB 1043 on the first image** rather than chase the AB 1856 open-source carve-out. We must know the child's age at setup anyway; the age-bracket API is cheap.
3. **Build the AI assistant to the strictest chatbot rule** (California SB 1119, July 2027): crisis routing, parent-only defaults, no companion persona, audit-ready logs.
4. **Defer EU/UK/other markets.** An OS is a CRA Class I "important product"; the RED/EAA/DSA/AI-Act stack adds roughly 9-18 months [I].
5. **Never sell or stock hardware** while D15/D16 hold; that keeps CPSIA, FCC/CE and CRA-manufacturer duties off us [I].

| Date | Event | Market |
|---|---|---|
| 2026-04-22 | Amended COPPA Rule compliance (live now) | US |
| 2026-09-11 | CRA Art. 14 vulnerability reporting live | EU |
| 2027-01-01 | AB 1043 (as amended by AB 1856) operative; Vermont design code; WA chatbot law | US |
| 2027-05-06 / 05-13 | Utah app-store duties; India DPDP children's rules | UT / IN |
| 2027-07-01 | AB 1043 deadline for earlier-set-up devices; CA SB 1119 binds (July) | US |
| 2027-12-11 | CRA full application | EU |

## 2. Findings

**F1. Amended COPPA Rule [S].** Published 2025-04-22 (90 FR 16918), effective 2025-06-23, compliance 2026-04-22. New: separate parental consent for non-integral third-party disclosure (incl. AI training); written retention policy in the online notice; written security program; voiceprints and faceprints are personal information (audio and photos of a child already were); text-plus consent. Email-plus consent is unavailable if we disclose to third parties. Penalty about $53,088 per violation. Arangarx/tutoring-notes@HEAD:docs/archive/handoff/coppa-compliance-research-2026-05-31.md; diprotis/mango@HEAD:working/0031-age-assurance-coppa.md. Safe harbors: kidSAFE, PRIVO, ESRB Privacy Certified, CARU, Aristotle/iKeepSafe, TrustArc (mukul975/Privacy-Data-Protection-Skills@HEAD:skills/privacy/coppa-compliance/SKILL.md).

**F2. California AB 1043 text [P].** Civ. Code 1798.500-.505 (Stats. 2025 ch. 675), operative 2027-01-01. "Operating system provider" = one who "develops, licenses, or controls the operating system software on a computer, mobile device, or any other general purpose computing device." Duties: an accessible interface **at account setup requiring the account holder (parent) to give the user's birth date or age**; a real-time API returning four brackets (<13, 13-15, 16-17, 18+); minimum data, no third-party sharing; own apps held to the same rules as third-party apps. Devices set up before 2027 need the interface by 2027-07-01. Penalty $2,500 (negligent) or $7,500 (intentional) per affected child, Attorney General only; good-faith safe harbor for erroneous signals. s.1798.504(f) excludes "the delivery or use of a physical product" (meaning unclear). aaronjuar-ez/PUBINFO-2025@7158ec8:LAW_SECTION_TBL_4980, _4981, _4982, _33102, _33103, _4983 (.lob; map in LAW_SECTION_TBL.dat).

**F3. AB 1856 [S].** Signed 2026-09-10 in a 13-bill child-safety package. It removes from "operating system provider" anyone distributing software "under license terms permitting a recipient to copy, redistribute, and modify"; Android stays in scope. Enrolled text unread (a digest read the 2026-08-21 Senate version). amehta0104/ditto-research-public@HEAD:research/2026-09-11-cycle-delta.md; xkef/swe-digest@HEAD:data/digests/2026-08-30.md.

**F4. Other OS and app-store age laws [S].** Texas SB 2420 is enforceable (injunction 2025-12-23; Fifth Circuit stay 2026-05-28/06-04; Supreme Court refused to vacate 2026-07-06). Utah duties 2027-05-06 (pre-installed apps in scope), Louisiana 2027-07-01, Alabama 2027-01-01, Colorado SB26-051 OS age attestation 2028-07-01. Brazil's Digital ECA (enforceable 2026-03-17, Decree 12.880) puts age-signal duties on **operating systems**. Play Age Signals already serves Texas and Brazil [P: developer.android.com/google/play/age-signals/overview]. mjmirza/app-store-compliance@HEAD:docs/GLOBAL-REGULATORY-2026.md; Davron2004/Whim@HEAD:docs/research/legal-surface-2026-09/README.md. We run no app store, so the store acts should not bind us [I].

**F5. AI-minor laws [S].** California SB 1119 "Adam's Law" (July 2027): "companion chatbot" is broad enough to cover general assistants; operators must determine age, document a risk assessment before releasing or materially changing a bot, route minors in crisis, alert parents to imminent self-harm, default to parent-only controls (time limits, muted notifications, memory), and avoid romantic role-play or dependence; private right of action, incident reporting, independent audits. SB 867 bans selling AI-companion **toys** for under-16s through 2030. SB 243 (in force 2026-01-01), WA HB 2225 and OR SB 1546 (2027-01-01) add disclosure and crisis duties. prajwalgajakesari/the-vault-ai@HEAD:editions/2026/09/10/stories/17-california-adam-raine-act-sb1119.md; docs/research/07-ai-assistant.md F8. EU AI Act Art. 50 disclosure applies from 2026-08-02; high-risk deferred to 2027-12-02 [S: mj EU-REGULATORY-2026.md].

**F6. Federal and design-code status [S].** At 2026-09-05 none of COPPA 2.0 (passed Senate 2026-03-05), the KIDS Act (passed House 2026-06-29), KOSA (reported 2026-08-05) or the federal App Store Accountability Act is law. The Ninth Circuit (2026-03-12) revived California design-code age-estimation and geolocation parts; data-use and DPIA parts stay enjoined. FTC's 2026-02-25 policy statement spares age-only collection that is single-purpose and promptly deleted. GLOBAL-REGULATORY-2026.md; the-machine-herald/machineherald.io@HEAD:src/content/articles/2026-03/23-congress-converges-....md.

**F7. FTC pattern [S].** Disney $10M for mislabelled YouTube videos (order 2025-12-23, report 06); Apitor (Sept 2025), a toy maker sued over a third-party SDK collecting kids' location ($500k, suspended); Genshin Impact $20M (Jan 2025); AI-chatbot 6(b) orders (2025-09-11); TAKE IT DOWN enforcement from 2026-05-19, with warning letters even to photo-storage and cloud firms. tconqueror/security-feed@HEAD:Bleeping/Markdown/2025/202509/20250904_...robot-toy-maker....md; the-machine-herald/machineherald.io@HEAD:src/content/articles/2026-05/22-ftc-begins-enforcing-the-take-it-down-act-....md.

**F8. CSAM [S].** 18 U.S.C. 2258A: report to NCMEC on actual knowledge; the REPORT Act (2024-05-07) adds trafficking and enticement, one-year preservation, fines up to $850k/$1M. Messenger and calls make us an electronic communication service. ItzDevoo/UnCorded@HEAD:docs/csam-compliance-research.md. California AB 1946 (CSAM reporting) was in the 2026-09-10 package [S].

**F9. EU CRA and RED [P/S].** CRA Annex III Class I lists "Operating systems", "Smart home general purpose virtual assistants" and wearables "intended for the use by and for children" [P: strictdoc-project/strictdoc-templates@HEAD:templates/EU_2024-2847/EN/EU_2024-2847-ANNEX-III.sdoc]. Art. 14 reporting (24 h for exploited vulnerabilities) live 2026-09-11; full duties 2027-12-11 [S: espressif/developer-portal@HEAD:content/blog/2026/09/esp32-cra-obligations-and-deadlines/index.md]. Class I needs a harmonised standard or a notified body [M]. RED Delegated Act applies from 2025-08-01; EN 18031 was cited in the OJ 2025-01-28 with restrictions, and EN 18031-2's toy/childcare access-control options may clash with parental controls, forcing a notified body [S: espressif/developer-portal@HEAD:content/blog/2025/04/esp32-red-da-en18031-compliance-guide/index.md].

**F10. EU/UK/other child rules [S/M].** GDPR Art. 8 consent age is 13-16 by member state; DSA minors guidelines 2025-07-14; the EAA has applied since 2025-06-28 to smartphones, e-readers and e-book software (microenterprise relief covers services, not products) [mj EU-REGULATORY-2026.md]. UK: Children's Code (DPIA, high-privacy defaults, signal when parents monitor); Online Safety Act child duties from 2025-07-25. Australia: Equipment Code child-account defaults since 2026-03-09 [S, Wayback]. India: under-18s need parental consent from 2027-05-13.

**F11. CPSIA [S/M].** A "children's product" is "designed or intended primarily for children 12 years of age or younger" (16 CFR 1200.2); it needs lab testing, a CPC, tracking labels (15 USC 2063(a)(5)), a 100 ppm lead limit, and certificate eFiling at import since 2026-07-08. JingzhiZhang520/enhanced-gencompliance@HEAD:reference_data/HIGH_QUALITY_CPSC_RULES.md; thirstypig/alephco.io-www@HEAD:blog/posts/the-children-s-product-compliance-checklist.md. Triggered only if we make or import a handset or accessory [I].

**F12. Open source and IP.** Android 17 ships software codec projects `libavc`, `libhevc`, `libmpeg2` and `aac` (FDK AAC), plus `libvpx`, `libaom`, `libopus`, `e2fsprogs`, `iproute2`, `iptables` [P: GrapheneOS/platform_manifest@17:default.xml]. FDK AAC grants no patent licence, and AVC/HEVC/AAC pools bill device makers [M]. The kernel is GPL-2.0 with a source-offer duty (report 17). Pixel images are personal-use, non-redistributable except per an unread enclosed licence (reports 02, 17). Avoid in the image: Piper (GPL-3), KOReader/MuPDF and libsignal (AGPL) (reports 07, 09, 13). "Android" is Google's mark; "Zune" was Microsoft's product [M].

## 3. Options & trade-offs

| Option | For | Against | Verdict |
|---|---|---|---|
| A. Comply with AB 1043 and COPPA now, US-wide | Cheap; satisfies CO 2028, Brazil, AU later | Engineering in image 1 | **Adopt** |
| B. License the OS permissively to use AB 1856's carve-out | Might lift the OS duty | Proprietary blobs, apps and EULA make qualification doubtful; poor optics; no COPPA relief | Reject |
| C. Exclude California | Avoids AB 1043/1119 | Largest market; others copy | Reject |
| D. US + UK + EU together | Wider market | CRA Class I, EN 18031, EAA, DSA, AI Act, GDPR-K | Defer |
| E. Sell phones | Margin, control | CPSIA, FCC/CE, CRA manufacturer, inventory | Reject (D15/D16) |

## 4. Recommended design for Zune

### 4.1 Risk-ranked compliance matrix
Costs and lead times are [I], order of magnitude only.

| # | Obligation | Applies when | Severity | Design implication | Owner | Cost / lead |
|---|---|---|---|---|---|---|
| 1 | Amended COPPA | US child under 13 (we are directed to children) | Critical | Parental consent at portal enrolment (card/ID/KBA, since we disclose to vendors); separate consent for AI-training or ad disclosure (ban by contract); retention schedule in notice; security program; review/delete/revoke endpoints; no cloud face grouping or voice-ID | Counsel, Platform | $20-50k; safe harbor $5-25k/yr; 8-12 wk |
| 2 | Interception law (wiretap, stored communications, state all-party consent) | Parent portal reads kid SMS and messages | High | No call audio; child-visible "parents can see this" signal (also design-code); written parental consent; counsel opinion pre-beta | Counsel, Telephony | $5-15k; 3-4 wk |
| 3 | AI-minor laws (CA SB 1119, SB 243, SB 867; WA, OR, NY) | AI assistant, esp. California | High | Tutor not companion; crisis routing (988) and parent alert; parent-only time/notification/memory defaults; risk assessment per model change; incident log; audit budget | AI lead, Counsel | Audit $30-100k by mid-2027 |
| 4 | CA AB 1043/1856 | CA from 2027-01-01 | High (hard date, per-child fines) | Parent-gated birth-date step in setup; `ZuneAgeSignal` API, four brackets; first-party apps call it; no sharing; accessible UI | Platform | 2-3 wk eng |
| 5 | Security and breach law (COPPA program, state statutes, CRA if EU) | Always | High | MFA, encryption, vendor DPAs, incident runbook; SOC 2 Type I then II | Security | $30-80k; 6-12 mo |
| 6 | CSAM and NCII (2258A, REPORT Act, TAKE IT DOWN) | Messenger, calls, camera, AI-image upload | High | Photos stay on device in Stage 1; AI image input passes a safety/CSAM check; NCMEC registration; one-year preservation; 48-h takedown path | T&S | $5-20k; 4-6 wk |
| 7 | OEM/Google firmware licence | OTA with OEM firmware; flashing customer phones | High | No OTA firmware until a written answer (report 17) | Founder | 8+ wk |
| 8 | YouTube terms and made-for-kids | Videos tier 2 | High (business) | Offline licensed tier 1 first; MFK-only; kill switch (report 06); treat YouTube identifiers as a third-party disclosure and name Google in the consent notice [I] | Product | Ongoing |
| 9 | State kids' laws (CA design code, VT, NY, NE, MD) | Under-18 users | Medium | High-privacy defaults; weather by ZIP not GPS; no dark patterns; DPIA on file | Product | 4 wk |
| 10 | GPL/open source | Any image | Medium | Publish kernel/GPL source or written offer; per-build SBOM and NOTICE; no GPL-3/AGPL in image | Release | Low |
| 11 | Codec patents (AVC, HEVC, AAC, MPEG-2) | Shipping software codecs | Medium | Disable unneeded sw codecs; prefer VP9/AV1/Opus; ask licensors | Platform | Unknown until quoted |
| 12 | Trademarks | Any public use | Medium | Clear and replace "Zune" before marketing; say "built on the Android Open Source Project"; no Android logo or "compatible" claim | Founder | $3-10k; 2-3 wk |
| 13 | FCC, carrier, E911 | We touch RF or modem firmware | Medium | Keep modem/Wi-Fi firmware stock; emergency calls always allowed; Wi-Fi calling off in Stage 1 (report 12); walkie-talkie is IP push-to-talk, no radio licence [I] | Platform | Low |
| 14 | CPSIA | We sell or import a handset or accessory | Medium (conditional) | Stay an installation service; if hardware is sold: CPC, lab tests, tracking label | Founder | $5-15k/SKU |
| 15 | Consumer, accessibility, export, insurance | Always | Medium | Parent is sole contracting party; no "100% safe" claims; WCAG 2.1 AA portal; self-classify crypto; cyber, E&O, product cover | Counsel, Ops | $20-60k/yr |
| 16 | EU/UK stack (GDPR-K, Children's Code, OSA, DSA, AI Act, CRA, RED, EAA) | Selling in EU/UK | High, deferred | Do not ship before CRA route and EN 18031 plan are costed | Founder | 9-18 mo [I] |
| 17 | App-store acts, federal bills | If we add third-party apps; watch KOSA/KIDS/COPPA 2.0 | Low | No app store or sideloading | Platform | Watch |

### 4.2 Build-in-from-day-one checklist
- Parent-gated setup step capturing birth month/year; device stores only the bracket; `ZuneAgeSignal` API.
- Parent portal as consent ledger: versioned consents, per-vendor disclosure list, one-click review/export/delete/revoke, retention timers.
- Data map and vendor register with DPAs and zero-retention, no-training clauses (LLM, weather, video, push, SMS).
- Child-visible indicator wherever parents can see content (SMS, messenger, AI logs).
- AI safety kit (crisis protocol, parent alerts, no-persona prompt, risk assessment, red-team log) and trust-and-safety kit (report button, CSAM/NCII runbook, NCMEC account, one-year evidence store).
- Security: signed builds, vulnerability intake with 24-h clock, SBOM per image, SOC 2 plan.
- Defaults: no analytics SDKs or ad IDs, coarse location, no face or voice templates in the cloud.
- Legal artifacts: parent terms, kid-readable privacy notice, retention schedule, GPL source page, trademark file.

### 4.3 Launch-market sequence
1. **Beta:** US, up to 100 provisioned devices, counsel engaged, COPPA consent live.
2. **US GA:** after safe-harbor certification, AB 1043 shipped, SB 1119 readiness, YouTube and OEM answers.
3. **UK**, then **EU** once CRA and RED routes are costed; Canada and Australia later.
4. **Avoid for now:** Brazil and India (OS age-verification mandates).

### 4.4 Ask a lawyer first
1. COPPA: operator status, consent method, whether LLM, weather and YouTube are "third parties".
2. Legality of parents reading kid SMS and messages; counterpart notice.
3. AB 1043 scope for a no-store OS; the "physical product" carve-out; Utah pre-installed apps.
4. SB 1119/SB 243/SB 867 scope; is a phone a "toy"?
5. OEM firmware redistribution, DMCA 1201, warranty.
6. "Zune" clearance; "Android" usage.
7. CPSIA framing of a returned customer phone; codec patents; insurance; consumer arbitration terms.

## 5. Risks & unknowns
- Nearly every date is [S] or [M]; AB 1856's enrolled text and SB 1119's final definitions were not read.
- Courts: Texas merits appeal, NetChoice suits against California's package, federal preemption (the Dec 2025 AI executive order carved out child safety [S]).
- Age range undecided; 13+ users pull in teen regimes.
- OEM blob licence, YouTube answer and notified-body routes are external dependencies.
- Interception law varies by state [M].

## 6. Decisions needed from the founder
1. Target age band (recommend 6-12 first).
2. Launch markets (recommend US-only, no geofence).
3. Approve complying with AB 1043 rather than seeking the AB 1856 carve-out.
4. May photos or AI-image uploads leave the device in Stage 1 (recommend no cloud photo storage)?
5. AI posture: tutor, not companion; fund the SB 1119 audit or limit AI in California until audited.
6. Budget: counsel retainer, safe-harbor program, SOC 2, insurance.
7. Rename the product before any public use.
8. Will the company ever sell hardware?

## 7. Load-bearing claims

| # | Claim | Source (full paths in section 2) | Basis |
|---|---|---|---|
| 1 | AB 1043 binds mobile "operating system providers" from 2027-01-01: setup age collection, four-bracket API, $2.5k/$7.5k per child, AG only | aaronjuar-ez/PUBINFO-2025@7158ec8:LAW_SECTION_TBL_4980/_4981/_33103/_4983 (F2) | PRIMARY |
| 2 | AB 1856 signed 2026-09-10; carve-out only for open-source-licensed OSes | ditto-research-public cycle-delta 2026-09-11 (F3) | SECONDARY |
| 3 | Amended COPPA: compliance 2026-04-22; separate consent for third-party disclosures; retention policy in notice | tutoring-notes COPPA brief (F1) | SECONDARY |
| 4 | SB 1119 binds broad chatbot operators from July 2027 with audits and a private right of action | the-vault-ai SB 1119 story (F5) | SECONDARY |
| 5 | Texas SB 2420 is enforceable; Supreme Court left the stay in place 2026-07-06 | Davron2004/Whim legal-surface README; developer.android.com Play Age Signals (F4) | SECONDARY |
| 6 | CRA Class I lists operating systems; reporting live 2026-09-11, full 2027-12-11 | strictdoc-templates ANNEX-III.sdoc; Espressif CRA blog (F9) | PRIMARY / SECONDARY |
| 7 | Android 17 ships AVC, HEVC, MPEG-2 and AAC software codec projects | GrapheneOS/platform_manifest@17:default.xml (F12) | PRIMARY |
| 8 | No federal kids' online-safety bill is law at 2026-09-05 | mjmirza GLOBAL-REGULATORY-2026.md (F6) | SECONDARY |
| 9 | FTC punishes third-party data flows in kids' products (Disney $10M, Apitor) | security-feed Apitor article; report 06 (F7) | SECONDARY |
| 10 | Brazil's Digital ECA puts age-signal duties on operating systems | GLOBAL-REGULATORY-2026.md section 3.3 (F4) | SECONDARY |
