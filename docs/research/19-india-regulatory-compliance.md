# 19. India: law and regulation for a kids OS with parent monitoring, internet messaging/voice/video, AI and flash-and-deliver

Date: 2026-10-02. Research, not legal advice. Tags: **[PRIMARY]** read in primary text this session; **[SECONDARY]** news or law-firm summary; **[INFERRED]** my judgement; **[MEMORY]** training knowledge, unchecked.

**Evidence limit.** AOSP and every Indian government host (meity, indiacode, dot, trai, cert-in, egazette, bis, pib, rbi) returned 403, as did most news and law-firm pages. I read the Gazette text of the DPDP Act, DPDP Rules 2025 and Telecommunications Act 2023 through GitHub mirrors (three copies of the Rules agree on the clauses cited), plus Anthropic's pages. Everything else is **[SECONDARY]** from search summaries I could not open; counsel must re-read the originals.

## 1. Summary & recommendation

India is workable for a 200-family, parent-contracted, internet-only pilot, but the binding risks differ from reports 11-13.

1. **Telecom licensing is not the main risk.** D19 removes PSTN, SMS and carrier-of-record issues. The live issues are DPDP s.9 (children), IT Act intermediary duties, POCSO reporting and a policy push against minors on messengers.
2. **A parental-control vendor has no class exemption.** DPDP s.9(3) bans "tracking or behavioural monitoring of children". The Fourth Schedule exempts clinics, schools, crèches and school transport (Part A), and purposes such as child-safety location and keeping harmful content from the child (Part B) [PRIMARY]. Parents reading messages, call metadata and AI chats is **not squarely exempt**. The defensible reading: the parent is part of the "Data Principal" for a child (s.2(j)(i)) and consents, so Zune is a conduit, not a monitor. Unsettled (gate G1).
3. **Dates.** s.9 and Rule 10 bind from **13 May 2027**; MeitY floated 13 Nov 2026 (not gazetted as far as I could see) [SECONDARY]. Behave as if the law is in force now.
4. **Direction-of-travel risk.** On 28 Sep 2026 the Centre told the Supreme Court it will amend the IT Rules so platforms cannot let under-18s open social-media accounts [SECONDARY]. A messenger is plausibly a "social media intermediary". Position Zune as a **family-managed, closed-contact tool** (no discovery, handles, feeds or groups).
5. **Recommendation.** Invite-only, parent-contracted pilot through an Indian entity with India-region hosting, Rule-10 parent verification at the provisioning visit, purpose-limited monitoring, a 112 path plus triple-press SOS, and counsel sign-off (section 4.4) before any external family is invited or charged.

## 2. Findings

### 2.1 DPDP Act 2023 and Rules 2025 ([PRIMARY] unless marked)
Sources: Rules at raw.githubusercontent.com/Abhinav-bv/Compiler-for-Law/HEAD/data/dpdp_rules_2025_text.txt (cross-checked with saurabh4269/dpdp-kavach@HEAD:data/DPDP_Rules_2025_English_only.md); Act at priyanshu-ogdev/Ssense@HEAD:ml/data-forge/dpdp_act_and_rules_2025.txt (carries the G.S.R. 843(E) commencement footnote). One mirror with non-official section numbers was discarded.

- **Commencement.** Rules 1, 2, 17-21: 13 Nov 2025. Rule 4 (consent managers): one year on. Rules 3, 5-16, 22, 23 and Act ss.3-17, 44(2): eighteen months on (13 May 2027). Until then **IT Act s.43A and the SPDI Rules stay in force** [MEMORY on content].
- **Roles.** Zune is the Data Fiduciary. AI, cloud, push, media and SMS vendors are Data Processors under contract (s.8(2)); we stay liable (s.8(1)). A parent's own reading is outside the Act as "personal or domestic purpose" (s.3(c)(i)); our processing is not.
- **Children.** Child = under 18 (s.2(f)), so age bands do not reduce the burden. s.9(1): verifiable parental consent before any processing. Rule 10: the parent must be an identifiable adult via details we hold, or details or a **virtual token from an authorised entity, including DigiLocker**. s.9(2) bars processing likely to harm well-being.
- **Exemptions (Rule 12, Fourth Schedule).** Part B: (4) real-time location "in the interest of safety, protection or security"; (5) processing "to the extent necessary" to keep harmful information, services or ads from the child; (6) age and parent verification. **No row for parental control or messaging.** The s.17(3) startup carve-out never covers s.9.
- **Cross-border and scale.** Transfer allowed unless a country is notified (s.16); Rule 13(4) localises only data specified for Significant Data Fiduciaries. **No blanket localisation.** Significant status turns on volume, sensitivity and risk (s.10), not a user count; a children's platform is a plausible future candidate [INFERRED].
- **Breach and retention.** Detailed report to the Board within **72 hours**, plus notice to each affected principal (Rule 7). Rule 6: encryption, access control, logs, one-year log retention. **Rule 8(3): keep personal data, traffic data and processing logs at least one year** (State-access purposes).
- **Process and penalties.** 90-day grievance route (Rule 14); published contact person (Rule 9); withdrawal as easy as consent (s.6(4)); notices must offer "English or any language specified in the Eighth Schedule" (ss.5(3), 6(3)). Penalties: Rs 200 crore for s.9, Rs 250 crore for security, Rs 200 crore for breach notification.
- **Status.** Board exists in law; chair reported appointed June 2026 [SECONDARY, conflicting]. Timeline compression: https://chambers.com/articles/meity-plans-to-cut-short-dpdp-compliance-timeline-and-notify-cross-border-restrictions-for-sdfs [SECONDARY].

### 2.2 Telecom and messaging
- **Broad text, untested.** "Telecommunication" is transmission of messages by wire, radio, optical or other electromagnetic systems; a service for it needs authorisation; operating without one is an offence (up to three years or Rs 2 crore) (ss.2(p), (t), 3(1)(a), 42(1)) [PRIMARY: abhinandansethi/TMT-Tracker@HEAD:data/act_text/telecom_2023.json]. TRAI (Sept 2024) excluded OTT from authorisation, and DoT created a separate "Telecommunication Identifier User Entity" (TIUE) category [SECONDARY] https://bestmediainfo.com/mediainfo/ott/trai-suggests-service-authorisations-framework-excludes-ott-platforms-from-licensing-regime-7077869 . Likely not an authorisable service, risk not zero [INFERRED].
- **TIUE and SIM binding.** Amendment Rules (22 Oct 2025) make any non-licensee that uses telecom identifiers (mobile numbers) to identify users a TIUE [SECONDARY] https://www.scconline.com/blog/post/2025/10/25/telecommunications-telecom-cyber-security-amendment-rules-2025-legal-news/ . The 28 Nov 2025 DoT direction keeps number-based messengers bound to the device SIM; deadline extended to **31 Dec 2026** [SECONDARY] https://www.tribuneindia.com/news/business/dot-extends-sim-binding-deadline-for-messaging-apps-to-december-31 . In July 2026 the Government sent notices to WhatsApp, Telegram and Signal over **phone-number-free usernames** [SECONDARY] https://www.businesstoday.in/technology/news/story/whatsapp-submits-reply-to-govt-notice-on-username-feature-542137-2026-07-10 . A number-free kid messenger is policy-adverse unless each child traces to a verified adult; a mobile-OTP parent portal probably makes us a TIUE [INFERRED].
- **Interception.** Telecom Act s.20(2) lets the Government order interception or suspension; **s.42(2)(b) makes unlawful interception an offence**; offences are cognizable and non-bailable (s.42(7)) [PRIMARY]. IT Act s.69 and the 2009 Interception Rules bind intermediaries [MEMORY]. Zune is the server endpoint, not a third-party interceptor, but disclosure to the other child's parent needs counsel.
- **Mandates.** The Sanchar Saathi pre-install order was withdrawn 3 Dec 2025 [SECONDARY] https://techobserver.in/news/egov/govt-withdraws-order-mandating-pre-installed-sanchar-saathi-on-all-phones-319314/ . Smartphone ITSAR (83 requirements): a Jan 2026 source-code proposal was denied by MeitY and I found no notification [SECONDARY] https://www.theregister.com/2026/01/12/india_mobile_security/ . It would bind handset makers; whether a reflasher counts is open [INFERRED].
- **Handset duties.** Panic Button and GPS Rules 2016: smartphones must trigger a panic call on three quick power-key presses and have GPS, binding makers and importers [SECONDARY] https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=142272&reg=48&lang=2 ; old rules survive under Telecom Act s.61 [PRIMARY]. **Replacing the OS removes the vendor's compliant SOS unless we rebuild it.** 112 (ERSS) has run nationally since 2019; 1098 Childline is being merged into it [SECONDARY] https://www.mha.gov.in/en/commoncontent/emergency-response-support-system-erss . I found **no rule requiring cellular voice on a handset sold in India** [INFERRED]. Tampering with telecom identifiers (IMEI) is an offence (s.42(3)(c); [MEMORY] up to three years).
- **Parent OTP/alert SMS** needs DLT registration of entity, header and template [MEMORY].

### 2.3 Equipment and product law
- **BIS CRS** (IS 13252 Part 1) binds makers and importers via an Indian representative [SECONDARY] https://www.ascgroup.in/bis-certification-for-mobile-phones-smartphone-is-13252/ ; **WPC ETA** for Wi-Fi/Bluetooth is self-declared [SECONDARY] https://eservices.dot.gov.in/equipment-type-approval-eta ; **TEC MTCTE** coverage of smartphones is unverified. Re-flashing an India-sold Pixel changes software, not registered hardware, so I do not read it as manufacture [INFERRED], but Telecom Act s.2(q) counts "software integral to" equipment. Own hardware (D21) triggers all three plus IMEI/CEIR and customs.
- **Warranty.** Google's India warranty excludes damage from unlocking the bootloader or altering firmware or OS [SECONDARY] https://support.google.com/product-documentation/answer/7540759?hl=en-IN . Disclose; offer return-to-stock.
- **Consumer law.** Consumer Protection Act 2019 Chapter VI makes manufacturers, service providers and sellers liable for defects [SECONDARY] https://vidhijudicial.com/sec-82-to-87-chapter-vi-(product-liability)-the-consumer-protection-act,-2019.html . For the flash we are a "product service provider", plausibly a manufacturer by branding [INFERRED]; consumer commissions can disregard unfair terms [MEMORY]. Minors cannot contract (Contract Act s.11) [MEMORY]: **only the parent contracts.**

### 2.4 IT Act, intermediaries, POCSO
- **Intermediary.** A "social media intermediary" "primarily or solely enables online interaction between two or more users"; the significant tier (50 lakh users) brings traceability [SECONDARY] https://www.tribuneindia.com/news/nation/govt-sets-50-lakh-users-threshold-to-define-significant-social-media-intermediary-under-it-rules-218237 . We are far below it, but grievance officer, takedown and published rules apply to all intermediaries.
- **2026 amendments** (in force 20 Feb): takedown on orders 36 h to **3 h**; intimate-image and CSAM complaints **2 h**; grievances 15 to 7 days; labelling of synthetic audio-visual content [SECONDARY] https://www.khaitanco.com/thought-leadership/MeitY-notifies-the-IT-Amendment-Rules-2026 . A text-only assistant is outside the synthetic-media rules; image generation would not be.
- **Under-18 accounts.** Hearing of 28 Sep 2026: amend IT Rules to bar under-18 accounts; earlier reports describe tiers 8-12, 12-16, 16-18, with educational services open on parental consent [SECONDARY] https://inc42.com/buzz/will-amend-it-rules-to-bar-under-18s-from-social-media-centre-to-sc/ . Whether a closed, parent-managed messenger is covered is unknown.
- **CERT-In 2022:** report incidents within **6 hours**; keep logs **180 days in India**; Indian NTP [SECONDARY] https://www.internetsociety.org/resources/doc/2022/internet-impact-brief-india-cert-in-cybersecurity-directions-2022/ .
- **POCSO.** ss.19-21 and POCSO Rules r.11 make reporting mandatory; *Just Rights for Children Alliance v S. Harish* (23 Sep 2024) held intermediaries lose s.79 safe harbour without it [SECONDARY] https://www.scobserver.in/journal/supreme-court-review-2024-a-progressive-year-for-the-rights-of-children/ . A child sending sexual images is victim and possible offender [INFERRED].
- No Digital India Act and no chatbot-for-minors rule; MeitY's AI Governance Guidelines (Nov 2025) are non-binding [SECONDARY]. DPDP s.9 is the operative rule.

### 2.5 Payments
- **RBI e-Mandate Framework 2026:** extra authentication at registration; recurring debits up to **Rs 15,000** need none after; **24-hour pre-debit notice**; covers cards, wallets, UPI AutoPay [SECONDARY] https://www.scconline.com/blog/post/2026/04/24/rbi-issues-digital-payments-e-mandate-framework-2026/ . **Payment aggregators** need RBI authorisation (Rs 15 crore net worth) [SECONDARY]: use an authorised one; store no card data.
- **GST.** Foreign online-service suppliers must register from the first sale and charge 18% IGST [SECONDARY] https://treelife.in/legal/oidar-registration-in-india/ ; Indian entities charge 18% [MEMORY]. $59/$12.99 is about Rs 5,000 and Rs 1,100 a month before GST at an unchecked Rs 85-90/USD [INFERRED]; report 20 owns price points. Dark-pattern and e-commerce rules govern cancellation and refunds [MEMORY].

### 2.6 Foreign AI and cloud vendors
- **Anthropic:** Bengaluru office opened 16 Feb 2026 [PRIMARY https://www.anthropic.com/news/bengaluru-office-partnerships-across-india ]; in-country inference via Bedrock Mumbai/Hyderabad announced [SECONDARY] https://www.businessworld.in/article/anthropic-brings-in-country-claude-inference-to-india-through-amazon-bedrock-617795 ; minors policy needs age verification, moderation, monitoring, AI disclosure, child-privacy compliance, with audits [PRIMARY https://support.claude.com/en/articles/9307344-responsible-use-of-anthropic-s-models-guidelines-for-organizations-serving-minors ].
- **OpenAI:** India residency covers storage only, not processing [SECONDARY] https://creuto.com/openai-data-residency-india-uae . **Gemini:** API terms bar apps "likely to be accessed by" under-18s (report 07) [SECONDARY]. **Sarvam:** India-hosted models and speech APIs [SECONDARY]. **Krutrim:** not researched.
- **Hosting:** AWS Mumbai/Hyderabad, GCP Mumbai [SECONDARY]. Blocking risk: DPDP s.37, Telecom Act s.20(2) [PRIMARY], IT Act s.69A [MEMORY]; keep report 07's provider abstraction.

## 3. Options & trade-offs

| Decision | Options | Verdict |
|---|---|---|
| Timing | act as if DPDP binds now / wait for May 2027 | **Now**: date may move; Rule 10 data cannot be backfilled |
| Monitoring depth | full content by default / tiered / alerts only | **Tiered**: content visible under 13, flagged excerpts plus metadata at 13+, child-visible notice; alerts-only fails D7 |
| Messenger identity | number-free invite-only parent-linked / child SIM-bound / public handles | **Invite-only parent-linked**; SIM-bound contradicts D19; handles are what DoT attacks |
| v1 verification | DigiLocker token / staff ID check / card payment | **Token plus staff check**; card is not Rule 10 |

## 4. Recommended Stage-1 design

### 4.1 Architecture
- **Entity and hosting:** Indian private limited; AWS Mumbai primary, Hyderabad DR; Indian NTP; 180-day logs in India.
- **Parent identity:** one verified adult per family (DigiLocker token, or staff-inspected government ID at the D16 visit), mobile OTP, consent ledger. Child accounts exist only under a verified parent; the device never shows the child an "I agree".
- **Monitoring:** parent-directed and purpose-bound (safety, content gating); no analytics SDKs, ad IDs or behavioural profiles; video topic search uses the current question only. Location only on SOS (Part B(4)); weather uses a parent-set city.
- **Both-family consent** per contact pair, naming what each parent sees (report 13).
- **Retention:** message content, AI transcripts and logs **12 months** in a restricted vault, then deleted, until counsel narrows Rule 8(3). Vendors keep nothing.
- **AI:** India-region inference; processor contracts; AI disclosure; no companion persona; crisis routing to 112, Tele-MANAS 14416 [MEMORY], Childline; image uploads screened for CSAM/NCII; no cloud face recognition.
- **Handset:** 112-only emergency path, triple-press SOS, IMEI and modem untouched (hash-checked at the station). Field-test 112 on Jio, Airtel, Vi and BSNL data-only SIMs; tell parents emergency calling is not guaranteed.
- **Intermediary basics:** resident grievance officer, published terms, 24x7 on-call for 3 h and 2 h takedowns, POCSO runbook, CERT-In 6 h and DPDP 72 h breach runbooks.
- **Money:** Indian aggregator or merchant of record, e-mandate with pre-debit notice, GST invoices, DLT-registered OTP sender.

### 4.2 Risk-ranked matrix

| # | Obligation | Applies | Severity | Design implication | Owner | Lead time |
|---|---|---|---|---|---|---|
| 1 | DPDP s.9(3) | May 2027 (maybe Nov 2026) | Critical, Rs 200 cr | Strict-reading design, opinion | Counsel, Product | 4-6 wk |
| 2 | Rule 10 verification | Same | Critical | Token plus ID, ledger | Platform | 4-8 wk |
| 3 | Under-18 account rule (proposed) | Unknown | High | Closed-contact positioning, MeitY outreach | Founder | Ongoing |
| 4 | POCSO ss.19-21; takedown 3 h/2 h | Now | High | Runbook, evidence vault, 24x7 on-call | T&S | 3-4 wk |
| 5 | Security, breach, CERT-In | Now / May 2027 | High, Rs 250 cr | Encryption, logs, runbooks | Security | 6-10 wk |
| 6 | Telecom Act ss.3, 42; TIUE; interception | Now, unclear | High | Counsel view; verified-parent traceability; consent text | Counsel | 3-4 wk |
| 7 | Rule 8(3) retention | May 2027 | Medium | 12-month vault | Platform | 2 wk |
| 8 | Panic button, 112, IMEI | Now | Medium | SOS, 112 path, IMEI untouched | Platform | 3-4 wk |
| 9 | Consumer law, warranty, bailment | Now | Medium | Parent contract, return-to-stock, insurance | Counsel, Ops | 3 wk |
| 10 | RBI, GST, DLT | First charge | Medium | Aggregator, GST-inclusive price | Finance | 4-6 wk |
| 11 | BIS, WPC, MTCTE, CEIR | Own hardware (D21) | Deferred | Plan with ODM (report 21) | Hardware | 4-9 mo [INFERRED] |

### 4.3 What changes versus the US plan and the cellular plan

| Item | US/cellular plan | India under D18-D21 |
|---|---|---|
| Child privacy, parent verification | COPPA, under 13, about $53k per violation; card or ID | DPDP s.9, under 18, up to Rs 200 crore; Rule 10 ID or DigiLocker token (card does not count) |
| Handset law | FCC, CPSIA | BIS/WPC/TEC only for own hardware; v1 keeps RF, IMEI, modem untouched and rebuilds SOS |
| OS age signal, CSAM | California AB 1043; NCMEC | No OS age law (IT Rules age proposal instead); POCSO reporting to police or cyber-crime portal |
| Report 12 issues that **disappear** | Carrier of record, CPNI, CALEA, STIR/SHAKEN, SMS vault, per-carrier VoLTE, WEA, E911 address | Gone under D19 |
| Report 12 issues that **remain** | Parent reading child messages; emergency calling; identifier tampering; parent SMS | Telecom Act s.42(2)(b), IT Act s.69, DPDP s.9(3), other family's child; 112 path (A9); s.42(3)(c); DLT |

### 4.4 Minimum compliance gate before the first 200-user phase
**G1** written counsel opinion on s.9(3), messenger classification and parent access vs interception law; **G2** Indian entity, India hosting, published grievance and DPDP contacts; **G3** Rule-10 consent, withdrawal and erasure flows live; **G4** parent-only contract, notices, custody terms, warranty disclosure, insurance; **G5** security baseline, CERT-In and breach runbooks, 180-day logs; **G6** POCSO and takedown on-call, tabletop drilled; **G7** vendor contracts, India-region inference, Anthropic's written confirmation for child use (report 07); **G8** 112 field test and SOS shipped; **G9** payments and DLT ready (or free pilot); **G10** invite-only list, no public marketing, kill switch.

**Build in from day one:** consent ledger, both-family consent, child-visible "parents can see this", no SDKs, per-child visibility mode, deletion jobs, India-only data map and vendor register, crisis protocol, breach clocks, SOS/112, IMEI hash checks.

## 5. Stage-2 improvements
Significant-Data-Fiduciary readiness (India DPO, DPIA, audit); automated DigiLocker and consent-manager option; parent-key E2EE only if counsel clears IT Act s.69; CSAM hash-matching; MeitY/DPB exemption dialogue (s.9(4), s.17(5)); on-shore models (Sarvam or self-hosted); Indic notices; BIS, WPC, MTCTE, CEIR, ITSAR for own hardware (report 21).

## 6. Conflicts with earlier reports
- **11:** "avoid India (OS age-verification mandates)" is wrong: India has DPDP s.9 and a pending IT Rules change, not an OS age signal **[REVISED]**. AB 1043, CPSIA and FCC rows do not apply; interception, CSAM and COPPA rows map to Telecom/IT Act, POCSO and DPDP.
- **12:** the cellular legal tree is gone; emergency calling and identifier tampering survive; 911 becomes 112.
- **13:** server-readable messages suit IT Act s.69 and POCSO; 180-day retention conflicts with Rule 8(3); NCMEC becomes the Indian police route; COPPA consent becomes Rule 10; both-family consent is now legally motivated.
- **17:** "a card payment may serve as parental consent" is wrong for India; USD pricing, Paddle/Lemon Squeezy India coverage (unchecked), FCC and EU CRA items need INR, GST and BIS replacements.
- **18:** "US only (A1)", USD costs, 10/25/100 cohorts, CPSIA and COPPA clauses are out of date; add DPDP consent and Indian-law bailment terms.
- **05 and 07:** US-pinned hosting and inference move to India; retention (180 d, 90 d, 30 d) needs the Rule 8(3) reconciliation.
- **D20:** English alone arguably satisfies ss.5(3)/6(3), but see decision 3.

## 7. Risks & unknowns
- Indian primary texts for DoT, IT Rules, RBI, POCSO and BIS were unreadable; every [SECONDARY] item can be wrong.
- s.9(3) has no guidance or Board ruling. The IT Rules under-18 amendment could capture the messenger; DPDP dates may compress to 13 Nov 2026.
- Whether 112 works on a data-only SIM with AOSP and no carrier configuration is untested [INFERRED].
- Whether a reflasher is a "manufacturer" (Telecom Act s.19, BIS, panic-button Rules, ITSAR) is open; Rule 8(3) scope (content or logs) is ambiguous.

## 8. Decisions needed from the founder (by impact)
1. **Authorise Indian counsel now** (G1, questions below). Default: yes, before inviting any family.
2. **Entity:** incorporate an Indian private limited. Default: yes.
3. **Hindi legal notices:** keep the product English-only (D20) but translate the parent consent and privacy notices into Hindi. Default: yes.
4. **A9 emergency path:** 112-only on cellular, 1098 shown as text, triple-press SOS, disclosed as not guaranteed. Default: yes.
5. **Monitoring defaults and age range (A8):** content visible under 13, excerpts plus metadata at 13+. Default: yes.
6. **Retention:** 12-month vault pending counsel. Default: yes.
7. **Free first phase** until payments, GST and DLT are ready. Default: free, invite-only.
8. **Positioning:** "family-managed contact tool", no public marketing, MeitY outreach after counsel. Default: yes.

## 9. Load-bearing claims

| # | Claim | Source | Basis |
|---|---|---|---|
| 1 | s.9 and Rule 10 bind 13 May 2027; Rule 4 on 13 Nov 2026 | Act footnote G.S.R. 843(E); Rule 1 (mirrors, 2.1) | PRIMARY |
| 2 | s.9(3) bans child tracking and behavioural monitoring; the Fourth Schedule has no parental-control or messaging exemption, only B(4) location and B(5) harmful-content gating | Act s.9; Rule 12, Fourth Schedule | PRIMARY |
| 3 | Rule 10 accepts held details or authorised-entity/DigiLocker tokens; child = under 18 | Rule 10; Act s.2(f) | PRIMARY |
| 4 | No blanket localisation (s.16, Rule 13(4)); s.9 penalty up to Rs 200 crore | Act s.16, Schedule | PRIMARY |
| 5 | Rule 8(3) one-year retention; 72-hour breach report | Rules 7, 8 | PRIMARY |
| 6 | Telecom Act: telecommunication service needs authorisation; unlawful interception and identifier tampering are offences | Telecom Act ss.2, 3, 42 | PRIMARY |
| 7 | Centre told the Supreme Court (28 Sep 2026) it will bar under-18 social-media accounts via IT Rules | https://inc42.com/buzz/will-amend-it-rules-to-bar-under-18s-from-social-media-centre-to-sc/ | SECONDARY |
| 8 | SIM-binding deadline 31 Dec 2026; July 2026 username notices; takedown 3 h/2 h | Tribune, BusinessToday, Khaitan links (2.2, 2.4) | SECONDARY |

## 10. Questions for Indian counsel
1. Is parent access to message content, call metadata and AI transcripts "tracking or behavioural monitoring" by the fiduciary under s.9(3), or consented processing for the parent as part of the Data Principal (s.2(j)(i))? Does B(5) cover safety scanning? Should we seek a s.9(4) or s.17(5) exemption?
2. Does staff inspection of government ID plus mobile OTP satisfy Rule 10 without a DigiLocker token? Can a private company integrate DigiLocker; may we use Aadhaar?
3. What notice and consent does the **other** child's parent need when the first child's parent can see the conversation?
4. Does Rule 8(3) require keeping message content for a year, or only logs, and how does it fit with erasure on withdrawal?
5. Is a parent-managed closed messenger a "social media intermediary", and would the proposed under-18 bar capture it?
6. Is it a "telecommunication service" (ss.3(1)(a), 42(1)), a TIUE, or within the SIM-binding direction, given parent mobile OTP and no child numbers or public usernames? Does portal access risk Telecom Act s.42(2)(b) or IT Act ss.69, 72, and what interception assistance must we build?
7. How do POCSO ss.19-21 and the Juvenile Justice Act apply when the sender is a child; what must be preserved versus erased?
8. Does replacing the OS on a certified phone make us a "manufacturer" or "product service provider" (CPA, Telecom Act s.19, BIS, panic-button Rules, ITSAR)? Is a handset without cellular voice lawful to sell and operate, and what is our liability if 112 fails?
9. Are liability caps, arbitration and custody terms enforceable against consumers; what bailment cover is needed?
10. Best payment structure, GST on the flash and subscription, FEMA for foreign vendors or a foreign parent, DLT for OTP SMS; does an English-only notice satisfy ss.5(3)/6(3); is a children's platform likely to become a Significant Data Fiduciary?
